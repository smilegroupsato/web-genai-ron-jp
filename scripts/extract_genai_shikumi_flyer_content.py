#!/usr/bin/env python3
"""Extract the public genai-shikumi flyer into a Markdown source."""

from __future__ import annotations

import argparse
import sys

from extract_genai_shikumi_series_content import Page, front_matter, metadata_for, parse_html
from extract_history_timeline_content import render_children
from extract_site_article_to_content import Node, find_first, normalize_space

ROUTE = "/series/genai-shikumi/flyer/"
PAGE = Page(
    route=ROUTE,
    source_html_path="site/series/genai-shikumi/flyer/index.html",
    output_path="content/series/genai-shikumi/flyer.md",
    page_type="series-support",
    order=None,
    chapter=None,
)


def render_main(main: Node) -> str:
    """Render every visible main block, including the flyer's visible footer."""
    blocks: list[str] = []
    for child in main.children:
        if not isinstance(child, Node):
            value = normalize_space(child)
            if value:
                blocks.append(value)
            continue
        rendered = (
            render_children(child.children)
            if child.tag == "footer"
            else render_children([child])
        )
        if rendered:
            blocks.append(rendered)
    return "\n\n".join(blocks)


def extract() -> str:
    root, comments = parse_html(PAGE)
    main = find_first(root, "main")
    if main is None:
        raise RuntimeError(f"main not found: {ROUTE}")
    return front_matter(metadata_for(PAGE, root, comments)) + render_main(main).strip() + "\n"


def write_or_check(write: bool) -> None:
    rendered = extract()
    if write:
        PAGE.output_md.parent.mkdir(parents=True, exist_ok=True)
        PAGE.output_md.write_text(rendered, encoding="utf-8")
    elif not PAGE.output_md.is_file() or PAGE.output_md.read_text(encoding="utf-8") != rendered:
        raise RuntimeError(f"Markdown output does not match extraction: {PAGE.output_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        write_or_check(write=not args.check)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"genai-shikumi flyer extraction: FAILED\n{exc}", file=sys.stderr)
        return 1
    mode = "check" if args.check else "write"
    print(f"genai-shikumi flyer extraction: OK ({mode}, 1 Markdown source)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
