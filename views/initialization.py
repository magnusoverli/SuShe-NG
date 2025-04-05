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
from utils.logging_utils import get_module_logger

# Get logger for this module
log = get_module_logger()


def initialize_repository(config: Config) -> ListRepository:
    """
    Initialize the list repository and handles repository setup.
    
    Args:
        config: Application configuration
        
    Returns:
        The initialized ListRepository instance
    """
    # Create the repository
    log.debug("Initializing list repository")
    repository = ListRepository()
    
    # Check if this is the first run
    first_run = config.get("repository/initialized", False) is False
    
    if first_run:
        log.info("First run detected, showing welcome message")
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
            log.debug("Showing migration dialog")
            reply = QMessageBox.question(
                None, "Welcome to SuShe NG",
                welcome_message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                log.info("User chose to migrate existing lists")
                migrate_existing_lists(config, repository)
            else:
                log.info("User declined migration of existing lists")
        else:
            log.warning("No QApplication instance, skipping migration dialog")
        
        # Mark as initialized
        config.set("repository/initialized", True)
        config.set("repository/path", repository.base_dir)
        log.info(f"Repository initialized at: {repository.base_dir}")
    else:
        log.debug("Repository already initialized")
    
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
    log.info(f"Attempting to migrate {len(recent_files)} recent files")
    
    # Import each file
    imported_count = 0
    for file_path in recent_files:
        try:
            # Skip non-existent files
            if not os.path.exists(file_path):
                log.warning(f"File not found, skipping: {file_path}")
                continue
            
            log.debug(f"Importing file: {file_path}")
            # Import the file
            new_path = repository.import_external_list(file_path)
            if new_path:
                imported_count += 1
                log.info(f"Successfully imported: {file_path} → {new_path}")
        except Exception as e:
            log.error(f"Error importing {file_path}: {e}")
            import traceback
            log.debug(traceback.format_exc())
    
    # Show result
    if imported_count > 0:
        log.info(f"Migration complete. Imported {imported_count} list(s)")
        app = QApplication.instance()
        if app:
            QMessageBox.information(
                None, "Import Complete",
                f"Successfully imported {imported_count} list(s) into the repository."
            )
    else:
        log.warning("No files were imported during migration")