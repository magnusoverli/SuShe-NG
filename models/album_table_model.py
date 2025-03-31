"""
Album table model for QTableView
"""

from typing import List, Optional, Any

from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QMimeData
from models.album import Album


class AlbumTableModel(QAbstractTableModel):
    """Table model for displaying and managing albums."""
    
    def __init__(self, albums: List[Album] = None):
        """
        Initialize the album table model.
        
        Args:
            albums: List of Album objects (optional)
        """
        super().__init__()
        self.albums = albums or []
        self.headers = ["Artist", "Album", "Release Date", "Genre 1", "Genre 2", "Comment"]
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of rows in the model."""
        return len(self.albums)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns in the model."""
        return len(self.headers)
    
    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> Optional[Any]:
        """
        Return data for the specified index and role.
        
        Args:
            index: The index to retrieve data for
            role: The role to retrieve data for
            
        Returns:
            The requested data or None if not available
        """
        if not index.isValid() or not (0 <= index.row() < len(self.albums)):
            return None
        
        album = self.albums[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return album.artist
            elif col == 1:
                return album.name
            elif col == 2:
                return album.release_date.strftime("%Y-%m-%d")
            elif col == 3:
                return album.genre1
            elif col == 4:
                return album.genre2
            elif col == 5:
                return album.comment
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, 
                  role=Qt.ItemDataRole.DisplayRole) -> Optional[str]:
        """
        Return header data for the specified section, orientation and role.
        
        Args:
            section: The section (row or column) to retrieve data for
            orientation: The orientation (horizontal or vertical)
            role: The role to retrieve data for
            
        Returns:
            The requested header data or None if not available
        """
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """
        Return the flags for the specified index.
        
        Args:
            index: The index to retrieve flags for
            
        Returns:
            The item flags for the index
        """
        default_flags = super().flags(index)
        if index.isValid():
            return default_flags | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        return default_flags | Qt.ItemFlag.ItemIsDropEnabled
    
    def supportedDragActions(self) -> Qt.DropAction:
        """Return the supported drag actions."""
        return Qt.DropAction.MoveAction
    
    def supportedDropActions(self) -> Qt.DropAction:
        """Return the supported drop actions."""
        return Qt.DropAction.MoveAction
    
    def mimeTypes(self) -> List[str]:
        """Return the supported MIME types."""
        return ["application/x-album-row"]
    
    def mimeData(self, indexes: List[QModelIndex]) -> QMimeData:
        """
        Return MIME data for the specified indexes.
        
        Args:
            indexes: The indexes to retrieve MIME data for
            
        Returns:
            The MIME data for the indexes
        """
        mime_data = QMimeData()
        encoded_data = bytearray()
        
        rows = set()
        for index in indexes:
            if index.isValid():
                rows.add(index.row())
        
        for row in rows:
            encoded_data.extend(str(row).encode())
        
        mime_data.setData("application/x-album-row", encoded_data)
        return mime_data
    
    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, 
                    row: int, column: int, parent: QModelIndex) -> bool:
        """
        Handle dropping MIME data on the model.
        
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
            return False
        
        if action == Qt.DropAction.IgnoreAction:
            return True
        
        encoded_data = data.data("application/x-album-row")
        source_row = int(encoded_data.data().decode())
        
        if row != -1:
            target_row = row
        elif parent.isValid():
            target_row = parent.row()
        else:
            target_row = self.rowCount()
        
        if source_row == target_row or source_row == target_row - 1:
            return False
        
        self.beginResetModel()
        album = self.albums.pop(source_row)
        
        if source_row < target_row:
            target_row -= 1
        
        self.albums.insert(target_row, album)
        self.endResetModel()
        
        return True

    def add_album(self, album: Album) -> None:
        """
        Add an album to the model.
        
        Args:
            album: The album to add
        """
        self.beginInsertRows(QModelIndex(), len(self.albums), len(self.albums))
        self.albums.append(album)
        self.endInsertRows()
    
    def remove_album(self, row: int) -> None:
        """
        Remove an album from the model.
        
        Args:
            row: The row index of the album to remove
        """
        if 0 <= row < len(self.albums):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.albums[row]
            self.endRemoveRows()