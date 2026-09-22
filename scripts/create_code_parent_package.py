"""Create a clean, reproducible VideoHoarder source-code handoff ZIP.

The package is intentionally source-focused. Runtime data, generated builds,
browser profiles, caches, databases, logs, and live machine/user configuration
are excluded. Governance evidence under ``docs/implementation`` is included as
persistent project memory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.public_release_audit import audit_tree
except ModuleNotFoundError:  # direct execution: python scripts/create_code_parent_package.py
    from public_release_audit import audit_tree


SOURCE_ROOT = Path(__file__).resolve().parents[1]
LIVE_PARENT = SOURCE_ROOT.parent
INSTALL_ROOT = LIVE_PARENT.parent if LIVE_PARENT.name == "VideoHoarder_App" else LIVE_PARENT
DEFAULT_OUTPUT = INSTALL_ROOT / "VideoHoarder_Code_Parent"
ARCHIVE_ROOT_NAME = "VideoHoarder_Code_Parent"

SOURCE_ITEMS = [
    ".gitignore",
    ".github",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "GOVERNANCE.md",
    "MAINTAINERS.md",
    "SUPPORT.md",
    "TESTING.md",
    "RELEASING.md",
    "ROADMAP.md",
    "OSS_PROJECT_OVERVIEW.md",
    "pytest.ini",
    "BUILD_AND_DEPLOY.bat",
    "BUILD_DEV_LAUNCHER.bat",
    "BUILD_DEV_LAUNCHER.ps1",
    "BUILD_SMALL_EXE.bat",
    "BUILD_SMALL_EXE.ps1",
    "BUILD_WINDOWS.ps1",
    "CREATE_CODE_PARENT_PACKAGE.bat",
    "DESKTOP_README.md",
    "INSTALL_GUI.ps1",
    "PREPARE_PORTABLE_BUILD.ps1",
    "V3_3_4_VTT_COVERAGE_CHANGE_SUMMARY.md",
    "VideoHoarder.spec",
    "VideoHoarder_launcher.spec",
    "VideoHoarder_onedir.spec",
    "requirements-build.txt",
    "requirements.txt",
    "run_gui.pyw",
    "app",
    "assets",
    "build_support",
    "docs",
    "scripts",
    "specs",
    "tests",
    "PROJECT_KNOWLEDGE",
]

# Names are excluded recursively from copied source trees.
EXCLUDE_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "runtime_data",
    "validation_tmp",
    "build",
    "dist",
    "logs",
    "exchange",
    "chatgpt_packages",
    "chatgpt_results",
    "all_transcripts",
    "evidence",  # archived real-video evidence in specs; keep synthetic fixtures
}

# ``data`` is normally runtime/user data, but this repository also keeps a
# small, deterministic integrity fixture below tests/fixtures.  Filter by
# path rather than by directory name so that fixture remains part of a
# replacement package.
EXCLUDED_RUNTIME_DIR_NAMES = {"data"}
ALLOWED_TEST_DATA_PREFIX = Path("tests") / "fixtures" / "chatgpt_integrity" / "data"

EXCLUDE_FROM_SOURCE_ITEMS = {
    "dist",
    "tools",
    "library_root.txt",
    "app/config.json",
}

EXCLUDE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".tmp",
    ".temp",
    ".bak",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".log",
    ".session",
    ".session-journal",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}

# Fields that can contain credentials or machine/user-specific paths. The
# handoff template keeps the schema but never copies these live values.
SANITIZED_CONFIG_OVERRIDES: dict[str, Any] = {
    "browser_for_cookies": "",
    "cookies_file": "",
    "cookies_mode": "none",
    "youtube_api_key_file": "",
    "youtube_data_api_key": "",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ignore_names(_directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    directory = Path(_directory).resolve()
    try:
        relative_directory = directory.relative_to(SOURCE_ROOT.resolve())
    except ValueError:
        relative_directory = Path()
    for name in names:
        candidate = Path(name)
        candidate_relative = relative_directory / candidate
        is_allowed_fixture_data = (
            candidate_relative == ALLOWED_TEST_DATA_PREFIX
            or ALLOWED_TEST_DATA_PREFIX in candidate_relative.parents
        )
        is_private_file = (name.lower() in {"config.json", "cookies.txt", "credentials.json", "token.json", "api_key.txt", "library_root.txt"}
                           or name.lower() == ".env" or name.lower().startswith(".env."))
        if (name in EXCLUDE_NAMES and not (name == "exchange" and is_allowed_fixture_data)) or (name in EXCLUDED_RUNTIME_DIR_NAMES and not is_allowed_fixture_data) or is_private_file:
            ignored.add(name)
        elif candidate.suffix.lower() in EXCLUDE_SUFFIXES:
            ignored.add(name)
    return ignored


def copy_item(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    if source.is_dir():
        shutil.copytree(source, destination, ignore=ignore_names, dirs_exist_ok=True)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def _write_sanitized_templates(packaged_source: Path) -> list[str]:
    """Create a portable full-schema example without copying live values."""

    written: list[str] = []
    # config.default.json is the authoritative schema and exists in a pristine
    # Code Parent. Never depend on a live config.json being created first.
    candidates = [
        SOURCE_ROOT / "app" / "config.default.json",
        SOURCE_ROOT / "app" / "config.example.json",
    ]
    data: dict[str, Any] = {}
    for config_source in candidates:
        if not config_source.exists():
            continue
        try:
            raw = json.loads(config_source.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                data = dict(raw)
                break
        except Exception:
            continue
    data.update(SANITIZED_CONFIG_OVERRIDES)
    config_target = packaged_source / "app" / "config.example.json"
    config_target.parent.mkdir(parents=True, exist_ok=True)
    config_target.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    written.append(str(config_target.relative_to(packaged_source.parent)))

    library_template = packaged_source / "library_root.example.txt"
    library_template.write_text(
        "# Set this only in your local installation if you need an explicit library root.\n"
        "# Example: <install-root>\\Library\n",
        encoding="utf-8",
    )
    written.append(str(library_template.relative_to(packaged_source.parent)))

    # Defensive cleanup in case a copied subtree gained one of these files.
    for live_path in (packaged_source / "app" / "config.json", packaged_source / "library_root.txt"):
        try:
            live_path.unlink()
        except FileNotFoundError:
            pass
    return written


def _stage_files(package_root: Path) -> list[Path]:
    return sorted(path for path in package_root.rglob("*") if path.is_file())


def _relative_archive_files(package_root: Path) -> list[str]:
    return [path.relative_to(package_root).as_posix() for path in _stage_files(package_root)]


def _source_snapshot_epoch() -> int:
    raw = str(os.environ.get("SOURCE_DATE_EPOCH") or "").strip()
    if raw:
        try:
            return max(315532800, int(raw))
        except ValueError:
            pass
    # A fixed epoch keeps package bytes deterministic even when excluded
    # runtime files have different mtimes between machines.
    return 315532800


def _snapshot_iso(epoch: int) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(timespec="seconds")


def _build_manifest(package_root: Path, copied_items: list[str], skipped: list[str], templates: list[str]) -> dict[str, Any]:
    manifest_path = package_root / "CODE_PARENT_MANIFEST.json"
    files = [p for p in _stage_files(package_root) if p != manifest_path]
    hashes = {p.relative_to(package_root).as_posix(): _sha256_file(p) for p in files}
    archive_files = sorted([*hashes, "CODE_PARENT_MANIFEST.json"])
    return {
        "manifest_version": 2,
        "created_at_utc": _snapshot_iso(_source_snapshot_epoch()),
        "timestamp_semantics": "deterministic source snapshot time; override with SOURCE_DATE_EPOCH",
        "layout": {"source": "Source"},
        "policy": {
            "included_source_items": list(SOURCE_ITEMS),
            "excluded_source_items": sorted(EXCLUDE_FROM_SOURCE_ITEMS),
            "excluded_names": sorted(EXCLUDE_NAMES),
            "excluded_suffixes": sorted(EXCLUDE_SUFFIXES),
            "live_configuration_included": False,
        },
        "copied_source_items": copied_items,
        "skipped_missing": skipped,
        "generated_templates": templates,
        "archive_files": archive_files,
        "content_sha256": hashes,
        "notes": [
            "CODE_PARENT_MANIFEST.json intentionally has no self-hash.",
            "All other archive files are covered by content_sha256.",
        ],
    }


def _write_manifest(package_root: Path, manifest: dict[str, Any]) -> None:
    (package_root / "CODE_PARENT_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def create_zip_from_folder(folder: Path, zip_path: Path | None = None) -> Path:
    """Create a byte-reproducible ZIP for unchanged source content."""
    zip_path = zip_path or folder.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    epoch=_source_snapshot_epoch()
    stamp=time.gmtime(epoch)[:6]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for item in _stage_files(folder):
            rel=Path(ARCHIVE_ROOT_NAME)/item.relative_to(folder)
            info=zipfile.ZipInfo(rel.as_posix(), date_time=stamp)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o644 & 0xFFFF) << 16
            info.create_system=3
            zf.writestr(info,item.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return zip_path


def validate_code_parent_zip(zip_path: Path) -> dict[str, Any]:
    """Validate archive contents and hashes against its embedded manifest."""

    with zipfile.ZipFile(zip_path, "r") as zf:
        file_names = sorted(name for name in zf.namelist() if not name.endswith("/"))
        roots = {name.split("/", 1)[0] for name in file_names}
        if len(roots) != 1:
            raise ValueError(f"Expected one archive root, found: {sorted(roots)}")
        root = next(iter(roots))
        manifest_name = f"{root}/CODE_PARENT_MANIFEST.json"
        if manifest_name not in file_names:
            raise ValueError("CODE_PARENT_MANIFEST.json is missing from archive")
        manifest = json.loads(zf.read(manifest_name).decode("utf-8"))
        relative_files = sorted(name[len(root) + 1 :] for name in file_names)
        expected = sorted(str(x) for x in manifest.get("archive_files") or [])
        if relative_files != expected:
            missing = sorted(set(expected) - set(relative_files))
            extra = sorted(set(relative_files) - set(expected))
            raise ValueError(f"Manifest/archive mismatch; missing={missing}, extra={extra}")
        hashes = manifest.get("content_sha256") or {}
        for rel, expected_hash in hashes.items():
            name = f"{root}/{rel}"
            if name not in file_names:
                raise ValueError(f"Hashed file missing from archive: {rel}")
            actual_hash = _sha256_bytes(zf.read(name))
            if actual_hash != expected_hash:
                raise ValueError(f"Hash mismatch for {rel}")
        forbidden_parts = set(EXCLUDE_NAMES) | EXCLUDED_RUNTIME_DIR_NAMES
        for rel in relative_files:
            parts = set(Path(rel).parts)
            rel_path = Path(rel)
            allowed_fixture = (
                ALLOWED_TEST_DATA_PREFIX in rel_path.parents
                or (Path("Source") / ALLOWED_TEST_DATA_PREFIX) in rel_path.parents
            )
            if (parts & forbidden_parts) and not allowed_fixture:
                raise ValueError(f"Forbidden runtime/cache path in archive: {rel}")
            if Path(rel).suffix.lower() in EXCLUDE_SUFFIXES:
                raise ValueError(f"Forbidden runtime suffix in archive: {rel}")
        forbidden_exact = {"Source/app/config.json", "Source/library_root.txt"}
        found = forbidden_exact & set(relative_files)
        if found:
            raise ValueError(f"Live configuration present in archive: {sorted(found)}")
        required = {
            "Source/README.md",
            "Source/LICENSE",
            "Source/CONTRIBUTING.md",
            "Source/SECURITY.md",
            "Source/.github/workflows/ci.yml",
            "Source/.github/workflows/codeql.yml",
            "Source/docs/implementation/FEATURE_INVENTORY.md",
            "Source/docs/OPENAI_API_INTEGRATION.md",
            "Source/docs/PUBLIC_RELEASE_CHECKLIST.md",
            "Source/scripts/public_release_audit.py",
            "Source/app/config.example.json",
            "Source/library_root.example.txt",
        }
        absent = required - set(relative_files)
        if absent:
            raise ValueError(f"Required handoff files are missing: {sorted(absent)}")
        # The sanitized example must preserve the full authoritative schema even
        # when packaging directly from a pristine handoff with no config.json.
        default_cfg = json.loads(zf.read(f"{root}/Source/app/config.default.json").decode("utf-8"))
        example_cfg = json.loads(zf.read(f"{root}/Source/app/config.example.json").decode("utf-8"))
        if set(example_cfg) != set(default_cfg):
            missing_keys = sorted(set(default_cfg) - set(example_cfg))
            extra_keys = sorted(set(example_cfg) - set(default_cfg))
            raise ValueError(f"config.example schema mismatch; missing={missing_keys}, extra={extra_keys}")
        return {
            "ok": True,
            "root": root,
            "file_count": len(relative_files),
            "hashed_file_count": len(hashes),
            "manifest_version": manifest.get("manifest_version"),
        }


def create_code_parent_package(output: Path = DEFAULT_OUTPUT, clean: bool = True, keep_folder: bool = False) -> dict[str, Any]:
    output = output.resolve()
    zip_path = output.with_suffix(".zip")
    if clean and output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    packaged_source = output / "Source"
    packaged_source.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    skipped: list[str] = []
    for item in SOURCE_ITEMS:
        src = SOURCE_ROOT / item
        dst = packaged_source / item
        if src.exists():
            copy_item(src, dst)
            copied.append(item)
        else:
            skipped.append(item)

    templates = _write_sanitized_templates(packaged_source)
    privacy_findings = audit_tree(packaged_source)
    if privacy_findings:
        # The audit returns only paths/categories, never secret values. Fail closed.
        raise ValueError(f"Public release audit failed: {privacy_findings}")

    readme = output / "README_VIDEOHOARDER_CODE_PARENT.txt"
    readme.write_text(
        "\n".join(
            [
                "VideoHoarder code parent folder",
                "",
                "Layout:",
                "  Source\\ = clean source-code tree for review or replacement",
                "",
                "Included deliberately:",
                "  docs\\implementation governance/project-memory evidence",
                "",
                "Excluded deliberately:",
                "  dist/build/log/cache/runtime databases/browser profile/user data",
                "  live app\\config.json and library_root.txt",
                "",
                "Portable templates:",
                "  Source\\app\\config.example.json",
                "  Source\\library_root.example.txt",
                "",
                "The archive is validated against CODE_PARENT_MANIFEST.json before success is returned.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    manifest = _build_manifest(output, copied, skipped, templates)
    _write_manifest(output, manifest)
    zip_path = create_zip_from_folder(output, zip_path)
    validation = validate_code_parent_zip(zip_path)

    result = dict(manifest)
    result["zip_file"] = str(zip_path)
    result["validation"] = validation
    if not keep_folder:
        shutil.rmtree(output, ignore_errors=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Parent folder to create. Default: install-root/VideoHoarder_Code_Parent",
    )
    parser.add_argument("--no-clean", action="store_true", help="Do not delete the previous output folder first.")
    parser.add_argument(
        "--keep-folder",
        action="store_true",
        help="Keep the staging folder after creating the ZIP. Default: delete it and leave only the ZIP.",
    )
    args = parser.parse_args()
    result = create_code_parent_package(Path(args.output), clean=not args.no_clean, keep_folder=args.keep_folder)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
