@echo off
REM Build script for creating Numpad Grid Mouse executable
REM Requires PyInstaller to be installed: pip install pyinstaller

echo Building Numpad Grid Mouse executable...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if %errorLevel% neq 0 (
    echo PyInstaller is not installed. Installing...
    pip install pyinstaller
)

echo.
echo Creating executable...
echo.

REM Build with PyInstaller using spec file (recommended)
pyinstaller NumpadGridMouse.spec

REM Alternative: Direct build command (uncomment to use instead)
REM pyinstaller --onefile ^
REM     --windowed ^
REM     --name "NumpadGridMouse" ^
REM     --hidden-import win32timezone ^
REM     --hidden-import pynput.keyboard ^
REM     --hidden-import pynput.mouse ^
REM     --hidden-import keyboard ^
REM     --hidden-import pyautogui ^
REM     --hidden-import win32gui ^
REM     --hidden-import win32con ^
REM     --hidden-import win32api ^
REM     --hidden-import win32com ^
REM     --hidden-import pythoncom ^
REM     --collect-all keyboard ^
REM     --collect-all pynput ^
REM     main.py

if %errorLevel% == 0 (
    echo.
    echo ========================================
    echo Build successful!
    echo Executable location: dist\NumpadGridMouse.exe
    echo ========================================
    echo.
    echo Note: The executable requires administrator privileges to run.
    echo Right-click the .exe and select "Run as Administrator"
) else (
    echo.
    echo Build failed! Check the error messages above.
)

pause
