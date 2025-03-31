"""
Resources package for SuShe NG.

This package contains all resources used by the application such as icons,
stylesheets, and other static assets.
"""

import os
import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource file.
    
    This function handles both development and frozen (packaged) environments.
    
    Args:
        relative_path: The path relative to the resources directory
        
    Returns:
        The absolute path to the resource file
    """
    # Determine if the application is running from a frozen executable
    if getattr(sys, 'frozen', False):
        # If we're running from a bundled executable
        # _MEIPASS is provided by PyInstaller
        if hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
        else:
            # Fallback to the executable directory
            base_path = Path(sys.executable).parent
    else:
        # If we're running in development mode
        base_path = Path(__file__).parent.parent
    
    # Join the base path with the resources directory and the relative path
    return str(base_path / 'resources' / relative_path)


def resource_exists(relative_path: str) -> bool:
    """
    Check if a resource file exists.
    
    Args:
        relative_path: The path relative to the resources directory
        
    Returns:
        True if the resource exists, False otherwise
    """
    return os.path.exists(get_resource_path(relative_path))