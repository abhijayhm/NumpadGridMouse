"""
Grid model: handles region math and recursion stack.
Manages the 3×3 grid subdivision and navigation.
"""
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class Region:
    """Represents a rectangular region on screen."""
    x: int
    y: int
    width: int
    height: int
    
    def center(self) -> Tuple[int, int]:
        """Get center point of region."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def subdivide(self, row: int, col: int) -> 'Region':
        """
        Subdivide region into 3×3 grid and return the specified cell.
        Row and col are 0-indexed (0-2).
        """
        cell_width = self.width // 3
        cell_height = self.height // 3
        
        x = self.x + col * cell_width
        y = self.y + row * cell_height
        
        # Handle remainder pixels by adding to last cells
        if col == 2:
            cell_width = self.width - 2 * (self.width // 3)
        if row == 2:
            cell_height = self.height - 2 * (self.height // 3)
        
        return Region(x, y, cell_width, cell_height)
    
    def bounds(self) -> Tuple[int, int, int, int]:
        """Return (x, y, width, height) tuple."""
        return (self.x, self.y, self.width, self.height)


class GridModel:
    """
    Manages the recursive grid navigation state.
    Maps numpad keys (1-9) to grid positions.
    """
    
    # Numpad to (row, col) mapping
    # Visual layout:
    #   7 8 9
    #   4 5 6
    #   1 2 3
    NUMPAD_MAP = {
        1: (2, 0),  # bottom-left
        2: (2, 1),  # bottom-center
        3: (2, 2),  # bottom-right
        4: (1, 0),  # middle-left
        5: (1, 1),  # middle-center
        6: (1, 2),  # middle-right
        7: (0, 0),  # top-left
        8: (0, 1),  # top-center
        9: (0, 2),  # top-right
    }
    
    def __init__(self, screen_region: Region, max_depth: int = 0):
        """
        Initialize grid model.
        
        Args:
            screen_region: Initial region (typically full screen or monitor)
            max_depth: Maximum recursion depth (0 = unlimited)
        """
        self.max_depth = max_depth
        self.stack: List[Region] = [screen_region]
        self.current_region = screen_region
    
    def select_region(self, numpad_key: int) -> Optional[Region]:
        """
        Select a region using numpad key (1-9).
        Returns the new current region, or None if selection failed.
        """
        if numpad_key not in self.NUMPAD_MAP:
            return None
        
        row, col = self.NUMPAD_MAP[numpad_key]
        new_region = self.current_region.subdivide(row, col)
        
        # Check depth limit - max_depth is the maximum depth we can reach
        # depth = len(stack) - 1, so after adding we'd have depth = len(stack)
        # We should prevent if the new depth would exceed max_depth
        if self.max_depth > 0 and len(self.stack) > self.max_depth:
            return None
        
        self.stack.append(new_region)
        self.current_region = new_region
        return new_region
    
    def go_up(self) -> Optional[Region]:
        """
        Go up one grid level.
        Returns the new current region, or None if already at root.
        """
        if len(self.stack) <= 1:
            return None
        
        self.stack.pop()
        self.current_region = self.stack[-1]
        return self.current_region
    
    def get_depth(self) -> int:
        """Get current recursion depth (0 = root level)."""
        return len(self.stack) - 1
    
    def get_current_region(self) -> Region:
        """Get current active region."""
        return self.current_region
    
    def reset(self, screen_region: Region):
        """Reset to initial state with new screen region."""
        self.stack = [screen_region]
        self.current_region = screen_region
    
    def get_all_regions(self) -> List[Region]:
        """Get all regions in the current grid (for visualization)."""
        if len(self.stack) == 1:
            # At root, return 3×3 subdivision
            regions = []
            for row in range(3):
                for col in range(3):
                    regions.append(self.current_region.subdivide(row, col))
            return regions
        else:
            # At deeper level, return 3×3 of current region
            regions = []
            for row in range(3):
                for col in range(3):
                    regions.append(self.current_region.subdivide(row, col))
            return regions
