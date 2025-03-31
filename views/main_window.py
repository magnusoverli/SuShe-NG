"""
Main window view for the SuShe NG application with Spotify-like design.
"""

from datetime import date
from typing import List, Optional

from PyQt6.QtGui import QAction, QIcon, QCloseEvent, QPixmap, QColor
from PyQt6.QtWidgets import (QMainWindow, QTableView, QStatusBar, QSplitter,
                           QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QMessageBox,
                           QLabel, QPushButton, QLineEdit, QFrame, QScrollArea,
                           QSizePolicy, QToolButton, QMenu, QHeaderView, QListWidget,
                           QListWidgetItem, QStyledItemDelegate, QStyle)
from PyQt6.QtCore import QSize, QPoint, Qt, QMargins, QEvent

from models.album import Album
from models.album_table_model import AlbumTableModel
from utils.theme import SpotifyTheme
from utils.config import Config
from resources import get_resource_path, resource_exists
from metadata import ICON_PATH


class SidebarItem(QFrame):
    """Custom sidebar item with Spotify-like styling."""
    
    def __init__(self, text: str, icon_name: str = None, parent=None):
        """
        Initialize a sidebar item.
        
        Args:
            text: The item text
            icon_name: Optional icon name
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setObjectName("sidebarItem")
        self.setFixedHeight(40)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)
        
        # Add icon if provided
        if icon_name:
            icon = QLabel()
            # In a real application, you would load an actual icon
            # For now, we'll use a placeholder
            icon.setText("🔍" if icon_name == "search" else 
                         "🏠" if icon_name == "home" else
                         "📚" if icon_name == "library" else "📁")
            icon.setStyleSheet("color: #B3B3B3;")
            layout.addWidget(icon)
        
        # Add text
        self.label = QLabel(text)
        self.label.setStyleSheet("color: #B3B3B3; font-weight: bold;")
        layout.addWidget(self.label)
        
        layout.addStretch()
        
        # Install event filter for hover effects
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle events for hover effects."""
        if event.type() == QEvent.Type.Enter:
            self.label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
            return True
        elif event.type() == QEvent.Type.Leave:
            self.label.setStyleSheet("color: #B3B3B3; font-weight: bold;")
            return True
        return super().eventFilter(obj, event)


class AlbumTableDelegate(QStyledItemDelegate):
    """Custom delegate for album table to add Spotify-like styling."""
    
    def paint(self, painter, option, index):
        """Custom paint method to style table cells."""
        # Create a copy of the option to modify
        opt = option
        
        # If the item is selected, use Spotify's selection style
        if opt.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(opt.rect, QColor(66, 66, 66))
            opt.palette.setColor(opt.palette.ColorRole.Text, Qt.GlobalColor.white)
        else:
            # Alternate row colors
            if index.row() % 2 == 0:
                painter.fillRect(opt.rect, QColor(24, 24, 24))
            else:
                painter.fillRect(opt.rect, QColor(18, 18, 18))
        
        # Draw the text
        super().paint(painter, opt, index)


