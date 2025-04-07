"""
utils/simple_collection_manager.py

Simple collection manager for SuShe NG.
Uses filesystem directories for collections and JSON files for album lists.
"""

import os
import re
import json
from datetime import datetime
import traceback

from models.album import Album
from utils.logging_utils import get_module_logger

# Get module logger
log = get_module_logger()


class SimpleCollectionManager:
    """
    Simple filesystem-based collection manager for SuShe NG.
    
    Collections are stored as directories, and album lists are stored as JSON files
    within those directories. This provides a simple hierarchical structure without
    complex abstractions.
    """
    
    def __init__(self):
        """Initialize the collection manager."""
        log.debug("Initializing SimpleCollectionManager")
        
        # Base app directory
        self.app_dir = self._get_app_directory()
        log.debug(f"App directory: {self.app_dir}")
        
        # Collections directory - each collection is a subdirectory
        self.collections_dir = os.path.join(self.app_dir, "collections")
        os.makedirs(self.collections_dir, exist_ok=True)
        log.debug(f"Collections directory: {self.collections_dir}")
        
        # Simple metadata to track recent lists
        self.metadata_path = os.path.join(self.app_dir, "metadata.json")
        self.metadata = self._load_metadata()
        
        # Create a default collection if none exists
        if not os.listdir(self.collections_dir):
            log.info("No collections found, creating default collection")
            os.makedirs(os.path.join(self.collections_dir, "Default"), exist_ok=True)
    
    def _get_app_directory(self):
        """Get the application data directory."""
        import platform
        
        # Determine the appropriate data directory based on platform
        if platform.system() == "Windows":
            # Windows: %APPDATA%\SusheNG
            base = os.path.join(os.environ["APPDATA"], "SusheNG")
            log.debug(f"Using Windows app data directory: {base}")
        elif platform.system() == "Darwin":
            # macOS: ~/Library/Application Support/SusheNG
            base = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "SusheNG")
            log.debug(f"Using macOS app data directory: {base}")
        else:
            # Linux/Unix: ~/.local/share/SusheNG
            base = os.path.join(os.path.expanduser("~"), ".local", "share", "SusheNG")
            log.debug(f"Using Linux app data directory: {base}")
        
        # Create the base directory if it doesn't exist
        os.makedirs(base, exist_ok=True)
        
        return base
    
    def _load_metadata(self):
        """Load metadata from JSON file."""
        if os.path.exists(self.metadata_path):
            try:
                log.debug(f"Loading metadata from {self.metadata_path}")
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                log.error(f"Error loading metadata: {e}")
                log.debug(traceback.format_exc())
        
        # Initialize with default metadata
        log.debug("Creating default metadata")
        return {
            "recent_lists": []
        }
    
    def _save_metadata(self):
        """Save metadata to JSON file."""
        try:
            log.debug(f"Saving metadata to {self.metadata_path}")
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            log.error(f"Error saving metadata: {e}")
            log.debug(traceback.format_exc())
    
    def get_collections(self):
        """
        Get all collections as a dictionary of collection_name -> list of list_info.
        
        Returns:
            A dictionary mapping collection names to lists of list information
        """
        log.debug("Getting all collections")
        collections = {}
        
        # Iterate through collection directories
        for collection_name in os.listdir(self.collections_dir):
            collection_path = os.path.join(self.collections_dir, collection_name)
            if not os.path.isdir(collection_path):
                continue
                
            # Get all .sush files in this collection
            lists = []
            log.debug(f"Processing collection: {collection_name}")
            for file_name in os.listdir(collection_path):
                if file_name.endswith(".sush"):
                    file_path = os.path.join(collection_path, file_name)
                    list_info = self._get_list_info(file_path)
                    if list_info:
                        lists.append(list_info)
            
            collections[collection_name] = lists
            log.debug(f"Collection {collection_name} has {len(lists)} lists")
        
        return collections
    
    def get_recent_lists(self, limit=5):
        """
        Get the most recently accessed lists.
        
        Args:
            limit: Maximum number of lists to return
            
        Returns:
            A list of dictionaries with list information
        """
        log.debug(f"Getting recent lists (limit: {limit})")
        recent_paths = self.metadata.get("recent_lists", [])[:limit]
        
        # Get info for each list
        recent_lists = []
        for path in recent_paths:
            if os.path.exists(path):
                list_info = self._get_list_info(path)
                if list_info:
                    recent_lists.append(list_info)
            else:
                log.warning(f"Recent list not found: {path}")
        
        log.debug(f"Returning {len(recent_lists)} recent lists")
        return recent_lists
    
    def _get_list_info(self, file_path):
        """
        Get basic info about a list without loading all albums.
        
        Args:
            file_path: Path to the list file
            
        Returns:
            A dictionary with list information or None if the file cannot be read
        """
        try:
            log.debug(f"Getting list info for: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parse the JSON data
            import json
            data = json.loads(content)
            
            # Check data format and extract info
            if isinstance(data, list):
                # Old format - just a list of albums
                title = os.path.basename(file_path)
                if title.endswith(".json") or title.endswith(".sush"):
                    title = title[:-5]  # Remove extension
                album_count = len(data)
                metadata = {"title": title}
            elif isinstance(data, dict) and "albums" in data:
                # New format with metadata and albums
                metadata = data.get("metadata", {})
                album_count = len(data.get("albums", []))
            else:
                # Unknown format
                log.error(f"Unknown file format: {file_path}")
                return None
            
            # Get file stats
            stats = os.stat(file_path)
            modified_time = datetime.fromtimestamp(stats.st_mtime).isoformat()
            
            list_info = {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "title": metadata.get("title", "Untitled List"),
                "album_count": album_count,
                "date_modified": modified_time,
                "collection": self.get_collection_for_list(file_path)
            }
            
            log.debug(f"Retrieved info for list: {list_info['title']}")
            return list_info
        except Exception as e:
            log.error(f"Error reading list file {file_path}: {e}")
            log.debug(traceback.format_exc())
            return None
    
    def create_collection(self, collection_name):
        """
        Create a new collection directory.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if successful, False if the collection already exists
        """
        log.info(f"Creating new collection: {collection_name}")
        
        # Sanitize the collection name for filesystem use
        safe_name = re.sub(r'[^\w\-_.]', '_', collection_name)
        collection_path = os.path.join(self.collections_dir, safe_name)
        
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)
            log.info(f"Collection created: {collection_name}")
            return True
            
        log.warning(f"Collection already exists: {collection_name}")
        return False
    
    def save_album_list(self, albums, metadata, collection_name=None, file_name=None):
        """
        Save an album list to a specific collection.
        
        Args:
            albums: List of Album objects
            metadata: Metadata dictionary
            collection_name: Name of the collection (optional)
            file_name: Name for the file (optional)
            
        Returns:
            Path to the saved file
        """
        log.debug(f"Saving album list, collection: {collection_name}")
        
        # If no collection specified, use the one from metadata or default
        if not collection_name:
            collection_name = metadata.get("collection", "Default")
            log.debug(f"Using collection from metadata: {collection_name}")
        
        # Ensure the collection exists
        collection_path = os.path.join(self.collections_dir, collection_name)
        if not os.path.exists(collection_path):
            log.debug(f"Collection doesn't exist, creating: {collection_name}")
            os.makedirs(collection_path)
        
        # Generate filename from title if not provided
        if not file_name:
            title = metadata.get("title", "Untitled")
            file_name = self._sanitize_filename(title)
            log.debug(f"Generated filename: {file_name}")
        
        # Ensure extension
        if not file_name.endswith(".sush"):
            file_name += ".sush"
        
        file_path = os.path.join(collection_path, file_name)
        log.debug(f"Full file path: {file_path}")
        
        # Just keep minimal metadata - title and modified date
        simple_metadata = {
            "title": metadata.get("title", "Untitled"),
            "collection": collection_name,
            "date_modified": datetime.now().isoformat()
        }
        
        # Save to file
        try:
            log.debug(f"Saving {len(albums)} albums to file")
            with open(file_path, "w", encoding="utf-8") as f:
                data = {
                    "metadata": simple_metadata,
                    "albums": [self._album_to_dict(album) for album in albums]
                }
                json.dump(data, f, indent=2)
            
            # Update recent files
            if file_path in self.metadata["recent_lists"]:
                self.metadata["recent_lists"].remove(file_path)
            self.metadata["recent_lists"].insert(0, file_path)
            self.metadata["recent_lists"] = self.metadata["recent_lists"][:10]
            
            self._save_metadata()
            log.info(f"Album list saved to {file_path}")
            return file_path
        except Exception as e:
            log.error(f"Error saving album list: {e}")
            log.debug(traceback.format_exc())
            raise
    
    def load_album_list(self, file_path):
        """
        Load an album list from a file path.
        
        Args:
            file_path: Path to the list file
            
        Returns:
            Tuple of (list of Albums, metadata)
        """
        log.debug(f"Loading album list from: {file_path}")
        try:
            # Read the file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parse the JSON data
            import json
            data = json.loads(content)
            
            # Check data format
            if isinstance(data, list):
                # Old format - just a list of albums
                log.debug("Old format detected (list of albums)")
                albums_data = data
                title = os.path.basename(file_path)
                if title.endswith(".json") or title.endswith(".sush"):
                    title = title[:-5]  # Remove extension
                metadata = {"title": title}
            elif isinstance(data, dict) and "albums" in data:
                # New format with metadata and albums
                log.debug("New format detected (metadata and albums)")
                albums_data = data.get("albums", [])
                metadata = data.get("metadata", {})
            else:
                # Unknown format
                log.error(f"Unknown file format: {file_path}")
                raise ValueError(f"Unknown file format: {file_path}")
            
            # Convert dict data to Album objects
            albums = []
            for album_data in albums_data:
                albums.append(self._dict_to_album(album_data))
            
            # Update recent lists
            if file_path in self.metadata["recent_lists"]:
                self.metadata["recent_lists"].remove(file_path)
            self.metadata["recent_lists"].insert(0, file_path)
            self.metadata["recent_lists"] = self.metadata["recent_lists"][:10]
            self._save_metadata()
            
            # Add collection information to metadata
            collection_name = self.get_collection_for_list(file_path)
            if collection_name and "collection" not in metadata:
                metadata["collection"] = collection_name
            
            log.info(f"Loaded {len(albums)} albums from {file_path}")
            return albums, metadata
        except Exception as e:
            log.error(f"Error loading album list: {e}")
            log.debug(traceback.format_exc())
            raise
    
    def get_collection_for_list(self, file_path):
        """
        Get the collection name for a list.
        
        Args:
            file_path: Path to the list file
            
        Returns:
            Collection name or None if not in a collection
        """
        # Extract collection name from path
        path_parts = os.path.normpath(file_path).split(os.sep)
        for i, part in enumerate(path_parts):
            if part == "collections" and i + 1 < len(path_parts):
                return path_parts[i + 1]
        return None
    
    def _sanitize_filename(self, filename):
        """
        Sanitize a filename to remove invalid characters.
        
        Args:
            filename: The filename to sanitize
            
        Returns:
            A sanitized filename
        """
        # Replace invalid characters with underscores
        safe_name = re.sub(r'[^\w\-_.]', '_', filename)
        
        # Limit length
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
            
        return safe_name
    
    def _album_to_dict(self, album):
        """
        Convert an Album object to a dictionary.
        
        Args:
            album: Album object
            
        Returns:
            Dictionary representation of the album
        """
        return {
            "artist": album.artist,
            "name": album.name,
            "release_date": album.release_date.isoformat(),
            "genre1": album.genre1,
            "genre2": album.genre2,
            "comment": album.comment,
            "cover_image_data": getattr(album, "cover_image_data", None),
            "cover_image_format": getattr(album, "cover_image_format", None)
        }
    
    def _dict_to_album(self, data):
        """
        Convert a dictionary to an Album object.
        
        Args:
            data: Dictionary with album data
            
        Returns:
            Album object
        """
        # Parse release date
        release_date_str = data.get("release_date", "")
        release_date = self._parse_release_date(release_date_str)
        
        # Handle cover art data - check all possible keys
        cover_image_data = None
        cover_image_format = None
        
        # Check for cover_image_data directly
        if "cover_image_data" in data:
            cover_image_data = data["cover_image_data"]
        
        # Check for cover_image in old format
        if "cover_image" in data and not cover_image_data:
            cover_image_data = data["cover_image"]
        
        # Get image format if available
        if "cover_image_format" in data:
            cover_image_format = data["cover_image_format"]
        
        from models.album import Album
        return Album(
            artist=data.get("artist", ""),
            name=data.get("album", data.get("name", "")),  # Support both name formats
            release_date=release_date,
            genre1=data.get("genre_1", data.get("genre1", "")),  # Support both genre formats
            genre2=data.get("genre_2", data.get("genre2", "")),
            comment=data.get("comments", data.get("comment", "")),  # Support both comment formats
            cover_image_data=cover_image_data,
            cover_image_format=cover_image_format
        )

    def import_external_list(self, file_path: str, collection_name: str) -> str:
        """
        Import an external list file into a collection.
        
        Args:
            file_path: Path to the external list file
            collection_name: Name of the collection to import into
            
        Returns:
            The path to the imported file or None if import failed
        """
        log.info(f"Importing external list: {file_path} to collection: {collection_name}")
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Try to parse the JSON
            import json
            try:
                data = json.loads(content)
                
                # Process based on format
                albums = []
                title = os.path.basename(file_path)
                if title.endswith(".json") or title.endswith(".sush"):
                    title = title[:-5]  # Remove extension
                
                # Check if the data is a list (old format) or dict with metadata (new format)
                if isinstance(data, list):
                    # Old format - just a list of albums
                    log.debug("Old format detected (list of albums)")
                    albums_data = data
                    metadata = {"title": title}
                elif isinstance(data, dict) and "albums" in data:
                    # New format - has metadata and albums
                    log.debug("New format detected (metadata and albums)")
                    albums_data = data.get("albums", [])
                    metadata = data.get("metadata", {})
                    if not metadata.get("title"):
                        metadata["title"] = title
                else:
                    # Unknown format
                    log.error(f"Unknown file format: {file_path}")
                    raise ValueError(f"Unknown file format: {file_path}")
                
                # Convert album data to Album objects
                for album_data in albums_data:
                    # Get release date
                    release_date_str = album_data.get("release_date", "")
                    release_date = self._parse_release_date(release_date_str)
                    
                    # Handle cover art data - check all possible keys
                    cover_image_data = None
                    cover_image_format = None
                    
                    # Check for cover_image_data directly
                    if "cover_image_data" in album_data:
                        cover_image_data = album_data["cover_image_data"]
                    
                    # Check for cover_image in old format
                    if "cover_image" in album_data and not cover_image_data:
                        cover_image_data = album_data["cover_image"]
                    
                    # Get image format if available
                    if "cover_image_format" in album_data:
                        cover_image_format = album_data["cover_image_format"]
                    
                    # Create album
                    from models.album import Album
                    album = Album(
                        artist=album_data.get("artist", ""),
                        name=album_data.get("album", album_data.get("name", "")),
                        release_date=release_date,
                        genre1=album_data.get("genre_1", album_data.get("genre1", "")),
                        genre2=album_data.get("genre_2", album_data.get("genre2", "")),
                        comment=album_data.get("comments", album_data.get("comment", "")),
                        cover_image_data=cover_image_data,
                        cover_image_format=cover_image_format
                    )
                    albums.append(album)
                
                # Save to collection
                log.debug(f"Saving {len(albums)} imported albums to collection: {collection_name}")
                new_path = self.save_album_list(
                    albums,
                    {"title": metadata.get("title", "Imported List")},
                    collection_name
                )
                
                return new_path
                
            except json.JSONDecodeError as e:
                log.error(f"Error parsing JSON: {e}")
                raise ValueError(f"Invalid JSON file: {e}")
                
        except Exception as e:
            log.error(f"Error importing external list: {e}")
            log.debug(traceback.format_exc())
            raise

    def _parse_release_date(self, date_str):
        """
        Parse release date from various formats.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            datetime.date object
        """
        if not date_str:
            from datetime import datetime
            return datetime.now().date()
            
        try:
            # Try ISO format first (YYYY-MM-DD)
            from datetime import datetime
            return datetime.fromisoformat(date_str).date()
        except ValueError:
            # Try DD-MM-YYYY format
            try:
                from datetime import datetime
                day, month, year = map(int, date_str.split('-'))
                return datetime(year, month, day).date()
            except Exception:
                log.warning(f"Failed to parse release date: {date_str}, using today's date")
                from datetime import datetime
                return datetime.now().date()
