# image_utils.py
"""
Image utility functions for thumbnail generation and image processing.
"""

import logging
import os
from PIL import Image

logger = logging.getLogger(__name__)


def create_thumbnail(image_path: str, thumbnail_path: str, size: tuple = (300, 300)) -> bool:
    """
    Create a thumbnail from an image file.
    
    Args:
        image_path: Path to original image
        thumbnail_path: Path to save thumbnail
        size: Thumbnail size (width, height)
    
    Returns:
        True if thumbnail created successfully, False otherwise
    """
    try:
        logger.info(f"Creating thumbnail from {image_path} to {thumbnail_path}")
        
        # Open image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for PNG with alpha channel)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail (maintains aspect ratio)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
        
        logger.info(f"Thumbnail created successfully: {thumbnail_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return False


def get_thumbnail_path(image_path: str) -> str:
    """
    Get the thumbnail path for an image.
    
    Args:
        image_path: Path to original image
    
    Returns:
        Path to thumbnail file
    """
    # Get directory and filename
    directory = os.path.dirname(image_path)
    filename = os.path.basename(image_path)
    
    # Create thumbnail filename (thumb_ prefix, .jpg extension)
    name, _ = os.path.splitext(filename)
    thumbnail_filename = f"thumb_{name}.jpg"
    
    return os.path.join(directory, thumbnail_filename)
