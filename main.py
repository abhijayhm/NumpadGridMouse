"""
Main entry point for Numpad Grid Mouse.
Coordinates all components and manages the application lifecycle.
"""
import sys
import time
import queue
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
        self.action_queue = queue.Queue()
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Register all input callbacks."""
        self.input_handler.register_callback('on_toggle', lambda: self.action_queue.put(('toggle', None)))
        self.input_handler.register_callback('on_exit', lambda: self.action_queue.put(('exit', None)))
        self.input_handler.register_callback('on_number', lambda key: self.action_queue.put(('number', key)))
        self.input_handler.register_callback('on_enter', lambda: self.action_queue.put(('enter', None)))
        self.input_handler.register_callback('on_shift_enter', lambda: self.action_queue.put(('shift_enter', None)))
        self.input_handler.register_callback('on_space', lambda: self.action_queue.put(('space', None)))
        self.input_handler.register_callback('on_backspace', lambda: self.action_queue.put(('backspace', None)))
        self.input_handler.register_callback('on_arrow', lambda direction: self.action_queue.put(('arrow', direction)))
    
    def _on_toggle(self):
        """Handle toggle hotkey."""
        # Lock mode: if grid is already visible, don't spawn another overlay
        if self.input_handler.state == GridState.VISIBLE:
            # Grid is locked - repeat last selection (drill deeper)
            if self.grid_model:
                # Re-select the center region (5)
                new_region = self.grid_model.select_region(5)
                if new_region:
                    center_x, center_y = new_region.center()
                    self.virtual_pointer.move_to(center_x, center_y, sync=True)
                self.overlay.update_display()
                self.sound_manager.play_refine_selection()
        else:
            # Grid is hidden - show it
            self._show_grid()
            # Move mouse to center of initial grid
            if self.grid_model:
                current = self.grid_model.get_current_region()
                center_x, center_y = current.center()
                self.virtual_pointer.move_to(center_x, center_y, sync=True)
    
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
        """Handle exit (hide grid) - always works regardless of state."""
        # Always clear overlay when ESC is pressed
        self.overlay.hide()
        self.input_handler.set_state(GridState.HIDDEN)
    
    def _on_number(self, key: int):
        """Handle number key selection."""
        if not self.grid_model:
            return
        
        new_region = self.grid_model.select_region(key)
        if new_region:
            # Move mouse to center of selected region
            center_x, center_y = new_region.center()
            self.virtual_pointer.move_to(center_x, center_y, sync=True)
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
    
    def _on_shift_enter(self):
        """Handle Shift+Enter (right click)."""
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
            # Move mouse to center of parent region
            center_x, center_y = new_region.center()
            self.virtual_pointer.move_to(center_x, center_y, sync=True)
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
                # Process actions from queue (thread-safe communication)
                try:
                    while True:
                        action, data = self.action_queue.get_nowait()
                        self._process_action(action, data)
                except queue.Empty:
                    pass
                
                # Update overlay if visible
                if self.overlay.is_visible():
                    self.overlay.update()
                else:
                    time.sleep(0.01)  # Small sleep to prevent busy waiting
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.shutdown()
    
    def _process_action(self, action: str, data):
        """Process an action from the queue (runs in main thread)."""
        if action == 'toggle':
            self._on_toggle()
        elif action == 'exit':
            self._on_exit()
        elif action == 'number':
            self._on_number(data)
        elif action == 'enter':
            self._on_enter()
        elif action == 'shift_enter':
            self._on_shift_enter()
        elif action == 'space':
            self._on_space()
        elif action == 'backspace':
            self._on_backspace()
        elif action == 'arrow':
            self._on_arrow(data)
    
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
