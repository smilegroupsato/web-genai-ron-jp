#!/usr/bin/env python3
"""Extract the public genai-shikumi-deep-dive index into Markdown."""

from __future__ import annotations

import argparse
import sys

import extract_genai_shikumi_series_content as shared

SERIES = "genai-shikumi-deep-dive"
ROUTE = f"/series/{SERIES}/"
PAGE = shared.Page(
    route=ROUTE,
    source_html_path=f"site/series/{SERIES}/index.html",
    output_path=f"content/series/{SERIES}/index.md",
    page_type="series-index",
    order=None,
    chapter=None,
)


def extract() -> str:
    """Use the established series renderer with the deep-dive identifier."""
    original_series = shared.SERIES
    try:
        shared.SERIES = SERIES
        return shared.extract(PAGE)
    finally:
        shared.SERIES = original_series


def write_or_check(write: bool) -> None:
    rendered = extract()
    if write:
        PAGE.output_md.parent.mkdir(parents=True, exist_ok=True)
        PAGE.output_md.write_text(rendered, encoding="utf-8")
    elif not PAGE.output_md.is_file() or PAGE.output_md.read_text(encoding="utf-8") != rendered:
        raise RuntimeError(f"Markdown output does not match extraction: {PAGE.output_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        write_or_check(write=not args.check)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"genai-shikumi-deep-dive index extraction: FAILED\n{exc}", file=sys.stderr)
        return 1
    mode = "check" if args.check else "write"
    print(f"genai-shikumi-deep-dive index extraction: OK ({mode}, 1 Markdown source)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
