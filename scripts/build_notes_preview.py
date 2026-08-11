#!/usr/bin/env python3
"""Build one research-note preview without writing to site/.

ページ作成日時：2026-08-04 16:22 JST
最終更新日時：2026-08-11 11:14 JST

The accepted lane is intentionally narrow:
- source: content/notes/index.md
- route: /notes/
- output: <preview-root>/notes/index.html
- source: content/notes/<slug>/index.md
- route: /notes/<slug>/
- output: <preview-root>/notes/<slug>/index.html
- source: content/notes/themes.md
- route: /notes/themes.html
- output: <preview-root>/notes/themes.html

Bulk globs remain outside this version.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Mapping

try:
    import markdown
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - operator setup
    raise SystemExit(
        "Publishing dependencies are missing. Install requirements-publishing.txt."
    ) from exc

from build_content_pages import BuildError

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = (REPO_ROOT / "content" / "notes").resolve()
SITE_ROOT = (REPO_ROOT / "site").resolve()
DEFAULT_PREVIEW_ROOT = REPO_ROOT / "_notes_build_preview"
TEMPLATE = REPO_ROOT / "publishing" / "templates" / "note.html"
ANCHOR_RE = re.compile(r'^<a id="([a-zA-Z0-9_-]+)"></a>\s*$', re.MULTILINE)
LINK_RE = re.compile(r"^\[([^\]]+)\]\(([^)]+)\)\s*$")
PLACEHOLDER_RE = re.compile(r"\{\{([a-z_]+)\}\}")
PERIOD_PREAMBLE_RE = re.compile(
    r"^(?P<label>Research Group [A-Z]|Theoretical Lines)\s*\n+"
    r"##\s+(?P<title>[^\n]+)\s*(?:\n+|$)"
)
THEME_LINK_RE = re.compile(
    r"^\[\*\*(?P<title>[^\n]+)\*\*\n(?P<description>[^\n]+)\]\((?P<href>[^)]+)\)$"
)
THEME_CANDIDATES = (
    (
        "理解・防御層・行動",
        "AIとの対話で生じた理解は、どのように行動へ更新されるのか。",
        "/article/understanding-defense-action/",
    ),
    (
        "AIによって得られた理解は、経験による理解と何が違うのか",
        "理解・発話・行動のあいだにある差異を扱う。",
        "/article/understanding-defense-action/chapter-03.html",
    ),
    (
        "状態変化ログの方法論",
        "状態変化をどのように記録し、比較可能な対象とするか。",
        "/article/state-change/chapter-14.html",
    ),
    (
        "AI側モードの精緻化",
        "問題化モードを含む応答モードの理論化。",
        "/article/state-change/chapter-13.html",
    ),
    (
        "依存性と倫理：世界への橋の条件",
        "AIが世界の代替ではなく橋として機能する条件。",
        "/article/state-change/chapter-15.html",
    ),
)


def load_source(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise BuildError("note source must start with YAML front matter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise BuildError("note source front matter is not terminated")
    data = yaml.safe_load(text[4:end])
    if not isinstance(data, dict):
        raise BuildError("note front matter must be a mapping")
    return data, text[end + len("\n---\n") :].strip()


def validate_source_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(CONTENT_ROOT)
    except ValueError as exc:
        raise BuildError("note source must be under content/notes/") from exc
    if relative.parts == ("index.md",):
        return ""
    if relative.parts == ("themes.md",):
        return ""
    if len(relative.parts) != 2:
        raise BuildError(
            "notes publication accepts only content/notes/index.md, "
            "content/notes/themes.md, or "
            "content/notes/<slug>/<page>.md"
        )
    slug = relative.parts[0]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise BuildError(f"invalid note slug: {slug!r}")
    allowed_name = relative.name == "index.md" or (
        slug == "history-of-generative-ai" and relative.name == "timeline.md"
    )
    if not allowed_name:
        raise BuildError("unsupported notes publication source")
    return slug


def output_name_for_source(source: Path) -> str:
    return "index.html" if source.name == "index.md" else f"{source.stem}.html"


def expected_route_for_source(source: Path, slug: str) -> str:
    if source.name == "themes.md":
        return "/notes/themes.html"
    if not slug:
        return "/notes/"
    if source.name == "index.md":
        return f"/notes/{slug}/"
    return f"/notes/{slug}/{output_name_for_source(source)}"


def require_scalar(meta: Mapping[str, object], key: str) -> str:
    value = str(meta.get(key) or "").strip()
    if not value:
        raise BuildError(f"required note metadata is missing: {key}")
    return value


def validate_metadata(meta: Mapping[str, object], source: Path, slug: str) -> None:
    route = require_scalar(meta, "route")
    expected_route = expected_route_for_source(source, slug)
    if route != expected_route:
        raise BuildError(f"route mismatch: expected {expected_route!r}, got {route!r}")
    if require_scalar(meta, "title") == "Untitled":
        raise BuildError("note title must be explicit")
    require_scalar(meta, "meta_description")
    expected_page_type = (
        "collection-index" if not slug and source.name == "index.md" else "note"
    )
    if str(meta.get("page_type") or "").strip() != expected_page_type:
        raise BuildError(f"page_type must be {expected_page_type}")
    if str(meta.get("series_or_article") or "").strip() != "notes":
        raise BuildError("series_or_article must be notes")


def parse_preamble(
    body: str, *, collection_index: bool = False
) -> tuple[dict[str, str], list[tuple[str, str]], str]:
    anchor = ANCHOR_RE.search(body)
    first_heading = re.search(r"^##\s+", body, re.MULTILINE)
    if anchor is None and first_heading is None:
        raise BuildError("note body must contain at least one section heading")
    section_start = anchor.start() if anchor is not None else first_heading.start()
    preamble = body[:section_start].strip()
    article = body[section_start:].strip()
    lines = [line.strip() for line in preamble.splitlines() if line.strip()]
    allowed_markers = ("NOTES",) if collection_index else ("CONTENTS", "PERIODS")
    marker = next((value for value in allowed_markers if value in lines), None)
    if marker is None:
        raise BuildError(
            "collection index preamble must contain NOTES"
            if collection_index
            else "note preamble must contain CONTENTS or PERIODS"
        )
    contents_index = lines.index(marker)
    hero = lines[:contents_index]
    toc = lines[contents_index + 1 :]
    minimum_hero_lines = 4 if collection_index else 5
    if len(hero) < minimum_hero_lines:
        raise BuildError(
            "note preamble must contain kicker, title, lead, and sublead"
            + ("" if collection_index else ", and meta")
        )

    kicker = hero[0]
    title_line = next((line for line in hero if line.startswith("# ")), "")
    lead_line = next(
        (line for line in hero if line.startswith("**") and line.endswith("**")),
        hero[2] if collection_index and len(hero) >= 3 else "",
    )
    if not title_line or not lead_line:
        raise BuildError("note preamble title or lead is missing")
    title = title_line[2:].strip()
    lead = (
        lead_line[2:-2].strip()
        if lead_line.startswith("**") and lead_line.endswith("**")
        else lead_line
    )
    title_index = hero.index(title_line)
    lead_index = hero.index(lead_line)
    meta_line = "" if collection_index else hero[-1]
    sublead_lines = hero[lead_index + 1 :] if collection_index else hero[lead_index + 1 : -1]
    if not sublead_lines:
        raise BuildError("note preamble sublead is missing")
    if title_index <= 0 or lead_index <= title_index:
        raise BuildError("note preamble order is invalid")

    links: list[tuple[str, str]] = []
    for line in toc:
        match = LINK_RE.fullmatch(line)
        if not match:
            raise BuildError(f"invalid CONTENTS entry: {line!r}")
        links.append((match.group(1), match.group(2)))
    if not links:
        raise BuildError("note CONTENTS must contain at least one link")

    return {
        "kicker": kicker,
        "title": title,
        "lead": lead,
        "sublead": " ".join(sublead_lines),
        "note_meta": meta_line,
        "sidebar_title": marker,
    }, links, article


def parse_themes_page(body: str) -> tuple[dict[str, str], list[tuple[str, str, str]]]:
    blocks = [value.strip() for value in re.split(r"\n{2,}", body.strip()) if value.strip()]
    if len(blocks) != 8:
        raise BuildError("themes page must contain one hero and exactly five candidate links")
    kicker, title_line, lead = blocks[:3]
    if kicker != "NEXT THEMES" or not title_line.startswith("# ") or not lead:
        raise BuildError("themes page hero is invalid")

    links: list[tuple[str, str, str]] = []
    for block in blocks[3:]:
        match = THEME_LINK_RE.fullmatch(block)
        if match is None:
            raise BuildError(f"invalid themes candidate link: {block!r}")
        links.append(
            (match.group("title"), match.group("description"), match.group("href"))
        )
    validate_theme_links(links)
    return {
        "kicker": kicker,
        "title": title_line[2:].strip(),
        "lead": lead,
        "sublead": "",
        "note_meta": "",
        "sidebar_title": "",
    }, links


def validate_theme_links(links: list[tuple[str, str, str]]) -> None:
    copy = tuple((title, description) for title, description, _ in links)
    expected_copy = tuple((title, description) for title, description, _ in THEME_CANDIDATES)
    if copy != expected_copy:
        raise BuildError("themes candidate titles, descriptions, and order must not change")

    hrefs = tuple(href for _, _, href in links)
    expected_hrefs = tuple(href for _, _, href in THEME_CANDIDATES)
    if hrefs == ("#",) * len(THEME_CANDIDATES):
        return
    if hrefs != expected_hrefs:
        raise BuildError("themes links must be all placeholders or the five approved routes")

    missing = []
    for href in hrefs:
        relative = href.removeprefix("/")
        target = SITE_ROOT / relative / "index.html" if href.endswith("/") else SITE_ROOT / relative
        if not target.is_file():
            missing.append(href)
    if missing:
        raise BuildError("themes link target is missing: " + ", ".join(missing))


def split_sections(
    article: str, links: list[tuple[str, str]]
) -> list[tuple[str, str]]:
    matches = list(ANCHOR_RE.finditer(article))
    if matches:
        return [
            (
                match.group(1),
                article[
                    match.end() : matches[index + 1].start()
                    if index + 1 < len(matches)
                    else len(article)
                ].strip(),
            )
            for index, match in enumerate(matches)
        ]

    headings = list(re.finditer(r"^##\s+[^\n]+\s*$", article, re.MULTILINE))
    section_ids = [href[1:] for _, href in links if href.startswith("#")]
    if len(section_ids) != len(links):
        raise BuildError("anchorless note CONTENTS must contain only in-page links")
    if len(headings) != len(section_ids):
        raise BuildError("anchorless note heading count must match CONTENTS")
    return [
        (
            section_ids[index],
            article[
                heading.start() : headings[index + 1].start()
                if index + 1 < len(headings)
                else len(article)
            ].strip(),
        )
        for index, heading in enumerate(headings)
    ]


def section_heading(section_markdown: str) -> tuple[str, str]:
    match = re.match(r"^##\s+(?P<title>[^\n]+)\s*(?:\n+|$)", section_markdown)
    if match is None:
        raise BuildError("special note section must start with an h2")
    return match.group("title"), section_markdown[match.end() :].strip()


def render_turning_points(section_markdown: str) -> str | None:
    title, body = section_heading(section_markdown)
    card_re = re.compile(
        r"(?ms)^(?P<number>\d+)\s*\n+###\s+(?P<title>[^\n]+)\s*\n+"
        r"(?P<body>.+?)(?=\n+(?:\d+)\s*\n+###\s+|\Z)"
    )
    cards = list(card_re.finditer(body))
    if not cards or card_re.sub("", body).strip():
        return None
    rendered_cards = []
    for match in cards:
        description = markdown.markdown(match.group("body").strip(), output_format="html5")
        rendered_cards.append(
            '            <article class="turning-card">'
            f'<span class="turning-number">{html.escape(match.group("number"))}</span>'
            f'<h3>{html.escape(match.group("title"))}</h3>{description}</article>'
        )
    return (
        f"          <h2>{html.escape(title)}</h2>\n"
        '          <div class="turning-grid">\n'
        + "\n".join(rendered_cards)
        + "\n          </div>"
    )


def render_collection_cards(section_markdown: str) -> str | None:
    title, body = section_heading(section_markdown)
    card_re = re.compile(
        r"(?ms)^(?P<number>\d+)\s*\n+###\s+\[(?P<title>[^\]]+)\]\((?P<href>[^)]+)\)\s*\n+"
        r"(?P<body>.+?)(?=\n+(?:\d+)\s*\n+###\s+|\Z)"
    )
    cards = list(card_re.finditer(body))
    if not cards or card_re.sub("", body).strip():
        return None
    rendered_cards = []
    for match in cards:
        description = markdown.markdown(match.group("body").strip(), output_format="html5")
        rendered_cards.append(
            '            <article class="turning-card">'
            f'<span class="turning-number">{html.escape(match.group("number"))}</span>'
            f'<h3><a href="{html.escape(match.group("href"), quote=True)}">'
            f'{html.escape(match.group("title"))}</a></h3>{description}</article>'
        )
    return (
        f"          <h2>{html.escape(title)}</h2>\n"
        '          <div class="note-card-grid note-card-grid-single">\n'
        + "\n".join(rendered_cards)
        + "\n          </div>"
    )


def render_theme_cards(links: list[tuple[str, str, str]]) -> str:
    cards = []
    for title, description, href in links:
        cards.append(
            f'          <a class="turning-card" href="{html.escape(href, quote=True)}">'
            f"<strong>{html.escape(title)}</strong><br>"
            f'<span class="small-note">{html.escape(description)}</span></a>'
        )
    return (
        '        <section class="note-section note-intro">\n'
        '          <div class="note-card-grid note-card-grid-single">\n'
        + "\n".join(cards)
        + "\n          </div>\n"
        "        </section>"
    )


def render_layer_grid(section_markdown: str) -> str | None:
    title, body = section_heading(section_markdown)
    headings = list(re.finditer(r"^###\s+(?P<title>[^\n]+)\s*$", body, re.MULTILINE))
    if not headings:
        return None
    intro = body[: headings[0].start()].strip()
    class_by_title = {
        "学問史": "academic",
        "技術史": "technology",
        "計算資源史": "compute",
        "企業／モデル史": "company",
        "社会／市場史": "society",
    }
    cards = []
    for index, heading in enumerate(headings):
        layer_title = heading.group("title")
        layer_class = class_by_title.get(layer_title)
        if layer_class is None:
            return None
        end = headings[index + 1].start() if index + 1 < len(headings) else len(body)
        description = markdown.markdown(body[heading.end() : end].strip(), output_format="html5")
        cards.append(
            f'            <article class="layer-card layer-{layer_class}">'
            f"<h3>{html.escape(layer_title)}</h3>{description}</article>"
        )
    intro_html = indent_fragment(markdown.markdown(intro, output_format="html5"))
    return (
        f"          <h2>{html.escape(title)}</h2>\n"
        f"{intro_html}\n"
        '          <div class="layer-grid">\n'
        + "\n".join(cards)
        + "\n          </div>"
    )


def render_history_timeline(article: str, links: list[tuple[str, str]]) -> str:
    period_re = re.compile(r"^第(?P<number>[1-5])期｜(?P<range>[^\n]+)\s*$", re.MULTILINE)
    source_re = re.compile(r"^##\s+出典・参考資料\s*$", re.MULTILINE)
    periods = list(period_re.finditer(article))
    sources = source_re.search(article)
    expected_ids = [f"period-{number}" for number in range(1, 6)] + ["sources"]
    toc_ids = [href[1:] for _, href in links if href.startswith("#")]
    if len(periods) != 5 or sources is None or toc_ids != expected_ids:
        raise BuildError("history timeline periods or CONTENTS are invalid")
    if sources.start() <= periods[-1].start():
        raise BuildError("history timeline sources must follow all periods")

    legend_markdown = article[: periods[0].start()].strip()
    legend = render_layer_grid(legend_markdown)
    if legend is None:
        raise BuildError("history timeline legend must contain all supported layer cards")
    sections = [
        '        <section id="legend" class="note-section note-intro">\n'
        f"{legend}\n"
        "        </section>"
    ]

    layer_classes = {
        "学問史": "academic",
        "技術史": "technology",
        "計算資源史": "compute",
        "企業／モデル史": "company",
        "社会／市場史": "society",
    }
    layer_pattern = "|".join(re.escape(value) for value in layer_classes)
    event_re = re.compile(
        rf"(?ms)^(?P<date>[^\n]+)\s*\n+(?P<layer>{layer_pattern})\s*\n+"
        rf"###\s+(?P<title>[^\n]+)\s*\n+(?P<body>.+?)"
        rf"(?=\n+[^\n]+\s*\n+(?:{layer_pattern})\s*\n+###\s+|\Z)"
    )

    for index, period in enumerate(periods):
        end = periods[index + 1].start() if index + 1 < len(periods) else sources.start()
        period_markdown = article[period.end() : end].strip()
        title, period_body = section_heading(period_markdown)
        events = list(event_re.finditer(period_body))
        if not events:
            raise BuildError(f"history timeline period {index + 1} has no events")
        summary = period_body[: events[0].start()].strip()
        event_text = period_body[events[0].start() :]
        if event_re.sub("", event_text).strip():
            raise BuildError(f"history timeline period {index + 1} has an unsupported event sequence")
        summary_html = markdown.markdown(summary, output_format="html5")
        if not summary_html.startswith("<p>") or summary_html.count("<p>") != 1:
            raise BuildError(f"history timeline period {index + 1} must have one summary paragraph")
        summary_html = summary_html.replace("<p>", '<p class="period-summary">', 1)
        cards = []
        for event in events:
            layer = event.group("layer")
            layer_class = layer_classes[layer]
            description = markdown.markdown(event.group("body").strip(), output_format="html5")
            cards.append(
                f'            <article class="timeline-card" data-layer="{layer_class}">'
                f'<div class="timeline-date">{html.escape(event.group("date"))}</div>'
                f'<div class="timeline-body"><span class="badge badge-{layer_class}">'
                f"{html.escape(layer)}</span><h3>{html.escape(event.group('title'))}</h3>"
                f"{description}</div></article>"
            )
        label = f"第{period.group('number')}期｜{period.group('range')}"
        sections.append(
            f'        <section id="period-{period.group("number")}" class="period">\n'
            '          <div class="period-header">\n'
            f'            <p class="period-label">{html.escape(label)}</p>\n'
            f"            <h2>{html.escape(title)}</h2>\n"
            f"            {summary_html}\n"
            "          </div>\n"
            '          <div class="timeline-list">\n'
            + "\n".join(cards)
            + "\n          </div>\n"
            "        </section>"
        )

    sources_markdown = article[sources.start() :].strip()
    sources_html = markdown.markdown(
        sources_markdown, extensions=["extra", "sane_lists"], output_format="html5"
    ).replace("<ol>", '<ol class="source-list">', 1)
    sections.append(
        '        <section id="sources" class="note-section note-intro">\n'
        f"{indent_fragment(sources_html)}\n"
        "        </section>"
    )
    return "\n\n".join(sections)


def render_sections(
    article: str, links: list[tuple[str, str]], *, collection_index: bool = False
) -> str:
    section_sources = (
        [("collection", article)] if collection_index else split_sections(article, links)
    )
    sections: list[str] = []
    for index, (section_id, section_markdown) in enumerate(section_sources):
        if not section_markdown:
            raise BuildError(f"empty note section: {section_id}")
        period_match = PERIOD_PREAMBLE_RE.match(section_markdown)
        period_header = ""
        section_class = "note-section"
        if period_match:
            section_class = "period"
            label = html.escape(period_match.group("label"))
            title = html.escape(period_match.group("title"))
            period_header = (
                '          <div class="period-header">\n'
                f'            <p class="period-label">{label}</p>\n'
                f'            <h2>{title}</h2>\n'
                "          </div>\n"
            )
            section_markdown = section_markdown[period_match.end() :].strip()
        rendered = None
        if collection_index and index == 0:
            rendered = render_collection_cards(section_markdown)
            if rendered is None:
                raise BuildError("notes collection index must contain numbered linked cards")
        elif section_id == "turning-points":
            rendered = render_turning_points(section_markdown)
        elif section_id == "layers":
            rendered = render_layer_grid(section_markdown)
        if rendered is None:
            rendered = markdown.markdown(
                section_markdown,
                extensions=["extra", "sane_lists"],
                output_format="html5",
            )
            if section_id == "references":
                rendered = rendered.replace("<ol>", '<ol class="source-list">', 1)
            rendered = indent_fragment(rendered)
        intro_class = " note-intro" if index == 0 and section_class == "note-section" else ""
        section_id_html = (
            "" if collection_index else f' id="{html.escape(section_id, quote=True)}"'
        )
        sections.append(
            f'        <section{section_id_html} '
            f'class="{section_class}{intro_class}">\n{period_header}{rendered}\n        </section>'
        )
    return "\n\n".join(sections)


def indent_fragment(fragment: str) -> str:
    """Keep generated note HTML reviewable and close to the legacy layout."""
    containers = {"<ul>": "</ul>", "<ol>": "</ol>", "<blockquote>": "</blockquote>"}
    closing = set(containers.values())
    lines: list[str] = []
    depth = 0
    for raw in fragment.splitlines():
        value = raw.strip()
        if value in closing:
            depth = max(0, depth - 1)
        if value.startswith("<h3") and lines and lines[-1] != "":
            lines.append("")
        lines.append(f"{'          '}{'  ' * depth}{value}")
        if value in containers:
            depth += 1
    return "\n".join(lines)


def render_template(values: Mapping[str, str]) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise BuildError(f"missing note template value: {key}")
        return values[key]

    rendered = PLACEHOLDER_RE.sub(replace, template)
    if PLACEHOLDER_RE.search(rendered):
        raise BuildError("unresolved note template placeholder")
    rendered = "\n".join(line.rstrip() for line in rendered.splitlines())
    return rendered.rstrip() + "\n"


def output_path(preview_root: Path, source: Path, slug: str) -> Path:
    resolved = preview_root.resolve()
    try:
        resolved.relative_to(SITE_ROOT)
    except ValueError:
        pass
    else:
        raise BuildError("notes preview root must not be inside site/")
    return resolved / "notes" / slug / output_name_for_source(source)


def build_one(source: Path, preview_root: Path) -> Path:
    slug = validate_source_path(source)
    themes_page = source.name == "themes.md" and not slug
    collection_index = source.name == "index.md" and not slug
    meta, body = load_source(source)
    validate_metadata(meta, source, slug)
    theme_links: list[tuple[str, str, str]] = []
    if themes_page:
        preamble, theme_links = parse_themes_page(body)
        links: list[tuple[str, str]] = []
        article = ""
    else:
        preamble, links, article = parse_preamble(body, collection_index=collection_index)
    title = require_scalar(meta, "title")
    if preamble["title"] != title:
        raise BuildError("front matter title and visible h1 differ")

    canonical = str(meta.get("canonical") or meta["route"]).strip()
    sidebar_links = "\n".join(
        f'        <a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
        for label, href in links
    )
    sidebar_html = (
        '      <aside class="note-sidebar" aria-label="ページ内目次" '
        'aria-hidden="true"></aside>'
        if themes_page
        else (
            '      <aside class="note-sidebar" aria-label="ページ内目次">\n'
            f'        <p class="note-sidebar-title">{html.escape(preamble["sidebar_title"])}</p>\n'
            f"{sidebar_links}\n"
            "      </aside>"
        )
    )
    values = {
        "document_title": html.escape(f"{title}｜GENAI-RON"),
        "description": html.escape(require_scalar(meta, "meta_description"), quote=True),
        "canonical": html.escape(canonical, quote=True),
        "kicker": html.escape(preamble["kicker"]),
        "title": html.escape(title),
        "lead_html": (
            html.escape(preamble["lead"])
            if collection_index or themes_page
            else f'<strong>{html.escape(preamble["lead"])}</strong>'
        ),
        "sublead": html.escape(preamble["sublead"]),
        "note_meta_html": (
            f'<p class="note-meta">{html.escape(preamble["note_meta"])}</p>'
            if preamble["note_meta"]
            else ""
        ),
        "sidebar_title": html.escape(preamble["sidebar_title"]),
        "sidebar_links": sidebar_links,
        "sidebar_html": sidebar_html,
        "layout_open": (
            '<section class="note-layout" aria-label="研究ノート一覧">'
            if collection_index
            else '<div class="note-layout">'
        ),
        "layout_close": "</section>" if collection_index else "</div>",
        "content_open": (
            '<div class="note-content">'
            if collection_index
            else '<article class="note-content">'
        ),
        "content_close": "</div>" if collection_index else "</article>",
        "article_html": (
            render_theme_cards(theme_links)
            if themes_page
            else render_history_timeline(article, links)
            if source.name == "timeline.md"
            else render_sections(article, links, collection_index=collection_index)
        ),
    }
    target = output_path(preview_root, source, slug)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_template(values), encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one research-note preview.")
    parser.add_argument(
        "--source",
        required=True,
        help="content/notes/index.md, content/notes/themes.md, or content/notes/<slug>/<page>.md",
    )
    parser.add_argument("--preview-root", default=str(DEFAULT_PREVIEW_ROOT))
    args = parser.parse_args()

    source = (REPO_ROOT / args.source).resolve()
    preview_arg = Path(args.preview_root)
    preview_root = preview_arg if preview_arg.is_absolute() else REPO_ROOT / preview_arg
    target = build_one(source, preview_root)
    print(target.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, ValueError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)
