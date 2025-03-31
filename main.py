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
from PyQt6.QtCore import QDir

# Add debug prints
print("Starting SuShe NG application...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

try:
    print("Importing modules...")
    from views.main_window import MainWindow
    print("MainWindow imported successfully")
    from resources import get_resource_path, resource_exists
    print("Resources imported successfully")
    from metadata import APP_NAME, ORG_NAME, ORG_DOMAIN, ICON_PATH, ICON_PATH_ICO, ICON_PATH_ICNS
    print("Metadata imported successfully")
    from utils.config import Config
    print("Config imported successfully")
except Exception as e:
    print(f"Error importing modules: {e}")
    traceback.print_exc()
    sys.exit(1)


def setup_application() -> QApplication:
    """
    Set up the QApplication with proper metadata and styling.
    
    Returns:
        Configured QApplication instance
    """
    print("Setting up application...")
    try:
        # Create the application
        app = QApplication(sys.argv)
        print("QApplication created")
        
        # Set application metadata
        app.setApplicationName(APP_NAME)
        app.setOrganizationName(ORG_NAME)
        app.setOrganizationDomain(ORG_DOMAIN)
        print("Application metadata set")
        
        # Set application style
        app.setStyle("Fusion")
        print("Application style set")
        
        # Set application icon
        set_application_icon(app)
        print("Application setup complete")
        
        return app
    except Exception as e:
        print(f"Error setting up application: {e}")
        traceback.print_exc()
        sys.exit(1)


def set_application_icon(app: QApplication) -> None:
    """
    Set the application icon based on the current platform.
    
    Args:
        app: The QApplication instance
    """
    print("Setting application icon...")
    try:
        # Determine which icon file to use based on platform
        if sys.platform == "win32" and resource_exists(ICON_PATH_ICO):
            # Windows prefers .ico files
            icon_path = get_resource_path(ICON_PATH_ICO)
            print(f"Using Windows icon: {icon_path}")
        elif sys.platform == "darwin" and resource_exists(ICON_PATH_ICNS):
            # macOS prefers .icns files
            icon_path = get_resource_path(ICON_PATH_ICNS)
            print(f"Using macOS icon: {icon_path}")
        elif resource_exists(ICON_PATH):
            # Default to PNG for other platforms or fallback
            icon_path = get_resource_path(ICON_PATH)
            print(f"Using default icon: {icon_path}")
        else:
            # No icon file found
            print("No icon file found, skipping")
            return
        
        # Set the application icon
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
        print("Application icon set")
    except Exception as e:
        print(f"Error setting application icon: {e}")
        traceback.print_exc()
        # Continue even if icon setting fails - non-critical error


def main():
    """Application entry point."""
    print("Entering main function")
    try:
        # Set up the QApplication
        app = setup_application()
        
        # Create the config manager
        print("Creating config manager...")
        config = Config()
        print("Config manager created")
        
        # Create and show the main window
        print("Creating main window...")
        window = MainWindow(config)
        print("Main window created")
        
        print("Showing main window...")
        window.show()
        print("Main window shown")
        
        # Start the event loop
        print("Starting event loop...")
        result = app.exec()
        print(f"Event loop ended with code: {result}")
        
        # Return the exit code
        return result
    except Exception as e:
        print(f"Error in main function: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    print("Script executed directly")
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
        sys.exit(1)
else:
    print("Script imported as a module")