"""Fail-closed preflight for publishing *source*, not an audit of existing Git history.

This scanner avoids printing matching secret values. It is a defense in depth and
cannot guarantee that all private information or copyrighted material is absent.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ALLOWED_TEXT_SUFFIXES = {'.py', '.pyw', '.ps1', '.bat', '.md', '.txt', '.json',
                         '.yml', '.yaml', '.toml', '.ini', '.html', '.css', '.js',
                         '.spec', '.csv', '.svg', '.xml', '.gitignore', ''}
FORBIDDEN_NAMES = {'.env', 'config.json', 'cookies.txt', 'api_key.txt', 'token.json',
                   'credentials.json', 'library_root.txt', 'id_rsa', 'id_ed25519'}
FORBIDDEN_PARTS = {'.git', '__pycache__', '.pytest_cache', '.venv', 'venv',
                   'runtime_data', 'downloads', 'chatgpt_packages', 'chatgpt_results',
                   'all_transcripts', 'exchange', 'logs', 'dist', 'build'}
FORBIDDEN_EXTENSIONS = {'.db', '.sqlite', '.sqlite3', '.session', '.log', '.pem',
                        '.key', '.p12', '.pfx', '.mp4', '.mkv', '.webm', '.mp3',
                        '.wav', '.m4a', '.zip', '.7z', '.rar', '.zst'}
RESTRICTED_PATTERNS = {
    'private-key-block': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'openai-key': re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b'),
    'github-token': re.compile(r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b'),
    'github-fine-grained-token': re.compile(r'\bgithub_pat_[A-Za-z0-9_]{20,}\b'),
    'google-api-key': re.compile(r'\bAIza[A-Za-z0-9_-]{30,}\b'),
    'bearer-secret': re.compile(r'\bBearer\s+[A-Za-z0-9._~-]{32,}\b', re.I),
    'local-installation': re.compile(r'(?:D:\\YT GUi|E:\\My Installations\\VideoHoarder)', re.I),
    'user-profile-path': re.compile(r'[A-Za-z]:\\(?:Users|Documents and Settings)\\(?!<)[^\\\s]+\\', re.I),
    'unix-home-path': re.compile(r'/(?:home|Users)/(?!(?:username|user|example|runner)/)[A-Za-z0-9_.-]+/', re.I),
}


def audit_tree(root: Path) -> list[dict[str, str]]:
    """Return diagnostic categories and paths only; never return secret content."""
    findings: list[dict[str, str]] = []
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        # A checked-out Git repository necessarily contains .git metadata.
        # The source audit evaluates files that can be committed, not Git's own
        # internal object database/configuration created by checkout.
        if relative.parts and relative.parts[0] == '.git':
            continue
        parts = set(relative.parts)
        # Historical synthetic fixture is permitted; real exchange directories are not.
        is_fixture = relative.parts[:3] == ('tests', 'fixtures', 'chatgpt_integrity')
        if relative.name.lower() in FORBIDDEN_NAMES or relative.name.lower().startswith('.env.'):
            findings.append({'path': str(relative), 'kind': 'private-filename'})
        if (parts & FORBIDDEN_PARTS) and not (is_fixture and parts & {'exchange'}):
            findings.append({'path': str(relative), 'kind': 'runtime-directory'})
        if path.suffix.lower() in FORBIDDEN_EXTENSIONS:
            findings.append({'path': str(relative), 'kind': 'private-or-binary-extension'})
        if path.is_symlink():
            findings.append({'path': str(relative), 'kind': 'symlink-not-allowed'})
            continue
        if path.suffix.lower() not in ALLOWED_TEXT_SUFFIXES:
            continue
        try:
            body = path.read_text(encoding='utf-8')
        except (UnicodeError, OSError):
            continue
        for kind, pattern in RESTRICTED_PATTERNS.items():
            if pattern.search(body):
                findings.append({'path': str(relative), 'kind': kind})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, nargs='?', default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    findings = audit_tree(args.root)
    print(json.dumps({'public_release_audit': 'FAIL' if findings else 'PASS',
                      'finding_count': len(findings), 'findings': findings}, indent=2))
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())