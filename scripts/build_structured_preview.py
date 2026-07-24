#!/usr/bin/env python3
"""Build GENAI-RON structured previews without touching site/.

This experimental builder combines:
- content/ Markdown
- publishing/site.yml
- publishing/templates/article.html
- publishing/components/*
- publishing/themes/*
- a logical theme id

It intentionally has no --write-site option. Promotion to the public build path
requires preview generation and semantic review first.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Dict, Iterable, List, Mapping

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised by operator setup
    yaml = None

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
SITE_REGISTRY = PUBLISHING_ROOT / "site.yml"
ARTICLE_TEMPLATE = PUBLISHING_ROOT / "templates" / "article.html"
SITE_HEADER = PUBLISHING_ROOT / "components" / "site-header.html"
SITE_FOOTER = PUBLISHING_ROOT / "components" / "site-footer.html"
READING_PREFERENCES = PUBLISHING_ROOT / "components" / "reading-preferences.html"

PLACEHOLDER_RE = re.compile(r"\{\{([a-zA-Z0-9_-]+)\}\}")


def read_required(path: Path) -> str:
    if not path.is_file():
        raise BuildError(f"required publishing file is missing: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8").rstrip("\n")


def load_yaml_mapping(path: Path) -> Dict[str, object]:
    if yaml is None:
        raise BuildError(
            "PyYAML is required for the structured preview builder. "
            "Install requirements-publishing.txt in an isolated environment."
        )
    raw = read_required(path)
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise BuildError(f"publishing manifest must be a mapping: {path.relative_to(REPO_ROOT)}")
    return data


def require_mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise BuildError(f"publishing manifest mapping is missing or invalid: {label}")
    return value


def repo_path(value: object, label: str) -> Path:
    raw = str(value or "").strip()
    if not raw:
        raise BuildError(f"publishing path is missing: {label}")
    path = (REPO_ROOT / raw).resolve()
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise BuildError(f"publishing path escapes repository: {label}") from exc
    return path


def theme_resolution(theme_id: str) -> Dict[str, str]:
    registry = load_yaml_mapping(SITE_REGISTRY)
    registered_themes = require_mapping(registry.get("themes"), "site.yml:themes")

    if theme_id == "default-academic":
        entry = require_mapping(registered_themes.get(theme_id), f"theme:{theme_id}")
        manifest_path = repo_path(entry.get("manifest"), f"theme:{theme_id}:manifest")
        manifest = load_yaml_mapping(manifest_path)
        hero = require_mapping(manifest.get("hero"), f"{manifest_path.name}:hero")
        return {
            "theme_id": theme_id,
            "theme_collection": str(manifest.get("collection_id", "core")),
            "theme_base": theme_id,
            "theme_season": "none",
            "hero_variant": str(hero.get("variant", "text-only")),
            "text_contrast": str(hero.get("text_contrast", "dark")),
            "asset_role": str(hero.get("asset_role", "none")),
            "asset_ref": "none",
            "asset_status": "none",
            "production_enabled": "true",
            "theme_manifest": str(manifest_path.relative_to(REPO_ROOT)),
        }

    library_entry = require_mapping(
        registered_themes.get("library-series"), "theme:library-series"
    )
    manifest_path = repo_path(
        library_entry.get("manifest"), "theme:library-series:manifest"
    )
    manifest = load_yaml_mapping(manifest_path)
    runtime_variants = require_mapping(
        manifest.get("runtime_variants"), f"{manifest_path.name}:runtime_variants"
    )
    variant = runtime_variants.get(theme_id)
    if not isinstance(variant, dict):
        available = ", ".join(sorted(str(key) for key in runtime_variants))
        raise BuildError(
            f"unknown structured-preview theme_id: {theme_id!r}. "
            f"Registered runtime variants: {available}"
        )

    base_theme_id = str(variant.get("base_theme", "")).strip()
    themes = require_mapping(manifest.get("themes"), f"{manifest_path.name}:themes")
    base_theme = require_mapping(
        themes.get(base_theme_id), f"{manifest_path.name}:themes:{base_theme_id}"
    )
    season = str(variant.get("season", "none")).strip() or "none"
    if season != "none":
        season_variants = require_mapping(
            manifest.get("season_variants"), f"{manifest_path.name}:season_variants"
        )
        if season not in season_variants:
            raise BuildError(f"unknown season {season!r} for theme {theme_id!r}")

    asset_ref = str(variant.get("asset_ref", "unresolved")).strip() or "unresolved"
    asset_status = "resolved" if asset_ref not in {"none", "unresolved"} else asset_ref

    return {
        "theme_id": theme_id,
        "theme_collection": str(manifest.get("collection_id", "library-series")),
        "theme_base": base_theme_id,
        "theme_season": season,
        "hero_variant": str(
            variant.get("hero_variant", base_theme.get("hero_variant", "image-background"))
        ),
        "text_contrast": str(
            variant.get("text_contrast", base_theme.get("text_contrast", "light"))
        ),
        "asset_role": str(variant.get("asset_role", "hero-main")),
        "asset_ref": asset_ref,
        "asset_status": asset_status,
        "production_enabled": str(bool(variant.get("production_enabled", False))).lower(),
        "theme_manifest": str(manifest_path.relative_to(REPO_ROOT)),
    }



def series_slug_from_meta(meta: Dict[str, object]) -> str:
    slug = str(meta.get("slug", "")).strip()
    if slug.startswith("/series/"):
        parts = slug.strip("/").split("/")
        if len(parts) >= 2:
            return parts[1]
    return ""


def render_site_header_for_series(series_slug: str) -> str:
    if series_slug == "ai-dialogue-intro":
        return """<header class="series-header">
  <div class="series-header-inner">
    <a class="series-brand" href="/"><span class="series-brand-main">GENAI-RON</span><span class="series-brand-sub">🧠生成AI論🥦</span></a>
    <nav class="series-nav" aria-label="サイト内ナビゲーション">
      <a href="/series/ai-dialogue-intro/">目次</a>
      <a href="/series/ai-dialogue-intro/introduction/">はじめに</a>
      <a href="/series/ai-dialogue-intro/01-start-talking/">第1章</a>
      <a href="/article/">論考一覧</a>
    </nav>
  </div>
