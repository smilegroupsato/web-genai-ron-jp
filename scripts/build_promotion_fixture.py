#!/usr/bin/env python3
"""Build a controlled promotion dry-run fixture without writing to site/.

ページ作成日時：2026-07-23 11:28 JST
最終更新日時：2026-07-23 11:28 JST

The fixture compares the current public HTML under site/ with the structured
candidate generated from content/ + publishing/. It writes review artifacts only
under _promotion_fixture/ and never changes site/.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict

from build_content_pages import BuildError
from build_structured_preview import REPO_ROOT, build_one

DEFAULT_FIXTURE_ROOT = REPO_ROOT / "_promotion_fixture"
DEFAULT_TMP_ROOT = REPO_ROOT / "_promotion_fixture_tmp"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def count_diff(diff: str) -> Dict[str, int]:
    additions = 0
    deletions = 0
    hunks = 0
    for line in diff.splitlines():
        if line.startswith("@@"):
            hunks += 1
        elif line.startswith("+") and not line.startswith("+++"):
            additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1
    return {"additions": additions, "deletions": deletions, "hunks": hunks}


def repo_relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def ensure_not_inside_site(path: Path, label: str) -> None:
    site_root = (REPO_ROOT / "site").resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(site_root)
    except ValueError:
        return
    raise BuildError(f"{label} must not be inside site/: {repo_relative(resolved)}")


def render_report(report: Dict[str, object]) -> str:
    diff_stats = report["diff"]
    return "\n".join(
        [
            f"# Promotion dry-run fixture｜{report['promotion_id']}",
            "",
            "ページ作成日時：2026-07-23 11:28 JST  ",
            "最終更新日時：2026-07-23 11:28 JST",
            "",
            "Status: dry-run / no site write",
            "",
            "## Target",
            "",
            f"- Source: `{report['source']}`",
            f"- Current site HTML: `{report['current_site_path']}`",
            f"- Candidate HTML: `{report['candidate_fixture_path']}`",
            f"- Current fixture HTML: `{report['current_fixture_path']}`",
            f"- Diff: `{report['diff_path']}`",
            "",
            "## Checksums",
            "",
            f"- current_sha256: `{report['current_sha256']}`",
            f"- candidate_sha256: `{report['candidate_sha256']}`",
            f"- byte_identical: `{str(report['byte_identical']).lower()}`",
            "",
            "## Diff stats",
            "",
            f"- additions: {diff_stats['additions']}",
            f"- deletions: {diff_stats['deletions']}",
            f"- hunks: {diff_stats['hunks']}",
            "",
            "## Promotion policy",
            "",
            "This fixture is review-only. It does not write to `site/`.",
            "A later controlled-write PR may copy the candidate to the target site path only after semantic parity and visual QA pass.",
            "",
            "## 更新履歴",
            "",
            "- 2026-07-23 11:28 JST：08ページのstructured promotion dry-run fixtureを生成。",
            "",
        ]
    )


def build_fixture(source: str, fixture_root: Path, tmp_root: Path, theme_id: str | None) -> Dict[str, object]:
    source_path = (REPO_ROOT / source).resolve()
    if not source_path.is_file():
        raise BuildError(f"source file is missing: {source}")
    try:
        source_path.relative_to(REPO_ROOT / "content")
    except ValueError as exc:
        raise BuildError("promotion source must be under content/") from exc

    ensure_not_inside_site(fixture_root, "fixture root")
    ensure_not_inside_site(tmp_root, "temporary fixture root")

    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)

    candidate_tmp = build_one(source_path, tmp_root, theme_id)
    relative_output = candidate_tmp.relative_to(tmp_root)
    current_site = REPO_ROOT / "site" / relative_output
    if not current_site.is_file():
        raise BuildError(f"current site HTML is missing: {repo_relative(current_site)}")

    fixture_dir = fixture_root / relative_output.parent
    fixture_dir.mkdir(parents=True, exist_ok=True)

    current_html = current_site.read_text(encoding="utf-8")
    candidate_html = candidate_tmp.read_text(encoding="utf-8")

    current_fixture = fixture_dir / "current.html"
    candidate_fixture = fixture_dir / "candidate.html"
    diff_path = fixture_dir / "diff.patch"
    report_json_path = fixture_dir / "report.json"
    report_md_path = fixture_dir / "REPORT.md"

    current_fixture.write_text(current_html, encoding="utf-8")
    candidate_fixture.write_text(candidate_html, encoding="utf-8")

    diff = "".join(
        difflib.unified_diff(
            current_html.splitlines(keepends=True),
            candidate_html.splitlines(keepends=True),
            fromfile=repo_relative(current_site),
            tofile=repo_relative(candidate_fixture),
            lineterm="",
        )
    )
    diff_path.write_text(diff, encoding="utf-8")

    report: Dict[str, object] = {
        "promotion_id": relative_output.parent.as_posix().replace("/", "__"),
        "source": repo_relative(source_path),
        "current_site_path": repo_relative(current_site),
        "current_fixture_path": repo_relative(current_fixture),
        "candidate_fixture_path": repo_relative(candidate_fixture),
        "diff_path": repo_relative(diff_path),
        "report_md_path": repo_relative(report_md_path),
        "current_sha256": sha256_text(current_html),
        "candidate_sha256": sha256_text(candidate_html),
        "byte_identical": current_html == candidate_html,
        "diff": count_diff(diff),
        "site_written": False,
    }

    report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_md_path.write_text(render_report(report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build promotion dry-run fixtures without touching site/.")
    parser.add_argument("--source", required=True, help="Content Markdown path relative to repo root.")
    parser.add_argument("--fixture-root", default=str(DEFAULT_FIXTURE_ROOT), help="Dry-run fixture output root.")
    parser.add_argument("--tmp-root", default=str(DEFAULT_TMP_ROOT), help="Temporary structured output root.")
    parser.add_argument("--theme-id", help="Optional structured theme id.")
    args = parser.parse_args()

    fixture_root = Path(args.fixture_root)
    if not fixture_root.is_absolute():
        fixture_root = (REPO_ROOT / fixture_root).resolve()
    tmp_root = Path(args.tmp_root)
    if not tmp_root.is_absolute():
        tmp_root = (REPO_ROOT / tmp_root).resolve()

    report = build_fixture(args.source, fixture_root, tmp_root, args.theme_id)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
