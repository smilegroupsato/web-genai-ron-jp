#!/usr/bin/env python3
"""Sync and validate /publishing/** assets required by one promoted HTML page.

ページ作成日時：2026-08-28 18:22 JST
最終更新日時：2026-08-28 18:22 JST
"""

from __future__ import annotations

import argparse
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "publishing"
SITE_ROOT = REPO_ROOT / "site"

CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", re.IGNORECASE)
CSS_IMPORT_RE = re.compile(r"@import\s+(?:url\(\s*)?['\"]([^'\"]+)['\"]", re.IGNORECASE)


class RefCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("href", "src"):
            value = values.get(key)
            if value:
                self.refs.append(value)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def normalize_publication_ref(raw: str, current: Path | None = None) -> Path | None:
    parsed = urlparse(raw.strip())
    if parsed.scheme or parsed.netloc:
        return None
    path = parsed.path
    if not path:
        return None
    if path.startswith("/publishing/"):
        relative = Path(path.removeprefix("/publishing/"))
    elif current is not None and not path.startswith("/"):
        relative = current.parent / path
    else:
        return None
    resolved = (SOURCE_ROOT / relative).resolve()
    try:
        return resolved.relative_to(SOURCE_ROOT)
    except ValueError as exc:
        raise ValueError(f"publication asset reference escapes publishing/: {raw}") from exc


def css_refs(relative: Path) -> list[Path]:
    source = SOURCE_ROOT / relative
    if source.suffix.lower() != ".css":
        return []
    text = source.read_text(encoding="utf-8")
    refs: list[Path] = []
    for match in CSS_URL_RE.finditer(text):
        ref = normalize_publication_ref(match.group(2), relative)
        if ref is not None:
            refs.append(ref)
    for match in CSS_IMPORT_RE.finditer(text):
        ref = normalize_publication_ref(match.group(1), relative)
        if ref is not None:
            refs.append(ref)
    return refs


def required_assets(html_path: Path) -> list[Path]:
    parser = RefCollector()
    parser.feed(html_path.read_text(encoding="utf-8"))
    queue = [ref for raw in parser.refs if (ref := normalize_publication_ref(raw)) is not None]
    seen: set[Path] = set()
    while queue:
        relative = queue.pop(0)
        if relative in seen:
            continue
        source = SOURCE_ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(f"missing publication source asset: publishing/{relative.as_posix()}")
        seen.add(relative)
        queue.extend(css_refs(relative))
    return sorted(seen, key=lambda path: path.as_posix())


def sync(html_path: Path) -> list[Path]:
    assets = required_assets(html_path)
    for relative in assets:
        source = SOURCE_ROOT / relative
        target = SITE_ROOT / "publishing" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return assets


def validate(html_path: Path) -> list[Path]:
    assets = required_assets(html_path)
    for relative in assets:
        source = SOURCE_ROOT / relative
        target = SITE_ROOT / "publishing" / relative
        if not target.is_file():
            raise FileNotFoundError(f"missing site publication asset: site/publishing/{relative.as_posix()}")
        if target.read_bytes() != source.read_bytes():
            raise ValueError(f"site publication asset differs from source: {relative.as_posix()}")
    return assets


def repo_path(raw: str) -> Path:
    path = (REPO_ROOT / raw).resolve()
    path.relative_to(REPO_ROOT)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Bridge publication assets into site/ for one page.")
    parser.add_argument("command", choices=("sync", "validate", "list"))
    parser.add_argument("--html", required=True)
    args = parser.parse_args()
    html_path = repo_path(args.html)
    if not html_path.is_file():
        raise FileNotFoundError(html_path)
    assets = required_assets(html_path) if args.command == "list" else sync(html_path) if args.command == "sync" else validate(html_path)
    for relative in assets:
        print(f"publishing/{relative.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# 更新履歴
# - 2026-08-28 18:22 JST：HTML/CSS参照を再帰追跡し、必要なpublishing資産だけをsiteへbyte-identical同期するbridgeを追加。
