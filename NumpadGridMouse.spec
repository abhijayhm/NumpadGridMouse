# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Numpad Grid Mouse

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'win32timezone',
        'pynput.keyboard',
        'pynput.mouse',
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        'keyboard',
        'pyautogui',
        'win32gui',
        'win32con',
        'win32api',
        'win32com',
        'pythoncom',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.font',
        'status_window',
    ],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NumpadGridMouse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (set to True for debugging)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)
