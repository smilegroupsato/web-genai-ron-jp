#!/usr/bin/env python3
"""Validate semantic parity for the seven genai-shikumi-technical sources."""

from __future__ import annotations

import sys

import validate_genai_shikumi_series_content_parity as shared
from extract_genai_shikumi_technical_series_content import CHAPTERS, PAGES, SERIES


def validate() -> float:
    """Run the established full series parity checks against the technical pages."""
    original = (shared.CHAPTERS, shared.PAGES, shared.SERIES)
    try:
        shared.CHAPTERS = CHAPTERS
        shared.PAGES = PAGES
        shared.SERIES = SERIES
        return shared.validate()
    finally:
        shared.CHAPTERS, shared.PAGES, shared.SERIES = original


def main() -> int:
    try:
        ratio = validate()
    except (OSError, KeyError, ValueError, shared.ParityError) as exc:
        print(f"genai-shikumi-technical series parity validation: FAILED\n{exc}", file=sys.stderr)
        return 1
    print(
        "genai-shikumi-technical series parity validation: OK "
        f"(7 HTML, 7 Markdown, minimum text ratio {ratio:.6f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
