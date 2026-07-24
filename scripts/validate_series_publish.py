#!/usr/bin/env python3
"""Validate structured publishing output for whole-series publish PRs.

ページ作成日時：2026-07-24 08:59 JST
最終更新日時：2026-07-24 08:59 JST

This gate is intentionally separate from validate_controlled_write.py.
The controlled-write gate protects one-page migrations, while this script protects
new structured series publication where multiple site pages are added together.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_RE = re.compile(r"^site/series/([^/]+)(?:/([^/]+))?/index\.html$")
ALLOWED_SERIES = {"ai-dialogue-intro"}
GATE_ALLOWLIST = {
    ".github/workflows/validate-series-publish.yml",
    ".github/workflows/validate-publishing-structure.yml",
    ".github/workflows/validate-promotion-fixture-04.yml",
    "scripts/validate_controlled_write.py",
    "scripts/validate_series_publish.py",
    "scripts/build_structured_preview.py",
    "publishing/templates/article.html",
    "publishing/design/components.css",
    "site/publishing/design/components.css",
}
SITE_ALLOWLIST = {
    "site/publishing/design/components.css",
}
FORBIDDEN_PUBLIC_TEXT = [
    "ページ作成日時",
    "最終更新日時",
    "更新履歴",
    "統合原稿から章別ページとして再構成",
]


class PageHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_h1 = False
        self.in_article = False
        self.skip = 0
        self.h1: list[str] = []
        self.article_text: list[str] = []
        self.article_links: list[str] = []
        self.has_article = False
        self.has_reading_preferences = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        classes = attr.get("class", "")
        if "reading-preferences" in classes:
            self.has_reading_preferences = True
        if tag == "h1":
            self.in_h1 = True
        if tag == "article":
            self.in_article = True
            self.has_article = True
        if self.in_article and tag in {"script", "style", "nav"}:
            self.skip += 1
        if self.in_article and not self.skip and tag == "a":
            href = attr.get("href", "")
            if href:
                self.article_links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self.in_h1 = False
        if self.in_article and tag in {"script", "style", "nav"} and self.skip:
            self.skip -= 1
        if tag == "article":
            self.in_article = False

    def handle_data(self, data: str) -> None:
        if self.in_h1:
            self.h1.append(data)
        if self.in_article and not self.skip:
            self.article_text.append(data)


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


def target_info(target: str) -> tuple[str, str]:
    match = TARGET_RE.match(target)
    if not match:
        raise ValueError(f"unsupported series publish target: {target}")
    series = match.group(1)
    page = match.group(2) or "index"
    return series, page


def source_for_target(target: str) -> Path:
    series, page = target_info(target)
    return REPO_ROOT / "content" / "series" / series / f"{page}.md"


def candidate_for_target(target: str, preview_root: Path) -> Path:
    return preview_root / target.removeprefix("site/")


def parse_html(path: Path) -> PageHTML:
    parser = PageHTML()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def normalized_text(values: list[str]) -> str:
    return re.sub(r"\s+", "", " ".join(values))


def validate_scope(files: list[str]) -> list[str]:
    site_targets = [path for path in files if TARGET_RE.match(path)]
    site_changes = [path for path in files if path.startswith("site/")]

    if not site_targets:
        if set(files) <= GATE_ALLOWLIST:
            print("series-publish gate-only change: OK")
        else:
            print("series-publish target not present: skipped")
        return []

    unexpected_site = sorted(set(site_changes) - set(site_targets) - SITE_ALLOWLIST)
    if unexpected_site:
        raise RuntimeError("unexpected site/ changes:\n" + "\n".join(unexpected_site))

    series_names = {target_info(path)[0] for path in site_targets}
    if len(series_names) != 1:
        raise RuntimeError("series publish PR must target exactly one series: " + ", ".join(sorted(series_names)))

    series = next(iter(series_names))
    if series not in ALLOWED_SERIES:
        raise RuntimeError(f"unsupported series for whole-series publish: {series}")

    allowed = set(site_targets) | GATE_ALLOWLIST
    unexpected = sorted(set(files) - allowed)
    if unexpected:
        raise RuntimeError("series publish PR has unexpected changes:\n" + "\n".join(unexpected))

    return sorted(site_targets)


def validate_public_html(target: str, series_targets: set[str]) -> None:
    html_path = REPO_ROOT / target
    parsed = parse_html(html_path)
    title = re.sub(r"\s+", " ", "".join(parsed.h1)).strip()
    article_text = normalized_text(parsed.article_text)

    if not title:
        raise RuntimeError(f"missing h1: {target}")
    if not parsed.has_article:
        raise RuntimeError(f"missing article: {target}")
    if not parsed.has_reading_preferences:
        raise RuntimeError(f"missing reading-preferences: {target}")

    leaked = [word for word in FORBIDDEN_PUBLIC_TEXT if word in article_text]
    if leaked:
        raise RuntimeError(f"management text leaked in {target}: {', '.join(leaked)}")

    series, _ = target_info(target)
    for href in parsed.article_links:
        if not href.startswith(f"/series/{series}/"):
            continue
        rel = href.removeprefix(f"/series/{series}/").strip("/")
        linked_target = f"site/series/{series}/index.html" if not rel else f"site/series/{series}/{rel}/index.html"
        if linked_target not in series_targets and not (REPO_ROOT / linked_target).is_file():
            raise RuntimeError(f"broken internal link in {target}: {href}")


def validate_targets(targets: list[str], preview_root: Path) -> None:
    if preview_root.resolve().is_relative_to((REPO_ROOT / "site").resolve()):
        raise RuntimeError("preview root must not be inside site/")

    shutil.rmtree(preview_root, ignore_errors=True)
    series_targets = set(targets)

    for target in targets:
        source = source_for_target(target)
        if not source.is_file():
            raise RuntimeError(f"content source is missing for target {target}: {source.relative_to(REPO_ROOT)}")

        run([
            sys.executable,
            "scripts/build_structured_preview.py",
            "--source",
            str(source.relative_to(REPO_ROOT)),
            "--preview-root",
            str(preview_root.relative_to(REPO_ROOT)),
        ])

        candidate = candidate_for_target(target, preview_root)
        promoted = REPO_ROOT / target
        if not candidate.is_file():
            raise RuntimeError(f"candidate is missing: {candidate.relative_to(REPO_ROOT)}")
        if candidate.read_bytes() != promoted.read_bytes():
            raise RuntimeError(f"promoted site HTML is not byte-identical to regenerated candidate: {target}")

        validate_public_html(target, series_targets)
        print(f"series publish target: OK {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate structured whole-series publication PRs.")
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--preview-root", default="_series_publish_preview")
    args = parser.parse_args()

    files = changed_files(args.base_ref)
    if not files:
        raise RuntimeError("no changed files detected")

    print("changed files:")
    for path in files:
        print(f"- {path}")

    targets = validate_scope(files)
    if not targets:
        return 0

    validate_targets(targets, (REPO_ROOT / args.preview_root).resolve())
    print("series publish: OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
