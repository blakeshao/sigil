from PIL import Image
from schema import Img
import base64
import os
from datetime import datetime
from constants import IMAGE_WIDTH, IMAGE_HEIGHT

def convert_png_to_pil(file_path: str) -> Image.Image:
    """Convert a local PNG file to a PIL Image.
    
    Args:
        file_path: Path to the local PNG image file
        
    Returns:
        PIL Image object
    """
    # Open and load the image file
    image = Image.open(file_path)
    
    # Convert to RGBA mode if not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
        
    return image

def convert_png_to_base64(file_path: str) -> str:
    """Convert a local PNG file to a base64 string.
    
    Args:
        file_path: Path to the local PNG image file
        
    Returns:
        Base64 string
    """
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def scale_to_fit(image: Image.Image) -> Image.Image:
    """Scale an image to fit within the standard image dimensions while maintaining aspect ratio.
    
    Args:
        image: PIL Image to scale
        
    Returns:
        Scaled PIL Image
    """
    
    
    # Get current dimensions
    width, height = image.size
    print(f"Current dimensions: {width}x{height}")
    if width < IMAGE_WIDTH or height < IMAGE_HEIGHT:
        return image
    
    # Calculate scaling ratios
    width_ratio = (float)(float(IMAGE_WIDTH) / float(width))
    height_ratio = (float)(float(IMAGE_HEIGHT) / float(height))
    
    # Use the smaller ratio to ensure image fits within bounds
    scale = min(width_ratio, height_ratio)
    
    # Calculate new dimensions
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    print(f"Scaling image from {width}x{height} to {new_width}x{new_height}")
    # Resize the image
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def convert_png_to_img(file_path: str) -> Img:
    """Convert a local PNG file to an Img object.
    
    Args:
        file_path: Path to the local PNG image file
        
    Returns:
        Img object
    """
    image = convert_png_to_pil(file_path)
    image = scale_to_fit(image)
    return Img(image=image, base64=convert_png_to_base64(file_path), dimensions=image.size)


