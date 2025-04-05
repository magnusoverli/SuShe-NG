"""
views/import_dialog.py

Import dialog for album lists
"""

import os
import traceback
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                           QFileDialog, QProgressBar, QMessageBox, QListWidget,
                           QListWidgetItem, QAbstractItemView, QLineEdit, QFormLayout,
                           QDialogButtonBox, QWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

from models.album import Album
from utils.album_list_manager import AlbumListManager
from utils.logging_utils import get_module_logger

# Get module logger
log = get_module_logger()


class ImportDialog(QDialog):
    """Dialog for importing album lists from various formats."""
    
    def __init__(self, parent=None):
        """Initialize the import dialog."""
        super().__init__(parent)
        log.debug("Initializing ImportDialog")
        
        self.setWindowTitle("Import Album List")
        self.setMinimumSize(600, 400)
        
        # List manager for handling the import
        self.list_manager = AlbumListManager()
        
        # Variables to store the import results
        self.imported_albums = []
        self.list_metadata = {}
        
        # Setup the UI
        self._setup_ui()
        log.debug("ImportDialog initialized")
    
    def _setup_ui(self):
        """Set up the user interface."""
        log.debug("Setting up import dialog UI")
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Welcome message
        welcome_label = QLabel("Import Album List")
        welcome_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        main_layout.addWidget(welcome_label)
        
        description_label = QLabel(
            "Import your album lists from older versions or from backup files. "
            "Supported formats: JSON (.json)"
        )
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)
        
        # Source file selection
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("color: #B3B3B3;")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_file)
        file_layout.addWidget(QLabel("Source File:"))
        file_layout.addWidget(self.file_path_label, 1)
        file_layout.addWidget(browse_button)
        main_layout.addLayout(file_layout)
        
        # List metadata form
        form_layout = QFormLayout()
        self.list_title_edit = QLineEdit()
        self.list_description_edit = QLineEdit()
        form_layout.addRow("List Title:", self.list_title_edit)
        form_layout.addRow("Description:", self.list_description_edit)
        main_layout.addLayout(form_layout)
        
        # Preview section
        preview_label = QLabel("Preview:")
        preview_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        main_layout.addWidget(preview_label)
        
        self.preview_list = QListWidget()
        self.preview_list.setAlternatingRowColors(True)
        self.preview_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.preview_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.preview_list.setMinimumHeight(150)
        main_layout.addWidget(self.preview_list)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        # Disable OK button initially
        button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Import")
        main_layout.addWidget(button_box)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #B3B3B3;")
        main_layout.addWidget(self.status_label)
        
        # Set the layout
        self.setLayout(main_layout)
        log.debug("Import dialog UI setup complete")
    
    def _browse_file(self):
        """Open a file dialog to select the source file."""
        log.debug("Opening file dialog to select source file")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Album List File",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            log.debug(f"Selected file: {file_path}")
            self.file_path_label.setText(os.path.basename(file_path))
            self._preview_import(file_path)
        else:
            log.debug("File selection cancelled")
    
    def _preview_import(self, file_path: str):
        """
        Generate a preview of the import.
        
        Args:
            file_path: Path to the source file
        """
        log.info(f"Generating preview for import from: {file_path}")
        try:
            # Clear the preview list
            self.preview_list.clear()
            
            # Show progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(10)
            
            # Update status
            self.status_label.setText("Parsing file...")
            
            # Import the file
            log.debug("Parsing file for preview")
            albums, metadata = self.list_manager.import_from_old_format(file_path)
            
            # Update progress
            self.progress_bar.setValue(50)
            
            # Store the imported albums and metadata
            self.imported_albums = albums
            self.list_metadata = metadata
            
            # Update the metadata form
            self.list_title_edit.setText(metadata.get("title", ""))
            self.list_description_edit.setText(metadata.get("description", ""))
            
            # Update preview list
            log.debug(f"Adding {min(len(albums), 20)} albums to preview list")
            for idx, album in enumerate(albums):
                if idx >= 20:  # Limit preview to 20 items
                    item = QListWidgetItem(f"... and {len(albums) - 20} more albums")
                    item.setForeground(Qt.GlobalColor.gray)
                    self.preview_list.addItem(item)
                    break
                
                item = QListWidgetItem(f"{album.artist} - {album.name} ({album.release_date.year})")
                self.preview_list.addItem(item)
            
            # Update progress
            self.progress_bar.setValue(100)
            
            # Update status
            self.status_label.setText(f"Found {len(albums)} albums in the file.")
            
            # Enable OK button
            self.ok_button.setEnabled(True)
            log.info(f"Import preview complete: {len(albums)} albums found")
            
        except Exception as e:
            # Handle error
            log.error(f"Error previewing import: {e}")
            log.debug(traceback.format_exc())
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Import Error", f"Failed to import file: {str(e)}")
    
    def get_import_results(self) -> Tuple[List[Album], dict]:
        """
        Get the imported albums and metadata.
        
        Returns:
            Tuple containing the list of albums and metadata dictionary
        """
        log.debug("Getting import results")
        # Update metadata with user-entered values
        self.list_metadata["title"] = self.list_title_edit.text()
        self.list_metadata["description"] = self.list_description_edit.text()
        
        return self.imported_albums, self.list_metadata


def show_import_dialog(parent=None) -> Tuple[Optional[List[Album]], Optional[dict]]:
    """
    Show the import dialog and return the results.
    
    Args:
        parent: Parent widget
        
    Returns:
        Tuple of (albums, metadata) if successful, (None, None) if canceled
    """
    log.info("Showing import dialog")
    dialog = ImportDialog(parent)
    result = dialog.exec()
    
    if result == QDialog.DialogCode.Accepted:
        albums, metadata = dialog.get_import_results()
        log.info(f"Import dialog accepted: {len(albums)} albums with title '{metadata.get('title')}'")
        return albums, metadata
    
    log.debug("Import dialog cancelled")
    return None, None