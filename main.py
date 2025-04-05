#!/usr/bin/env python3
"""
SuShe NG - A PyQt6 application for managing music albums
Entry point for the application
"""

import sys
import os
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Set up logging first
from utils.logging_utils import SusheNGLogger, setup_qt_logging, get_module_logger

# Initialize the logger
logger = SusheNGLogger.initialize(
    app_name="SusheNG",
    console_level="INFO",
    file_level="DEBUG",
    log_to_file=True
)

# Get module-specific logger
log = get_module_logger()

# Log application startup
log.info("Starting SuShe NG application...")
log.debug(f"Python version: {sys.version}")
log.debug(f"Current directory: {os.getcwd()}")
log.debug(f"Files in current directory: {os.listdir('.')}")

try:
    log.debug("Importing modules...")
    from views.main_window import MainWindow
    log.debug("MainWindow imported successfully")
    from resources import get_resource_path, resource_exists
    log.debug("Resources imported successfully")
    from metadata import APP_NAME, ORG_NAME, ORG_DOMAIN, ICON_PATH, ICON_PATH_ICO, ICON_PATH_ICNS
    log.debug("Metadata imported successfully")
    from utils.config import Config
    log.debug("Config imported successfully")
except Exception as e:
    log.critical(f"Error importing modules: {e}")
    log.critical(traceback.format_exc())
    sys.exit(1)


def setup_application() -> QApplication:
    """
    Set up the QApplication with proper metadata and styling.
    
    Returns:
        Configured QApplication instance
    """
    log.debug("Setting up application...")
    try:
        # Set up Qt logging
        setup_qt_logging()
        
        # Create the application
        app = QApplication(sys.argv)
        log.debug("QApplication created")
        
        # Set application metadata
        app.setApplicationName(APP_NAME)
        app.setOrganizationName(ORG_NAME)
        app.setOrganizationDomain(ORG_DOMAIN)
        log.debug("Application metadata set")
        
        # Set application style
        app.setStyle("Fusion")
        log.debug("Application style set")
        
        # Set application icon
        set_application_icon(app)
        log.debug("Application setup complete")
        
        return app
    except Exception as e:
        log.critical(f"Error setting up application: {e}")
        log.critical(traceback.format_exc())
        sys.exit(1)


def set_application_icon(app: QApplication) -> None:
    """
    Set the application icon based on the current platform.
    
    Args:
        app: The QApplication instance
    """
    log.debug("Setting application icon...")
    try:
        # Determine which icon file to use based on platform
        if sys.platform == "win32" and resource_exists(ICON_PATH_ICO):
            # Windows prefers .ico files
            icon_path = get_resource_path(ICON_PATH_ICO)
            log.debug(f"Using Windows icon: {icon_path}")
        elif sys.platform == "darwin" and resource_exists(ICON_PATH_ICNS):
            # macOS prefers .icns files
            icon_path = get_resource_path(ICON_PATH_ICNS)
            log.debug(f"Using macOS icon: {icon_path}")
        elif resource_exists(ICON_PATH):
            # Default to PNG for other platforms or fallback
            icon_path = get_resource_path(ICON_PATH)
            log.debug(f"Using default icon: {icon_path}")
        else:
            # No icon file found
            log.warning("No icon file found, skipping")
            return
        
        # Set the application icon
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
        log.debug("Application icon set")
    except Exception as e:
        log.error(f"Error setting application icon: {e}")
        log.debug(traceback.format_exc())
        # Continue even if icon setting fails - non-critical error


def main():
    """Application entry point."""
    log.debug("Entering main function")
    try:
        # Set up the QApplication
        app = setup_application()
        
        # Create the config manager
        log.debug("Creating config manager...")
        config = Config()
        log.debug("Config manager created")
        
        # Initialize the list repository
        log.debug("Initializing list repository...")
        from utils.list_repository import ListRepository
        from views.initialization import initialize_repository
        list_repository = initialize_repository(config)
        log.debug("List repository initialized")
        
        # Create and show the main window
        log.debug("Creating main window...")
        window = MainWindow(config, list_repository)
        log.debug("Main window created")
        
        log.debug("Showing main window...")
        window.show()
        log.debug("Main window shown")
        
        # Start the event loop
        log.info("Starting event loop...")
        result = app.exec()
        log.info(f"Event loop ended with code: {result}")
        
        # Return the exit code
        return result
    except Exception as e:
        log.critical(f"Error in main function: {e}")
        log.critical(traceback.format_exc())
        return 1


if __name__ == "__main__":
    log.debug("Script executed directly")
    try:
        sys.exit(main())
    except Exception as e:
        log.critical(f"Unhandled exception: {e}")
        log.critical(traceback.format_exc())
        sys.exit(1)
else:
    log.debug("Script imported as a module")