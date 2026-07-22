#!/usr/bin/env python3
"""Compare current and structured preview HTML for semantic parity.

This validator intentionally ignores formatting and source-level whitespace. It
checks the parts that must remain stable while the publishing implementation is
being separated: article title, headings, article body text, links, global page
regions, and resolved theme metadata.
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
        self.in_h1 = False
        self.in_h2 = False
        self.in_nav = False
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
        self.theme_collection: str | None = None
        self.theme_base: str | None = None
        self.theme_season: str | None = None
        self.production_enabled: str | None = None
        self.hero_variant: str | None = None
        self.text_contrast: str | None = None
        self.asset_role: str | None = None
        self.asset_ref: str | None = None
        self.asset_status: str | None = None

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
            self.theme_collection = attrs_dict.get("data-theme-collection")
            self.theme_base = attrs_dict.get("data-theme-base")
            self.theme_season = attrs_dict.get("data-theme-season")
            self.production_enabled = attrs_dict.get("data-theme-production-enabled")
        if tag == "section" and "series-hero" in classes:
            self.hero_variant = attrs_dict.get("data-hero-variant")
            self.text_contrast = attrs_dict.get("data-text-contrast")
            self.asset_role = attrs_dict.get("data-asset-role")
            self.asset_ref = attrs_dict.get("data-asset-ref")
            self.asset_status = attrs_dict.get("data-asset-status")
        if tag == "header" and "series-header" in classes:
            self.has_header = True
        if tag == "footer" and "series-footer" in classes:
            self.has_footer = True
        if starts_article:
            self.in_article = True
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

        if self.stack:
            _, started_article = self.stack.pop()
            if started_article:
                self.in_article = False

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
            "theme_collection": self.theme_collection,
            "theme_base": self.theme_base,
            "theme_season": self.theme_season,
            "production_enabled": self.production_enabled,
            "hero_variant": self.hero_variant,
            "text_contrast": self.text_contrast,
            "asset_role": self.asset_role,
            "asset_ref": self.asset_ref,
            "asset_status": self.asset_status,
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


def add_expectation(
    errors: List[str], snapshot: dict[str, object], key: str, expected: str | None
) -> None:
    if expected is None:
        return
    actual = snapshot.get(key)
    if actual != expected:
        errors.append(f"{key} mismatch: expected {expected!r}, got {actual!r}")


def main() -> int:
    argp = argparse.ArgumentParser(description="Validate structured preview semantic parity.")
    argp.add_argument("current", type=Path)
    argp.add_argument("structured", type=Path)
    argp.add_argument("--expected-theme", default="default-academic")
    argp.add_argument("--expected-collection")
    argp.add_argument("--expected-base")
    argp.add_argument("--expected-season")
    argp.add_argument("--expected-hero-variant")
    argp.add_argument("--expected-text-contrast")
    argp.add_argument("--expected-asset-role")
    argp.add_argument("--expected-asset-status")
    argp.add_argument("--expected-production-enabled")
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

    add_expectation(errors, structured, "theme_id", args.expected_theme)
    add_expectation(errors, structured, "theme_collection", args.expected_collection)
    add_expectation(errors, structured, "theme_base", args.expected_base)
    add_expectation(errors, structured, "theme_season", args.expected_season)
    add_expectation(errors, structured, "hero_variant", args.expected_hero_variant)
    add_expectation(errors, structured, "text_contrast", args.expected_text_contrast)
    add_expectation(errors, structured, "asset_role", args.expected_asset_role)
    add_expectation(errors, structured, "asset_status", args.expected_asset_status)
    add_expectation(
        errors, structured, "production_enabled", args.expected_production_enabled
    )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("structured preview semantic parity: OK")
    print(f"title: {structured['title']}")
    print(f"h2 count: {len(structured['headings'])}")
    print(f"article links: {len(structured['article_links'])}")
    print(
        "theme: "
        f"{structured['theme_id']} / {structured['theme_collection']} / "
        f"{structured['theme_base']} / {structured['theme_season']}"
    )
    print(
        "hero: "
        f"{structured['hero_variant']} / {structured['text_contrast']} / "
        f"{structured['asset_role']} / {structured['asset_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
