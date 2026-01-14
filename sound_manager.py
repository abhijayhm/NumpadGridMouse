"""
Sound manager for accessibility cues.
Provides optional audio feedback for actions.
"""
import winsound
import threading
from config import Config
from typing import Optional


class SoundManager:
    """Manages sound cues for accessibility."""
    
    # Windows system sound frequencies (Hz)
    SOUNDS = {
        'show': 800,
        'refine': 600,
        'click': 1000,
        'scroll': 400,
    }
    
    def __init__(self, config: Config):
        self.config = config
        self.enabled = self.config.get('sounds', 'enabled')
    
    def _play_beep(self, frequency: int, duration: int = 100):
        """Play a beep sound."""
        if not self.enabled:
            return
        
        try:
            winsound.Beep(frequency, duration)
        except Exception as e:
            # Silently fail if sound can't play
            pass
    
    def play_show_grid(self):
        """Play sound when grid is shown."""
        if self.config.get('sounds', 'show_grid'):
            self._play_beep(self.SOUNDS['show'])
    
    def play_refine_selection(self):
        """Play sound when selection is refined."""
        if self.config.get('sounds', 'refine_selection'):
            self._play_beep(self.SOUNDS['refine'])
    
    def play_click(self):
        """Play sound when clicking."""
        if self.config.get('sounds', 'click'):
            self._play_beep(self.SOUNDS['click'], 50)
    
    def play_scroll(self):
        """Play sound when scrolling."""
        if self.config.get('sounds', 'scroll'):
            self._play_beep(self.SOUNDS['scroll'], 50)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable sounds."""
        self.enabled = enabled
        self.config.set('sounds', 'enabled', value=enabled)
