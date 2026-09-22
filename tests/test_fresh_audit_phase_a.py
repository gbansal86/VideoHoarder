from pathlib import Path

from app.file_safety import files_equal, windows_safe_component


def test_equal_size_different_content_is_not_duplicate(tmp_path: Path):
    left = tmp_path / "left.bin"
    right = tmp_path / "right.bin"
    left.write_bytes(b"AAAA")
    right.write_bytes(b"BBBB")
    assert left.stat().st_size == right.stat().st_size
    assert files_equal(left, right) is False


def test_identical_content_is_duplicate(tmp_path: Path):
    left = tmp_path / "left.bin"
    right = tmp_path / "right.bin"
    left.write_bytes(b"same")
    right.write_bytes(b"same")
    assert files_equal(left, right) is True


def test_windows_reserved_names_are_escaped():
    for name in ["CON", "AUX", "NUL", "PRN", "COM1", "LPT9", "CON.txt", "aux.JSON"]:
        assert windows_safe_component(name).startswith("_")
    assert windows_safe_component("normal title") == "normal title"


def test_installed_writable_state_is_based_on_base_source_contract():
    text = Path("app/app.py").read_text(encoding="utf-8")
    assert 'URLS = Path(os.environ.get("VLM_URLS_FILE") or (BASE / "urls.txt"))' in text
    assert 'token_file=BASE/"data"/"credentials"/"youtube_subscriptions_token.json"' in text
    assert 'token_file=CODE_ROOT/"data"/"credentials"' not in text
