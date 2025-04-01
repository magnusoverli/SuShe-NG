"""
views/new_list_dialog.py

Dialog for creating a new list with integrated collection selection.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QComboBox, QPushButton, QFormLayout,
                            QDialogButtonBox, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class NewListDialog(QDialog):
    """Dialog for creating a new album list with collection selection."""
    
    def __init__(self, collection_names, parent=None):
        """
        Initialize the new list dialog.
        
        Args:
            collection_names: List of existing collection names
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.collection_names = collection_names
        self.setWindowTitle("Create New List")
        self.setMinimumWidth(400)
        
        # Set Spotify-style dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #333333;
                color: #FFFFFF;
                border-radius: 4px;
                padding: 8px;
                border: 1px solid #444444;
            }
            QComboBox {
                background-color: #333333;
                color: #FFFFFF;
                border-radius: 4px;
                padding: 8px;
                border: 1px solid #444444;
                min-width: 200px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 24px;
                border-left: none;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: #FFFFFF;
                border: 1px solid #444444;
                selection-background-color: #505050;
            }
            QPushButton {
                background-color: #1DB954;
                color: #FFFFFF;
                border-radius: 4px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1ED760;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #999999;
            }
        """)
        
        # Create the layout
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Header
        header_label = QLabel("Create New List")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Form layout for fields
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Title field
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("My Album List")
        form_layout.addRow("Title:", self.title_edit)
        
        # Description field
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Optional description for your list")
        form_layout.addRow("Description:", self.description_edit)
        
        # Collection dropdown
        self.collection_combo = QComboBox()
        
        # Populate with existing collections
        for name in collection_names:
            self.collection_combo.addItem(name)
            
        # Add "Create new collection..." option
        self.collection_combo.addItem("Create new collection...")
        
        # Connect to handle "Create new collection" selection
        self.collection_combo.currentIndexChanged.connect(self._handle_collection_change)
        
        form_layout.addRow("Collection:", self.collection_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                     QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Style buttons
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Create")
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setStyleSheet("background-color: #333333;")
        
        layout.addWidget(button_box)
        
        # Set focus to title field
        self.title_edit.setFocus()
    
    def _handle_collection_change(self, index):
        """
        Handle selection of "Create new collection" option.
        
        Args:
            index: Index of selected item
        """
        if index == self.collection_combo.count() - 1:
            # User selected "Create new collection..."
            name, ok = QInputDialog.getText(
                self, "Create Collection", "Collection name:")
            
            if ok and name:
                # Insert the new name before the "Create new" option
                self.collection_combo.insertItem(index, name)
                self.collection_combo.setCurrentIndex(index)
                return
                
            # If user canceled, revert to first collection
            if self.collection_combo.count() > 1:
                self.collection_combo.setCurrentIndex(0)
    
    def get_list_info(self):
        """
        Get the entered list information.
        
        Returns:
            Dictionary with list title, description, collection name, and is_new_collection flag
        """
        title = self.title_edit.text().strip()
        if not title:
            title = "My Album List"
            
        description = self.description_edit.text().strip()
        
        collection_index = self.collection_combo.currentIndex()
        collection_name = self.collection_combo.currentText()
        
        # Check if this is a new collection (but not the placeholder item)
        is_new_collection = (collection_index != self.collection_combo.count() - 1 and
                             collection_name not in self.collection_names)
        
        return {
            "title": title,
            "description": description,
            "collection_name": collection_name,
            "is_new_collection": is_new_collection
        }


def show_new_list_dialog(collection_names, parent=None):
    """
    Show the new list dialog and return the results.
    
    Args:
        collection_names: List of existing collection names
        parent: Parent widget
        
    Returns:
        Dictionary with list info or None if canceled
    """
    dialog = NewListDialog(collection_names, parent)
    result = dialog.exec()
    
    if result == QDialog.DialogCode.Accepted:
        return dialog.get_list_info()
    
    return None