"""
Test that the main application can start without errors.
This is a quick smoke test.
"""
import sys
import time
import threading

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from grid_model import GridModel, Region
        from overlay import OverlayWindow
        from input_handler import InputHandler, GridState
        from virtual_pointer import VirtualPointer
        from sound_manager import SoundManager
        from monitor_utils import get_monitor_containing_cursor
        from config import Config
        from main import NumpadGridMouse
        print("[OK] All imports successful")
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """Test that the app can be created."""
    print("\nTesting app creation...")
    try:
        from main import NumpadGridMouse
        app = NumpadGridMouse()
        print("[OK] App created successfully")
        
        # Test that components are initialized
        assert app.config is not None, "Config not initialized"
        assert app.overlay is not None, "Overlay not initialized"
        assert app.input_handler is not None, "Input handler not initialized"
        assert app.virtual_pointer is not None, "Virtual pointer not initialized"
        assert app.sound_manager is not None, "Sound manager not initialized"
        print("[OK] All components initialized")
        
        # Clean up
        app.shutdown()
        print("[OK] App shutdown successful")
        return True
    except Exception as e:
        print(f"[FAIL] App creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hotkey_format():
    """Test that hotkey format is valid."""
    print("\nTesting hotkey format...")
    try:
        import keyboard
        from config import Config
        
        config = Config()
        hotkey = config.get('hotkeys', 'toggle')
        print(f"Hotkey from config: '{hotkey}'")
        
        # Try to register the hotkey (will fail if format is wrong)
        try:
            keyboard.add_hotkey(hotkey, lambda: None)
            print(f"[OK] Hotkey '{hotkey}' is valid")
            keyboard.unhook_all()
            return True
        except Exception as e:
            print(f"[FAIL] Hotkey '{hotkey}' is invalid: {e}")
            # Try alternative format
            if '/' in hotkey:
                alt_hotkey = hotkey.replace('/', 'slash')
                try:
                    keyboard.add_hotkey(alt_hotkey, lambda: None)
                    print(f"[INFO] Alternative format '{alt_hotkey}' works")
                    keyboard.unhook_all()
                except:
                    pass
            return False
    except Exception as e:
        print(f"[FAIL] Hotkey test error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Startup Tests")
    print("=" * 60)
    
    success = True
    success &= test_imports()
    success &= test_app_creation()
    success &= test_hotkey_format()
    
    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] All startup tests passed!")
        sys.exit(0)
    else:
        print("[FAILURE] Some startup tests failed!")
        sys.exit(1)
