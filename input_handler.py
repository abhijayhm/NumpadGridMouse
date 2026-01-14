"""
Input handling: hotkeys and state machine.
Manages keyboard input and state transitions.
"""
import keyboard
import pynput
from pynput import keyboard as pynput_keyboard
import threading
from typing import Callable, Optional
from enum import Enum
from config import Config


class GridState(Enum):
    """State machine for grid navigation."""
    HIDDEN = "hidden"
    VISIBLE = "visible"
    SELECTING = "selecting"


class InputHandler:
    """
    Handles all keyboard input and manages the state machine.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.state = GridState.HIDDEN
        self.hotkey_registered = False
        self.callbacks = {
            'on_toggle': None,
            'on_exit': None,
            'on_number': None,
            'on_enter': None,
            'on_ctrl_enter': None,
            'on_space': None,
            'on_backspace': None,
            'on_arrow': None,
        }
        self._hook_thread: Optional[threading.Thread] = None
        self._pynput_listener: Optional[pynput_keyboard.Listener] = None
        self._stop_hook = False
        self._pressed_keys = set()
    
    def register_callback(self, event: str, callback: Callable):
        """Register a callback for an input event."""
        if event in self.callbacks:
            self.callbacks[event] = callback
    
    def _on_toggle(self):
        """Handle toggle hotkey."""
        if self.callbacks['on_toggle']:
            self.callbacks['on_toggle']()
    
    def _on_exit(self):
        """Handle exit key."""
        if self.state == GridState.VISIBLE:
            if self.callbacks['on_exit']:
                self.callbacks['on_exit']()
    
    def _on_number(self, key: int):
        """Handle number key press (1-9)."""
        if self.state == GridState.VISIBLE:
            if self.callbacks['on_number']:
                self.callbacks['on_number'](key)
    
    def _on_enter(self):
        """Handle Enter key."""
        if self.state == GridState.VISIBLE:
            if self.callbacks['on_enter']:
                self.callbacks['on_enter']()
    
    def _on_ctrl_enter(self):
        """Handle Ctrl+Enter."""
        if self.state == GridState.VISIBLE:
            if self.callbacks['on_ctrl_enter']:
                self.callbacks['on_ctrl_enter']()
    
    def _on_space(self):
        """Handle Space key."""
        if self.state == GridState.VISIBLE:
            if self.callbacks['on_space']:
                self.callbacks['on_space']()
    
    def _on_backspace(self):
        """Handle Backspace key."""
        if self.state == GridState.VISIBLE:
            if self.callbacks['on_backspace']:
                self.callbacks['on_backspace']()
    
    def _on_arrow(self, direction: str):
        """Handle arrow key."""
        if self.state == GridState.VISIBLE:
            if self.callbacks['on_arrow']:
                self.callbacks['on_arrow'](direction)
    
    def _on_pynput_press(self, key):
        """Handle key press using pynput (for key suppression)."""
        self._pressed_keys.add(key)
        
        if self.state != GridState.VISIBLE:
            return True  # Don't suppress
        
        try:
            # Handle number keys
            if hasattr(key, 'char') and key.char and key.char.isdigit():
                num = int(key.char)
                if 1 <= num <= 9:
                    self._on_number(num)
                    return False  # Suppress key
            
            # Handle special keys
            if key == pynput_keyboard.Key.enter:
                ctrl_pressed = (pynput_keyboard.Key.ctrl_l in self._pressed_keys or 
                               pynput_keyboard.Key.ctrl_r in self._pressed_keys)
                if ctrl_pressed:
                    self._on_ctrl_enter()
                else:
                    self._on_enter()
                return False
            
            if key == pynput_keyboard.Key.space:
                self._on_space()
                return False
            
            if key == pynput_keyboard.Key.backspace:
                self._on_backspace()
                return False
            
            if key == pynput_keyboard.Key.up:
                self._on_arrow('up')
                return False
            
            if key == pynput_keyboard.Key.down:
                self._on_arrow('down')
                return False
            
            if key == pynput_keyboard.Key.left:
                self._on_arrow('left')
                return False
            
            if key == pynput_keyboard.Key.right:
                self._on_arrow('right')
                return False
            
            if key == pynput_keyboard.Key.esc:
                self._on_exit()
                return False
        except Exception:
            pass
        
        return True  # Don't suppress other keys
    
    def _on_pynput_release(self, key):
        """Handle key release using pynput."""
        self._pressed_keys.discard(key)
        return True
    
    def _hook_loop(self):
        """Main hook loop for capturing keyboard input."""
        # Register global hotkey using keyboard library
        toggle_hotkey = self.config.get('hotkeys', 'toggle')
        keyboard.add_hotkey(toggle_hotkey, self._on_toggle)
        
        # Start pynput listener for key suppression when grid is visible
        self._pynput_listener = pynput_keyboard.Listener(
            on_press=self._on_pynput_press,
            on_release=self._on_pynput_release
        )
        self._pynput_listener.start()
        
        # Keep thread alive
        while not self._stop_hook:
            keyboard.wait()
    
    def start(self):
        """Start the input handler."""
        if self._hook_thread is None or not self._hook_thread.is_alive():
            self._stop_hook = False
            self._hook_thread = threading.Thread(target=self._hook_loop, daemon=True)
            self._hook_thread.start()
    
    def stop(self):
        """Stop the input handler."""
        self._stop_hook = True
        keyboard.unhook_all()
        if self._pynput_listener:
            self._pynput_listener.stop()
    
    def set_state(self, state: GridState):
        """Update the state machine."""
        self.state = state
