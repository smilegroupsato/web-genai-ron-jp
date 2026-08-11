#!/usr/bin/env python3
"""Build v2 route and content-salvage manifests from the current static site."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPO_ROOT / "site"
CONTENT_ROOT = REPO_ROOT / "content"
ROUTE_MANIFEST = REPO_ROOT / "data" / "site-routes.manifest.json"
SALVAGE_MANIFEST = REPO_ROOT / "data" / "site-content-salvage.manifest.json"

DATE_LABELS = {
    "created_at": ("ページ作成日時",),
    "updated_at": ("最終更新日時",),
    "manuscript_created_at": ("Notion原稿作成日時", "原稿作成日時"),
    "manuscript_updated_at": ("Notion原稿最終更新日時", "原稿最終更新日時"),
    "web_migrated_at": ("Web移植日時",),
}
UNDERSTANDING_DATE_LABELS = {
    **DATE_LABELS,
    "created_at": (*DATE_LABELS["created_at"], "初版公開日"),
    "updated_at": (*DATE_LABELS["updated_at"], "最終更新日"),
}
ARTICLE_ALIAS_VERIFIED_ROUTES = {
    "/article/bibliography.html",
    *(f"/article/chapter-{index:02d}.html" for index in range(1, 17)),
    "/article/state-change.html",
    "/article/state-change-lit-review/",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.body_parts: list[str] = []
        self.comments: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.title_depth = 0
        self.body_depth = 0
        self.body_class = ""
        self.meta_description = ""
        self.canonical_value: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag == "title":
            self.title_depth += 1
        if tag == "body":
            self.body_depth += 1
            self.body_class = values.get("class", "")
        if tag == "meta" and values.get("name", "").lower() == "description":
            self.meta_description = values.get("content", "")
        if tag == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonical_value = values.get("href", "")
        for attribute in ("href", "src"):
            value = values.get(attribute)
            if value:
                self.links.append((tag, value))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.title_depth:
            self.title_depth -= 1
        if tag == "body" and self.body_depth:
            self.body_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_parts.append(data)
        if self.body_depth:
            self.body_parts.append(data)

    def handle_comment(self, data: str) -> None:
        self.comments.append(data)


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def route_for(path: Path) -> str:
    relative = path.relative_to(SITE_ROOT).as_posix()
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        return f"/{relative.removesuffix('index.html')}"
    return f"/{relative}"


def page_type_for(route: str) -> str:
    if route == "/":
        return "home"
    if route in {"/article/", "/notes/", "/essay/"}:
        return "collection-index"
    if route.endswith("/bibliography.html"):
        return "bibliography"
    if "/article/" in route and re.search(r"/chapter-\d+\.html$", route):
        return "article-chapter"
    if route in {"/article/state-change/", "/article/understanding-defense-action/"}:
        return "article-index"
    if route.startswith("/article/"):
        return "article-alias"
    if route.startswith("/notes/"):
        return "note"
    if route.startswith("/essay/"):
        return "essay"
    if route.startswith("/series/"):
        leaf = route.strip("/").split("/")
        if len(leaf) == 2:
            return "series-index"
        if leaf[-1] in {"concept-map", "glossary", "misconceptions", "flyer"}:
            return "series-support"
        return "series-entry"
    return "utility"


def content_path_for(route: str) -> str | None:
    if route == "/":
        candidate = Path("content") / "index.md"
        return candidate.as_posix() if (REPO_ROOT / candidate).is_file() else None
    if route == "/article/":
        candidate = Path("content") / "article" / "index.md"
        return candidate.as_posix() if (REPO_ROOT / candidate).is_file() else None
    article_match = re.fullmatch(
        r"/article/(state-change|understanding-defense-action)/", route
    )
    if article_match:
        candidate = Path("content/article") / article_match.group(1) / "index.md"
        return candidate.as_posix() if (REPO_ROOT / candidate).is_file() else None
    match = re.fullmatch(
        r"/article/(state-change|understanding-defense-action)/"
        r"(chapter-\d{2}|bibliography)\.html",
        route,
    )
    if match:
        candidate = Path("content/article") / match.group(1) / f"{match.group(2)}.md"
        return candidate.as_posix() if (REPO_ROOT / candidate).is_file() else None
    if route.startswith("/essay/"):
        remainder = route.removeprefix("/essay/")
        if route.endswith("/"):
            slug = remainder.rstrip("/")
            candidate = Path("content") / "essay" / slug / "index.md" if slug else Path("content") / "essay" / "index.md"
            return candidate.as_posix() if (REPO_ROOT / candidate).is_file() else None
        if route.endswith(".html"):
            candidate = Path("content") / "essay" / f"{remainder.removesuffix('.html')}.md"
            return candidate.as_posix() if (REPO_ROOT / candidate).is_file() else None
    if route.startswith("/notes/"):
        remainder = route.removeprefix("/notes/")
        if route.endswith("/"):
            slug = remainder.rstrip("/")
            candidate = Path("content") / "notes" / slug / "index.md" if slug else Path("content") / "notes" / "index.md"
            return candidate.as_posix() if (REPO_ROOT / candidate).is_file() else None
        if route.endswith(".html"):
            candidate = Path("content") / "notes" / f"{remainder.removesuffix('.html')}.md"
            return candidate.as_posix() if (REPO_ROOT / candidate).is_file() else None
    if not route.startswith("/series/") or not route.endswith("/"):
        return None
    parts = route.strip("/").split("/")
    if len(parts) < 2:
        return None
    filename = "index.md" if len(parts) == 2 else f"{parts[-1]}.md"
    candidate = Path("content") / "series" / parts[1] / filename
    return candidate.as_posix() if (REPO_ROOT / candidate).is_file() else None


def frontmatter_for(path: str | None) -> str:
    if not path:
        return ""
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 4)
    return text[4:end] if end >= 0 else ""


def find_date(text: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        prefix_guard = (
            r"(?<!原稿)" if label in {"最終更新日時", "最終更新日"} else ""
        )
        match = re.search(
            rf"{prefix_guard}{re.escape(label)}[：:]\s*[\"']?"
            rf"(\d{{4}}-\d{{2}}-\d{{2}}"
            rf"(?:\s+\d{{2}}:\d{{2}}(?:\s+(?:JST|Z|[+-]\d{{2}}:\d{{2}}))?)?)",
            text,
        )
        if match:
            return compact(match.group(1))
    return None


def metadata_inventory(
    visible_body: str,
    html_comment: str,
    markdown_frontmatter: str,
    date_labels: dict[str, tuple[str, ...]] = DATE_LABELS,
) -> tuple[dict[str, list[str]], dict[str, str | None]]:
    locations: dict[str, list[str]] = {}
    values: dict[str, str | None] = {}
    sources = (
        ("visible_body", visible_body),
        ("html_comment", html_comment),
        ("markdown_frontmatter", markdown_frontmatter),
    )
    for field, labels in date_labels.items():
        found: list[tuple[str, str]] = []
        for location, text in sources:
            value = find_date(text, labels)
            if value:
                found.append((location, value))
        locations[field] = [location for location, _ in found] or ["absent"]
        values[field] = found[0][1] if found else None
    return locations, values


def public_ref(route: str, raw: str) -> str | None:
    parsed = urlparse(raw)
    if parsed.scheme in {"mailto", "tel", "javascript", "data"}:
        return None
    if parsed.scheme in {"http", "https"} and parsed.netloc not in {
        "genai-ron.jp",
        "www.genai-ron.jp",
    }:
        return None
    base = f"https://genai-ron.jp{route}"
    resolved = urlparse(urljoin(base, raw))
    value = resolved.path or "/"
    if resolved.query:
        value += f"?{resolved.query}"
    if resolved.fragment:
        value += f"#{resolved.fragment}"
    return value


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def classify_refs(
    route: str, links: list[tuple[str, str]]
) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    css: list[str] = []
    js: list[str] = []
    assets: list[str] = []
    internal: list[str] = []
    downloads: list[str] = []
    for tag, raw in links:
        ref = public_ref(route, raw)
        if ref is None:
            continue
        path = ref.split("#", 1)[0].split("?", 1)[0]
        if tag == "link" and path.endswith(".css"):
            css.append(path)
        elif tag == "script" and path.endswith(".js"):
            js.append(path)
        elif path.startswith("/downloads/"):
            downloads.append(path)
        elif (
            path.startswith("/assets/")
            or path.startswith("/publishing/")
            or tag in {"img", "source", "video", "audio"}
        ):
            assets.append(path)
        elif tag in {"a", "area"} and not path.endswith((".css", ".js")):
            internal.append(ref)
    return tuple(unique(values) for values in (css, js, assets, internal, downloads))  # type: ignore[return-value]


def status_for(
    route: str, title: str, canonical: str | None, content_path: str | None
) -> tuple[str, str]:
    if content_path:
        return "content_source_exists", "needs_parity_check"
    if "移動しました" in title:
        status = "alias_verified" if route in ARTICLE_ALIAS_VERIFIED_ROUTES else "alias_review"
        return "redirect_notice", status
    if canonical:
        canonical_path = public_ref(route, canonical)
        if canonical_path and canonical_path.rstrip("/") != route.rstrip("/"):
            status = "alias_verified" if route in ARTICLE_ALIAS_VERIFIED_ROUTES else "alias_review"
            return "alias", status
    return "html_only", "needs_extraction"


def build_entry(path: Path) -> dict[str, object]:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    route = route_for(path)
    content_path = content_path_for(route)
    date_labels = (
        UNDERSTANDING_DATE_LABELS
        if route.startswith("/article/understanding-defense-action/")
        else DATE_LABELS
    )
    metadata_locations, metadata_values = metadata_inventory(
        compact(" ".join(parser.body_parts)),
        "\n".join(parser.comments),
        frontmatter_for(content_path),
        date_labels,
    )
    css, js, assets, internal, downloads = classify_refs(route, parser.links)
    source_status, salvage_status = status_for(
        route,
        compact(" ".join(parser.title_parts)),
        parser.canonical_value,
        content_path,
    )
    return {
        "route": route,
        "source_html_path": path.relative_to(REPO_ROOT).as_posix(),
        "page_type": page_type_for(route),
        "title": compact(" ".join(parser.title_parts)),
        "meta_description": compact(parser.meta_description) or None,
        "canonical_present": parser.canonical_value is not None,
        "canonical_value": parser.canonical_value,
        "body_class": compact(parser.body_class) or None,
        "loaded_css": css,
        "loaded_js": js,
        "content_source_status": source_status,
        "corresponding_content_path": content_path,
        "metadata_locations": metadata_locations,
        "metadata_values": metadata_values,
        "created_at_known": metadata_values["created_at"] is not None,
        "updated_at_known": metadata_values["updated_at"] is not None,
        "manuscript_created_at_known": metadata_values["manuscript_created_at"] is not None,
        "manuscript_updated_at_known": metadata_values["manuscript_updated_at"] is not None,
        "web_migrated_at_known": metadata_values["web_migrated_at"] is not None,
        "assets": assets,
        "internal_links": internal,
        "download_links": downloads,
        "preserve_route": True,
        "salvage_status": salvage_status,
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if committed manifests differ")
    args = parser.parse_args()

    pages = [build_entry(path) for path in sorted(SITE_ROOT.rglob("*.html"))]
    route_manifest = {
        "manifest_version": 1,
        "source_root": "site",
        "route_count": len(pages),
        "routes": [
            {
                "route": page["route"],
                "source_html_path": page["source_html_path"],
                "page_type": page["page_type"],
                "preserve_route": page["preserve_route"],
            }
            for page in pages
        ],
    }
    salvage_manifest = {
        "manifest_version": 1,
        "source_root": "site",
        "page_count": len(pages),
        "pages": pages,
    }

    if args.check:
        expected = (
            (ROUTE_MANIFEST, route_manifest),
            (SALVAGE_MANIFEST, salvage_manifest),
        )
        stale = [
            path.relative_to(REPO_ROOT).as_posix()
            for path, value in expected
            if not path.is_file()
            or path.read_text(encoding="utf-8")
            != json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        ]
        if stale:
            raise SystemExit("stale manifest(s): " + ", ".join(stale))
        print(f"manifest generation check: OK ({len(pages)} pages)")
        return 0

    write_json(ROUTE_MANIFEST, route_manifest)
    write_json(SALVAGE_MANIFEST, salvage_manifest)
    print(f"wrote {len(pages)} routes and salvage records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
