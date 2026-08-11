#!/usr/bin/env python3
"""Extract the seven public genai-shikumi-technical pages into Markdown."""

from __future__ import annotations

import argparse
import sys

import extract_genai_shikumi_series_content as shared

SERIES = "genai-shikumi-technical"
CHAPTERS = (
    "01-memory",
    "02-instruction-hierarchy",
    "03-tool-calling",
    "04-context-window-retrieval",
    "05-grounding-hallucination",
    "06-workflow-design",
)
PAGES = (
    shared.Page(
        route=f"/series/{SERIES}/",
        source_html_path=f"site/series/{SERIES}/index.html",
        output_path=f"content/series/{SERIES}/index.md",
        page_type="series-index",
        order=None,
        chapter=None,
    ),
    *(
        shared.Page(
            route=f"/series/{SERIES}/{chapter}/",
            source_html_path=f"site/series/{SERIES}/{chapter}/index.html",
            output_path=f"content/series/{SERIES}/{chapter}.md",
            page_type="series-entry",
            order=order,
            chapter=chapter,
        )
        for order, chapter in enumerate(CHAPTERS, start=1)
    ),
)


def extract(page: shared.Page) -> str:
    """Use the established series renderer with this series identifier."""
    original_series = shared.SERIES
    try:
        shared.SERIES = SERIES
        return shared.extract(page)
    finally:
        shared.SERIES = original_series


def write_or_check(write: bool) -> None:
    for page in PAGES:
        rendered = extract(page)
        if write:
            page.output_md.parent.mkdir(parents=True, exist_ok=True)
            page.output_md.write_text(rendered, encoding="utf-8")
        elif not page.output_md.is_file() or page.output_md.read_text(encoding="utf-8") != rendered:
            raise RuntimeError(f"Markdown output does not match extraction: {page.output_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        write_or_check(write=not args.check)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"genai-shikumi-technical series extraction: FAILED\n{exc}", file=sys.stderr)
        return 1
    mode = "check" if args.check else "write"
    print(f"genai-shikumi-technical series extraction: OK ({mode}, 7 Markdown sources)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
