"""
views/enhanced_drag_drop.py

Enhanced drag and drop functionality for table views.
"""

from PyQt6.QtGui import (QDrag, QPainter, QPixmap, QColor, QBrush, QPen, QFont, 
                    QFontMetrics, QLinearGradient, QImage)
from PyQt6.QtCore import Qt, QMimeData, QByteArray, QSize, QPoint, QModelIndex, QRect, QEvent
from PyQt6.QtWidgets import QStyle, QAbstractItemView

from utils.logging_utils import get_module_logger

# Get module logger
log = get_module_logger()


def apply_drag_drop_enhancements(table_view, table_model, table_delegate):
    """
    Apply drag and drop enhancements to the table components.
    
    Args:
        table_view: The QTableView instance
        table_model: The AlbumTableModel instance
        table_delegate: The AlbumTableDelegate instance
    """
    log.debug("Applying drag and drop enhancements")
    
    # 1. Enhance the table model's mime data method
    table_model.original_mime_data = table_model.mimeData
    table_model.mimeData = lambda indexes: enhanced_mime_data(table_model, indexes)
    
    # 2. Add the last_drag_source and last_drag_target attributes to the model
    table_model.last_drag_source = -1
    table_model.last_drag_target = -1
    
    # 3. Enhance the dropMimeData method
    table_model.original_drop_mime_data = table_model.dropMimeData
    table_model.dropMimeData = lambda data, action, row, column, parent: enhanced_drop_mime_data(
        table_model, data, action, row, column, parent)
    
    # 4. Override the startDrag method in the table view
    table_view.startDrag = lambda supportedActions: start_drag(table_view, supportedActions)
    table_view.create_drag_preview = lambda album_names: create_drag_preview(table_view, album_names)
    
    # Add property to track drag state
    table_view.isDragInProgress = False
    
    # 5. Enhance the delegate's paint method with drag handles
    # Store a reference to the original paint method outside the delegate to avoid recursion
    original_paint = table_delegate.paint
    
    # Create a wrapper function that will call our enhanced method
    def paint_wrapper(painter, option, index):
        paint_with_drag_handle(table_delegate, painter, option, index, original_paint)
    
    # Replace the paint method with our wrapper
    table_delegate.paint = paint_wrapper
    
    # 6. Configure table view for improved drag and drop experience
    table_view.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
    table_view.setDefaultDropAction(Qt.DropAction.MoveAction)
    table_view.setDragEnabled(True)
    table_view.setAcceptDrops(True)
    table_view.setDropIndicatorShown(True)
    
    # 7. Enable multiple selection for dragging multiple items
    table_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    
    # 8. Add hover tracking for drag handle indicators
    table_view.setMouseTracking(True)
    
    log.debug("Drag and drop enhancements applied")


def enhanced_mime_data(self, indexes):
    """
    Enhanced version of mimeData that creates a richer drag representation
    and includes all necessary data for the drag operation.
    
    Args:
        indexes: The indexes being dragged
        
    Returns:
        The enhanced MIME data
    """
    mime_data = QMimeData()
    
    # Get unique rows
    rows = set(index.row() for index in indexes if index.isValid())
    if not rows:
        log.debug("No valid rows for drag operation")
        return mime_data
    
    # Store row indices as before
    encoded_data = QByteArray()
    for row in rows:
        encoded_data.append(str(row).encode())
    mime_data.setData("application/x-album-row", encoded_data)
    
    # Store the number of rows being dragged
    mime_data.setData("application/x-album-count", QByteArray(str(len(rows)).encode()))
    
    # If we have album data, store the album names for rich preview
    album_names = []
    for row in rows:
        if row < len(self.albums):
            album_names.append(f"{self.albums[row].artist} - {self.albums[row].name}")
    
    if album_names:
        mime_data.setData("application/x-album-names", QByteArray("\n".join(album_names).encode()))
    
    log.debug(f"Created enhanced mime data for {len(rows)} rows")
    return mime_data


