"""
views/sidebar_manager.py

Manager for the application sidebar with Spotify-inspired design.
"""

import os
from typing import Callable, Dict, List, Optional, Any

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                           QScrollArea, QFrame, QMenu, QInputDialog,
                           QMessageBox, QTreeWidget, QTreeWidgetItem,
                           QHBoxLayout, QSizePolicy, QToolButton)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QMargins
from PyQt6.QtGui import QIcon, QAction, QFont, QCursor, QColor, QPainter, QPixmap

from utils.list_repository import ListRepository


class SpotifyIconProvider:
    """Provider for Spotify-style icons using text characters."""
    
    # Icon unicode characters
    HOME = "🏠"
    SEARCH = "🔍"
    LIBRARY = "📚"
    PLUS = "+"
    MUSIC = "♪"
    HEART = "♥"
    HEART_FILLED = "❤"
    SETTINGS = "⚙"
    COLLECTION = "📁"
    
    @classmethod
    def get_icon(cls, name: str, color: QColor = QColor(179, 179, 179), size: int = 16) -> QIcon:
        """
        Get a Spotify-style icon.
        
        Args:
            name: Icon name
            color: Icon color
            size: Icon size
            
        Returns:
            QIcon with the requested icon
        """
        # Get the icon character
        char = cls.HOME
        if name == "home":
            char = cls.HOME
        elif name == "search":
            char = cls.SEARCH
        elif name == "library":
            char = cls.LIBRARY
        elif name == "plus":
            char = cls.PLUS
        elif name == "music":
            char = cls.MUSIC
        elif name == "heart":
            char = cls.HEART
        elif name == "heart-filled":
            char = cls.HEART_FILLED
        elif name == "settings":
            char = cls.SETTINGS
        elif name == "collection":
            char = cls.COLLECTION
        
        # Create a pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Draw the icon
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setPen(color)
        # Convert float to int for font size - fixes the error
        painter.setFont(QFont("Segoe UI", int(size * 0.75)))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, char)
        painter.end()
        
        return QIcon(pixmap)


class SpotifyNav(QFrame):
    """A Spotify-style navigation item."""
    
    clicked = pyqtSignal(str, object)  # Signal emitted when clicked (item_id, item_data)
    
    def __init__(self, item_id: str, text: str, icon_name: str = None, item_data: Any = None, parent=None):
        """
        Initialize a Spotify navigation item.
        
        Args:
            item_id: Unique identifier for the item
            text: Display text
            icon_name: Icon name (optional)
            item_data: Associated data (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        self.item_id = item_id
        self.item_data = item_data
        
        self.setObjectName("spotifyNav")
        self.setFixedHeight(40)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(16)
        
        # Add icon if provided
        if icon_name:
            self.icon_label = QLabel()
            self.icon_label.setObjectName("spotifyNavIcon")
            self.icon_label.setFixedSize(24, 24)
            
            # Set icon
            icon = SpotifyIconProvider.get_icon(icon_name, QColor(179, 179, 179), 18)
            pixmap = icon.pixmap(18, 18)
            self.icon_label.setPixmap(pixmap)
            
            layout.addWidget(self.icon_label)
        else:
            # Add spacing if no icon
            layout.addSpacing(24)
        
        # Add text label
        self.label = QLabel(text)
        self.label.setObjectName("spotifyNavLabel")
        self.label.setFont(QFont("Gotham", 14, QFont.Weight.Bold))
        self.label.setStyleSheet("color: #B3B3B3;")
        layout.addWidget(self.label)
        
        # Add spacer to push content to the left
        layout.addStretch()
        
        # Set mouseover behavior
        self.setMouseTracking(True)
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle mouse events."""
        if obj == self:
            if event.type() == event.Type.Enter:
                self.setStyleSheet("background-color: #282828; border-radius: 4px;")
                self.label.setStyleSheet("color: #FFFFFF;")
                return True
            elif event.type() == event.Type.Leave:
                self.setStyleSheet("")
                self.label.setStyleSheet("color: #B3B3B3;")
                return True
            elif event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.clicked.emit(self.item_id, self.item_data)
                return True
        return super().eventFilter(obj, event)


