#!/usr/bin/env python3
"""Validate semantic parity for the extracted history timeline note."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from extract_history_timeline_content import DATE_FIELDS, OUTPUT_MD, ROUTE, SOURCE_HTML, date_metadata
from extract_site_article_to_content import TreeParser, find_all, find_first, normalize_space, text_of

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "site-content-salvage.manifest.json"
MIN_TEXT_RATIO = 0.990


class ParityError(RuntimeError):
    pass


@dataclass
class MarkdownSource:
    metadata: dict[str, object]
    body: str


def load_manifest() -> dict[str, object]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ParityError("manifest root must be an object")
    return manifest


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


def parse_markdown(path: Path) -> MarkdownSource:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ParityError(f"missing front matter: {path.relative_to(REPO_ROOT)}")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ParityError(f"unterminated front matter: {path.relative_to(REPO_ROOT)}")
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
    return MarkdownSource(metadata, text[end + len("\n---\n") :].strip())


def markdown_headings(body: str) -> list[str]:
    return [
        normalize_space(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", match.group(2)).replace("**", "").replace("*", "").replace("`", ""))
        for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", body, re.MULTILINE)
    ]


def markdown_text(body: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    value = re.sub(r"^#{1,6}\s+", "", value, flags=re.MULTILINE)
    value = re.sub(r"^\s*(?:>\s*|[-*+]\s+|\d+\.\s+)", "", value, flags=re.MULTILINE)
    value = value.replace("**", "").replace("*", "").replace("`", "")
    return value


def comparable(value: str) -> str:
    return re.sub(r"\s+", "", value)


def html_document(source: Path) -> tuple[list[str], str, dict[str, str | None], dict[str, str], list[str], list[str]]:
    parser = TreeParser()
    parser.feed(source.read_text(encoding="utf-8"))
    main = find_first(parser.root, "main")
    if main is None:
        raise ParityError(f"missing main: {source.relative_to(REPO_ROOT)}")
    headings = [
        normalize_space(text_of(node))
        for node in find_all(main)
        if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}
    ]
    semantic_text = text_of(main)
    dates, provenance = date_metadata(semantic_text, parser.comments)
    sources = [normalize_space(text_of(node)) for node in find_all(main, "li") if find_first(node, "a")]
    source_hrefs = []
    for node in find_all(main, "a"):
        href = node.attr("href")
        if href.startswith("http"):
            source_hrefs.append(href)
    return headings, semantic_text, dates, provenance, sources, source_hrefs


def target_page(manifest: dict[str, object]) -> dict[str, object]:
    pages = manifest.get("pages")
    if not isinstance(pages, list):
        raise ParityError("manifest pages must be an array")
    page = next((item for item in pages if item.get("route") == ROUTE), None)
    if page is None:
        raise ParityError(f"route missing from manifest: {ROUTE}")
    content_path = page.get("corresponding_content_path")
    if content_path != "content/notes/history-of-generative-ai/timeline.md":
        raise ParityError("route not mapped to timeline content source")
    return page


def validate() -> tuple[int, float]:
    manifest = load_manifest()
    page = target_page(manifest)

    if page.get("content_source_status") != "content_source_exists":
        raise ParityError("manifest content_source_status not updated")
    if page.get("salvage_status") not in {"needs_parity_check", "done"}:
        raise ParityError("manifest salvage_status not set for review")

    if not SOURCE_HTML.is_file():
        raise ParityError(f"missing HTML: {SOURCE_HTML.relative_to(REPO_ROOT)}")
    if not OUTPUT_MD.is_file():
        raise ParityError(f"missing Markdown: {OUTPUT_MD.relative_to(REPO_ROOT)}")

    markdown = parse_markdown(OUTPUT_MD)
    metadata = markdown.metadata
    required = [
        "title",
        "route",
        "source_html_path",
        "source_html_sha256",
        "page_type",
        "series_or_article",
        "order",
        "chapter",
        "meta_description",
        "canonical",
        "created_at",
        "updated_at",
        "manuscript_created_at",
        "manuscript_updated_at",
        "web_migrated_at",
        "metadata_provenance",
        "extraction_status",
    ]
    missing = [field for field in required if field not in metadata]
    if missing:
        raise ParityError(f"missing metadata fields: {missing}")

    if metadata.get("route") != ROUTE:
        raise ParityError("route mismatch")
    if metadata.get("source_html_path") != "site/notes/history-of-generative-ai/timeline.html":
        raise ParityError("source_html_path mismatch")
    if metadata.get("source_html_sha256") != hashlib.sha256(SOURCE_HTML.read_bytes()).hexdigest():
        raise ParityError("source_html_sha256 mismatch")

    html_headings, html_text, html_dates, html_provenance, html_source_items, html_source_hrefs = html_document(SOURCE_HTML)
    md_headings = markdown_headings(markdown.body)
    if html_headings != md_headings:
        raise ParityError(
            "heading mismatch\n"
            f"  HTML={html_headings}\n  Markdown={md_headings}"
        )

    html_comp = comparable(html_text)
    md_comp = comparable(markdown_text(markdown.body))
    ratio = SequenceMatcher(None, html_comp, md_comp, autojunk=False).ratio()
    if ratio < MIN_TEXT_RATIO:
        raise ParityError(f"normalized text ratio {ratio:.6f} below {MIN_TEXT_RATIO:.3f}")

    for field in DATE_FIELDS:
        if metadata.get(field) != html_dates.get(field):
            raise ParityError(f"{field} does not match the HTML source value")
    provenance = metadata.get("metadata_provenance")
    if not isinstance(provenance, dict):
        raise ParityError("metadata_provenance must be a mapping")
    for key, value in html_provenance.items():
        if value != provenance.get(key):
            raise ParityError(f"metadata provenance mismatch for {key}")

    md_source_items = [
        line.strip()
        for line in markdown.body.splitlines()
        if re.match(r"^\s*(?:[-*+]|\d+\.)\s+", line)
    ]
    if len(md_source_items) != len(html_source_items):
        raise ParityError(
            f"source list length mismatch: HTML={len(html_source_items)} Markdown={len(md_source_items)}"
        )
    md_source_hrefs = re.findall(r"\((https?://[^)]+)\)", markdown.body)
    if sorted(set(md_source_hrefs)) != sorted(set(html_source_hrefs)):
        raise ParityError("external source links are missing or altered in Markdown")

    return 1, ratio


def main() -> int:
    try:
        count, minimum_ratio = validate()
    except (OSError, ValueError, ParityError) as exc:
        print(f"history timeline parity validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(
        "history timeline parity validation: OK "
        f"({count} HTML, {count} Markdown, minimum text ratio {minimum_ratio:.6f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
