# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/COLLAB.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/ending.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/fish1.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/fish2.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/fish3.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/fish4.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/fishingboat.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/fishingnet.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/heart.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/level1.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/level9.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/ocean.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/player2.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/trash.png', '.'), ('/Users/sofiaanusasananancuomo/cs10-game-fia-annabelle/whale.png', '.')],
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
    [],
    exclude_binaries=True,
    name='Grey Whale Migration',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Grey Whale Migration',
)
app = BUNDLE(
    coll,
    name='Grey Whale Migration.app',
    icon=None,
    bundle_identifier=None,
)
