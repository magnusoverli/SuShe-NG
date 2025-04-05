"""
utils/album_list_manager.py

Album list manager module for SuShe NG.
This module handles importing, exporting, and managing album lists.
"""

import os
import json
import base64
import traceback
from datetime import datetime, date
from typing import List, Dict, Any, Tuple
from pathlib import Path

from models.album import Album
from utils.logging_utils import get_module_logger

# Get module logger
log = get_module_logger()


class AlbumListManager:
    """Manager for importing and exporting album lists."""
    
    # Current file format version for forward compatibility
    CURRENT_FORMAT_VERSION = 1
    
    # File extension for the new format
    FILE_EXTENSION = ".sush"
    
    def __init__(self, covers_directory: str = "resources/covers"):
        """
        Initialize the album list manager.
        
        Args:
            covers_directory: Directory to store album cover images
        """
        log.debug(f"Initializing AlbumListManager with covers directory: {covers_directory}")
        self.covers_directory = covers_directory
        os.makedirs(covers_directory, exist_ok=True)
    
    def import_from_old_format(self, file_path: str) -> Tuple[List[Album], Dict[str, Any]]:
        """
        Import albums from the old format JSON file.
        
        Args:
            file_path: Path to the old format JSON file
            
        Returns:
            tuple: (list of Album objects, metadata dict)
        """
        log.info(f"Importing from old format: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            log.debug(f"Loaded old format JSON with {len(data)} albums")
            albums = []
            # Extract list title from filename if available
            list_name = Path(file_path).stem
            log.debug(f"Using list name from filename: {list_name}")
            
            for idx, album_data in enumerate(data):
                # Convert release date string to date object
                release_date_str = album_data.get('release_date', '')
                try:
                    # Try to parse DD-MM-YYYY format
                    day, month, year = map(int, release_date_str.split('-'))
                    release_date = date(year, month, day)
                except (ValueError, AttributeError):
                    # Fallback to today's date if parsing fails
                    log.warning(f"Failed to parse release date: {release_date_str}, using today's date")
                    release_date = date.today()
                
                # For old format, keep image data directly in the Album object
                cover_image_data = album_data.get('cover_image')
                cover_image_format = album_data.get('cover_image_format', 'PNG')
                
                # Create album object
                album = Album(
                    artist=album_data.get('artist', ''),
                    name=album_data.get('album', ''),
                    release_date=release_date,
                    genre1=album_data.get('genre_1', ''),
                    genre2=album_data.get('genre_2', ''),
                    comment=album_data.get('comments', ''),
                    cover_image=None,  # No file path needed
                    cover_image_data=cover_image_data,
                    cover_image_format=cover_image_format
                )
                
                # Store additional metadata as attributes
                album.album_id = album_data.get('album_id', '')
                album.country = album_data.get('country', '')
                album.rank = album_data.get('rank', idx + 1)
                
                albums.append(album)
                log.debug(f"Imported album: {album.artist} - {album.name}")
            
            # Create metadata for the list
            metadata = {
                "title": list_name,
                "description": f"Imported from {Path(file_path).name}",
                "date_created": datetime.now().isoformat(),
                "date_modified": datetime.now().isoformat(),
                "source_file": file_path,
                "album_count": len(albums)
            }
            
            log.info(f"Successfully imported {len(albums)} albums from {file_path}")
            return albums, metadata
            
        except Exception as e:
            log.error(f"Failed to import album list: {e}")
            log.debug(traceback.format_exc())
            raise ImportError(f"Failed to import album list: {e}")
    
    def export_to_new_format(self, albums: List[Album], metadata: Dict[str, Any], 
                        file_path: str) -> None:
        """
        Export albums to the new format JSON file.
        
        Args:
            albums: List of Album objects to export
            metadata: Metadata for the album list
            file_path: Path to save the new format JSON file
        """
        log.info(f"Exporting {len(albums)} albums to {file_path}")
        # Ensure the file has the correct extension
        if not file_path.endswith(self.FILE_EXTENSION):
            file_path += self.FILE_EXTENSION
            log.debug(f"Added extension to file path: {file_path}")
        
        # Load points mapping from resources
        points_mapping = self._load_points_mapping()
        
        # Build the data structure for the new format
        data = {
            "format_version": self.CURRENT_FORMAT_VERSION,
            "metadata": {
                "title": metadata.get("title", "My Album List"),
                "description": metadata.get("description", ""),
                "date_created": metadata.get("date_created", datetime.now().isoformat()),
                "date_modified": datetime.now().isoformat(),
                "album_count": len(albums)
            },
            "albums": []
        }
        
        log.debug(f"Building export data structure with metadata: {data['metadata']['title']}")
        
        # Add each album to the data structure
        for idx, album in enumerate(albums):
            # Calculate rank (1-based index)
            rank = idx + 1
            
            # Look up points based on rank
            points = points_mapping.get(str(rank), 1)  # Default to 1 point if rank not found
            
            album_data = {
                "artist": album.artist,
                "title": album.name,
                "release_date": album.release_date.isoformat() if album.release_date else None,
                "genre1": album.genre1,
                "genre2": album.genre2,
                "comment": album.comment,
                # Store cover image data directly in the file
                "cover_image_data": album.cover_image_data,
                "cover_image_format": album.cover_image_format,
                "rank": rank,  # Update rank based on current position
                "points": points,  # Add points based on rank
                # Add any additional fields from the Album object
                "album_id": getattr(album, "album_id", ""),
                "country": getattr(album, "country", "")
            }
            data["albums"].append(album_data)
            log.debug(f"Added album to export: {album.artist} - {album.name}")
        
        # Save the data to the file
        try:
            log.debug(f"Writing export data to file: {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log.info(f"Successfully exported {len(albums)} albums to {file_path}")
        except Exception as e:
            log.error(f"Failed to export album list: {e}")
            log.debug(traceback.format_exc())
            raise ExportError(f"Failed to export album list: {e}")

    def _load_points_mapping(self) -> Dict[str, int]:
        """
        Load the points mapping from the resources file.
        
        Returns:
            A dictionary mapping rank (as string) to points
        """
        log.debug("Loading points mapping")
        try:
            # Try to load the points mapping from the resources directory
            from resources import get_resource_path
            points_path = get_resource_path("points.json")
            
            with open(points_path, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
                log.debug(f"Loaded points mapping from {points_path}")
                return mapping
        except Exception as e:
            # If there's an error, use a default mapping
            log.warning(f"Could not load points mapping: {e}")
            log.debug(traceback.format_exc())
            log.info("Using default points mapping (rank = points)")
            
            # Default mapping: rank = points
            default_mapping = {str(i): max(1, 61-i) for i in range(1, 61)}
            return default_mapping
    
    def import_from_new_format(self, file_path: str) -> Tuple[List[Album], Dict[str, Any]]:
        """
        Import albums from the new format JSON file.
        
        Args:
            file_path: Path to the new format JSON file
            
        Returns:
            tuple: (list of Album objects, metadata dict)
        """
        log.info(f"Importing from new format: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check format version for compatibility
            format_version = data.get("format_version", 0)
            if format_version > self.CURRENT_FORMAT_VERSION:
                log.warning(f"File format version ({format_version}) is newer than supported ({self.CURRENT_FORMAT_VERSION})")
            
            # Extract metadata
            metadata = data.get("metadata", {})
            log.debug(f"Loaded file metadata: {metadata.get('title', 'Untitled')}")
            
            # Process albums
            albums = []
            album_data_list = data.get("albums", [])
            log.debug(f"Found {len(album_data_list)} albums in file")
            
            for album_data in album_data_list:
                # Parse release date
                release_date_str = album_data.get("release_date")
                if release_date_str:
                    try:
                        release_date = date.fromisoformat(release_date_str)
                    except ValueError:
                        log.warning(f"Failed to parse release date: {release_date_str}, using today's date")
                        release_date = date.today()
                else:
                    release_date = date.today()
                
                # Create Album object
                album = Album(
                    artist=album_data.get("artist", ""),
                    name=album_data.get("title", ""),
                    release_date=release_date,
                    genre1=album_data.get("genre1", ""),
                    genre2=album_data.get("genre2", ""),
                    comment=album_data.get("comment", ""),
                    cover_image=None,  # No file path needed
                    cover_image_data=album_data.get("cover_image_data"),
                    cover_image_format=album_data.get("cover_image_format")
                )
                
                # Add any additional fields
                if "album_id" in album_data:
                    album.album_id = album_data["album_id"]
                if "country" in album_data:
                    album.country = album_data["country"]
                if "rank" in album_data:
                    album.rank = album_data["rank"]
                if "points" in album_data:
                    album.points = album_data["points"]
                
                albums.append(album)
                log.debug(f"Imported album: {album.artist} - {album.name}")
            
            log.info(f"Successfully imported {len(albums)} albums from {file_path}")
            return albums, metadata
        
        except Exception as e:
            log.error(f"Failed to import album list: {e}")
            log.debug(traceback.format_exc())
            raise ImportError(f"Failed to import album list: {e}")


class ImportError(Exception):
    """Exception raised when importing an album list fails."""
    pass


class ExportError(Exception):
    """Exception raised when exporting an album list fails."""
    pass