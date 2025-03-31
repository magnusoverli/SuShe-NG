"""
Main window view for the SuShe NG application with Spotify-like design.
"""

import os
from datetime import date
from typing import List, Optional

from PyQt6.QtGui import (QAction, QIcon, QCloseEvent, QPixmap, QColor,
                    QPainter, QPen, QPainterPath, QBrush, QFont)
from PyQt6.QtWidgets import (QMainWindow, QTableView, QStatusBar, QSplitter,
                           QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QMessageBox,
                           QLabel, QPushButton, QLineEdit, QFrame, QScrollArea,
                           QSizePolicy, QToolButton, QMenu, QHeaderView, QListWidget,
                           QListWidgetItem, QStyledItemDelegate, QStyle)
from PyQt6.QtCore import (QSize, QPoint, Qt, QMargins, QEvent, QRect, QRectF, QModelIndex)

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
                
                # Check if album has a cover image
                if hasattr(album, 'cover_image') and album.cover_image:
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
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the main window.
        
        Args:
            config: Application configuration manager (optional)
        """
        print("MainWindow.__init__ starting...")
        try:
            super().__init__()
            print("Super initialized")
            
            # Store the configuration manager
            self.config = config or Config()
            print("Config stored")
            
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
            
            # Create the sidebar
            print("Creating sidebar...")
            self.sidebar = self.create_sidebar()
            print("Sidebar created")
            content_layout.addWidget(self.sidebar)
            print("Sidebar added to layout")
            
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
            
            # Create sample albums
            self.albums = self.create_sample_albums()
            
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

    def setup_table_view(self) -> None:
        """Set up the table view with appropriate settings."""
        print("setup_table_view starting...")
        try:
            print("Setting drag and drop...")
            self.table_view.setDragEnabled(True)
            self.table_view.setAcceptDrops(True)
            self.table_view.setDragDropMode(QTableView.DragDropMode.InternalMove)
            print("Setting selection behavior...")
            self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            print("Setting grid and colors...")
            self.table_view.setShowGrid(False)
            self.table_view.setAlternatingRowColors(True)
            
            print("Setting resize modes...")
            # More Spotify-like table settings
            try:
                print("Setting column 0 resize mode...")
                self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
                print("Setting column 1 resize mode...")
                self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
                print("Setting column 2 resize mode...")
                self.table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
                print("Setting column 3 resize mode...")
                self.table_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
                print("Setting column 4 resize mode...")
                self.table_view.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
                print("Setting column 5 resize mode...")
                self.table_view.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
            except Exception as resize_error:
                print(f"Error setting resize modes: {resize_error}")
                # Use a safer approach that doesn't require specific column knowledge
                print("Falling back to default resize mode...")
                self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            print("Setting column widths...")
            try:
                # Set column widths
                self.table_view.setColumnWidth(0, 300)  # Album name + cover
                self.table_view.setColumnWidth(1, 180)  # Artist
                self.table_view.setColumnWidth(2, 120)  # Release date
                self.table_view.setColumnWidth(3, 140)  # Genre 1
                self.table_view.setColumnWidth(4, 140)  # Genre 2
            except Exception as width_error:
                print(f"Error setting column widths: {width_error}")
            
            print("Setting header alignment...")
            self.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            print("Setting vertical header visibility...")
            self.table_view.verticalHeader().setVisible(False)
            print("Setting frame shape...")
            self.table_view.setFrameShape(QFrame.Shape.NoFrame)
            print("Setting selection mode...")
            self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            
            print("Setting row height...")
            # Set row height
            self.table_view.verticalHeader().setDefaultSectionSize(56)
            
            print("Setting header stylesheet...")
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
            print("setup_table_view completed")
        except Exception as e:
            import traceback
            print(f"Error in setup_table_view: {e}")
            traceback.print_exc()
            raise
    
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
        
        # Toggle status bar action
        toggle_status_bar_action = QAction("Toggle &Status Bar", self)
        toggle_status_bar_action.setShortcut("Ctrl+/")
        toggle_status_bar_action.triggered.connect(self.toggle_status_bar)
        view_menu.addAction(toggle_status_bar_action)
    
    def toggle_sidebar(self):
        """Toggle the visibility of the sidebar."""
        self.sidebar.setVisible(not self.sidebar.isVisible())
    
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
        print("create_sample_albums starting...")
        try:
            # Base directory for cover images
            cover_dir = "resources/covers"
            print(f"Cover directory: {cover_dir}")
            
            # Check if the directory exists, if not let's continue without images
            if not os.path.exists(cover_dir):
                print(f"Cover directory doesn't exist, creating: {cover_dir}")
                try:
                    os.makedirs(cover_dir)
                    print(f"Created directory: {cover_dir}")
                except Exception as dir_err:
                    print(f"Error creating cover directory: {dir_err}")
            else:
                print(f"Cover directory exists: {cover_dir}")
                print(f"Files in cover directory: {os.listdir(cover_dir) if os.path.isdir(cover_dir) else 'Not a directory'}")
            
            # Create albums with paths to cover images, they may not exist yet
            print("Creating album objects...")
            albums = [
                Album("Daft Punk", "Random Access Memories", date(2013, 5, 17), 
                    "Electronic", "Disco", "Grammy-winning album",
                    cover_image=os.path.join(cover_dir, "daft_punk_ram.jpg")),
                Album("Radiohead", "OK Computer", date(1997, 5, 21), 
                    "Alternative Rock", "Art Rock", "Critically acclaimed",
                    cover_image=os.path.join(cover_dir, "radiohead_okc.jpg")),
                Album("Kendrick Lamar", "To Pimp a Butterfly", date(2015, 3, 15), 
                    "Hip Hop", "Jazz Rap", "Masterpiece",
                    cover_image=os.path.join(cover_dir, "kendrick_tpab.jpg")),
                Album("Fleetwood Mac", "Rumours", date(1977, 2, 4), 
                    "Rock", "Pop Rock", "Classic album",
                    cover_image=os.path.join(cover_dir, "fleetwood_rumours.jpg")),
                Album("Amy Winehouse", "Back to Black", date(2006, 10, 27), 
                    "Soul", "R&B", "Breakthrough album",
                    cover_image=os.path.join(cover_dir, "amy_black.jpg")),
                Album("The Beatles", "Abbey Road", date(1969, 9, 26),
                    "Rock", "Pop Rock", "Iconic album cover",
                    cover_image=os.path.join(cover_dir, "beatles_abbey.jpg")),
                Album("Pink Floyd", "Dark Side of the Moon", date(1973, 3, 1),
                    "Progressive Rock", "Psychedelic Rock", "One of the best-selling albums of all time",
                    cover_image=os.path.join(cover_dir, "floyd_darkside.jpg")),
                Album("Michael Jackson", "Thriller", date(1982, 11, 30),
                    "Pop", "R&B", "Best-selling album worldwide",
                    cover_image=os.path.join(cover_dir, "jackson_thriller.jpg")),
                Album("Nirvana", "Nevermind", date(1991, 9, 24),
                    "Grunge", "Alternative Rock", "Defined a generation",
                    cover_image=os.path.join(cover_dir, "nirvana_nevermind.jpg")),
                Album("Adele", "21", date(2011, 1, 24),
                    "Soul", "Pop", "Multi-Grammy winner",
                    cover_image=os.path.join(cover_dir, "adele_21.jpg"))
            ]
            print(f"Created {len(albums)} album objects")
            print("create_sample_albums completed")
            return albums
        except Exception as e:
            import traceback
            print(f"Error in create_sample_albums: {e}")
            traceback.print_exc()
            raise
    
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