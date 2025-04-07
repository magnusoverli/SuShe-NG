"""
Main window view for the SuShe NG application with Spotify-like design.
"""
import os
import base64
from datetime import datetime
from typing import Optional
import traceback

from PyQt6.QtGui import (QAction, QIcon, QCloseEvent, QPixmap, QColor,
                    QPainter, QPen, QPainterPath, QFont, QImage)
from PyQt6.QtWidgets import (QMainWindow, QTableView, QStatusBar,
                           QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFileDialog,
                           QPushButton, QLineEdit, QFrame, QHeaderView, QMessageBox,
                            QStyledItemDelegate, QStyle)
from PyQt6.QtCore import (Qt, QEvent, QRect, QRectF)

from views.import_dialog import show_import_dialog
from utils.album_list_manager import AlbumListManager
from utils.simple_collection_manager import SimpleCollectionManager  # New import
from models.album_table_model import AlbumTableModel
from utils.theme import SpotifyTheme
from utils.config import Config
from resources import get_resource_path, resource_exists
from metadata import ICON_PATH
from utils.logging_utils import get_module_logger

# Get module logger
log = get_module_logger()


class AlbumTableDelegate(QStyledItemDelegate):
    """Custom delegate for album table to add Spotify-like styling with album artwork."""
    
    def __init__(self, parent=None):
        """Initialize the delegate."""
        super().__init__(parent)
        # Cache for placeholder images to avoid recreating them
        self.placeholder_cache = {}
        log.debug("AlbumTableDelegate initialized")
    
    def paint(self, painter, option, index):
        """Custom paint method to style table cells with album artwork."""
        # Create a copy of the option to modify
        opt = option
        
        # Get the model and row index
        model = index.model()
        row = index.row()
        col = index.column()
        
        # If the item is selected, use Spotify's selection style
        if opt.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(opt.rect, QColor(66, 66, 66))
            text_color = Qt.GlobalColor.white
        else:
            # Alternate row colors
            if row % 2 == 0:
                painter.fillRect(opt.rect, QColor(24, 24, 24))
            else:
                painter.fillRect(opt.rect, QColor(18, 18, 18))
            text_color = QColor(255, 255, 255)  # White text
        
        # Get the album
        if hasattr(model, 'albums') and row < len(model.albums):
            album = model.albums[row]
            
            # Handle first column with album artwork and name
            if col == 0:
                # Draw album artwork
                image_size = 48  # Size of the album image
                image_rect = QRect(opt.rect.left() + 12, opt.rect.top() + 4, 
                                image_size, image_size)
                
                # Get pixmap from base64 data if available
                pixmap = None
                if hasattr(album, 'cover_image_data') and album.cover_image_data:
                    try:
                        # Convert base64 to image
                        image_data = base64.b64decode(album.cover_image_data)
                        qimage = QImage()
                        qimage.loadFromData(image_data)
                        pixmap = QPixmap.fromImage(qimage)
                    except Exception as e:
                        log.warning(f"Error loading image from base64: {e}")
                        pixmap = self._get_placeholder_image(image_size)
                elif hasattr(album, 'cover_image') and album.cover_image:
                    # Fallback to file path (for backward compatibility)
                    pixmap = QPixmap(album.cover_image)
                    if pixmap.isNull():
                        pixmap = self._get_placeholder_image(image_size)
                else:
                    # Create a placeholder image
                    pixmap = self._get_placeholder_image(image_size)
                
                # Scale the image while keeping aspect ratio
                pixmap = pixmap.scaled(image_size, image_size, 
                                    Qt.AspectRatioMode.KeepAspectRatio, 
                                    Qt.TransformationMode.SmoothTransformation)
                
                # Draw the image with a subtle shadow effect
                painter.save()
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(0, 0, 0, 40))
                shadow_rect = image_rect.adjusted(2, 2, 2, 2)
                painter.drawRoundedRect(shadow_rect, 4, 4)
                painter.restore()
                
                # Create a path with rounded corners for the image
                painter.save()
                path = QPainterPath()
                # Convert QRect to QRectF for addRoundedRect
                path.addRoundedRect(QRectF(image_rect), 4, 4)
                painter.setClipPath(path)
                painter.drawPixmap(image_rect, pixmap)
                painter.restore()
                
                # Draw album name
                text_rect = QRect(opt.rect)
                text_rect.setLeft(image_rect.right() + 16)  # Add margin after image
                
                painter.setPen(text_color)
                painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                elidedText = painter.fontMetrics().elidedText(
                    album.name, Qt.TextElideMode.ElideRight, text_rect.width() - 20)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, elidedText)
                
            else:
                # Draw text for other columns
                text = ""
                if col == 1:
                    text = album.artist
                    font = QFont("Segoe UI", 10, QFont.Weight.Medium)
                elif col == 2:
                    text = album.release_date.strftime("%Y-%m-%d")
                    font = QFont("Segoe UI", 9)
                elif col == 3:
                    text = album.genre1
                    font = QFont("Segoe UI", 9)
                elif col == 4:
                    text = album.genre2
                    font = QFont("Segoe UI", 9)
                elif col == 5:
                    text = album.comment
                    font = QFont("Segoe UI", 9)
                
                painter.setPen(text_color)
                painter.setFont(font)
                # Elide text if it's too long
                elidedText = painter.fontMetrics().elidedText(
                    text, Qt.TextElideMode.ElideRight, opt.rect.width() - 16)
                painter.drawText(opt.rect.adjusted(8, 0, -8, 0), 
                            Qt.AlignmentFlag.AlignVCenter, elidedText)
        else:
            # Fallback to default rendering
            super().paint(painter, opt, index)
    
    def sizeHint(self, option, index):
        """Return a size hint that accommodates the album artwork."""
        size = super().sizeHint(option, index)
        # Make rows taller to fit album artwork
        size.setHeight(56)
        return size
    
    def _get_placeholder_image(self, size):
        """
        Create a placeholder image for albums without covers.
        
        Args:
            size: The size of the placeholder image
            
        Returns:
            QPixmap: The placeholder image
        """
        # Check cache first
        if size in self.placeholder_cache:
            return self.placeholder_cache[size]
        
        # Create a new placeholder
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(40, 40, 40))  # Dark gray background
        
        # Draw a music note icon in the center
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(180, 180, 180), 1))  # Light gray for the icon
        painter.setFont(QFont("Segoe UI", size // 4))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "♪")
        painter.end()
        
        # Cache the placeholder
        self.placeholder_cache[size] = pixmap
        return pixmap


class MainWindow(QMainWindow):
    """Main application window with Spotify-like design."""
    
    def __init__(self, config: Optional[Config] = None, collection_manager: Optional[SimpleCollectionManager] = None):
        """
        Initialize the main window.
        
        Args:
            config: Application configuration manager (optional)
            collection_manager: Collection manager for list management (optional)
        """
        log.debug("MainWindow.__init__ starting...")
        try:
            super().__init__()
            log.debug("Super initialized")
            
            # Store the configuration manager
            self.config = config or Config()
            log.debug("Config stored")
            
            # Store the collection manager
            self.collection_manager = collection_manager or SimpleCollectionManager()
            log.debug("Collection manager stored")
            
            self.setWindowTitle("SuShe NG")
            self.setMinimumSize(1000, 700)
            log.debug("Window title and size set")
            
            # Set window icon if available
            if resource_exists(ICON_PATH):
                log.debug(f"Setting window icon from {ICON_PATH}")
                self.setWindowIcon(QIcon(get_resource_path(ICON_PATH)))
            else:
                log.warning("No icon found for window")
            
            # Create the central widget
            log.debug("Creating central widget...")
            central_widget = QWidget()
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            log.debug("Central widget layout created")
            
            # Create the main content area
            log.debug("Creating content widget...")
            content_widget = QWidget()
            content_layout = QHBoxLayout(content_widget)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(0)
            log.debug("Content widget created")
            
            # Create the main panel
            log.debug("Creating main panel...")
            self.main_panel = self.create_main_panel()
            log.debug("Main panel created")
            content_layout.addWidget(self.main_panel, 1)  # Give it stretch factor
            log.debug("Main panel added to content layout")
            
            # Add the content widget to the main layout
            main_layout.addWidget(content_widget, 1)
            log.debug("Content widget added to main layout")
            
            # Set the central widget
            self.setCentralWidget(central_widget)
            log.debug("Central widget set")
            
            # Create the menu bar
            log.debug("Creating menu bar...")
            self.create_menu_bar()
            log.debug("Menu bar created")
            
            # Create the status bar
            log.debug("Creating status bar...")
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("Ready")
            self.status_bar.setFixedHeight(24)
            log.debug("Status bar created")
            
            # Apply Spotify-like dark theme
            log.debug("Applying theme...")
            self.apply_theme()
            log.debug("Theme applied")
            
            # Restore window geometry from config
            log.debug("Restoring window state...")
            self.restore_window_state()
            log.debug("Window state restored")
            log.info("MainWindow initialization completed")
            
        except Exception as e:
            log.critical(f"Error in MainWindow.__init__: {e}")
            log.critical(traceback.format_exc())
            raise

    def _new_file(self):
        """Create a new empty album list."""
        log.debug("Creating new album list")
        try:
            # Ask confirmation if there are unsaved changes
            if hasattr(self, 'albums') and self.albums:
                log.debug("Unsaved changes detected, prompting user")
                result = QMessageBox.question(
                    self,
                    "New Album List",
                    "Do you want to create a new album list? Any unsaved changes will be lost.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if result != QMessageBox.StandardButton.Yes:
                    log.debug("User cancelled new album list creation")
                    return
            
            # Get collections from manager
            collections = self.collection_manager.get_collections()
            collection_names = list(collections.keys())
            log.debug(f"Available collections: {collection_names}")
            
            # Import the new list dialog
            from views.new_list_dialog import show_new_list_dialog
            
            # Show the new list dialog with integrated collection selection
            log.debug("Showing new list dialog")
            list_info = show_new_list_dialog(collection_names, self)
            
            if not list_info:
                # User canceled
                log.debug("User cancelled new list dialog")
                return
            
            # Create the new collection if needed
            if list_info["is_new_collection"]:
                log.info(f"Creating new collection: {list_info['collection_name']}")
                self.collection_manager.create_collection(list_info["collection_name"])
            
            # Create a new empty list
            log.debug("Creating new empty album list")
            self.albums = []
            self.model = AlbumTableModel(self.albums)
            self.table_view.setModel(self.model)
            
            # Set up the table again to ensure proper display
            self.setup_enhanced_drag_drop()
            
            # Reset current file path
            self.current_file_path = None
            
            # Set metadata with the provided information
            self.list_metadata = {
                "title": list_info["title"],
                "collection": list_info["collection_name"]
            }
            
            # Update window title
            self.setWindowTitle(f"{list_info['title']} - SuShe NG")
            
            # Update status bar
            self.status_bar.showMessage(f"Created new album list in collection: {list_info['collection_name']}")
            log.info(f"Created new album list: {list_info['title']} in collection: {list_info['collection_name']}")
            
            # Save the empty list to collection manager - create the file
            self.save_to_collection_manager(allow_empty=True)

        except Exception as e:
            log.error(f"Error creating new file: {e}")
            log.debug(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while creating a new list: {str(e)}"
            )

    def _import_list(self):
        """Import an album list from a file."""
        log.debug("Importing album list")
        try:
            # Get file path from dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Album List",
                "",
                "Album Lists (*.json *.sush);;All Files (*.*)"
            )
            
            if not file_path:
                log.debug("User cancelled file selection")
                return
                    
            # Get collections
            collections = self.collection_manager.get_collections()
            collection_names = list(collections.keys())
            
            # Import the collection selection dialog
            from views.collection_selection_dialog import select_collection
            
            # Show the collection selection dialog
            log.debug("Showing collection selection dialog")
            collection_name, is_new, ok = select_collection(
                collection_names,
                self,
                "Import Album List",
                "Choose a collection for the imported list:"
            )
            
            if not ok:
                # User canceled
                log.debug("User cancelled collection selection")
                return
            
            # Create the new collection if needed
            if is_new:
                log.info(f"Creating new collection for import: {collection_name}")
                self.collection_manager.create_collection(collection_name)
                
            # Import the file
            log.info(f"Importing file: {file_path}")
            imported_path = self.collection_manager.import_external_list(file_path, collection_name)
            if imported_path:
                # Open the imported list
                self.open_album_list(imported_path)
                self.status_bar.showMessage(f"Imported list from {file_path} to collection: {collection_name}")
                log.info(f"Successfully imported list from {file_path} to collection: {collection_name}")
                    
        except Exception as e:
            log.error(f"Error importing list: {e}")
            log.debug(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Import Error",
                f"An error occurred while importing: {str(e)}"
            )

    def _export_list(self):
        """
        Export the current album list to a file.
        """
        log.debug("Exporting album list")
        try:
            # Check if there are albums to export
            if not hasattr(self, 'albums') or not self.albums:
                log.warning("No albums to export")
                QMessageBox.warning(
                    self,
                    "Export Warning",
                    "There are no albums to export."
                )
                return
            
            # Create metadata if it doesn't exist
            if not hasattr(self, 'list_metadata'):
                log.debug("Creating default metadata for export")
                self.list_metadata = {
                    "title": "My Album List",
                    "description": "Album list created with SuShe NG"
                }
            
            # Get save file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Album List",
                f"{self.list_metadata.get('title', 'My Album List')}.sush",
                "SuShe NG Files (*.sush);;All Files (*.*)"
            )
            
            if not file_path:
                # User canceled
                log.debug("User cancelled export dialog")
                return
            
            # Create a list manager
            list_manager = AlbumListManager()
            
            # Export the list
            log.info(f"Exporting {len(self.albums)} albums to {file_path}")
            list_manager.export_to_new_format(
                self.albums,
                self.list_metadata,
                file_path
            )
            
            # Update the status bar
            self.status_bar.showMessage(f"Exported {len(self.albums)} albums to {file_path}")
            
            # Add to recent files
            if hasattr(self, 'config') and self.config:
                log.debug("Adding exported file to recent files")
                self.config.add_recent_file(file_path)
                self._update_recent_files_menu()
            
        except Exception as e:
            # Show error message
            log.error(f"Error exporting list: {e}")
            log.debug(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred while exporting: {str(e)}"
            )


    def _open_file(self):
        """
        Open an album list from a file.
        """
        log.debug("Opening album list file")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Album List",
            "",
            "SuShe NG Files (*.sush);;JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            log.info(f"Selected file to open: {file_path}")
            self.open_album_list(file_path)
        else:
            log.debug("User cancelled file selection")


    def open_album_list(self, file_path):
        """
        Open an album list from a file.
        
        Args:
            file_path: Path to the album list file
        """
        log.debug(f"Opening album list from: {file_path}")
        try:
            # Load the list from the collection manager
            albums, metadata = self.collection_manager.load_album_list(file_path)
            
            # Set the albums
            self.albums = albums
            
            # Create a new model with the loaded albums
            self.model = AlbumTableModel(self.albums)
            self.table_view.setModel(self.model)
            
            # Set up the table again to ensure proper display
            self.setup_enhanced_drag_drop()
            
            # Store the metadata
            self.list_metadata = metadata
            
            # Store the current file path
            self.current_file_path = file_path
            
            # Update window title
            list_title = metadata.get("title", "Untitled List")
            self.setWindowTitle(f"{list_title} - SuShe NG")
            
            # Get collection name
            collection_name = self.collection_manager.get_collection_for_list(file_path)
            if collection_name:
                self.list_metadata["collection"] = collection_name
            
            # Update the status bar
            if collection_name:
                self.status_bar.showMessage(f"Opened {len(albums)} albums from collection: {collection_name}")
            else:
                self.status_bar.showMessage(f"Opened {len(albums)} albums from {file_path}")
                
            log.info(f"Successfully opened {len(albums)} albums from {file_path}")
            
        except Exception as e:
            # Show error message
            log.error(f"Error opening file {file_path}: {e}")
            log.debug(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Open Error",
                f"An error occurred while opening the file: {str(e)}"
            )

    def save_to_collection_manager(self, existing_path=None, allow_empty=False):
        """
        Save the current album list to the collection manager.
        
        Args:
            existing_path: Path to existing file (optional)
            allow_empty: Whether to allow saving empty lists (for new list creation)
        """
        log.debug("Saving to collection manager")
        try:
            # Make sure we have albums and metadata, but allow empty albums if specified
            if not hasattr(self, 'albums') or (not self.albums and not allow_empty):
                log.warning("No albums to save and empty lists not allowed")
                QMessageBox.warning(
                    self,
                    "Save Warning",
                    "There are no albums to save."
                )
                return
            
            # Create metadata if it doesn't exist
            if not hasattr(self, 'list_metadata'):
                log.debug("Creating default metadata for save")
                self.list_metadata = {
                    "title": "My Album List"
                }
            
            # Get the collection from metadata or ask user
            collection_name = self.list_metadata.get("collection")
            
            if not collection_name:
                log.debug("No collection specified, prompting user")
                # Get collections
                collections = self.collection_manager.get_collections()
                collection_names = list(collections.keys())
                
                # Ask which collection to save to
                from views.collection_selection_dialog import select_collection
                collection_name, is_new, ok = select_collection(
                    collection_names,
                    self,
                    "Save Album List",
                    "Choose a collection for your album list:"
                )
                
                if not ok:
                    log.debug("User cancelled collection selection")
                    return
                
                # Create new collection if needed
                if is_new:
                    log.info(f"Creating new collection: {collection_name}")
                    self.collection_manager.create_collection(collection_name)
                
                # Update metadata with collection
                self.list_metadata["collection"] = collection_name
            
            # Get the file name from the existing path, if provided
            file_name = None
            if existing_path:
                file_name = os.path.basename(existing_path)
                log.debug(f"Using existing filename: {file_name}")
            
            # Save to the collection manager
            log.debug(f"Saving {len(self.albums)} albums to collection: {collection_name}")
            file_path = self.collection_manager.save_album_list(
                self.albums, 
                self.list_metadata, 
                collection_name,
                file_name
            )
            
            # Store the current file path
            self.current_file_path = file_path
            log.debug(f"Saved to: {file_path}")
            
            # Update window title
            list_title = self.list_metadata.get("title", "Untitled List")
            self.setWindowTitle(f"{list_title} - SuShe NG")
            
            # Update the status bar
            self.status_bar.showMessage(f"Saved {len(self.albums)} albums to collection: {collection_name}")
            log.info(f"Successfully saved {len(self.albums)} albums to collection: {collection_name}")
            
            # Add to recent files in config
            if hasattr(self, 'config') and self.config:
                log.debug("Adding saved file to recent files")
                self.config.add_recent_file(file_path)
                # Update the recent files menu
                self._update_recent_files_menu()
                
        except Exception as e:
            log.error(f"Error saving to collection manager: {e}")
            log.debug(traceback.format_exc())
            # Show error message
            QMessageBox.critical(
                self,
                "Save Error",
                f"An error occurred while saving: {str(e)}"
            )

    def _save_file(self):
        """
        Save the current album list to a file.
        """
        log.debug("Saving album list")
        # Check if we have a current file path
        current_file = getattr(self, 'current_file_path', None)
        
        if current_file:
            # Save to the current file
            log.debug(f"Saving to existing file: {current_file}")
            self.save_to_collection_manager(existing_path=current_file)
        else:
            # No current file, use Save As
            log.debug("No current file, using Save As")
            self._save_file_as()


    def _save_file_as(self):
        """
        Save the current album list to a new file.
        """
        log.debug("Saving album list as new file")
        # Check if there are albums to save
        if not hasattr(self, 'albums') or not self.albums:
            log.warning("No albums to save")
            QMessageBox.warning(
                self,
                "Save Warning",
                "There are no albums to save."
            )
            return
        
        # Create metadata if it doesn't exist
        if not hasattr(self, 'list_metadata'):
            log.debug("Creating default metadata for save")
            self.list_metadata = {
                "title": "My Album List"
            }
        
        # Get collections
        collections = self.collection_manager.get_collections()
        collection_names = list(collections.keys())
        
        # Ask which collection to save to
        from views.collection_selection_dialog import select_collection
        collection_name, is_new, ok = select_collection(
            collection_names,
            self,
            "Save Album List",
            "Choose a collection for your album list:"
        )
        
        if not ok:
            log.debug("User cancelled save dialog")
            return
        
        # Create new collection if needed
        if is_new:
            log.info(f"Creating new collection: {collection_name}")
            self.collection_manager.create_collection(collection_name)
        
        # Update metadata with collection
        self.list_metadata["collection"] = collection_name
        
        # Save to collection manager
        log.debug(f"Saving to collection: {collection_name}")
        self.save_to_collection_manager()

    def _update_recent_files_menu(self):
        """
        Update the recent files menu.
        """
        log.debug("Updating recent files menu")
        if not hasattr(self, 'recent_files_menu'):
            log.warning("Recent files menu not found")
            return
        
        # Clear the menu
        self.recent_files_menu.clear()
        
        # Get recent files from both sources
        recent_files = []
        if hasattr(self, 'config') and self.config:
            # Get from config
            config_recent = self.config.get_recent_files()
            recent_files.extend(config_recent)
        
        if hasattr(self, 'collection_manager'):
            # Get from collection manager
            manager_recent = [item["file_path"] for item in self.collection_manager.get_recent_lists()]
            # Add to the list if not already there
            for path in manager_recent:
                if path not in recent_files:
                    recent_files.append(path)
        
        # Remove duplicates and non-existent files
        recent_files = [f for f in recent_files if os.path.exists(f)]
        # Limit to first 10
        recent_files = recent_files[:10]
        
        if not recent_files:
            # Add a disabled "No recent files" action
            log.debug("No recent files found")
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_files_menu.addAction(action)
        else:
            # Add actions for each recent file
            log.debug(f"Adding {len(recent_files)} recent files to menu")
            for file_path in recent_files:
                # Try to get more descriptive name from collection manager
                title = os.path.basename(file_path)
                collection = None
                
                if hasattr(self, 'collection_manager'):
                    # Try to get info from collection manager
                    list_info = self.collection_manager._get_list_info(file_path)
                    if list_info:
                        title = list_info.get("title", title)
                        collection = list_info.get("collection")
                
                # Create menu item name
                if collection:
                    display_name = f"{title} ({collection})"
                else:
                    display_name = title
                    
                action = QAction(display_name, self)
                action.setData(file_path)
                action.triggered.connect(lambda checked, path=file_path: self.open_album_list(path))
                self.recent_files_menu.addAction(action)
            
            # Add separator
            self.recent_files_menu.addSeparator()
            
            # Add "Clear Recent Files" action
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self._clear_recent_files)
            self.recent_files_menu.addAction(clear_action)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the window close event.
        
        Args:
            event: The close event
        """
        log.debug("Close event received")
        # Check for unsaved changes
        # This is a simple implementation - you might want to add more sophisticated change tracking
        if hasattr(self, 'albums') and self.albums and not hasattr(self, 'current_file_path'):
            # Unsaved changes
            log.info("Unsaved changes detected, prompting user")
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if result == QMessageBox.StandardButton.Save:
                log.debug("User chose to save before closing")
                self._save_file()
                # Check if save was successful
                if not hasattr(self, 'current_file_path'):
                    # Save was canceled or failed
                    log.debug("Save was cancelled or failed, ignoring close event")
                    event.ignore()
                    return
            elif result == QMessageBox.StandardButton.Cancel:
                log.debug("User cancelled close operation")
                event.ignore()
                return
        
        # Save window state before closing
        log.debug("Saving window state before closing")
        self.save_window_state()
        
        # Accept the close event
        log.info("Application closing")
        event.accept()

    def _clear_recent_files(self):
        """
        Clear the recent files list.
        """
        log.debug("Clearing recent files list")
        if hasattr(self, 'config') and self.config:
            self.config.set("recent_files", [])
        
        if hasattr(self, 'collection_manager') and hasattr(self.collection_manager, 'metadata'):
            self.collection_manager.metadata["recent_lists"] = []
            self.collection_manager._save_metadata()
        
        self._update_recent_files_menu()
        log.info("Recent files list cleared")

    def create_main_panel(self) -> QWidget:
        """Create the main content panel with header and album table."""
        log.debug("Creating main panel")
        try:
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # Create header panel
            header = QWidget()
            header.setObjectName("mainHeader")
            header.setFixedHeight(64)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(16, 8, 16, 8)
            
            # Add search box (placeholder - not functional yet)
            search_box = QLineEdit()
            search_box.setPlaceholderText("Search albums...")
            search_box.setFixedWidth(220)
            search_box.setStyleSheet("""
                QLineEdit {
                    background-color: #FFFFFF;
                    border-radius: 16px;
                    padding: 8px 12px;
                    color: #121212;
                }
            """)
            header_layout.addWidget(search_box)
            
            # Add navigation buttons (placeholders - not functional yet)
            nav_back = QPushButton("←")
            nav_back.setFixedSize(32, 32)
            nav_back.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.7);
                    color: #FFFFFF;
                    border-radius: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
            
            nav_forward = QPushButton("→")
            nav_forward.setFixedSize(32, 32)
            nav_forward.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.7);
                    color: #FFFFFF;
                    border-radius: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
            
            header_layout.addWidget(nav_back)
            header_layout.addWidget(nav_forward)
            header_layout.addStretch()
            
            # Table view button removed
            
            layout.addWidget(header)
            
            # Add a title bar for the album section
            title_bar = QWidget()
            title_bar_layout = QHBoxLayout(title_bar)
            title_bar_layout.setContentsMargins(16, 16, 16, 8)
            
            title_label = QLabel("All Albums")
            title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
            title_bar_layout.addWidget(title_label)
            
            layout.addWidget(title_bar)
            
            # Create and set up the table view
            self.table_view = QTableView()
            log.debug("Creating table view")
            
            # Basic setup that doesn't depend on model
            self.table_view.setDragEnabled(True)
            self.table_view.setAcceptDrops(True)
            self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            self.table_view.setShowGrid(False)
            self.table_view.setAlternatingRowColors(True)
            self.table_view.setDragDropMode(QTableView.DragDropMode.InternalMove)
            self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.table_view.setFrameShape(QFrame.Shape.NoFrame)
            self.table_view.verticalHeader().setVisible(False)
            self.table_view.verticalHeader().setDefaultSectionSize(56)
            
            # Start with an empty album list
            self.albums = []
            
            # Create the model
            log.debug("Creating table model")
            self.model = AlbumTableModel(self.albums)
            self.table_view.setModel(self.model)
            
            # Now set properties that require a model to be set first
            log.debug("Creating table delegate")
            self.table_view.setItemDelegate(AlbumTableDelegate())
            
            # Style the headers
            self.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_view.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #121212;
                    color: #B3B3B3;
                    padding: 8px;
                    border: none;
                    border-bottom: 1px solid #333333;
                    font-weight: bold;
                }
            """)
            
            # Set resize modes now that we have a model
            header = self.table_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            if self.model.columnCount() > 0:
                # If we have columns, set their specific resize modes
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Album name + cover
                self.table_view.setColumnWidth(0, 300)
                
                if self.model.columnCount() > 1:
                    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Artist
                    self.table_view.setColumnWidth(1, 180)
                
                if self.model.columnCount() > 2:
                    header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # Release date
                    self.table_view.setColumnWidth(2, 120)
                
                if self.model.columnCount() > 3:
                    header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # Genre 1
                    self.table_view.setColumnWidth(3, 140)
                
                if self.model.columnCount() > 4:
                    header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # Genre 2
                    self.table_view.setColumnWidth(4, 140)
                
                if self.model.columnCount() > 5:
                    header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Comment
            
            # Add the table view to the layout
            layout.addWidget(self.table_view, 1)  # Give it stretch factor
            
            # Create list metadata for the empty list
            # MOVED BEFORE setup_enhanced_drag_drop to avoid uninitialized variable risk
            log.debug("Creating default list metadata")
            self.list_metadata = {
                "title": "Untitled List",
                "description": "New album list",
                "date_created": datetime.now().isoformat(),
                "date_modified": datetime.now().isoformat()
            }
            
            # Set up enhanced drag and drop functionality
            self.setup_enhanced_drag_drop()
                
            return panel
        except Exception as e:
            log.critical(f"Error in create_main_panel: {e}")
            log.critical(traceback.format_exc())
            raise

    def highlight_row(self, row_index):
        """
        Create a brief highlight animation for the specified row.
        
        Args:
            row_index: Index of row to highlight
        """
        log.debug(f"Highlighting row: {row_index}")
        from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QAbstractAnimation
        
        # Get the index for the row
        index = self.model.index(row_index, 0)
        
        # Scroll to ensure it's visible
        self.table_view.scrollTo(index)
        
        # Create a transient style sheet for the highlight
        original_style = self.table_view.styleSheet()
        
        # Select the row briefly
        self.table_view.selectRow(row_index)
        
        # Set a timer to clear the selection after a delay
        QTimer.singleShot(800, lambda: self.table_view.clearSelection())

    def on_data_changed(self, top_left, bottom_right):
        """
        Handle data changes in the model, particularly after drag and drop.
        
        Args:
            top_left: Top-left index of the changed data
            bottom_right: Bottom-right index of the changed data
        """
        log.debug("Model data changed")
        # Flash a subtle highlight on the rows that were affected by a drag and drop
        if hasattr(self.model, 'last_drag_target') and self.model.last_drag_target >= 0:
            target_row = self.model.last_drag_target
            log.debug(f"Drag operation detected, highlighting target row: {target_row}")
            
            # Create a temporary style for the target row to highlight it
            self.highlight_row(target_row)
            
            # Reset the drag source/target
            self.model.last_drag_source = -1
            self.model.last_drag_target = -1

    def setup_enhanced_drag_drop(self):
        """Set up enhanced drag and drop functionality for the album table."""
        log.debug("Setting up enhanced drag and drop")
        from views.enhanced_drag_drop import apply_drag_drop_enhancements
        
        # Apply the enhancements to our components
        apply_drag_drop_enhancements(
            self.table_view,
            self.model,
            self.table_view.itemDelegate()
        )
        
        # Connect to dataChanged signal for animations
        self.model.dataChanged.connect(self.on_data_changed)
        
        # Add visual feedback when dragging
        self.table_view.setShowGrid(False)  # Ensure grid is off for cleaner look
        self.table_view.setStyleSheet("""
            QTableView {
                background-color: #121212;
                alternate-background-color: #181818;
                color: #FFFFFF;
                border: none;
                selection-background-color: #333333;
                selection-color: #FFFFFF;
                outline: none; /* Remove focus outline */
            }
            QTableView::item {
                padding: 8px;
                border-bottom: 1px solid #282828;
            }
            QTableView::item:selected {
                background-color: #333333;
            }
            QTableView::item:hover {
                background-color: #282828;
            }
            /* Style for drop indicator */
            QTableView::drop-indicator {
                background-color: #1DB954;
                border-radius: 2px;
                height: 4px;
                width: 100%;
            }
        """)

    
    def create_menu_bar(self) -> None:
        """Create the application menu bar with standard file options."""
        log.debug("Creating menu bar")
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # New action
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)
        
        # Open action
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        # Save action
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        # Save As action
        save_as_action = QAction("Save &As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Import action
        import_action = QAction("&Import List...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._import_list)
        file_menu.addAction(import_action)
        
        # Export action
        export_action = QAction("&Export List...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_list)
        file_menu.addAction(export_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Recent files submenu
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        self._update_recent_files_menu()
        
        # Add another separator
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")

        # Toggle status bar action
        toggle_status_bar_action = QAction("Toggle &Status Bar", self)
        toggle_status_bar_action.setShortcut("Ctrl+/")
        toggle_status_bar_action.triggered.connect(self.toggle_status_bar)
        view_menu.addAction(toggle_status_bar_action)
    
    def toggle_status_bar(self):
        """Toggle the visibility of the status bar."""
        log.debug("Toggling status bar visibility")
        self.status_bar.setVisible(not self.status_bar.isVisible())
    
    def apply_theme(self) -> None:
        """Apply the Spotify-like theme to the window and its components."""
        log.debug("Applying Spotify theme")
        # Use the updated Spotify theme
        SpotifyTheme.apply_to_window(self)
        
        # Additional styling for the Spotify-like components
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            #mainHeader {
                background-color: rgba(0, 0, 0, 0.5);
                border-bottom: 1px solid #333333;
            }
            QTableView {
                background-color: #121212;
                alternate-background-color: #181818;
                color: #FFFFFF;
                border: none;
                selection-background-color: #333333;
                selection-color: #FFFFFF;
            }
            QTableView::item {
                padding: 8px;
                border-bottom: 1px solid #282828;
            }
            QTableView::item:selected {
                background-color: #333333;
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
            QStatusBar {
                background-color: #181818;
                color: #B3B3B3;
            }
            QMenuBar {
                background-color: #121212;
                color: #FFFFFF;
            }
            QMenuBar::item:selected {
                background-color: #333333;
            }
            QMenu {
                background-color: #282828;
                color: #FFFFFF;
                border: 1px solid #121212;
            }
            QMenu::item:selected {
                background-color: #333333;
            }
        """)

    def restore_window_state(self) -> None:
        """Restore window size and position from saved configuration."""
        log.debug("Restoring window state")
        # Get saved window geometry
        width = self.config.get("window/width", self.config.get_default("window/width"))
        height = self.config.get("window/height", self.config.get_default("window/height"))
        pos_x = self.config.get("window/position_x")
        pos_y = self.config.get("window/position_y")
        maximized = self.config.get("window/maximized", False)
        
        # Set window size
        if width and height:
            log.debug(f"Restoring window size: {width}x{height}")
            self.resize(width, height)
        
        # Set window position if it was saved
        if pos_x is not None and pos_y is not None:
            log.debug(f"Restoring window position: ({pos_x}, {pos_y})")
            self.move(pos_x, pos_y)
        
        # Maximize window if it was maximized
        if maximized:
            log.debug("Restoring maximized state")
            self.setWindowState(Qt.WindowState.WindowMaximized)
    
    def save_window_state(self) -> None:
        """Save window size and position to configuration."""
        log.debug("Saving window state")
        # Only save if we have a config manager
        if not self.config:
            log.warning("No config manager available, skipping window state save")
            return
        
        # Save maximized state
        is_maximized = self.windowState() & Qt.WindowState.WindowMaximized
        self.config.set("window/maximized", bool(is_maximized))
        log.debug(f"Saved maximized state: {bool(is_maximized)}")
        
        # Only save size and position if not maximized
        if not is_maximized:
            log.debug(f"Saved window size: {self.width()}x{self.height()}")
            log.debug(f"Saved window position: ({self.x()}, {self.y()})")
            self.config.set("window/width", self.width())
            self.config.set("window/height", self.height())
            self.config.set("window/position_x", self.x())
            self.config.set("window/position_y", self.y())