</header>"""
    return read_required(SITE_HEADER)


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
        try:
            path.relative_to(CONTENT_ROOT)
        except ValueError as exc:
            raise BuildError("structured preview source must be under content/") from exc
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
    series_slug = series_slug_from_meta(meta)
    header = render_site_header_for_series(series_slug)
    footer = read_required(SITE_FOOTER)
    reading_preferences = read_required(READING_PREFERENCES)
    theme = theme_resolution(theme_id)

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

    values = {
        "series_slug": html.escape(series_slug, quote=True),
        "theme_id": html.escape(theme["theme_id"], quote=True),
        "theme_collection": html.escape(theme["theme_collection"], quote=True),
        "theme_base": html.escape(theme["theme_base"], quote=True),
        "theme_season": html.escape(theme["theme_season"], quote=True),
        "theme_manifest": html.escape(theme["theme_manifest"], quote=True),
        "production_enabled": html.escape(theme["production_enabled"], quote=True),
        "document_title": html.escape(document_title),
        "description": html.escape(description, quote=True),
        "og_title": html.escape(og_title, quote=True),
        "og_image": html.escape(str(meta.get("og_image", "/assets/og.svg")), quote=True),
        "original_created": html.escape(str(meta.get("original_notion_created_at", ""))),
        "original_updated": html.escape(str(meta.get("original_notion_updated_at", ""))),
        "web_migrated": html.escape(str(meta.get("web_migrated_at", ""))),
        "site_header": header,
        "reading_preferences": reading_preferences,
        "hero_variant": html.escape(theme["hero_variant"], quote=True),
        "text_contrast": html.escape(theme["text_contrast"], quote=True),
        "asset_role": html.escape(theme["asset_role"], quote=True),
        "asset_ref": html.escape(theme["asset_ref"], quote=True),
        "asset_status": html.escape(theme["asset_status"], quote=True),
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
    registry = load_yaml_mapping(SITE_REGISTRY)
    site = require_mapping(registry.get("site"), "site.yml:site")
    default_theme_id = str(site.get("default_theme_id", "default-academic"))
    theme_id = cli_theme_id or str(meta.get("theme_id", default_theme_id)).strip()
    if not theme_id:
        theme_id = default_theme_id

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
        help="Logical theme id. Defaults to source metadata or publishing/site.yml.",
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
