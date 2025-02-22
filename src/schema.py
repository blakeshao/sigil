from pydantic import BaseModel
from typing import List

class Step(BaseModel):
    step: str
    image: str

class Plan(BaseModel):
    theme: str
    steps: List[Step]