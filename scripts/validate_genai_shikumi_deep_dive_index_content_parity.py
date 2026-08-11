#!/usr/bin/env python3
"""Validate semantic parity for the genai-shikumi-deep-dive index source."""

from __future__ import annotations

import sys

import validate_genai_shikumi_series_content_parity as shared
from extract_genai_shikumi_deep_dive_index_content import PAGE, SERIES


def validate() -> float:
    """Run the full established series parity checks against the index page."""
    original = (shared.CHAPTERS, shared.PAGES, shared.SERIES)
    try:
        shared.CHAPTERS = ()
        shared.PAGES = (PAGE,)
        shared.SERIES = SERIES
        return shared.validate()
    finally:
        shared.CHAPTERS, shared.PAGES, shared.SERIES = original


def main() -> int:
    try:
        ratio = validate()
    except (OSError, KeyError, ValueError, shared.ParityError) as exc:
        print(f"genai-shikumi-deep-dive index parity validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(
        "genai-shikumi-deep-dive index parity validation: OK "
        f"(1 HTML, 1 Markdown, minimum text ratio {ratio:.6f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
