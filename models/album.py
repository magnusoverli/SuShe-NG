"""
Album data model
"""

from datetime import date
from typing import Optional


class Album:
    """Class representing a musical album."""
    
    def __init__(self, artist: str, name: str, release_date: date,
                 genre1: str, genre2: str = "", comment: str = "", 
                 cover_image: Optional[str] = None):
        """
        Initialize an Album object.
        
        Args:
            artist: Name of the artist/band
            name: Name of the album
            release_date: Release date of the album
            genre1: Primary genre
            genre2: Secondary genre (optional)
            comment: Additional comments (optional)
            cover_image: Path to cover image file (optional)
        """
        self.artist = artist
        self.name = name
        self.release_date = release_date
        self.genre1 = genre1
        self.genre2 = genre2
        self.comment = comment
        self.cover_image = cover_image
    
    def __str__(self) -> str:
        """Return string representation of the album."""
        return f"{self.artist} - {self.name} ({self.release_date.year})"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the album."""
        return (f"Album(artist='{self.artist}', name='{self.name}', "
                f"release_date={self.release_date}, genre1='{self.genre1}', "
                f"genre2='{self.genre2}', comment='{self.comment}')")