from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path

from scripts.create_code_parent_package import create_code_parent_package, validate_code_parent_zip


def _archive_relative_names(zip_path: Path) -> tuple[str, set[str]]:
    with zipfile.ZipFile(zip_path) as zf:
        names = {name for name in zf.namelist() if not name.endswith('/')}
    root = sorted(names)[0].split('/', 1)[0]
    return root, {name[len(root) + 1 :] for name in names}


def test_code_parent_contains_governance_and_sanitized_templates() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / 'VideoHoarder_Code_Parent'
        result = create_code_parent_package(output, keep_folder=True)
        zip_path = Path(result['zip_file'])
        root, names = _archive_relative_names(zip_path)
        assert root == 'VideoHoarder_Code_Parent'
        assert 'Source/docs/implementation/FEATURE_INVENTORY.md' in names
        assert 'Source/docs/PUBLIC_RELEASE_CHECKLIST.md' in names
        assert 'Source/scripts/public_release_audit.py' in names
        assert not any(name.startswith('Source/specs/evidence/') for name in names)
        assert 'Source/app/config.example.json' in names
        assert 'Source/library_root.example.txt' in names
        assert 'Source/BUILD_WINDOWS.ps1' in names
        assert 'Source/BUILD_DEV_LAUNCHER.ps1' in names
        assert 'Source/BUILD_DEV_LAUNCHER.bat' in names
        assert 'Source/CREATE_CODE_PARENT_PACKAGE.bat' in names
        assert 'Source/VideoHoarder.spec' in names
        assert 'Source/VideoHoarder_launcher.spec' in names
        assert 'Source/app/config.json' not in names
        assert 'Source/library_root.txt' not in names
        assert 'Source/tests/fixtures/chatgpt_integrity/data/chatgpt/exchange/outgoing/pkg/evidence.json' in names
        assert not any('/data/' in f'/{name}/' and not name.startswith('Source/tests/fixtures/chatgpt_integrity/data/') for name in names)
        assert not any('/dist/' in f'/{name}/' for name in names)
        assert not any('/logs/' in f'/{name}/' for name in names)
        assert not any('/runtime_data/' in f'/{name}/' for name in names)
        assert not any('/__pycache__/' in f'/{name}/' for name in names)


def test_code_parent_manifest_matches_archive_and_hashes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / 'VideoHoarder_Code_Parent'
        result = create_code_parent_package(output, keep_folder=False)
        check = validate_code_parent_zip(Path(result['zip_file']))
        assert check['ok'] is True
        assert check['file_count'] == check['hashed_file_count'] + 1


def test_sanitized_config_contains_no_live_cookie_or_key_paths() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / 'VideoHoarder_Code_Parent'
        result = create_code_parent_package(output, keep_folder=False)
        zip_path = Path(result['zip_file'])
        with zipfile.ZipFile(zip_path) as zf:
            root = zf.namelist()[0].split('/', 1)[0]
            cfg = json.loads(zf.read(f'{root}/Source/app/config.example.json').decode('utf-8'))
        assert cfg.get('youtube_data_api_key') == ''
        assert cfg.get('youtube_api_key_file') == ''
        assert cfg.get('cookies_file') == ''
        assert cfg.get('browser_for_cookies') == ''
        assert cfg.get('cookies_mode') == 'none'


def test_code_parent_repeated_generation_has_same_approved_file_set_and_content_hashes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        first = create_code_parent_package(base / 'VideoHoarder_Code_Parent_A', keep_folder=False)
        second = create_code_parent_package(base / 'VideoHoarder_Code_Parent_B', keep_folder=False)
        assert first['archive_files'] == second['archive_files']
        assert first['content_sha256'] == second['content_sha256']
