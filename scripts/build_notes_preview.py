#!/usr/bin/env python3
"""Build one nested research-note preview without writing to site/.

ページ作成日時：2026-08-04 16:22 JST
最終更新日時：2026-08-04 16:36 JST

The accepted lane is intentionally narrow:
- source: content/notes/<slug>/index.md
- route: /notes/<slug>/
- output: <preview-root>/notes/<slug>/index.html

Root note indexes, flat .html routes, and bulk globs remain outside this v0.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Mapping

try:
    import markdown
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - operator setup
    raise SystemExit(
        "Publishing dependencies are missing. Install requirements-publishing.txt."
    ) from exc

from build_content_pages import BuildError

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = (REPO_ROOT / "content" / "notes").resolve()
SITE_ROOT = (REPO_ROOT / "site").resolve()
DEFAULT_PREVIEW_ROOT = REPO_ROOT / "_notes_build_preview"
TEMPLATE = REPO_ROOT / "publishing" / "templates" / "note.html"
ANCHOR_RE = re.compile(r'^<a id="([a-zA-Z0-9_-]+)"></a>\s*$', re.MULTILINE)
LINK_RE = re.compile(r"^\[([^\]]+)\]\(([^)]+)\)\s*$")
PLACEHOLDER_RE = re.compile(r"\{\{([a-z_]+)\}\}")


def load_source(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise BuildError("note source must start with YAML front matter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise BuildError("note source front matter is not terminated")
    data = yaml.safe_load(text[4:end])
    if not isinstance(data, dict):
        raise BuildError("note front matter must be a mapping")
    return data, text[end + len("\n---\n") :].strip()


def validate_source_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(CONTENT_ROOT)
    except ValueError as exc:
        raise BuildError("note source must be under content/notes/") from exc
    if len(relative.parts) != 2 or relative.name != "index.md":
        raise BuildError("notes publication v0 accepts only content/notes/<slug>/index.md")
    slug = relative.parts[0]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise BuildError(f"invalid note slug: {slug!r}")
    return slug


def require_scalar(meta: Mapping[str, object], key: str) -> str:
    value = str(meta.get(key) or "").strip()
    if not value:
        raise BuildError(f"required note metadata is missing: {key}")
    return value


def validate_metadata(meta: Mapping[str, object], slug: str) -> None:
    route = require_scalar(meta, "route")
    expected_route = f"/notes/{slug}/"
    if route != expected_route:
        raise BuildError(f"route mismatch: expected {expected_route!r}, got {route!r}")
    if require_scalar(meta, "title") == "Untitled":
        raise BuildError("note title must be explicit")
    require_scalar(meta, "meta_description")
    if str(meta.get("page_type") or "").strip() != "note":
        raise BuildError("page_type must be note")
    if str(meta.get("series_or_article") or "").strip() != "notes":
        raise BuildError("series_or_article must be notes")


def parse_preamble(body: str) -> tuple[dict[str, str], list[tuple[str, str]], str]:
    anchor = ANCHOR_RE.search(body)
    if anchor is None:
        raise BuildError("note body must contain at least one explicit section anchor")
    preamble = body[: anchor.start()].strip()
    article = body[anchor.start() :].strip()
    lines = [line.strip() for line in preamble.splitlines() if line.strip()]
    if "CONTENTS" not in lines:
        raise BuildError("note preamble must contain CONTENTS")
    contents_index = lines.index("CONTENTS")
    hero = lines[:contents_index]
    toc = lines[contents_index + 1 :]
    if len(hero) < 5:
        raise BuildError("note preamble must contain kicker, title, lead, sublead, and meta")

    kicker = hero[0]
    title_line = next((line for line in hero if line.startswith("# ")), "")
    lead_line = next((line for line in hero if line.startswith("**") and line.endswith("**")), "")
    if not title_line or not lead_line:
        raise BuildError("note preamble title or lead is missing")
    title = title_line[2:].strip()
    lead = lead_line[2:-2].strip()
    title_index = hero.index(title_line)
    lead_index = hero.index(lead_line)
    meta_line = hero[-1]
    sublead_lines = hero[lead_index + 1 : -1]
    if not sublead_lines:
        raise BuildError("note preamble sublead is missing")
    if title_index <= 0 or lead_index <= title_index:
        raise BuildError("note preamble order is invalid")

    links: list[tuple[str, str]] = []
    for line in toc:
        match = LINK_RE.fullmatch(line)
        if not match:
            raise BuildError(f"invalid CONTENTS entry: {line!r}")
        links.append((match.group(1), match.group(2)))
    if not links:
        raise BuildError("note CONTENTS must contain at least one link")

    return {
        "kicker": kicker,
        "title": title,
        "lead": lead,
        "sublead": " ".join(sublead_lines),
        "note_meta": meta_line,
    }, links, article


def render_sections(article: str) -> str:
    matches = list(ANCHOR_RE.finditer(article))
    sections: list[str] = []
    for index, match in enumerate(matches):
        section_id = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(article)
        section_markdown = article[start:end].strip()
        if not section_markdown:
            raise BuildError(f"empty note section: {section_id}")
        rendered = markdown.markdown(
            section_markdown,
            extensions=["extra", "sane_lists"],
            output_format="html5",
        )
        rendered = indent_fragment(rendered)
        intro_class = " note-intro" if index == 0 else ""
        sections.append(
            f'        <section id="{html.escape(section_id, quote=True)}" '
            f'class="note-section{intro_class}">\n{rendered}\n        </section>'
        )
    return "\n\n".join(sections)


def indent_fragment(fragment: str) -> str:
    """Keep generated note HTML reviewable and close to the legacy layout."""
    containers = {"<ul>": "</ul>", "<ol>": "</ol>", "<blockquote>": "</blockquote>"}
    closing = set(containers.values())
    lines: list[str] = []
    depth = 0
    for raw in fragment.splitlines():
        value = raw.strip()
        if value in closing:
            depth = max(0, depth - 1)
        if value.startswith("<h3") and lines and lines[-1] != "":
            lines.append("")
        lines.append(f"{'          '}{'  ' * depth}{value}")
        if value in containers:
            depth += 1
    return "\n".join(lines)


def render_template(values: Mapping[str, str]) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise BuildError(f"missing note template value: {key}")
        return values[key]

    rendered = PLACEHOLDER_RE.sub(replace, template)
    if PLACEHOLDER_RE.search(rendered):
        raise BuildError("unresolved note template placeholder")
    return rendered.rstrip() + "\n"


def output_path(preview_root: Path, slug: str) -> Path:
    resolved = preview_root.resolve()
    try:
        resolved.relative_to(SITE_ROOT)
    except ValueError:
        pass
    else:
        raise BuildError("notes preview root must not be inside site/")
    return resolved / "notes" / slug / "index.html"


def build_one(source: Path, preview_root: Path) -> Path:
    slug = validate_source_path(source)
    meta, body = load_source(source)
    validate_metadata(meta, slug)
    preamble, links, article = parse_preamble(body)
    title = require_scalar(meta, "title")
    if preamble["title"] != title:
        raise BuildError("front matter title and visible h1 differ")

    canonical = str(meta.get("canonical") or meta["route"]).strip()
    sidebar_links = "\n".join(
        f'        <a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
        for label, href in links
    )
    values = {
        "document_title": html.escape(f"{title}｜GENAI-RON"),
        "description": html.escape(require_scalar(meta, "meta_description"), quote=True),
        "canonical": html.escape(canonical, quote=True),
        "kicker": html.escape(preamble["kicker"]),
        "title": html.escape(title),
        "lead": html.escape(preamble["lead"]),
        "sublead": html.escape(preamble["sublead"]),
        "note_meta": html.escape(preamble["note_meta"]),
        "sidebar_links": sidebar_links,
        "article_html": render_sections(article),
    }
    target = output_path(preview_root, slug)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_template(values), encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one research-note preview.")
    parser.add_argument("--source", required=True, help="content/notes/<slug>/index.md")
    parser.add_argument("--preview-root", default=str(DEFAULT_PREVIEW_ROOT))
    args = parser.parse_args()

    source = (REPO_ROOT / args.source).resolve()
    preview_arg = Path(args.preview_root)
    preview_root = preview_arg if preview_arg.is_absolute() else REPO_ROOT / preview_arg
    target = build_one(source, preview_root)
    print(target.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, ValueError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)
