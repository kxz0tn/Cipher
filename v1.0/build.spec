# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Cipher v1.0 — onefile, windowed."""

from pathlib import Path

block_cipher = None

_ASSET_DIR = Path('cipher') / 'assets'
_asset_datas = []
if _ASSET_DIR.is_dir():
    _asset_datas.append((str(_ASSET_DIR), 'cipher/assets'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=_asset_datas,
    hiddenimports=['numpy', 'pygame', 'pygame._sdl2'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

_icon = 'cipher.ico' if Path('cipher.ico').is_file() else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Cipher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)
