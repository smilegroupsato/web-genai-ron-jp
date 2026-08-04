#!/usr/bin/env python3
"""Extract the root home index into a Markdown source candidate."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from extract_history_timeline_content import date_metadata, render_inline
from extract_site_article_to_content import Node, TreeParser, direct_children, find_all, find_first, normalize_space, text_of
from extract_tool_discovery_layer_content import front_matter, head_node

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_HTML = REPO_ROOT / "site" / "index.html"
OUTPUT_MD = REPO_ROOT / "content" / "index.md"
ROUTE = "/"
SOURCE_PATH = "site/index.html"
SECTION_IDS = ("series", "articles", "notes", "essays")


def has_class(node: Node, class_name: str) -> bool:
    return class_name in node.attr("class").split()


def first_with_class(root: Node, tag: str, class_name: str) -> Node | None:
    return next((node for node in find_all(root, tag) if has_class(node, class_name)), None)


def parse_html() -> tuple[Node, list[str]]:
    parser = TreeParser()
    parser.feed(SOURCE_HTML.read_text(encoding="utf-8"))
    return parser.root, parser.comments


def metadata_for(root: Node, comments: list[str]) -> dict[str, object]:
    body = find_first(root, "body")
    if body is None:
        raise RuntimeError("body not found")
    title_node = find_first(find_first(root, "head") or root, "title")
    description_node = head_node(root, "meta", "name", "description")
    canonical_node = head_node(root, "link", "rel", "canonical")
    dates, date_provenance = date_metadata(text_of(body), comments)
    return {
        "title": normalize_space(text_of(title_node or find_first(body, "h1") or body)),
        "route": ROUTE,
        "source_html_path": SOURCE_PATH,
        "source_html_sha256": hashlib.sha256(SOURCE_HTML.read_bytes()).hexdigest(),
        "page_type": "home",
        "series_or_article": "home",
        "order": None,
        "chapter": None,
        "meta_description": description_node.attr("content") if description_node else None,
        "canonical": canonical_node.attr("href") if canonical_node else None,
        **dates,
        "metadata_provenance": {
            "title": "html_head" if title_node else "visible_body",
            "meta_description": "html_head" if description_node else "absent",
            "canonical": "html_head" if canonical_node else "absent",
            **date_provenance,
        },
        "extraction_status": "source-reconstruction-draft",
    }


def render_links(node: Node) -> str:
    return "\n".join(f"- {render_inline([link])}" for link in find_all(node, "a"))


def render_header(header: Node) -> str:
    brand = first_with_class(header, "a", "brand")
    nav = find_first(header, "nav")
    blocks = [render_inline([brand]) if brand else ""]
    if nav:
        blocks.append(render_links(nav))
    return "\n\n".join(block for block in blocks if block)


def render_hero(hero: Node) -> str:
    blocks: list[str] = []
    for child in hero.children:
        if not isinstance(child, Node):
            continue
        if child.tag == "h1":
            blocks.append(f"# {normalize_space(text_of(child))}")
        elif child.tag == "p":
            blocks.append(render_inline(child.children))
        elif child.tag == "nav":
            blocks.append(render_links(child))
    return "\n\n".join(blocks)


def render_item(item: Node) -> str:
    title = first_with_class(item, "a", "index-title")
    caption = first_with_class(item, "p", "index-caption")
    meta = first_with_class(item, "p", "index-meta")
    blocks = [f"### {render_inline([title])}" if title else ""]
    if caption:
        blocks.append(render_inline(caption.children))
    if meta:
        blocks.append(render_inline(meta.children))
    children = first_with_class(item, "ol", "series-children")
    if children:
        blocks.append("\n".join(
            f"{index}. {render_inline(child.children)}"
            for index, child in enumerate(direct_children(children, "li"), start=1)
        ))
    item_links = first_with_class(item, "p", "index-links")
    if item_links:
        blocks.append(render_links(item_links))
    return "\n\n".join(block for block in blocks if block)


def render_section(section: Node) -> str:
    kicker = first_with_class(section, "p", "index-kicker")
    heading = find_first(first_with_class(section, "div", "section-heading") or section, "h2")
    item_list = first_with_class(section, "ol", "index-list")
    blocks = [f'<a id="{section.attr("id")}"></a>']
    if kicker:
        blocks.append(render_inline(kicker.children))
    if heading:
        blocks.append(f"## {render_inline(heading.children)}")
    if item_list:
        blocks.extend(render_item(item) for item in direct_children(item_list, "li"))
    return "\n\n".join(blocks)


def render_body(body: Node) -> str:
    header = find_first(body, "header")
    main = find_first(body, "main")
    footer = find_first(body, "footer")
    if main is None:
        raise RuntimeError("main not found")
    blocks: list[str] = []
    if header:
        blocks.append(render_header(header))
    hero = first_with_class(main, "section", "index-hero")
    if hero:
        blocks.append(render_hero(hero))
    sections = [node for node in direct_children(main, "section") if node.attr("id")]
    if tuple(node.attr("id") for node in sections) != SECTION_IDS:
        raise RuntimeError("unexpected root section sequence")
    blocks.extend(render_section(section) for section in sections)
    if footer:
        blocks.append(normalize_space(text_of(footer)))
    return "\n\n".join(block for block in blocks if block)


def extract() -> str:
    root, comments = parse_html()
    body = find_first(root, "body")
    if body is None:
        raise RuntimeError("body not found")
    return front_matter(metadata_for(root, comments)) + render_body(body).strip() + "\n"


def write_or_check(write: bool) -> None:
    rendered = extract()
    if write:
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
        print(f"root home index extraction: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(f"root home index extraction: OK ({'check' if args.check else 'write'}, 1 Markdown source)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
