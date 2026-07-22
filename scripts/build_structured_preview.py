#!/usr/bin/env python3
"""Build GENAI-RON structured previews without touching site/.

This experimental builder combines:
- content/ Markdown
- publishing/templates/article.html
- publishing/components/*
- a logical theme id

It intentionally has no --write-site option. Promotion to the public build path
requires preview generation and diff review first.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Dict, Iterable, List

from build_content_pages import (
    BuildError,
    parse_front_matter,
    render_article_nav,
    render_markdown_body,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = REPO_ROOT / "content"
PUBLISHING_ROOT = REPO_ROOT / "publishing"
DEFAULT_PREVIEW_ROOT = REPO_ROOT / "_structured_build_preview"
ARTICLE_TEMPLATE = PUBLISHING_ROOT / "templates" / "article.html"
SITE_HEADER = PUBLISHING_ROOT / "components" / "site-header.html"
SITE_FOOTER = PUBLISHING_ROOT / "components" / "site-footer.html"

PLACEHOLDER_RE = re.compile(r"\{\{([a-zA-Z0-9_-]+)\}\}")


def read_required(path: Path) -> str:
    if not path.is_file():
        raise BuildError(f"required publishing file is missing: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8").rstrip("\n")


def theme_manifest_for(theme_id: str) -> Path:
    if theme_id == "default-academic":
        return PUBLISHING_ROOT / "themes" / "default.yml"
    if theme_id == "library-series" or theme_id.startswith("library-"):
        return PUBLISHING_ROOT / "themes" / "library-series.yml"
    raise BuildError(f"unknown structured-preview theme_id: {theme_id!r}")


def render_template(template: str, values: Dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise BuildError(f"template value is missing: {key}")
        return values[key]

    rendered = PLACEHOLDER_RE.sub(replace, template)
    unresolved = sorted(set(PLACEHOLDER_RE.findall(rendered)))
    if unresolved:
        raise BuildError(f"unresolved template placeholders: {', '.join(unresolved)}")
    return rendered


def source_paths(explicit: str | None) -> Iterable[Path]:
    if explicit:
        path = (REPO_ROOT / explicit).resolve()
        if not path.is_file():
            raise BuildError(f"content source is missing: {explicit}")
        yield path
        return
    yield from sorted(CONTENT_ROOT.glob("series/**/*.md"))


def output_path_for(meta: Dict[str, object], preview_root: Path) -> Path:
    slug = str(meta.get("slug", "")).strip()
    if not slug.startswith("/") or not slug.endswith("/"):
        raise BuildError(f"invalid or missing slug: {slug!r}")
    return preview_root / slug.strip("/") / "index.html"


def build_article(meta: Dict[str, object], body_html: str, theme_id: str) -> str:
    template = read_required(ARTICLE_TEMPLATE)
    header = read_required(SITE_HEADER)
    footer = read_required(SITE_FOOTER)

    manifest_path = theme_manifest_for(theme_id)
    read_required(manifest_path)

    title = str(meta.get("title", "Untitled"))
    subtitle = str(meta.get("subtitle", ""))
    description = str(meta.get("description", subtitle))
    series_label = str(meta.get("series_label", "生成AIのしくみ 超詳解"))
    order_raw = str(meta.get("series_order", "")).strip()
    order = str(meta.get("order_display", "")).strip() or (
        order_raw.zfill(2) if order_raw.isdigit() else order_raw
    )
    series_kicker = " ".join(part for part in (series_label, order) if part).strip()

    document_title = f"{series_kicker}｜GENAI-RON" if series_kicker else f"{title}｜GENAI-RON"
    og_title = series_kicker or title
    hero_variant = "text-only" if theme_id == "default-academic" else "image-background"

    values = {
        "theme_id": html.escape(theme_id, quote=True),
        "document_title": html.escape(document_title),
        "description": html.escape(description, quote=True),
        "og_title": html.escape(og_title, quote=True),
        "og_image": html.escape(str(meta.get("og_image", "/assets/og.svg")), quote=True),
        "original_created": html.escape(str(meta.get("original_notion_created_at", ""))),
        "original_updated": html.escape(str(meta.get("original_notion_updated_at", ""))),
        "web_migrated": html.escape(str(meta.get("web_migrated_at", ""))),
        "site_header": header,
        "hero_variant": html.escape(hero_variant, quote=True),
        "series_kicker": html.escape(series_kicker),
        "title": html.escape(title),
        "subtitle": html.escape(subtitle),
        "body_html": body_html,
        "article_nav": render_article_nav(meta),
        "site_footer": footer,
    }
    return render_template(template, values) + "\n"


def build_one(path: Path, preview_root: Path, cli_theme_id: str | None) -> Path:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)
    theme_id = cli_theme_id or str(meta.get("theme_id", "default-academic")).strip()
    if not theme_id:
        theme_id = "default-academic"

    body_html = render_markdown_body(body)
    page = build_article(meta, body_html, theme_id)
    out_path = output_path_for(meta, preview_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build structured GENAI-RON previews from content/ and publishing/."
    )
    parser.add_argument("--source", help="Single content Markdown path relative to repo root.")
    parser.add_argument(
        "--preview-root",
        default=str(DEFAULT_PREVIEW_ROOT),
        help="Preview output root. This builder never writes to site/.",
    )
    parser.add_argument(
        "--theme-id",
        help="Logical theme id. Defaults to source metadata or default-academic.",
    )
    args = parser.parse_args()

    preview_arg = Path(args.preview_root)
    preview_root = preview_arg if preview_arg.is_absolute() else (REPO_ROOT / preview_arg).resolve()

    site_root = (REPO_ROOT / "site").resolve()
    try:
        preview_root.relative_to(site_root)
    except ValueError:
        pass
    else:
        raise BuildError("structured preview root must not be inside site/")

    built: List[Path] = []
    for path in source_paths(args.source):
        built.append(build_one(path, preview_root, args.theme_id))

    for path in built:
        print(path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
