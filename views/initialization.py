"""
views/initialization.py

Initialization utilities for the application.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any

from PyQt6.QtWidgets import QMessageBox, QApplication

from utils.list_repository import ListRepository
from utils.config import Config


def initialize_repository(config: Config) -> ListRepository:
    """
    Initialize the list repository and handles repository setup.
    
    Args:
        config: Application configuration
        
    Returns:
        The initialized ListRepository instance
    """
    # Create the repository
    repository = ListRepository()
    
    # Check if this is the first run
    first_run = config.get("repository/initialized", False) is False
    
    if first_run:
        # Show welcome message
        welcome_message = (
            "Welcome to SuShe NG!\n\n"
            "We've created a dedicated storage area for your album lists. "
            "Would you like to migrate your existing lists to this new location?\n\n"
            "This will copy your lists into the application's storage, making them "
            "easier to manage."
        )
        
        # Skip migration dialog when testing with no app instance
        app = QApplication.instance()
        if app:
            reply = QMessageBox.question(
                None, "Welcome to SuShe NG",
                welcome_message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                migrate_existing_lists(config, repository)
        
        # Mark as initialized
        config.set("repository/initialized", True)
        config.set("repository/path", repository.base_dir)
    
    return repository


def migrate_existing_lists(config: Config, repository: ListRepository) -> None:
    """
    Migrate existing lists to the repository.
    
    Args:
        config: Application configuration
        repository: The list repository
    """
    # Get recent files from config
    recent_files = config.get_recent_files()
    
    # Import each file
    imported_count = 0
    for file_path in recent_files:
        try:
            # Skip non-existent files
            if not os.path.exists(file_path):
                continue
            
            # Import the file
            new_path = repository.import_external_list(file_path)
            if new_path:
                imported_count += 1
        except Exception as e:
            print(f"Error importing {file_path}: {e}")
    
    # Show result
    if imported_count > 0:
        app = QApplication.instance()
        if app:
            QMessageBox.information(
                None, "Import Complete",
                f"Successfully imported {imported_count} list(s) into the repository."
            )