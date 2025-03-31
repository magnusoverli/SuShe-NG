#!/usr/bin/env python3
"""
Album Manager - A PyQt6 application for managing music albums
Entry point for the application
"""

import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Fusion style works well with custom palettes
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()