"""
Main window view for the SuShe NG application.
"""

from datetime import date
from typing import List, Optional

from PyQt6.QtGui import QAction, QIcon, QCloseEvent
from PyQt6.QtWidgets import (QMainWindow, QTableView, QStatusBar,
                           QVBoxLayout, QWidget, QFileDialog, QMessageBox)
from PyQt6.QtCore import QSize, QPoint, Qt

from models.album import Album
from models.album_table_model import AlbumTableModel
from utils.theme import SpotifyTheme
from utils.config import Config
from resources import get_resource_path, resource_exists
from metadata import ICON_PATH


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the main window.
        
        Args:
            config: Application configuration manager (optional)
        """
        super().__init__()
        
        # Store the configuration manager
        self.config = config or Config()
        
        self.setWindowTitle("SuShe NG")
        self.setMinimumSize(800, 600)
        
        # Set window icon if available
        if resource_exists(ICON_PATH):
            self.setWindowIcon(QIcon(get_resource_path(ICON_PATH)))
        
        # Create a central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Set up the table view
        self.table_view = QTableView()
        self.setup_table_view()
        
        # Create and set the model
        self.albums = self.create_sample_albums()
        self.model = AlbumTableModel(self.albums)
        self.table_view.setModel(self.model)
        
        # Add the table view to the layout
        layout.addWidget(self.table_view)
        
        # Set the central widget
        self.setCentralWidget(central_widget)
        
        # Create the menu bar
        self.create_menu_bar()
        
        # Create the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Apply Spotify-like dark theme
        self.apply_theme()
        
        # Restore window geometry from config
        self.restore_window_state()
    
    def setup_table_view(self) -> None:
        """Set up the table view with appropriate settings."""
        self.table_view.setDragEnabled(True)
        self.table_view.setAcceptDrops(True)
        self.table_view.setDragDropMode(QTableView.DragDropMode.InternalMove)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setShowGrid(False)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
    
    def create_menu_bar(self) -> None:
        """Create the application menu bar with standard file options."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # New action
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        # Open action
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        # Save action
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        # Save As action
        save_as_action = QAction("Save &As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(save_as_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Recent files submenu (placeholder for now)
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        
        # Add another separator
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def apply_theme(self) -> None:
        """Apply the Spotify-like theme to the window and its components."""
        SpotifyTheme.apply_to_window(self)
        SpotifyTheme.style_table_view(self.table_view)
    
    def create_sample_albums(self) -> List[Album]:
        """
        Create sample album data for demonstration purposes.
        
        Returns:
            A list of sample Album objects
        """
        return [
            Album("Daft Punk", "Random Access Memories", date(2013, 5, 17), 
                 "Electronic", "Disco", "Grammy-winning album"),
            Album("Radiohead", "OK Computer", date(1997, 5, 21), 
                 "Alternative Rock", "Art Rock", "Critically acclaimed"),
            Album("Kendrick Lamar", "To Pimp a Butterfly", date(2015, 3, 15), 
                 "Hip Hop", "Jazz Rap", "Masterpiece"),
            Album("Fleetwood Mac", "Rumours", date(1977, 2, 4), 
                 "Rock", "Pop Rock", "Classic album"),
            Album("Amy Winehouse", "Back to Black", date(2006, 10, 27), 
                 "Soul", "R&B", "Breakthrough album")
        ]
    
    def restore_window_state(self) -> None:
        """Restore window size and position from saved configuration."""
        # Get saved window geometry
        width = self.config.get("window/width", self.config.get_default("window/width"))
        height = self.config.get("window/height", self.config.get_default("window/height"))
        pos_x = self.config.get("window/position_x")
        pos_y = self.config.get("window/position_y")
        maximized = self.config.get("window/maximized", False)
        
        # Set window size
        if width and height:
            self.resize(width, height)
        
        # Set window position if it was saved
        if pos_x is not None and pos_y is not None:
            self.move(pos_x, pos_y)
        
        # Maximize window if it was maximized
        if maximized:
            self.setWindowState(Qt.WindowState.WindowMaximized)
    
    def save_window_state(self) -> None:
        """Save window size and position to configuration."""
        # Only save if we have a config manager
        if not self.config:
            return
        
        # Save maximized state
        is_maximized = self.windowState() & Qt.WindowState.WindowMaximized
        self.config.set("window/maximized", bool(is_maximized))
        
        # Only save size and position if not maximized
        if not is_maximized:
            self.config.set("window/width", self.width())
            self.config.set("window/height", self.height())
            self.config.set("window/position_x", self.x())
            self.config.set("window/position_y", self.y())
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the window close event.
        
        Args:
            event: The close event
        """
        # Save window state before closing
        self.save_window_state()
        
        # Accept the close event
        event.accept()