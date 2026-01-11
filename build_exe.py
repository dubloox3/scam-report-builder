"""
Build script for creating Scam Report Builder EXE using PyInstaller
Run: python build_exe.py
"""

import PyInstaller.__main__
import sys
import os
from pathlib import Path

def build_exe():
    """Build the standalone Windows EXE"""
    
    print("Building Scam Report Builder EXE...")
    print("=" * 50)
    
    # PyInstaller arguments
    args = [
        'main.py',                          # Main script
        '--name=Scam-Report-Builder',       # EXE name
        '--onefile',                        # Single EXE file
        '--windowed',                       # No console window (GUI app)
        '--clean',                          # Clean cache before building
        
        # Include data files if needed (images, etc.)
        # '--add-data=path/to/data;data',
        
        # Hidden imports (PyInstaller sometimes misses these)
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=odfpy',
        '--hidden-import=dateutil',
        '--hidden-import=dateutil.parser',
        
        # Collect all submodules
        '--collect-all=PySide6',
        '--collect-all=PIL',
        '--collect-all=odfpy',
        
        # Icon (optional - add if you have an icon file)
        # '--icon=icon.ico',
        
        # Additional paths
        '--paths=.',
        
        # Exclude unnecessary modules to reduce size
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=scipy',
    ]
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 50)
        print("Build completed successfully!")
        print(f"EXE location: dist/Scam-Report-Builder.exe")
        print("\nNote: Windows may show a security warning on first run.")
        print("This is normal for unsigned executables.")
    except Exception as e:
        print(f"\nBuild failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed.")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)
    
    build_exe()
