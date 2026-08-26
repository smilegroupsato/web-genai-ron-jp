#!/usr/bin/env python3
"""Validate route-to-content and page-type contracts for the site manifest."""

from __future__ import annotations

import tempfile
from pathlib import Path

import build_site_manifest as manifest


MEMBRANE_CASES = {
    "/membrane/": ("content/membrane/index.md", "membrane-index"),
    "/membrane/about/": ("content/membrane/about.md", "membrane-entry"),
    "/membrane/research-map/": (
        "content/membrane/research-map.md",
        "membrane-entry",
    ),
    "/membrane/thoughts/exchange-device/": (
        "content/membrane/thoughts/exchange-device.md",
        "membrane-entry",
    ),
    "/membrane/reading/example-title/": (
        "content/membrane/reading/example-title.md",
        "membrane-entry",
    ),
    "/membrane/bibliography/": (
        "content/membrane/bibliography.md",
        "membrane-entry",
    ),
}

EXISTING_CASES = {
    "/": ("content/index.md", "home"),
    "/article/": ("content/article/index.md", "collection-index"),
    "/essay/example/": ("content/essay/example/index.md", "essay"),
    "/notes/example/": ("content/notes/example/index.md", "note"),
    "/series/example/": ("content/series/example/index.md", "series-index"),
    "/series/example/entry/": (
        "content/series/example/entry.md",
        "series-entry",
    ),
}


def main() -> int:
    original_root = manifest.REPO_ROOT
    try:
        with tempfile.TemporaryDirectory(prefix="genai-manifest-routing-") as temp_dir:
            manifest.REPO_ROOT = Path(temp_dir)
            cases = {**EXISTING_CASES, **MEMBRANE_CASES}
            for content_path, _ in cases.values():
                path = manifest.REPO_ROOT / content_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("---\nid: fixture\n---\n", encoding="utf-8")

            for route, (content_path, page_type) in cases.items():
                actual_path = manifest.content_path_for(route)
                if actual_path != content_path:
                    raise SystemExit(
                        f"content path mismatch for {route}: "
                        f"expected {content_path}, got {actual_path}"
                    )
                actual_type = manifest.page_type_for(route)
                if actual_type != page_type:
                    raise SystemExit(
                        f"page type mismatch for {route}: "
                        f"expected {page_type}, got {actual_type}"
                    )

            unsupported = {
                "/membrane/unknown/": "membrane-entry",
                "/membrane/thoughts/too/deep/": "membrane-entry",
            }
            for route, page_type in unsupported.items():
                if manifest.content_path_for(route) is not None:
                    raise SystemExit(f"unsupported membrane route resolved: {route}")
                if manifest.page_type_for(route) != page_type:
                    raise SystemExit(f"membrane namespace lost its page type: {route}")
    finally:
        manifest.REPO_ROOT = original_root

    print(
        "site manifest routing: OK "
        f"({len(MEMBRANE_CASES)} membrane, {len(EXISTING_CASES)} existing)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
