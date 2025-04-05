"""
views/sidebar_panel.py

Spotify-style sidebar panel implementation with Home and Library sections.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
                           QFrame, QHBoxLayout, QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QPixmap, QPainter, QBrush

from utils.logging_utils import get_module_logger
from resources import get_resource_path

# Get module logger
log = get_module_logger()


class SidebarButton(QPushButton):
    """Custom button for sidebar navigation items."""
    
    def __init__(self, text, icon_name=None, parent=None):
        """Initialize the sidebar button."""
        super().__init__(text, parent)
        self.setObjectName("sidebarButton")
        
        # Set fixed height and layout characteristics
        self.setFixedHeight(40)
        self.setIconSize(QSize(20, 20))
        
        # Setup icon if provided
        if icon_name:
            # This would normally load an icon file
            # Since we don't have actual icon files, we'll create placeholder icons
            self.setIcon(self._create_placeholder_icon(icon_name))
        
        # Set up the styling
        self.setStyleSheet("""
            QPushButton#sidebarButton {
                background-color: transparent;
                color: #B3B3B3;
                border: none;
                border-radius: 4px;
                padding-left: 12px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton#sidebarButton:hover {
                background-color: #282828;
                color: #FFFFFF;
            }
            QPushButton#sidebarButton:checked {
                color: #FFFFFF;
                font-weight: bold;
            }
            QPushButton#sidebarButton:checked {
                border-left: 4px solid #1DB954;
                padding-left: 8px;  /* Adjust for the border */
            }
        """)
        
        # Make the button checkable (to show active state)
        self.setCheckable(True)
    
    def _create_placeholder_icon(self, icon_name):
        """Create a placeholder icon since we don't have actual icon files."""
        # Create a pixmap for the icon
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Create painter for drawing on the pixmap
        painter = QPainter(pixmap)
        
        # Set up the icon appearance based on the icon name
        if icon_name == "home":
            # Home icon (simplified house)
            painter.setPen(QColor(180, 180, 180))
            painter.setBrush(QBrush(QColor(180, 180, 180)))
            painter.drawRect(5, 10, 10, 7)  # House base
            painter.drawPolygon([QPoint(3, 10), QPoint(10, 3), QPoint(17, 10)])  # Roof
        elif icon_name == "library":
            # Library icon (books/shelves)
            painter.setPen(QColor(180, 180, 180))
            painter.drawRect(3, 5, 14, 3)   # Top shelf
            painter.drawRect(3, 10, 14, 3)  # Middle shelf
            painter.drawRect(3, 15, 14, 3)  # Bottom shelf
        elif icon_name == "collection":
            # Collection icon (folder)
            painter.setPen(QColor(180, 180, 180))
            painter.setBrush(QBrush(QColor(180, 180, 180, 100)))
            painter.drawRect(3, 7, 14, 10)  # Folder
        elif icon_name == "list":
            # List icon (three lines)
            painter.setPen(QColor(180, 180, 180))
            painter.drawLine(5, 5, 15, 5)   # Top line
            painter.drawLine(5, 10, 15, 10) # Middle line
            painter.drawLine(5, 15, 15, 15) # Bottom line
        elif icon_name == "plus":
            # Plus icon
            painter.setPen(QColor(180, 180, 180))
            painter.drawLine(10, 5, 10, 15)  # Vertical line
            painter.drawLine(5, 10, 15, 10)  # Horizontal line
        else:
            # Default - just draw a circle
            painter.setPen(QColor(180, 180, 180))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(3, 3, 14, 14)
        
        painter.end()
        return QIcon(pixmap)


class SidebarHeader(QWidget):
    """Header widget for sidebar sections."""
    
    def __init__(self, text, parent=None):
        """Initialize the sidebar header."""
        super().__init__(parent)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 4)
        
        # Create label
        label = QLabel(text.upper())
        label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        label.setStyleSheet("color: #B3B3B3;")
        
        # Add label to layout
        layout.addWidget(label)
        
        # Make it fixed height
        self.setFixedHeight(32)


