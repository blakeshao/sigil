from PIL import Image
import numpy as np
from schema import Img 
from constants import IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_BACKGROUND_COLOR
from utils import convert_png_to_img
import uuid


class Canvas:
    def __init__(self, layers: dict[str, Img], images: dict[str, Img], current_layer_id: str | None):
        # Change to RGBA mode to support transparency
        self.canvas = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), IMAGE_BACKGROUND_COLOR)
        self.layers = layers  # Dictionary to store layers
        self.images = images
        self.current_layer_id = current_layer_id

    def add_layer(self, img_id: str, x: int, y: int) -> int:
        """Add an image as a new layer to the canvas at the specified coordinates.
        
        Args:
            img_id: id of the image to add to the canvas
            x: x-coordinate for placement
            y: y-coordinate for placement
            
        Returns:
            layer_id: Unique identifier for the added layer
        """
        # Convert image to RGBA if it isn't already
        image = self.images[img_id].image
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        layer_id = str(uuid.uuid4())
        
        # Store the layer info
        self.layers[layer_id] = {
            'image': image,
            'position': (x, y)
        }
        
        # Composite all layers
        self._update_canvas()
        self.current_layer_id = layer_id
        return layer_id

    def move_layer(self, layer_id: str, x: int, y: int):
        """Move a specific layer to a new position.
        
        Args:
            layer_id: ID of the layer to move
            x: new x-coordinate
            y: new y-coordinate
        """
        if layer_id in self.layers:
            self.layers[layer_id]['position'] = (x, y)
            self._update_canvas()

    def scale_layer(self, layer_id: str, scale_x: float, scale_y: float):
        """Scale a specific layer.
        
        Args:
            layer_id: ID of the layer to scale
            scale_x: horizontal scale factor (1.0 = original size)
            scale_y: vertical scale factor (1.0 = original size)
        """
        if layer_id in self.layers:
            original = self.layers[layer_id]['image']
            new_width = int(original.width * scale_x)
            new_height = int(original.height * scale_y)
            scaled = original.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.layers[layer_id]['image'] = scaled
            self._update_canvas()

    def rotate_layer(self, layer_id: str, angle: float):
        """Rotate a specific layer.
        
        Args:
            layer_id: ID of the layer to rotate
            angle: Angle in degrees to rotate the layer 
        """
        if layer_id in self.layers:
            original = self.layers[layer_id]['image']
            rotated = original.rotate(angle, expand=True)
            self.layers[layer_id]['image'] = rotated
            self._update_canvas()

    def delete_layer(self, layer_id: str):
        """Delete a specific layer.
        
        Args:
            layer_id: ID of the layer to delete
        """
        if layer_id in self.layers:
            del self.layers[layer_id]
            self._update_canvas()


    def inspect_canvas(self) -> Image.Image:
        """Inspect the current canvas."""
        return self.canvas

  

    def _update_canvas(self):
        """Internal method to update the canvas by compositing all layers."""
        # Start with a blank transparent canvas
        self.canvas = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), IMAGE_BACKGROUND_COLOR)
        
        # Composite all layers in order
        for layer_id in sorted(self.layers.keys()):
            layer = self.layers[layer_id]
            self.canvas.paste(layer['image'], layer['position'], layer['image'])

  

def main():
    # Open the image
    image = convert_png_to_img("img/1.png")
    
    # Create the images dictionary with proper Img instantiation
    images = {
        "1": image
    }
    
    canvas = Canvas(images, {}, None)
    id_1 = canvas.add_layer("1", 0, 0)
    canvas.move_layer(id_1, 200, 200)
    id_2 = canvas.add_layer("1", 0, 0)
    canvas.scale_layer(id_2, 0.5, 0.5)
    canvas.rotate_layer(id_2, 45)
    canvas.canvas.show()

if __name__ == "__main__":
    main()