import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts.create_code_parent_package import create_code_parent_package, validate_code_parent_zip


def test_code_parent_is_byte_reproducible_for_same_source(tmp_path: Path):
    a=create_code_parent_package(tmp_path/"A", keep_folder=False)["zip_file"]
    b=create_code_parent_package(tmp_path/"B", keep_folder=False)["zip_file"]
    pa,pb=Path(a),Path(b)
    assert hashlib.sha256(pa.read_bytes()).hexdigest() == hashlib.sha256(pb.read_bytes()).hexdigest()
    assert validate_code_parent_zip(pa)["ok"] is True
    assert validate_code_parent_zip(pb)["ok"] is True


def test_handoff_scripts_have_no_required_d_drive_default():
    for name in ["CREATE_CODE_PARENT_PACKAGE.bat","scripts/process_batch_packages.py","scripts/validate_incoming_results.py"]:
        text=Path(name).read_text(encoding="utf-8")
        assert "D:\\YT GUi" not in text


def test_duplicate_prompt_copy_removed():
    assert Path("app/prompts/VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL.md").is_file()
    assert not Path("app/prompts/VIDEO_LIBRARY_MASTER_PROMPT_V3_3_4_FINAL - Copy.txt").exists()


def test_feature_inventory_ids_are_unique():
    import re
    text=Path("docs/implementation/FEATURE_INVENTORY.md").read_text(encoding="utf-8")
    ids=re.findall(r"^\| (F-\d+) \|",text,re.M)
    assert len(ids) == len(set(ids))
