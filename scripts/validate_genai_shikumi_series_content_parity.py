#!/usr/bin/env python3
"""Validate semantic parity for the nine genai-shikumi series sources."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

from extract_genai_shikumi_series_content import CHAPTERS, PAGES, SERIES, Page
from extract_history_timeline_content import DATE_FIELDS, date_metadata
from extract_site_article_to_content import TreeParser, find_all, find_first, normalize_space, text_of
from validate_tool_discovery_layer_content_parity import compact, markdown_text, scalar

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "site-content-salvage.manifest.json"
MIN_TEXT_RATIO = 0.995


class ParityError(RuntimeError):
    pass


def parse_markdown(page: Page) -> tuple[dict[str, object], str]:
    text = page.output_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ParityError(f"missing front matter: {page.output_path}")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ParityError(f"unterminated front matter: {page.output_path}")
    metadata: dict[str, object] = {}
    nested: dict[str, object] | None = None
    for line in text[4:end].splitlines():
        if line.startswith("  ") and nested is not None:
            key, value = line.strip().split(":", 1)
            nested[key] = scalar(value)
            continue
        nested = None
        key, value = line.split(":", 1)
        if value.strip():
            metadata[key] = scalar(value)
        else:
            nested = {}
            metadata[key] = nested
    return metadata, text[end + len("\n---\n"):].strip()


def validate_manifest() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_pages = manifest["pages"]
    for page in PAGES:
        matches = [item for item in manifest_pages if item.get("route") == page.route]
        if len(matches) != 1:
            raise ParityError(f"expected one manifest route for {page.route}, found {len(matches)}")
        expected = {
            "page_type": page.page_type,
            "content_source_status": "content_source_exists",
            "corresponding_content_path": page.output_path,
            "salvage_status": "needs_parity_check",
        }
        for field, value in expected.items():
            if matches[0].get(field) != value:
                raise ParityError(f"manifest {field} mismatch: {page.route}")


def validate_metadata(page: Page, metadata: dict[str, object], parser: TreeParser) -> None:
    required = {
        "title", "route", "slug", "source_html_path", "source_html_sha256", "page_type",
        "series_or_article", "order", "chapter", "meta_description", "canonical",
        "created_at", "updated_at", "manuscript_created_at", "manuscript_updated_at",
        "web_migrated_at", "metadata_provenance", "extraction_status",
    }
    if missing := sorted(required - metadata.keys()):
        raise ParityError(f"missing metadata fields for {page.route}: {missing}")
    main = find_first(parser.root, "main")
    if main is None:
        raise ParityError(f"main not found: {page.route}")
    expected = {
        "title": normalize_space(text_of(find_first(main, "h1") or main)),
        "route": page.route,
        "slug": page.route,
        "source_html_path": page.source_html_path,
        "source_html_sha256": hashlib.sha256(page.source_html.read_bytes()).hexdigest(),
        "page_type": page.page_type,
        "series_or_article": SERIES,
        "order": page.order,
        "chapter": page.chapter,
        "canonical": None,
    }
    for field, value in expected.items():
        if metadata.get(field) != value:
            raise ParityError(f"metadata {field} mismatch: {page.route}")
    if page.chapter:
        if page.chapter not in page.route or not page.output_path.endswith(f"/{page.chapter}.md"):
            raise ParityError(f"chapter/slug/route mismatch: {page.route}")
        if not page.chapter.startswith(f"{page.order:02d}-"):
            raise ParityError(f"chapter number mismatch: {page.route}")

    dates, date_provenance = date_metadata(text_of(main), parser.comments)
    provenance = metadata.get("metadata_provenance")
    if not isinstance(provenance, dict):
        raise ParityError(f"metadata_provenance must be a mapping: {page.route}")
    for field in DATE_FIELDS:
        if metadata.get(field) != dates[field] or provenance.get(field) != date_provenance[field]:
            raise ParityError(f"date metadata mismatch: {page.route} {field}")


def validate_structure(page: Page, parser: TreeParser, body: str) -> float:
    main = find_first(parser.root, "main")
    if main is None:
        raise ParityError(f"main not found: {page.route}")
    hero = next(
        (node for node in find_all(main, "section") if "series-hero" in node.attr("class").split()),
        None,
    )
    if hero is None or find_first(hero, "h1") is None:
        raise ParityError(f"series hero/title missing: {page.route}")
    hero_text = [normalize_space(text_of(child)) for child in hero.children if hasattr(child, "tag")]
    cursor = 0
    compact_body = compact(markdown_text(body))
    for value in hero_text:
        compact_value = compact(value)
        position = compact_body.find(compact_value, cursor)
        if position < 0:
            raise ParityError(f"hero text/order mismatch: {page.route} {value}")
        cursor = position + len(compact_value)

    html_headings = [
        normalize_space(text_of(node)) for node in find_all(main)
        if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}
    ]
    md_headings = [
        normalize_space(match.group(1).replace("**", ""))
        for match in re.finditer(r"^#{1,6}\s+(.+)$", body, re.MULTILINE)
    ]
    md_headings = [re.sub(r"^\[|\]\([^)]+\)$", "", value) for value in md_headings]
    if html_headings != md_headings:
        raise ParityError(f"heading sequence mismatch: {page.route}")

    html_section_ids = tuple(node.attr("id") for node in find_all(main, "section") if node.attr("id"))
    md_anchors = tuple(re.findall(r'^<a id="([^"]+)"></a>$', body, re.MULTILINE))
    if html_section_ids != md_anchors:
        raise ParityError(f"section anchor sequence mismatch: {page.route}")

    html_hrefs = [node.attr("href") for node in find_all(main, "a") if node.attr("href")]
    md_hrefs = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", body)
    if html_hrefs != md_hrefs:
        raise ParityError(f"internal/external link sequence mismatch: {page.route}")
    html_downloads = [href for href in html_hrefs if href.lower().endswith(".pdf")]
    md_downloads = [href for href in md_hrefs if href.lower().endswith(".pdf")]
    if html_downloads != md_downloads:
        raise ParityError(f"PDF/download link sequence mismatch: {page.route}")

    html_images = [(node.attr("alt"), node.attr("src")) for node in find_all(main, "img")]
    md_images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body)
    if html_images != md_images:
        raise ParityError(f"body image alt/src sequence mismatch: {page.route}")

    ratio = SequenceMatcher(
        None, compact(text_of(main)), compact(markdown_text(body)), autojunk=False
    ).ratio()
    if ratio < MIN_TEXT_RATIO:
        raise ParityError(f"normalized text ratio {ratio:.6f} below {MIN_TEXT_RATIO:.3f}: {page.route}")
    return ratio


def validate() -> float:
    if tuple(page.chapter for page in PAGES[1:]) != CHAPTERS:
        raise ParityError("configured chapter sequence mismatch")
    validate_manifest()
    ratios: list[float] = []
    for page in PAGES:
        metadata, body = parse_markdown(page)
        parser = TreeParser()
        parser.feed(page.source_html.read_text(encoding="utf-8"))
        validate_metadata(page, metadata, parser)
        ratios.append(validate_structure(page, parser, body))
    return min(ratios)


def main() -> int:
    try:
        ratio = validate()
    except (OSError, KeyError, ValueError, ParityError) as exc:
        print(f"genai-shikumi series parity validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(f"genai-shikumi series parity validation: OK (9 HTML, 9 Markdown, minimum text ratio {ratio:.6f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
