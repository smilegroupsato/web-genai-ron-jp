#!/usr/bin/env python3
"""Extract the history timeline note into a Markdown content source."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from extract_site_article_to_content import (
    Child,
    Node,
    TreeParser,
    direct_children,
    find_first,
    normalize_space,
    text_of,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_HTML = REPO_ROOT / "site" / "notes" / "history-of-generative-ai" / "timeline.html"
OUTPUT_MD = REPO_ROOT / "content" / "notes" / "history-of-generative-ai" / "timeline.md"
ROUTE = "/notes/history-of-generative-ai/timeline.html"
DATE_FIELDS = {
    "created_at": ("ページ作成日時", "初版公開日"),
    "updated_at": ("最終更新日時", "最終更新日", "最終更新"),
    "manuscript_created_at": ("Notion原稿作成日時", "原稿作成日時"),
    "manuscript_updated_at": ("Notion原稿最終更新日時", "原稿最終更新日時"),
    "web_migrated_at": ("Web移植日時",),
}


def yaml_value(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def find_date(text: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        prefix_guard = r"(?<!原稿)" if label in {"最終更新日時", "最終更新日", "最終更新"} else ""
        match = re.search(
            rf"{prefix_guard}{re.escape(label)}[：:]\s*[\"']?"
            rf"(\d{{4}}-\d{{2}}-\d{{2}}"
            rf"(?:\s+\d{{2}}:\d{{2}}(?:\s+(?:JST|Z|[+-]\d{{2}}:\d{{2}}))?)?)",
            text,
        )
        if match:
            return normalize_space(match.group(1))
    return None


def date_metadata(visible_body: str, comments: list[str]) -> tuple[dict[str, str | None], dict[str, str]]:
    values: dict[str, str | None] = {}
    provenance: dict[str, str] = {}
    comment_text = "\n".join(comments)
    for field, labels in DATE_FIELDS.items():
        visible = find_date(visible_body, labels)
        comment = find_date(comment_text, labels)
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


def render_inline(children: list[Child]) -> str:
    parts: list[str] = []
    for child in children:
        if isinstance(child, str):
            parts.append(child)
            continue
        if child.tag == "a":
            label = render_inline(child.children)
            href = child.attr("href")
            parts.append(f"[{label}]({href})" if href else label)
            continue
        if child.tag == "strong":
            parts.append(f"**{render_inline(child.children)}**")
            continue
        if child.tag == "em":
            parts.append(f"*{render_inline(child.children)}*")
            continue
        if child.tag == "code":
            parts.append(f"`{text_of(child).replace('`', '\\`')}`")
            continue
        if child.tag == "br":
            parts.append("\n")
            continue
        parts.append(render_inline(child.children))
    text = "".join(parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def render_list(node: Node, ordered: bool) -> str:
    lines: list[str] = []
    for index, item in enumerate(direct_children(node, "li"), start=1):
        marker = f"{index}." if ordered else "-"
        lines.append(f"{marker} {render_inline(item.children)}")
    return "\n".join(lines)


def render_table(node: Node) -> str:
    header_cells = [render_inline(th.children) for th in direct_children(find_first(node, "thead") or node, "th")]
    rows: list[list[str]] = []
    tbody = find_first(node, "tbody") or node
    for tr in direct_children(tbody, "tr"):
        cells = [render_inline(td.children) for td in direct_children(tr, "td")]
        if cells:
            rows.append(cells)
    if not header_cells and rows:
        header_cells = [f"列{i + 1}" for i in range(len(rows[0]))]
    if not header_cells:
        return ""
    width = len(header_cells)
    lines = [
        "| " + " | ".join(cell.replace("|", "\\|") for cell in header_cells) + " |",
        "|" + "|".join("---" for _ in range(width)) + "|",
    ]
    for row in rows:
        padded = row + [""] * (width - len(row))
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in padded[:width]) + " |")
    return "\n".join(lines)


def render_block(node: Child) -> str:
    if isinstance(node, str):
        return normalize_space(node)
    if node.tag in {"footer", "nav", "script", "style"}:
        return ""
    if node.tag == "h1":
        return f"# {render_inline(node.children)}"
    if node.tag == "h2":
        return f"## {render_inline(node.children)}"
    if node.tag == "h3":
        return f"### {render_inline(node.children)}"
    if node.tag == "h4":
        return f"#### {render_inline(node.children)}"
    if node.tag == "h5":
        return f"##### {render_inline(node.children)}"
    if node.tag == "h6":
        return f"###### {render_inline(node.children)}"
    if node.tag == "p":
        return render_inline(node.children)
    if node.tag == "blockquote":
        lines = [line for line in render_children(node.children).splitlines() if line.strip()]
        if not lines:
            return ""
        return "\n".join(f"> {line}" for line in lines)
    if node.tag == "ul":
        return render_list(node, ordered=False)
    if node.tag == "ol":
        return render_list(node, ordered=True)
    if node.tag == "pre":
        return f"```\n{text_of(node).strip()}\n```"
    if node.tag == "table":
        return render_table(node)
    if node.tag == "hr":
        return "---"
    if node.tag == "img":
        alt = node.attr("alt")
        src = node.attr("src")
        return f"![{alt}]({src})" if src else alt
    if node.tag == "a":
        return render_inline([node])
    if node.tag in {"main", "article", "section", "div", "aside"}:
        return render_children(node.children)
    return render_inline(node.children)


def render_children(children: list[Child]) -> str:
    blocks = [block for block in (render_block(child).strip() for child in children) if block]
    return "\n\n".join(blocks)


def front_matter(metadata: dict[str, object]) -> str:
    fields = [
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
    ]
    lines = ["---"]
    for field in fields:
        lines.append(f"{field}: {yaml_value(metadata.get(field))}")
    lines.append("metadata_provenance:")
    provenance = metadata["metadata_provenance"]
    assert isinstance(provenance, dict)
    for key in ("title", "meta_description", "canonical", *DATE_FIELDS):
        lines.append(f"  {key}: {yaml_value(provenance.get(key))}")
    lines.append(f"extraction_status: {yaml_value(metadata['extraction_status'])}")
    lines.extend(["---", ""])
    return "\n".join(lines)


def parse_html() -> tuple[Node, list[str]]:
    parser = TreeParser()
    parser.feed(SOURCE_HTML.read_text(encoding="utf-8"))
    return parser.root, parser.comments


def metadata_for(root: Node, comments: list[str]) -> dict[str, object]:
    head = find_first(root, "head")
    head_children = [child for child in head.children if isinstance(child, Node)] if head else []
    title = normalize_space(text_of(find_first(root, "h1") or find_first(root, "title") or root))
    description_node = next(
        (node for node in head_children if node.tag == "meta" and node.attr("name") == "description"),
        None,
    )
    canonical_node = next(
        (node for node in head_children if node.tag == "link" and "canonical" in node.attr("rel").lower().split()),
        None,
    )
    main = find_first(root, "main")
    if main is None:
        raise RuntimeError("main not found")
    visible_body = text_of(main)
    dates, provenance = date_metadata(visible_body, comments)
    return {
        "title": title,
        "route": ROUTE,
        "source_html_path": "site/notes/history-of-generative-ai/timeline.html",
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
            "created_at": provenance["created_at"],
            "updated_at": provenance["updated_at"],
            "manuscript_created_at": provenance["manuscript_created_at"],
            "manuscript_updated_at": provenance["manuscript_updated_at"],
            "web_migrated_at": provenance["web_migrated_at"],
        },
        "extraction_status": "source-reconstruction-draft",
    }


def extract() -> str:
    root, comments = parse_html()
    main = find_first(root, "main")
    if main is None:
        raise RuntimeError("main not found")
    metadata = metadata_for(root, comments)
    body = render_children(main.children)
    return front_matter(metadata) + body.strip() + "\n"


def write_or_check(write: bool) -> Path:
    rendered = extract()
    if write:
        OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_MD.write_text(rendered, encoding="utf-8")
    else:
        if not OUTPUT_MD.is_file():
            raise RuntimeError("missing Markdown output")
        existing = OUTPUT_MD.read_text(encoding="utf-8")
        if existing != rendered:
            raise RuntimeError("Markdown output does not match extraction")
    return OUTPUT_MD


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify committed Markdown matches extraction output")
    args = parser.parse_args()
    try:
        write_or_check(write=not args.check)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"history timeline extraction: FAILED\n{exc}", file=sys.stderr)
        return 1
    mode = "check" if args.check else "write"
    print(f"history timeline extraction: OK ({mode}, 1 Markdown source)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
