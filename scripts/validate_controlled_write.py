#!/usr/bin/env python3
"""Validate one-page structured publishing controlled writes.

This script is intended for PR CI. It verifies that a controlled-write PR either:

1. Changes exactly one supported public article HTML file under site/ and that the
   promoted file is byte-identical to the structured candidate generated from
   content/ + publishing/;
2. Is a gate-only PR that changes only this validator / workflow; or
3. Is a non-controlled-write PR where no supported public article HTML file is
   changed, in which case the controlled-write gate is skipped.

The dedicated new-document publication validator owns registered publication
routes and their site/publishing bridge assets. A PR carrying a production
publication receipt is therefore delegated to that validator instead of being
classified by this legacy controlled-write gate.

It does not write to site/.

ページ作成日時：2026-07-23 12:08 JST
最終更新日時：2026-09-02 12:20 JST
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_RE = re.compile(r"^site/series/genai-shikumi-deep-dive/([^/]+)/index\.html$")
SERIES_PUBLISH_SITE_RE = re.compile(r"^site/series/ai-dialogue-intro/(?:[^/]+/)?index\.html$")
NOTES_PUBLISH_SITE_RE = re.compile(
    r"^site/notes/(?:index|themes|[a-z0-9][a-z0-9-]*/(?:index|timeline))\.html$"
)
RELATED_THEMES_CROSS_REFERENCE = "site/article/state-change/bibliography.html"
GATE_ONLY_ALLOWLIST = {
    ".github/workflows/validate-controlled-write.yml",
    "scripts/validate_controlled_write.py",
}

EXPECTED_ARGS = [
    "--expected-theme",
    "default-academic",
    "--expected-collection",
    "core",
    "--expected-base",
    "default-academic",
    "--expected-season",
    "none",
    "--expected-hero-variant",
    "text-only",
    "--expected-text-contrast",
    "dark",
    "--expected-asset-role",
    "none",
    "--expected-asset-status",
    "none",
    "--expected-production-enabled",
    "true",
]


def run(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def changed_files(base_ref: str) -> list[str]:
    result = run(["git", "diff", "--name-only", f"{base_ref}...HEAD"], capture=True)
    return sorted(line.strip() for line in result.stdout.splitlines() if line.strip())


def source_for_target(target: str) -> Path:
    match = TARGET_RE.match(target)
    if not match:
        raise ValueError(f"unsupported controlled-write target: {target}")
    slug = match.group(1)
    return REPO_ROOT / "content" / "series" / "genai-shikumi-deep-dive" / f"{slug}.md"


def fixture_candidate_path(target: str, fixture_root: Path) -> Path:
    relative = target.removeprefix("site/").removesuffix("/index.html")
    return fixture_root / relative / "candidate.html"


def validate_scope(files: list[str], base_ref: str) -> str | None:
    publication_receipts = [
        path for path in files
        if path.startswith("publishing/releases/") and path.endswith(".json")
    ]
    if publication_receipts:
        if len(publication_receipts) != 1:
            raise RuntimeError("new-document promotion PR must contain exactly one publication receipt")
        run([
            sys.executable,
            "scripts/validate_new_document_publication_pr.py",
            "--base-ref",
            base_ref,
        ])
        print("new-document promotion PR: delegated from controlled-write validator")
        return None

    site_targets = [path for path in files if TARGET_RE.match(path)]
    site_changes = [path for path in files if path.startswith("site/")]

    if len(site_targets) > 1:
        raise RuntimeError("controlled-write PR must change at most one public article HTML file:\n" + "\n".join(site_targets))

    series_publish_site_changes = [path for path in site_changes if SERIES_PUBLISH_SITE_RE.match(path)]
    notes_publish_site_changes = [path for path in site_changes if NOTES_PUBLISH_SITE_RE.match(path)]
    publication_bridge_changes = [path for path in site_changes if path.startswith("site/publishing/")]
    related_themes_cross_reference = (
        {RELATED_THEMES_CROSS_REFERENCE}
        if "site/notes/themes.html" in notes_publish_site_changes
        else set()
    )
    delegated_publication_changes = set(publication_bridge_changes)

    unexpected_site = sorted(
        set(site_changes)
        - set(site_targets)
        - set(series_publish_site_changes)
        - set(notes_publish_site_changes)
        - related_themes_cross_reference
        - delegated_publication_changes
    )
    if unexpected_site:
        raise RuntimeError("unexpected site/ changes:\n" + "\n".join(unexpected_site))

    if not site_targets:
        if set(files) <= GATE_ONLY_ALLOWLIST:
            print("controlled-write gate-only change: OK")
        elif delegated_publication_changes:
            print("dedicated publication bridge present: delegated")
        else:
            print("controlled-write target not present: skipped")
        return None

    allowed = set(site_targets) | GATE_ONLY_ALLOWLIST
    unexpected = sorted(set(files) - allowed)
    if unexpected:
        raise RuntimeError("controlled-write PR has unexpected changes:\n" + "\n".join(unexpected))

    return site_targets[0]


def validate_target(target: str, base_ref: str, fixture_root: Path, tmp_root: Path) -> None:
    source = source_for_target(target)
    if not source.is_file():
        raise RuntimeError(f"content source is missing for target {target}: {source.relative_to(REPO_ROOT)}")

    if fixture_root.resolve().is_relative_to((REPO_ROOT / "site").resolve()):
        raise RuntimeError("fixture root must not be inside site/")
    if tmp_root.resolve().is_relative_to((REPO_ROOT / "site").resolve()):
        raise RuntimeError("tmp root must not be inside site/")

    shutil.rmtree(fixture_root, ignore_errors=True)
    shutil.rmtree(tmp_root, ignore_errors=True)

    run([
        sys.executable,
        "scripts/build_promotion_fixture.py",
        "--source",
        str(source.relative_to(REPO_ROOT)),
        "--fixture-root",
        str(fixture_root.relative_to(REPO_ROOT)),
        "--tmp-root",
        str(tmp_root.relative_to(REPO_ROOT)),
    ])

    candidate = fixture_candidate_path(target, fixture_root)
    promoted = REPO_ROOT / target
    if not candidate.is_file():
        raise RuntimeError(f"candidate fixture is missing: {candidate.relative_to(REPO_ROOT)}")
    if candidate.read_bytes() != promoted.read_bytes():
        raise RuntimeError("promoted site HTML is not byte-identical to regenerated structured candidate")

    base_current = fixture_root / "base-current.html"
    base_html = run(["git", "show", f"{base_ref}:{target}"], capture=True).stdout
    base_current.write_text(base_html, encoding="utf-8")

    run([
        sys.executable,
        "scripts/validate_structured_preview.py",
        str(base_current.relative_to(REPO_ROOT)),
        target,
        *EXPECTED_ARGS,
    ])

    print("controlled-write target: OK")
    print(f"target: {target}")
    print(f"source: {source.relative_to(REPO_ROOT)}")
    print(f"candidate: {candidate.relative_to(REPO_ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one-page controlled writes for structured publishing.")
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--fixture-root", default="_controlled_write_fixture")
    parser.add_argument("--tmp-root", default="_controlled_write_tmp")
    args = parser.parse_args()

    files = changed_files(args.base_ref)
    if not files:
        raise RuntimeError("no changed files detected")

    print("changed files:")
    for path in files:
        print(f"- {path}")

    target = validate_scope(files, args.base_ref)
    if target is None:
        return 0

    validate_target(
        target,
        args.base_ref,
        (REPO_ROOT / args.fixture_root).resolve(),
        (REPO_ROOT / args.tmp_root).resolve(),
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

# 更新履歴
# - 2026-09-02 12:20 JST：publication receiptを持つ正式new-document promotion PRを正本final validatorへ委譲。
# - 2026-08-29 00:20 JST：MEMBRANE正式publication targetとsite/publishing bridgeを専用publication validatorへ委譲。
