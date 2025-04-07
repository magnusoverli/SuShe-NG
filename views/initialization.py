"""
views/initialization.py

Initialization utilities for the application.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any

from PyQt6.QtWidgets import QMessageBox, QApplication

from utils.simple_collection_manager import SimpleCollectionManager  # Updated import
from utils.config import Config
from utils.logging_utils import get_module_logger

# Get logger for this module
log = get_module_logger()


def initialize_repository(config: Config) -> SimpleCollectionManager:  # Updated return type
    """
    Initialize the collection manager and handles setup.
    
    Args:
        config: Application configuration
        
    Returns:
        The initialized SimpleCollectionManager instance
    """
    # Create the collection manager
    log.debug("Initializing collection manager")
    collection_manager = SimpleCollectionManager()  # Updated class
    
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
                migrate_existing_lists(config, collection_manager)
            else:
                log.info("User declined migration of existing lists")
        else:
            log.warning("No QApplication instance, skipping migration dialog")
        
        # Mark as initialized
        config.set("repository/initialized", True)
        config.set("repository/path", collection_manager.app_dir)  # Updated path
        log.info(f"Collection manager initialized at: {collection_manager.app_dir}")
    else:
        log.debug("Collection manager already initialized")
    
    return collection_manager


def migrate_existing_lists(config: Config, collection_manager: SimpleCollectionManager) -> None:  # Updated param type
    """
    Migrate existing lists to the collection manager.
    
    Args:
        config: Application configuration
        collection_manager: The collection manager
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
            # Try to load the file
            if file_path.endswith('.json') or file_path.endswith('.sush'):
                try:
                    # Open and parse the file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract basic info from the file
                    metadata = data.get("metadata", {})
                    title = metadata.get("title", Path(file_path).stem)
                    
                    # Import to Default collection
                    log.debug(f"Importing '{title}' to Default collection")
                    
                    # Load albums using Legacy approach (simplified for migration)
                    from models.album import Album
                    from datetime import datetime
                    
                    albums = []
                    for album_data in data.get("albums", []):
                        # Convert date string to date object if needed
                        release_date_str = album_data.get("release_date", "")
                        try:
                            if "-" in release_date_str:
                                # Try ISO format
                                release_date = datetime.fromisoformat(release_date_str).date()
                            else:
                                # Legacy format might be different
                                release_date = datetime.now().date()
                        except:
                            release_date = datetime.now().date()
                        
                        # Create album object
                        album = Album(
                            artist=album_data.get("artist", ""),
                            name=album_data.get("album", album_data.get("name", "")),
                            release_date=release_date,
                            genre1=album_data.get("genre_1", album_data.get("genre1", "")),
                            genre2=album_data.get("genre_2", album_data.get("genre2", "")),
                            comment=album_data.get("comments", album_data.get("comment", "")),
                            cover_image_data=album_data.get("cover_image_data", "")
                        )
                        albums.append(album)
                    
                    # Save to new location
                    new_path = collection_manager.save_album_list(
                        albums, 
                        {"title": title},
                        "Default"
                    )
                    
                    imported_count += 1
                    log.info(f"Successfully imported: {file_path} → {new_path}")
                except Exception as e:
                    log.error(f"Error processing file {file_path}: {e}")
                    import traceback
                    log.debug(traceback.format_exc())
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