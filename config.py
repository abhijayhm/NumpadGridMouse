"""
Configuration system for Numpad Grid Mouse.
Stores user preferences in app data folder.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """Manages application configuration."""
    
    def __init__(self):
        self.app_data_dir = Path(os.getenv('APPDATA', '')) / 'NumpadGridMouse'
        self.config_file = self.app_data_dir / 'config.json'
        self.app_data_dir.mkdir(exist_ok=True)
        
        # Default configuration
        self.defaults = {
            'grid': {
                'line_thickness': 1,
                'font_size': 16,
                'opacity': 0.85,
                'border_color': '#00FF00',
                'text_color': '#FFFFFF',
                'background_color': '#000000',
                'high_contrast': False
            },
            'hud': {
                'enabled': True,
                'font_size': 14,
                'position': 'top_left',
                'text_color': '#FFFFFF',
                'background_color': '#00000080'
            },
            'sounds': {
                'enabled': True,
                'show_grid': True,
                'refine_selection': True,
                'click': True,
                'scroll': False
            },
            'behavior': {
                'max_depth': 0,  # 0 = unlimited
                'scroll_amount': 3,  # lines/pixels
                'scroll_scale': 10,  # multiplier for scroll strength
                'animation_duration': 0.1  # seconds
            },
            'hotkeys': {
                'toggle': 'ctrl+shift+/',
                'exit': 'esc'
            }
        }
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    config = self._merge_dicts(self.defaults, loaded)
                    return config
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
                return self.defaults.copy()
        else:
            self._save_config(self.defaults)
            return self.defaults.copy()
    
    def _merge_dicts(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, *keys):
        """Get nested config value using dot notation."""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def set(self, *keys, value):
        """Set nested config value using dot notation."""
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def save(self):
        """Explicitly save current configuration."""
        self._save_config(self.config)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self.defaults.copy()
        self._save_config(self.config)
