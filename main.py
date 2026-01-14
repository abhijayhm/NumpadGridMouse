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
from monitor_utils import get_monitor_containing_cursor, get_all_monitors, get_primary_monitor
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
        self.selected_monitor = None  # Store selected monitor
        self.monitor_selection_mode = False
        self._overlay_was_visible_before_pause = False  # Track overlay visibility before pause
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Register all input callbacks."""
        self.input_handler.register_callback('on_toggle', lambda: self.action_queue.put(('toggle', None)))
        self.input_handler.register_callback('on_exit', lambda: self.action_queue.put(('exit', None)))
        self.input_handler.register_callback('on_reset_to_top', lambda: self.action_queue.put(('reset_to_top', None)))
        self.input_handler.register_callback('on_number', lambda key: self.action_queue.put(('number', key)))
        self.input_handler.register_callback('on_enter', lambda: self.action_queue.put(('enter', None)))
        self.input_handler.register_callback('on_shift_enter', lambda: self.action_queue.put(('shift_enter', None)))
        self.input_handler.register_callback('on_space', lambda: self.action_queue.put(('space', None)))
        self.input_handler.register_callback('on_backspace', lambda: self.action_queue.put(('backspace', None)))
        self.input_handler.register_callback('on_arrow', lambda direction: self.action_queue.put(('arrow', direction)))
        self.input_handler.register_callback('on_pause', lambda: self.action_queue.put(('pause', None)))
        self.input_handler.register_callback('on_resume', lambda: self.action_queue.put(('resume', None)))
    
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
        elif self.input_handler.state == GridState.SELECTING_MONITOR:
            # Already in monitor selection, ignore
            pass
        else:
            # Grid is hidden - start fresh (always check for monitor selection if multiple monitors)
            # Reset any previous selection to ensure fresh start
            self.selected_monitor = None
            self.grid_model = None
            
            monitors = get_all_monitors()
            if len(monitors) > 1:
                # Multiple monitors - show selection
                self._show_monitor_selection(monitors)
            else:
                # Single monitor - use primary monitor by default
                monitor = get_primary_monitor()
                self.selected_monitor = monitor
                self._show_grid()
                # Move mouse to center of initial grid
                if self.grid_model:
                    current = self.grid_model.get_current_region()
                    center_x, center_y = current.center()
                    self.virtual_pointer.move_to(center_x, center_y, sync=True)
    
    def _show_monitor_selection(self, monitors):
        """Show monitor selection grid."""
        # Draw monitor selection directly (no grid model needed)
        self.overlay.show_monitor_selection(monitors)
        self.overlay.show()
        
        # Set state to monitor selection
        self.input_handler.set_state(GridState.SELECTING_MONITOR)
        self.monitor_selection_mode = True
        self.sound_manager.play_show_grid()
    
    def _show_grid(self):
        """Show the grid overlay."""
        # Use selected monitor or fallback to primary monitor
        if self.selected_monitor:
            monitor = self.selected_monitor
        else:
            monitor = get_primary_monitor()
        
        # Always create a fresh grid model with the selected monitor's coordinates
        # This ensures the grid spans the entire selected monitor
        screen_region = Region(monitor[0], monitor[1], monitor[2], monitor[3])
        
        # Always create a new grid model to ensure fresh state
        max_depth = self.config.get('behavior', 'max_depth')
        self.grid_model = GridModel(screen_region, max_depth)
        
        # Update overlay
        self.overlay.set_grid_model(self.grid_model)
        self.overlay.update_display()
        self.overlay.show()
        
        # Update state
        self.input_handler.set_state(GridState.VISIBLE)
        self.sound_manager.play_show_grid()
    
    def _on_exit(self):
        """Handle exit (hide grid and reset state) - only when grid is hidden."""
        # Only exit when grid is hidden (ESC pressed when not in grid mode)
        self.overlay.hide()
        # Completely reset ALL state - start completely fresh next time
        self.input_handler.set_state(GridState.HIDDEN)
        self.monitor_selection_mode = False
        self.selected_monitor = None  # Reset selected monitor
        self.grid_model = None  # Reset grid model
        # Force overlay to clear any display
        if self.overlay.canvas:
            self.overlay.canvas.delete("all")
    
    def _on_reset_to_top(self):
        """Reset grid to original full screen (top level)."""
        if not self.grid_model:
            return
        
        # Get the root region (first region in stack)
        root_region = self.grid_model.stack[0]
        
        # Reset the grid model to top level
        self.grid_model.reset(root_region)
        
        # Move mouse to center of the full screen grid
        current_region = self.grid_model.get_current_region()
        center_x, center_y = current_region.center()
        self.virtual_pointer.move_to(center_x, center_y, sync=True)
        
        # Update display
        self.overlay.update_display()
        self.sound_manager.play_refine_selection()
    
    def _on_number(self, key: int):
        """Handle number key selection."""
        # If in monitor selection mode, handle monitor selection
        if self.input_handler.state == GridState.SELECTING_MONITOR:
            monitors = get_all_monitors()
            if 1 <= key <= len(monitors):
                # User selected a monitor - completely reset state first
                self.selected_monitor = monitors[key - 1]
                self.grid_model = None  # Clear any existing grid model
                self.monitor_selection_mode = False
                self.input_handler.set_state(GridState.HIDDEN)
                # Hide monitor selection overlay
                self.overlay.hide()
                # Now show the actual grid with the selected monitor
                self._show_grid()
                # Move mouse to center of initial grid
                if self.grid_model:
                    current = self.grid_model.get_current_region()
                    center_x, center_y = current.center()
                    self.virtual_pointer.move_to(center_x, center_y, sync=True)
            return
        
        # Normal grid navigation
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
        
        # Keep grid visible - don't hide after click
    
    def _on_shift_enter(self):
        """Handle Shift+Enter (right click)."""
        if not self.grid_model:
            return
        
        current_region = self.grid_model.get_current_region()
        center_x, center_y = current_region.center()
        
        self.virtual_pointer.move_to(center_x, center_y, sync=True)
        self.virtual_pointer.click('right')
        self.sound_manager.play_click()
        
        # Keep grid visible - don't hide after click
    
    def _on_space(self):
        """Handle Space (move pointer only)."""
        if not self.grid_model:
            return
        
        current_region = self.grid_model.get_current_region()
        center_x, center_y = current_region.center()
        
        self.virtual_pointer.move_to(center_x, center_y, sync=True)
        
        # Keep grid visible - don't hide after move
    
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
    
    def _on_pause(self):
        """Handle pause (hide overlay and track visibility state)."""
        # Store whether overlay was visible before pausing
        self._overlay_was_visible_before_pause = self.overlay.is_visible()
        self.overlay.hide()
    
    def _on_resume(self):
        """Handle resume (restore overlay if it was visible before pause)."""
        if self._overlay_was_visible_before_pause:
            # Restore overlay visibility
            if self.grid_model:
                self.overlay.set_grid_model(self.grid_model)
                self.overlay.update_display()
            self.overlay.show()
            self._overlay_was_visible_before_pause = False  # Reset flag
    
    def run(self):
        """Main application loop."""
        print("Numpad Grid Mouse started")
        print("Press Ctrl+Shift+/ to toggle grid")
        print("Press Esc or Ctrl+Shift+/ to reset to full screen grid (when grid is visible)")
        print("Press Esc to exit (when grid is hidden)")
        
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
        elif action == 'reset_to_top':
            self._on_reset_to_top()
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
        elif action == 'pause':
            self._on_pause()
        elif action == 'resume':
            self._on_resume()
    
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
