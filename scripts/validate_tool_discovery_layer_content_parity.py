#!/usr/bin/env python3
"""Validate semantic parity for the tool-discovery-layer research note."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

from extract_history_timeline_content import DATE_FIELDS, date_metadata
from extract_site_article_to_content import TreeParser, find_all, find_first, normalize_space, text_of
from extract_tool_discovery_layer_content import OUTPUT_MD, ROUTE, SOURCE_HTML, SOURCE_PATH

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "site-content-salvage.manifest.json"
MIN_TEXT_RATIO = 0.995
EXPECTED_SECTION_IDS = (
    "overview", "toc", "case", "problem", "layers", "technical", "control",
    "security", "countermeasures", "public-discussion", "core", "references",
)


class ParityError(RuntimeError):
    pass


def scalar(value: str) -> object:
    value = value.strip()
    if value == "null":
        return None
    if value in {"true", "false"}:
        return value == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith('"'):
        return json.loads(value)
    return value


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


def markdown_text(body: str) -> str:
    value = re.sub(r'<a id="[^"]+"></a>', "", body)
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"^#{1,6}\s+", "", value, flags=re.MULTILINE)
    value = re.sub(r"^\s*(?:>\s*|[-*+]\s+|\d+\.\s+)", "", value, flags=re.MULTILINE)
    return value.replace("**", "").replace("*", "").replace("`", "")


def compact(value: str) -> str:
    return re.sub(r"\s+", "", value)


def validate() -> float:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    page = next((item for item in manifest["pages"] if item.get("route") == ROUTE), None)
    if page is None:
        raise ParityError("route missing from manifest")
    expected_manifest = {
        "preserve_route": True,
        "page_type": "note",
        "content_source_status": "content_source_exists",
        "corresponding_content_path": "content/notes/tool-discovery-layer/index.md",
        "salvage_status": "needs_parity_check",
    }
    for field, expected in expected_manifest.items():
        if page.get(field) != expected:
            raise ParityError(f"manifest {field} mismatch")

    metadata, body = parse_markdown()
    required = {
        "title", "route", "source_html_path", "source_html_sha256", "page_type",
        "series_or_article", "order", "chapter", "meta_description", "canonical",
        "created_at", "updated_at", "manuscript_created_at", "manuscript_updated_at",
        "web_migrated_at", "metadata_provenance", "extraction_status",
    }
    if missing := sorted(required - metadata.keys()):
        raise ParityError(f"missing metadata fields: {missing}")
    expected_metadata = {
        "route": ROUTE,
        "source_html_path": SOURCE_PATH,
        "source_html_sha256": hashlib.sha256(SOURCE_HTML.read_bytes()).hexdigest(),
        "page_type": "note",
        "series_or_article": "notes",
        "order": None,
        "chapter": None,
    }
    for field, expected in expected_metadata.items():
        if metadata.get(field) != expected:
            raise ParityError(f"metadata {field} mismatch")

    parser = TreeParser()
    parser.feed(SOURCE_HTML.read_text(encoding="utf-8"))
    main = find_first(parser.root, "main")
    if main is None:
        raise ParityError("main not found")

    html_headings = [normalize_space(text_of(node)) for node in find_all(main) if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}]
    md_headings = [normalize_space(match.group(1).replace("**", "")) for match in re.finditer(r"^#{1,6}\s+(.+)$", body, re.MULTILINE)]
    if html_headings != md_headings:
        raise ParityError("heading sequence mismatch")

    section_ids = tuple(node.attr("id") for node in find_all(main, "section") if node.attr("id"))
    md_anchors = tuple(re.findall(r'^<a id="([^"]+)"></a>$', body, re.MULTILINE))
    if section_ids != EXPECTED_SECTION_IDS or md_anchors != section_ids:
        raise ParityError("section anchor sequence mismatch")

    html_hrefs = [node.attr("href") for node in find_all(main, "a") if node.attr("href")]
    md_hrefs = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", body)
    if html_hrefs != md_hrefs:
        raise ParityError("link sequence mismatch")

    html_images = [(node.attr("alt"), node.attr("src")) for node in find_all(main, "img")]
    md_images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body)
    if html_images != md_images:
        raise ParityError("image alt/src sequence mismatch")

    dates, date_provenance = date_metadata(text_of(main), parser.comments)
    provenance = metadata.get("metadata_provenance")
    if not isinstance(provenance, dict):
        raise ParityError("metadata_provenance must be a mapping")
    for field in DATE_FIELDS:
        if metadata.get(field) != dates[field] or provenance.get(field) != date_provenance[field]:
            raise ParityError(f"date metadata mismatch: {field}")

    ratio = SequenceMatcher(None, compact(text_of(main)), compact(markdown_text(body)), autojunk=False).ratio()
    if ratio < MIN_TEXT_RATIO:
        raise ParityError(f"normalized text ratio {ratio:.6f} below {MIN_TEXT_RATIO:.3f}")
    return ratio


def main() -> int:
    try:
        ratio = validate()
    except (OSError, KeyError, ValueError, ParityError) as exc:
        print(f"tool discovery layer parity validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(f"tool discovery layer parity validation: OK (1 HTML, 1 Markdown, text ratio {ratio:.6f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
