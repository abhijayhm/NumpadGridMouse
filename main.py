"""
Main entry point for Numpad Grid Mouse.
Coordinates all components and manages the application lifecycle.
"""
import sys
import time
import pyautogui
from grid_model import GridModel, Region
from overlay import OverlayWindow
from input_handler import InputHandler, GridState
from virtual_pointer import VirtualPointer
from sound_manager import SoundManager
from monitor_utils import get_monitor_containing_cursor
from config import Config


class NumpadGridMouse:
    """Main application class."""
    
    def __init__(self):
        self.config = Config()
        self.grid_model: GridModel = None
        self.overlay = OverlayWindow(self.config)
        self.input_handler = InputHandler(self.config)
        self.virtual_pointer = VirtualPointer()
        self.sound_manager = SoundManager(self.config)
        
        self.running = True
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Register all input callbacks."""
        self.input_handler.register_callback('on_toggle', self._on_toggle)
        self.input_handler.register_callback('on_exit', self._on_exit)
        self.input_handler.register_callback('on_number', self._on_number)
        self.input_handler.register_callback('on_enter', self._on_enter)
        self.input_handler.register_callback('on_ctrl_enter', self._on_ctrl_enter)
        self.input_handler.register_callback('on_space', self._on_space)
        self.input_handler.register_callback('on_backspace', self._on_backspace)
        self.input_handler.register_callback('on_arrow', self._on_arrow)
    
    def _on_toggle(self):
        """Handle toggle hotkey."""
        if self.input_handler.state == GridState.HIDDEN:
            self._show_grid()
        else:
            # Repeat last selection (drill deeper)
            if self.grid_model:
                current = self.grid_model.get_current_region()
                # Re-select the center region (5)
                self.grid_model.select_region(5)
                self.overlay.update_display()
                self.sound_manager.play_refine_selection()
    
    def _show_grid(self):
        """Show the grid overlay."""
        # Get monitor containing cursor
        monitor = get_monitor_containing_cursor()
        screen_region = Region(monitor[0], monitor[1], monitor[2], monitor[3])
        
        # Initialize or reset grid model
        max_depth = self.config.get('behavior', 'max_depth')
        if self.grid_model is None:
            self.grid_model = GridModel(screen_region, max_depth)
        else:
            self.grid_model.reset(screen_region)
        
        # Update overlay
        self.overlay.set_grid_model(self.grid_model)
        self.overlay.update_display()
        self.overlay.show()
        
        # Update state
        self.input_handler.set_state(GridState.VISIBLE)
        self.sound_manager.play_show_grid()
    
    def _on_exit(self):
        """Handle exit (hide grid)."""
        self.overlay.hide()
        self.input_handler.set_state(GridState.HIDDEN)
    
    def _on_number(self, key: int):
        """Handle number key selection."""
        if not self.grid_model:
            return
        
        new_region = self.grid_model.select_region(key)
        if new_region:
            self.overlay.update_display()
            self.sound_manager.play_refine_selection()
    
    def _on_enter(self):
        """Handle Enter (left click)."""
        if not self.grid_model:
            return
        
        current_region = self.grid_model.get_current_region()
        center_x, center_y = current_region.center()
        
        self.virtual_pointer.move_to(center_x, center_y, sync=True)
        self.virtual_pointer.click('left')
        self.sound_manager.play_click()
        
        # Hide grid after click
        self._on_exit()
    
    def _on_ctrl_enter(self):
        """Handle Ctrl+Enter (right click)."""
        if not self.grid_model:
            return
        
        current_region = self.grid_model.get_current_region()
        center_x, center_y = current_region.center()
        
        self.virtual_pointer.move_to(center_x, center_y, sync=True)
        self.virtual_pointer.click('right')
        self.sound_manager.play_click()
        
        # Hide grid after click
        self._on_exit()
    
    def _on_space(self):
        """Handle Space (move pointer only)."""
        if not self.grid_model:
            return
        
        current_region = self.grid_model.get_current_region()
        center_x, center_y = current_region.center()
        
        self.virtual_pointer.move_to(center_x, center_y, sync=True)
        
        # Hide grid after move
        self._on_exit()
    
    def _on_backspace(self):
        """Handle Backspace (go up one level)."""
        if not self.grid_model:
            return
        
        new_region = self.grid_model.go_up()
        if new_region:
            self.overlay.update_display()
            self.sound_manager.play_refine_selection()
    
    def _on_arrow(self, direction: str):
        """Handle arrow key (scroll)."""
        if not self.grid_model:
            return
        
        current_region = self.grid_model.get_current_region()
        center_x, center_y = current_region.center()
        
        # Move pointer to center first
        self.virtual_pointer.move_to(center_x, center_y, sync=True)
        
        # Get scroll amount from config
        scroll_amount = self.config.get('behavior', 'scroll_amount')
        
        # Determine scroll direction
        dx, dy = 0, 0
        if direction == 'up':
            dy = scroll_amount
        elif direction == 'down':
            dy = -scroll_amount
        elif direction == 'left':
            dx = -scroll_amount
        elif direction == 'right':
            dx = scroll_amount
        
        self.virtual_pointer.scroll(dx, dy)
        self.sound_manager.play_scroll()
    
    def run(self):
        """Main application loop."""
        print("Numpad Grid Mouse started")
        print("Press Ctrl+Shift+/ to toggle grid")
        print("Press Esc to exit grid mode")
        
        self.input_handler.start()
        
        try:
            while self.running:
                if self.overlay.is_visible():
                    self.overlay.update()
                else:
                    time.sleep(0.1)  # Reduce CPU usage when hidden
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown."""
        self.input_handler.stop()
        self.overlay.destroy()
        self.running = False


def main():
    """Entry point."""
    # Disable pyautogui failsafe for smoother operation
    pyautogui.FAILSAFE = False
    
    app = NumpadGridMouse()
    app.run()


if __name__ == '__main__':
    main()
