#!/usr/bin/env python3
"""Extract the nine public genai-shikumi series pages into Markdown sources."""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

from extract_history_timeline_content import DATE_FIELDS, date_metadata, render_children
from extract_site_article_to_content import Node, TreeParser, find_first, normalize_space, text_of
from extract_tool_discovery_layer_content import head_node, yaml_value

REPO_ROOT = Path(__file__).resolve().parents[1]
SERIES = "genai-shikumi"


@dataclass(frozen=True)
class Page:
    route: str
    source_html_path: str
    output_path: str
    page_type: str
    order: int | None
    chapter: str | None

    @property
    def source_html(self) -> Path:
        return REPO_ROOT / self.source_html_path

    @property
    def output_md(self) -> Path:
        return REPO_ROOT / self.output_path


CHAPTERS = (
    "01-memory", "02-prompt", "03-tools", "04-context", "05-forgetting",
    "06-understanding", "07-workflow", "08-context-design",
)
PAGES = (
    Page(
        route="/series/genai-shikumi/",
        source_html_path="site/series/genai-shikumi/index.html",
        output_path="content/series/genai-shikumi/index.md",
        page_type="series-index",
        order=None,
        chapter=None,
    ),
    *(
        Page(
            route=f"/series/genai-shikumi/{chapter}/",
            source_html_path=f"site/series/genai-shikumi/{chapter}/index.html",
            output_path=f"content/series/genai-shikumi/{chapter}.md",
            page_type="series-entry",
            order=index,
            chapter=chapter,
        )
        for index, chapter in enumerate(CHAPTERS, start=1)
    ),
)


def parse_html(page: Page) -> tuple[Node, list[str]]:
    parser = TreeParser()
    parser.feed(page.source_html.read_text(encoding="utf-8"))
    return parser.root, parser.comments


def front_matter(metadata: dict[str, object]) -> str:
    fields = (
        "title", "route", "slug", "source_html_path", "source_html_sha256", "page_type",
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


def metadata_for(page: Page, root: Node, comments: list[str]) -> dict[str, object]:
    main = find_first(root, "main")
    if main is None:
        raise RuntimeError(f"main not found: {page.route}")
    description_node = head_node(root, "meta", "name", "description")
    canonical_node = head_node(root, "link", "rel", "canonical")
    dates, date_provenance = date_metadata(text_of(main), comments)
    return {
        "title": normalize_space(text_of(find_first(main, "h1") or main)),
        "route": page.route,
        "slug": page.route,
        "source_html_path": page.source_html_path,
        "source_html_sha256": hashlib.sha256(page.source_html.read_bytes()).hexdigest(),
        "page_type": page.page_type,
        "series_or_article": SERIES,
        "order": page.order,
        "chapter": page.chapter,
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


def extract(page: Page) -> str:
    root, comments = parse_html(page)
    main = find_first(root, "main")
    if main is None:
        raise RuntimeError(f"main not found: {page.route}")
    return front_matter(metadata_for(page, root, comments)) + render_main(main).strip() + "\n"


def render_main(main: Node) -> str:
    """Render visible main content and retain direct or one-level nested section ids."""
    blocks: list[str] = []
    for child in main.children:
        if not isinstance(child, Node):
            value = normalize_space(child)
            if value:
                blocks.append(value)
            continue
        if child.tag == "section":
            anchor = f'<a id="{child.attr("id")}"></a>\n\n' if child.attr("id") else ""
            blocks.append(anchor + render_children(child.children))
            continue
        if child.tag == "div":
            nested: list[str] = []
            for descendant in child.children:
                if not isinstance(descendant, Node):
                    value = normalize_space(descendant)
                    if value:
                        nested.append(value)
                    continue
                if descendant.tag == "section":
                    anchor = (
                        f'<a id="{descendant.attr("id")}"></a>\n\n'
                        if descendant.attr("id") else ""
                    )
                    nested.append(anchor + render_children(descendant.children))
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


def write_or_check(write: bool) -> None:
    for page in PAGES:
        rendered = extract(page)
        if write:
            page.output_md.parent.mkdir(parents=True, exist_ok=True)
            page.output_md.write_text(rendered, encoding="utf-8")
        elif not page.output_md.is_file() or page.output_md.read_text(encoding="utf-8") != rendered:
            raise RuntimeError(f"Markdown output does not match extraction: {page.output_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        write_or_check(write=not args.check)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"genai-shikumi series extraction: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(f"genai-shikumi series extraction: OK ({'check' if args.check else 'write'}, 9 Markdown sources)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
