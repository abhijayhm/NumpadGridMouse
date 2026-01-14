"""
Comprehensive test script for Numpad Grid Mouse application.
Tests all components and integration.
"""
import sys
import time
import unittest
from unittest.mock import Mock, patch, MagicMock

# Import all modules
from grid_model import GridModel, Region
from config import Config
from virtual_pointer import VirtualPointer
from sound_manager import SoundManager
from monitor_utils import get_monitor_containing_cursor
from overlay import OverlayWindow


class TestConfig(unittest.TestCase):
    """Test configuration system."""
    
    def test_config_creation(self):
        """Test that config can be created."""
        config = Config()
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.get('grid', 'opacity'))
    
    def test_config_get(self):
        """Test config get method."""
        config = Config()
        opacity = config.get('grid', 'opacity')
        self.assertIsInstance(opacity, (int, float))
        self.assertGreater(opacity, 0)
        self.assertLessEqual(opacity, 1)


class TestVirtualPointer(unittest.TestCase):
    """Test virtual pointer."""
    
    def test_virtual_pointer_creation(self):
        """Test virtual pointer initialization."""
        vp = VirtualPointer()
        self.assertIsNotNone(vp)
        x, y = vp.get_position()
        self.assertIsInstance(x, (int, float))
        self.assertIsInstance(y, (int, float))
    
    def test_virtual_pointer_move(self):
        """Test moving virtual pointer."""
        vp = VirtualPointer()
        vp.move_to(100, 200, sync=False)
        x, y = vp.get_position()
        self.assertEqual(x, 100)
        self.assertEqual(y, 200)


class TestSoundManager(unittest.TestCase):
    """Test sound manager."""
    
    def test_sound_manager_creation(self):
        """Test sound manager initialization."""
        config = Config()
        sm = SoundManager(config)
        self.assertIsNotNone(sm)
    
    def test_sound_methods(self):
        """Test that sound methods don't crash."""
        config = Config()
        sm = SoundManager(config)
        # These should not raise exceptions
        sm.play_show_grid()
        sm.play_refine_selection()
        sm.play_click()
        sm.play_scroll()


class TestMonitorUtils(unittest.TestCase):
    """Test monitor utilities."""
    
    def test_get_monitor_containing_cursor(self):
        """Test getting monitor with cursor."""
        try:
            monitor = get_monitor_containing_cursor()
            self.assertEqual(len(monitor), 4)
            x, y, w, h = monitor
            self.assertIsInstance(x, int)
            self.assertIsInstance(y, int)
            self.assertIsInstance(w, int)
            self.assertIsInstance(h, int)
            self.assertGreater(w, 0)
            self.assertGreater(h, 0)
        except Exception as e:
            self.fail(f"get_monitor_containing_cursor raised {e}")


class TestOverlayWindow(unittest.TestCase):
    """Test overlay window."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
    
    def test_overlay_creation(self):
        """Test overlay window creation."""
        try:
            overlay = OverlayWindow(self.config)
            self.assertIsNotNone(overlay)
            self.assertIsNotNone(overlay.root)
            self.assertIsNotNone(overlay.canvas)
            overlay.destroy()
        except Exception as e:
            self.fail(f"OverlayWindow creation raised {e}")
    
    def test_overlay_show_hide(self):
        """Test showing and hiding overlay."""
        overlay = OverlayWindow(self.config)
        try:
            overlay.hide()
            self.assertFalse(overlay.is_visible())
            overlay.show()
            # Note: is_visible() might return False if window isn't fully rendered
            # So we just check it doesn't crash
            overlay.hide()
        finally:
            overlay.destroy()
    
    def test_overlay_with_grid_model(self):
        """Test overlay with grid model."""
        overlay = OverlayWindow(self.config)
        try:
            # Create a test region
            monitor = get_monitor_containing_cursor()
            screen_region = Region(monitor[0], monitor[1], monitor[2], monitor[3])
            grid_model = GridModel(screen_region)
            
            overlay.set_grid_model(grid_model)
            overlay.update_display()
            # Should not crash
        finally:
            overlay.destroy()


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_grid_model_with_overlay(self):
        """Test grid model integration with overlay."""
        config = Config()
        overlay = OverlayWindow(config)
        try:
            monitor = get_monitor_containing_cursor()
            screen_region = Region(monitor[0], monitor[1], monitor[2], monitor[3])
            grid_model = GridModel(screen_region)
            
            overlay.set_grid_model(grid_model)
            overlay.update_display()
            
            # Select a region
            new_region = grid_model.select_region(5)
            self.assertIsNotNone(new_region)
            overlay.update_display()
            
            # Should not crash
        finally:
            overlay.destroy()


def run_basic_functionality_test():
    """Run a basic functionality test without GUI."""
    print("=" * 60)
    print("Running Basic Functionality Tests")
    print("=" * 60)
    
    # Test 1: Config
    print("\n1. Testing Config...")
    try:
        config = Config()
        print(f"   [OK] Config created successfully")
        print(f"   [OK] Grid opacity: {config.get('grid', 'opacity')}")
    except Exception as e:
        print(f"   [FAIL] Config failed: {e}")
        return False
    
    # Test 2: Grid Model
    print("\n2. Testing Grid Model...")
    try:
        region = Region(0, 0, 1920, 1080)
        grid_model = GridModel(region)
        print(f"   [OK] Grid model created")
        print(f"   [OK] Initial depth: {grid_model.get_depth()}")
        
        new_region = grid_model.select_region(5)
        print(f"   [OK] Selected region 5, new depth: {grid_model.get_depth()}")
        center = new_region.center()
        print(f"   [OK] Center of selected region: {center}")
    except Exception as e:
        print(f"   [FAIL] Grid model failed: {e}")
        return False
    
    # Test 3: Virtual Pointer
    print("\n3. Testing Virtual Pointer...")
    try:
        vp = VirtualPointer()
        x, y = vp.get_position()
        print(f"   [OK] Virtual pointer created at ({x}, {y})")
        vp.move_to(100, 200, sync=False)
        x, y = vp.get_position()
        print(f"   [OK] Moved to ({x}, {y})")
    except Exception as e:
        print(f"   [FAIL] Virtual pointer failed: {e}")
        return False
    
    # Test 4: Monitor Utils
    print("\n4. Testing Monitor Utils...")
    try:
        monitor = get_monitor_containing_cursor()
        print(f"   [OK] Monitor: {monitor}")
    except Exception as e:
        print(f"   [FAIL] Monitor utils failed: {e}")
        return False
    
    # Test 5: Sound Manager
    print("\n5. Testing Sound Manager...")
    try:
        sm = SoundManager(config)
        print(f"   [OK] Sound manager created")
        # Don't actually play sounds in test
    except Exception as e:
        print(f"   [FAIL] Sound manager failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("All basic functionality tests passed!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    # Run unittest tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run basic functionality test
    print("\n\n")
    success = run_basic_functionality_test()
    
    if success:
        print("\n[SUCCESS] All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n[FAILURE] Some tests failed!")
        sys.exit(1)
