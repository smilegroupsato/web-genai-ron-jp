#!/usr/bin/env python3
"""Validate semantic parity for the small essay and note content sources."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from extract_site_article_to_content import TreeParser, find_all, find_first, normalize_space, text_of
from extract_small_pages_content import (
    DATE_FIELDS,
    TARGET_ROUTES,
    date_metadata,
    output_path,
    source_path,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "site-content-salvage.manifest.json"
CONTENT_PREFIXES = ("content/essay/", "content/notes/")
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
        normalize_space(
            re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", match.group(2)).replace("**", "").replace("*", "").replace("`", "")
        )
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


def html_document(source: Path) -> tuple[list[str], str, dict[str, str | None], dict[str, str]]:
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
    if not headings:
        h1 = find_first(main, "h1")
        if h1 is not None:
            headings.append(normalize_space(text_of(h1)))
    semantic_text = text_of(main)
    dates, provenance = date_metadata(semantic_text, parser.comments)
    return headings, semantic_text, dates, provenance


def target_pages(manifest: dict[str, object]) -> list[dict[str, object]]:
    pages = manifest.get("pages")
    if not isinstance(pages, list):
        raise ParityError("manifest pages must be an array")
    by_route = {page.get("route"): page for page in pages if isinstance(page.get("route"), str)}
    selected: list[dict[str, object]] = []
    for route in TARGET_ROUTES:
        page = by_route.get(route)
        if page is None:
            raise ParityError(f"route missing from manifest: {route}")
        content_path = page.get("corresponding_content_path")
        if not isinstance(content_path, str) or not content_path.startswith(CONTENT_PREFIXES):
            raise ParityError(f"route not mapped to small-page content: {route}")
        selected.append(page)
    return selected


def validate() -> tuple[int, float]:
    manifest = load_manifest()
    pages = target_pages(manifest)
    if len(pages) != len(TARGET_ROUTES):
        raise ParityError("selected page count mismatch")

    errors: list[str] = []
    ratios: list[float] = []

    for page in pages:
        route = page["route"]
        assert isinstance(route, str)
        source = source_path(route)
        markdown_path = output_path(route)
        if not source.is_file():
            errors.append(f"missing HTML: {source.relative_to(REPO_ROOT)}")
            continue
        if not markdown_path.is_file():
            errors.append(f"missing Markdown: {markdown_path.relative_to(REPO_ROOT)}")
            continue

        markdown = parse_markdown(markdown_path)
        metadata = markdown.metadata
        for field in [
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
        ]:
            if field not in metadata:
                errors.append(f"{markdown_path.name}: missing metadata field {field}")
        if metadata.get("route") != route:
            errors.append(f"{markdown_path.name}: route mismatch")
        if metadata.get("source_html_path") != source.relative_to(REPO_ROOT).as_posix():
            errors.append(f"{markdown_path.name}: source_html_path mismatch")
        if not isinstance(metadata.get("source_html_path"), str) or not source.is_file():
            errors.append(f"{markdown_path.name}: source_html_path does not exist")
        elif metadata.get("source_html_sha256") != hashlib.sha256(source.read_bytes()).hexdigest():
            errors.append(f"{markdown_path.name}: source_html_sha256 mismatch")
        if page.get("content_source_status") != "content_source_exists":
            errors.append(f"{markdown_path.name}: manifest content_source_status not updated")
        expected_content = markdown_path.relative_to(REPO_ROOT).as_posix()
        if page.get("corresponding_content_path") != expected_content:
            errors.append(f"{markdown_path.name}: manifest content path mismatch")
        if page.get("salvage_status") not in {"needs_parity_check", "done"}:
            errors.append(f"{markdown_path.name}: manifest salvage_status not set for review")

        provenance = metadata.get("metadata_provenance")
        if not isinstance(provenance, dict):
            errors.append(f"{markdown_path.name}: metadata_provenance must be a mapping")

        html_headings, html_text, html_dates, html_provenance = html_document(source)
        md_headings = markdown_headings(markdown.body)
        if html_headings != md_headings:
            errors.append(
                f"{markdown_path.name}: heading mismatch\n"
                f"  HTML={html_headings}\n  Markdown={md_headings}"
            )

        html_comp = comparable(html_text)
        md_comp = comparable(markdown_text(markdown.body))
        ratio = SequenceMatcher(None, html_comp, md_comp, autojunk=False).ratio()
        ratios.append(ratio)
        if ratio < MIN_TEXT_RATIO:
            errors.append(
                f"{markdown_path.name}: normalized text ratio {ratio:.6f} below {MIN_TEXT_RATIO:.3f}"
            )

        for field in DATE_FIELDS:
            value = metadata.get(field)
            provenance_value = None
            if isinstance(provenance, dict):
                provenance_value = provenance.get(field)
            if value != html_dates.get(field):
                errors.append(
                    f"{markdown_path.name}: {field} does not match the HTML source value"
                )
            if value is not None and provenance_value not in {"visible_body", "html_comment"}:
                errors.append(
                    f"{markdown_path.name}: {field} provenance must be visible_body or html_comment"
                )

    if errors:
        raise ParityError("\n".join(errors))
    return len(pages), min(ratios)


def main() -> int:
    try:
        count, minimum_ratio = validate()
    except (OSError, ValueError, ParityError) as exc:
        print(f"small page parity validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(
        "small page parity validation: OK "
        f"({count} HTML, {count} Markdown, minimum text ratio {minimum_ratio:.6f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
