#!/usr/bin/env python3
"""Validate extracted understanding-defense-action Markdown against canonical HTML."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

from extract_site_article_to_content import (
    Child,
    TreeParser,
    find_all,
    normalize_space,
    text_of,
)
from extract_understanding_defense_action_content import (
    CONTENT_DIR,
    REPO_ROOT,
    content_nodes,
    sources,
)
from validate_state_change_content_parity import (
    DATE_FIELDS,
    REQUIRED_METADATA,
    ParityError,
    markdown_headings,
    parse_markdown,
)

MANIFEST_PATH = REPO_ROOT / "data" / "site-content-salvage.manifest.json"
MIN_TEXT_RATIO = 0.995


def text_without_navigation(node: Child) -> str:
    if isinstance(node, str):
        return node
    if node.has_class("prev-next") or node.has_class("button-row"):
        return ""
    return "".join(text_without_navigation(child) for child in node.children)


def html_document(source: Path) -> tuple[list[str], str, set[str]]:
    parser = TreeParser()
    parser.feed(source.read_text(encoding="utf-8"))
    title, nodes = content_nodes(parser.root, source)
    headings = [normalize_space(text_of(title))]
    semantic_parts = [text_of(title)]
    for node in nodes:
        if node is title:
            continue
        semantic_parts.append(text_without_navigation(node))
        headings.extend(
            normalize_space(text_of(heading))
            for heading in find_all(node)
            if heading.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}
        )
    doi_links = {
        link.attr("href")
        for node in nodes
        for link in find_all(node, "a")
        if link.attr("href").startswith("https://doi.org/")
    }
    return headings, "".join(semantic_parts), doi_links


def markdown_text(body: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    value = re.sub(r"^#{1,6}\s+", "", value, flags=re.MULTILINE)
    value = re.sub(r"^\s*(?:>\s*|[-*+]\s+|\d+\.\s+)", "", value, flags=re.MULTILINE)
    value = re.sub(
        r"^\s*\|\s*(?:---\s*\|\s*)+\s*$", "", value, flags=re.MULTILINE
    )
    value = value.replace("**", "").replace("*", "").replace("`", "")
    value = value.replace("\\|", "|").replace("|", "")
    return value


def comparable(value: str) -> str:
    return re.sub(r"\s+", "", value)


def expected_route(source: Path) -> str:
    if source.name == "index.html":
        return "/article/understanding-defense-action/"
    return f"/article/understanding-defense-action/{source.name}"


def validate_dates(
    source: Path, metadata: dict[str, object], errors: list[str]
) -> None:
    provenance = metadata.get("metadata_provenance")
    if not isinstance(provenance, dict):
        errors.append(f"{source.name}: metadata_provenance must be a mapping")
        return
    for field in DATE_FIELDS:
        if source.name == "index.html" and field in {"created_at", "updated_at"}:
            if metadata.get(field) != "2026-05-20" or provenance.get(field) != "visible_body":
                errors.append(
                    f"{source.name}: {field} must preserve explicit 2026-05-20/visible_body"
                )
        elif metadata.get(field) is not None or provenance.get(field) != "absent":
            errors.append(
                f"{source.name}: {field} must remain null/absent without source evidence"
            )


def validate() -> tuple[int, float, int]:
    html_sources = sources()
    markdown_paths = sorted(CONTENT_DIR.glob("*.md"))
    if len(html_sources) != 15:
        raise ParityError(f"expected 15 canonical HTML files, found {len(html_sources)}")
    if len(markdown_paths) != len(html_sources):
        raise ParityError(
            f"HTML/Markdown count mismatch: {len(html_sources)} HTML, "
            f"{len(markdown_paths)} Markdown"
        )

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    pages = {page["route"]: page for page in manifest["pages"]}
    errors: list[str] = []
    ratios: list[float] = []
    bibliography_links = 0

    for source in html_sources:
        markdown_path = CONTENT_DIR / source.with_suffix(".md").name
        if not markdown_path.is_file():
            errors.append(f"missing Markdown: {markdown_path.relative_to(REPO_ROOT)}")
            continue
        markdown = parse_markdown(markdown_path)
        metadata = markdown.metadata
        missing_metadata = sorted(REQUIRED_METADATA - set(metadata))
        if missing_metadata:
            errors.append(f"{markdown_path.name}: missing metadata {missing_metadata}")

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

        validate_dates(source, metadata, errors)
        expected_content = markdown_path.relative_to(REPO_ROOT).as_posix()
        page = pages[route]
        if page.get("content_source_status") != "content_source_exists":
            errors.append(f"{markdown_path.name}: manifest status not updated")
        if page.get("corresponding_content_path") != expected_content:
            errors.append(f"{markdown_path.name}: manifest content path mismatch")
        if page.get("salvage_status") != "needs_parity_check":
            errors.append(f"{markdown_path.name}: expected needs_parity_check")

        html_headings, html_text, html_doi_links = html_document(source)
        md_headings = markdown_headings(markdown.body)
        if html_headings != md_headings:
            errors.append(
                f"{markdown_path.name}: heading mismatch\n"
                f"  HTML={html_headings}\n  Markdown={md_headings}"
            )

        ratio = SequenceMatcher(
            None,
            comparable(html_text),
            comparable(markdown_text(markdown.body)),
            autojunk=False,
        ).ratio()
        ratios.append(ratio)
        if ratio < MIN_TEXT_RATIO:
            errors.append(
                f"{markdown_path.name}: normalized text ratio {ratio:.6f} "
                f"is below {MIN_TEXT_RATIO:.3f}"
            )

        if source.name == "bibliography.html":
            markdown_hrefs = set(re.findall(r"\]\((https://doi\.org/[^)]+)\)", markdown.body))
            missing_links = sorted(html_doi_links - markdown_hrefs)
            bibliography_links = len(html_doi_links)
            if missing_links:
                errors.append(
                    f"bibliography.md: missing {len(missing_links)} DOI links: "
                    + ", ".join(missing_links)
                )

    state_change_pages = [
        page
        for page in manifest["pages"]
        if page["route"].startswith("/article/state-change/")
    ]
    if any(
        page.get("content_source_status") != "content_source_exists"
        or page.get("salvage_status") != "needs_parity_check"
        for page in state_change_pages
    ):
        errors.append("previous state-change extraction state must remain unchanged")

    if errors:
        raise ParityError("\n".join(errors))
    return len(html_sources), min(ratios), bibliography_links


def main() -> int:
    try:
        count, minimum_ratio, bibliography_links = validate()
    except (OSError, ValueError, ParityError) as exc:
        print(
            f"understanding-defense-action parity validation: FAILED\n{exc}",
            file=sys.stderr,
        )
        return 1
    print(
        "understanding-defense-action parity validation: OK "
        f"({count} HTML, {count} Markdown, minimum text ratio "
        f"{minimum_ratio:.6f}, bibliography DOI links {bibliography_links})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
