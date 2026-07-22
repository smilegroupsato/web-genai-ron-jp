#!/usr/bin/env python3
"""Generate a controlled publishing promotion fixture without touching site/.

The fixture creates a structured candidate outside the public tree, compares it
with one explicitly registered public HTML file, and writes a machine-readable
report plus unified diff. It has no site-write mode.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import shutil
from pathlib import Path
from typing import Mapping

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

from build_content_pages import BuildError, parse_front_matter
from build_structured_preview import REPO_ROOT, build_one

DEFAULT_FIXTURE = (
    REPO_ROOT / "publishing" / "promotions" / "04-tool-execution-loop.yml"
)
SITE_ROOT = (REPO_ROOT / "site").resolve()
PROMOTION_ROOT = (REPO_ROOT / "_promotion_fixture").resolve()


def require_mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise BuildError(f"promotion fixture mapping is missing or invalid: {label}")
    return value


def load_fixture(path: Path) -> dict[str, object]:
    if yaml is None:
        raise BuildError(
            "PyYAML is required. Install requirements-publishing.txt in an isolated environment."
        )
    if not path.is_file():
        raise BuildError(f"promotion fixture is missing: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise BuildError("promotion fixture must be a YAML mapping")
    return data


def repo_path(value: object, label: str) -> Path:
    raw = str(value or "").strip()
    if not raw:
        raise BuildError(f"promotion path is missing: {label}")
    path = (REPO_ROOT / raw).resolve()
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise BuildError(f"promotion path escapes repository: {label}") from exc
    return path


def ensure_outside_site(path: Path, label: str) -> None:
    try:
        path.relative_to(SITE_ROOT)
    except ValueError:
        return
    raise BuildError(f"{label} must remain outside site/: {path}")


def ensure_promotion_root(path: Path, label: str) -> None:
    try:
        path.relative_to(PROMOTION_ROOT)
    except ValueError as exc:
        raise BuildError(f"{label} must remain under _promotion_fixture/: {path}") from exc


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def line_stats(diff_lines: list[str]) -> dict[str, int]:
    additions = sum(
        1 for line in diff_lines if line.startswith("+") and not line.startswith("+++")
    )
    deletions = sum(
        1 for line in diff_lines if line.startswith("-") and not line.startswith("---")
    )
    hunks = sum(1 for line in diff_lines if line.startswith("@@"))
    return {"additions": additions, "deletions": deletions, "hunks": hunks}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a dry-run GENAI-RON promotion fixture."
    )
    parser.add_argument(
        "--fixture",
        default=str(DEFAULT_FIXTURE.relative_to(REPO_ROOT)),
        help="Promotion fixture YAML path relative to the repository root.",
    )
    args = parser.parse_args()

    fixture_path = repo_path(args.fixture, "fixture")
    fixture = load_fixture(fixture_path)

    if fixture.get("write_enabled") is not False:
        raise BuildError("promotion fixture must explicitly set write_enabled: false")
    if str(fixture.get("status", "")).strip() != "dry-run-only":
        raise BuildError("promotion fixture status must be dry-run-only")

    promotion_id = str(fixture.get("promotion_id", "")).strip()
    if not promotion_id:
        raise BuildError("promotion_id is required")

    source = require_mapping(fixture.get("source"), "source")
    current = require_mapping(
        fixture.get("current_public_artifact"), "current_public_artifact"
    )
    candidate = require_mapping(fixture.get("candidate"), "candidate")
    scope = require_mapping(fixture.get("scope"), "scope")

    content_path = repo_path(source.get("content_path"), "source.content_path")
    current_path = repo_path(current.get("path"), "current_public_artifact.path")
    candidate_root = repo_path(candidate.get("root"), "candidate.root")
    report_path = repo_path(candidate.get("report"), "candidate.report")
    diff_path = repo_path(candidate.get("diff"), "candidate.diff")

    ensure_outside_site(candidate_root, "candidate.root")
    ensure_outside_site(report_path, "candidate.report")
    ensure_outside_site(diff_path, "candidate.diff")
    ensure_promotion_root(candidate_root, "candidate.root")
    ensure_promotion_root(report_path, "candidate.report")
    ensure_promotion_root(diff_path, "candidate.diff")

    if not content_path.is_file():
        raise BuildError(f"content source does not exist: {content_path}")
    if not current_path.is_file():
        raise BuildError(f"current public artifact does not exist: {current_path}")
    try:
        current_path.relative_to(SITE_ROOT)
    except ValueError as exc:
        raise BuildError("current public artifact must be under site/") from exc

    allowed = scope.get("allowed_site_paths")
    if not isinstance(allowed, list) or len(allowed) != 1:
        raise BuildError("scope.allowed_site_paths must contain exactly one path")
    allowed_path = repo_path(allowed[0], "scope.allowed_site_paths[0]")
    if allowed_path != current_path:
        raise BuildError("registered current artifact and allowed site path differ")

    source_text = content_path.read_text(encoding="utf-8")
    meta, _ = parse_front_matter(source_text)
    expected_slug = str(source.get("expected_slug", "")).strip()
    actual_slug = str(meta.get("slug", "")).strip()
    if not expected_slug or actual_slug != expected_slug:
        raise BuildError(
            f"source slug mismatch: expected {expected_slug!r}, got {actual_slug!r}"
        )

    theme_id = str(source.get("theme_id", "default-academic")).strip()
    if not theme_id:
        raise BuildError("source.theme_id is required")

    fixture_output_root = report_path.parent
    ensure_promotion_root(fixture_output_root, "fixture output root")
    if fixture_output_root.exists():
        shutil.rmtree(fixture_output_root)
    fixture_output_root.mkdir(parents=True, exist_ok=True)

    generated_path = build_one(content_path, candidate_root, theme_id)
    ensure_outside_site(generated_path.resolve(), "generated candidate")

    expected_candidate = candidate_root / expected_slug.strip("/") / "index.html"
    if generated_path.resolve() != expected_candidate.resolve():
        raise BuildError(
            f"candidate output mismatch: expected {expected_candidate}, got {generated_path}"
        )

    current_text = current_path.read_text(encoding="utf-8")
    candidate_text = generated_path.read_text(encoding="utf-8")
    diff_lines = list(
        difflib.unified_diff(
            current_text.splitlines(keepends=True),
            candidate_text.splitlines(keepends=True),
            fromfile=str(current_path.relative_to(REPO_ROOT)),
            tofile=str(generated_path.relative_to(REPO_ROOT)),
        )
    )
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.write_text("".join(diff_lines), encoding="utf-8")

    report = {
        "promotion_id": promotion_id,
        "status": "dry-run-generated",
        "write_enabled": False,
        "fixture": str(fixture_path.relative_to(REPO_ROOT)),
        "source": str(content_path.relative_to(REPO_ROOT)),
        "slug": actual_slug,
        "theme_id": theme_id,
        "current_public_artifact": {
            "path": str(current_path.relative_to(REPO_ROOT)),
            "sha256": sha256(current_path),
            "size_bytes": current_path.stat().st_size,
            "line_count": len(current_text.splitlines()),
        },
        "candidate_artifact": {
            "path": str(generated_path.relative_to(REPO_ROOT)),
            "sha256": sha256(generated_path),
            "size_bytes": generated_path.stat().st_size,
            "line_count": len(candidate_text.splitlines()),
        },
        "diff": {
            "path": str(diff_path.relative_to(REPO_ROOT)),
            **line_stats(diff_lines),
            "identical_bytes": current_text == candidate_text,
        },
        "scope": {
            "allowed_site_paths": [str(current_path.relative_to(REPO_ROOT))],
            "site_mutated": False,
        },
        "rollback": {
            "base_commit": str(current.get("rollback_base_commit", "")).strip(),
            "reference_path": str(current_path.relative_to(REPO_ROOT)),
        },
    }
    if not report["rollback"]["base_commit"]:
        raise BuildError("rollback_base_commit is required")

    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"candidate: {generated_path.relative_to(REPO_ROOT)}")
    print(f"report: {report_path.relative_to(REPO_ROOT)}")
    print(f"diff: {diff_path.relative_to(REPO_ROOT)}")
    print(
        "diff stats: "
        f"+{report['diff']['additions']} -{report['diff']['deletions']} "
        f"hunks={report['diff']['hunks']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