class CollectionTreeWidget(QTreeWidget):
    """Custom tree widget for collections with Spotify styling."""
    
    def __init__(self, parent=None):
        """Initialize the collection tree widget."""
        super().__init__(parent)
        
        # Set up basic properties
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setAnimated(True)
        self.setIndentation(20)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Set up the styling
        self.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
            }
            QTreeWidget::item {
                height: 32px;
                padding-left: 6px;
                border-radius: 4px;
                color: #B3B3B3;
            }
            QTreeWidget::item:hover {
                background-color: #282828;
                color: #FFFFFF;
            }
            QTreeWidget::item:selected {
                background-color: #333333;
                color: #FFFFFF;
                font-weight: bold;
            }
            QTreeWidget::branch {
                background-color: transparent;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                image: url(:/icons/closed.png);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                image: url(:/icons/open.png);
            }
        """)
        
        # Create initial empty placeholder
        placeholder = QTreeWidgetItem(["No collections"])
        placeholder.setDisabled(True)
        self.addTopLevelItem(placeholder)


class SidebarPanel(QWidget):
    """Spotify-style sidebar panel with Home and Library sections."""
    
    # Define signals
    home_clicked = pyqtSignal()
    collection_clicked = pyqtSignal(str)
    list_clicked = pyqtSignal(str)
    create_list_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the sidebar panel."""
        super().__init__(parent)
        log.debug("Initializing SidebarPanel")
        
        # Set fixed width for the sidebar
        self.setFixedWidth(220)
        
        # Set the background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))  # Black background
        self.setPalette(palette)
        
        # Setup UI
        self._setup_ui()
        
        log.debug("SidebarPanel initialized")
    
    def _setup_ui(self):
        """Set up the user interface for the sidebar."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top logo section
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(16, 16, 16, 8)
        
        # Logo or app name
        logo_label = QLabel("SuShe NG")
        logo_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: #FFFFFF;")
        logo_layout.addWidget(logo_label)
        
        layout.addWidget(logo_widget)
        
        # Add some space
        layout.addSpacing(8)
        
        # Navigation buttons
        home_button = SidebarButton("Home", "home")
        home_button.clicked.connect(self.home_clicked.emit)
        layout.addWidget(home_button)
        
        library_button = SidebarButton("Your Library", "library")
        library_button.setChecked(True)  # Initially selected
        layout.addWidget(library_button)
        
        # Add spacing
        layout.addSpacing(16)
        
        # Library section
        library_header = SidebarHeader("My Library")
        layout.addWidget(library_header)
        
        # Scroll area for collections (in case there are many)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #121212;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #535353;
                border-radius: 4px;
                min-height: 30px;
                margin: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container widget for the scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(8, 4, 8, 8)
        scroll_layout.setSpacing(4)
        
        # Create collections tree
        self.collections_tree = CollectionTreeWidget()
        self.collections_tree.itemClicked.connect(self._handle_tree_item_clicked)
        scroll_layout.addWidget(self.collections_tree)
        
        # Set scroll widget
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area, 1)  # Give it stretch factor
        
        # Create new list button at bottom
        create_button = QPushButton("Create New List")
        create_button.setIcon(SidebarButton("", "plus")._create_placeholder_icon("plus"))
        create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        create_button.setFixedHeight(40)
        create_button.clicked.connect(self.create_list_clicked.emit)
        create_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #B3B3B3;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 8px;
                margin: 8px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #282828;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """)
        layout.addWidget(create_button)
    
    def _handle_tree_item_clicked(self, item, column):
        """Handle when a tree item is clicked."""
        # Check if it's a collection or a list
        parent = item.parent()
        
        if parent is None:
            # This is a collection
            log.debug(f"Collection clicked: {item.text(0)}")
            self.collection_clicked.emit(item.text(0))
        else:
            # This is a list
            log.debug(f"List clicked: {item.text(0)}")
            # Get the file path from item data
            file_path = item.data(0, Qt.ItemDataRole.UserRole)
            if file_path:
                self.list_clicked.emit(file_path)
    
    def populate_collections(self, collections_data):
        """
        Populate the collections tree with data.
        
        Args:
            collections_data: Dictionary mapping collection names to lists of list info
        """
        log.debug(f"Populating collections tree with {len(collections_data)} collections")
        
        # Clear the tree first
        self.collections_tree.clear()
        
        # Add collections and their lists
        for collection_name, lists in collections_data.items():
            # Create collection item
            collection_item = QTreeWidgetItem([collection_name])
            collection_item.setIcon(0, SidebarButton("", "collection")._create_placeholder_icon("collection"))
            self.collections_tree.addTopLevelItem(collection_item)
            
            # Add lists to this collection
            for list_info in lists:
                list_item = QTreeWidgetItem([list_info.get("title", "Untitled List")])
                list_item.setIcon(0, SidebarButton("", "list")._create_placeholder_icon("list"))
                
                # Store the file path in the item data for later retrieval
                list_item.setData(0, Qt.ItemDataRole.UserRole, list_info.get("file_path"))
                
                collection_item.addChild(list_item)
            
            # Expand the collection
            collection_item.setExpanded(True)
        
        # If no collections, add a placeholder
        if len(collections_data) == 0:
            placeholder = QTreeWidgetItem(["No collections"])
            placeholder.setDisabled(True)
            self.collections_tree.addTopLevelItem(placeholder)
    
    def select_list(self, file_path):
        """
        Select a list in the tree.
        
        Args:
            file_path: Path to the list file
        """
        # Find the item with this file path
        for i in range(self.collections_tree.topLevelItemCount()):
            collection_item = self.collections_tree.topLevelItem(i)
            
            for j in range(collection_item.childCount()):
                list_item = collection_item.child(j)
                item_path = list_item.data(0, Qt.ItemDataRole.UserRole)
                
                if item_path == file_path:
                    # Found the item, select it
                    self.collections_tree.setCurrentItem(list_item)
                    return
        
        # If we get here, item wasn't found
        log.debug(f"List not found in sidebar: {file_path}")