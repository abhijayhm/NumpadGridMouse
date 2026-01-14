"""
Setup script for Numpad Grid Mouse.
Can be used for creating installers or packaging.
"""
from setuptools import setup, find_packages

setup(
    name="numpad-grid-mouse",
    version="1.0.0",
    description="A keyboard-driven mouse control system using recursive 3×3 grids",
    author="Your Name",
    py_modules=[
        'main',
        'config',
        'grid_model',
        'overlay',
        'input_handler',
        'virtual_pointer',
        'sound_manager',
        'monitor_utils',
    ],
    install_requires=[
        'pynput>=1.7.6',
        'pyautogui>=0.9.54',
        'keyboard>=0.13.5',
        'pywin32>=306',
        'Pillow>=10.0.0',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'numpad-grid-mouse=main:main',
        ],
    },
)
