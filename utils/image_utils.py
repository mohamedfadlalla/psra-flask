"""
Image Processing Utilities Module

Provides image upload and processing utilities to reduce duplicate code
for handling profile pictures and event images.
"""

import os
from PIL import Image
from werkzeug.utils import secure_filename
from flask import url_for
from typing import Optional, Tuple


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory to ensure exists
    """
    os.makedirs(directory, exist_ok=True)


def process_image(
    file,
    output_path: str,
    size: Optional[Tuple[int, int]] = None,
    crop_square: bool = False,
    quality: int = 85
) -> bool:
    """
    Process and save an image file with optional resizing and cropping.
    
    Args:
        file: The uploaded file object
        output_path: Full path where the image should be saved
        size: Optional tuple of (width, height) for resizing
        crop_square: If True, crop to square from center before resizing
        quality: JPEG quality (1-100)
    
    Returns:
        True if successful, False if an error occurred
    """
    try:
        image = Image.open(file)
        
        # Convert to RGB if necessary (handles RGBA and palette images)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Crop to square from center if requested
        if crop_square:
            size_min = min(image.size)
            left = (image.width - size_min) // 2
            top = (image.height - size_min) // 2
            right = left + size_min
            bottom = top + size_min
            image = image.crop((left, top, right, bottom))
        
        # Resize if size is specified
        if size:
            image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Ensure output directory exists
        ensure_directory_exists(os.path.dirname(output_path))
        
        # Save the image
        image.save(output_path, quality=quality)
        return True
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return False


def process_profile_picture(
    file,
    user_id: int,
    upload_folder: str,
    app_root: str,
    size: Tuple[int, int] = (150, 150)
) -> Optional[str]:
    """
    Process and save a profile picture.
    
    Args:
        file: The uploaded file object
        user_id: The user's ID for filename generation
        upload_folder: The upload folder path (relative to app root)
        app_root: The application root path
        size: Target size for the profile picture (default 150x150)
    
    Returns:
        URL path to the saved image, or None if processing failed
    """
    filename = secure_filename(f"{user_id}_profile_{file.filename}")
    full_upload_path = os.path.join(app_root, upload_folder)
    output_path = os.path.join(full_upload_path, filename)
    
    if process_image(file, output_path, size=size, crop_square=True):
        return url_for('static', filename=f'profile_images/{filename}')
    
    return None


def save_event_image(
    file,
    app_root: str,
    images_folder: str = 'static/images'
) -> Optional[str]:
    """
    Save an event image without resizing.
    
    Args:
        file: The uploaded file object
        app_root: The application root path
        images_folder: The folder for event images
    
    Returns:
        Filename of the saved image, or None if saving failed
    """
    filename = secure_filename(file.filename)
    images_dir = os.path.join(app_root, images_folder)
    output_path = os.path.join(images_dir, filename)
    
    ensure_directory_exists(images_dir)
    
    try:
        file.save(output_path)
        return filename
    except Exception as e:
        print(f"Error saving event image: {e}")
        return None


def delete_file(file_path: str) -> bool:
    """
    Delete a file if it exists.
    
    Args:
        file_path: Full path to the file to delete
    
    Returns:
        True if file was deleted or didn't exist, False on error
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def get_event_image_path(filename: str, app_root: str) -> str:
    """
    Get the full path for an event image.
    
    Args:
        filename: The image filename
        app_root: The application root path
    
    Returns:
        Full path to the event image
    """
    return os.path.join(app_root, 'static', 'images', filename)
