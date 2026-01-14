"""
Overlay rendering system: transparent, always-on-top window.
Displays the 3×3 grid and HUD information.
"""
import tkinter as tk
from tkinter import font
import win32gui
import win32con
import win32api
from typing import List, Optional
from grid_model import Region, GridModel
from config import Config


class OverlayWindow:
    """
    Transparent, always-on-top overlay window displaying the grid.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.root = tk.Tk()
        self.canvas: Optional[tk.Canvas] = None
        self.grid_model: Optional[GridModel] = None
        self._setup_window()
        self._setup_canvas()
        # Hide overlay initially
        self.hide()
    
    def _setup_window(self):
        """Configure window properties for overlay."""
        self.root.title("Numpad Grid Mouse Overlay")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', self.config.get('grid', 'opacity'))
        self.root.overrideredirect(True)  # Borderless
        
        # Use a specific transparent color that won't interfere with drawing
        # Use a very specific color that we'll never use for drawing
        transparent_color = '#010101'  # Almost black but not pure black
        self.root.config(bg=transparent_color)
        self.root.attributes('-transparentcolor', transparent_color)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Position window to cover entire screen
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Update to ensure window is created
        self.root.update_idletasks()
        
        # Make window click-through (Windows-specific)
        self._make_click_through()
    
    def _make_click_through(self):
        """Make the window click-through using Windows API."""
        try:
            # Ensure window is fully created
            self.root.update_idletasks()
            self.root.update()
            
            # Get window handle - try multiple methods for reliability
            hwnd = None
            
            # Method 1: Use winfo_id() directly (works on Windows)
            try:
                frame_hwnd = self.root.winfo_id()
                if frame_hwnd:
                    # On Windows, winfo_id() returns the frame widget handle
                    # Try to get the parent window (actual window handle)
                    parent_hwnd = win32gui.GetParent(frame_hwnd)
                    if parent_hwnd:
                        hwnd = parent_hwnd
                    else:
                        # If no parent, the frame handle might be the window itself
                        hwnd = frame_hwnd
            except:
                pass
            
            # Method 2: Find window by title if method 1 failed
            if not hwnd:
                try:
                    hwnd = win32gui.FindWindow(None, "Numpad Grid Mouse Overlay")
                except:
                    pass
            
            if hwnd:
                # Get extended window style
                ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                # Add layered and transparent flags
                ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
        except Exception as e:
            print(f"Warning: Could not set click-through: {e}")
            # Click-through is optional, continue without it
    
    def _setup_canvas(self):
        """Create and configure canvas for drawing."""
        # Use the same transparent color as window
        transparent_color = '#010101'
        self.canvas = tk.Canvas(
            self.root,
            bg=transparent_color,
            highlightthickness=0,
            borderwidth=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
    
    def set_grid_model(self, grid_model: GridModel):
        """Set the grid model to visualize."""
        self.grid_model = grid_model
    
    def update_display(self):
        """Redraw the grid overlay."""
        if not self.canvas or not self.grid_model:
            return
        
        self.canvas.delete("all")
        
        # Get current region and all sub-regions
        current_region = self.grid_model.get_current_region()
        all_regions = self.grid_model.get_all_regions()
        
        # Draw grid lines and labels
        line_thickness = self.config.get('grid', 'line_thickness')
        border_color = self.config.get('grid', 'border_color')
        text_color = self.config.get('grid', 'text_color')
        font_size = self.config.get('grid', 'font_size')
        
        # Create font
        label_font = font.Font(size=font_size, weight='bold')
        
        # Draw grid cells
        numpad_to_key = {v: k for k, v in GridModel.NUMPAD_MAP.items()}
        
        for idx, region in enumerate(all_regions):
            x, y, w, h = region.bounds()
            
            # Draw border with thicker lines for visibility
            self.canvas.create_rectangle(
                x, y, x + w, y + h,
                outline=border_color,
                width=line_thickness,
                fill=''  # Empty fill - transparent
            )
            
            # Calculate which numpad key this corresponds to
            # Current region is subdivided into 3×3
            row = idx // 3
            col = idx % 3
            numpad_key = numpad_to_key.get((row, col))
            
            if numpad_key:
                # Draw label in center with background for visibility
                center_x = x + w // 2
                center_y = y + h // 2
                # Draw background circle for text visibility - use bright color
                text_bg_size = font_size // 2 + 12
                # Use bright yellow background - NOT the transparent color
                bg_fill = '#FFFF00'  # Bright yellow
                # Draw filled circle background with border
                self.canvas.create_oval(
                    center_x - text_bg_size, center_y - text_bg_size,
                    center_x + text_bg_size, center_y + text_bg_size,
                    fill=bg_fill, outline=border_color, width=2
                )
                # Draw text with strong contrast - black on yellow
                self.canvas.create_text(
                    center_x, center_y,
                    text=str(numpad_key),
                    fill='#000000',  # Black text
                    font=label_font,
                    anchor='center'
                )
        
        # Draw HUD if enabled
        if self.config.get('hud', 'enabled'):
            self._draw_hud(current_region)
        
        # Force update to ensure drawing is visible
        self.root.update_idletasks()
        self.root.update()
    
    def _draw_hud(self, current_region: Region):
        """Draw HUD showing depth and region bounds."""
        if not self.canvas or not self.grid_model:
            return
        
        depth = self.grid_model.get_depth()
        x, y, w, h = current_region.bounds()
        center_x, center_y = current_region.center()
        
        hud_text = f"Depth: {depth}\nRegion: ({x}, {y}) {w}×{h}\nCenter: ({center_x}, {center_y})"
        
        hud_font_size = self.config.get('hud', 'font_size')
        hud_font = font.Font(size=hud_font_size)
        hud_text_color = self.config.get('hud', 'text_color')
        hud_bg_color = self.config.get('hud', 'background_color')
        
        # Parse background color (supports hex with alpha)
        bg_color = hud_bg_color
        if bg_color.endswith('80'):  # Semi-transparent
            bg_color = bg_color[:-2]
        
        # Position HUD
        position = self.config.get('hud', 'position')
        if position == 'top_left':
            hud_x, hud_y = 10, 10
        elif position == 'top_right':
            hud_x = self.root.winfo_width() - 200
            hud_y = 10
        elif position == 'bottom_left':
            hud_x = 10
            hud_y = self.root.winfo_height() - 100
        else:  # bottom_right
            hud_x = self.root.winfo_width() - 200
            hud_y = self.root.winfo_height() - 100
        
        # Draw background rectangle
        self.canvas.create_rectangle(
            hud_x - 5, hud_y - 5,
            hud_x + 190, hud_y + 90,
            fill=bg_color,
            outline=''
        )
        
        # Draw text
        self.canvas.create_text(
            hud_x, hud_y,
            text=hud_text,
            fill=hud_text_color,
            font=hud_font,
            anchor='nw'
        )
    
    def show(self):
        """Show the overlay window."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        # Force window to be visible
        self.root.update_idletasks()
        self.root.update()
        # Update display when showing
        if self.grid_model:
            self.update_display()
        # Re-apply click-through after showing
        self._make_click_through()
        # Final update to ensure everything is rendered
        self.root.update_idletasks()
        self.root.update()
    
    def hide(self):
        """Hide the overlay window."""
        self.root.withdraw()
    
    def is_visible(self) -> bool:
        """Check if overlay is currently visible."""
        try:
            return self.root.winfo_viewable()
        except:
            return False
    
    def update(self):
        """Update the window (call in main loop)."""
        self.root.update_idletasks()
        self.root.update()
    
    def destroy(self):
        """Destroy the overlay window."""
        self.root.destroy()
