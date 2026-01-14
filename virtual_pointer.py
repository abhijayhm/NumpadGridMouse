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
        """Sync virtual pointer to current OS cursor position."""
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
        
        # Move to position and scroll
        pyautogui.moveTo(x, y)
        
        if dy != 0:
            pyautogui.scroll(dy, x=x, y=y)
        
        if dx != 0:
            # Horizontal scrolling requires win32api on Windows
            win32api.mouse_event(
                win32con.MOUSEEVENTF_HWHEEL,
                x, y, dx * 120, 0  # 120 is standard scroll unit
            )
