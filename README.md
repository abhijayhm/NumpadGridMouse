# Numpad Grid Mouse

A Windows-first desktop utility that provides a fully keyboard-driven pointing system. Control your mouse with precision using a recursive 3×3 grid, number keys, and minimal hand movement.

## Features

- **Recursive Grid Navigation**: Divide your screen into a 3×3 grid, then drill down into any region recursively
- **Keyboard-Only Control**: Complete mouse control without touching your mouse
- **Precise Targeting**: Navigate to any pixel on screen with multiple levels of refinement
- **Multi-Monitor Support**: Automatically detects and works with the monitor containing your cursor
- **Always-On-Top Overlay**: Transparent grid overlay that doesn't interfere with your work
- **Virtual Pointer**: Smart pointer system that only moves the OS cursor when needed
- **Accessibility Features**: Sound cues, high-contrast themes, and customizable settings

## Installation

### Prerequisites

- Windows 10 or later
- Python 3.8 or later
- Administrator privileges (for global hotkey registration)

### Quick Start

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Running as Administrator

The application needs administrator privileges to register global hotkeys. Right-click your terminal/PowerShell and select "Run as Administrator", then run:

```bash
python main.py
```

Alternatively, you can create a shortcut that always runs as administrator (see Packaging section).

## Usage

### Basic Controls

| Action | Key Combination | Description |
|--------|----------------|-------------|
| **Show Grid** | `Ctrl + Shift + /` | Toggle the grid overlay on/off |
| **Exit Grid** | `Esc` | Hide the grid overlay |
| **Select Region** | `1-9` | Select a region in the 3×3 grid |
| **Left Click** | `Enter` | Move pointer to center and left click |
| **Right Click** | `Ctrl + Enter` | Move pointer to center and right click |
| **Move Only** | `Space` | Move pointer to center (no click) |
| **Go Up Level** | `Backspace` | Return to previous grid level |
| **Scroll Up** | `↑` | Scroll up at current region |
| **Scroll Down** | `↓` | Scroll down at current region |
| **Scroll Left** | `←` | Scroll left at current region |
| **Scroll Right** | `→` | Scroll right at current region |
| **Drill Deeper** | `Ctrl + Shift + /` (when visible) | Repeat last selection (zoom into same region) |

### Grid Layout

The grid is labeled with numpad-style numbers:

```
┌─────┬─────┬─────┐
│  7  │  8  │  9  │
├─────┼─────┼─────┤
│  4  │  5  │  6  │
├─────┼─────┼─────┤
│  1  │  2  │  3  │
└─────┴─────┴─────┘
```

### Workflow Example

1. Press `Ctrl + Shift + /` to show the grid
2. Press `5` to select the center region
3. Press `5` again to zoom into the center of that region
4. Press `7` to select the top-left of the refined region
5. Press `Enter` to click at that location

The grid can be refined indefinitely (or until you hit the depth limit in config).

## Configuration

Configuration is stored in `%APPDATA%\NumpadGridMouse\config.json`. You can edit this file directly or modify it through the application.

### Configuration Options

```json
{
  "grid": {
    "line_thickness": 2,
    "font_size": 24,
    "opacity": 0.85,
    "border_color": "#00FF00",
    "text_color": "#FFFFFF",
    "background_color": "#000000",
    "high_contrast": false
  },
  "hud": {
    "enabled": true,
    "font_size": 14,
    "position": "top_left",
    "text_color": "#FFFFFF",
    "background_color": "#00000080"
  },
  "sounds": {
    "enabled": true,
    "show_grid": true,
    "refine_selection": true,
    "click": true,
    "scroll": false
  },
  "behavior": {
    "max_depth": 0,
    "scroll_amount": 3,
    "animation_duration": 0.1
  },
  "hotkeys": {
    "toggle": "ctrl+shift+/",
    "exit": "esc"
  }
}
```

### Configuration Fields

- **grid.line_thickness**: Thickness of grid lines in pixels
- **grid.font_size**: Size of region number labels
- **grid.opacity**: Overlay transparency (0.0 to 1.0)
- **grid.border_color**: Hex color for grid lines
- **grid.text_color**: Hex color for number labels
- **grid.high_contrast**: Enable high-contrast theme
- **hud.enabled**: Show depth and region info
- **hud.position**: HUD position (`top_left`, `top_right`, `bottom_left`, `bottom_right`)
- **sounds.enabled**: Enable all sound cues
- **behavior.max_depth**: Maximum recursion depth (0 = unlimited)
- **behavior.scroll_amount**: Lines/pixels to scroll per arrow key press
- **hotkeys.toggle**: Hotkey to toggle grid (keyboard library format)

## Architecture

The application is organized into clean, separate modules:

