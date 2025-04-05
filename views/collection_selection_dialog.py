"""
views/collection_selection_dialog.py

Dialog for selecting or creating a collection for a list.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QListWidget, QListWidgetItem, QLineEdit, 
                           QDialogButtonBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from utils.logging_utils import get_module_logger

# Get module logger
log = get_module_logger()

class CollectionSelectionDialog(QDialog):
    """Dialog for selecting a collection when creating or saving a list."""
    
    def __init__(self, collection_names, parent=None, title="Select Collection", 
                 message="Choose a collection for your list:"):
        """
        Initialize the collection selection dialog.
        
        Args:
            collection_names: List of existing collection names
            parent: Parent widget
            title: Dialog title
            message: Dialog message
        """
        super().__init__(parent)
        
        log.debug(f"Creating collection selection dialog with {len(collection_names)} collections")
        self.collection_names = collection_names
        self.setWindowTitle(title)
        self.setMinimumWidth(350)
        
        # Set dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QListWidget {
                background-color: #282828;
                color: #FFFFFF;
                border-radius: 4px;
                border: none;
            }
            QListWidget::item {
                height: 30px;
                padding: 4px 8px;
            }
            QListWidget::item:selected {
                background-color: #333333;
            }
            QListWidget::item:hover {
                background-color: #333333;
            }
            QLineEdit {
                background-color: #333333;
                color: #FFFFFF;
                border-radius: 4px;
                padding: 8px;
                border: 1px solid #444444;
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
        """)
        
        # Create the layout
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Add title
        header_label = QLabel(message)
        header_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(header_label)
        
        # Existing collections section
        if collection_names:
            log.debug("Adding existing collections list")
            existing_label = QLabel("Select an existing collection:")
            layout.addWidget(existing_label)
            
            # Collection list
            self.collection_list = QListWidget()
            self.collection_list.setMaximumHeight(150)
            for name in collection_names:
                item = QListWidgetItem(name)
                self.collection_list.addItem(item)
            
            # Select the first item by default
            if collection_names:
                self.collection_list.setCurrentRow(0)
                
            layout.addWidget(self.collection_list)
        else:
            log.debug("No existing collections to display")
        
        # New collection section
        new_label = QLabel("Or create a new collection:")
        layout.addWidget(new_label)
        
        # New collection input
        self.new_collection_input = QLineEdit()
        self.new_collection_input.setPlaceholderText("Enter new collection name")
        layout.addWidget(self.new_collection_input)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("background-color: #333333;")
        self.cancel_button.clicked.connect(self.reject)
        
        self.ok_button = QPushButton("Confirm")
        self.ok_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        log.debug("Collection selection dialog initialized")
    
    def get_selected_collection(self):
        """
        Get the selected collection name and whether it's new.
        
        Returns:
            Tuple of (collection_name, is_new)
        """
        log.debug("Getting selected collection")
        # Check if user entered a new collection name
        new_name = self.new_collection_input.text().strip()
        if new_name:
            log.debug(f"New collection name entered: {new_name}")
            return new_name, True
            
        # Otherwise use the selected existing collection
        if hasattr(self, 'collection_list'):
            current_item = self.collection_list.currentItem()
            if current_item:
                collection_name = current_item.text()
                log.debug(f"Existing collection selected: {collection_name}")
                return collection_name, False
                
        # If we get here, no valid selection was made
        log.warning("No valid collection selected")
        return None, False


def select_collection(collection_names, parent=None, title="Select Collection", 
                     message="Choose a collection for your list:"):
    """
    Show the collection selection dialog.
    
    Args:
        collection_names: List of existing collection names
        parent: Parent widget
        title: Dialog title
        message: Dialog message
        
    Returns:
        Tuple of (collection_name, is_new, ok)
    """
    log.debug(f"Showing collection selection dialog with {len(collection_names)} collections")
    dialog = CollectionSelectionDialog(collection_names, parent, title, message)
    result = dialog.exec()
    
    if result == QDialog.DialogCode.Accepted:
        collection_name, is_new = dialog.get_selected_collection()
        log.info(f"Collection selection result: {collection_name}, is_new: {is_new}")
        return collection_name, is_new, True
    
    log.debug("Collection selection cancelled")
    return None, False, False