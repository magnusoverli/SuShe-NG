"""
utils/album_list_manager.py

Album list manager module for SuShe NG.
This module handles importing, exporting, and managing album lists.
"""

import os
import json
import base64
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from models.album import Album


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
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            albums = []
            # Extract list title from filename if available
            list_name = os.path.splitext(os.path.basename(file_path))[0]
            
            for idx, album_data in enumerate(data):
                # Convert release date string to date object
                release_date_str = album_data.get('release_date', '')
                try:
                    # Try to parse DD-MM-YYYY format
                    day, month, year = map(int, release_date_str.split('-'))
                    release_date = date(year, month, day)
                except (ValueError, AttributeError):
                    # Fallback to today's date if parsing fails
                    release_date = date.today()
                
                # Handle cover image - decode base64 and save to file
                cover_image_path = None
                if 'cover_image' in album_data and album_data['cover_image']:
                    cover_format = album_data.get('cover_image_format', 'PNG').lower()
                    
                    # Generate a unique filename for the cover
                    album_id = album_data.get('album_id', f"import_{idx}")
                    cover_filename = f"{album_id}.{cover_format}"
                    cover_path = os.path.join(self.covers_directory, cover_filename)
                    
                    try:
                        # Decode and save the image
                        image_data = base64.b64decode(album_data['cover_image'])
                        with open(cover_path, 'wb') as img_file:
                            img_file.write(image_data)
                        cover_image_path = cover_path
                    except Exception as e:
                        print(f"Error saving cover image: {e}")
                
                # Create album object
                album = Album(
                    artist=album_data.get('artist', ''),
                    name=album_data.get('album', ''),
                    release_date=release_date,
                    genre1=album_data.get('genre_1', ''),
                    genre2=album_data.get('genre_2', ''),
                    comment=album_data.get('comments', ''),
                    cover_image=cover_image_path
                )
                
                # Store additional metadata as attributes
                album.album_id = album_data.get('album_id', '')
                album.country = album_data.get('country', '')
                album.rank = album_data.get('rank', idx + 1)
                
                albums.append(album)
            
            # Create metadata for the list
            metadata = {
                "title": list_name,
                "description": f"Imported from {os.path.basename(file_path)}",
                "date_created": datetime.now().isoformat(),
                "date_modified": datetime.now().isoformat(),
                "source_file": file_path,
                "album_count": len(albums)
            }
            
            return albums, metadata
            
        except Exception as e:
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
        # Ensure the file has the correct extension
        if not file_path.endswith(self.FILE_EXTENSION):
            file_path += self.FILE_EXTENSION
        
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
        
        # Add each album to the data structure
        for idx, album in enumerate(albums):
            album_data = {
                "artist": album.artist,
                "title": album.name,
                "release_date": album.release_date.isoformat() if album.release_date else None,
                "genre1": album.genre1,
                "genre2": album.genre2,
                "comment": album.comment,
                "cover_image_path": album.cover_image,
                "rank": idx + 1,  # Update rank based on current position
                # Add any additional fields from the Album object
                "album_id": getattr(album, "album_id", ""),
                "country": getattr(album, "country", "")
            }
            data["albums"].append(album_data)
        
        # Save the data to the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ExportError(f"Failed to export album list: {e}")
    
    def import_from_new_format(self, file_path: str) -> Tuple[List[Album], Dict[str, Any]]:
        """
        Import albums from the new format JSON file.
        
        Args:
            file_path: Path to the new format JSON file
            
        Returns:
            tuple: (list of Album objects, metadata dict)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check format version for compatibility
            format_version = data.get("format_version", 0)
            if format_version > self.CURRENT_FORMAT_VERSION:
                print(f"Warning: File format version ({format_version}) is newer than supported ({self.CURRENT_FORMAT_VERSION})")
            
            # Extract metadata
            metadata = data.get("metadata", {})
            
            # Process albums
            albums = []
            for album_data in data.get("albums", []):
                # Parse release date
                release_date_str = album_data.get("release_date")
                if release_date_str:
                    try:
                        release_date = date.fromisoformat(release_date_str)
                    except ValueError:
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
                    cover_image=album_data.get("cover_image_path")
                )
                
                # Add any additional fields
                if "album_id" in album_data:
                    album.album_id = album_data["album_id"]
                if "country" in album_data:
                    album.country = album_data["country"]
                if "rank" in album_data:
                    album.rank = album_data["rank"]
                
                albums.append(album)
            
            return albums, metadata
        
        except Exception as e:
            raise ImportError(f"Failed to import album list: {e}")


class ImportError(Exception):
    """Exception raised for errors during import."""
    pass


class ExportError(Exception):
    """Exception raised for errors during export."""
    pass