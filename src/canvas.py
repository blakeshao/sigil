from PIL import Image
import numpy as np
from langgraph.prebuilt import tool


class Canvas:
    def __init__(self):
        # Change to RGBA mode to support transparency
        self.canvas = Image.new("RGBA", (1000, 1000), (0, 0, 0, 0))
        self.layers = {}  # Dictionary to store layers
        self.layer_counter = 0

    @tool()
    def add_layer(self, image: Image.Image, x: int, y: int) -> int:
        """Add an image as a new layer to the canvas at the specified coordinates.
        
        Args:
            image: PIL Image to add to the canvas
            x: x-coordinate for placement
            y: y-coordinate for placement
            
        Returns:
            layer_id: Unique identifier for the added layer
        """
        # Convert image to RGBA if it isn't already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        self.layer_counter += 1
        layer_id = self.layer_counter
        
        # Store the layer info
        self.layers[layer_id] = {
            'image': image,
            'position': (x, y)
        }
        
        # Composite all layers
        self._update_canvas()
        return layer_id

    @tool()
    def move_layer(self, layer_id: int, x: int, y: int):
        """Move a specific layer to a new position.
        
        Args:
            layer_id: ID of the layer to move
            x: new x-coordinate
            y: new y-coordinate
        """
        if layer_id in self.layers:
            self.layers[layer_id]['position'] = (x, y)
            self._update_canvas()

    @tool()
    def scale_layer(self, layer_id: int, scale_x: float, scale_y: float):
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

    @tool()
    def rotate_layer(self, layer_id: int, angle: float):
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
    
    @tool()
    def delete_layer(self, layer_id: int):
        """Delete a specific layer.
        
        Args:
            layer_id: ID of the layer to delete
        """
        if layer_id in self.layers:
            del self.layers[layer_id]
            self._update_canvas()

    @tool()
    def inspect_canvas(self) -> Image.Image:
        """Inspect the current canvas."""
        return self.canvas

  

    def _update_canvas(self):
        """Internal method to update the canvas by compositing all layers."""
        # Start with a blank transparent canvas
        self.canvas = Image.new("RGBA", (1000, 1000), (0, 0, 0, 0))
        
        # Composite all layers in order
        for layer_id in sorted(self.layers.keys()):
            layer = self.layers[layer_id]
            self.canvas.paste(layer['image'], layer['position'], layer['image'])

  

