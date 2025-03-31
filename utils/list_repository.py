"""
utils/list_repository.py

Repository for managing album lists in a centralized location.
"""

import os
import json
import shutil
import platform
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from utils.album_list_manager import AlbumListManager
from models.album import Album


class ListRepository:
    """Manages the storage and retrieval of album lists."""
    
    def __init__(self):
        """Initialize the list repository."""
        # Set up the repository base directory
        self.base_dir = self._get_base_directory()
        
        # Ensure the directories exist
        self.lists_dir = os.path.join(self.base_dir, "Lists")
        self.collections_dir = os.path.join(self.base_dir, "Collections")
        self.metadata_file = os.path.join(self.base_dir, "metadata.json")
        
        os.makedirs(self.lists_dir, exist_ok=True)
        os.makedirs(self.collections_dir, exist_ok=True)
        
        # Initialize the repository metadata
        self.metadata = self._load_metadata()
        
        # Album list manager for importing/exporting
        self.list_manager = AlbumListManager()
        
        # Log repository info for debugging
        print(f"Repository initialized at: {self.base_dir}")
        print(f"Lists directory: {self.lists_dir}")
        print(f"Collections directory: {self.collections_dir}")
        print(f"Loaded metadata with {len(self.metadata.get('collections', {}))} collections")
    
    def _get_base_directory(self) -> str:
        """
        Get the base directory for the application data.
        
        Returns:
            The path to the base directory
        """
        # Determine the appropriate data directory based on platform
        if platform.system() == "Windows":
            # Windows: %APPDATA%\SusheNG
            base = os.path.join(os.environ["APPDATA"], "SusheNG")
        elif platform.system() == "Darwin":
            # macOS: ~/Library/Application Support/SusheNG
            base = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "SusheNG")
        else:
            # Linux/Unix: ~/.local/share/SusheNG
            base = os.path.join(os.path.expanduser("~"), ".local", "share", "SusheNG")
        
        # Create the base directory if it doesn't exist
        os.makedirs(base, exist_ok=True)
        
        return base
    
    def _load_metadata(self) -> Dict[str, Any]:
        """
        Load the repository metadata.
        
        Returns:
            The metadata dictionary
        """
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
                traceback.print_exc()
        
        # Initialize with default metadata
        return {
            "recent_lists": [],
            "favorite_lists": [],
            "collections": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_metadata(self) -> None:
        """Save the repository metadata."""
        try:
            # Update the last updated timestamp
            self.metadata["last_updated"] = datetime.now().isoformat()
            
            # Create the file path if it doesn't exist
            metadata_dir = os.path.dirname(self.metadata_file)
            os.makedirs(metadata_dir, exist_ok=True)
            
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2)
                
            # Log that we saved the metadata for debugging
            print(f"Saved metadata: {len(self.metadata.get('collections', {}))} collections")
        except Exception as e:
            print(f"Error saving metadata: {e}")
            traceback.print_exc()
    
    def get_all_lists(self) -> List[Dict[str, Any]]:
        """
        Get information about all lists in the repository.
        
        Returns:
            A list of dictionaries with list information
        """
        lists = []
        
        # Get files with .sush extension
        for filename in os.listdir(self.lists_dir):
            if filename.endswith(".sush"):
                file_path = os.path.join(self.lists_dir, filename)
                list_info = self._get_list_info(file_path)
                if list_info:
                    lists.append(list_info)
        
        # Sort by last modified date (newest first)
        return sorted(lists, key=lambda x: x.get("last_modified", ""), reverse=True)
    
    def get_recent_lists(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recently accessed lists.
        
        Args:
            limit: Maximum number of lists to return
            
        Returns:
            A list of dictionaries with list information
        """
        recent_paths = self.metadata.get("recent_lists", [])[:limit]
        
        # Get info for each list
        recent_lists = []
        for path in recent_paths:
            if os.path.exists(path):
                list_info = self._get_list_info(path)
                if list_info:
                    recent_lists.append(list_info)
        
        return recent_lists
    
    def get_favorite_lists(self) -> List[Dict[str, Any]]:
        """
        Get the favorite lists.
        
        Returns:
            A list of dictionaries with list information
        """
        favorite_paths = self.metadata.get("favorite_lists", [])
        
        # Get info for each list
        favorite_lists = []
        for path in favorite_paths:
            if os.path.exists(path):
                list_info = self._get_list_info(path)
                if list_info:
                    favorite_lists.append(list_info)
        
        return favorite_lists
    
    def get_collections(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all collections and their lists.
        
        Returns:
            A dictionary mapping collection names to lists of list information
        """
        collections = {}
        
        for collection_name, list_paths in self.metadata.get("collections", {}).items():
            collection_lists = []
            
            for path in list_paths:
                if os.path.exists(path):
                    list_info = self._get_list_info(path)
                    if list_info:
                        collection_lists.append(list_info)
            
            if collection_lists:
                collections[collection_name] = collection_lists
        
        return collections
    
    def _get_list_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a list file.
        
        Args:
            file_path: Path to the list file
            
        Returns:
            A dictionary with list information or None if the file cannot be read
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            metadata = data.get("metadata", {})
            album_count = len(data.get("albums", []))
            
            # Get file stats
            stats = os.stat(file_path)
            modified_time = datetime.fromtimestamp(stats.st_mtime).isoformat()
            
            # Check if it's a favorite
            is_favorite = file_path in self.metadata.get("favorite_lists", [])
            
            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "title": metadata.get("title", "Untitled List"),
                "description": metadata.get("description", ""),
                "album_count": album_count,
                "date_created": metadata.get("date_created", ""),
                "date_modified": metadata.get("date_modified", ""),
                "last_modified": modified_time,
                "is_favorite": is_favorite
            }
        except Exception as e:
            print(f"Error reading list file {file_path}: {e}")
            return None
    
    def add_list_to_recent(self, file_path: str) -> None:
        """
        Add a list to the recent lists.
        
        Args:
            file_path: Path to the list file
        """
        recent_lists = self.metadata.get("recent_lists", [])
        
        # Remove the file if it's already in the list
        if file_path in recent_lists:
            recent_lists.remove(file_path)
        
        # Add to the beginning of the list
        recent_lists.insert(0, file_path)
        
        # Limit to 10 recent lists
        self.metadata["recent_lists"] = recent_lists[:10]
        
        # Save the metadata
        self._save_metadata()
    
    def toggle_favorite(self, file_path: str) -> bool:
        """
        Toggle the favorite status of a list.
        
        Args:
            file_path: Path to the list file
            
        Returns:
            True if the list is now a favorite, False otherwise
        """
        favorite_lists = self.metadata.get("favorite_lists", [])
        
        if file_path in favorite_lists:
            # Remove from favorites
            favorite_lists.remove(file_path)
            is_favorite = False
        else:
            # Add to favorites
            favorite_lists.append(file_path)
            is_favorite = True
        
        self.metadata["favorite_lists"] = favorite_lists
        self._save_metadata()
        
        return is_favorite
    
    def add_to_collection(self, file_path: str, collection_name: str) -> None:
        """
        Add a list to a collection.
        
        Args:
            file_path: Path to the list file
            collection_name: Name of the collection
        """
        collections = self.metadata.get("collections", {})
        
        # Create the collection if it doesn't exist
        if collection_name not in collections:
            collections[collection_name] = []
        
        # Add the file to the collection if it's not already there
        if file_path not in collections[collection_name]:
            collections[collection_name].append(file_path)
        
        self.metadata["collections"] = collections
        self._save_metadata()
    
    def remove_from_collection(self, file_path: str, collection_name: str) -> None:
        """
        Remove a list from a collection.
        
        Args:
            file_path: Path to the list file
            collection_name: Name of the collection
        """
        collections = self.metadata.get("collections", {})
        
        if collection_name in collections and file_path in collections[collection_name]:
            collections[collection_name].remove(file_path)
            
            # Remove the collection if it's empty
            if not collections[collection_name]:
                del collections[collection_name]
            
            self.metadata["collections"] = collections
            self._save_metadata()
    
    def create_collection(self, collection_name: str) -> None:
        """
        Create a new collection.
        
        Args:
            collection_name: Name of the collection
        """
        # Sanity check the name
        if not collection_name.strip():
            print("Error: Cannot create collection with empty name")
            return
            
        # Get existing collections or initialize empty dict
        collections = self.metadata.get("collections", {})
        
        # Check if collection exists
        if collection_name in collections:
            print(f"Collection {collection_name} already exists, skipping creation")
            return
            
        # Create the collection directory
        collection_dir = os.path.join(self.collections_dir, collection_name)
        os.makedirs(collection_dir, exist_ok=True)
        
        # Add the collection to metadata
        collections[collection_name] = []
        self.metadata["collections"] = collections
        
        # Save the metadata
        print(f"Creating new collection: {collection_name}")
        self._save_metadata()
    
    def rename_collection(self, old_name: str, new_name: str) -> bool:
        """
        Rename a collection.
        
        Args:
            old_name: Current name of the collection
            new_name: New name for the collection
            
        Returns:
            True if successful, False otherwise
        """
        # Sanity check the names
        if not old_name.strip() or not new_name.strip():
            return False
            
        collections = self.metadata.get("collections", {})
        
        if old_name in collections and new_name not in collections:
            # Rename the collection in metadata
            collections[new_name] = collections[old_name]
            del collections[old_name]
            
            # Rename the collection directory
            old_dir = os.path.join(self.collections_dir, old_name)
            new_dir = os.path.join(self.collections_dir, new_name)
            
            # Only try to rename if the old directory exists
            if os.path.exists(old_dir):
                try:
                    os.rename(old_dir, new_dir)
                except Exception as e:
                    print(f"Error renaming collection directory: {e}")
                    # Continue anyway since the metadata is more important
            
            self.metadata["collections"] = collections
            self._save_metadata()
            return True
        
        return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if successful, False otherwise
        """
        collections = self.metadata.get("collections", {})
        
        if collection_name in collections:
            # Remove from metadata
            del collections[collection_name]
            
            # Remove the collection directory
            collection_dir = os.path.join(self.collections_dir, collection_name)
            if os.path.exists(collection_dir):
                try:
                    shutil.rmtree(collection_dir)
                except Exception as e:
                    print(f"Error removing collection directory: {e}")
                    # Continue anyway since the metadata is more important
            
            self.metadata["collections"] = collections
            self._save_metadata()
            return True
        
        return False
    
    def save_list(self, albums: List[Album], metadata: Dict[str, Any], 
                 file_name: Optional[str] = None) -> str:
        """
        Save an album list to the repository.
        
        Args:
            albums: List of Album objects
            metadata: List metadata
            file_name: Optional file name to use (without extension)
            
        Returns:
            The path to the saved file
        """
        # Generate a file name if not provided
        if not file_name:
            file_name = metadata.get("title", "Untitled List")
            
        # Sanitize the file name
        file_name = self._sanitize_filename(file_name)
        
        # Ensure it has the .sush extension
        if not file_name.endswith(".sush"):
            file_name += ".sush"
        
        # Create the full file path
        file_path = os.path.join(self.lists_dir, file_name)
        
        # Export the list
        self.list_manager.export_to_new_format(albums, metadata, file_path)
        
        # Add to recent lists
        self.add_list_to_recent(file_path)
        
        return file_path
    
    def load_list(self, file_path: str) -> Tuple[List[Album], Dict[str, Any]]:
        """
        Load an album list from a file.
        
        Args:
            file_path: Path to the list file
            
        Returns:
            Tuple of (list of Albums, metadata)
        """
        # Add to recent lists
        self.add_list_to_recent(file_path)
        
        # Check if it's a .sush file
        if file_path.endswith(".sush"):
            return self.list_manager.import_from_new_format(file_path)
        elif file_path.endswith(".json"):
            return self.list_manager.import_from_old_format(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    def delete_list(self, file_path: str) -> bool:
        """
        Delete a list from the repository.
        
        Args:
            file_path: Path to the list file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                return False
            
            # Remove from recent lists
            if file_path in self.metadata.get("recent_lists", []):
                self.metadata["recent_lists"].remove(file_path)
            
            # Remove from favorites
            if file_path in self.metadata.get("favorite_lists", []):
                self.metadata["favorite_lists"].remove(file_path)
            
            # Remove from collections
            collections = self.metadata.get("collections", {})
            for collection, files in list(collections.items()):
                if file_path in files:
                    files.remove(file_path)
                    
                    # If this was the last file in the collection, consider removing the collection
                    if not files:
                        collections[collection] = []
            
            # Save metadata changes
            self._save_metadata()
            
            # Delete the file
            os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"Error deleting list: {e}")
            traceback.print_exc()
            return False
    
    def import_external_list(self, external_path: str) -> Optional[str]:
        """
        Import an external list file into the repository.
        
        Args:
            external_path: Path to the external list file
            
        Returns:
            The path to the imported file or None if import failed
        """
        try:
            # Load the external file
            if external_path.endswith(".sush"):
                albums, metadata = self.list_manager.import_from_new_format(external_path)
            elif external_path.endswith(".json"):
                albums, metadata = self.list_manager.import_from_old_format(external_path)
            else:
                raise ValueError(f"Unsupported file format: {external_path}")
            
            # Generate a file name from the list title
            file_name = metadata.get("title", os.path.basename(external_path))
            
            # Save to the repository
            return self.save_list(albums, metadata, file_name)
        except Exception as e:
            print(f"Error importing external list: {e}")
            traceback.print_exc()
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename to remove invalid characters.
        
        Args:
            filename: The filename to sanitize
            
        Returns:
            A sanitized filename
        """
        # Replace invalid characters with underscores
        invalid_chars = '\\/:*?"<>|'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename