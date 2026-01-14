# Project Structure

## Core Modules

### `main.py`
Main application entry point. Coordinates all components:
- Initializes all subsystems
- Manages application lifecycle
- Handles callbacks from input handler
- Main event loop

### `config.py`
Configuration management system:
- Loads/saves user preferences to `%APPDATA%\NumpadGridMouse\config.json`
- Provides default values
- Supports nested configuration access

### `grid_model.py`
Grid subdivision logic:
- `Region` class: Represents rectangular screen regions
- `GridModel` class: Manages recursive grid navigation
- Maps numpad keys (1-9) to grid positions
- Handles depth tracking and navigation stack

### `overlay.py`
Transparent overlay window:
- Uses tkinter for rendering
- Always-on-top, borderless window
- Displays 3×3 grid with labels
- Shows HUD with depth and region info
- Windows-specific click-through support

### `input_handler.py`
Keyboard input management:
- Global hotkey registration (keyboard library)
- Key capture and suppression (pynput library)
- State machine for grid visibility
- Handles all keyboard shortcuts

### `virtual_pointer.py`
Virtual pointer abstraction:
- Maintains virtual cursor position
- Only syncs to OS cursor on actions
- Handles mouse clicks and scrolling
- Windows-specific scroll support

### `sound_manager.py`
Accessibility sound cues:
- Optional audio feedback for actions
- Uses Windows Beep API
- Configurable per-action

### `monitor_utils.py`
Multi-monitor support:
- Detects monitor containing cursor
- Gets monitor dimensions
- Enumerates all monitors

## Test Files

### `test_grid_model.py`
Unit tests for grid functionality:
- Region subdivision tests
- Numpad mapping validation
- Depth limit tests
- Navigation stack tests

## Configuration Files

### `requirements.txt`
Python dependencies:
- pynput: Keyboard/mouse control
- pyautogui: Mouse automation
- keyboard: Global hotkeys
- pywin32: Windows API access
- Pillow: Image processing (for pyautogui)

### `config.json` (generated at runtime)
User configuration stored in app data folder

## Documentation

### `README.md`
Comprehensive documentation:
- Installation instructions
- Usage guide
- Configuration reference
- Troubleshooting
- Architecture overview

### `QUICKSTART.md`
Quick reference guide for first-time users

### `PROJECT_STRUCTURE.md`
This file - project organization

## Build Files

### `setup.py`
Python package setup (for packaging)

### `run.bat`
Windows launcher script with admin check

### `.gitignore`
Git ignore patterns

## Data Files

### `%APPDATA%\NumpadGridMouse\config.json`
User configuration (created at first run)

## Architecture Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Modularity**: Components can be tested and modified independently
3. **Extensibility**: Easy to add new features or modify behavior
4. **Windows-First**: Uses Windows-specific APIs for best performance
5. **Accessibility**: Built-in support for sound cues and customization

## Data Flow

```
User Input → InputHandler → Main App → GridModel
                                    ↓
                              OverlayWindow (visual feedback)
                                    ↓
                              VirtualPointer → OS Mouse
```

## Key Design Decisions

1. **Hybrid Input System**: Uses `keyboard` library for global hotkeys and `pynput` for key suppression
2. **Virtual Pointer**: Maintains separate virtual position to avoid cursor flicker
3. **Recursive Grid**: Unlimited depth by default, configurable limit
4. **Transparent Overlay**: Click-through support for non-intrusive operation
5. **Multi-Monitor**: Automatically detects and works with cursor's monitor