- **`config.py`**: Configuration management
- **`grid_model.py`**: Grid subdivision logic and recursion stack
- **`overlay.py`**: Transparent overlay window rendering
- **`input_handler.py`**: Keyboard input and state machine
- **`virtual_pointer.py`**: Virtual pointer abstraction and OS mouse interface
- **`sound_manager.py`**: Accessibility sound cues
- **`monitor_utils.py`**: Multi-monitor detection and positioning
- **`main.py`**: Main application coordinator

## Troubleshooting

### Hotkey Not Working

- **Run as Administrator**: The application needs admin privileges to register global hotkeys
- **Check for Conflicts**: Another application might be using `Ctrl + Shift + /`
- **Modify Hotkey**: Edit `config.json` to use a different hotkey combination

### Overlay Not Visible

- **Check Opacity**: Increase `grid.opacity` in config (try 0.9 or 1.0)
- **Check Colors**: Ensure border and text colors are visible against your background
- **Multiple Monitors**: The overlay appears on the monitor containing your cursor

### Grid Not Responding to Keys

- **Focus**: The overlay should capture keyboard input automatically
- **Check State**: Press `Ctrl + Shift + /` again to ensure grid is active
- **Restart**: Close and restart the application

### Performance Issues

- **Reduce Opacity**: Lower opacity can improve rendering performance
- **Disable HUD**: Set `hud.enabled` to `false` in config
- **Disable Sounds**: Set `sounds.enabled` to `false` in config

## Permissions Notes

- **Global Hotkeys**: Requires administrator privileges to register system-wide hotkeys
- **Mouse Control**: Needs permission to control mouse cursor and clicks
- **Always-On-Top**: May require special permissions on some Windows configurations

## Packaging

### Single-File Build

To create a single executable file:

#### Option 1: Using the Build Script (Recommended)

1. **Install PyInstaller** (if not already installed):
   ```bash
   pip install pyinstaller
   ```

2. **Run the build script:**
   ```bash
   build_exe.bat
   ```
   
   Or use the simple version:
   ```bash
   build_exe_simple.bat
   ```

3. **The executable will be in the `dist` folder** as `NumpadGridMouse.exe`

#### Option 2: Manual Build

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build using the spec file:**
   ```bash
   pyinstaller NumpadGridMouse.spec
   ```

3. **Or build directly:**
   ```bash
   pyinstaller --onefile --windowed --name "NumpadGridMouse" --hidden-import win32timezone --hidden-import pynput.keyboard --hidden-import pynput.mouse --hidden-import keyboard --collect-all keyboard --collect-all pynput main.py
   ```

#### Running the Executable

- The executable requires **administrator privileges** to register global hotkeys
- Right-click `NumpadGridMouse.exe` and select **"Run as Administrator"**
- Or create a shortcut with "Run as Administrator" enabled in properties

#### Build Options

- **Windowed mode** (default): No console window, runs silently in background
- **Console mode**: For debugging, modify the spec file and set `console=True`

### Installer with Startup Option

For a full installer with startup option, you can use:

1. **Inno Setup** (Windows installer creator)
2. **NSIS** (Nullsoft Scriptable Install System)

Create an installer script that:
- Copies the executable to Program Files
- Creates a Start Menu shortcut
- Adds a registry entry for "Run on Startup" (optional)
- Sets up uninstaller

## Development

### Running Tests

```bash
python -m pytest test_grid_model.py
```

Or using unittest:

```bash
python test_grid_model.py
```

### Project Structure

```
GridNav/
├── main.py                 # Main entry point
├── config.py               # Configuration system
├── grid_model.py           # Grid logic
├── overlay.py              # Overlay rendering
├── input_handler.py        # Input handling
├── virtual_pointer.py      # Mouse control
├── sound_manager.py        # Sound cues
├── monitor_utils.py        # Multi-monitor support
├── test_grid_model.py      # Unit tests
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Design Goals

- ✅ **Fast**: Minimal latency between keypress and action
- ✅ **Precise**: Recursive subdivision allows pixel-perfect targeting
- ✅ **Low Cognitive Load**: Simple numpad mapping, clear visual feedback
- ✅ **Extensible**: Modular architecture for future features

## Future Enhancements

Potential features for future versions:

- Custom grid sizes (4×4, 5×5, etc.)
- Mouse movement animations
- Gesture recognition
- Custom action mappings
- Plugin system
- Cross-platform support (Linux, macOS)

## License

This project is provided as-is for personal and educational use.

## Contributing

Contributions are welcome! Please ensure:

- Code follows the existing architecture
- Unit tests are included for new features
- Documentation is updated
- Code is tested on Windows 10/11

## Support

For issues, questions, or feature requests, please open an issue in the repository.

---

**Enjoy precise mouse control with your keyboard!** 🎯
