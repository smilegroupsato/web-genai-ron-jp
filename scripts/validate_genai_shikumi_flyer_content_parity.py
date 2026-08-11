#!/usr/bin/env python3
"""Validate semantic parity for the rescued genai-shikumi flyer source."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from difflib import SequenceMatcher

from extract_genai_shikumi_flyer_content import PAGE, ROUTE
from extract_history_timeline_content import DATE_FIELDS, date_metadata
from extract_site_article_to_content import TreeParser, find_all, find_first, normalize_space, text_of
from extract_tool_discovery_layer_content import head_node
from validate_genai_shikumi_series_content_parity import parse_markdown
from validate_tool_discovery_layer_content_parity import compact, markdown_text

MIN_TEXT_RATIO = 0.995


class ParityError(RuntimeError):
    pass


def validate_manifest() -> None:
    manifest_path = PAGE.output_md.parents[3] / "data" / "site-content-salvage.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    matches = [item for item in manifest["pages"] if item.get("route") == ROUTE]
    if len(matches) != 1:
        raise ParityError(f"expected one manifest route, found {len(matches)}")
    expected = {
        "preserve_route": True,
        "page_type": PAGE.page_type,
        "content_source_status": "content_source_exists",
        "corresponding_content_path": PAGE.output_path,
        "salvage_status": "needs_parity_check",
    }
    for field, value in expected.items():
        if matches[0].get(field) != value:
            raise ParityError(f"manifest {field} mismatch")


def validate_metadata(metadata: dict[str, object], parser: TreeParser) -> None:
    required = {
        "title", "route", "slug", "source_html_path", "source_html_sha256", "page_type",
        "series_or_article", "order", "chapter", "meta_description", "canonical",
        "created_at", "updated_at", "manuscript_created_at", "manuscript_updated_at",
        "web_migrated_at", "metadata_provenance", "extraction_status",
    }
    if missing := sorted(required - metadata.keys()):
        raise ParityError(f"missing front matter fields: {missing}")
    main = find_first(parser.root, "main")
    if main is None:
        raise ParityError("main not found")
    description = head_node(parser.root, "meta", "name", "description")
    expected = {
        "title": normalize_space(text_of(find_first(main, "h1") or main)),
        "route": ROUTE,
        "slug": ROUTE,
        "source_html_path": PAGE.source_html_path,
        "source_html_sha256": hashlib.sha256(PAGE.source_html.read_bytes()).hexdigest(),
        "page_type": "series-support",
        "series_or_article": "genai-shikumi",
        "order": None,
        "chapter": None,
        "meta_description": description.attr("content") if description else None,
        "canonical": None,
        "extraction_status": "source-reconstruction-draft",
    }
    for field, value in expected.items():
        if metadata.get(field) != value:
            raise ParityError(f"front matter {field} mismatch")

    dates, provenance_dates = date_metadata(text_of(main), parser.comments)
    provenance = metadata.get("metadata_provenance")
    if not isinstance(provenance, dict):
        raise ParityError("metadata_provenance must be a mapping")
    expected_provenance = {
        "title": "visible_body",
        "meta_description": "html_head" if description else "absent",
        "canonical": "absent",
        **provenance_dates,
    }
    for field in DATE_FIELDS:
        if metadata.get(field) != dates[field]:
            raise ParityError(f"date front matter mismatch: {field}")
    for field, value in expected_provenance.items():
        if provenance.get(field) != value:
            raise ParityError(f"metadata provenance mismatch: {field}")


def validate_structure(parser: TreeParser, body: str) -> tuple[float, int]:
    main = find_first(parser.root, "main")
    if main is None:
        raise ParityError("main not found")
    html_headings = [
        normalize_space(text_of(node)) for node in find_all(main)
        if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}
    ]
    md_headings = [
        normalize_space(match.group(1).replace("**", ""))
        for match in re.finditer(r"^#{1,6}\s+(.+)$", body, re.MULTILINE)
    ]
    if html_headings != md_headings:
        raise ParityError("heading sequence mismatch")

    html_hrefs = [node.attr("href") for node in find_all(main, "a") if node.attr("href")]
    md_hrefs = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", body)
    if html_hrefs != md_hrefs:
        raise ParityError("link sequence mismatch")
    html_downloads = [href for href in html_hrefs if href.lower().endswith(".pdf")]
    md_downloads = [href for href in md_hrefs if href.lower().endswith(".pdf")]
    if html_downloads != md_downloads:
        raise ParityError("PDF/download link sequence mismatch")

    html_images = [(node.attr("alt"), node.attr("src")) for node in find_all(main, "img")]
    md_images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body)
    if html_images != md_images:
        raise ParityError("image alt/src sequence mismatch")

    # Image parity is checked above. HTML ``text_of`` excludes img alt text, so
    # exclude the Markdown image token from the visible-text comparison too.
    text_body = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", body)
    ratio = SequenceMatcher(
        None, compact(text_of(main)), compact(markdown_text(text_body)), autojunk=False
    ).ratio()
    if ratio < MIN_TEXT_RATIO:
        raise ParityError(f"normalized text ratio {ratio:.6f} below {MIN_TEXT_RATIO:.3f}")
    return ratio, len(html_downloads)


def validate() -> tuple[float, int]:
    validate_manifest()
    metadata, body = parse_markdown(PAGE)
    parser = TreeParser()
    parser.feed(PAGE.source_html.read_text(encoding="utf-8"))
    validate_metadata(metadata, parser)
    return validate_structure(parser, body)


def main() -> int:
    try:
        ratio, downloads = validate()
    except (OSError, KeyError, ValueError, ParityError) as exc:
        print(f"genai-shikumi flyer parity validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(
        "genai-shikumi flyer parity validation: OK "
        f"(1 HTML, 1 Markdown, {downloads} download links, text ratio {ratio:.6f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
