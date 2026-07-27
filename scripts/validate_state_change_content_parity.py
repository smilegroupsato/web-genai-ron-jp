#!/usr/bin/env python3
"""Validate semantic parity for extracted state-change Markdown sources."""

from __future__ import annotations

import json
import hashlib
import re
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from extract_site_article_to_content import (
    Child,
    Node,
    TreeParser,
    direct_children,
    find_all,
    find_first,
    normalize_space,
    text_of,
)
from extract_state_change_content import REPO_ROOT, sources

CONTENT_DIR = REPO_ROOT / "content" / "article" / "state-change"
MANIFEST_PATH = REPO_ROOT / "data" / "site-content-salvage.manifest.json"
MIN_TEXT_RATIO = 0.995
REQUIRED_METADATA = {
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
}
DATE_FIELDS = {
    "created_at",
    "updated_at",
    "manuscript_created_at",
    "manuscript_updated_at",
    "web_migrated_at",
}


class ParityError(RuntimeError):
    pass


@dataclass
class MarkdownSource:
    metadata: dict[str, object]
    body: str


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


def text_without(node: Child, excluded_class: str) -> str:
    if isinstance(node, str):
        return node
    if node.has_class(excluded_class):
        return ""
    return "".join(text_without(child, excluded_class) for child in node.children)


def html_document(source: Path) -> tuple[list[str], str, set[str]]:
    parser = TreeParser()
    parser.feed(source.read_text(encoding="utf-8"))
    title = find_first(parser.root, "h1")
    body = find_first(parser.root, "div", "article-body")
    if title is None or body is None:
        raise ParityError(f"missing h1/article-body: {source.relative_to(REPO_ROOT)}")
    headings = [normalize_space(text_of(title))]
    headings.extend(
        normalize_space(text_of(node))
        for node in find_all(body)
        if node.tag in {"h2", "h3", "h4", "h5", "h6"}
    )
    semantic_text = text_of(title) + text_without(body, "article-nav")
    dois = set(re.findall(r"DOI:\s*\S+", semantic_text))
    return headings, semantic_text, dois


def markdown_headings(body: str) -> list[str]:
    return [
        normalize_space(match.group(2))
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


def expected_route(source: Path) -> str:
    if source.name == "index.html":
        return "/article/state-change/"
    return f"/article/state-change/{source.name}"


def validate() -> tuple[int, float]:
    html_sources = sources()
    markdown_paths = sorted(CONTENT_DIR.glob("*.md"))
    if len(html_sources) != 18:
        raise ParityError(f"expected 18 canonical HTML files, found {len(html_sources)}")
    if len(markdown_paths) != len(html_sources):
        raise ParityError(
            f"HTML/Markdown count mismatch: {len(html_sources)} HTML, "
            f"{len(markdown_paths)} Markdown"
        )

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    pages = {page["route"]: page for page in manifest["pages"]}
    errors: list[str] = []
    ratios: list[float] = []

    for source in html_sources:
        markdown_path = CONTENT_DIR / source.with_suffix(".md").name
        if not markdown_path.is_file():
            errors.append(f"missing Markdown: {markdown_path.relative_to(REPO_ROOT)}")
            continue
        markdown = parse_markdown(markdown_path)
        metadata = markdown.metadata
        missing_metadata = sorted(REQUIRED_METADATA - set(metadata))
        if missing_metadata:
            errors.append(
                f"{markdown_path.name}: missing metadata fields {missing_metadata}"
            )
        source_path = metadata.get("source_html_path")
        route = metadata.get("route")
        if source_path != source.relative_to(REPO_ROOT).as_posix():
            errors.append(f"{markdown_path.name}: source_html_path mismatch")
        if not isinstance(source_path, str) or not (REPO_ROOT / source_path).is_file():
            errors.append(f"{markdown_path.name}: source_html_path does not exist")
        elif metadata.get("source_html_sha256") != hashlib.sha256(
            (REPO_ROOT / source_path).read_bytes()
        ).hexdigest():
            errors.append(f"{markdown_path.name}: source_html_sha256 mismatch")
        if route != expected_route(source) or route not in pages:
            errors.append(f"{markdown_path.name}: route missing/mismatched in manifest")
            continue

        provenance = metadata.get("metadata_provenance")
        if not isinstance(provenance, dict):
            errors.append(f"{markdown_path.name}: metadata_provenance must be a mapping")
        else:
            for field in DATE_FIELDS:
                if metadata.get(field) is not None or provenance.get(field) != "absent":
                    errors.append(
                        f"{markdown_path.name}: {field} must remain null/absent "
                        "because the source HTML contains no explicit value"
                    )

        expected_content = markdown_path.relative_to(REPO_ROOT).as_posix()
        page = pages[route]
        if page.get("content_source_status") != "content_source_exists":
            errors.append(f"{markdown_path.name}: manifest content_source_status not updated")
        if page.get("corresponding_content_path") != expected_content:
            errors.append(f"{markdown_path.name}: manifest content path mismatch")
        if page.get("salvage_status") != "needs_parity_check":
            errors.append(f"{markdown_path.name}: expected needs_parity_check")

        html_headings, html_text, html_dois = html_document(source)
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
                f"{markdown_path.name}: normalized text ratio {ratio:.6f} "
                f"is below {MIN_TEXT_RATIO:.3f}"
            )

        if source.name == "bibliography.html":
            md_dois = set(re.findall(r"DOI:\s*\S+", markdown.body))
            missing_dois = sorted(html_dois - md_dois)
            if missing_dois:
                errors.append(
                    f"bibliography.md: missing {len(missing_dois)} DOI/reference items: "
                    + ", ".join(missing_dois)
                )

    alias_pages = [
        page
        for page in manifest["pages"]
        if page["route"].startswith("/article/chapter-")
        or page["route"] == "/article/state-change.html"
    ]
    if any(page.get("salvage_status") != "alias_review" for page in alias_pages):
        errors.append("legacy state-change aliases must remain alias_review")

    if errors:
        raise ParityError("\n".join(errors))
    return len(html_sources), min(ratios)


def main() -> int:
    try:
        count, minimum_ratio = validate()
    except (OSError, ValueError, ParityError) as exc:
        print(f"state-change parity validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(
        "state-change parity validation: OK "
        f"({count} HTML, {count} Markdown, minimum text ratio {minimum_ratio:.6f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
