"""
Configuration utilities for SuShe NG.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import traceback

from PyQt6.QtCore import QSettings

from metadata import APP_NAME, ORG_NAME, ORG_DOMAIN
from utils.logging_utils import get_module_logger

# Get module logger
log = get_module_logger()


class Config:
    """
    Configuration manager for SuShe NG.
    
    This class provides an interface for reading and writing 
    application configuration.
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        log.debug("Initializing Config manager")
        # Set up QSettings with organization and application information
        self.settings = QSettings(ORG_NAME, APP_NAME)
        log.debug(f"QSettings created with org: {ORG_NAME}, app: {APP_NAME}")
        
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
        log.debug("Configuration defaults set")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key (can be nested using '/' separator)
            default: The default value to return if the key doesn't exist
            
        Returns:
            The configuration value, or the default if not found
        """
        value = self.settings.value(key, default)
        log.debug(f"Config get: {key} = {value}")
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key (can be nested using '/' separator)
            value: The value to set
        """
        log.debug(f"Config set: {key} = {value}")
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
                log.warning(f"No default value for config key: {key_path}")
                return None
        
        log.debug(f"Config default: {key_path} = {current}")
        return current
    
    def add_recent_file(self, filepath: str, max_entries: int = 10) -> None:
        """
        Add a file to the recent files list.
        
        Args:
            filepath: The path to the file
            max_entries: The maximum number of recent files to store
        """
        log.debug(f"Adding recent file: {filepath}")
        recent_files = self.get("recent_files", [])
        
        # Make sure it's a list
        if not isinstance(recent_files, list):
            log.warning("Recent files not a list, resetting")
            recent_files = []
        
        # Remove the file if it already exists in the list
        if filepath in recent_files:
            log.debug("File already in recent files, moving to top")
            recent_files.remove(filepath)
        
        # Add the file to the front of the list
        recent_files.insert(0, filepath)
        
        # Trim the list to the maximum number of entries
        if len(recent_files) > max_entries:
            log.debug(f"Trimming recent files list to {max_entries} entries")
            recent_files = recent_files[:max_entries]
        
        # Save the updated list
        self.set("recent_files", recent_files)
        log.debug(f"Recent files updated, count: {len(recent_files)}")
    
    def get_recent_files(self) -> list:
        """
        Get the list of recent files.
        
        Returns:
            A list of file paths
        """
        log.debug("Getting recent files")
        recent_files = self.get("recent_files", [])
        
        # Make sure it's a list
        if not isinstance(recent_files, list):
            log.warning("Recent files not a list, returning empty list")
            return []
        
        # Filter out files that no longer exist
        valid_files = []
        for f in recent_files:
            if os.path.exists(f):
                valid_files.append(f)
            else:
                log.debug(f"Recent file no longer exists: {f}")
        
        if len(valid_files) != len(recent_files):
            log.debug(f"Filtered {len(recent_files) - len(valid_files)} non-existent files")
            # If we filtered out files, update the stored list
            self.set("recent_files", valid_files)
        
        log.debug(f"Returning {len(valid_files)} recent files")
        return valid_files
    
    def clear_recent_files(self) -> None:
        """Clear the list of recent files."""
        log.info("Clearing recent files list")
        self.set("recent_files", [])
    
    def export_to_json(self, filepath: str) -> bool:
        """
        Export the entire configuration to a JSON file.
        
        Args:
            filepath: Path to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        log.info(f"Exporting configuration to {filepath}")
        try:
            # Create a dictionary to store all settings
            settings_dict = {}
            
            # Iterate through all keys
            for key in self.settings.allKeys():
                value = self.get(key)
                settings_dict[key] = value
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, indent=2)
            
            log.info("Configuration exported successfully")
            return True
        except Exception as e:
            log.error(f"Error exporting configuration: {e}")
            log.debug(traceback.format_exc())
            return False
    
    def import_from_json(self, filepath: str) -> bool:
        """
        Import configuration from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        log.info(f"Importing configuration from {filepath}")
        try:
            # Read the JSON file
            with open(filepath, 'r', encoding='utf-8') as f:
                settings_dict = json.load(f)
            
            # Apply each setting
            for key, value in settings_dict.items():
                self.set(key, value)
            
            # Sync to ensure all values are saved
            self.settings.sync()
            
            log.info(f"Imported {len(settings_dict)} configuration values")
            return True
        except Exception as e:
            log.error(f"Error importing configuration: {e}")
            log.debug(traceback.format_exc())
            return False
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to their default values."""
        log.info("Resetting configuration to defaults")
        # Clear the entire settings
        self.settings.clear()
        
        # Apply defaults
        self._apply_defaults()
        
        # Sync to ensure all values are saved
        self.settings.sync()
        log.info("Configuration reset complete")
    
    def _apply_defaults(self) -> None:
        """Apply default values to the settings."""
        log.debug("Applying default configuration values")
        
        def apply_dict(prefix, d):
            for key, value in d.items():
                full_key = f"{prefix}/{key}" if prefix else key
                if isinstance(value, dict):
                    apply_dict(full_key, value)
                else:
                    self.set(full_key, value)
        
        apply_dict("", self.defaults)