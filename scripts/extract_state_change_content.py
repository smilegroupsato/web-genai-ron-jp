#!/usr/bin/env python3
"""Extract canonical state-change article HTML into reviewable Markdown sources."""

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

REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = REPO_ROOT / "site" / "article" / "state-change"
CONTENT_DIR = REPO_ROOT / "content" / "article" / "state-change"
DATE_FIELDS = {
    "created_at": ("ページ作成日時",),
    "updated_at": ("最終更新日時",),
    "manuscript_created_at": ("Notion原稿作成日時", "原稿作成日時"),
    "manuscript_updated_at": ("Notion原稿最終更新日時", "原稿最終更新日時"),
    "web_migrated_at": ("Web移植日時",),
}


def sources() -> list[Path]:
    names = ["index.html", *(f"chapter-{number:02}.html" for number in range(1, 17)), "bibliography.html"]
    return [SITE_DIR / name for name in names]


def output_path(source: Path) -> Path:
    return CONTENT_DIR / source.with_suffix(".md").name


def yaml_value(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def render_inline(children: list[Child]) -> str:
    parts: list[str] = []
    for child in children:
        if isinstance(child, str):
            parts.append(child)
        elif child.tag == "a":
            label = render_inline(child.children)
            href = child.attr("href")
            parts.append(f"[{label}]({href})" if href else label)
        elif child.tag == "strong":
            parts.append(f"**{render_inline(child.children)}**")
        elif child.tag == "em":
            parts.append(f"*{render_inline(child.children)}*")
        elif child.tag == "code":
            parts.append(f"`{text_of(child).replace('`', '\\`')}`")
        elif child.tag == "br":
            parts.append("\n")
        else:
            parts.append(render_inline(child.children))
    return re.sub(r"[ \t]+", " ", "".join(parts)).strip()


def render_list(node: Node, ordered: bool) -> str:
    lines: list[str] = []
    for index, item in enumerate(direct_children(node, "li"), start=1):
        marker = f"{index}." if ordered else "-"
        lines.append(f"{marker} {render_inline(item.children)}")
    return "\n".join(lines)


def render_block(node: Node) -> str:
    if node.has_class("article-nav"):
        return ""
    if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return f"{'#' * int(node.tag[1])} {render_inline(node.children)}"
    if node.tag == "p":
        return render_inline(node.children)
    if node.tag == "blockquote":
        lines = render_inline(node.children).splitlines() or [render_inline(node.children)]
        return "\n".join(f"> {line}" for line in lines if line)
    if node.tag == "a":
        return render_inline([node])
    if node.tag == "ul":
        return render_list(node, ordered=False)
    if node.tag == "ol":
        return render_list(node, ordered=True)
    if node.tag == "hr":
        return "---"
    if node.tag == "pre":
        return f"```\n{text_of(node).strip()}\n```"
    rendered_children = [
        render_block(child).strip()
        for child in direct_children(node)
        if not child.has_class("article-nav")
    ]
    if rendered_children:
        return "\n\n".join(value for value in rendered_children if value)
    return render_inline(node.children)


def find_date(text: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        prefix_guard = r"(?<!原稿)" if label == "最終更新日時" else ""
        match = re.search(
            rf"{prefix_guard}{re.escape(label)}[：:]\s*[\"']?"
            rf"([^\"'<>\n\r|/]+?(?:JST|Z|[+-]\d{{2}}:\d{{2}}))",
            text,
        )
        if match:
            return normalize_space(match.group(1))
    return None


def date_metadata(
    visible_body: str, comments: str
) -> tuple[dict[str, str | None], dict[str, str]]:
    values: dict[str, str | None] = {}
    provenance: dict[str, str] = {}
    for field, labels in DATE_FIELDS.items():
        visible = find_date(visible_body, labels)
        comment = find_date(comments, labels)
        if visible is not None:
            values[field] = visible
            provenance[field] = "visible_body"
        elif comment is not None:
            values[field] = comment
            provenance[field] = "html_comment"
        else:
            values[field] = None
            provenance[field] = "absent"
    return values, provenance


def metadata_for(source: Path, root: Node, comments: list[str]) -> dict[str, object]:
    route = "/article/state-change/" if source.name == "index.html" else f"/article/state-change/{source.name}"
    title_node = find_first(root, "h1")
    title = normalize_space(text_of(title_node)) if title_node else ""
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
    body_node = find_first(root, "div", "article-body")
    visible_body = text_of(body_node) if body_node else ""
    dates, date_provenance = date_metadata(visible_body, "\n".join(comments))

    if source.name == "index.html":
        page_type = "article-index"
        chapter: int | str | None = None
        order = 0
    elif source.name == "bibliography.html":
        page_type = "bibliography"
        chapter = "bibliography"
        order = 17
    else:
        page_type = "article-chapter"
        chapter = int(re.search(r"(\d+)", source.stem).group(1))  # type: ignore[union-attr]
        order = chapter

    provenance = {
        "title": "visible_body",
        "meta_description": "html_head" if description_node else "absent",
        "canonical": "html_head" if canonical_node else "absent",
        **date_provenance,
    }
    return {
        "title": title,
        "route": route,
        "source_html_path": source.relative_to(REPO_ROOT).as_posix(),
        "source_html_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "page_type": page_type,
        "series_or_article": "state-change",
        "order": order,
        "chapter": chapter,
        "meta_description": description_node.attr("content") if description_node else None,
        "canonical": canonical_node.attr("href") if canonical_node else None,
        **dates,
        "metadata_provenance": provenance,
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
    root = parser.root
    body = find_first(root, "div", "article-body")
    if body is None:
        raise RuntimeError(f"article-body not found: {source.relative_to(REPO_ROOT)}")
    title = find_first(root, "h1")
    if title is None:
        raise RuntimeError(f"h1 not found: {source.relative_to(REPO_ROOT)}")

    blocks = [f"# {render_inline(title.children)}"]
    for child in direct_children(body):
        rendered = render_block(child).strip()
        if rendered:
            blocks.append(rendered)
    metadata = metadata_for(source, root, parser.comments)
    return front_matter(metadata) + "\n\n".join(blocks).strip() + "\n"


def generated() -> Iterable[tuple[Path, str]]:
    for source in sources():
        if not source.is_file():
            raise RuntimeError(f"source HTML not found: {source.relative_to(REPO_ROOT)}")
        yield output_path(source), extract(source)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when extracted Markdown is stale")
    parser.add_argument("--overwrite", action="store_true", help="replace existing extracted Markdown")
    args = parser.parse_args()

    if args.check:
        stale = [
            path.relative_to(REPO_ROOT).as_posix()
            for path, content in generated()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit("stale state-change extraction(s): " + ", ".join(stale))
        print("state-change extraction check: OK (18 Markdown sources)")
        return 0

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for path, content in generated():
        if path.exists() and not args.overwrite:
            raise SystemExit(f"refusing to overwrite existing content source: {path.relative_to(REPO_ROOT)}")
        path.write_text(content, encoding="utf-8")
        written += 1
    print(f"wrote {written} state-change Markdown sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