def start_drag(self, supportedActions):
    """
    Create a custom drag object with a rich visual representation.
    
    Args:
        supportedActions: The supported drag actions
    """
    indexes = self.selectedIndexes()
    if not indexes:
        log.debug("No indexes selected for drag")
        return
    
    # Get the model and unique rows
    model = self.model()
    rows = set(index.row() for index in indexes)
    
    log.debug(f"Starting drag operation for {len(rows)} rows")
    
    # Set drag in progress flag
    self.isDragInProgress = True
    
    # Create the MIME data
    mime_data = model.mimeData(indexes)
    
    # Create a pixmap for drag preview
    if mime_data.hasFormat("application/x-album-names"):
        album_names = bytes(mime_data.data("application/x-album-names")).decode().split("\n")
        log.debug(f"Creating rich drag preview with {len(album_names)} album names")
        drag_pixmap = self.create_drag_preview(album_names)
    else:
        # Fallback to a simple colored rectangle
        log.debug("Creating simple drag preview (no album names)")
        drag_pixmap = QPixmap(300, 70)
        drag_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(drag_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(40, 40, 40, 230)))
        painter.setPen(QPen(QColor(29, 185, 84), 2))
        painter.drawRoundedRect(0, 0, 300, 70, 10, 10)
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(drag_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Moving selection...")
        painter.end()
    
    # Create and execute the drag
    drag = QDrag(self)
    drag.setMimeData(mime_data)
    drag.setPixmap(drag_pixmap)
    drag.setHotSpot(QPoint(int(drag_pixmap.width() / 2), 20))
    
    # Add a drop indicator animation to enhance the drag effect
    self.setDragDropOverwriteMode(False)
    
    # Execute the drag
    log.debug("Executing drag operation")
    result = drag.exec(supportedActions)
    
    # Reset the drag in progress flag
    self.isDragInProgress = False
    
    log.debug(f"Drag operation completed with result: {result}")


def create_drag_preview(self, album_names):
    """
    Create a visually appealing drag preview with album names.
    
    Args:
        album_names: List of album names to display
        
    Returns:
        QPixmap with the drag preview
    """
    log.debug(f"Creating drag preview for {len(album_names)} albums")
    # Set maximum number of items to show
    max_items = 3
    display_names = album_names[:max_items]
    more_count = len(album_names) - max_items if len(album_names) > max_items else 0
    
    # Calculate size
    font = QFont("Segoe UI", 10)
    bold_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
    metrics = QFontMetrics(font)
    
    # Calculate maximum width needed
    max_width = 300  # Minimum width
    for name in display_names:
        width = metrics.horizontalAdvance(name) + 40  # Add padding
        max_width = max(max_width, min(width, 400))  # Cap at 400px
    
    # Height based on number of items
    row_height = 24
    total_height = (len(display_names) * row_height) + 30  # Base height plus padding
    
    # Add space for "and X more..." if needed
    if more_count > 0:
        total_height += row_height
    
    # Create the pixmap
    pixmap = QPixmap(max_width, total_height)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    # Create painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw background with gradient
    gradient = QLinearGradient(0, 0, 0, total_height)
    gradient.setColorAt(0, QColor(40, 40, 40, 240))
    gradient.setColorAt(1, QColor(30, 30, 30, 240))
    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(60, 60, 60), 1))
    painter.drawRoundedRect(0, 0, max_width, total_height, 10, 10)
    
    # Draw top accent bar (Spotify green)
    painter.setBrush(QBrush(QColor(29, 185, 84)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRect(0, 0, max_width, 4)
    
    # Draw album icon on the left
    icon_size = 24
    for i, name in enumerate(display_names):
        y_pos = 20 + (i * row_height)
        
        # Draw album icon placeholder
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.drawEllipse(15, y_pos, icon_size, icon_size)
        
        # Draw note symbol
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(QRect(15, y_pos, icon_size, icon_size), 
                         Qt.AlignmentFlag.AlignCenter, "♪")
        
        # Draw album name
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(font)
        
        # Elide text if too long
        text_rect = QRect(50, y_pos, max_width - 60, row_height)
        elided_text = metrics.elidedText(name, Qt.TextElideMode.ElideRight, text_rect.width())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, elided_text)
    
    # Draw "and X more..." if needed
    if more_count > 0:
        y_pos = 20 + (len(display_names) * row_height)
        painter.setPen(QPen(QColor(180, 180, 180)))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Normal))
        painter.drawText(QRect(50, y_pos, max_width - 60, row_height), 
                         Qt.AlignmentFlag.AlignVCenter, f"and {more_count} more...")
    
    painter.end()
    log.debug(f"Created drag preview pixmap: {pixmap.width()}x{pixmap.height()}")
    return pixmap


def enhanced_drop_mime_data(self, data, action, row, column, parent):
    """
    Enhanced version of dropMimeData that prepares for animation.
    
    Args:
        data: The MIME data being dropped
        action: The drop action
        row: The row where the data is dropped
        column: The column where the data is dropped
        parent: The parent index where the data is dropped
            
    Returns:
        True if the data was successfully handled, False otherwise
    """
    if not data.hasFormat("application/x-album-row"):
        log.debug("Drop data doesn't have album row format")
        return False
    
    if action == Qt.DropAction.IgnoreAction:
        log.debug("Drop action is IgnoreAction, accepting")
        return True
    
    encoded_data = data.data("application/x-album-row")
    source_row = int(encoded_data.data().decode())
    
    if row != -1:
        target_row = row
    elif parent.isValid():
        target_row = parent.row()
    else:
        target_row = self.rowCount()
    
    log.debug(f"Drop operation: source row {source_row} to target row {target_row}")
    
    if source_row == target_row or source_row == target_row - 1:
        log.debug("Invalid drop target (same position), rejecting")
        return False
    
    # Emit signals for custom animation
    self.beginResetModel()
    
    # Store the source and target for anyone who wants to animate
    self.last_drag_source = source_row
    self.last_drag_target = target_row
    
    # Move the item
    log.debug(f"Moving album from row {source_row} to row {target_row}")
    album = self.albums.pop(source_row)
    
    if source_row < target_row:
        target_row -= 1
    
    self.albums.insert(target_row, album)
    self.endResetModel()
    
    # Notify view of the change
    min_row = min(source_row, target_row)
    max_row = max(source_row, target_row)
    log.debug(f"Emitting dataChanged for rows {min_row} to {max_row}")
    self.dataChanged.emit(self.index(min_row, 0),
                         self.index(max_row, self.columnCount() - 1))
    
    return True


def paint_with_drag_handle(self, painter, option, index, original_paint):
    """
    Paint method with added drag handle indicators.
    
    Args:
        self: The delegate instance
        painter: The QPainter to use
        option: The style option
        index: The model index being painted
        original_paint: The original paint method to call (not self.original_paint)
    """
    # Call the original paint method directly (not through self)
    original_paint(painter, option, index)
    
    # Then add our drag handle enhancements when hovering over the first column
    # BUT only when not in a drag operation
    col = index.column()
    
    # Check if we are in a drag operation by looking at the view
    view = self.parent()
    in_drag = False
    if hasattr(view, 'isDragInProgress') and view.isDragInProgress:
        in_drag = True