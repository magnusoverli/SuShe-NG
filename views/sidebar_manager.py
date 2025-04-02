"""
views/sidebar_manager.py

Manager for the application sidebar with Spotify-inspired design.
"""
from typing import Dict, Any

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                           QScrollArea, QFrame, QMenu, QInputDialog,
                           QMessageBox, QTreeWidget, QTreeWidgetItem,
                           QHBoxLayout, QStyledItemDelegate, QStyleOptionViewItem)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import QIcon, QAction, QFont, QCursor, QColor, QPainter, QPixmap, QBrush

from utils.list_repository import ListRepository


class SpotifyIconProvider:
    """Provider for Spotify-style SVG icons."""
    
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
        # Path to SVG icons
        from resources import get_resource_path, resource_exists
        
        icon_path = f"icons/{name}.svg"
        if resource_exists(icon_path):
            full_path = get_resource_path(icon_path)
            icon = QIcon(full_path)
        else:
            # Fallback to text-based icons if SVG not found
            char = cls._get_fallback_char(name)
            
            # Create a pixmap
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            # Draw the icon
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.setPen(color)
            painter.setFont(QFont("Segoe UI", int(size * 0.75)))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, char)
            painter.end()
            
            icon = QIcon(pixmap)
        
        return icon

    # New method to add to SpotifyIconProvider class
    @staticmethod
    def _get_fallback_char(name: str) -> str:
        """Get fallback text character for an icon name."""
        if name == "home":
            return "🏠"
        elif name == "search":
            return "🔍"
        elif name == "library":
            return "📚"
        elif name == "plus":
            return "+"
        elif name == "music":
            return "♪"
        elif name == "heart":
            return "♥"
        elif name == "heart-filled":
            return "❤"
        elif name == "settings":
            return "⚙"
        elif name == "collection":
            return "📁"
        else:
            return "•"

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
    """A list item in the sidebar tree widget with Spotify styling."""
    
    def __init__(self, list_info: Dict[str, Any], parent=None):
        """
        Initialize a sidebar list item.
        
        Args:
            list_info: Dictionary with list information
            parent: Parent item
        """
        # Create the item
        super().__init__(parent)
        
        # Set clean title text - Spotify uses very clean labels
        self.setText(0, list_info.get("title", "Untitled List"))
        
        # Store the list info
        self.list_info = list_info
        
        # Add album count in parentheses - Spotify style
        album_count = list_info.get("album_count", 0)
        if album_count > 0:
            self.setText(0, f"{self.text(0)} ({album_count})")
        
        # Set informative tooltip
        description = list_info.get("description", "")
        last_modified = list_info.get("last_modified", "")
        
        tooltip = f"{list_info.get('title', 'Untitled List')}"
        if description:
            tooltip += f"\n{description}"
        tooltip += f"\n{album_count} albums"
        if last_modified:
            tooltip += f"\nLast updated {last_modified[:10]}"
        
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
        
        # Initialize tree_states dictionary
        self.tree_states = {}
        
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
        
        # Add "Create List" button like Spotify's "Create Playlist"
        self.create_button = SpotifyCreateButton("Create List")
        self.create_button.clicked.connect(self.create_new_list.emit)
        self.sidebar_layout.addSpacing(16)
        self.sidebar_layout.addWidget(self.create_button, 0, Qt.AlignmentFlag.AlignHCenter)
        
        # Set the widget
        self.setWidget(self.sidebar_widget)

        # Load stylesheet using our reliable method
        self.load_sidebar_stylesheet()

        # Get sidebar width from config
        sidebar_width = 220  # Default width
        
        if hasattr(list_repository, 'config'):
            config_width = list_repository.config.get("sidebar/width")
            if config_width is not None:
                try:
                    sidebar_width = int(config_width)
                except (ValueError, TypeError):
                    # If config value isn't a valid integer, use default
                    sidebar_width = 220
        
        # Set the sidebar width
        self.setFixedWidth(sidebar_width)

    def _update_expansion_indicators(self):
        """Update the expansion indicator state for all items."""
        # Update top-level items
        for i in range(self.lists_tree.topLevelItemCount()):
            item = self.lists_tree.topLevelItem(i)
            item.setData(0, Qt.ItemDataRole.UserRole + 1, item.isExpanded())
            
            # Update children
            for j in range(item.childCount()):
                child = item.child(j)
                child.setData(0, Qt.ItemDataRole.UserRole + 1, child.isExpanded())

    def load_sidebar_stylesheet(self):
        """Load the sidebar stylesheet in a reliable way."""
        try:
            # Use the resource module to get the path
            from resources import get_resource_path
            import os
            
            # First try to get the file through the resource system
            css_path = get_resource_path("spotify_sidebar.css")
            
            # If that fails, try looking in views/resources
            if not os.path.exists(css_path):
                # Try the views/resources directory
                module_dir = os.path.dirname(__file__)
                css_path = os.path.join(module_dir, "resources", "spotify_sidebar.css")
            
            # Load the stylesheet
            if os.path.exists(css_path):
                with open(css_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
                    return True
            else:
                print(f"Warning: Could not find CSS file at any location")
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
                return False
        except Exception as e:
            print(f"Error loading sidebar stylesheet: {e}")
            return False
    
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
    
    def refresh_lists(self) -> None:
        """Refresh the lists displayed in the sidebar."""
        # Save expansion state before refreshing
        self.save_tree_state()
        
        # Clear the tree
        self.lists_tree.clear()
        
        # 1. Add "Collections" at the top
        collections_item = QTreeWidgetItem(self.lists_tree)
        collections_item.setText(0, "Collections")
        collections_item.setData(0, Qt.ItemDataRole.UserRole, "collections")
        # Set visible indicator for expandable items
        collections_item.setData(0, Qt.ItemDataRole.UserRole + 1, True)  # Show as expanded by default
        collections_item.setFont(0, QFont("Segoe UI", 12, QFont.Weight.Bold))
        
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
            # Set expansion indicator flag
            collection_item.setData(0, Qt.ItemDataRole.UserRole + 1, False)  # Default collapsed
            collection_item.setFont(0, QFont("Segoe UI", 11))
            collection_items[collection_name] = collection_item
            
            # Add lists to the collection
            for list_info in collection_lists:
                SidebarListItem(list_info, collection_item)
        
        # 2. Add "Recent Lists" below Collections
        recent_lists_item = QTreeWidgetItem(self.lists_tree)
        recent_lists_item.setText(0, "Recent Lists")
        recent_lists_item.setData(0, Qt.ItemDataRole.UserRole, "recent_lists")
        # Set visible indicator for expandable items
        recent_lists_item.setData(0, Qt.ItemDataRole.UserRole + 1, True)  # Show as expanded by default
        recent_lists_item.setFont(0, QFont("Segoe UI", 12, QFont.Weight.Medium))
        
        # Add recent lists
        recent_lists = self.list_repository.get_recent_lists()
        for list_info in recent_lists:
            SidebarListItem(list_info, recent_lists_item)
        
        # Restore expansion state
        self.restore_tree_state()
        
        # Update expansion indicators based on current state
        self._update_expansion_indicators()
        
        # Refresh the view
        self.lists_tree.update()
    
    def create_library_section(self) -> None:
        """Create the library section with Spotify styling."""
        # Create the library header with buttons
        self.library_header = SpotifyLibraryHeader()
        self.sidebar_layout.addWidget(self.library_header)
        
        # Add spacing
        self.sidebar_layout.addSpacing(8)
        
        # Create the tree widget for lists
        self.lists_tree = QTreeWidget()
        self.lists_tree.setObjectName("spotifyLibraryTree")
        self.lists_tree.setHeaderHidden(True)
        self.lists_tree.setIndentation(20)  # Slightly increased for better visibility
        self.lists_tree.setFrameShape(QFrame.Shape.NoFrame)
        self.lists_tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.lists_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lists_tree.customContextMenuRequested.connect(self.show_list_context_menu)
        
        # Connect to item clicked to handle expansion
        self.lists_tree.itemClicked.connect(self.handle_item_clicked)
        
        # Important: disable automatic expand/collapse on double-click
        # We'll handle expansions manually
        self.lists_tree.setExpandsOnDoubleClick(False)
        
        # Connect to double click for opening lists
        self.lists_tree.itemDoubleClicked.connect(self.handle_list_double_clicked)
        
        # Apply Spotify font
        tree_font = QFont("Segoe UI", 12)  # Using Segoe UI as more reliable fallback
        self.lists_tree.setFont(tree_font)
        
        # Set tree properties to show icons
        self.lists_tree.setAnimated(True)
        
        # Add the tree widget to the layout with stretch factor 1
        self.sidebar_layout.addWidget(self.lists_tree, 1)
        
        # Add custom drawing delegate for tree items
        self.tree_delegate = SpotifyTreeDelegate()
        self.lists_tree.setItemDelegate(self.tree_delegate)
        
        # Populate the lists
        self.refresh_lists()
    
    def create_expansion_icons(self):
        """Create chevron icons for tree expansion if they don't exist."""
        import os
        from PyQt6.QtGui import QPainter, QPixmap, QPolygon
        from PyQt6.QtCore import QPoint
        
        # Create icons directory if needed
        icons_dir = os.path.join(os.path.dirname(__file__), "resources", "icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        # Create right chevron icon
        right_chevron_path = os.path.join(icons_dir, "chevron-right.png")
        if not os.path.exists(right_chevron_path):
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setPen(QColor(179, 179, 179))  # Light gray for icon
            # Draw a right-facing chevron
            points = [QPoint(6, 4), QPoint(10, 8), QPoint(6, 12)]
            painter.drawPolyline(QPolygon(points))
            painter.end()
            pixmap.save(right_chevron_path)
        
        # Create down chevron icon
        down_chevron_path = os.path.join(icons_dir, "chevron-down.png")
        if not os.path.exists(down_chevron_path):
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setPen(QColor(179, 179, 179))  # Light gray for icon
            # Draw a down-facing chevron
            points = [QPoint(4, 6), QPoint(8, 10), QPoint(12, 6)]
            painter.drawPolyline(QPolygon(points))
            painter.end()
            pixmap.save(down_chevron_path)
    
    def save_tree_state(self):
        """Save the expansion state of the sidebar tree."""
        if not hasattr(self, 'tree_states'):
            self.tree_states = {}
        
        # Only save if tree exists and has items
        if not hasattr(self, 'lists_tree') or self.lists_tree.topLevelItemCount() == 0:
            return
            
        # Clear previous states
        self.tree_states.clear()
        
        # Process top-level items
        for i in range(self.lists_tree.topLevelItemCount()):
            item = self.lists_tree.topLevelItem(i)
            item_id = item.data(0, Qt.ItemDataRole.UserRole)
            if item_id:
                self.tree_states[item_id] = item.isExpanded()
                
                # Process children (collections)
                for j in range(item.childCount()):
                    child = item.child(j)
                    child_id = child.data(0, Qt.ItemDataRole.UserRole)
                    if child_id:
                        self.tree_states[child_id] = child.isExpanded()

    def restore_tree_state(self):
        """Restore the saved expansion state."""
        if not hasattr(self, 'tree_states') or not self.tree_states:
            # Default: expand Collections and Recent Lists
            for i in range(self.lists_tree.topLevelItemCount()):
                item = self.lists_tree.topLevelItem(i)
                item_id = item.data(0, Qt.ItemDataRole.UserRole)
                if item_id in ["collections", "recent_lists"]:
                    item.setExpanded(True)
            return
        
        # Process top-level items
        for i in range(self.lists_tree.topLevelItemCount()):
            item = self.lists_tree.topLevelItem(i)
            item_id = item.data(0, Qt.ItemDataRole.UserRole)
            if item_id and item_id in self.tree_states:
                item.setExpanded(self.tree_states[item_id])
                
                # Process children (collections)
                for j in range(item.childCount()):
                    child = item.child(j)
                    child_id = child.data(0, Qt.ItemDataRole.UserRole)
                    if child_id and child_id in self.tree_states:
                        child.setExpanded(self.tree_states[child_id])
    
    def handle_item_clicked(self, item, column):
        """Handle item clicked with improved expansion behavior."""
        # Get the item type
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        
        # For collection items or top-level categories, toggle expansion
        if (item_type and (item_type.startswith("collection:") or 
                    item_type in ["collections", "recent_lists"])):
            # Save current expansion state
            was_expanded = item.isExpanded()
            
            # Toggle expansion state
            item.setExpanded(not was_expanded)
            
            # Update the expansion indicator
            item.setData(0, Qt.ItemDataRole.UserRole + 1, item.isExpanded())
            
            # Apply styling to show active state when expanded
            if item.isExpanded():
                item.setBackground(0, QBrush(QColor(40, 40, 40)))
            else:
                item.setBackground(0, QBrush(Qt.GlobalColor.transparent))
        
        # For SidebarListItem (music lists), don't change expansion but prepare for double-click
        elif isinstance(item, SidebarListItem):
            # Do nothing here - double click will handle opening
            pass

    def handle_list_double_clicked(self, item, column):
        """Handle double-clicking on a list item."""
        # If it's a list item, open it
        if isinstance(item, SidebarListItem):
            file_path = item.list_info.get("file_path")
            if file_path:
                self.open_list.emit(file_path)
    
    def set_sidebar_width(self, width: int):
        """
        Set the sidebar width and save to config.
        
        Args:
            width: New width in pixels
        """
        self.setFixedWidth(width)
        if hasattr(self.list_repository, 'config'):
            self.list_repository.config.set("sidebar/width", width)
    
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
        
        # Create the context menu - uses CSS from stylesheet
        menu = QMenu(self)
        
        if isinstance(item, SidebarListItem):
            # List item context menu
            file_path = item.list_info.get("file_path")
            
            # Add "Open" action
            open_action = QAction("Open", menu)
            open_action.triggered.connect(lambda: self.open_list.emit(file_path))
            menu.addAction(open_action)
            
            # Add "Add to Collection" submenu
            add_to_collection_menu = QMenu("Add to Collection", menu)
            
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
            self, "Create Collection", "Collection name:")
        
        if ok and name:
            # Save tree state before modifying
            self.save_tree_state()
                
            self.list_repository.create_collection(name)
            self.refresh_lists()
            
            # Ensure collections item is expanded
            for i in range(self.lists_tree.topLevelItemCount()):
                item = self.lists_tree.topLevelItem(i)
                if item.data(0, Qt.ItemDataRole.UserRole) == "collections":
                    item.setExpanded(True)
                    
                    # Find and select the new collection
                    for j in range(item.childCount()):
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
            self, "Create Collection", "Collection name:")
        
        if ok and name:
            self.list_repository.create_collection(name)
            self.list_repository.add_to_collection(file_path, name)
            self.refresh_lists()
            
            # Show confirmation message
            QMessageBox.information(
                self, "Success", 
                f"Added list to new collection '{name}'")
    
    def rename_collection(self, collection_name: str) -> None:
        """
        Rename a collection.
        
        Args:
            collection_name: Current name of the collection
        """
        new_name, ok = QInputDialog.getText(
            self, "Rename Collection", "New name:", text=collection_name)
        
        if ok and new_name and new_name != collection_name:
            # Save tree state before modifying
            self.save_tree_state()
                
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
            self, "Delete Collection",
            f"Are you sure you want to delete the collection '{collection_name}'?\n\n"
            "The lists in the collection will not be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Save tree state before modifying
            self.save_tree_state()
                
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

