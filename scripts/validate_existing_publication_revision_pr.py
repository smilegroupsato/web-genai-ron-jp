#!/usr/bin/env python3
"""Validate a final PR that revises an already-published registered document.

ページ作成日時：2026-08-29 00:43 JST
最終更新日時：2026-09-02 16:59 JST
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from build_content_pages import BuildError
from new_document_publication import (
    REPO_ROOT,
    existing_routes,
    is_publication_theme_infra,
    load_registry,
    repo_path,
    target_for_route,
    validate_receipt,
)
from sync_publication_assets import required_assets, validate as validate_publication_assets

REVISION_VERSION = "0.1"
INFRA_ALLOWLIST = {
    ".github/workflows/existing-publication-revision.yml",
    ".github/workflows/validate-publishing-structure.yml",
    "scripts/revise_existing_publication.py",
    "scripts/validate_controlled_write.py",
    "scripts/validate_existing_publication_revision_pr.py",
    "scripts/validate_new_document_publication_pr.py",
}


def changed_files(base_ref: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return sorted({line for line in result.stdout.splitlines() if line})


def read_revision(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"invalid revision record: {path.relative_to(REPO_ROOT)}") from exc
    required = {
        "revision_version",
        "id",
        "reviewed_candidate_sha256",
        "target",
        "page_created_at",
        "last_updated_at",
    }
    if set(value) != required:
        raise BuildError("revision record has unexpected fields")
    if value["revision_version"] != REVISION_VERSION:
        raise BuildError("unsupported revision record version")
    return value


def validate(base_ref: str, registry_raw: str) -> None:
    files = changed_files(base_ref)
    if not files:
        raise BuildError("no changed files detected")

    revision_files = [
        path for path in files
        if path.startswith("publishing/revisions/") and path.endswith(".json")
    ]
    if not revision_files:
        publication_receipts = [
            path for path in files
            if path.startswith("publishing/releases/") and path.endswith(".json")
        ]
        if publication_receipts:
            if len(publication_receipts) != 1:
                raise BuildError("new-document promotion PR must contain exactly one publication receipt")
            subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_new_document_publication_pr.py",
                    "--base-ref",
                    base_ref,
                    "--registry",
                    registry_raw,
                ],
                cwd=REPO_ROOT,
                check=True,
            )
            print("new-document promotion PR: delegated from revision validator")
            return

        gate_hint = (
            "data/new-document-routes.json" in files
            or any(path.startswith("content/") for path in files)
        )
        if gate_hint:
            subprocess.run(
                [
                    sys.executable,
                    "scripts/new_document_publication.py",
                    "validate-pr",
                    "--base-ref",
                    base_ref,
                ],
                cwd=REPO_ROOT,
                check=True,
            )
            print("new-document gate-only PR: delegated from revision validator")
            return

        unexpected = sorted(path for path in files if path not in INFRA_ALLOWLIST and not is_publication_theme_infra(path))
        if unexpected:
            raise BuildError(
                "existing-publication revision infra PR contains unrelated changes:\n"
                + "\n".join(unexpected)
            )
        print("existing-publication revision infra change: OK")
        return
    if len(revision_files) != 1:
        raise BuildError("revision PR must change exactly one revision record")

    revision_path = REPO_ROOT / revision_files[0]
    revision = read_revision(revision_path)
    entry_id = str(revision["id"])
    registry_path = repo_path(registry_raw, "registry")
    entries = load_registry(registry_path)
    if entry_id not in entries:
        raise BuildError(f"revision id is not registered: {entry_id}")
    entry = entries[entry_id]
    if entry.get("test_only"):
        raise BuildError("test fixture cannot use revision lane")

    target = target_for_route(str(entry["route"])).relative_to(REPO_ROOT).as_posix()
    target_path = REPO_ROOT / target
    if not target_path.is_file():
        raise BuildError("revision target is missing from current tree")
    if str(revision["target"]) != target:
        raise BuildError("revision record target does not match registry")
    if str(entry["route"]) not in existing_routes():
        raise BuildError("revision route is missing from site route manifest")

    receipt_path = REPO_ROOT / "publishing" / "releases" / f"{entry_id}.json"
    receipt, regenerated = validate_receipt(receipt_path, require_candidate=False)
    reviewed_sha = str(revision["reviewed_candidate_sha256"])
    if reviewed_sha != receipt.get("candidate_sha256"):
        raise BuildError("revision record SHA does not match publication receipt")
    if target_path.read_bytes() != regenerated:
        raise BuildError("existing public target is not byte-identical to reviewed candidate")

    required_bridge = {
        f"site/publishing/{relative.as_posix()}" for relative in required_assets(target_path)
    }
    changed_bridge = {path for path in files if path.startswith("site/publishing/")}
    extra_bridge = sorted(changed_bridge - required_bridge)
    if extra_bridge:
        raise BuildError(
            "revision PR contains unreferenced publishing bridge assets:\n"
            + "\n".join(extra_bridge)
        )
    validate_publication_assets(target_path)

    site_changes = {path for path in files if path.startswith("site/")}
    allowed_site = changed_bridge | ({target} if target in files else set())
    if site_changes != allowed_site:
        raise BuildError(
            "revision PR has unrelated site changes:\n" + "\n".join(sorted(site_changes))
        )

    generated_optional = {
        target,
        f"publishing/releases/{entry_id}.json",
        "data/site-routes.manifest.json",
        "data/site-content-salvage.manifest.json",
    }
    allowed = {revision_files[0]} | changed_bridge | (generated_optional & set(files))
    unexpected = sorted(set(files) - allowed)
    if unexpected:
        raise BuildError("revision PR has unrelated changes:\n" + "\n".join(unexpected))

    subprocess.run(
        [sys.executable, "scripts/build_site_manifest.py", "--check"],
        cwd=REPO_ROOT,
        check=True,
    )
    print(f"existing publication revision: OK {entry_id}")
    print(f"reviewed candidate SHA-256: {reviewed_sha}")
    for path in sorted(changed_bridge):
        print(f"revised bridge asset: OK {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an existing publication revision PR.")
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--registry", default="data/new-document-routes.json")
    args = parser.parse_args()
    validate(args.base_ref, args.registry)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

# 更新履歴
# - 2026-09-02 16:59 JST：theme infrastructure判定を正本helperへ統一し、revision laneのscope外theme追加を正常委譲。
# - 2026-09-02 12:24 JST：publication validator群を同一infra PRで整合させるため、相互に必要なworkflow/scriptだけallowlistへ追加。
# - 2026-09-02 12:20 JST：publication receiptを持つ正式new-document promotion PRを正本final validatorへ委譲。
# - 2026-09-02 10:48 JST：新規文書gate-only PRを正本new-document gate validatorへ委譲。
# - 2026-08-29 00:43 JST：revision recordで対象文書を固定し、reviewed SHA・target byte identity・参照assetだけを検証するvalidatorを追加。
