# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['desktop_timer.py'],
    pathex=[],
    binaries=[],
    datas=[('lang', 'lang'), ('sounds', 'sounds'), ('img', 'img'), ('settings', 'settings')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DesktopTimer',
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
    icon=r"C:\\Users\\Tika\\Desktop\\学校\\PersonalProject\\DesktopTimer\\img\\timer_icon.ico",
)
