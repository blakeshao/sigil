from pydantic import BaseModel
from typing import List, Dict, Tuple, Optional, TypedDict, Sequence
from PIL import Image
from langchain.schema import BaseMessage
from langgraph.graph import add_messages
from typing import Annotated


class Step(BaseModel):
    step: str
    image_id: Optional[str] = None

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
    
class AgentState(TypedDict):
    images: dict[str, Img]
    messages: Annotated[list[BaseMessage], add_messages]
    canvas: any
    plan: Plan | None
    current_step_index: int
    reference_image: Img | None
    reference_image_base64: str | None
