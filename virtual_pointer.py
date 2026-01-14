"""
Virtual pointer abstraction and OS mouse interface.
Manages the virtual pointer position and syncs to real OS cursor on actions.
"""
import pyautogui
import win32api
import win32con
from typing import Tuple, Optional


class VirtualPointer:
    """
    Manages a virtual pointer position that only syncs to OS cursor
    when an action (click, scroll) occurs.
    """
    
    def __init__(self):
        self.virtual_x: Optional[int] = None
        self.virtual_y: Optional[int] = None
        self._sync_to_os()
    
    def _sync_to_os(self):
        """Sync virtual pointer to current OS cursor position using native Windows API."""
        if self.virtual_x is not None and self.virtual_y is not None:
            # Move OS cursor to virtual pointer position using native Windows API
            try:
                win32api.SetCursorPos((int(self.virtual_x), int(self.virtual_y)))
            except Exception as e:
                # Fallback to pyautogui if win32api fails
                pyautogui.moveTo(self.virtual_x, self.virtual_y)
        else:
            # Initialize from current OS cursor position
            x, y = pyautogui.position()
            self.virtual_x = x
            self.virtual_y = y
    
    def move_to(self, x: int, y: int, sync: bool = False):
        """
        Move virtual pointer to position.
        
        Args:
            x, y: Target coordinates
            sync: If True, also move OS cursor immediately
        """
        self.virtual_x = x
        self.virtual_y = y
        
        if sync:
            self._sync_to_os()
    
    def get_position(self) -> Tuple[int, int]:
        """Get current virtual pointer position."""
        if self.virtual_x is None or self.virtual_y is None:
            self._sync_to_os()
        return (self.virtual_x, self.virtual_y)
    
    def click(self, button: str = 'left', sync_before: bool = True):
        """
        Perform a click at virtual pointer position.
        
        Args:
            button: 'left' or 'right'
            sync_before: If True, sync OS cursor before clicking
        """
        if sync_before:
            self._sync_to_os()
        
        x, y = self.get_position()
        
        if button == 'left':
            pyautogui.click(x, y)
        elif button == 'right':
            pyautogui.rightClick(x, y)
    
    def scroll(self, dx: int, dy: int, sync_before: bool = True):
        """
        Perform scrolling at virtual pointer position.
        
        Args:
            dx: Horizontal scroll amount (positive = right, negative = left)
            dy: Vertical scroll amount (positive = up, negative = down)
            sync_before: If True, sync OS cursor before scrolling
        """
        if sync_before:
            self._sync_to_os()
        
        x, y = self.get_position()
        
        # Move to position
        pyautogui.moveTo(x, y)
        
        # Convert to integers and handle large scroll values
        # pyautogui.scroll expects integer values, and Windows API has limits
        # Break large scrolls into multiple smaller scrolls
        max_scroll_per_call = 120  # Standard Windows scroll unit
        
        if dy != 0:
            dy_int = int(round(dy))
            # Break into chunks if too large
            if abs(dy_int) > max_scroll_per_call:
                # Calculate number of scroll calls needed
                num_scrolls = abs(dy_int) // max_scroll_per_call
                remainder = abs(dy_int) % max_scroll_per_call
                direction = 1 if dy_int > 0 else -1
                
                # Perform multiple scrolls
                for _ in range(num_scrolls):
                    pyautogui.scroll(direction * max_scroll_per_call, x=x, y=y)
                
                # Perform remainder scroll if any
                if remainder > 0:
                    pyautogui.scroll(direction * remainder, x=x, y=y)
            else:
                pyautogui.scroll(dy_int, x=x, y=y)
        
        if dx != 0:
            dx_int = int(round(dx))
            # Convert to Windows scroll units (120 per unit)
            scroll_units = dx_int * 120
            # Break into chunks if too large (Windows limit is typically 32767)
            max_wheel_delta = 32767
            
            if abs(scroll_units) > max_wheel_delta:
                # Calculate number of scroll calls needed
                num_scrolls = abs(scroll_units) // max_wheel_delta
                remainder = abs(scroll_units) % max_wheel_delta
                direction = 1 if scroll_units > 0 else -1
                
                # Perform multiple scrolls
                for _ in range(num_scrolls):
                    win32api.mouse_event(
                        win32con.MOUSEEVENTF_HWHEEL,
                        x, y, direction * max_wheel_delta, 0
                    )
                
                # Perform remainder scroll if any
                if remainder > 0:
                    win32api.mouse_event(
                        win32con.MOUSEEVENTF_HWHEEL,
                        x, y, direction * remainder, 0
                    )
            else:
                # Horizontal scrolling requires win32api on Windows
                win32api.mouse_event(
                    win32con.MOUSEEVENTF_HWHEEL,
                    x, y, scroll_units, 0
                )
