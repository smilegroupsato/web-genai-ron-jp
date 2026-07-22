#!/usr/bin/env python3
"""Extract existing site article HTML into content/ Markdown sources.

This helper is intentionally conservative. It is for migration/recovery work:
- read current public HTML under site/
- extract article text, headings, notes, code, tables, references, and nav
- write Markdown under content/
- skip existing content files unless --overwrite is passed

It is not a general HTML-to-Markdown converter. It is tailored to the current
GENAI-RON article page structure so that old generated HTML can be turned back
into source-like Markdown and reviewed before using it as a content source.
"""

from __future__ import annotations

import argparse
import html
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Union
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPO_ROOT / "site"
CONTENT_ROOT = REPO_ROOT / "content"

Child = Union["Node", str]


@dataclass
class Node:
    tag: str
    attrs: Dict[str, str] = field(default_factory=dict)
    children: List[Child] = field(default_factory=list)

    def attr(self, name: str, default: str = "") -> str:
        return self.attrs.get(name, default)

    def has_class(self, class_name: str) -> bool:
        return class_name in self.attr("class", "").split()


class TreeParser(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack: List[Node] = [self.root]
        self.comments: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
        node = Node(tag, {key: value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if tag not in self.VOID_TAGS:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if data:
            self.stack[-1].children.append(data)

    def handle_comment(self, data: str) -> None:
        self.comments.append(data.strip())


def text_of(node: Child) -> str:
    if isinstance(node, str):
        return node
    return "".join(text_of(child) for child in node.children)


def find_first(node: Node, tag: str | None = None, class_name: str | None = None) -> Node | None:
    if (tag is None or node.tag == tag) and (class_name is None or node.has_class(class_name)):
        return node
    for child in node.children:
        if isinstance(child, Node):
            found = find_first(child, tag, class_name)
            if found:
                return found
    return None


def find_all(node: Node, tag: str | None = None, class_name: str | None = None) -> List[Node]:
    found: List[Node] = []
    if (tag is None or node.tag == tag) and (class_name is None or node.has_class(class_name)):
        found.append(node)
    for child in node.children:
        if isinstance(child, Node):
            found.extend(find_all(child, tag, class_name))
    return found


def direct_children(node: Node, tag: str | None = None) -> List[Node]:
    return [child for child in node.children if isinstance(child, Node) and (tag is None or child.tag == tag)]


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def escape_md_table_cell(text: str) -> str:
    return text.replace("|", "\\|").strip()


def render_inline(children: List[Child]) -> str:
    parts: List[str] = []
    for child in children:
        if isinstance(child, str):
            parts.append(child)
            continue
        if child.tag == "code":
            code = text_of(child).replace("`", "\\`")
            parts.append(f"`{code}`")
            continue
        if child.tag == "a":
            label = normalize_space(render_inline(child.children))
            href = child.attr("href")
            if href:
                parts.append(f"[{label}]({href})")
            else:
                parts.append(label)
            continue
        parts.append(render_inline(child.children))
    return normalize_space("".join(parts))


def render_pre(node: Node) -> str:
    code = find_first(node, "code")
    source = text_of(code or node).rstrip("\n")
    if node.has_class("article-phrase"):
        lang = "text"
    else:
        class_attr = (code or node).attr("class", "") if isinstance(code or node, Node) else ""
        match = re.search(r"language-([A-Za-z0-9_-]+)", class_attr)
        lang = match.group(1) if match else ""
    return f"```{lang}\n{source}\n```"


def render_table(node: Node) -> str:
    header_cells = [render_inline(th.children) for th in find_all(find_first(node, "thead") or node, "th")]
    rows: List[List[str]] = []
    tbody = find_first(node, "tbody") or node
    for tr in find_all(tbody, "tr"):
        cells = [render_inline(td.children) for td in direct_children(tr, "td")]
        if cells:
            rows.append(cells)
    if not header_cells and rows:
        header_cells = [f"列{i + 1}" for i in range(len(rows[0]))]
    if not header_cells:
        return ""
    width = len(header_cells)
    out = [
        "| " + " | ".join(escape_md_table_cell(cell) for cell in header_cells) + " |",
        "|" + "|".join("---" for _ in range(width)) + "|",
    ]
    for row in rows:
        padded = row + [""] * (width - len(row))
        out.append("| " + " | ".join(escape_md_table_cell(cell) for cell in padded[:width]) + " |")
    return "\n".join(out)


def render_list(node: Node) -> str:
    lines: List[str] = []
    for li in direct_children(node, "li"):
        lines.append(f"- {render_inline(li.children)}")
    return "\n".join(lines)


def render_block(node: Node, nav_meta: Dict[str, str]) -> str:
    if node.tag == "h2":
        return f"## {render_inline(node.children)}"
    if node.tag == "p":
        return render_inline(node.children)
    if node.tag == "blockquote":
        body = "\n\n".join(render_block(child, nav_meta) for child in direct_children(node) if render_block(child, nav_meta))
        if not body:
            body = normalize_space(text_of(node))
        return f":::note\n{body}\n:::"
    if node.tag == "pre":
        return render_pre(node)
    if node.tag == "table":
        return render_table(node)
    if node.tag in {"ul", "ol"}:
        return render_list(node)
    if node.tag == "nav" and node.has_class("article-link"):
        extract_nav(node, nav_meta)
        return ""
    return normalize_space(text_of(node))


def extract_nav(node: Node, nav_meta: Dict[str, str]) -> None:
    for link in find_all(node, "a"):
        label = normalize_space(text_of(link))
        href = link.attr("href")
        if label.startswith("前へ"):
            nav_meta["previous_label"] = label
            nav_meta["previous_href"] = href
        elif label.startswith("次へ"):
            nav_meta["next_label"] = label
            nav_meta["next_href"] = href
        elif "トップ" in label:
            nav_meta["top_label"] = label
            nav_meta["top_href"] = href


def parse_comment_metadata(comments: List[str]) -> Dict[str, str]:
    meta: Dict[str, str] = {}
    joined = " / ".join(comments)
    patterns = {
        "original_notion_created_at": r"Notion原稿作成日時：([^/]+)",
        "original_notion_updated_at": r"Notion原稿最終更新日時：([^/]+)",
        "web_migrated_at": r"Web移植日時：([^/]+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, joined)
        if match:
            meta[key] = match.group(1).strip()
    return meta


def deep_dive_output_path(site_path: Path) -> Path:
    rel = site_path.relative_to(SITE_ROOT)
    parts = rel.parts
    if len(parts) >= 4 and parts[0] == "series" and parts[1] == "genai-shikumi-deep-dive" and parts[-1] == "index.html":
        slug = parts[2]
        return CONTENT_ROOT / "series" / "genai-shikumi-deep-dive" / f"{slug}.md"
    raise ValueError(f"cannot infer content output path from {site_path}")


def source_blob_sha(site_path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(site_path)], cwd=REPO_ROOT, text=True).strip()


def extract_article(site_path: Path) -> Tuple[Dict[str, str], str]:
    parser = TreeParser()
    parser.feed(site_path.read_text(encoding="utf-8"))
    root = parser.root

    article = find_first(root, "article", "note-box")
    if not article:
        raise RuntimeError(f"article.note-box not found: {site_path}")

    title_node = find_first(root, "h1")
    subtitle_node = find_first(root, "p", "series-subtitle")
    kicker_node = find_first(root, "p", "series-kicker")
    description_node = next((m for m in find_all(root, "meta") if m.attr("name") == "description"), None)

    title = normalize_space(text_of(title_node)) if title_node else site_path.parent.name
    subtitle = normalize_space(text_of(subtitle_node)) if subtitle_node else ""
    kicker = normalize_space(text_of(kicker_node)) if kicker_node else ""
    description = description_node.attr("content") if description_node else subtitle

    order_display_match = re.search(r"(\d{2})$", kicker)
    order_display = order_display_match.group(1) if order_display_match else ""
    order_int = str(int(order_display)) if order_display.isdigit() else ""
    series_label = kicker[: -len(order_display)].strip() if order_display else "生成AIのしくみ 超詳解"

    slug = "/" + str(site_path.parent.relative_to(SITE_ROOT)).strip("/") + "/"
    canonical = "https://genai-ron.jp" + slug

    nav_meta: Dict[str, str] = {}
    blocks: List[str] = []
    first_content_block = True
    for child in direct_children(article):
        # Drop old visible page timestamp lists from reconstructed public content.
        if first_content_block and child.tag == "ul" and "ページ作成日時" in text_of(child) and "最終更新日時" in text_of(child):
            continue
        first_content_block = False
        rendered = render_block(child, nav_meta).strip()
        if rendered:
            blocks.append(rendered)

    now = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M JST")
    meta: Dict[str, str] = {
        "ページ作成日時": now,
        "最終更新日時": now,
        "id": f"genai-shikumi-deep-dive-{order_display or site_path.parent.name}",
        "title": title,
        "subtitle": subtitle,
        "series": "genai-shikumi-deep-dive",
        "series_label": series_label,
        "series_order": order_int,
        "order_display": order_display,
        "slug": slug,
        "canonical_url": canonical,
        "description": description,
        "source_reconstruction_from": str(site_path.relative_to(REPO_ROOT)),
        "source_html_blob_sha": source_blob_sha(site_path),
        "status": "source-reconstruction-draft",
    }
    meta.update(parse_comment_metadata(parser.comments))
    meta.update(nav_meta)

    return meta, "\n\n".join(blocks).strip() + "\n"


def front_matter(meta: Dict[str, str]) -> str:
    ordered_keys = [
        "ページ作成日時",
        "最終更新日時",
        "id",
        "title",
        "subtitle",
        "series",
        "series_label",
        "series_order",
        "order_display",
        "previous_label",
        "previous_href",
        "next_label",
        "next_href",
        "top_label",
        "top_href",
        "slug",
        "canonical_url",
        "description",
        "source_reconstruction_from",
        "source_html_blob_sha",
        "original_notion_created_at",
        "original_notion_updated_at",
        "web_migrated_at",
        "status",
    ]
    lines = ["---"]
    for key in ordered_keys:
        value = meta.get(key, "")
        if value:
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}: "{escaped}"')
    lines.extend([
        "exclude_from_public_body:",
        '  - "更新履歴"',
        '  - "作業履歴"',
        '  - "内部TODO"',
        '  - "変換ログ"',
        "rendering_contract:",
        '  note: "semantic block. Web側でblockquote, callout, accordion等へ変換してよい。"',
        '  phrase: "semantic phrase/code block. Web側で article-phrase 相当へ変換してよい。"',
        '  table: "content table. Web側で responsive table へ変換してよい。"',
        '  references: "公式参照。タイトル文字列を通常リンクにする。"',
        "---",
        "",
    ])
    return "\n".join(lines)


def site_sources(args: argparse.Namespace) -> Iterable[Path]:
    if args.source:
        yield (REPO_ROOT / args.source).resolve()
        return
    if args.all_deep_dive:
        yield from sorted((SITE_ROOT / "series" / "genai-shikumi-deep-dive").glob("*/index.html"))
        return
    raise SystemExit("pass --source or --all-deep-dive")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract site article HTML into content Markdown.")
    parser.add_argument("--source", help="Single site HTML path, relative to repo root.")
    parser.add_argument("--all-deep-dive", action="store_true", help="Extract all deep dive article pages under site/series/genai-shikumi-deep-dive/*/index.html.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing content files. Default is to skip them.")
    parser.add_argument("--dry-run", action="store_true", help="Print target paths without writing files.")
    args = parser.parse_args()

    written: List[Path] = []
    skipped: List[Path] = []
    for site_path in site_sources(args):
        output = deep_dive_output_path(site_path)
        if output.exists() and not args.overwrite:
            skipped.append(output)
            continue
        meta, body = extract_article(site_path)
        content = front_matter(meta) + body
        if args.dry_run:
            print(f"would write {output.relative_to(REPO_ROOT)}")
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(content, encoding="utf-8")
            written.append(output)

    for path in written:
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    for path in skipped:
        print(f"skipped existing {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
