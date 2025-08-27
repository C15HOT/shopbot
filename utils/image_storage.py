
import os
import shutil
import uuid
from typing import Optional
from pathlib import Path

# Directory for storing images
IMAGES_DIR = "images"

def init_images_directory():
    """Create images directory if it doesn't exist"""
    Path(IMAGES_DIR).mkdir(exist_ok=True)

def generate_image_id() -> str:
    """Generate unique image ID"""
    return str(uuid.uuid4())

def get_image_path(image_id: str, extension: str = "") -> str:
    """Get full path for image file"""
    filename = f"{image_id}{extension}" if extension else image_id
    return os.path.join(IMAGES_DIR, filename)

def save_image(image_data: bytes, extension: str = ".jpg") -> str:
    """Save image data to file and return image ID"""
    init_images_directory()
    image_id = generate_image_id()
    image_path = get_image_path(image_id, extension)
    
    with open(image_path, 'wb') as f:
        f.write(image_data)
    
    return image_id

def delete_image(image_path: str) -> bool:
    """Delete image file"""
    try:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            return True
        return False
    except Exception:
        return False

def get_image_url(image_path: Optional[str]) -> Optional[str]:
    """Get URL for serving image (for web interface)"""
    if image_path and os.path.exists(image_path):
        return f"/{image_path}"
    return None
