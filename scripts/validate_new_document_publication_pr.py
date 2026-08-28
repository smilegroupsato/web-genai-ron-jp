#!/usr/bin/env python3
"""Validate the final PR produced by the two-stage new-document publication lane.

ページ作成日時：2026-08-28 17:12 JST
最終更新日時：2026-08-29 00:48 JST

The gate-only stage may register source/route/index before publication. Therefore
source, registry, and index files do not need to change again in the final
promotion PR; their exact bytes are already pinned by the publication receipt.
Referenced /publishing/** assets are allowed only when required by the promoted
page and byte-identical to their source-of-truth files under publishing/.

Final promotion validation intentionally evaluates only committed diff against
base_ref. Ephemeral QA worktree files such as node_modules/ or the preview assets
symlink are not part of the publication PR and must not affect this validator.

Existing-publication revision PRs are delegated to
validate_existing_publication_revision_pr.py when they contain exactly one
publishing/revisions/*.json record. The dedicated revision workflow is required
to validate those PRs.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from build_content_pages import BuildError
from new_document_publication import (
    REPO_ROOT,
    existing_routes,
    load_registry,
    path_exists_in_base,
    repo_path,
    target_for_route,
    validate_receipt,
)
from sync_publication_assets import required_assets, validate as validate_publication_assets

AUTOMATION_INFRA_ALLOWLIST = {
    ".github/workflows/new-document-publication-automation.yml",
    "publishing/NEW_DOCUMENT_PUBLICATION.md",
    "publishing/themes/membrane.yml",
    "publishing/themes/membrane-mobile-reading-v0.1.css",
    "scripts/sync_publication_assets.py",
    "scripts/validate_new_document_publication_pr.py",
}


def committed_changed_files(base_ref: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return sorted({line for line in result.stdout.splitlines() if line})


def validate(base_ref: str, registry_raw: str) -> None:
    registry_path = repo_path(registry_raw, "registry")
    files = committed_changed_files(base_ref)
    if not files:
        raise BuildError("no changed files detected")

    revision_records = [
        path
        for path in files
        if path.startswith("publishing/revisions/") and path.endswith(".json")
    ]
    if revision_records:
        if len(revision_records) != 1:
            raise BuildError("revision PR must contain exactly one revision record")
        print(
            "existing-publication revision detected; "
            "delegated to validate_existing_publication_revision_pr.py"
        )
        print(f"revision record: {revision_records[0]}")
        return

    entries = load_registry(registry_path)
    production = [entry for entry in entries.values() if not entry.get("test_only")]
    by_target = {
        target_for_route(str(entry["route"])).relative_to(REPO_ROOT).as_posix(): entry
        for entry in production
    }
    changed_targets = [target for target in by_target if target in files]

    if not changed_targets:
        unexpected = sorted(set(files) - AUTOMATION_INFRA_ALLOWLIST)
        if unexpected:
            raise BuildError(
                "publication automation PR has no public target and contains unrelated changes:\n"
                + "\n".join(unexpected)
            )
        print("new-document publication automation infra change: OK")
        return

    if len(changed_targets) != 1:
        raise BuildError("publication PR must add exactly one registered public target")

    target = changed_targets[0]
    if path_exists_in_base(base_ref, target):
        raise BuildError("publication PR cannot overwrite a route present in base")

    entry = by_target[target]
    entry_id = str(entry["id"])
    receipt_path = f"publishing/releases/{entry_id}.json"
    required_changed = {
        receipt_path,
        target,
        "data/site-routes.manifest.json",
        "data/site-content-salvage.manifest.json",
    }
    missing = sorted(required_changed - set(files))
    if missing:
        raise BuildError(
            "publication PR is missing required generated changes:\n" + "\n".join(missing)
        )

    receipt, regenerated = validate_receipt(REPO_ROOT / receipt_path, require_candidate=False)
    if receipt.get("target") != target:
        raise BuildError("receipt target does not match changed target")
    target_path = REPO_ROOT / target
    if target_path.read_bytes() != regenerated:
        raise BuildError("public target is not byte-identical to regenerated candidate")

    required_bridge = {
        f"site/publishing/{relative.as_posix()}" for relative in required_assets(target_path)
    }
    changed_bridge = {path for path in files if path.startswith("site/publishing/")}
    missing_bridge = sorted(required_bridge - changed_bridge)
    extra_bridge = sorted(changed_bridge - required_bridge)
    if missing_bridge:
        raise BuildError(
            "publication PR is missing required publishing bridge assets:\n"
            + "\n".join(missing_bridge)
        )
    if extra_bridge:
        raise BuildError(
            "publication PR contains unreferenced publishing bridge assets:\n"
            + "\n".join(extra_bridge)
        )
    validate_publication_assets(target_path)

    site_changes = {path for path in files if path.startswith("site/")}
    allowed_site_changes = {target} | required_bridge
    if site_changes != allowed_site_changes:
        raise BuildError(
            "publication PR site/ changes do not match target + required bridge assets:\n"
            + "\n".join(sorted(site_changes))
        )

    allowed_changed = required_changed | required_bridge
    unexpected = sorted(set(files) - allowed_changed)
    if unexpected:
        raise BuildError(
            "publication PR has unrelated changes:\n" + "\n".join(unexpected)
        )

    if str(entry["route"]) not in existing_routes():
        raise BuildError("published route is missing from site route manifest")

    subprocess.run(
        [sys.executable, "scripts/build_site_manifest.py", "--check"],
        cwd=REPO_ROOT,
        check=True,
    )
    print(f"two-stage new-document publication target: OK {target}")
    for path in sorted(required_bridge):
        print(f"publication bridge asset: OK {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate two-stage new-document publication PR.")
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
# - 2026-08-29 00:48 JST：revision recordを持つ既存公開物PRを専用revision validatorへ委譲。
# - 2026-08-29 00:16 JST：final promotion validatorをcommitted diff限定にし、QA用未追跡worktree fileを判定対象外化。
# - 2026-08-28 18:22 JST：promoted HTML/CSSが参照するpublishing bridge assetだけを許可し、原本とのbyte identityを検証。
# - 2026-08-28 17:12 JST：gate-only登録済みsource/index/registryをreceipt hashで固定する二段階PR検証を追加。
