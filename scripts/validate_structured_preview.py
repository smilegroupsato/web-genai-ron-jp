#!/usr/bin/env python3
"""Compare current and structured preview HTML for semantic parity.

This validator intentionally ignores formatting and source-level whitespace. It
checks the parts that must remain stable while the publishing implementation is
being separated: article title, headings, article body text, links, and the
presence of global page regions.
"""

from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Tuple


class ArticleSnapshotParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: List[Tuple[str, bool]] = []
        self.in_article = False
        self.article_depth = 0
        self.in_h1 = False
        self.in_h2 = False
        self.in_nav = False
        self.in_header = False
        self.in_footer = False
        self.title_parts: List[str] = []
        self.heading_parts: List[str] = []
        self.current_heading: List[str] = []
        self.article_text_parts: List[str] = []
        self.article_links: List[Tuple[str, str]] = []
        self.current_link_href: str | None = None
        self.current_link_text: List[str] = []
        self.has_header = False
        self.has_footer = False
        self.theme_id: str | None = None
        self.hero_variant: str | None = None

    @staticmethod
    def _classes(attrs: List[Tuple[str, str | None]]) -> set[str]:
        value = dict(attrs).get("class") or ""
        return set(value.split())

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        classes = self._classes(attrs)
        starts_article = tag == "article" and "note-box" in classes
        self.stack.append((tag, starts_article))

        if tag == "html":
            self.theme_id = attrs_dict.get("data-theme-id")
        if tag == "section" and "series-hero" in classes:
            self.hero_variant = attrs_dict.get("data-hero-variant")
        if tag == "header" and "series-header" in classes:
            self.in_header = True
            self.has_header = True
        if tag == "footer" and "series-footer" in classes:
            self.in_footer = True
            self.has_footer = True
        if starts_article:
            self.in_article = True
            self.article_depth = len(self.stack)
        if tag == "h1":
            self.in_h1 = True
        if self.in_article and tag == "h2":
            self.in_h2 = True
            self.current_heading = []
        if self.in_article and tag == "nav" and "article-link" in classes:
            self.in_nav = True
        if self.in_article and tag == "a":
            self.current_link_href = attrs_dict.get("href") or ""
            self.current_link_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self.in_h1 = False
        if self.in_article and tag == "h2" and self.in_h2:
            self.heading_parts.append(normalize_text(" ".join(self.current_heading)))
            self.current_heading = []
            self.in_h2 = False
        if self.in_article and tag == "a" and self.current_link_href is not None:
            self.article_links.append(
                (self.current_link_href, normalize_text(" ".join(self.current_link_text)))
            )
            self.current_link_href = None
            self.current_link_text = []
        if tag == "nav" and self.in_nav:
            self.in_nav = False
        if tag == "header" and self.in_header:
            self.in_header = False
        if tag == "footer" and self.in_footer:
            self.in_footer = False

        if self.stack:
            _, started_article = self.stack.pop()
            if started_article:
                self.in_article = False
                self.article_depth = 0

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        if self.in_h1:
            self.title_parts.append(data)
        if self.in_article:
            self.article_text_parts.append(data)
            if self.in_h2:
                self.current_heading.append(data)
            if self.current_link_href is not None:
                self.current_link_text.append(data)

    def snapshot(self) -> dict[str, object]:
        return {
            "title": normalize_text(" ".join(self.title_parts)),
            "headings": self.heading_parts,
            "article_text": normalize_text(" ".join(self.article_text_parts)),
            "article_links": self.article_links,
            "has_header": self.has_header,
            "has_footer": self.has_footer,
            "theme_id": self.theme_id,
            "hero_variant": self.hero_variant,
        }


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if "{{" in text or "}}" in text:
        raise SystemExit(f"unresolved template marker found: {path}")
    parser = ArticleSnapshotParser()
    parser.feed(text)
    return parser.snapshot()


def main() -> int:
    argp = argparse.ArgumentParser(description="Validate structured preview semantic parity.")
    argp.add_argument("current", type=Path)
    argp.add_argument("structured", type=Path)
    argp.add_argument("--expected-theme", default="default-academic")
    args = argp.parse_args()

    current = parse(args.current)
    structured = parse(args.structured)

    errors: List[str] = []
    for key in ("title", "headings", "article_text", "article_links"):
        if current[key] != structured[key]:
            errors.append(f"semantic mismatch: {key}")

    if not structured["has_header"]:
        errors.append("structured preview has no series header")
    if not structured["has_footer"]:
        errors.append("structured preview has no series footer")
    if structured["theme_id"] != args.expected_theme:
        errors.append(
            f"theme mismatch: expected {args.expected_theme!r}, got {structured['theme_id']!r}"
        )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("structured preview semantic parity: OK")
    print(f"title: {structured['title']}")
    print(f"h2 count: {len(structured['headings'])}")
    print(f"article links: {len(structured['article_links'])}")
    print(f"theme: {structured['theme_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
