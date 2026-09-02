#!/usr/bin/env python3
"""Prepare, verify, promote, and validate one new content-first document.

ページ作成日時：2026-08-11 15:35 JST
最終更新日時：2026-09-02 16:59 JST
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from build_content_pages import BuildError, parse_front_matter
from build_structured_preview import build_one

REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPO_ROOT / "site"
DEFAULT_REGISTRY = REPO_ROOT / "data" / "new-document-routes.json"
SITE_ROUTE_MANIFEST = REPO_ROOT / "data" / "site-routes.manifest.json"
DEFAULT_CANDIDATE_ROOT = REPO_ROOT / "_new_document_candidate"
RECEIPT_VERSION = "0.1"
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2} JST$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ROUTE_RE = re.compile(r"^/[a-z0-9][a-z0-9/-]*/$")
REQUIRED_METADATA = {
    "id",
    "title",
    "subtitle",
    "description",
    "slug",
    "canonical_url",
    "theme_id",
    "status",
    "page_created_at",
    "last_updated_at",
}
INFRA_ALLOWLIST = {
    ".gitignore",
    ".github/workflows/validate-new-content-publication-lane-v0.yml",
    ".github/workflows/validate-promotion-fixture-04.yml",
    ".github/workflows/validate-publishing-structure.yml",
    "content/fixtures/v2-publication-lane-test.md",
    "content/fixtures/membrane-index-layout-test.md",
    "content/templates/new-document.md",
    "data/new-document-routes.json",
    "data/site-content-salvage.manifest.json",
    "publishing/NEW_DOCUMENT_PUBLICATION.md",
    "publishing/README.md",
    "publishing/fixtures/new-document-index.html",
    "publishing/fixtures/new-document-index.md",
    "publishing/components/membrane-header.html",
    "publishing/components/membrane-index.html",
    "publishing/site.yml",
    "publishing/templates/article.html",
    "publishing/themes/membrane.css",
    "publishing/themes/membrane.yml",
    "scripts/build_site_manifest.py",
    "scripts/build_content_pages.py",
    "scripts/build_structured_preview.py",
    "scripts/capture_structured_preview.js",
    "scripts/new_document_publication.py",
    "scripts/validate_new_document_publication_pr.py",
    "scripts/validate_existing_publication_revision_pr.py",
    "scripts/validate_new_document_visual.js",
    "scripts/validate_structured_preview.py",
    "scripts/validate_site_manifest_routing.py",
}


THEME_INFRA_PREFIXES = (
    "publishing/themes/",
    "publishing/design/",
    "publishing/components/",
)
THEME_INFRA_FILES = {
    "publishing/site.yml",
    "scripts/build_structured_preview.py",
    "data/site-content-salvage.manifest.json",
}


def is_publication_theme_infra(path: str) -> bool:
    return path in THEME_INFRA_FILES or path.startswith(THEME_INFRA_PREFIXES)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repo_path(raw: str, label: str) -> Path:
    value = raw.strip()
    if not value:
        raise BuildError(f"missing path: {label}")
    path = (REPO_ROOT / value).resolve()
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise BuildError(f"path escapes repository: {label}") from exc
    return path


def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise BuildError(f"missing {label}: {path.relative_to(REPO_ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BuildError(f"invalid JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"{label} must be a JSON object")
    return value


def load_registry(path: Path) -> dict[str, dict[str, Any]]:
    data = read_json(path, "new-document route registry")
    if data.get("registry_version") != RECEIPT_VERSION:
        raise BuildError("unsupported new-document registry version")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise BuildError("registry entries must be a list")
    result: dict[str, dict[str, Any]] = {}
    routes: set[str] = set()
    sources: set[str] = set()
    for raw in entries:
        if not isinstance(raw, dict):
            raise BuildError("registry entry must be an object")
        entry_id = str(raw.get("id", "")).strip()
        source = str(raw.get("source", "")).strip()
        route = str(raw.get("route", "")).strip()
        index_source = str(raw.get("index_source", "")).strip()
        index_html = str(raw.get("index_html", "")).strip()
        if not ID_RE.fullmatch(entry_id):
            raise BuildError(f"invalid registry id: {entry_id!r}")
        if entry_id in result or source in sources or route in routes:
            raise BuildError(f"duplicate id, source, or route in registry: {entry_id}")
        if not source.startswith("content/") or not source.endswith(".md"):
            raise BuildError(f"registry source must be a Markdown file under content/: {source}")
        if not ROUTE_RE.fullmatch(route) or "//" in route or any(
            part in {".", ".."} for part in route.split("/")
        ):
            raise BuildError(f"registry route must be an absolute directory route: {route}")
        if not index_html.endswith(".html"):
            raise BuildError(f"registry index_html must be an HTML file: {index_html}")
        if not index_source.endswith(".md"):
            raise BuildError(f"registry index_source must be a Markdown file: {index_source}")
        result[entry_id] = raw
        routes.add(route)
        sources.add(source)
    return result


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.hrefs.append(href)


def validate_index(index_source: Path, index_path: Path, route: str, test_only: bool) -> None:
    if not index_source.is_file():
        raise BuildError(f"index source is missing: {index_source.relative_to(REPO_ROOT)}")
    if not index_path.is_file():
        raise BuildError(f"index HTML is missing: {index_path.relative_to(REPO_ROOT)}")
    if not test_only:
        try:
            index_source.relative_to(REPO_ROOT / "content")
        except ValueError as exc:
            raise BuildError("production index_source must be under content/") from exc
        try:
            index_path.relative_to(SITE_ROOT)
        except ValueError as exc:
            raise BuildError("production index_html must be under site/") from exc
    parser = LinkCollector()
    parser.feed(index_path.read_text(encoding="utf-8"))
    if parser.hrefs.count(route) != 1:
        raise BuildError(f"index HTML must contain exactly one link to {route}")
    markdown_links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", index_source.read_text(encoding="utf-8"))
    if markdown_links.count(route) != 1:
        raise BuildError(f"index source must contain exactly one link to {route}")


def existing_routes() -> set[str]:
    manifest = read_json(SITE_ROUTE_MANIFEST, "site route manifest")
    routes = manifest.get("routes")
    if not isinstance(routes, list):
        raise BuildError("site route manifest routes must be a list")
    return {
        str(entry.get("route"))
        for entry in routes
        if isinstance(entry, dict) and entry.get("route")
    }


def validate_metadata(source: Path, entry: dict[str, Any]) -> dict[str, object]:
    if not source.is_file():
        raise BuildError(f"content source is missing: {source.relative_to(REPO_ROOT)}")
    meta, _ = parse_front_matter(source.read_text(encoding="utf-8"))
    missing = sorted(key for key in REQUIRED_METADATA if not str(meta.get(key, "")).strip())
    if missing:
        raise BuildError("missing required metadata: " + ", ".join(missing))
    entry_id = str(entry["id"])
    route = str(entry["route"])
    if meta["id"] != entry_id:
        raise BuildError("source id does not match registry id")
    if not ID_RE.fullmatch(str(meta["id"])):
        raise BuildError("source id must use lowercase letters, digits, and hyphens")
    if meta["slug"] != route:
        raise BuildError("source slug does not match registry route")
    if meta["canonical_url"] != f"https://genai-ron.jp{route}":
        raise BuildError("canonical_url does not match the registered public route")
    test_only = bool(entry.get("test_only", False))
    expected_status = "preview-only-fixture" if test_only else "publication-candidate"
    if meta["status"] != expected_status:
        raise BuildError(f"status must be {expected_status!r}")
    for key in ("page_created_at", "last_updated_at"):
        if not TIMESTAMP_RE.fullmatch(str(meta[key])):
            raise BuildError(f"{key} must use YYYY-MM-DD HH:MM JST")
    placeholders = ("replace-with", "YYYY-MM-DD", "文書タイトル")
    for key in REQUIRED_METADATA:
        value = str(meta[key])
        if any(token in value for token in placeholders):
            raise BuildError(f"placeholder remains in metadata: {key}")
    return meta


def target_for_route(route: str) -> Path:
    return SITE_ROOT / route.strip("/") / "index.html"


def validate_new_route(entry: dict[str, Any]) -> None:
    route = str(entry["route"])
    target = target_for_route(route)
    if target.exists():
        raise BuildError(f"refusing to overwrite existing site target: {target.relative_to(REPO_ROOT)}")
    if route in existing_routes():
        raise BuildError(f"refusing already registered public route: {route}")


def resolve_entry(entry_id: str, registry_path: Path) -> tuple[dict[str, Any], Path, Path, Path]:
    entries = load_registry(registry_path)
    if entry_id not in entries:
        raise BuildError(f"document id is not registered: {entry_id}")
    entry = entries[entry_id]
    source = repo_path(str(entry["source"]), "registry source")
    try:
        source.relative_to(REPO_ROOT / "content")
    except ValueError as exc:
        raise BuildError("registry source must resolve under content/") from exc
    index_source = repo_path(str(entry["index_source"]), "registry index_source")
    index_path = repo_path(str(entry["index_html"]), "registry index_html")
    validate_metadata(source, entry)
    validate_index(index_source, index_path, str(entry["route"]), bool(entry.get("test_only", False)))
    return entry, source, index_source, index_path


def candidate_for(entry: dict[str, Any], source: Path, candidate_root: Path) -> Path:
    candidate_root = candidate_root.resolve()
    try:
        candidate_root.relative_to(SITE_ROOT)
    except ValueError:
        pass
    else:
        raise BuildError("candidate root must not be inside site/")
    candidate = build_one(source, candidate_root, None)
    expected = candidate_root / str(entry["route"]).strip("/") / "index.html"
    if candidate.resolve() != expected.resolve():
        raise BuildError("builder output does not match the registered route")
    metadata, _ = parse_front_matter(source.read_text(encoding="utf-8"))
    text = candidate.read_text(encoding="utf-8")
    icon_link = '  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">'
    canonical_link = f'  <link rel="canonical" href="{escape(str(metadata["canonical_url"]), quote=True)}">'
    if icon_link not in text:
        raise BuildError("candidate is missing the canonical insertion point")
    text = text.replace(icon_link, canonical_link + "\n" + icon_link, 1)
    provenance_marker = " / Notion原稿作成日時："
    if provenance_marker not in text:
        raise BuildError("candidate is missing the provenance insertion point")
    publication_provenance = (
        f" / ページ作成日時：{escape(str(metadata['page_created_at']))}"
        f" / 最終更新日時：{escape(str(metadata['last_updated_at']))}"
        + provenance_marker
    )
    text = text.replace(provenance_marker, publication_provenance, 1)
    candidate.write_text(text, encoding="utf-8")
    if 'data-theme-production-enabled="true"' not in text:
        raise BuildError("candidate theme is not enabled for production")
    canonical = str(entry["route"])
    if f'<link rel="canonical" href="https://genai-ron.jp{canonical}">' not in text:
        raise BuildError("candidate is missing the registered canonical URL")
    return candidate


def receipt_value(
    entry: dict[str, Any], source: Path, index_source: Path, index_path: Path, registry_path: Path, candidate: Path
) -> dict[str, Any]:
    return {
        "receipt_version": RECEIPT_VERSION,
        "id": entry["id"],
        "source": source.relative_to(REPO_ROOT).as_posix(),
        "source_sha256": sha256(source),
        "route": entry["route"],
        "target": target_for_route(str(entry["route"])).relative_to(REPO_ROOT).as_posix(),
        "index_source": index_source.relative_to(REPO_ROOT).as_posix(),
        "index_source_sha256": sha256(index_source),
        "index_html": index_path.relative_to(REPO_ROOT).as_posix(),
        "index_sha256": sha256(index_path),
        "registry": registry_path.relative_to(REPO_ROOT).as_posix(),
        "registry_sha256": sha256(registry_path),
        "candidate": candidate.relative_to(REPO_ROOT).as_posix(),
        "candidate_sha256": sha256(candidate),
        "test_only": bool(entry.get("test_only", False)),
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare(entry_id: str, registry_path: Path, candidate_root: Path, receipt_path: Path) -> dict[str, Any]:
    entry, source, index_source, index_path = resolve_entry(entry_id, registry_path)
    candidate_relative = candidate_root.resolve().relative_to(REPO_ROOT)
    if not candidate_relative.parts or not candidate_relative.parts[0].startswith("_new_document_"):
        raise BuildError("candidate root must use a repository-local _new_document_* directory")
    if entry.get("test_only"):
        try:
            receipt_path.resolve().relative_to(REPO_ROOT / "_new_document_test_tmp")
        except ValueError as exc:
            raise BuildError("test receipt must be under _new_document_test_tmp/") from exc
        if receipt_path.suffix != ".json":
            raise BuildError("test receipt must be a JSON file")
    else:
        expected_receipt = REPO_ROOT / "publishing" / "releases" / f"{entry_id}.json"
        if receipt_path.resolve() != expected_receipt.resolve():
            raise BuildError(f"receipt path must be {expected_receipt.relative_to(REPO_ROOT)}")
    validate_new_route(entry)
    candidate = candidate_for(entry, source, candidate_root)
    value = receipt_value(entry, source, index_source, index_path, registry_path, candidate)
    write_json(receipt_path, value)
    return value


def validate_receipt(receipt_path: Path, require_candidate: bool = True) -> tuple[dict[str, Any], bytes]:
    receipt = read_json(receipt_path, "publication receipt")
    if receipt.get("receipt_version") != RECEIPT_VERSION:
        raise BuildError("unsupported publication receipt version")
    registry_path = repo_path(str(receipt.get("registry", "")), "receipt registry")
    if sha256(registry_path) != receipt.get("registry_sha256"):
        raise BuildError("registry hash does not match receipt")
    entry_id = str(receipt.get("id", ""))
    entry, source, index_source, index_path = resolve_entry(entry_id, registry_path)
    if receipt.get("source") != source.relative_to(REPO_ROOT).as_posix():
        raise BuildError("receipt source does not match registry")
    if receipt.get("route") != entry["route"]:
        raise BuildError("receipt route does not match registry")
    if receipt.get("target") != target_for_route(str(entry["route"])).relative_to(REPO_ROOT).as_posix():
        raise BuildError("receipt target does not match registry")
    if sha256(source) != receipt.get("source_sha256"):
        raise BuildError("source hash does not match receipt")
    if receipt.get("index_source") != index_source.relative_to(REPO_ROOT).as_posix():
        raise BuildError("receipt index source does not match registry")
    if sha256(index_source) != receipt.get("index_source_sha256"):
        raise BuildError("index source hash does not match receipt")
    if sha256(index_path) != receipt.get("index_sha256"):
        raise BuildError("index hash does not match receipt")
    candidate_path = repo_path(str(receipt.get("candidate", "")), "receipt candidate")
    if require_candidate and not candidate_path.is_file():
        raise BuildError("candidate file is missing")
    with tempfile.TemporaryDirectory(prefix="genai-new-document-") as temp_dir:
        regenerated = candidate_for(entry, source, Path(temp_dir))
        regenerated_bytes = regenerated.read_bytes()
    regenerated_sha = hashlib.sha256(regenerated_bytes).hexdigest()
    if regenerated_sha != receipt.get("candidate_sha256"):
        raise BuildError("regenerated candidate hash does not match receipt")
    if require_candidate and candidate_path.read_bytes() != regenerated_bytes:
        raise BuildError("candidate is not byte-identical to regenerated output")
    return receipt, regenerated_bytes


def promote(receipt_path: Path, expected_sha: str, write_site: bool) -> Path:
    receipt, regenerated = validate_receipt(receipt_path)
    if not write_site:
        raise BuildError("refusing site write without --write-site")
    if receipt.get("test_only"):
        raise BuildError("test fixture cannot be promoted to site/")
    if expected_sha != receipt.get("candidate_sha256"):
        raise BuildError("--expected-sha does not match the reviewed candidate")
    entry, _, _, _ = resolve_entry(str(receipt["id"]), repo_path(str(receipt["registry"]), "receipt registry"))
    validate_new_route(entry)
    target = target_for_route(str(entry["route"]))
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as handle:
        handle.write(regenerated)
    subprocess.run([sys.executable, "scripts/build_site_manifest.py"], cwd=REPO_ROOT, check=True)
    return target


def changed_files(base_ref: str) -> list[str]:
    committed = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    working = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return sorted(
        {
            line
            for output in (committed.stdout, working.stdout, untracked.stdout)
            for line in output.splitlines()
            if line
        }
    )


def path_exists_in_base(base_ref: str, path: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{base_ref}:{path}"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def validate_pr(base_ref: str, registry_path: Path) -> None:
    files = changed_files(base_ref)
    if not files:
        raise BuildError("no changed files detected")
    entries = load_registry(registry_path)
    production = [entry for entry in entries.values() if not entry.get("test_only")]
    targets = [
        target_for_route(str(entry["route"])).relative_to(REPO_ROOT).as_posix()
        for entry in production
    ]
    changed_targets = [target for target in targets if target in files]
    site_changes = [path for path in files if path.startswith("site/")]
    if not changed_targets:
        if site_changes:
            raise BuildError("new-document gate-only change must not modify site/")
        registered_gate_paths = {
            path
            for entry in production
            for path in (str(entry["source"]), str(entry["index_source"]))
        }
        allowed = INFRA_ALLOWLIST | registered_gate_paths
        unexpected = sorted(path for path in files if path not in allowed and not is_publication_theme_infra(path))
        if unexpected:
            raise BuildError(
                "new-document gate-only PR has unrelated changes:\n"
                + "\n".join(unexpected)
            )
        print("new-document publication gate-only change: OK")
        return
    if len(changed_targets) != 1:
        raise BuildError("new-document publication PR must add exactly one public target")
    target = changed_targets[0]
    if path_exists_in_base(base_ref, target):
        raise BuildError("new-document publication cannot overwrite a route present in base")
    entry = next(entry for entry in production if target_for_route(str(entry["route"])).relative_to(REPO_ROOT).as_posix() == target)
    entry_id = str(entry["id"])
    source = str(entry["source"])
    index_source = str(entry["index_source"])
    index_html = str(entry["index_html"])
    receipt_path = f"publishing/releases/{entry_id}.json"
    required = {source, index_source, index_html, receipt_path, target, "data/new-document-routes.json", "data/site-routes.manifest.json", "data/site-content-salvage.manifest.json"}
    missing = sorted(required - set(files))
    if missing:
        raise BuildError("publication PR is missing required changed files:\n" + "\n".join(missing))
    if set(site_changes) != {index_html, target}:
        raise BuildError("publication PR may change only its registered index and target under site/")
    unexpected = sorted(set(files) - required)
    if unexpected:
        raise BuildError("publication PR has unrelated changes:\n" + "\n".join(unexpected))
    receipt, regenerated = validate_receipt(REPO_ROOT / receipt_path, require_candidate=False)
    if receipt.get("target") != target:
        raise BuildError("receipt target does not match changed target")
    if (REPO_ROOT / target).read_bytes() != regenerated:
        raise BuildError("public target is not byte-identical to regenerated candidate")
    current_routes = existing_routes()
    if str(entry["route"]) not in current_routes:
        raise BuildError("published route is missing from site route manifest")
    subprocess.run([sys.executable, "scripts/build_site_manifest.py", "--check"], cwd=REPO_ROOT, check=True)
    print(f"new-document publication target: OK {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Controlled publication for one new GENAI-RON document.")
    sub = parser.add_subparsers(dest="command", required=True)

    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--id", required=True)
    prepare_parser.add_argument("--registry", default=str(DEFAULT_REGISTRY.relative_to(REPO_ROOT)))
    prepare_parser.add_argument("--candidate-root", default=str(DEFAULT_CANDIDATE_ROOT.relative_to(REPO_ROOT)))
    prepare_parser.add_argument("--receipt", required=True)

    verify_parser = sub.add_parser("verify-receipt")
    verify_parser.add_argument("--receipt", required=True)

    promote_parser = sub.add_parser("promote")
    promote_parser.add_argument("--receipt", required=True)
    promote_parser.add_argument("--expected-sha", required=True)
    promote_parser.add_argument("--write-site", action="store_true")

    pr_parser = sub.add_parser("validate-pr")
    pr_parser.add_argument("--base-ref", default="origin/main")
    pr_parser.add_argument("--registry", default=str(DEFAULT_REGISTRY.relative_to(REPO_ROOT)))

    args = parser.parse_args()
    if args.command == "prepare":
        value = prepare(
            args.id,
            repo_path(args.registry, "registry"),
            repo_path(args.candidate_root, "candidate root"),
            repo_path(args.receipt, "receipt"),
        )
        print(json.dumps(value, ensure_ascii=False, indent=2))
    elif args.command == "verify-receipt":
        receipt, _ = validate_receipt(repo_path(args.receipt, "receipt"))
        print(f"publication receipt: OK {receipt['candidate_sha256']}")
    elif args.command == "promote":
        target = promote(repo_path(args.receipt, "receipt"), args.expected_sha, args.write_site)
        print(target.relative_to(REPO_ROOT))
    elif args.command == "validate-pr":
        validate_pr(args.base_ref, repo_path(args.registry, "registry"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

# 更新履歴
# - 2026-09-02 16:59 JST：publication themeのmanifest/design/componentとtheme登録・builder・salvage manifestを共通infraとして認識。
