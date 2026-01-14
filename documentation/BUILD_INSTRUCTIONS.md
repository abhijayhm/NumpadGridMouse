# Building Numpad Grid Mouse Executable

This guide explains how to build a standalone Windows executable from the Python source code.

## Prerequisites

1. **Python 3.8+** installed
2. **All dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```
3. **PyInstaller** installed:
   ```bash
   pip install pyinstaller
   ```

## Quick Build

### Method 1: Automated Build Script (Easiest)

Simply run:
```bash
build_exe.bat
```

This will:
- Check if PyInstaller is installed
- Install it if missing
- Build the executable
- Place it in the `dist` folder

### Method 2: Using Spec File

```bash
pyinstaller NumpadGridMouse.spec
```

### Method 3: Direct Command

```bash
pyinstaller --onefile --windowed --name "NumpadGridMouse" --hidden-import win32timezone --hidden-import pynput.keyboard --hidden-import pynput.mouse --hidden-import keyboard --collect-all keyboard --collect-all pynput main.py
```

## Output

After building, you'll find:
- **Executable**: `dist\NumpadGridMouse.exe`
- **Build files**: `build\` folder (can be deleted)
- **Spec file**: `NumpadGridMouse.spec` (configuration file)

## Executable Size

The executable will be approximately **15-25 MB** due to:
- Python runtime bundled inside
- All required libraries (pynput, keyboard, pyautogui, win32, etc.)
- Tkinter GUI components

## Running the Executable

### Important: Administrator Privileges Required

The executable **must** be run as Administrator to register global hotkeys:

1. **Right-click** `NumpadGridMouse.exe`
2. Select **"Run as Administrator"**

### Creating a Shortcut with Admin Rights

1. Create a shortcut to the executable
2. Right-click the shortcut → **Properties**
3. Click **"Advanced"**
4. Check **"Run as Administrator"**
5. Click OK

Now you can double-click the shortcut to run with admin rights.

## Troubleshooting Build Issues

### "Module not found" errors

If PyInstaller can't find certain modules, add them to `hiddenimports` in the spec file:

```python
hiddenimports=[
    'module_name',
    # ... existing imports
],
```

### Large executable size

This is normal. PyInstaller bundles the entire Python runtime. To reduce size:
- Use `--exclude-module` to exclude unused modules
- Consider using `--onedir` instead of `--onefile` (creates a folder with multiple files)

### Executable doesn't work

1. **Test in console mode first**: Edit `NumpadGridMouse.spec` and set `console=True` to see error messages
2. **Check dependencies**: Ensure all required DLLs are included
3. **Test on clean system**: The executable should work on Windows 10/11 without Python installed

### Antivirus warnings

Some antivirus software may flag PyInstaller executables as suspicious. This is a false positive. You can:
- Add an exception in your antivirus
- Sign the executable with a code signing certificate (for distribution)

## Advanced Configuration

### Custom Icon

1. Create or obtain an `.ico` file
2. Edit `NumpadGridMouse.spec`:
   ```python
   icon='path/to/icon.ico',
   ```
3. Rebuild

### Console Mode (for debugging)

Edit `NumpadGridMouse.spec`:
```python
console=True,  # Show console window
```

This allows you to see print statements and error messages.

### One Directory Mode

Instead of a single file, create a folder with multiple files (smaller, faster startup):

Edit `NumpadGridMouse.spec` and change:
```python
exe = EXE(...)  # Remove --onefile equivalent
```

Or use:
```bash
pyinstaller --onedir --windowed --name "NumpadGridMouse" main.py
```

## Distribution

### For Personal Use

Simply copy `NumpadGridMouse.exe` to any Windows 10/11 computer and run as Administrator.

### For Distribution

Consider:
1. **Code signing**: Sign the executable with a certificate
2. **Installer**: Create an installer using Inno Setup or NSIS
3. **Documentation**: Include README and QUICKSTART.md
4. **Version info**: Add version information to the executable

## Build Script Details

The `build_exe.bat` script includes:
- Automatic PyInstaller installation check
- Hidden imports for all required modules
- Data collection for keyboard and pynput libraries
- Windowed mode (no console)
- UPX compression (if available)

## File Structure After Build

```
GridNav/
├── dist/
│   └── NumpadGridMouse.exe  ← Your executable
├── build/                    ← Temporary build files (can delete)
├── NumpadGridMouse.spec      ← PyInstaller configuration
└── ... (source files)
```

## Notes

- The executable is **portable** - no installation needed
- Configuration is still stored in `%APPDATA%\NumpadGridMouse\config.json`
- The executable works independently of Python installation
- First run may be slightly slower (extraction of bundled files)
