@echo off
REM Simple build script using the spec file

echo Building Numpad Grid Mouse executable...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if %errorLevel% neq 0 (
    echo PyInstaller is not installed. Installing...
    pip install pyinstaller
)

echo.
echo Building from spec file...
pyinstaller NumpadGridMouse.spec

if %errorLevel% == 0 (
    echo.
    echo ========================================
    echo Build successful!
    echo Executable: dist\NumpadGridMouse.exe
    echo ========================================
) else (
    echo Build failed!
)

pause