class MainWindow(QMainWindow):
    """Main application window with Spotify-like design."""
    
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
        self.setMinimumSize(1000, 700)
        
        # Set window icon if available
        if resource_exists(ICON_PATH):
            self.setWindowIcon(QIcon(get_resource_path(ICON_PATH)))
        
        # Create the central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create the main content area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create the sidebar
        self.sidebar = self.create_sidebar()
        content_layout.addWidget(self.sidebar)
        
        # Create the main view splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)
        content_layout.addWidget(self.splitter, 1)  # Give the splitter more space
        
        # Create the main panel
        self.main_panel = self.create_main_panel()
        self.splitter.addWidget(self.main_panel)
        
        # Set initial sizes for the splitter
        self.splitter.setSizes([220, 780])
        
        # Add the content widget to the main layout
        main_layout.addWidget(content_widget, 1)
        
        # Set the central widget
        self.setCentralWidget(central_widget)
        
        # Create the menu bar
        self.create_menu_bar()
        
        # Create the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        self.status_bar.setFixedHeight(24)
        
        # Apply Spotify-like dark theme
        self.apply_theme()
        
        # Restore window geometry from config
        self.restore_window_state()
    
    def create_sidebar(self) -> QWidget:
        """Create the Spotify-like sidebar."""
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(8)
        
        # Add sidebar items
        layout.addWidget(SidebarItem("Home", "home"))
        layout.addWidget(SidebarItem("Search", "search"))
        
        # Add a separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #282828; max-height: 1px;")
        layout.addWidget(separator)
        layout.addSpacing(8)
        
        # Add library section
        layout.addWidget(SidebarItem("Your Library", "library"))
        layout.addWidget(SidebarItem("All Albums"))
        layout.addWidget(SidebarItem("By Artist"))
        layout.addWidget(SidebarItem("By Genre"))
        layout.addWidget(SidebarItem("Recently Added"))
        
        # Add stretch to push items to the top
        layout.addStretch()
        
        return sidebar
    
    def create_main_panel(self) -> QWidget:
        """Create the main content panel with header and album table."""
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
        
        # Create and set up the table view
        self.table_view = QTableView()
        self.setup_table_view()
        
        # Create and set the model
        self.albums = self.create_sample_albums()
        self.model = AlbumTableModel(self.albums)
        self.table_view.setModel(self.model)
        
        # Set custom delegate for Spotify-like styling
        self.table_view.setItemDelegate(AlbumTableDelegate())
        
        # Add the table view to the layout
        layout.addWidget(self.table_view, 1)  # Give it stretch factor
        
        return panel
    
    def setup_table_view(self) -> None:
        """Set up the table view with appropriate settings."""
        self.table_view.setDragEnabled(True)
        self.table_view.setAcceptDrops(True)
        self.table_view.setDragDropMode(QTableView.DragDropMode.InternalMove)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setShowGrid(False)
        self.table_view.setAlternatingRowColors(True)
        
        # More Spotify-like table settings
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setFrameShape(QFrame.Shape.NoFrame)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        
        # Set row height
        self.table_view.verticalHeader().setDefaultSectionSize(56)
        
        # Customize the header
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
        
        # Recent files submenu
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        
        # Add another separator
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")
        
        # Toggle sidebar action
        toggle_sidebar_action = QAction("Toggle &Sidebar", self)
        toggle_sidebar_action.setShortcut("Ctrl+B")
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)
    
    def toggle_sidebar(self):
        """Toggle the visibility of the sidebar."""
        self.sidebar.setVisible(not self.sidebar.isVisible())
    
    def apply_theme(self) -> None:
        """Apply the Spotify-like theme to the window and its components."""
        # Use the updated Spotify theme
        SpotifyTheme.apply_to_window(self)
        
        # Additional styling for the Spotify-like components
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            #sidebar {
                background-color: #000000;
                border: none;
            }
            #sidebarItem {
                background-color: transparent;
                border-radius: 4px;
            }
            #sidebarItem:hover {
                background-color: #282828;
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
                 "Soul", "R&B", "Breakthrough album"),
            Album("The Beatles", "Abbey Road", date(1969, 9, 26),
                 "Rock", "Pop Rock", "Iconic album cover"),
            Album("Pink Floyd", "Dark Side of the Moon", date(1973, 3, 1),
                 "Progressive Rock", "Psychedelic Rock", "One of the best-selling albums of all time"),
            Album("Michael Jackson", "Thriller", date(1982, 11, 30),
                 "Pop", "R&B", "Best-selling album worldwide"),
            Album("Nirvana", "Nevermind", date(1991, 9, 24),
                 "Grunge", "Alternative Rock", "Defined a generation"),
            Album("Adele", "21", date(2011, 1, 24),
                 "Soul", "Pop", "Multi-Grammy winner")
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