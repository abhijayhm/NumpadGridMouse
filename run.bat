@echo off
REM Launcher script for Numpad Grid Mouse
REM Checks for admin privileges and runs the application

net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
    python main.py
) else (
    echo This application requires administrator privileges for global hotkeys.
    echo Please run this script as Administrator.
    echo.
    echo Right-click this file and select "Run as Administrator"
    pause
)
