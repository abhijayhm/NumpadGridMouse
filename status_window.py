"""
Status window showing listener status and quick usage guide.
"""
import tkinter as tk
from tkinter import font, ttk
from typing import Optional
from config import Config


class StatusWindow:
    """
    Status window displaying listener status and usage guide.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.root: Optional[tk.Tk] = None
        self.status_label: Optional[tk.Label] = None
        self.scroll_scale_var: Optional[tk.DoubleVar] = None
        self.scroll_scale_label: Optional[tk.Label] = None
        self._listener_paused = False
        self._setup_window()
    
    def _setup_window(self):
        """Create and configure the status window."""
        self.root = tk.Tk()
        self.root.title("Numpad Grid Mouse - Status")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        # Configure window style
        self.root.configure(bg='#2b2b2b')
        
        # Configure scrollbar style first
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Vertical.TScrollbar",
                       background='#444444',
                       troughcolor='#2b2b2b',
                       borderwidth=0,
                       arrowcolor='#888888',
                       darkcolor='#444444',
                       lightcolor='#444444')
        
        # Create scrollable frame
        canvas = tk.Canvas(self.root, bg='#2b2b2b', highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        scrollable_frame = tk.Frame(canvas, bg='#2b2b2b')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create main frame inside scrollable frame
        main_frame = tk.Frame(scrollable_frame, bg='#2b2b2b', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_font = font.Font(size=18, weight='bold')
        title_label = tk.Label(
            main_frame,
            text="Numpad Grid Mouse",
            font=title_font,
            bg='#2b2b2b',
            fg='#ffffff'
        )
        title_label.pack(pady=(0, 20))
        
        # Status section
        status_frame = tk.Frame(main_frame, bg='#2b2b2b')
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        status_title = tk.Label(
            status_frame,
            text="Listener Status:",
            font=font.Font(size=12, weight='bold'),
            bg='#2b2b2b',
            fg='#cccccc'
        )
        status_title.pack(anchor='w')
        
        self.status_label = tk.Label(
            status_frame,
            text="Active",
            font=font.Font(size=14, weight='bold'),
            bg='#2b2b2b',
            fg='#00ff00'
        )
        self.status_label.pack(anchor='w', pady=(5, 0))
        
        # Separator
        separator = tk.Frame(main_frame, height=2, bg='#444444')
        separator.pack(fill=tk.X, pady=(0, 20))
        
        # Usage guide section
        guide_frame = tk.Frame(main_frame, bg='#2b2b2b')
        guide_frame.pack(fill=tk.X, pady=(0, 20))
        
        guide_title = tk.Label(
            guide_frame,
            text="Quick Guide:",
            font=font.Font(size=12, weight='bold'),
            bg='#2b2b2b',
            fg='#cccccc'
        )
        guide_title.pack(anchor='w', pady=(0, 10))
        
        # Guide steps
        guide_steps = [
            "1. Press Ctrl+Shift+/ to show grid",
            "2. Use numpad 1-9 to navigate",
            "3. Press Enter for left click",
            "4. Press Shift+Enter for right click",
            "5. Use ↑↓ arrow keys to scroll",
            "6. Press Esc to exit"
        ]
        
        guide_font = font.Font(size=11)
        for step in guide_steps:
            step_label = tk.Label(
                guide_frame,
                text=step,
                font=guide_font,
                bg='#2b2b2b',
                fg='#ffffff',
                anchor='w',
                justify='left'
            )
            step_label.pack(anchor='w', pady=3)
        
        # Separator
        separator2 = tk.Frame(main_frame, height=2, bg='#444444')
        separator2.pack(fill=tk.X, pady=(20, 20))
        
        # Scroll scale section
        scale_frame = tk.Frame(main_frame, bg='#2b2b2b')
        scale_frame.pack(fill=tk.X, pady=(0, 20))
        
        scale_title = tk.Label(
            scale_frame,
            text="Scroll Scale:",
            font=font.Font(size=12, weight='bold'),
            bg='#2b2b2b',
            fg='#cccccc'
        )
        scale_title.pack(anchor='w', pady=(0, 10))
        
        # Get current scroll scale from config
        current_scale = self.config.get('behavior', 'scroll_scale')
        if current_scale is None:
            current_scale = 10.0
        
        self.scroll_scale_var = tk.DoubleVar(value=float(current_scale))
        
        # Scale slider
        scale_slider = ttk.Scale(
            scale_frame,
            from_=1.0,
            to=50.0,
            orient=tk.HORIZONTAL,
            variable=self.scroll_scale_var,
            command=self._on_scale_change
        )
        scale_slider.pack(fill=tk.X, pady=(0, 5))
        
        # Scale value label
        self.scroll_scale_label = tk.Label(
            scale_frame,
            text=f"Current: {current_scale:.1f}x",
            font=font.Font(size=10),
            bg='#2b2b2b',
            fg='#ffffff'
        )
        self.scroll_scale_label.pack(anchor='w')
        
        # Additional info
        info_label = tk.Label(
            main_frame,
            text="Press Ctrl+Shift+. to pause/resume",
            font=font.Font(size=9),
            bg='#2b2b2b',
            fg='#888888',
            anchor='w'
        )
        info_label.pack(anchor='w', pady=(10, 0))
        
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _on_scale_change(self, value):
        """Handle scroll scale slider change."""
        scale_value = float(value)
        # Update config
        self.config.set('behavior', 'scroll_scale', value=scale_value)
        # Update label
        if self.scroll_scale_label:
            self.scroll_scale_label.config(text=f"Current: {scale_value:.1f}x")
    
    def update_status(self, paused: bool):
        """Update the listener status display."""
        self._listener_paused = paused
        if self.status_label:
            if paused:
                self.status_label.config(text="Paused", fg='#ff8800')
            else:
                self.status_label.config(text="Active", fg='#00ff00')
    
    def show(self):
        """Show the status window."""
        if self.root:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
    
    def hide(self):
        """Hide the status window."""
        if self.root:
            self.root.withdraw()
    
    def is_visible(self) -> bool:
        """Check if window is visible."""
        if not self.root:
            return False
        try:
            return self.root.winfo_viewable()
        except:
            return False
    
    def update(self):
        """Update the window (call in main loop)."""
        if self.root:
            try:
                self.root.update_idletasks()
                self.root.update()
            except:
                pass
    
    def destroy(self):
        """Destroy the status window."""
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
            self.root = None
