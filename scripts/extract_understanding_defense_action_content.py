#!/usr/bin/env python3
"""Extract canonical understanding-defense-action HTML into Markdown sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

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
from extract_state_change_content import render_inline, yaml_value

REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = REPO_ROOT / "site" / "article" / "understanding-defense-action"
CONTENT_DIR = REPO_ROOT / "content" / "article" / "understanding-defense-action"
DATE_FIELDS = {
    "created_at": ("ページ作成日時", "初版公開日"),
    "updated_at": ("最終更新日時", "最終更新日"),
    "manuscript_created_at": ("Notion原稿作成日時", "原稿作成日時"),
    "manuscript_updated_at": ("Notion原稿最終更新日時", "原稿最終更新日時"),
    "web_migrated_at": ("Web移植日時",),
}


def sources() -> list[Path]:
    names = [
        "index.html",
        *(f"chapter-{number:02}.html" for number in range(0, 13)),
        "bibliography.html",
    ]
    return [SITE_DIR / name for name in names]


def output_path(source: Path) -> Path:
    return CONTENT_DIR / source.with_suffix(".md").name


def render_list(node: Node, ordered: bool) -> str:
    lines: list[str] = []
    for index, item in enumerate(direct_children(node, "li"), start=1):
        marker = f"{index}." if ordered else "-"
        lines.append(f"{marker} {render_inline(item.children)}")
    return "\n".join(lines)


def table_cells(row: Node, tags: set[str]) -> list[str]:
    return [
        render_inline(child.children)
        for child in direct_children(row)
        if child.tag in tags
    ]


def render_table(node: Node) -> str:
    rows = [
        table_cells(row, {"th", "td"})
        for row in find_all(node, "tr")
    ]
    rows = [row for row in rows if row]
    if not rows:
        return ""
    header = rows[0]
    body = rows[1:]
    width = len(header)
    lines = [
        "| " + " | ".join(cell.replace("|", "\\|") for cell in header) + " |",
        "| " + " | ".join("---" for _ in range(width)) + " |",
    ]
    for row in body:
        padded = (row + [""] * width)[:width]
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in padded) + " |")
    return "\n".join(lines)


def render_block(node: Node) -> str:
    if node.has_class("prev-next") or node.has_class("button-row"):
        return ""
    if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return f"{'#' * int(node.tag[1])} {render_inline(node.children)}"
    if node.tag == "p":
        return render_inline(node.children)
    if node.tag == "blockquote":
        return "\n".join(
            f"> {line}" for line in render_inline(node.children).splitlines() if line
        )
    if node.tag == "a":
        return render_inline([node])
    if node.tag == "ul":
        return render_list(node, ordered=False)
    if node.tag == "ol":
        return render_list(node, ordered=True)
    if node.tag == "table":
        return render_table(node)
    if node.tag == "hr":
        return "---"
    if node.tag == "pre":
        return f"```\n{text_of(node).strip()}\n```"
    rendered = [
        render_block(child).strip()
        for child in direct_children(node)
        if not child.has_class("prev-next") and not child.has_class("button-row")
    ]
    if rendered:
        return "\n\n".join(value for value in rendered if value)
    return render_inline(node.children)


def find_date(text: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        prefix_guard = r"(?<!原稿)" if label in {"最終更新日時", "最終更新日"} else ""
        match = re.search(
            rf"{prefix_guard}{re.escape(label)}[：:]\s*[\"']?"
            rf"(\d{{4}}-\d{{2}}-\d{{2}}(?:\s+\d{{2}}:\d{{2}}(?:\s+JST)?)?)",
            text,
        )
        if match:
            return normalize_space(match.group(1))
    return None


def content_nodes(root: Node, source: Path) -> tuple[Node, list[Node]]:
    if source.name == "index.html":
        article_content = find_first(root, "div", "article-content")
        article_head = find_first(article_content or root, "section", "article-head")
        title = find_first(article_head or root, "h1")
        prose = next(
            (
                node
                for node in find_all(article_content or root, "section")
                if node.has_class("prose")
            ),
            None,
        )
        if title is None or prose is None:
            raise RuntimeError(f"index content not found: {source.relative_to(REPO_ROOT)}")
        return title, direct_children(prose)

    article = next(
        (
            node
            for node in find_all(root, "article")
            if node.has_class("prose") and node.has_class("full-text")
        ),
        None,
    )
    title = find_first(article or root, "h1")
    if article is None or title is None:
        raise RuntimeError(f"full-text article not found: {source.relative_to(REPO_ROOT)}")
    return title, direct_children(article)


def metadata_for(source: Path, root: Node, comments: list[str]) -> dict[str, object]:
    route = (
        "/article/understanding-defense-action/"
        if source.name == "index.html"
        else f"/article/understanding-defense-action/{source.name}"
    )
    title_node, _ = content_nodes(root, source)
    description_node = next(
        (node for node in find_all(root, "meta") if node.attr("name") == "description"),
        None,
    )
    canonical_node = next(
        (
            node
            for node in find_all(root, "link")
            if "canonical" in node.attr("rel").lower().split()
        ),
        None,
    )
    article_content = find_first(root, "div", "article-content")
    visible = text_of(article_content) if article_content else ""
    comment_text = "\n".join(comments)
    dates: dict[str, str | None] = {}
    date_provenance: dict[str, str] = {}
    for field, labels in DATE_FIELDS.items():
        body_value = find_date(visible, labels)
        comment_value = find_date(comment_text, labels)
        if body_value is not None:
            dates[field] = body_value
            date_provenance[field] = "visible_body"
        elif comment_value is not None:
            dates[field] = comment_value
            date_provenance[field] = "html_comment"
        else:
            dates[field] = None
            date_provenance[field] = "absent"

    if source.name == "index.html":
        page_type = "article-index"
        chapter: int | str | None = None
        order = 0
    elif source.name == "bibliography.html":
        page_type = "bibliography"
        chapter = "bibliography"
        order = 14
    else:
        page_type = "article-chapter"
        chapter = int(re.search(r"(\d+)", source.stem).group(1))  # type: ignore[union-attr]
        order = chapter + 1

    return {
        "title": normalize_space(text_of(title_node)),
        "route": route,
        "source_html_path": source.relative_to(REPO_ROOT).as_posix(),
        "source_html_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "page_type": page_type,
        "series_or_article": "understanding-defense-action",
        "order": order,
        "chapter": chapter,
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


def front_matter(metadata: dict[str, object]) -> str:
    lines = ["---"]
    for key in (
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
    ):
        lines.append(f"{key}: {yaml_value(metadata.get(key))}")
    lines.append("metadata_provenance:")
    provenance = metadata["metadata_provenance"]
    assert isinstance(provenance, dict)
    for key, value in provenance.items():
        lines.append(f"  {key}: {yaml_value(value)}")
    lines.append(f"extraction_status: {yaml_value(metadata['extraction_status'])}")
    lines.extend(["---", ""])
    return "\n".join(lines)


def extract(source: Path) -> str:
    parser = TreeParser()
    parser.feed(source.read_text(encoding="utf-8"))
    title, nodes = content_nodes(parser.root, source)
    blocks = [f"# {render_inline(title.children)}"]
    for node in nodes:
        if node is title:
            continue
        rendered = render_block(node).strip()
        if rendered:
            blocks.append(rendered)
    metadata = metadata_for(source, parser.root, parser.comments)
    return front_matter(metadata) + "\n\n".join(blocks).strip() + "\n"


def generated() -> Iterable[tuple[Path, str]]:
    for source in sources():
        if not source.is_file():
            raise RuntimeError(f"source HTML not found: {source.relative_to(REPO_ROOT)}")
        yield output_path(source), extract(source)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.check:
        stale = [
            path.relative_to(REPO_ROOT).as_posix()
            for path, content in generated()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit(
                "stale understanding-defense-action extraction(s): " + ", ".join(stale)
            )
        print("understanding-defense-action extraction check: OK (15 Markdown sources)")
        return 0

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for path, content in generated():
        if path.exists() and not args.overwrite:
            raise SystemExit(f"refusing to overwrite: {path.relative_to(REPO_ROOT)}")
        path.write_text(content, encoding="utf-8")
        written += 1
    print(f"wrote {written} understanding-defense-action Markdown sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
