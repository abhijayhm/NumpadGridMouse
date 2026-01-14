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
from monitor_utils import get_virtual_desktop_bounds, get_all_monitor_rects


class OverlayWindow:
    """
    Transparent, always-on-top overlay window displaying the grid.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.root = tk.Tk()
        self.canvas: Optional[tk.Canvas] = None
        self.grid_model: Optional[GridModel] = None
        self.window_offset_x = 0
        self.window_offset_y = 0
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
        
        # Get virtual desktop bounds to cover all monitors
        min_x, min_y, max_x, max_y = get_virtual_desktop_bounds()
        screen_width = max_x - min_x
        screen_height = max_y - min_y
        
        # Store window offset for coordinate conversion
        self.window_offset_x = min_x
        self.window_offset_y = min_y
        
        # Position window to cover entire virtual desktop (all monitors)
        self.root.geometry(f"{screen_width}x{screen_height}+{min_x}+{min_y}")
        
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
    
    def show_monitor_selection(self, monitors):
        """Show monitor selection overlay."""
        if not self.canvas:
            return
        
        self.canvas.delete("all")
        
        # Get virtual desktop bounds for overlay
        min_x, min_y, max_x, max_y = get_virtual_desktop_bounds()
        screen_width = max_x - min_x
        screen_height = max_y - min_y
        
        # Draw each monitor with a number
        border_color = self.config.get('grid', 'border_color')
        base_font_size = self.config.get('grid', 'font_size')
        label_font = font.Font(size=base_font_size, weight='bold')
        
        # Get full monitor rects (not work areas) for accurate outline display
        monitor_rects = get_all_monitor_rects()
        
        for idx, monitor_rect in enumerate(monitor_rects):
            x, y, w, h = monitor_rect
            
            # Convert screen coordinates to canvas coordinates (relative to window)
            canvas_x = x - self.window_offset_x
            canvas_y = y - self.window_offset_y
            
            # Draw monitor border (make it thinner)
            self.canvas.create_rectangle(
                canvas_x, canvas_y, canvas_x + w, canvas_y + h,
                outline=border_color,
                width=2,
                fill=''
            )
            
            # Draw monitor number in center
            center_x = canvas_x + w // 2
            center_y = canvas_y + h // 2
            monitor_num = idx + 1
            
            # Draw background circle (make it smaller)
            text_bg_size = base_font_size // 2 + 6
            bg_fill = '#FFFF00'  # Bright yellow
            self.canvas.create_oval(
                center_x - text_bg_size, center_y - text_bg_size,
                center_x + text_bg_size, center_y + text_bg_size,
                fill=bg_fill, outline=border_color, width=1
            )
            
            # Draw number
            self.canvas.create_text(
                center_x, center_y,
                text=str(monitor_num),
                fill='#000000',
                font=label_font,
                anchor='center'
            )
            
            # Draw monitor info text below number
            info_font = font.Font(size=base_font_size // 2)
            info_text = f"Monitor {monitor_num}\n{w}×{h}"
            self.canvas.create_text(
                center_x, center_y + text_bg_size + 20,
                text=info_text,
                fill='#FFFFFF',
                font=info_font,
                anchor='center'
            )
        
        # Show instruction text at top (relative to window)
        instruction_font = font.Font(size=base_font_size // 2 + 4, weight='bold')
        instruction_text = "Select Monitor: Press 1-9 to choose"
        self.canvas.create_text(
            screen_width // 2, 30,
            text=instruction_text,
            fill='#FFFFFF',
            font=instruction_font,
            anchor='center'
        )
        
        # Force update
        self.root.update_idletasks()
        self.root.update()
    
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
        base_font_size = self.config.get('grid', 'font_size')
        
        # Scale font size based on region size to prevent overlapping
        # Use the smallest dimension of the first region as reference
        if all_regions:
            first_region = all_regions[0]
            _, _, w, h = first_region.bounds()
            min_dimension = min(w, h)
            # Scale font: smaller regions get smaller font
            # Base size for full screen, scale down proportionally
            # Minimum font size of 6, maximum of base_font_size
            # Use smaller divisor (40 instead of 25) to make text smaller
            font_size = max(6, min(base_font_size, int(min_dimension / 40)))
        else:
            font_size = base_font_size
        
        # Create font
        label_font = font.Font(size=font_size, weight='bold')
        
        # Draw grid cells
        numpad_to_key = {v: k for k, v in GridModel.NUMPAD_MAP.items()}
        
        for idx, region in enumerate(all_regions):
            x, y, w, h = region.bounds()
            
            # Convert screen coordinates to canvas coordinates (relative to window)
            canvas_x = x - self.window_offset_x
            canvas_y = y - self.window_offset_y
            
            # Draw border with thicker lines for visibility
            self.canvas.create_rectangle(
                canvas_x, canvas_y, canvas_x + w, canvas_y + h,
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
                center_x = canvas_x + w // 2
                center_y = canvas_y + h // 2
                # Draw background circle for text visibility - use bright color
                # Scale background size with font size (make it smaller)
                text_bg_size = max(6, font_size // 2 + 4)
                # Use bright yellow background - NOT the transparent color
                bg_fill = '#FFFF00'  # Bright yellow
                # Draw filled circle background with border (make border thinner)
                self.canvas.create_oval(
                    center_x - text_bg_size, center_y - text_bg_size,
                    center_x + text_bg_size, center_y + text_bg_size,
                    fill=bg_fill, outline=border_color, width=1
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
