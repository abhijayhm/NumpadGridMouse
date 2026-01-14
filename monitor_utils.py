"""
Monitor utilities: multi-monitor support.
Handles getting monitor information and positioning overlay.
"""
import win32api
import win32con
from typing import List, Tuple
from grid_model import Region


def get_monitor_containing_point(x: int, y: int) -> Tuple[int, int, int, int]:
    """
    Get the monitor that contains the given point.
    Returns (x, y, width, height) of the monitor's work area.
    """
    monitor = win32api.MonitorFromPoint((x, y), win32con.MONITOR_DEFAULTTONEAREST)
    monitor_info = win32api.GetMonitorInfo(monitor)
    work_area = monitor_info['Work']
    return (work_area[0], work_area[1], work_area[2] - work_area[0], work_area[3] - work_area[1])


def get_monitor_containing_cursor() -> Tuple[int, int, int, int]:
    """Get the monitor containing the current cursor position."""
    cursor_pos = win32api.GetCursorPos()
    return get_monitor_containing_point(cursor_pos[0], cursor_pos[1])


def get_all_monitors() -> List[Tuple[int, int, int, int]]:
    """Get all monitors as (x, y, width, height) tuples using Work area (usable area excluding taskbar)."""
    monitors = []
    
    # EnumDisplayMonitors returns a list of (hMonitor, hdcMonitor, monitorRect) tuples
    monitor_list = win32api.EnumDisplayMonitors()
    
    for hMonitor, hdcMonitor, monitorRect in monitor_list:
        monitor_info = win32api.GetMonitorInfo(hMonitor)
        work_area = monitor_info['Work']  # Work area (excludes taskbar)
        monitors.append((work_area[0], work_area[1], work_area[2] - work_area[0], work_area[3] - work_area[1]))
    
    return monitors


def get_all_monitor_rects() -> List[Tuple[int, int, int, int]]:
    """Get all monitors' full rects (not work area) as (x, y, width, height) tuples for outline display."""
    monitors = []
    
    # EnumDisplayMonitors returns a list of (hMonitor, hdcMonitor, monitorRect) tuples
    monitor_list = win32api.EnumDisplayMonitors()
    
    for hMonitor, hdcMonitor, monitorRect in monitor_list:
        monitor_info = win32api.GetMonitorInfo(hMonitor)
        monitor_rect = monitor_info['Monitor']  # Full monitor rect
        x = monitor_rect[0]
        y = monitor_rect[1]
        width = monitor_rect[2] - monitor_rect[0]
        height = monitor_rect[3] - monitor_rect[1]
        monitors.append((x, y, width, height))
    
    return monitors


def get_primary_monitor() -> Tuple[int, int, int, int]:
    """
    Get the primary monitor (typically at 0,0 or the first monitor).
    Returns (x, y, width, height) of the primary monitor.
    """
    monitors = get_all_monitors()
    if not monitors:
        # Fallback to cursor monitor if no monitors found
        return get_monitor_containing_cursor()
    
    # Primary monitor is typically at (0, 0) or the first one
    # Try to find monitor at (0, 0) first
    for monitor in monitors:
        x, y, w, h = monitor
        if x == 0 and y == 0:
            return monitor
    
    # If no monitor at (0, 0), return the first monitor
    return monitors[0]


def get_virtual_desktop_bounds() -> Tuple[int, int, int, int]:
    """
    Get the bounding box of all monitors (virtual desktop).
    Returns (min_x, min_y, max_x, max_y) covering all monitors.
    Uses full monitor rects (not work areas) to cover entire desktop.
    """
    monitor_rects = get_all_monitor_rects()
    if not monitor_rects:
        # Fallback to primary monitor
        monitor = get_primary_monitor()
        x, y, w, h = monitor
        return (x, y, x + w, y + h)
    
    # Calculate bounding box using full monitor rects
    min_x = min(m[0] for m in monitor_rects)
    min_y = min(m[1] for m in monitor_rects)
    max_x = max(m[0] + m[2] for m in monitor_rects)
    max_y = max(m[1] + m[3] for m in monitor_rects)
    
    return (min_x, min_y, max_x, max_y)
