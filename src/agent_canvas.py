from PIL import Image
from schema import Img 
from constants import IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_BACKGROUND_COLOR
from img_utils import convert_png_to_img
import uuid
from PIL import ImageDraw, ImageFont
import io
import base64
from langchain.tools import tool

class Canvas:
    def __init__(self, layers: dict[str, Img], images: dict[str, Img], current_layer_id: str | None):
        # Change to RGBA mode to support transparency
        self.canvas = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), (0,0,0,0))
        self.layers = layers  # Dictionary to store layers
        self.images = images
        self.current_layer_id = current_layer_id

    def add_layer(self, img_id: str, x: int | float, y: int | float) -> int:
        """Add an image as a new layer to the canvas at the specified coordinates.
        
        Args:
            img_id: id of the image to add to the canvas
            x: x-coordinate for placement (can be int or float, if float is between 0-1 it's treated as percentage)
            y: y-coordinate for placement (can be int or float, if float is between 0-1 it's treated as percentage)
            
        Returns:
            layer_id: Unique identifier for the added layer
        """
        print(f"Adding layer {img_id} at {x}, {y}")
        # Convert image to RGBA if it isn't already
        image = self.images[img_id].image
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        # Handle percentage-based positioning (if x or y is a float between 0 and 1)
        if isinstance(x, float) and 0 <= x <= 1:
            x = int(x * IMAGE_WIDTH)
        if isinstance(y, float) and 0 <= y <= 1:
            y = int(y * IMAGE_HEIGHT)
            
        # Ensure coordinates are integers
        x = int(x)
        y = int(y)
            
        layer_id = str(uuid.uuid4())
        
        # Store the layer info
        self.layers[layer_id] = {
            'image': image,
            'position': (x, y)
        }
        
        # Composite all layers
        self._update_canvas()
        self.current_layer_id = layer_id
        return "layer_id: " + layer_id

    def move_layer(self, layer_id: str, x: int | float, y: int | float):
        """Move a specific layer to a new position.
        
        Args:
            layer_id: ID of the layer to move
            x: new x-coordinate
            y: new y-coordinate
        """
        print(f"Moving layer {layer_id} to {x}, {y}")
        if layer_id in self.layers:
            if isinstance(x, float) and 0 <= x <= 1:
                x = int(x * IMAGE_WIDTH)
            if isinstance(y, float) and 0 <= y <= 1:
                y = int(y * IMAGE_HEIGHT)
            self.layers[layer_id]['position'] = (x, y)
            self._update_canvas()

    def scale_layer(self, layer_id: str, scale: float):
        """Scale a specific layer.
        
        Args:
            layer_id: ID of the layer to scale
            scale: scale factor (1.0 = original size)
        """
        print(f"Scaling layer {layer_id} to {scale}")
        if layer_id in self.layers:
            original = self.layers[layer_id]['image']
            new_width = int(original.width * scale)
            new_height = int(original.height * scale)
            scaled = original.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.layers[layer_id]['image'] = scaled
            self._update_canvas()

    def rotate_layer(self, layer_id: str, angle: float):
        """Rotate a specific layer.
        
        Args:
            layer_id: ID of the layer to rotate
            angle: Angle in degrees to rotate the layer 
        """
        print(f"Rotating layer {layer_id} to {angle}")
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
        print(f"Deleting layer {layer_id}")
        if layer_id in self.layers:
            del self.layers[layer_id]
            self._update_canvas()

    def add_text(self, text: str, x: int, y: int, font_size: int = 16, color: str = "black"):
        """Add text to the canvas at the specified coordinates.
        
        Args:
            text: The text to add
            x: The x-coordinate for placement
            y: The y-coordinate for placement
            font_size: The size of the font
            color: The color of the text
        """
        print(f"Adding text {text} at {x}, {y}")
        font = ImageFont.truetype("fonts/SF-Pro.ttf", font_size)
        text_layer = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (0,0,0,0))
        draw = ImageDraw.Draw(text_layer)
        draw.text((x, y), text, fill=color, font=font)
        
        # Add the text layer to layers with a unique ID
        layer_id = f"text_{len(self.layers)}"
        self.layers[layer_id] = {
            'image': text_layer,
            'position': (0, 0)
        }
        self.current_layer_id = layer_id
        self._update_canvas()

    def modify_text_color(self, layer_id: str, new_color: str):
        """Modify the color of a text layer.
        
        Args:
            layer_id: ID of the text layer to modify
            new_color: New color for the text (e.g. "red", "#FF0000")
        """
        print(f"Modifying text color of layer {layer_id} to {new_color}")
        if layer_id in self.layers and layer_id.startswith("text_"):
            # Get current text layer properties
            text_layer = self.layers[layer_id]['image']
            
            # Create new transparent layer
            new_text_layer = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (0,0,0,0))
            
            # Get text content and position from original
            text_bbox = text_layer.getbbox()
            if text_bbox:
                text_content = ImageDraw.Draw(text_layer)._text[0][1]  # Access internal text content
                x, y = text_bbox[0], text_bbox[1]  # Use bounding box for position
                
                # Get current font size from image size
                font_size = text_bbox[3] - text_bbox[1]  # Approximate from height
                font = ImageFont.truetype("fonts/SF-Pro.ttf", font_size)
                
                # Draw text with new color
                draw = ImageDraw.Draw(new_text_layer)
                draw.text((x, y), text_content, fill=new_color, font=font)
                
                # Update layer
                self.layers[layer_id]['image'] = new_text_layer
                self._update_canvas()

    def modify_text_size(self, layer_id: str, new_size: int):
        """Modify the font size of a text layer.
        
        Args:
            layer_id: ID of the text layer to modify
            new_size: New font size in pixels
        """
        print(f"Modifying text size of layer {layer_id} to {new_size}")
        if layer_id in self.layers and layer_id.startswith("text_"):
            # Get current text layer properties
            text_layer = self.layers[layer_id]['image']
            
            # Create new transparent layer
            new_text_layer = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (0,0,0,0))
            
            # Get text content and position from original
            text_bbox = text_layer.getbbox()
            if text_bbox:
                text_content = ImageDraw.Draw(text_layer)._text[0][1]  # Access internal text content
                x, y = text_bbox[0], text_bbox[1]  # Use bounding box for position
                
                # Get current color
                color = ImageDraw.Draw(text_layer)._text[0][2]  # Access internal color
                
                # Create new font with new size
                font = ImageFont.truetype("fonts/SF-Pro.ttf", new_size)
                
                # Draw text with new size
                draw = ImageDraw.Draw(new_text_layer)
                draw.text((x, y), text_content, fill=color, font=font)
                
                # Update layer
                self.layers[layer_id]['image'] = new_text_layer
                self._update_canvas()

    def get_canvas_base64(self) -> str:
        """Inspect the current canvas and return base64 encoded image.
        
        Returns:
            str: Base64 encoded PNG image of the current canvas
        """
        buffer = io.BytesIO()
        self.canvas.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return img_str
        

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