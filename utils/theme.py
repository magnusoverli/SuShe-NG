"""
Theme utilities for the application with more accurate Spotify styling.
"""

from PyQt6.QtGui import QPalette, QColor, QFont, QBrush
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView, QStatusBar, QMenuBar


class SpotifyTheme:
    """Spotify-like theme for the application with exact Spotify colors."""
    
    # Color constants - exact Spotify colors
    BACKGROUND = QColor(18, 18, 18)        # #121212 - Main background
    BACKGROUND_DARKER = QColor(0, 0, 0)    # #000000 - Sidebar background
    BACKGROUND_LIGHTER = QColor(40, 40, 40)# #282828 - Card background
    FOREGROUND = QColor(255, 255, 255)     # #FFFFFF - Primary text
    FOREGROUND_SECONDARY = QColor(179, 179, 179)  # #B3B3B3 - Secondary text
    HIGHLIGHT = QColor(29, 185, 84)        # #1DB954 - Spotify green
    HIGHLIGHT_HOVER = QColor(30, 215, 96)  # #1ED760 - Spotify green (hover)
    SURFACE = QColor(24, 24, 24)           # #181818 - Top bar, now playing
    SURFACE_HIGHLIGHT = QColor(40, 40, 40) # #282828 - Hover states
    DIVIDER = QColor(40, 40, 40)           # #282828 - Lines and dividers
    ACTIVE = QColor(80, 80, 80)            # #505050 - Selected items

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
        
        # Apply global stylesheet
        window.setStyleSheet(cls.get_global_stylesheet())
        
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
        palette.setColor(QPalette.ColorRole.Base, cls.BACKGROUND)
        palette.setColor(QPalette.ColorRole.AlternateBase, cls.SURFACE)
        palette.setColor(QPalette.ColorRole.Text, cls.FOREGROUND)
        palette.setColor(QPalette.ColorRole.Button, cls.BACKGROUND_LIGHTER)
        palette.setColor(QPalette.ColorRole.ButtonText, cls.FOREGROUND)
        palette.setColor(QPalette.ColorRole.BrightText, cls.FOREGROUND)
        
        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, cls.HIGHLIGHT)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        # Link colors - Spotify uses green for links
        palette.setColor(QPalette.ColorRole.Link, cls.HIGHLIGHT)
        palette.setColor(QPalette.ColorRole.LinkVisited, cls.HIGHLIGHT)
        
        # Disabled colors - corrected to use ColorGroup.Disabled
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, cls.FOREGROUND_SECONDARY)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, cls.FOREGROUND_SECONDARY)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, cls.FOREGROUND_SECONDARY)
        
        # Tool tip colors
        palette.setColor(QPalette.ColorRole.ToolTipBase, cls.BACKGROUND_LIGHTER)
        palette.setColor(QPalette.ColorRole.ToolTipText, cls.FOREGROUND)
        
        return palette
    
    @staticmethod
    def get_global_stylesheet() -> str:
        """
        Get the global stylesheet for the application.
        
        Returns:
            A CSS string with global styles
        """
        return """
            QWidget {
                background-color: #121212;
                color: #FFFFFF;
                border: none;
            }
            
            QPushButton {
                background-color: #1DB954;
                color: #000000;
                border-radius: 20px;
                padding: 8px 32px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #1ED760;
            }
            
            QPushButton:pressed {
                background-color: #1AA34A;
            }
            
            QPushButton:disabled {
                background-color: #535353;
                color: #A0A0A0;
            }
            
            QLineEdit {
                background-color: #FFFFFF;
                color: #000000;
                border-radius: 4px;
                padding: 8px 12px;
                selection-background-color: #1DB954;
                selection-color: #FFFFFF;
            }
            
            QComboBox {
                background-color: #333333;
                color: #FFFFFF;
                border-radius: 4px;
                padding: 8px 12px;
                min-width: 6em;
            }
            
            QComboBox:hover {
                background-color: #404040;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 24px;
                border-left: none;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            
            QScrollBar:vertical {
                background-color: #121212;
                width: 12px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #535353;
                border-radius: 6px;
                min-height: 30px;
                margin: 3px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                background-color: #121212;
                height: 12px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #535353;
                border-radius: 6px;
                min-width: 30px;
                margin: 3px;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QToolTip {
                background-color: #282828;
                color: #FFFFFF;
                border: 1px solid #000000;
                padding: 4px;
            }
        """
    
    @staticmethod
    def style_menu_bar(menu_bar: QMenuBar) -> None:
        """
        Apply Spotify-like styling to a menu bar.
        
        Args:
            menu_bar: The QMenuBar instance
        """
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #121212;
                color: #FFFFFF;
                padding: 2px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #333333;
            }
            QMenuBar::item:pressed {
                background-color: #404040;
            }
            QMenu {
                background-color: #282828;
                color: #FFFFFF;
                border: 1px solid #121212;
                border-radius: 4px;
                padding: 8px 0px;
            }
            QMenu::item {
                padding: 6px 32px 6px 20px;
                border: none;
            }
            QMenu::item:selected {
                background-color: #333333;
            }
            QMenu::separator {
                height: 1px;
                background-color: #404040;
                margin: 4px 12px;
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
                min-height: 24px;
                padding: 0px 16px;
            }
            QStatusBar::item {
                border: none;
                padding: 0px;
            }
        """)