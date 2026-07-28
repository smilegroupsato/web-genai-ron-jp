#!/usr/bin/env python3
"""Extract small essay and note pages into Markdown content sources."""

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
MANIFEST_PATH = REPO_ROOT / "data" / "site-content-salvage.manifest.json"
CONTENT_ROOT = REPO_ROOT / "content"
TARGET_ROUTES = (
    "/essay/",
    "/essay/ai-era-authorship/",
    "/essay/ai-only-generation/",
    "/notes/",
    "/notes/history-of-generative-ai/",
    "/notes/themes.html",
)
ORDER_BY_ROUTE = {
    "/essay/": 0,
    "/essay/ai-era-authorship/": 1,
    "/essay/ai-only-generation/": 2,
    "/notes/": 0,
    "/notes/history-of-generative-ai/": 1,
    "/notes/themes.html": 2,
}
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


def load_manifest_pages() -> list[dict[str, object]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    pages = manifest.get("pages")
    if not isinstance(pages, list):
        raise RuntimeError("site-content-salvage manifest is malformed")
    return pages


def route_order(route: str) -> int:
    try:
        return ORDER_BY_ROUTE[route]
    except KeyError as exc:
        raise RuntimeError(f"route not in target set: {route}") from exc


def output_path(route: str) -> Path:
    if route == "/essay/":
        return CONTENT_ROOT / "essay" / "index.md"
    if route.startswith("/essay/") and route.endswith("/"):
        slug = route.removeprefix("/essay/").rstrip("/")
        return CONTENT_ROOT / "essay" / slug / "index.md"
    if route == "/notes/":
        return CONTENT_ROOT / "notes" / "index.md"
    if route.startswith("/notes/") and route.endswith("/"):
        slug = route.removeprefix("/notes/").rstrip("/")
        return CONTENT_ROOT / "notes" / slug / "index.md"
    if route.startswith("/notes/") and route.endswith(".html"):
        slug = route.removeprefix("/notes/").removesuffix(".html")
        return CONTENT_ROOT / "notes" / f"{slug}.md"
    raise RuntimeError(f"unsupported target route: {route}")


def source_path(route: str) -> Path:
    if route == "/essay/":
        return REPO_ROOT / "site" / "essay" / "index.html"
    if route.startswith("/essay/") and route.endswith("/"):
        slug = route.removeprefix("/essay/").rstrip("/")
        return REPO_ROOT / "site" / "essay" / slug / "index.html"
    if route == "/notes/":
        return REPO_ROOT / "site" / "notes" / "index.html"
    if route.startswith("/notes/") and route.endswith("/"):
        slug = route.removeprefix("/notes/").rstrip("/")
        return REPO_ROOT / "site" / "notes" / slug / "index.html"
    if route.startswith("/notes/") and route.endswith(".html"):
        slug = route.removeprefix("/notes/").removesuffix(".html")
        return REPO_ROOT / "site" / "notes" / f"{slug}.html"
    raise RuntimeError(f"unsupported target route: {route}")


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
    if node.tag in {"main", "article", "section", "div", "aside", "header"}:
        return render_children(node.children)
    return render_inline(node.children)


def render_children(children: list[Child]) -> str:
    blocks = [block for block in (render_block(child).strip() for child in children) if block]
    return "\n\n".join(blocks)


def title_for(root: Node) -> str:
    title = find_first(root, "h1")
    if title is None:
        raise RuntimeError("h1 not found")
    return normalize_space(text_of(title))


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


def page_metadata(entry: dict[str, object], root: Node, comments: list[str]) -> dict[str, object]:
    route = entry["route"]
    assert isinstance(route, str)
    title = title_for(root)
    head = find_first(root, "head")
    head_children = [child for child in head.children if isinstance(child, Node)] if head else []
    meta_description_node = next(
        (
            node
            for node in head_children
            if node.tag == "meta" and node.attr("name") == "description"
        ),
        None,
    )
    canonical_node = next(
        (
            node
            for node in head_children
            if node.tag == "link" and "canonical" in node.attr("rel").lower().split()
        ),
        None,
    )
    body = find_first(root, "body")
    body_class = body.attr("class") if body else ""
    main = find_first(root, "main")
    visible_text = text_of(main or root)
    dates, provenance = date_metadata(visible_text, comments)

    if route == "/essay/" or route == "/notes/":
        order = 0
        chapter = None
    elif route.startswith("/essay/"):
        order = route_order(route)
        chapter = None
    else:
        order = route_order(route)
        chapter = None

    series_or_article = "essay" if route.startswith("/essay/") else "notes"
    return {
        "title": title,
        "route": route,
        "source_html_path": entry["source_html_path"],
        "source_html_sha256": hashlib.sha256(source_path(route).read_bytes()).hexdigest(),
        "page_type": entry["page_type"],
        "series_or_article": series_or_article,
        "order": order,
        "chapter": chapter,
        "meta_description": meta_description_node.attr("content") if meta_description_node else None,
        "canonical": canonical_node.attr("href") if canonical_node else None,
        **dates,
        "metadata_provenance": {
            "title": "visible_body",
            "meta_description": "html_head" if meta_description_node else "absent",
            "canonical": "html_head" if canonical_node else "absent",
            "created_at": provenance["created_at"],
            "updated_at": provenance["updated_at"],
            "manuscript_created_at": provenance["manuscript_created_at"],
            "manuscript_updated_at": provenance["manuscript_updated_at"],
            "web_migrated_at": provenance["web_migrated_at"],
        },
        "extraction_status": "source-reconstruction-draft",
        "body_class": body_class or None,
    }


def extract_page(entry: dict[str, object]) -> str:
    route = entry["route"]
    assert isinstance(route, str)
    source = source_path(route)
    parser = TreeParser()
    parser.feed(source.read_text(encoding="utf-8"))
    root = parser.root
    main = find_first(root, "main")
    if main is None:
        raise RuntimeError(f"main not found: {source.relative_to(REPO_ROOT)}")
    metadata = page_metadata(entry, root, parser.comments)
    body = render_children(main.children)
    return front_matter(metadata) + body.strip() + "\n"


def target_entries() -> list[dict[str, object]]:
    pages = load_manifest_pages()
    by_route = {page.get("route"): page for page in pages if isinstance(page.get("route"), str)}
    entries: list[dict[str, object]] = []
    for route in TARGET_ROUTES:
        page = by_route.get(route)
        if page is None:
            raise RuntimeError(f"route missing from manifest: {route}")
        if page.get("content_source_status") not in {"html_only", "content_source_exists"}:
            raise RuntimeError(f"route is not a small-page target in manifest: {route}")
        entries.append(page)
    return entries


def write_or_check(write: bool) -> list[Path]:
    entries = target_entries()
    written: list[Path] = []
    for entry in entries:
        route = entry["route"]
        assert isinstance(route, str)
        out = output_path(route)
        rendered = extract_page(entry)
        if write:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(rendered, encoding="utf-8")
        else:
            if not out.is_file():
                raise RuntimeError(f"missing content source: {out.relative_to(REPO_ROOT)}")
            existing = out.read_text(encoding="utf-8")
            if existing != rendered:
                raise RuntimeError(f"content mismatch: {out.relative_to(REPO_ROOT)}")
        written.append(out)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify committed Markdown matches extraction output")
    args = parser.parse_args()
    try:
        paths = write_or_check(write=not args.check)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"small page extraction: FAILED\n{exc}", file=sys.stderr)
        return 1
    mode = "check" if args.check else "write"
    print(f"small page extraction: OK ({mode}, {len(paths)} Markdown sources)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
