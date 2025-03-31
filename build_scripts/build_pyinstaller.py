#!/usr/bin/env python3
"""
Build script for creating a standalone executable using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Import metadata from the project
sys.path.insert(0, str(PROJECT_ROOT))
from susheng.metadata import APP_NAME, APP_VERSION


def build_executable():
    """Build the executable using PyInstaller."""
    # Change to the project root directory
    os.chdir(PROJECT_ROOT)
    
    # Clean previous build files
    build_dir = PROJECT_ROOT / "build"
    dist_dir = PROJECT_ROOT / "dist"
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # Determine icon path
    if sys.platform == "win32":
        icon_path = PROJECT_ROOT / "susheng" / "resources" / "icons" / "susheng.ico"
    elif sys.platform == "darwin":
        icon_path = PROJECT_ROOT / "susheng" / "resources" / "icons" / "susheng.icns"
    else:
        icon_path = PROJECT_ROOT / "susheng" / "resources" / "icons" / "susheng.png"
    
    # Ensure icon path exists
    if not icon_path.exists():
        print(f"Warning: Icon file not found at {icon_path}")
        icon_path = None
    
    # Build the command
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onedir",
        "--windowed",
        "--clean",
        "--noconfirm",
    ]
    
    # Add icon if available
    if icon_path:
        cmd.extend(["--icon", str(icon_path)])
    
    # Add additional data files
    cmd.extend([
        "--add-data", f"susheng/resources/icons:susheng/resources/icons",
    ])
    
    # Add entry point
    cmd.append("susheng/main.py")
    
    # Run PyInstaller
    print("Building executable with PyInstaller...")
    subprocess.run(cmd, check=True)
    
    print(f"\nBuild completed successfully. Executable is in the 'dist/{APP_NAME}' directory.")


if __name__ == "__main__":
    build_executable()