#!/usr/bin/env python3
"""Validate semantic and structural parity for the root home index source."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

from extract_history_timeline_content import DATE_FIELDS, date_metadata
from extract_root_home_index_content import OUTPUT_MD, ROUTE, SECTION_IDS, SOURCE_HTML, SOURCE_PATH, first_with_class
from extract_site_article_to_content import TreeParser, direct_children, find_all, find_first, normalize_space, text_of
from validate_tool_discovery_layer_content_parity import compact, markdown_text, scalar

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "site-content-salvage.manifest.json"
MIN_TEXT_RATIO = 0.990
HERO_TEXT = (
    "Research Archive of Generative AI",
    "GENAI-RON",
    "生成AI論",
    "生成AIを、使い方ではなく、記憶・文脈・行為・理解・社会化の問題として読む。",
    "シリーズ、論考、研究ノート、エッセイを公開順・主題別にたどるための研究アーカイブです。",
    "Series", "Articles", "Research Notes", "Essays",
)


class ParityError(RuntimeError):
    pass


def parse_markdown() -> tuple[dict[str, object], str]:
    text = OUTPUT_MD.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ParityError("missing front matter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ParityError("unterminated front matter")
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
    matches = [item for item in manifest["pages"] if item.get("route") == ROUTE]
    if len(matches) != 1:
        raise ParityError(f"expected one root manifest route, found {len(matches)}")
    expected = {
        "preserve_route": True,
        "page_type": "home",
        "content_source_status": "content_source_exists",
        "corresponding_content_path": "content/index.md",
        "salvage_status": "needs_parity_check",
    }
    for field, value in expected.items():
        if matches[0].get(field) != value:
            raise ParityError(f"manifest {field} mismatch")


def validate_metadata(metadata: dict[str, object], parser: TreeParser) -> None:
    required = {
        "title", "route", "source_html_path", "source_html_sha256", "page_type",
        "series_or_article", "order", "chapter", "meta_description", "canonical",
        "created_at", "updated_at", "manuscript_created_at", "manuscript_updated_at",
        "web_migrated_at", "metadata_provenance", "extraction_status",
    }
    if missing := sorted(required - metadata.keys()):
        raise ParityError(f"missing metadata fields: {missing}")
    expected = {
        "title": "GENAI-RON｜生成AI論",
        "route": ROUTE,
        "source_html_path": SOURCE_PATH,
        "source_html_sha256": hashlib.sha256(SOURCE_HTML.read_bytes()).hexdigest(),
        "page_type": "home",
        "series_or_article": "home",
        "order": None,
        "chapter": None,
        "canonical": None,
    }
    for field, value in expected.items():
        if metadata.get(field) != value:
            raise ParityError(f"metadata {field} mismatch")
    body = find_first(parser.root, "body")
    if body is None:
        raise ParityError("body not found")
    dates, date_provenance = date_metadata(text_of(body), parser.comments)
    provenance = metadata.get("metadata_provenance")
    if not isinstance(provenance, dict):
        raise ParityError("metadata_provenance must be a mapping")
    for field in DATE_FIELDS:
        if metadata.get(field) != dates[field] or provenance.get(field) != date_provenance[field]:
            raise ParityError(f"date metadata mismatch: {field}")
    if any(metadata.get(field) is not None for field in DATE_FIELDS):
        raise ParityError("root date metadata must remain null")
    if provenance.get("canonical") != "absent":
        raise ParityError("missing canonical must have absent provenance")


def validate_structure(parser: TreeParser, body_text: str) -> None:
    body = find_first(parser.root, "body")
    main = find_first(parser.root, "main")
    if body is None or main is None:
        raise ParityError("body or main not found")
    if body.attr("class") != "home-index" or "index-main" not in main.attr("class").split():
        raise ParityError("root body/main class mismatch")
    for value in HERO_TEXT:
        if value not in body_text:
            raise ParityError(f"hero text missing: {value}")

    sections = [node for node in direct_children(main, "section") if node.attr("id")]
    html_section_ids = tuple(node.attr("id") for node in sections)
    md_anchors = tuple(re.findall(r'^<a id="([^"]+)"></a>$', body_text, re.MULTILINE))
    if html_section_ids != SECTION_IDS or md_anchors != SECTION_IDS:
        raise ParityError("section sequence mismatch")
    html_section_headings = [normalize_space(text_of(find_first(section, "h2") or section)) for section in sections]
    md_section_headings = [normalize_space(value) for value in re.findall(r"^##\s+(.+)$", body_text, re.MULTILINE)]
    if html_section_headings != md_section_headings:
        raise ParityError("section heading sequence mismatch")

    html_item_titles: list[str] = []
    expected_counts: list[int] = []
    for section in sections:
        item_list = first_with_class(section, "ol", "index-list")
        items = direct_children(item_list, "li") if item_list else []
        expected_counts.append(len(items))
        html_item_titles.extend(
            normalize_space(text_of(first_with_class(item, "a", "index-title") or item))
            for item in items
        )
    if expected_counts != [4, 2, 3, 2]:
        raise ParityError(f"item counts mismatch: {expected_counts}")
    md_item_titles = [
        normalize_space(re.sub(r"^\[|\]\([^)]+\)$", "", value))
        for value in re.findall(r"^###\s+(.+)$", body_text, re.MULTILINE)
    ]
    if html_item_titles != md_item_titles:
        raise ParityError("item title sequence mismatch")


def validate_links_and_images(parser: TreeParser, body_text: str) -> None:
    body = find_first(parser.root, "body")
    if body is None:
        raise ParityError("body not found")
    html_hrefs = [node.attr("href") for node in find_all(body, "a") if node.attr("href")]
    md_hrefs = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", body_text)
    if html_hrefs != md_hrefs:
        raise ParityError("internal href sequence mismatch")

    child_hrefs = [
        link.attr("href")
        for child_list in find_all(body, "ol") if "series-children" in child_list.attr("class").split()
        for link in find_all(child_list, "a") if link.attr("href")
    ]
    if [href for href in md_hrefs if href in set(child_hrefs)] != child_hrefs:
        raise ParityError("series child link sequence mismatch")
    download_hrefs = [href for href in html_hrefs if href.lower().endswith(".pdf")]
    if [href for href in md_hrefs if href.lower().endswith(".pdf")] != download_hrefs:
        raise ParityError("PDF/download link sequence mismatch")

    html_images = [(node.attr("alt"), node.attr("src")) for node in find_all(body, "img")]
    md_images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body_text)
    if html_images != md_images:
        raise ParityError("body image alt/src sequence mismatch")


def validate() -> float:
    validate_manifest()
    metadata, body_text = parse_markdown()
    parser = TreeParser()
    parser.feed(SOURCE_HTML.read_text(encoding="utf-8"))
    validate_metadata(metadata, parser)
    validate_structure(parser, body_text)
    validate_links_and_images(parser, body_text)
    body = find_first(parser.root, "body")
    if body is None:
        raise ParityError("body not found")
    ratio = SequenceMatcher(
        None, compact(text_of(body)), compact(markdown_text(body_text)), autojunk=False
    ).ratio()
    if ratio < MIN_TEXT_RATIO:
        raise ParityError(f"normalized text ratio {ratio:.6f} below {MIN_TEXT_RATIO:.3f}")
    return ratio


def main() -> int:
    try:
        ratio = validate()
    except (OSError, KeyError, ValueError, ParityError) as exc:
        print(f"root home index parity validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(f"root home index parity validation: OK (1 HTML, 1 Markdown, text ratio {ratio:.6f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
