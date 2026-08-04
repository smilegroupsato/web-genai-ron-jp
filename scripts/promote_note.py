#!/usr/bin/env python3
"""Explicitly promote one regenerated research note into site/.

ページ作成日時：2026-08-04 16:22 JST
最終更新日時：2026-08-04 18:42 JST

This command never accepts a glob or destination path. The source metadata and
the narrow notes-v0 path contract determine the only permitted target.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from build_content_pages import BuildError
from build_notes_preview import (
    REPO_ROOT,
    SITE_ROOT,
    build_one,
    output_name_for_source,
    validate_source_path,
)

DEFAULT_CANDIDATE_ROOT = REPO_ROOT / "_notes_promotion_candidate"


def promote(source: Path, candidate_root: Path, write_site: bool) -> Path:
    slug = validate_source_path(source)
    candidate = build_one(source, candidate_root)
    output_name = output_name_for_source(source)
    target = SITE_ROOT / "notes" / slug / output_name
    expected = candidate_root.resolve() / "notes" / slug / output_name
    if candidate.resolve() != expected:
        raise BuildError("generated note candidate path is outside the controlled target")
    if not write_site:
        raise BuildError("refusing site write without --write-site")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(candidate, target)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote exactly one research note.")
    parser.add_argument(
        "--source",
        required=True,
        help="content/notes/index.md or content/notes/<slug>/<page>.md",
    )
    parser.add_argument("--candidate-root", default=str(DEFAULT_CANDIDATE_ROOT))
    parser.add_argument("--write-site", action="store_true", help="Required explicit site-write confirmation.")
    args = parser.parse_args()

    source = (REPO_ROOT / args.source).resolve()
    root_arg = Path(args.candidate_root)
    candidate_root = root_arg if root_arg.is_absolute() else REPO_ROOT / root_arg
    target = promote(source, candidate_root, args.write_site)
    print(target.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, ValueError) as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)
