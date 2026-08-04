#!/usr/bin/env python3
"""Validate semantic parity for the state-change literature review note."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

from extract_history_timeline_content import DATE_FIELDS, date_metadata
from extract_site_article_to_content import Node, TreeParser, find_all, find_first, normalize_space, text_of
from extract_state_change_lit_review_content import OUTPUT_MD, ROUTE, SOURCE_HTML, SOURCE_PATH
from validate_tool_discovery_layer_content_parity import compact, markdown_text, scalar

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "site-content-salvage.manifest.json"
MIN_TEXT_RATIO = 0.995
EXPECTED_SECTION_IDS = (
    "intro", "question", "unit", "group-a", "group-b", "group-c", "group-d",
    "theory", "axes", "conclusion", "program", "references",
)
EXPECTED_RESEARCH_LABELS = (
    "Research Group A", "Research Group B", "Research Group C", "Research Group D",
    "Theoretical Lines",
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


def node_with_class(root: Node, tag: str, class_name: str) -> Node | None:
    return next(
        (node for node in find_all(root, tag) if class_name in node.attr("class").split()),
        None,
    )


def validate_manifest() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    matches = [item for item in manifest["pages"] if item.get("route") == ROUTE]
    if len(matches) != 1:
        raise ParityError(f"expected one manifest route, found {len(matches)}")
    expected = {
        "preserve_route": True,
        "page_type": "note",
        "content_source_status": "content_source_exists",
        "corresponding_content_path": "content/notes/state-change-lit-review/index.md",
        "salvage_status": "needs_parity_check",
    }
    for field, value in expected.items():
        if matches[0].get(field) != value:
            raise ParityError(f"manifest {field} mismatch")


def validate_metadata(metadata: dict[str, object], parser: TreeParser, main: Node) -> None:
    required = {
        "title", "route", "source_html_path", "source_html_sha256", "page_type",
        "series_or_article", "order", "chapter", "meta_description", "canonical",
        "created_at", "updated_at", "manuscript_created_at", "manuscript_updated_at",
        "web_migrated_at", "metadata_provenance", "extraction_status",
    }
    if missing := sorted(required - metadata.keys()):
        raise ParityError(f"missing metadata fields: {missing}")
    expected = {
        "route": ROUTE,
        "source_html_path": SOURCE_PATH,
        "source_html_sha256": hashlib.sha256(SOURCE_HTML.read_bytes()).hexdigest(),
        "page_type": "note",
        "series_or_article": "notes",
        "order": None,
        "chapter": None,
        "canonical": ROUTE,
    }
    for field, value in expected.items():
        if metadata.get(field) != value:
            raise ParityError(f"metadata {field} mismatch")

    dates, date_provenance = date_metadata(text_of(main), parser.comments)
    provenance = metadata.get("metadata_provenance")
    if not isinstance(provenance, dict):
        raise ParityError("metadata_provenance must be a mapping")
    for field in DATE_FIELDS:
        if metadata.get(field) != dates[field] or provenance.get(field) != date_provenance[field]:
            raise ParityError(f"date metadata mismatch: {field}")
    if metadata.get("created_at") is not None or provenance.get("created_at") != "absent":
        raise ParityError("visible publication date must not be promoted to created_at")


def validate_structure(main: Node, body: str) -> None:
    hero = node_with_class(main, "section", "note-hero")
    sidebar = node_with_class(main, "aside", "note-sidebar")
    article = node_with_class(main, "article", "note-content")
    if hero is None or sidebar is None or article is None:
        raise ParityError("note hero, sidebar, or article structure missing")
    for class_name in ("note-kicker", "note-lead", "note-sublead", "note-meta"):
        if node_with_class(hero, "p", class_name) is None:
            raise ParityError(f"hero field missing: {class_name}")
    if "公開日：2026-06-20 JST" not in body:
        raise ParityError("visible publication date missing from Markdown body")

    section_ids = tuple(node.attr("id") for node in find_all(article, "section") if node.attr("id"))
    md_anchors = tuple(re.findall(r'^<a id="([^"]+)"></a>$', body, re.MULTILINE))
    if section_ids != EXPECTED_SECTION_IDS or md_anchors != section_ids:
        raise ParityError("section anchor sequence mismatch")

    labels = tuple(
        normalize_space(text_of(node))
        for node in find_all(article, "p")
        if "period-label" in node.attr("class").split()
    )
    if labels != EXPECTED_RESEARCH_LABELS:
        raise ParityError("research group label sequence mismatch")
    if any(label not in body for label in labels):
        raise ParityError("research group label missing from Markdown")

    references = next((node for node in find_all(article, "section") if node.attr("id") == "references"), None)
    source_list = node_with_class(references, "ol", "source-list") if references else None
    if source_list is None or len([node for node in find_all(source_list, "li")]) != 22:
        raise ParityError("reference list structure mismatch")


def validate() -> float:
    validate_manifest()
    metadata, body = parse_markdown()
    parser = TreeParser()
    parser.feed(SOURCE_HTML.read_text(encoding="utf-8"))
    main = find_first(parser.root, "main")
    if main is None:
        raise ParityError("main not found")
    validate_metadata(metadata, parser, main)
    validate_structure(main, body)

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
    html_images = [(node.attr("alt"), node.attr("src")) for node in find_all(main, "img")]
    md_images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body)
    if html_images != md_images:
        raise ParityError("image alt/src sequence mismatch")

    ratio = SequenceMatcher(
        None, compact(text_of(main)), compact(markdown_text(body)), autojunk=False
    ).ratio()
    if ratio < MIN_TEXT_RATIO:
        raise ParityError(f"normalized text ratio {ratio:.6f} below {MIN_TEXT_RATIO:.3f}")
    return ratio


def main() -> int:
    try:
        ratio = validate()
    except (OSError, KeyError, ValueError, ParityError) as exc:
        print(f"state change literature review parity validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(
        "state change literature review parity validation: "
        f"OK (1 HTML, 1 Markdown, text ratio {ratio:.6f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
