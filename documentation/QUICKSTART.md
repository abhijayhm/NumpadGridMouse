# Quick Start Guide

## Installation

1. **Install Python 3.8+** if you haven't already
   - Download from https://www.python.org/downloads/

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   - **Option 1:** Double-click `run.bat` (right-click → Run as Administrator)
   - **Option 2:** Open PowerShell/CMD as Administrator and run:
     ```bash
     python main.py
     ```

## First Use

1. **Start the application** (as Administrator)
   - You should see: "Numpad Grid Mouse started"
   - The application runs in the background

2. **Activate the grid:**
   - Press `Ctrl + Shift + /` (forward slash)
   - A 3×3 grid overlay should appear on your screen

3. **Navigate:**
   - Press number keys `1-9` to select regions
   - The grid will zoom into the selected region
   - Press `Backspace` to go back one level

4. **Click:**
   - Press `Enter` to left-click at the center of current region
   - Press `Ctrl + Enter` to right-click
   - Press `Space` to move pointer only (no click)

5. **Scroll:**
   - Use arrow keys (`↑ ↓ ← →`) to scroll at the current region

6. **Exit:**
   - Press `Esc` to hide the grid
   - Close the terminal to exit the application

## Troubleshooting

**Grid doesn't appear:**
- Make sure you ran as Administrator
- Check that no other app is using `Ctrl + Shift + /`
- Try increasing opacity in config: `%APPDATA%\NumpadGridMouse\config.json`

**Keys not working:**
- Ensure the grid is visible (press `Ctrl + Shift + /` again)
- Some keys may pass through to the active app - this is normal

**Hotkey conflict:**
- Edit `config.json` and change the `hotkeys.toggle` value
- Example: `"toggle": "ctrl+shift+g"`

## Configuration

Edit: `%APPDATA%\NumpadGridMouse\config.json`

Common settings:
- `grid.opacity`: 0.0 to 1.0 (higher = more visible)
- `grid.line_thickness`: Grid line width in pixels
- `grid.font_size`: Size of number labels
- `behavior.scroll_amount`: Lines to scroll per arrow key
- `sounds.enabled`: Enable/disable sound cues

## Tips

- Use `Ctrl + Shift + /` while grid is visible to drill deeper into the same region
- The grid automatically appears on the monitor containing your cursor
- You can refine the selection multiple times for pixel-perfect accuracy
- The HUD shows your current depth and region coordinates

Enjoy precise mouse control! 🎯
