# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path(SPECPATH).resolve()
icon_path = project_root / "assets" / "app_icon.ico"
version_path = project_root / "build_support" / "version_info.txt"

datas = [
    (str(project_root / "app" / "config.json"), "app"),
    (str(project_root / "app" / "VERSION.txt"), "app"),
    (str(project_root / "assets" / "app_icon.svg"), "assets"),
]

a = Analysis(
    [str(project_root / "run_gui.pyw")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=["app.app"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "pytest"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    exclude_binaries=False,
    name="VideoHoarder",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
    version=str(version_path),
)
