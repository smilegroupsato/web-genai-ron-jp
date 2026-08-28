#!/usr/bin/env python3
"""Validate the final PR produced by the two-stage new-document publication lane.

ページ作成日時：2026-08-28 17:12 JST
最終更新日時：2026-08-28 17:12 JST

The gate-only stage may register source/route/index before publication. Therefore
source, registry, and index files do not need to change again in the final
promotion PR; their exact bytes are already pinned by the publication receipt.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from build_content_pages import BuildError
from new_document_publication import (
    REPO_ROOT,
    changed_files,
    existing_routes,
    load_registry,
    path_exists_in_base,
    repo_path,
    target_for_route,
    validate_receipt,
)

AUTOMATION_INFRA_ALLOWLIST = {
    ".github/workflows/new-document-publication-automation.yml",
    "publishing/NEW_DOCUMENT_PUBLICATION.md",
    "scripts/validate_new_document_publication_pr.py",
}


def validate(base_ref: str, registry_raw: str) -> None:
    registry_path = repo_path(registry_raw, "registry")
    files = changed_files(base_ref)
    if not files:
        raise BuildError("no changed files detected")

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

    site_changes = sorted(path for path in files if path.startswith("site/"))
    if site_changes != [target]:
        raise BuildError(
            "publication PR may add only its registered target under site/:\n"
            + "\n".join(site_changes)
        )

    unexpected = sorted(set(files) - required_changed)
    if unexpected:
        raise BuildError(
            "publication PR has unrelated changes:\n" + "\n".join(unexpected)
        )

    receipt, regenerated = validate_receipt(REPO_ROOT / receipt_path, require_candidate=False)
    if receipt.get("target") != target:
        raise BuildError("receipt target does not match changed target")
    if (REPO_ROOT / target).read_bytes() != regenerated:
        raise BuildError("public target is not byte-identical to regenerated candidate")
    if str(entry["route"]) not in existing_routes():
        raise BuildError("published route is missing from site route manifest")

    import subprocess

    subprocess.run(
        [sys.executable, "scripts/build_site_manifest.py", "--check"],
        cwd=REPO_ROOT,
        check=True,
    )
    print(f"two-stage new-document publication target: OK {target}")


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
    except (BuildError, OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

# 更新履歴
# - 2026-08-28 17:12 JST：gate-only登録済みsource/index/registryをreceipt hashで固定する二段階PR検証を追加。