class SpotifyTreeDelegate(QStyledItemDelegate):
    """Custom delegate for drawing Spotify-style tree items with expansion indicators."""
    
    def paint(self, painter, option, index):
        """Custom paint method to show expansion indicators."""
        # Call the base class method first to draw the basic item
        super().paint(painter, option, index)
        
        # Get the item
        model = index.model()
        has_children = model.hasChildren(index)
        
        # Only draw expansion indicators for items that have children
        if has_children:
            # Determine the item's state (expanded/collapsed)
            is_expanded = index.model().data(index, Qt.ItemDataRole.UserRole + 1) or False
            
            # Calculate the indicator position
            rect = option.rect
            indicator_rect = QRect(rect.left() - 16, rect.top() + (rect.height() - 16) // 2, 16, 16)
            
            # Set up the painter
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw the expansion indicator (triangle)
            color = QColor(180, 180, 180)  # Light gray for the indicator
            if option.state & QStyleOptionViewItem.State.Selected:
                color = QColor(255, 255, 255)  # White if selected
                
            painter.setPen(color)
            painter.setBrush(QBrush(color))
            
            # Draw triangle based on expansion state
            if is_expanded:
                # Down arrow
                painter.drawText(indicator_rect, Qt.AlignmentFlag.AlignCenter, "▼")
            else:
                # Right arrow
                painter.drawText(indicator_rect, Qt.AlignmentFlag.AlignCenter, "▶")
                
            painter.restore()