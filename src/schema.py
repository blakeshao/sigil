from pydantic import BaseModel
from typing import List, Dict, Tuple
from PIL import Image


class Step(BaseModel):
    step: str
    image_id: str

class Plan(BaseModel):
    theme: str
    steps: List[Step]

class Img(BaseModel):
    image: Image.Image
    base64: str
    dimensions: Tuple[int, int]
    
    model_config = {
        "arbitrary_types_allowed": True
    }

