#!/usr/bin/env python3
"""Extract the tool-discovery-layer research note into Markdown."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from extract_history_timeline_content import DATE_FIELDS, date_metadata, render_children
from extract_site_article_to_content import Node, TreeParser, find_first, normalize_space, text_of

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_HTML = REPO_ROOT / "site" / "notes" / "tool-discovery-layer" / "index.html"
OUTPUT_MD = REPO_ROOT / "content" / "notes" / "tool-discovery-layer" / "index.md"
ROUTE = "/notes/tool-discovery-layer/"
SOURCE_PATH = "site/notes/tool-discovery-layer/index.html"


def yaml_value(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def front_matter(metadata: dict[str, object]) -> str:
    fields = (
        "title", "route", "source_html_path", "source_html_sha256", "page_type",
        "series_or_article", "order", "chapter", "meta_description", "canonical",
        "created_at", "updated_at", "manuscript_created_at", "manuscript_updated_at",
        "web_migrated_at",
    )
    lines = ["---", *(f"{field}: {yaml_value(metadata.get(field))}" for field in fields)]
    lines.append("metadata_provenance:")
    provenance = metadata["metadata_provenance"]
    assert isinstance(provenance, dict)
    for key in ("title", "meta_description", "canonical", *DATE_FIELDS):
        lines.append(f"  {key}: {yaml_value(provenance.get(key))}")
    lines.extend([
        f"extraction_status: {yaml_value(metadata['extraction_status'])}",
        "---",
        "",
    ])
    return "\n".join(lines)


def parse_html() -> tuple[Node, list[str]]:
    parser = TreeParser()
    parser.feed(SOURCE_HTML.read_text(encoding="utf-8"))
    return parser.root, parser.comments


def head_node(root: Node, tag: str, attribute: str, expected: str) -> Node | None:
    head = find_first(root, "head")
    if head is None:
        return None
    return next(
        (
            child for child in head.children
            if isinstance(child, Node)
            and child.tag == tag
            and expected in child.attr(attribute).lower().split()
        ),
        None,
    )


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


def render_main(main: Node) -> str:
    """Render all visible main content and preserve section ids as explicit anchors."""
    blocks: list[str] = []
    for child in main.children:
        if not isinstance(child, Node):
            value = normalize_space(child)
            if value:
                blocks.append(value)
            continue
        if child.tag == "section" and child.attr("id"):
            blocks.append(f'<a id="{child.attr("id")}"></a>\n\n{render_children(child.children)}')
            continue
        if child.tag == "div":
            nested: list[str] = []
            for descendant in child.children:
                if isinstance(descendant, Node) and descendant.tag == "article":
                    for section in descendant.children:
                        if isinstance(section, Node) and section.tag == "section" and section.attr("id"):
                            nested.append(
                                f'<a id="{section.attr("id")}"></a>\n\n'
                                f'{render_children(section.children)}'
                            )
                        elif isinstance(section, Node):
                            rendered = render_children(section.children)
                            if rendered:
                                nested.append(rendered)
                    continue
                rendered = render_children([descendant])
                if rendered:
                    nested.append(rendered)
            blocks.append("\n\n".join(nested))
            continue
        rendered = render_children([child])
        if rendered:
            blocks.append(rendered)
    return "\n\n".join(blocks)


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
        print(f"tool discovery layer extraction: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(f"tool discovery layer extraction: OK ({'check' if args.check else 'write'}, 1 Markdown source)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
