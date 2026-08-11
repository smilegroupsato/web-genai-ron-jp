#!/usr/bin/env python3
"""Validate reviewed /article/ alias and redirect-notice routes."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from build_site_manifest import ARTICLE_ALIAS_VERIFIED_ROUTES, public_ref
from extract_site_article_to_content import Node, TreeParser, find_all, find_first, normalize_space, text_of

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "site-content-salvage.manifest.json"
EXPECTED_TARGETS = {
    "/article/bibliography.html": "/article/state-change/bibliography.html",
    **{
        f"/article/chapter-{index:02d}.html":
        f"/article/state-change/chapter-{index:02d}.html"
        for index in range(1, 17)
    },
    "/article/state-change.html": "/article/state-change/index.html",
    "/article/state-change-lit-review/": "/notes/state-change-lit-review/",
}
REDIRECT_NOTICE_ROUTE = "/article/state-change-lit-review/"


class ValidationError(RuntimeError):
    pass


def head_node(root: Node, tag: str, attribute: str, value: str) -> Node | None:
    head = find_first(root, "head")
    if head is None:
        return None
    return next(
        (node for node in find_all(head, tag) if node.attr(attribute).lower() == value.lower()),
        None,
    )


def expected_source_path(route: str) -> Path:
    if route.endswith("/"):
        return REPO_ROOT / "site" / route.strip("/") / "index.html"
    return REPO_ROOT / "site" / route.lstrip("/")


def forbidden_markdown_paths(route: str) -> tuple[Path, ...]:
    leaf = route.rstrip("/").rsplit("/", 1)[-1]
    if route.endswith("/"):
        return (REPO_ROOT / "content" / "article" / leaf / "index.md",)
    stem = leaf.removesuffix(".html")
    return (REPO_ROOT / "content" / "article" / f"{stem}.md",)


def validate_html(route: str, target: str, source: Path) -> None:
    parser = TreeParser()
    parser.feed(source.read_text(encoding="utf-8"))
    title = find_first(parser.root, "title")
    if title is None or not normalize_space(text_of(title)):
        raise ValidationError(f"missing HTML title: {route}")

    canonical = head_node(parser.root, "link", "rel", "canonical")
    canonical_target = public_ref(route, canonical.attr("href")) if canonical else None
    if canonical_target != target:
        raise ValidationError(f"canonical target mismatch: {route} -> {canonical_target}")

    refresh = head_node(parser.root, "meta", "http-equiv", "refresh")
    refresh_match = re.search(r"url\s*=\s*(.+)$", refresh.attr("content"), re.IGNORECASE) if refresh else None
    refresh_target = public_ref(route, refresh_match.group(1).strip()) if refresh_match else None
    if refresh_target != target:
        raise ValidationError(f"meta refresh target mismatch: {route} -> {refresh_target}")

    body = find_first(parser.root, "body")
    if body is None:
        raise ValidationError(f"missing visible body: {route}")
    links = [public_ref(route, node.attr("href")) for node in find_all(body, "a")]
    if links != [target]:
        raise ValidationError(f"visible primary link mismatch: {route} -> {links}")
    if not normalize_space(text_of(body)):
        raise ValidationError(f"empty visible body: {route}")


def validate() -> None:
    if set(EXPECTED_TARGETS) != set(ARTICLE_ALIAS_VERIFIED_ROUTES):
        raise ValidationError("validator and manifest-builder route sets differ")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    pages = manifest["pages"]
    by_route = {item.get("route"): item for item in pages}
    if len(by_route) != len(pages):
        raise ValidationError("manifest contains duplicate routes")

    unexpected_verified = sorted(
        route for route, item in by_route.items()
        if item.get("salvage_status") == "alias_verified" and route not in EXPECTED_TARGETS
    )
    if unexpected_verified:
        raise ValidationError(f"non-target routes marked alias_verified: {unexpected_verified}")

    for route, target in EXPECTED_TARGETS.items():
        item = by_route.get(route)
        if item is None:
            raise ValidationError(f"route missing from manifest: {route}")
        expected_status = "redirect_notice" if route == REDIRECT_NOTICE_ROUTE else "alias"
        expected = {
            "preserve_route": True,
            "content_source_status": expected_status,
            "corresponding_content_path": None,
            "salvage_status": "alias_verified",
            "download_links": [],
            "internal_links": [target],
        }
        for field, value in expected.items():
            if item.get(field) != value:
                raise ValidationError(f"manifest {field} mismatch: {route}")

        source = expected_source_path(route)
        if not source.is_file() or item.get("source_html_path") != source.relative_to(REPO_ROOT).as_posix():
            raise ValidationError(f"source HTML mismatch: {route}")
        validate_html(route, target, source)
        existing = [path.relative_to(REPO_ROOT).as_posix() for path in forbidden_markdown_paths(route) if path.exists()]
        if existing:
            raise ValidationError(f"alias Markdown source must not exist: {route}: {existing}")


def main() -> int:
    try:
        validate()
    except (OSError, KeyError, ValueError, ValidationError) as exc:
        print(f"article alias route validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print("article alias route validation: OK (18 aliases, 1 redirect notice, 19 verified targets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
