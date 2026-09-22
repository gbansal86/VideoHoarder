"""Defensive public release audit of the staged GitHub source tree."""
from pathlib import Path

from scripts.public_release_audit import audit_tree


def test_audit_accepts_a_minimal_public_source(tmp_path: Path):
    (tmp_path / 'README.md').write_text('Set OPENAI_API_KEY in your own environment.\n', encoding='utf-8')
    (tmp_path / 'config.default.json').write_text('{"openai_api_enabled": false}', encoding='utf-8')
    assert audit_tree(tmp_path) == []


def test_audit_rejects_realistic_private_files_and_a_key(tmp_path: Path):
    (tmp_path / '.env').write_text('not-a-real-secret', encoding='utf-8')
    (tmp_path / 'api_key.txt').write_text('not-a-real-secret', encoding='utf-8')
    (tmp_path / 'notes.md').write_text('sk-' + 'Z'*32, encoding='utf-8')
    (tmp_path / 'library.db').write_bytes(b'SQLite format 3')
    findings = audit_tree(tmp_path)
    assert any(x['kind'] == 'openai-key' for x in findings)
    assert sum(x['kind'] == 'private-filename' for x in findings) >= 2
    assert any(x['kind'] == 'private-or-binary-extension' for x in findings)
    assert not any('Z'*20 in str(x) for x in findings)


def test_audit_rejects_machine_paths(tmp_path: Path):
    (tmp_path / 'docs.md').write_text('Local installation: D:\\YT GUi\\Source', encoding='utf-8')
    assert any(x['kind'] == 'local-installation' for x in audit_tree(tmp_path))
