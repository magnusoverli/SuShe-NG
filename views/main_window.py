"""
Main window view for the SuShe NG application with Spotify-like design.
"""

import os
import base64
from datetime import datetime
from typing import Optional

from PyQt6.QtGui import (QAction, QIcon, QCloseEvent, QPixmap, QColor,
                    QPainter, QPen, QPainterPath, QFont, QImage)
from PyQt6.QtWidgets import (QMainWindow, QTableView, QStatusBar, QSplitter,
                           QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFileDialog,
                           QPushButton, QLineEdit, QFrame, QHeaderView, QMessageBox,
                            QStyledItemDelegate, QStyle)
from PyQt6.QtCore import (Qt, QEvent, QRect, QRectF)
from views.import_dialog import show_import_dialog
from utils.album_list_manager import AlbumListManager
from models.album_table_model import AlbumTableModel
from utils.theme import SpotifyTheme
from utils.config import Config
from resources import get_resource_path, resource_exists
from metadata import ICON_PATH

from utils.list_repository import ListRepository
from PyQt6.QtWidgets import QInputDialog

class AlbumTableDelegate(QStyledItemDelegate):
    """Custom delegate for album table to add Spotify-like styling with album artwork."""
    
    def __init__(self, parent=None):
        """Initialize the delegate."""
        super().__init__(parent)
        # Cache for placeholder images to avoid recreating them
        self.placeholder_cache = {}
    
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
                        print(f"Error loading image from base64: {e}")
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
    
    def __init__(self, config: Optional[Config] = None, list_repository: Optional[ListRepository] = None):
        """
        Initialize the main window.
        
        Args:
            config: Application configuration manager (optional)
            list_repository: Repository for list management (optional)
        """
        print("MainWindow.__init__ starting...")
        try:
            super().__init__()
            print("Super initialized")
            
            # Store the configuration manager
            self.config = config or Config()
            print("Config stored")
            
            # Store the list repository
            self.list_repository = list_repository or ListRepository()
            print("List repository stored")
            
            self.setWindowTitle("SuShe NG")
            self.setMinimumSize(1000, 700)
            print("Window title and size set")
            
            # Set window icon if available
            if resource_exists(ICON_PATH):
                print(f"Setting window icon from {ICON_PATH}")
                self.setWindowIcon(QIcon(get_resource_path(ICON_PATH)))
            else:
                print("No icon found for window")
            
            # Create the central widget
            print("Creating central widget...")
            central_widget = QWidget()
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            print("Central widget layout created")
            
            # Create the main content area
            print("Creating content widget...")
            content_widget = QWidget()
            content_layout = QHBoxLayout(content_widget)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(0)
            print("Content widget created")
            
            # Create the main view splitter
            print("Creating splitter...")
            self.splitter = QSplitter(Qt.Orientation.Horizontal)
            self.splitter.setHandleWidth(1)
            self.splitter.setChildrenCollapsible(False)
            content_layout.addWidget(self.splitter, 1)  # Give the splitter more space
            print("Splitter added to layout")
            
            # Create the main panel
            print("Creating main panel...")
            self.main_panel = self.create_main_panel()
            print("Main panel created")
            self.splitter.addWidget(self.main_panel)
            print("Main panel added to splitter")
            
            # Set initial sizes for the splitter
            self.splitter.setSizes([220, 780])
            print("Splitter sizes set")
            
            # Add the content widget to the main layout
            main_layout.addWidget(content_widget, 1)
            print("Content widget added to main layout")
            
            # Set the central widget
            self.setCentralWidget(central_widget)
            print("Central widget set")
            
            # Create the menu bar
            print("Creating menu bar...")
            self.create_menu_bar()
            print("Menu bar created")
            
            # Create the status bar
            print("Creating status bar...")
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("Ready")
            self.status_bar.setFixedHeight(24)
            print("Status bar created")
            
            # Apply Spotify-like dark theme
            print("Applying theme...")
            self.apply_theme()
            print("Theme applied")
            
            # Restore window geometry from config
            print("Restoring window state...")
            self.restore_window_state()
            print("Window state restored")
            print("MainWindow.__init__ completed")
            
        except Exception as e:
            import traceback
            print(f"Error in MainWindow.__init__: {e}")
            traceback.print_exc()
            raise

    def _new_file(self):
        """Create a new empty album list."""
        try:
            # Ask confirmation if there are unsaved changes
            if hasattr(self, 'albums') and self.albums:
                result = QMessageBox.question(
                    self,
                    "New Album List",
                    "Do you want to create a new album list? Any unsaved changes will be lost.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if result != QMessageBox.StandardButton.Yes:
                    return
            
            # Get collections from repository
            if hasattr(self, 'list_repository') and self.list_repository:
                collections = self.list_repository.get_collections()
                collection_names = list(collections.keys())
                
                # Import the new list dialog
                from views.new_list_dialog import show_new_list_dialog
                
                # Show the new list dialog with integrated collection selection
                list_info = show_new_list_dialog(collection_names, self)
                
                if not list_info:
                    # User canceled
                    return
                
                # Create the new collection if needed
                if list_info["is_new_collection"]:
                    self.list_repository.create_collection(list_info["collection_name"])
                
                # Create a new empty list
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
                    "description": list_info["description"],
                    "date_created": datetime.now().isoformat(),
                    "date_modified": datetime.now().isoformat(),
                    "collection": list_info["collection_name"]  # Store collection information
                }
                
                # Update window title
                self.setWindowTitle(f"{list_info['title']} - SuShe NG")
                
                # Update status bar
                self.status_bar.showMessage(f"Created new album list in collection: {list_info['collection_name']}")
                
                # Save the empty list to repository - passing True to allow empty list
                self.save_to_repository(allow_empty=True)
                
                # Add to the selected collection
                if self.current_file_path:
                    self.list_repository.add_to_collection(self.current_file_path, list_info["collection_name"])

        except Exception as e:
            import traceback
            print(f"Error creating new file: {e}")
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while creating a new list: {str(e)}"
            )

    def _import_list(self):
        """Import an album list from a file."""
        try:
            # Get file path from dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Album List",
                "",
                "Album Lists (*.json *.sush);;All Files (*.*)"
            )
            
            if not file_path:
                return
                    
            # Import the file into the repository
            if hasattr(self, 'list_repository') and self.list_repository:
                # Get collections from repository
                collections = self.list_repository.get_collections()
                collection_names = list(collections.keys())
                
                # Import the collection selection dialog
                from views.collection_selection_dialog import select_collection
                
                # Show the collection selection dialog
                collection_name, is_new, ok = select_collection(
                    collection_names,
                    self,
                    "Import Album List",
                    "Choose a collection for the imported list:"
                )
                
                if not ok:
                    # User canceled
                    return
                
                # Create the new collection if needed
                if is_new:
                    self.list_repository.create_collection(collection_name)
                    
                # Import the file
                imported_path = self.list_repository.import_external_list(file_path)
                if imported_path:
                    # Add to the selected collection
                    self.list_repository.add_to_collection(imported_path, collection_name)
                    
                    # Open the imported list
                    self.open_album_list(imported_path)
                    
                    # Add collection info to the metadata
                    if hasattr(self, 'list_metadata'):
                        self.list_metadata["collection"] = collection_name
                    
                    self.status_bar.showMessage(f"Imported list from {file_path} to collection: {collection_name}")
            else:
                # Fallback to old import method
                self.open_album_list(file_path)
                    
        except Exception as e:
            import traceback
            print(f"Error importing list: {e}")
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Import Error",
                f"An error occurred while importing: {str(e)}"
            )

    def _export_list(self):
        """
        Export the current album list to a file.
        """
        try:
            # Check if there are albums to export
            if not hasattr(self, 'albums') or not self.albums:
                QMessageBox.warning(
                    self,
                    "Export Warning",
                    "There are no albums to export."
                )
                return
            
            # Create metadata if it doesn't exist
            if not hasattr(self, 'list_metadata'):
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
                return
            
            # Create a list manager
            list_manager = AlbumListManager()
            
            # Export the list
            list_manager.export_to_new_format(
                self.albums,
                self.list_metadata,
                file_path
            )
            
            # Update the status bar
            self.status_bar.showMessage(f"Exported {len(self.albums)} albums to {file_path}")
            
            # Add to recent files
            if hasattr(self, 'config') and self.config:
                self.config.add_recent_file(file_path)
                self._update_recent_files_menu()
            
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred while exporting: {str(e)}"
            )


    def _open_file(self):
        """
        Open an album list from a file.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Album List",
            "",
            "SuShe NG Files (*.sush);;JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            self.open_album_list(file_path)


    def open_album_list(self, file_path):
        """
        Open an album list from a file.
        
        Args:
            file_path: Path to the album list file
        """
        try:
            # Load the list from the repository or directly from the file
            if hasattr(self, 'list_repository') and self.list_repository:
                albums, metadata = self.list_repository.load_list(file_path)
            else:
                # Fallback to direct loading for backward compatibility
                if file_path.endswith('.json'):
                    # Old format
                    list_manager = AlbumListManager()
                    albums, metadata = list_manager.import_from_old_format(file_path)
                elif file_path.endswith('.sush'):
                    # New format
                    list_manager = AlbumListManager()
                    albums, metadata = list_manager.import_from_new_format(file_path)
                else:
                    # Unknown format
                    QMessageBox.warning(
                        self,
                        "Unknown File Format",
                        f"The file {file_path} has an unsupported format."
                    )
                    return
            
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
            
            # Update the status bar
            self.status_bar.showMessage(f"Opened {len(albums)} albums from {file_path}")
            
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                "Open Error",
                f"An error occurred while opening the file: {str(e)}"
            )



    def _save_file(self):
        """
        Save the current album list to a file.
        """
        # Check if we have a current file path
        current_file = getattr(self, 'current_file_path', None)
        
        if current_file:
            # Save to the current file
            self._do_save_file(current_file)
        else:
            # No current file, use Save As
            self._save_file_as()


    def _save_file_as(self):
        """
        Save the current album list to a new file.
        """
        # Check if there are albums to save
        if not hasattr(self, 'albums') or not self.albums:
            QMessageBox.warning(
                self,
                "Save Warning",
                "There are no albums to save."
            )
            return
        
        # Create metadata if it doesn't exist
        if not hasattr(self, 'list_metadata'):
            self.list_metadata = {
                "title": "My Album List",
                "description": "Album list created with SuShe NG"
            }
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Album List",
            f"{self.list_metadata.get('title', 'My Album List')}.sush",
            "SuShe NG Files (*.sush);;All Files (*.*)"
        )
        
        if file_path:
            self._do_save_file(file_path)


    def _do_save_file(self, file_path):
        """
        Save the current album list to the specified file.
        
        Args:
            file_path: Path to save the file
        """
        try:
            # Create a list manager
            list_manager = AlbumListManager()
            
            # Create metadata if it doesn't exist
            if not hasattr(self, 'list_metadata'):
                self.list_metadata = {
                    "title": "My Album List",
                    "description": "Album list created with SuShe NG",
                    "date_created": datetime.now().isoformat(),
                    "date_modified": datetime.now().isoformat()
                }
            else:
                # Update the modification date
                self.list_metadata["date_modified"] = datetime.now().isoformat()
            
            # Export the list
            list_manager.export_to_new_format(
                self.albums,
                self.list_metadata,
                file_path
            )
            
            # Store the current file path
            self.current_file_path = file_path
            
            # Update window title
            list_title = self.list_metadata.get("title", "Untitled List")
            self.setWindowTitle(f"{list_title} - SuShe NG")
            
            # Update the status bar
            self.status_bar.showMessage(f"Saved {len(self.albums)} albums to {file_path}")
            
            # Add to recent files
            if hasattr(self, 'config') and self.config:
                self.config.add_recent_file(file_path)
                
                # Update the recent files menu
                self._update_recent_files_menu()
                
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                "Save Error",
                f"An error occurred while saving: {str(e)}"
            )


    def _update_recent_files_menu(self):
        """
        Update the recent files menu.
        """
        if not hasattr(self, 'recent_files_menu'):
            return
        
        # Clear the menu
        self.recent_files_menu.clear()
        
        # Get recent files
        recent_files = []
        if hasattr(self, 'config') and self.config:
            recent_files = self.config.get_recent_files()
        
        if not recent_files:
            # Add a disabled "No recent files" action
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_files_menu.addAction(action)
        else:
            # Add actions for each recent file
            for file_path in recent_files:
                file_name = os.path.basename(file_path)
                action = QAction(file_name, self)
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
        # Check for unsaved changes
        # This is a simple implementation - you might want to add more sophisticated change tracking
        if hasattr(self, 'albums') and self.albums and not hasattr(self, 'current_file_path'):
            # Unsaved changes
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if result == QMessageBox.StandardButton.Save:
                self._save_file()
                # Check if save was successful
                if not hasattr(self, 'current_file_path'):
                    # Save was canceled or failed
                    event.ignore()
                    return
            elif result == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # Save window state before closing
        self.save_window_state()
        
        # Accept the close event
        event.accept()

    def _clear_recent_files(self):
        """
        Clear the recent files list.
        """
        if hasattr(self, 'config') and self.config:
            self.config.set("recent_files", [])
            self._update_recent_files_menu()

    def save_to_repository(self, existing_path: str = None, allow_empty: bool = False) -> None:
        """
        Save the current album list to the repository.
        
        Args:
            existing_path: Path to existing file (optional)
            allow_empty: Whether to allow saving empty lists (for new list creation)
        """
        try:
            # Make sure we have albums and metadata, but allow empty albums if specified
            if not hasattr(self, 'albums') or (not self.albums and not allow_empty):
                QMessageBox.warning(
                    self,
                    "Save Warning",
                    "There are no albums to save."
                )
                return
            
            # Create metadata if it doesn't exist
            if not hasattr(self, 'list_metadata'):
                self.list_metadata = {
                    "title": "My Album List",
                    "description": "Album list created with SuShe NG",
                    "date_created": datetime.now().isoformat(),
                    "date_modified": datetime.now().isoformat()
                }
            else:
                # Update the modification date
                self.list_metadata["date_modified"] = datetime.now().isoformat()
            
            # Get the file name from the existing path, if provided
            file_name = None
            if existing_path:
                file_name = os.path.basename(existing_path)
            
            # Save to the repository
            file_path = self.list_repository.save_list(
                self.albums, self.list_metadata, file_name)
            
            # Store the current file path
            self.current_file_path = file_path
            
            # Check if this list is in a collection, and add it if not
            if "collection" in self.list_metadata:
                # Add to the specified collection
                collection_name = self.list_metadata["collection"]
                self.list_repository.add_to_collection(file_path, collection_name)
            else:
                # No collection specified, check if it's in any collection
                collections = self.list_repository.get_collections()
                found_in_collection = False
                
                for collection_name, collection_lists in collections.items():
                    for list_info in collection_lists:
                        if list_info.get("file_path") == file_path:
                            found_in_collection = True
                            # Store the collection info for future saves
                            self.list_metadata["collection"] = collection_name
                            break
                    if found_in_collection:
                        break
                        
                if not found_in_collection:
                    # Not in any collection, ask user to select one
                    collection_names = list(collections.keys())
                    
                    # Import the collection selection dialog
                    from views.collection_selection_dialog import select_collection
                    
                    # Show the collection selection dialog
                    collection_name, is_new, ok = select_collection(
                        collection_names,
                        self,
                        "Save Album List",
                        "This list is not in any collection. Choose a collection for it:"
                    )
                    
                    if not ok:
                        # Default to creating a new collection based on the list name
                        collection_name = f"{self.list_metadata.get('title', 'My')} Collection"
                        is_new = True
                    
                    # Create the new collection if needed
                    if is_new:
                        self.list_repository.create_collection(collection_name)
                    
                    # Add to the selected collection
                    self.list_repository.add_to_collection(file_path, collection_name)
                    # Store for future saves
                    self.list_metadata["collection"] = collection_name
            
            # Update window title
            list_title = self.list_metadata.get("title", "Untitled List")
            self.setWindowTitle(f"{list_title} - SuShe NG")
            
            # Update the status bar
            collection_name = self.list_metadata.get("collection", "")
            if collection_name:
                self.status_bar.showMessage(f"Saved {len(self.albums)} albums to collection: {collection_name}")
            else:
                self.status_bar.showMessage(f"Saved {len(self.albums)} albums to repository")
        except Exception as e:
            import traceback
            print(f"Error saving to repository: {e}")
            traceback.print_exc()
            # Show error message
            QMessageBox.critical(
                self,
                "Save Error",
                f"An error occurred while saving: {str(e)}"
            )

    
    def create_main_panel(self) -> QWidget:
        """Create the main content panel with header and album table."""
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
            
            # Add search box
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
            
            # Add navigation buttons
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
            
            # Add view options
            view_button = QPushButton("Table View")
            view_button.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: #FFFFFF;
                    border-radius: 16px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
            """)
            header_layout.addWidget(view_button)
            
            layout.addWidget(header)
            
            # Add a title bar for the album section
            title_bar = QWidget()
            title_bar_layout = QHBoxLayout(title_bar)
            title_bar_layout.setContentsMargins(16, 16, 16, 8)
            
            title_label = QLabel("All Albums")
            title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
            title_bar_layout.addWidget(title_label)
            
            layout.addWidget(title_bar)
            
            # Create and set up the table view - CHANGE THE ORDER OF OPERATIONS
            self.table_view = QTableView()
            
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
            self.model = AlbumTableModel(self.albums)
            self.table_view.setModel(self.model)
            
            # Now set properties that require a model to be set first
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
            self.setup_enhanced_drag_drop()
            
            # Create list metadata for the empty list
            self.list_metadata = {
                "title": "Untitled List",
                "description": "New album list",
                "date_created": datetime.now().isoformat(),
                "date_modified": datetime.now().isoformat()
            }
                
            return panel
        except Exception as e:
            import traceback
            print(f"Error in create_main_panel: {e}")
            traceback.print_exc()
            raise

    def highlight_row(self, row_index):
        """
        Create a brief highlight animation for the specified row.
        
        Args:
            row_index: Index of row to highlight
        """
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
        # Flash a subtle highlight on the rows that were affected by a drag and drop
        if hasattr(self.model, 'last_drag_target') and self.model.last_drag_target >= 0:
            target_row = self.model.last_drag_target
            
            # Create a temporary style for the target row to highlight it
            self.highlight_row(target_row)
            
            # Reset the drag source/target
            self.model.last_drag_source = -1
            self.model.last_drag_target = -1

    def setup_enhanced_drag_drop(self):
        """Set up enhanced drag and drop functionality for the album table."""
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
        self.status_bar.setVisible(not self.status_bar.isVisible())
    
    def apply_theme(self) -> None:
        """Apply the Spotify-like theme to the window and its components."""
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
            QSplitter::handle {
                background-color: #282828;
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