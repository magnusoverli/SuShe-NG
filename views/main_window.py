"""
Main window view for the SuShe NG application.
"""

from datetime import date
from typing import List

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QMainWindow, QTableView, QStatusBar,
                           QVBoxLayout, QWidget)

from models.album import Album
from models.album_table_model import AlbumTableModel
from utils.theme import SpotifyTheme


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.setWindowTitle("SuShe NG")
        self.setMinimumSize(800, 600)
        
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
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
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