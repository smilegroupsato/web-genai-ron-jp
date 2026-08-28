#!/usr/bin/env python3
"""Prepare and promote a revision of an already-published registered document.

ページ作成日時：2026-08-29 00:43 JST
最終更新日時：2026-08-29 00:43 JST

This is intentionally separate from new_document_publication.py so the new-route
lane keeps its existing-target refusal unchanged. A revision is permitted only
when both the registered route and its site target already exist.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from build_content_pages import BuildError
from new_document_publication import (
    DEFAULT_CANDIDATE_ROOT,
    DEFAULT_REGISTRY,
    REPO_ROOT,
    SITE_ROOT,
    candidate_for,
    existing_routes,
    receipt_value,
    repo_path,
    resolve_entry,
    target_for_route,
    validate_receipt,
    write_json,
)


def validate_existing_route(entry: dict[str, object]) -> Path:
    route = str(entry["route"])
    target = target_for_route(route)
    if not target.is_file():
        raise BuildError(
            f"existing-publication revision requires current site target: {target.relative_to(REPO_ROOT)}"
        )
    if route not in existing_routes():
        raise BuildError(f"existing-publication revision requires registered public route: {route}")
    return target


def prepare_revision(
    entry_id: str,
    registry_path: Path,
    candidate_root: Path,
    receipt_path: Path,
) -> dict[str, object]:
    entry, source, index_source, index_path = resolve_entry(entry_id, registry_path)
    if entry.get("test_only"):
        raise BuildError("test fixture cannot use existing-publication revision lane")
    validate_existing_route(entry)

    candidate_relative = candidate_root.resolve().relative_to(REPO_ROOT)
    if not candidate_relative.parts or not candidate_relative.parts[0].startswith("_new_document_"):
        raise BuildError("candidate root must use a repository-local _new_document_* directory")

    expected_receipt = REPO_ROOT / "publishing" / "releases" / f"{entry_id}.json"
    if receipt_path.resolve() != expected_receipt.resolve():
        raise BuildError(f"receipt path must be {expected_receipt.relative_to(REPO_ROOT)}")

    candidate = candidate_for(entry, source, candidate_root)
    value = receipt_value(entry, source, index_source, index_path, registry_path, candidate)
    write_json(receipt_path, value)
    return value


def promote_revision(receipt_path: Path, expected_sha: str, write_site: bool) -> Path:
    receipt, regenerated = validate_receipt(receipt_path)
    if not write_site:
        raise BuildError("refusing site write without --write-site")
    if receipt.get("test_only"):
        raise BuildError("test fixture cannot be revised under site/")
    if expected_sha != receipt.get("candidate_sha256"):
        raise BuildError("--expected-sha does not match the reviewed candidate")

    entry, _, _, _ = resolve_entry(
        str(receipt["id"]),
        repo_path(str(receipt["registry"]), "receipt registry"),
    )
    target = validate_existing_route(entry)
    if receipt.get("target") != target.relative_to(REPO_ROOT).as_posix():
        raise BuildError("receipt target does not match existing site target")

    # Replace only after every receipt/SHA/route validation above has passed.
    target.write_bytes(regenerated)
    subprocess.run([sys.executable, "scripts/build_site_manifest.py"], cwd=REPO_ROOT, check=True)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Controlled revision for one existing GENAI-RON document.")
    sub = parser.add_subparsers(dest="command", required=True)

    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--id", required=True)
    prepare_parser.add_argument("--registry", default=str(DEFAULT_REGISTRY.relative_to(REPO_ROOT)))
    prepare_parser.add_argument("--candidate-root", default=str(DEFAULT_CANDIDATE_ROOT.relative_to(REPO_ROOT)))
    prepare_parser.add_argument("--receipt", required=True)

    promote_parser = sub.add_parser("promote")
    promote_parser.add_argument("--receipt", required=True)
    promote_parser.add_argument("--expected-sha", required=True)
    promote_parser.add_argument("--write-site", action="store_true")

    args = parser.parse_args()
    if args.command == "prepare":
        value = prepare_revision(
            args.id,
            repo_path(args.registry, "registry"),
            repo_path(args.candidate_root, "candidate root"),
            repo_path(args.receipt, "receipt"),
        )
        print(json.dumps(value, ensure_ascii=False, indent=2))
    else:
        target = promote_revision(
            repo_path(args.receipt, "receipt"),
            args.expected_sha,
            args.write_site,
        )
        print(target.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

# 更新履歴
# - 2026-08-29 00:43 JST：既存routeの再版専用prepare/promoteを新規追加。新規公開の上書き禁止は変更しない。
