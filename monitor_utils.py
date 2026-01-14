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
    Returns (x, y, width, height) of the monitor.
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
    """Get all monitors as (x, y, width, height) tuples."""
    monitors = []
    
    def enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
        monitor_info = win32api.GetMonitorInfo(hMonitor)
        work_area = monitor_info['Work']
        monitors.append((work_area[0], work_area[1], work_area[2] - work_area[0], work_area[3] - work_area[1]))
        return True
    
    win32api.EnumDisplayMonitors(None, None, enum_proc, None)
    return monitors
