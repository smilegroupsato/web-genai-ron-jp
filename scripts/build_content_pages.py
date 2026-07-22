#!/usr/bin/env python3
"""Build genai-ron.jp pages from content/ Markdown sources.

This is a minimal, dependency-free builder for the first content-source proof.

Default behavior is intentionally safe:
- read Markdown sources under content/
- write generated HTML under _content_build_preview/
- do not overwrite site/ unless --write-site is explicitly passed

The builder is not yet a full static-site generator. It exists to prove that
article content can be separated from site-wide presentation code and then
re-rendered into a public HTML page.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = REPO_ROOT / "content"
DEFAULT_PREVIEW_ROOT = REPO_ROOT / "_content_build_preview"
SITE_ROOT = REPO_ROOT / "site"


class BuildError(RuntimeError):
    pass


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_front_matter(text: str) -> Tuple[Dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        raise BuildError("front matter starts with --- but has no closing ---")

    raw = text[4:end].splitlines()
    body = text[end + len("\n---\n") :]
    meta: Dict[str, object] = {}
    current_list_key: str | None = None

    for line in raw:
        if not line.strip():
            continue
        if line.startswith("  - ") and current_list_key:
            meta.setdefault(current_list_key, [])
            assert isinstance(meta[current_list_key], list)
            meta[current_list_key].append(strip_quotes(line[4:]))
            continue
        if line.startswith("  "):
            # Nested mapping is preserved only as source-level metadata for now.
            # The minimal builder does not need it to render the public article.
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            meta[key] = strip_quotes(value)
            current_list_key = None
        else:
            meta[key] = []
            current_list_key = key

    return meta, body


def render_inline(text: str) -> str:
    tokens: List[str] = []

    def stash(value: str) -> str:
        tokens.append(value)
        return f"\u0000{len(tokens) - 1}\u0000"

    def link_repl(match: re.Match[str]) -> str:
        label = html.escape(match.group(1), quote=False)
        url = html.escape(match.group(2), quote=True)
        return stash(f'<a href="{url}">{label}</a>')

    def code_repl(match: re.Match[str]) -> str:
        code = html.escape(match.group(1), quote=False)
        return stash(f"<code>{code}</code>")

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)
    text = re.sub(r"`([^`]+)`", code_repl, text)
    escaped = html.escape(text, quote=False)

    def restore(match: re.Match[str]) -> str:
        return tokens[int(match.group(1))]

    return re.sub("\u0000(\\d+)\u0000", restore, escaped)


def render_code_block(lang: str, code: List[str]) -> str:
    code_html = html.escape("\n".join(code), quote=False)
    if lang == "text":
        return f'<pre class="article-phrase"><code>{code_html}\n</code></pre>'
    class_attr = f' class="language-{html.escape(lang, quote=True)}"' if lang else ""
    return f"<pre><code{class_attr}>{code_html}\n</code></pre>"


def split_table_row(line: str) -> List[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_start(lines: List[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    return lines[index].lstrip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", lines[index + 1]) is not None


def render_table(lines: List[str], index: int) -> Tuple[str, int]:
    header = split_table_row(lines[index])
    rows: List[List[str]] = []
    index += 2
    while index < len(lines) and lines[index].lstrip().startswith("|"):
        rows.append(split_table_row(lines[index]))
        index += 1

    thead = "<thead>\n<tr>\n" + "".join(f"  <th>{render_inline(cell)}</th>\n" for cell in header) + "</tr>\n</thead>"
    tbody_rows = []
    for row in rows:
        cells = "".join(f"  <td>{render_inline(cell)}</td>\n" for cell in row)
        tbody_rows.append(f"<tr>\n{cells}</tr>")
    tbody = "<tbody>\n" + "\n".join(tbody_rows) + "\n</tbody>"
    return f'<table class="content-table">\n{thead}\n{tbody}\n</table>', index


def render_list(lines: List[str], index: int) -> Tuple[str, int]:
    items = []
    while index < len(lines) and lines[index].startswith("- "):
        items.append(f"<li>{render_inline(lines[index][2:].strip())}</li>")
        index += 1
    return "<ul>\n" + "\n".join(items) + "\n</ul>", index


def render_note(lines: List[str], index: int) -> Tuple[str, int]:
    body: List[str] = []
    index += 1
    while index < len(lines) and lines[index].strip() != ":::":
        if lines[index].strip():
            body.append(lines[index].strip())
        index += 1
    if index < len(lines) and lines[index].strip() == ":::":
        index += 1
    paragraph = render_inline(" ".join(body))
    return f"<blockquote>\n<p>{paragraph}</p>\n</blockquote>", index


def render_markdown_body(markdown: str) -> str:
    lines = markdown.splitlines()
    out: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            code: List[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            out.append(render_code_block(lang, code))
            continue

        if stripped == ":::note":
            html_block, i = render_note(lines, i)
            out.append(html_block)
            continue

        if is_table_start(lines, i):
            html_block, i = render_table(lines, i)
            out.append(html_block)
            continue

        if line.startswith("- "):
            html_block, i = render_list(lines, i)
            out.append(html_block)
            continue

        if stripped.startswith("## "):
            out.append(f"<h2>{render_inline(stripped[3:].strip())}</h2>")
            i += 1
            continue

        paragraph = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            nxt_stripped = nxt.strip()
            if not nxt_stripped:
                i += 1
                break
            if nxt_stripped.startswith(("```", ":::note", "## ")) or nxt.startswith("- ") or is_table_start(lines, i):
                break
            paragraph.append(nxt_stripped)
            i += 1
        out.append(f"<p>{render_inline(' '.join(paragraph))}</p>")

    return "\n".join(out)


def build_article_html(meta: Dict[str, object], body_html: str) -> str:
    title = str(meta.get("title", "Untitled"))
    subtitle = str(meta.get("subtitle", ""))
    description = str(meta.get("description", subtitle))
    series_label = str(meta.get("series_label", "生成AIのしくみ 超詳解"))
    order = str(meta.get("series_order", ""))
    original_created = str(meta.get("original_notion_created_at", ""))
    original_updated = str(meta.get("original_notion_updated_at", ""))
    web_migrated = str(meta.get("web_migrated_at", ""))

    return f'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(series_label)} {html.escape(order)}｜GENAI-RON</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <meta property="og:title" content="{html.escape(series_label)} {html.escape(order)}">
  <meta property="og:description" content="{html.escape(description, quote=True)}">
  <meta property="og:type" content="article">
  <meta property="og:image" content="/assets/og.svg">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/assets/style-genai-shikumi.css">
  <link rel="stylesheet" href="/assets/theme.css">
</head>
<body class="series-page series-page-compact">
  <!-- Generated from content/ Markdown / Notion原稿作成日時：{html.escape(original_created)} / Notion原稿最終更新日時：{html.escape(original_updated)} / Web移植日時：{html.escape(web_migrated)} -->
  <header class="series-header">
    <div class="series-header-inner">
      <a class="series-brand" href="/"><span class="series-brand-main">GENAI-RON</span><span class="series-brand-sub">🧠生成AI論🥦</span></a>
      <nav class="series-nav" aria-label="サイト内ナビゲーション">
        <a href="/series/genai-shikumi-deep-dive/">超詳解トップ</a>
        <a href="/series/genai-shikumi/">一般向け版</a>
        <a href="/series/genai-shikumi-technical/">詳解版</a>
        <a href="/article/">論考一覧</a>
      </nav>
    </div>
  </header>
  <main>
    <section class="series-hero">
      <p class="series-kicker">{html.escape(series_label)} {html.escape(order)}</p>
      <h1>{html.escape(title)}</h1>
      <p class="series-subtitle">{html.escape(subtitle)}</p>
    </section>
    <div class="series-main">
      <article class="note-box">
{body_html}
      </article>
    </div>
  </main>
  <footer class="series-footer"><p>GENAI-RON｜🧠生成AI論🥦</p></footer>
  <script src="/assets/theme.js" defer></script>
</body>
</html>
'''


def source_paths(explicit: str | None) -> Iterable[Path]:
    if explicit:
        yield (REPO_ROOT / explicit).resolve()
        return
    yield from sorted(CONTENT_ROOT.glob("series/**/*.md"))


def output_path_for(meta: Dict[str, object], preview_root: Path, write_site: bool) -> Path:
    slug = str(meta.get("slug", "")).strip()
    if not slug.startswith("/") or not slug.endswith("/"):
        raise BuildError(f"invalid or missing slug: {slug!r}")
    root = SITE_ROOT if write_site else preview_root
    return root / slug.strip("/") / "index.html"


def build_one(path: Path, preview_root: Path, write_site: bool) -> Path:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)
    body_html = render_markdown_body(body)
    page = build_article_html(meta, body_html)
    out_path = output_path_for(meta, preview_root, write_site)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build GENAI-RON pages from content Markdown.")
    parser.add_argument("--source", help="Single content Markdown path to build, relative to repo root.")
    parser.add_argument("--preview-root", default=str(DEFAULT_PREVIEW_ROOT), help="Preview output root. Ignored with --write-site.")
    parser.add_argument("--write-site", action="store_true", help="Write into site/ instead of preview output. Use only after diff review.")
    args = parser.parse_args()

    preview_root = (REPO_ROOT / args.preview_root).resolve() if not Path(args.preview_root).is_absolute() else Path(args.preview_root)
    built: List[Path] = []
    for path in source_paths(args.source):
        built.append(build_one(path, preview_root, args.write_site))

    for path in built:
        print(path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
