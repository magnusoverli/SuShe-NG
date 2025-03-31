"""
Theme utilities for the application.
"""

from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView, QStatusBar, QMenuBar


class SpotifyTheme:
    """Spotify-like theme for the application."""
    
    # Color constants
    BACKGROUND = QColor(18, 18, 18)
    FOREGROUND = QColor(255, 255, 255)
    HIGHLIGHT = QColor(30, 215, 96)  # Spotify green
    SURFACE = QColor(40, 40, 40)
    SURFACE_ALT = QColor(60, 60, 60)
    TEXT_SECONDARY = QColor(179, 179, 179)  # #B3B3B3
    BORDER = QColor(40, 40, 40)  # #282828
    
    @classmethod
    def apply_to_application(cls, app: QApplication) -> None:
        """
        Apply the Spotify theme to the entire application.
        
        Args:
            app: The QApplication instance
        """
        # Set the fusion style which works well with custom palettes
        app.setStyle("Fusion")
        
        # Create and apply a dark palette
        palette = cls.create_palette()
        app.setPalette(palette)
        
        # Set the default font
        font = QFont("Segoe UI", 10)
        app.setFont(font)
    
    @classmethod
    def apply_to_window(cls, window: QMainWindow) -> None:
        """
        Apply the Spotify theme to a specific window.
        
        Args:
            window: The QMainWindow instance
        """
        # Create and apply a dark palette
        palette = cls.create_palette()
        window.setPalette(palette)
        
        # Set the default font
        font = QFont("Segoe UI", 10)
        window.setFont(font)
        
        # Apply stylesheets to specific components
        cls.style_menu_bar(window.menuBar())
        
        # Style the status bar if it exists
        status_bar = window.statusBar()
        if status_bar:
            cls.style_status_bar(status_bar)
    
    @classmethod
    def create_palette(cls) -> QPalette:
        """
        Create a QPalette with Spotify-like colors.
        
        Returns:
            A QPalette configured with Spotify colors
        """
        palette = QPalette()
        
        # Set colors for various palette roles
        palette.setColor(QPalette.ColorRole.Window, cls.BACKGROUND)
        palette.setColor(QPalette.ColorRole.WindowText, cls.FOREGROUND)
        palette.setColor(QPalette.ColorRole.Base, cls.SURFACE)
        palette.setColor(QPalette.ColorRole.AlternateBase, cls.SURFACE_ALT)
        palette.setColor(QPalette.ColorRole.Text, cls.FOREGROUND)
        palette.setColor(QPalette.ColorRole.Button, cls.BACKGROUND)
        palette.setColor(QPalette.ColorRole.ButtonText, cls.FOREGROUND)
        palette.setColor(QPalette.ColorRole.Highlight, cls.HIGHLIGHT)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        return palette
    
    @staticmethod
    def style_menu_bar(menu_bar: QMenuBar) -> None:
        """
        Apply Spotify-like styling to a menu bar.
        
        Args:
            menu_bar: The QMenuBar instance
        """
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #181818;
                color: #FFFFFF;
            }
            QMenuBar::item:selected {
                background-color: #282828;
            }
            QMenu {
                background-color: #282828;
                color: #FFFFFF;
                border: 1px solid #181818;
            }
            QMenu::item:selected {
                background-color: #333333;
            }
        """)
    
    @staticmethod
    def style_status_bar(status_bar: QStatusBar) -> None:
        """
        Apply Spotify-like styling to a status bar.
        
        Args:
            status_bar: The QStatusBar instance
        """
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #181818;
                color: #B3B3B3;
                border-top: 1px solid #282828;
            }
        """)
    
    @staticmethod
    def style_table_view(table_view: QTableView) -> None:
        """
        Apply Spotify-like styling to a table view.
        
        Args:
            table_view: The QTableView instance
        """
        table_view.setStyleSheet("""
            QTableView {
                background-color: #181818;
                alternate-background-color: #1E1E1E;
                color: #FFFFFF;
                border: none;
            }
            QTableView::item:selected {
                background-color: #333333;
            }
            QHeaderView::section {
                background-color: #282828;
                color: #B3B3B3;
                padding: 5px;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #181818;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #535353;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)