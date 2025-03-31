"""
Configuration utilities for SuShe NG.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt6.QtCore import QSettings

from metadata import APP_NAME, ORG_NAME, ORG_DOMAIN


class Config:
    """
    Configuration manager for SuShe NG.
    
    This class provides an interface for reading and writing 
    application configuration.
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        # Set up QSettings with organization and application information
        self.settings = QSettings(ORG_NAME, APP_NAME)
        
        # Default configuration values
        self.defaults = {
            "window": {
                "width": 900,
                "height": 700,
                "maximized": False,
                "position_x": None,
                "position_y": None
            },
            "theme": {
                "name": "spotify"
            },
            "recent_files": []
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key (can be nested using '/' separator)
            default: The default value to return if the key doesn't exist
            
        Returns:
            The configuration value, or the default if not found
        """
        return self.settings.value(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key (can be nested using '/' separator)
            value: The value to set
        """
        self.settings.setValue(key, value)
        self.settings.sync()
    
    def get_default(self, key_path: str) -> Any:
        """
        Get the default value for a configuration key.
        
        Args:
            key_path: The path to the configuration key (e.g., 'window/width')
            
        Returns:
            The default value, or None if the path doesn't exist
        """
        parts = key_path.split('/')
        current = self.defaults
        
        for part in parts:
            if part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def reset_to_defaults(self) -> None:
        """Reset all configuration values to their defaults."""
        self.settings.clear()
        self._set_defaults_recursive(self.defaults)
    
    def _set_defaults_recursive(self, defaults_dict: Dict[str, Any], 
                               prefix: str = "") -> None:
        """
        Recursively set default values.
        
        Args:
            defaults_dict: The dictionary of default values
            prefix: The prefix for the key path
        """
        for key, value in defaults_dict.items():
            full_key = f"{prefix}/{key}" if prefix else key
            
            if isinstance(value, dict):
                self._set_defaults_recursive(value, full_key)
            else:
                self.set(full_key, value)
    
    def add_recent_file(self, filepath: str, max_entries: int = 10) -> None:
        """
        Add a file to the recent files list.
        
        Args:
            filepath: The path to the file
            max_entries: The maximum number of recent files to store
        """
        recent_files = self.get("recent_files", [])
        
        # Make sure it's a list
        if not isinstance(recent_files, list):
            recent_files = []
        
        # Remove the file if it already exists in the list
        if filepath in recent_files:
            recent_files.remove(filepath)
        
        # Add the file to the front of the list
        recent_files.insert(0, filepath)
        
        # Trim the list to the maximum number of entries
        recent_files = recent_files[:max_entries]
        
        # Save the updated list
        self.set("recent_files", recent_files)
    
    def get_recent_files(self) -> list:
        """
        Get the list of recent files.
        
        Returns:
            A list of file paths
        """
        recent_files = self.get("recent_files", [])
        
        # Make sure it's a list
        if not isinstance(recent_files, list):
            return []
        
        # Filter out files that no longer exist
        return [f for f in recent_files if os.path.exists(f)]