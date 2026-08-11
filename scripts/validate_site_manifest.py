#!/usr/bin/env python3
"""Validate genai-ron.jp v2 route and content-salvage manifests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
ROUTE_MANIFEST = REPO_ROOT / "data" / "site-routes.manifest.json"
SALVAGE_MANIFEST = REPO_ROOT / "data" / "site-content-salvage.manifest.json"
SALVAGE_STATUSES = {
    "done",
    "needs_extraction",
    "needs_parity_check",
    "alias_review",
    "alias_verified",
    "unknown",
}


class ValidationError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"manifest does not exist: {path.relative_to(REPO_ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"invalid JSON in {path.relative_to(REPO_ROOT)}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ValidationError(f"manifest root must be an object: {path.relative_to(REPO_ROOT)}")
    return value


def require_list(manifest: dict[str, Any], key: str, path: Path) -> list[dict[str, Any]]:
    value = manifest.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValidationError(f"{path.relative_to(REPO_ROOT)}:{key} must be an array of objects")
    return value


def repo_file(raw: object, label: str) -> Path:
    if not isinstance(raw, str) or not raw:
        raise ValidationError(f"{label} must be a non-empty repository-relative path")
    path = (REPO_ROOT / raw).resolve()
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValidationError(f"{label} escapes repository: {raw}") from exc
    return path


def download_file(raw: object, label: str) -> Path:
    if not isinstance(raw, str) or not raw.startswith("/downloads/"):
        raise ValidationError(f"{label} must start with /downloads/: {raw!r}")
    parsed = urlparse(raw)
    relative = unquote(parsed.path).removeprefix("/")
    return repo_file(f"site/{relative}", label)


def validate() -> tuple[int, int]:
    routes_manifest = load_json(ROUTE_MANIFEST)
    salvage_manifest = load_json(SALVAGE_MANIFEST)
    routes = require_list(routes_manifest, "routes", ROUTE_MANIFEST)
    pages = require_list(salvage_manifest, "pages", SALVAGE_MANIFEST)
    errors: list[str] = []

    preserved: dict[str, str] = {}
    for index, item in enumerate(routes):
        label = f"routes[{index}]"
        source = item.get("source_html_path")
        try:
            if not repo_file(source, f"{label}.source_html_path").is_file():
                errors.append(f"{label}.source_html_path does not exist: {source}")
        except ValidationError as exc:
            errors.append(str(exc))
        route = item.get("route")
        if item.get("preserve_route") is True:
            if not isinstance(route, str) or not route.startswith("/"):
                errors.append(f"{label}.route must be an absolute public path")
            elif route in preserved:
                errors.append(
                    f"duplicate preserved route {route!r}: {preserved[route]} and {label}"
                )
            else:
                preserved[route] = label

    salvage_routes: set[str] = set()
    salvage_preserved: dict[str, str] = {}
    for index, item in enumerate(pages):
        label = f"pages[{index}]"
        route = item.get("route")
        if isinstance(route, str):
            salvage_routes.add(route)
            if item.get("preserve_route") is True:
                if route in salvage_preserved:
                    errors.append(
                        f"duplicate preserved salvage route {route!r}: "
                        f"{salvage_preserved[route]} and {label}"
                    )
                else:
                    salvage_preserved[route] = label
        elif item.get("preserve_route") is True:
            errors.append(f"{label}.route must be an absolute public path")
        source = item.get("source_html_path")
        try:
            if not repo_file(source, f"{label}.source_html_path").is_file():
                errors.append(f"{label}.source_html_path does not exist: {source}")
        except ValidationError as exc:
            errors.append(str(exc))

        content = item.get("corresponding_content_path")
        if content is not None:
            try:
                if not repo_file(content, f"{label}.corresponding_content_path").is_file():
                    errors.append(
                        f"{label}.corresponding_content_path does not exist: {content}"
                    )
            except ValidationError as exc:
                errors.append(str(exc))

        downloads = item.get("download_links")
        if not isinstance(downloads, list):
            errors.append(f"{label}.download_links must be an array")
        else:
            for download_index, download in enumerate(downloads):
                download_label = f"{label}.download_links[{download_index}]"
                try:
                    if not download_file(download, download_label).is_file():
                        errors.append(f"{download_label} does not exist: {download}")
                except ValidationError as exc:
                    errors.append(str(exc))

        status = item.get("salvage_status")
        if status not in SALVAGE_STATUSES:
            errors.append(
                f"{label}.salvage_status is invalid: {status!r}; "
                f"expected one of {sorted(SALVAGE_STATUSES)}"
            )

    route_set = set(preserved)
    if route_set != salvage_routes:
        errors.append(
            "route/salvage manifest route sets differ: "
            f"routes-only={sorted(route_set - salvage_routes)}, "
            f"salvage-only={sorted(salvage_routes - route_set)}"
        )
    if routes_manifest.get("route_count") != len(routes):
        errors.append("route_count does not match routes array length")
    if salvage_manifest.get("page_count") != len(pages):
        errors.append("page_count does not match pages array length")

    if errors:
        raise ValidationError("\n".join(errors))
    return len(routes), len(pages)


def main() -> int:
    try:
        route_count, page_count = validate()
    except (OSError, ValidationError) as exc:
        print(f"site manifest validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(
        "site manifest validation: OK "
        f"({route_count} preserved routes, {page_count} salvage records)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
