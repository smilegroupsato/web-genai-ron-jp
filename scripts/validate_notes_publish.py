#!/usr/bin/env python3
"""Validate the one-note controlled publication lane.

ページ作成日時：2026-08-04 16:22 JST
最終更新日時：2026-08-04 16:22 JST

PR mode validates the changed-file scope and requires the public note to be
byte-identical to a candidate regenerated from content/notes/<slug>/index.md.
Source-check mode proves semantic parity against an existing public note while
the gate itself is being introduced. This validator never writes to site/.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

from build_content_pages import BuildError
from build_notes_preview import REPO_ROOT, SITE_ROOT, build_one, validate_source_path

TARGET_RE = re.compile(r"^site/notes/([a-z0-9][a-z0-9-]*)/index\.html$")
GATE_ALLOWLIST = {
    ".gitignore",
    ".github/workflows/validate-notes-publish.yml",
    "publishing/NOTES_PUBLICATION.md",
    "publishing/templates/note.html",
    "requirements-publishing.txt",
    "scripts/build_notes_preview.py",
    "scripts/promote_note.py",
    "scripts/validate_notes_publish.py",
}
FORBIDDEN_PUBLIC_TEXT = {
    "source_html_path",
    "source_html_sha256",
    "metadata_provenance",
    "extraction_status",
}


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


class NoteSnapshot(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, bool, bool]] = []
        self.in_main = False
        self.in_article = False
        self.in_sidebar = False
        self.in_h1 = False
        self.in_heading = False
        self.current_heading: list[str] = []
        self.current_link_href: str | None = None
        self.current_link_text: list[str] = []
        self.h1: list[str] = []
        self.main_text: list[str] = []
        self.article_text: list[str] = []
        self.headings: list[str] = []
        self.article_links: list[tuple[str, str]] = []
        self.sidebar_links: list[tuple[str, str]] = []
        self.has_header = False
        self.has_footer = False

    @staticmethod
    def classes(attrs: list[tuple[str, str | None]]) -> set[str]:
        return set((dict(attrs).get("class") or "").split())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = self.classes(attrs)
        starts_main = tag == "main"
        starts_article = tag == "article" and bool({"note-content", "note-box"} & classes)
        starts_sidebar = tag == "aside" and "note-sidebar" in classes
        self.stack.append((tag, starts_main, starts_article, starts_sidebar))
        if tag == "header" and ({"site-header", "series-header"} & classes):
            self.has_header = True
        if tag == "footer" and ({"site-footer", "series-footer"} & classes):
            self.has_footer = True
        if starts_main:
            self.in_main = True
        if starts_article:
            self.in_article = True
        if starts_sidebar:
            self.in_sidebar = True
        if self.in_main and tag == "h1":
            self.in_h1 = True
        if self.in_article and tag in {"h2", "h3", "h4", "h5", "h6"}:
            self.in_heading = True
            self.current_heading = []
        if (self.in_article or self.in_sidebar) and tag == "a":
            self.current_link_href = dict(attrs).get("href") or ""
            self.current_link_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self.in_h1 = False
        if self.in_article and tag in {"h2", "h3", "h4", "h5", "h6"} and self.in_heading:
            self.headings.append(normalize(" ".join(self.current_heading)))
            self.current_heading = []
            self.in_heading = False
        if tag == "a" and self.current_link_href is not None:
            link = (self.current_link_href, normalize(" ".join(self.current_link_text)))
            if self.in_article:
                self.article_links.append(link)
            elif self.in_sidebar:
                self.sidebar_links.append(link)
            self.current_link_href = None
            self.current_link_text = []
        if self.stack:
            _, started_main, started_article, started_sidebar = self.stack.pop()
            if started_article:
                self.in_article = False
            if started_sidebar:
                self.in_sidebar = False
            if started_main:
                self.in_main = False

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        if self.in_main:
            self.main_text.append(data)
        if self.in_h1:
            self.h1.append(data)
        if self.in_article:
            self.article_text.append(data)
            if self.in_heading:
                self.current_heading.append(data)
        if self.current_link_href is not None:
            self.current_link_text.append(data)

    def snapshot(self) -> dict[str, object]:
        return {
            "title": normalize(" ".join(self.h1)),
            "main_text": normalize(" ".join(self.main_text)),
            "article_text": normalize(" ".join(self.article_text)),
            "headings": self.headings,
            "article_links": self.article_links,
            "sidebar_links": self.sidebar_links,
            "has_header": self.has_header,
            "has_footer": self.has_footer,
        }


def parse_html(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    leaked = sorted(value for value in FORBIDDEN_PUBLIC_TEXT if value in text)
    if leaked:
        raise BuildError(f"management metadata leaked into public HTML: {', '.join(leaked)}")
    parser = NoteSnapshot()
    parser.feed(text)
    return parser.snapshot()


def validate_semantic_parity(current: Path, candidate: Path) -> None:
    left = parse_html(current)
    right = parse_html(candidate)
    errors: list[str] = []
    for key in (
        "title",
        "main_text",
        "article_text",
        "headings",
        "article_links",
        "sidebar_links",
    ):
        if left[key] != right[key]:
            errors.append(f"semantic mismatch: {key}")
    for key in ("has_header", "has_footer"):
        if not right[key]:
            errors.append(f"candidate missing required region: {key}")
    if errors:
        raise BuildError("\n".join(errors))


def run(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def changed_files(base_ref: str) -> list[str]:
    result = run(["git", "diff", "--name-only", f"{base_ref}...HEAD"], capture=True)
    return sorted(line.strip() for line in result.stdout.splitlines() if line.strip())


def source_for_target(target: str) -> Path:
    match = TARGET_RE.match(target)
    if not match:
        raise BuildError(f"unsupported notes target: {target}")
    return REPO_ROOT / "content" / "notes" / match.group(1) / "index.md"


def validate_scope(files: list[str]) -> str | None:
    targets = [path for path in files if TARGET_RE.match(path)]
    site_changes = [path for path in files if path.startswith("site/")]
    if len(targets) > 1:
        raise BuildError("notes publication PR must change at most one public note")
    unexpected_site = sorted(set(site_changes) - set(targets))
    if unexpected_site:
        raise BuildError("unexpected site/ changes:\n" + "\n".join(unexpected_site))
    if not targets:
        if set(files) <= GATE_ALLOWLIST:
            print("notes-publish gate-only change: OK")
        else:
            print("notes-publish target not present: skipped")
        return None

    target = targets[0]
    source = source_for_target(target).relative_to(REPO_ROOT).as_posix()
    allowed = GATE_ALLOWLIST | {target, source}
    unexpected = sorted(set(files) - allowed)
    if unexpected:
        raise BuildError("notes publication PR has unexpected changes:\n" + "\n".join(unexpected))
    return target


def validate_target(target: str, base_ref: str, preview_root: Path) -> None:
    source = source_for_target(target)
    if not source.is_file():
        raise BuildError(f"content source is missing: {source.relative_to(REPO_ROOT)}")
    shutil.rmtree(preview_root, ignore_errors=True)
    candidate = build_one(source, preview_root)
    promoted = REPO_ROOT / target
    if candidate.read_bytes() != promoted.read_bytes():
        raise BuildError("promoted note is not byte-identical to the regenerated candidate")

    base_current = preview_root / "base-current.html"
    try:
        result = run(["git", "show", f"{base_ref}:{target}"], capture=True)
    except subprocess.CalledProcessError:
        result = None
    if result is not None:
        base_current.write_text(result.stdout, encoding="utf-8")
        validate_semantic_parity(base_current, promoted)
    print("notes controlled promotion: OK")
    print(f"source: {source.relative_to(REPO_ROOT)}")
    print(f"target: {target}")


def validate_source_check(source: Path, preview_root: Path) -> None:
    slug = validate_source_path(source)
    current = SITE_ROOT / "notes" / slug / "index.html"
    if not current.is_file():
        raise BuildError(f"source-check public note is missing: {current.relative_to(REPO_ROOT)}")
    shutil.rmtree(preview_root, ignore_errors=True)
    candidate = build_one(source, preview_root)
    validate_semantic_parity(current, candidate)
    print("notes source-check semantic parity: OK")
    print(f"source: {source.relative_to(REPO_ROOT)}")
    print(f"current: {current.relative_to(REPO_ROOT)}")
    print(f"candidate: {candidate.relative_to(REPO_ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate controlled research-note publication.")
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--preview-root", default="_notes_publish_preview")
    parser.add_argument("--source-check", help="Validate one existing content/notes/<slug>/index.md source.")
    args = parser.parse_args()
    preview_root = (REPO_ROOT / args.preview_root).resolve()
    if args.source_check:
        validate_source_check((REPO_ROOT / args.source_check).resolve(), preview_root)
        return 0

    files = changed_files(args.base_ref)
    if not files:
        raise BuildError("no changed files detected")
    print("changed files:")
    for path in files:
        print(f"- {path}")
    target = validate_scope(files)
    if target:
        validate_target(target, args.base_ref, preview_root)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
