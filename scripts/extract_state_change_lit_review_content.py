#!/usr/bin/env python3
"""Extract the state-change literature review note into Markdown."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from extract_history_timeline_content import DATE_FIELDS, date_metadata
from extract_site_article_to_content import Node, TreeParser, find_first, normalize_space, text_of
from extract_tool_discovery_layer_content import front_matter, head_node, render_main

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_HTML = REPO_ROOT / "site" / "notes" / "state-change-lit-review" / "index.html"
OUTPUT_MD = REPO_ROOT / "content" / "notes" / "state-change-lit-review" / "index.md"
ROUTE = "/notes/state-change-lit-review/"
SOURCE_PATH = "site/notes/state-change-lit-review/index.html"


def parse_html() -> tuple[Node, list[str]]:
    parser = TreeParser()
    parser.feed(SOURCE_HTML.read_text(encoding="utf-8"))
    return parser.root, parser.comments


def metadata_for(root: Node, comments: list[str]) -> dict[str, object]:
    main = find_first(root, "main")
    if main is None:
        raise RuntimeError("main not found")
    description_node = head_node(root, "meta", "name", "description")
    canonical_node = head_node(root, "link", "rel", "canonical")
    dates, date_provenance = date_metadata(text_of(main), comments)
    return {
        "title": normalize_space(text_of(find_first(main, "h1") or main)),
        "route": ROUTE,
        "source_html_path": SOURCE_PATH,
        "source_html_sha256": hashlib.sha256(SOURCE_HTML.read_bytes()).hexdigest(),
        "page_type": "note",
        "series_or_article": "notes",
        "order": None,
        "chapter": None,
        "meta_description": description_node.attr("content") if description_node else None,
        "canonical": canonical_node.attr("href") if canonical_node else None,
        **dates,
        "metadata_provenance": {
            "title": "visible_body",
            "meta_description": "html_head" if description_node else "absent",
            "canonical": "html_head" if canonical_node else "absent",
            **date_provenance,
        },
        "extraction_status": "source-reconstruction-draft",
    }


def extract() -> str:
    root, comments = parse_html()
    main = find_first(root, "main")
    if main is None:
        raise RuntimeError("main not found")
    return front_matter(metadata_for(root, comments)) + render_main(main).strip() + "\n"


def write_or_check(write: bool) -> None:
    rendered = extract()
    if write:
        OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_MD.write_text(rendered, encoding="utf-8")
    elif not OUTPUT_MD.is_file() or OUTPUT_MD.read_text(encoding="utf-8") != rendered:
        raise RuntimeError("Markdown output does not match extraction")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        write_or_check(write=not args.check)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"state change literature review extraction: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(
        "state change literature review extraction: "
        f"OK ({'check' if args.check else 'write'}, 1 Markdown source)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