class SpotifyLibraryHeader(QFrame):
    """Spotify-style library header with title."""
    
    # Keep the signal declaration even though we won't use the + button
    new_clicked = pyqtSignal()  # Signal emitted when the new button is clicked
    
    def __init__(self, parent=None):
        """
        Initialize a Spotify library header.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setObjectName("spotifyLibraryHeader")
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)
        
        # Add icon and title
        lib_icon = QLabel()
        lib_icon.setFixedSize(24, 24)
        lib_icon.setPixmap(SpotifyIconProvider.get_icon("library", QColor(179, 179, 179), 18).pixmap(18, 18))
        layout.addWidget(lib_icon)
        
        # Add title label
        title_label = QLabel("Your Library")
        title_label.setObjectName("spotifyLibraryTitle")
        title_label.setFont(QFont("Gotham", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #B3B3B3;")
        layout.addWidget(title_label)
        
        # Add spacer
        layout.addStretch()


class SpotifyCreateButton(QPushButton):
    """Spotify-style create button."""
    
    def __init__(self, text: str, parent=None):
        """
        Initialize a Spotify create button.
        
        Args:
            text: Button text
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.setObjectName("spotifyCreateButton")
        
        # Set style
        self.setStyleSheet("""
            QPushButton#spotifyCreateButton {
                color: #000000;
                background-color: #FFFFFF;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton#spotifyCreateButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton#spotifyCreateButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        self.setFont(QFont("Gotham", 12, QFont.Weight.Bold))


class SidebarListItem(QTreeWidgetItem):
    """A list item in the sidebar tree widget."""
    
    def __init__(self, list_info: Dict[str, Any], parent=None):
        """
        Initialize a sidebar list item.
        
        Args:
            list_info: Dictionary with list information
            parent: Parent item
        """
        # Create the item
        super().__init__(parent)
        
        # Set the text
        self.setText(0, list_info.get("title", "Untitled List"))
        
        # Store the list info
        self.list_info = list_info
        
        # Add album count in parentheses
        album_count = list_info.get("album_count", 0)
        if album_count > 0:
            self.setText(0, f"{self.text(0)} ({album_count})")
        
        # Set tooltip with description and details
        description = list_info.get("description", "")
        last_modified = list_info.get("last_modified", "")
        
        tooltip = f"{list_info.get('title', 'Untitled List')}\n"
        if description:
            tooltip += f"{description}\n"
        tooltip += f"Albums: {album_count}\n"
        if last_modified:
            tooltip += f"Last modified: {last_modified[:10]}"
        
        self.setToolTip(0, tooltip)


class SidebarManager(QScrollArea):
    """Manager for the application sidebar."""
    
    # Define signals
    item_selected = pyqtSignal(str, object)  # Signal emitted when an item is selected (item_id, item_data)
    create_new_list = pyqtSignal()  # Signal emitted when the user wants to create a new list
    import_list = pyqtSignal()  # Signal emitted when the user wants to import a list
    open_list = pyqtSignal(str)  # Signal emitted when a list should be opened (file_path)
    list_deleted = pyqtSignal(str)  # Signal emitted when a list is deleted (file_path)
    
    def __init__(self, list_repository: ListRepository, parent=None):
        """
        Initialize the sidebar manager.
        
        Args:
            list_repository: Repository for managing album lists
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store the list repository
        self.list_repository = list_repository
        
        # Set up the scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setObjectName("spotifySidebar")
        
        # Create the main widget
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("spotifySidebarWidget")
        
        # Set up the main layout
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setContentsMargins(0, 12, 0, 12)
        self.sidebar_layout.setSpacing(0)
        
        # Create Spotify-style navigation section
        self.create_navigation_section()
        
        # Add spacer between navigation and library
        spacer = QFrame()
        spacer.setObjectName("spotifySpacer")
        spacer.setFrameShape(QFrame.Shape.HLine)
        spacer.setFixedHeight(1)
        spacer.setStyleSheet("background-color: #282828;")
        self.sidebar_layout.addWidget(spacer)
        self.sidebar_layout.addSpacing(8)
        
        # Create library section
        self.create_library_section()
        
        # Remove the stretcher that was here
        # self.sidebar_layout.addStretch(1)
        
        # Add "Create List" button like Spotify's "Create Playlist"
        self.create_button = SpotifyCreateButton("Create List")
        self.create_button.clicked.connect(self.create_new_list.emit)
        self.sidebar_layout.addSpacing(16)
        self.sidebar_layout.addWidget(self.create_button, 0, Qt.AlignmentFlag.AlignHCenter)
        
        # Set the widget
        self.setWidget(self.sidebar_widget)

        # Load CSS from file with better error handling
        from PyQt6.QtCore import QFile, QTextStream
        import os
        
        # Try different paths to find the CSS file
        css_path = "views/resources/spotify_sidebar.css"
        if not os.path.exists(css_path):
            # Try alternative path relative to the current file
            alt_path = os.path.join(os.path.dirname(__file__), "resources", "spotify_sidebar.css")
            if os.path.exists(alt_path):
                css_path = alt_path
            else:
                try:
                    from resources import get_resource_path
                    alt_path2 = get_resource_path("spotify_sidebar.css")
                    if os.path.exists(alt_path2):
                        css_path = alt_path2
                except Exception as e:
                    print(f"Error getting resource path: {e}")
        
        # Load CSS from file
        css_file = QFile(css_path)
        if css_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(css_file)
            self.setStyleSheet(stream.readAll())
            css_file.close()
        else:
            print(f"Warning: Could not open CSS file at {css_path}")
            # Fall back to direct styling for the button
            self.create_button.setStyleSheet("""
                QPushButton {
                    color: #000000;
                    background-color: #FFFFFF;
                    border: none;
                    border-radius: 20px;
                    padding: 8px 16px;
                    font-weight: bold;
                    margin: 16px 20px;
                    min-height: 32px;
                }
                QPushButton:hover {
                    background-color: #F0F0F0;
                }
                QPushButton:pressed {
                    background-color: #E0E0E0;
                }
            """)

        # Set fixed width
        self.setFixedWidth(220)
    
    def create_navigation_section(self) -> None:
        """Create the Spotify-style navigation section."""
        # Add Home
        home_nav = SpotifyNav("home", "Home", "home")
        home_nav.clicked.connect(self.item_selected.emit)
        self.sidebar_layout.addWidget(home_nav)
        
        # Add Search
        search_nav = SpotifyNav("search", "Search", "search")
        search_nav.clicked.connect(self.item_selected.emit)
        self.sidebar_layout.addWidget(search_nav)
        
        # Add spacing after navigation items
        self.sidebar_layout.addSpacing(8)
    
    def create_library_section(self) -> None:
        """Create the library section with Spotify styling."""
        # Create the library header with buttons
        self.library_header = SpotifyLibraryHeader()
        # No longer connect to the new_clicked signal since we removed the button
        self.sidebar_layout.addWidget(self.library_header)
        
        # Add spacing
        self.sidebar_layout.addSpacing(8)
        
        # Create the tree widget for lists
        self.lists_tree = QTreeWidget()
        self.lists_tree.setObjectName("spotifyLibraryTree")
        self.lists_tree.setHeaderHidden(True)
        self.lists_tree.setIndentation(16)
        self.lists_tree.setFrameShape(QFrame.Shape.NoFrame)
        self.lists_tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.lists_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lists_tree.customContextMenuRequested.connect(self.show_list_context_menu)
        self.lists_tree.itemDoubleClicked.connect(self.handle_list_double_clicked)
        
        # Apply Spotify font
        tree_font = QFont("Gotham", 12)
        self.lists_tree.setFont(tree_font)
        
        # Add the tree widget to the layout with stretch factor 1 to make it expand
        self.sidebar_layout.addWidget(self.lists_tree, 1)  # Change from 0 to 1
        
        # Populate the lists
        self.refresh_lists()
    
    def refresh_lists(self) -> None:
        """Refresh the lists displayed in the sidebar."""
        # Save expansion state before refreshing
        expansion_state = {}
        for i in range(self.lists_tree.topLevelItemCount()):
            item = self.lists_tree.topLevelItem(i)
            item_id = item.data(0, Qt.ItemDataRole.UserRole)
            if item_id:
                expansion_state[item_id] = item.isExpanded()
        
        # Clear the tree
        self.lists_tree.clear()
        
        # Add "All Lists" top-level item
        all_lists_item = QTreeWidgetItem(self.lists_tree)
        all_lists_item.setText(0, "All Lists")
        all_lists_item.setData(0, Qt.ItemDataRole.UserRole, "all_lists")
        all_lists_item.setFont(0, QFont("Gotham", 12, QFont.Weight.Medium))
        
        # Add lists to the "All Lists" item
        lists = self.list_repository.get_all_lists()
        for list_info in lists:
            SidebarListItem(list_info, all_lists_item)
        
        # Add "Recent Lists" top-level item
        recent_lists_item = QTreeWidgetItem(self.lists_tree)
        recent_lists_item.setText(0, "Recent Lists")
        recent_lists_item.setData(0, Qt.ItemDataRole.UserRole, "recent_lists")
        recent_lists_item.setFont(0, QFont("Gotham", 12, QFont.Weight.Medium))
        
        # Add recent lists
        recent_lists = self.list_repository.get_recent_lists()
        for list_info in recent_lists:
            SidebarListItem(list_info, recent_lists_item)
        
        # Removed "Liked Lists" section
        
        # Add "Collections" top-level item
        collections_item = QTreeWidgetItem(self.lists_tree)
        collections_item.setText(0, "Collections")
        collections_item.setData(0, Qt.ItemDataRole.UserRole, "collections")
        collections_item.setFont(0, QFont("Gotham", 12, QFont.Weight.Bold))  # Make it bold to stand out
        
        # Get collections
        collections = self.list_repository.get_collections()
        print(f"Refreshing collections: {collections.keys()}")  # Debug output
        
        # Add collections and their lists
        collection_items = {}
        for collection_name, collection_lists in collections.items():
            # Create the collection item
            collection_item = QTreeWidgetItem(collections_item)
            collection_item.setText(0, collection_name)
            collection_item.setData(0, Qt.ItemDataRole.UserRole, f"collection:{collection_name}")
            collection_item.setFont(0, QFont("Gotham", 11))
            collection_items[collection_name] = collection_item
            
            # Add lists to the collection
            for list_info in collection_lists:
                SidebarListItem(list_info, collection_item)
        
        # Restore expansion state
        for i in range(self.lists_tree.topLevelItemCount()):
            item = self.lists_tree.topLevelItem(i)
            item_id = item.data(0, Qt.ItemDataRole.UserRole)
            if item_id in expansion_state:
                item.setExpanded(expansion_state[item_id])
            else:
                # Default expansion for items we've never seen before
                item.setExpanded(True)
        
        # IMPORTANT: Always make Collections visible and expanded
        collections_item.setExpanded(True)
        
        # Make sure the Collections section is always visible
        self.lists_tree.scrollToItem(collections_item)
        
        # Highlight the Collections item to draw attention to it
        self.lists_tree.setCurrentItem(collections_item)
        
        # Refresh the view to ensure everything is displayed properly
        self.lists_tree.update()


    def remember_collection_expansion_state(self) -> None:
        """
        Store the current expansion state of collections for later restoration.
        Should be called before operations like rename/create that refresh the tree.
        """
        if not hasattr(self, 'collection_expansion_state'):
            self.collection_expansion_state = {}
        
        # Find the collections item
        for i in range(self.lists_tree.topLevelItemCount()):
            item = self.lists_tree.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == "collections":
                # Save overall collections expansion
                self.collection_expansion_state["collections"] = item.isExpanded()
                
                # Save individual collection expansion states
                for j in range(item.childCount()):
                    child = item.child(j)
                    item_id = child.data(0, Qt.ItemDataRole.UserRole)
                    if item_id and item_id.startswith("collection:"):
                        collection_name = item_id.split(":", 1)[1]
                        self.collection_expansion_state[f"collection:{collection_name}"] = child.isExpanded()
                break

    def handle_list_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Handle double-clicking on a list item.
        
        Args:
            item: The clicked item
            column: The clicked column
        """
        # Get the item type
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        
        if isinstance(item, SidebarListItem):
            # Open the list
            file_path = item.list_info.get("file_path")
            if file_path:
                self.open_list.emit(file_path)
        elif item_type and item_type.startswith("collection:"):
            # Toggle expansion of collection
            item.setExpanded(not item.isExpanded())
    
    def show_list_context_menu(self, position: QPoint) -> None:
        """
        Show the context menu for a list item.
        
        Args:
            position: Position where the menu should be shown
        """
        # Get the item at the position
        item = self.lists_tree.itemAt(position)
        if not item:
            return
        
        # Get the item type
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        
        # Create the context menu with Spotify styling
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #282828;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 8px 0px;
            }
            QMenu::item {
                padding: 8px 24px;
            }
            QMenu::item:selected {
                background-color: #333333;
            }
            QMenu::separator {
                height: 1px;
                background-color: #333333;
                margin: 4px 8px;
            }
        """)
        
        if isinstance(item, SidebarListItem):
            # List item context menu
            file_path = item.list_info.get("file_path")
            
            # Add "Open" action
            open_action = QAction("Open", menu)
            open_action.triggered.connect(lambda: self.open_list.emit(file_path))
            menu.addAction(open_action)
            
            # Removed "Add to / Remove from Liked Lists" action
            
            # Add "Add to Collection" submenu
            add_to_collection_menu = QMenu("Add to Collection", menu)
            add_to_collection_menu.setStyleSheet(menu.styleSheet())
            
            # Get all collections
            collections = self.list_repository.get_collections()
            
            for collection_name in collections.keys():
                collection_action = QAction(collection_name, add_to_collection_menu)
                collection_action.triggered.connect(
                    lambda checked, cn=collection_name: self.add_to_collection(file_path, cn))
                add_to_collection_menu.addAction(collection_action)
            
            # Add "New Collection" action
            add_to_collection_menu.addSeparator()
            new_collection_action = QAction("Create New Collection", add_to_collection_menu)
            new_collection_action.triggered.connect(
                lambda: self.create_new_collection_and_add(file_path))
            add_to_collection_menu.addAction(new_collection_action)
            
            menu.addMenu(add_to_collection_menu)
            
            # Add separator
            menu.addSeparator()
            
            # Add "Delete" action
            delete_action = QAction("Delete", menu)
            delete_action.triggered.connect(lambda: self.delete_list(file_path))
            menu.addAction(delete_action)
        
        elif item_type and item_type.startswith("collection:"):
            # Collection item context menu
            collection_name = item_type.split(":", 1)[1]
            
            # Add "Rename" action
            rename_action = QAction("Rename", menu)
            rename_action.triggered.connect(lambda: self.rename_collection(collection_name))
            menu.addAction(rename_action)
            
            # Add "Delete" action
            delete_action = QAction("Delete", menu)
            delete_action.triggered.connect(lambda: self.delete_collection(collection_name))
            menu.addAction(delete_action)
        
        elif item_type == "collections":
            # Collections top-level item context menu
            add_action = QAction("Create New Collection", menu)
            add_action.triggered.connect(self.create_new_collection)
            menu.addAction(add_action)
        
        # Show the menu if it has actions
        if not menu.isEmpty():
            menu.exec(QCursor.pos())
    
    def add_to_collection(self, file_path: str, collection_name: str) -> None:
        """
        Add a list to a collection.
        
        Args:
            file_path: Path to the list file
            collection_name: Name of the collection
        """
        self.list_repository.add_to_collection(file_path, collection_name)
        self.refresh_lists()
    
    def create_new_collection(self) -> None:
        """Create a new collection."""
        name, ok = QInputDialog.getText(
            self, "Create Collection", "Collection name:")  # Changed from "Folder"
        
        if ok and name:
            # Remember expansion state before refreshing
            if hasattr(self, 'remember_collection_expansion_state'):
                self.remember_collection_expansion_state()
                
            self.list_repository.create_collection(name)
            self.refresh_lists()
            
            # Ensure collections item is expanded
            for i in range(self.lists_tree.topLevelItemCount()):
                item = self.lists_tree.topLevelItem(i)
                if item.data(0, Qt.ItemDataRole.UserRole) == "collections":
                    item.setExpanded(True)
                    
                    # Find and select the new collection
                    for j in range(item.childCount() - 1):  # -1 to skip the "Add Collection" item
                        child = item.child(j)
                        if child.text(0) == name:
                            self.lists_tree.setCurrentItem(child)
                            break
                    break
    
    def create_new_collection_and_add(self, file_path: str) -> None:
        """
        Create a new collection and add a list to it.
        
        Args:
            file_path: Path to the list file
        """
        name, ok = QInputDialog.getText(
            self, "Create Collection", "Collection name:")  # Changed from "Folder"
        
        if ok and name:
            self.list_repository.create_collection(name)
            self.list_repository.add_to_collection(file_path, name)
            self.refresh_lists()
            
            # Show confirmation message
            QMessageBox.information(
                self, "Success", 
                f"Added list to new collection '{name}'")  # Changed terminology
    

    def rename_collection(self, collection_name: str) -> None:
        """
        Rename a collection.
        
        Args:
            collection_name: Current name of the collection
        """
        new_name, ok = QInputDialog.getText(
            self, "Rename Collection", "New name:", text=collection_name)  # Changed terminology
        
        if ok and new_name and new_name != collection_name:
            # Remember expansion state before refreshing
            if hasattr(self, 'remember_collection_expansion_state'):
                self.remember_collection_expansion_state()
                
            success = self.list_repository.rename_collection(collection_name, new_name)
            if success:
                self.refresh_lists()
            else:
                QMessageBox.warning(
                    self, "Rename Failed", 
                    "Could not rename collection. A collection with that name may already exist.")
    
    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of the collection
        """
        reply = QMessageBox.question(
            self, "Delete Collection",  # Changed terminology
            f"Are you sure you want to delete the collection '{collection_name}'?\n\n"
            "The lists in the collection will not be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remember expansion state before refreshing
            if hasattr(self, 'remember_collection_expansion_state'):
                self.remember_collection_expansion_state()
                
            success = self.list_repository.delete_collection(collection_name)
            if success:
                self.refresh_lists()
    
    def delete_list(self, file_path: str) -> None:
        """
        Delete a list.
        
        Args:
            file_path: Path to the list file
        """
        # Get the list info
        list_info = None
        for info in self.list_repository.get_all_lists():
            if info.get("file_path") == file_path:
                list_info = info
                break
        
        if not list_info:
            return
        
        title = list_info.get("title", "Untitled List")
        
        reply = QMessageBox.question(
            self, "Delete List",
            f"Are you sure you want to delete the list '{title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.list_repository.delete_list(file_path)
            if success:
                self.list_deleted.emit(file_path)
                self.refresh_lists()