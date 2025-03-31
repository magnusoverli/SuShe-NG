#!/usr/bin/env python3
"""
SuShe NG - A PyQt6 application for managing music albums
Entry point for the application
"""

import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QDir

from views.main_window import MainWindow
from resources import get_resource_path, resource_exists
from metadata import APP_NAME, ORG_NAME, ORG_DOMAIN, ICON_PATH, ICON_PATH_ICO, ICON_PATH_ICNS
from utils.config import Config


def setup_application() -> QApplication:
    """
    Set up the QApplication with proper metadata and styling.
    
    Returns:
        Configured QApplication instance
    """
    # Create the application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    app.setOrganizationDomain(ORG_DOMAIN)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set application icon
    set_application_icon(app)
    
    return app


def set_application_icon(app: QApplication) -> None:
    """
    Set the application icon based on the current platform.
    
    Args:
        app: The QApplication instance
    """
    # Determine which icon file to use based on platform
    if sys.platform == "win32" and resource_exists(ICON_PATH_ICO):
        # Windows prefers .ico files
        icon_path = get_resource_path(ICON_PATH_ICO)
    elif sys.platform == "darwin" and resource_exists(ICON_PATH_ICNS):
        # macOS prefers .icns files
        icon_path = get_resource_path(ICON_PATH_ICNS)
    elif resource_exists(ICON_PATH):
        # Default to PNG for other platforms or fallback
        icon_path = get_resource_path(ICON_PATH)
    else:
        # No icon file found
        return
    
    # Set the application icon
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)


def main():
    """Application entry point."""
    # Set up the QApplication
    app = setup_application()
    
    # Create the config manager
    config = Config()
    
    # Create and show the main window
    window = MainWindow(config)
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()