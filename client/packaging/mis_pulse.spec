# -*- mode: python ; coding: utf-8 -*-
# Build with: pyinstaller packaging/mis_pulse.spec  (run from the client/ directory)
import os

from PyInstaller.utils.hooks import collect_all

CLIENT_DIR = os.path.abspath(os.path.join(SPECPATH, ".."))

datas = []
binaries = []
hiddenimports = []

for pkg in ["PySide6", "sqlalchemy", "openpyxl"]:
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

a = Analysis(
    [os.path.join(CLIENT_DIR, "run_app.py")],
    pathex=[CLIENT_DIR],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FCG MIS Pulse",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="FCG MIS Pulse",
)
