from langchain_openai import ChatOpenAI
import json
from prompts import PLANNING_PROMPT
from dotenv import load_dotenv
from schema import Plan, Step

load_dotenv()


def run_planning(state):
    """Planning agent that creates a collage plan based on input images."""
    # Initialize chat model
    llm = ChatOpenAI(model="gpt-4o", temperature=1.0)
    
    # Create messages list with system prompt and images
    messages = [{
        "role": "system",
        "content": PLANNING_PROMPT
    }, {
        "role": "user",
        "content": [
            {"type": "text", "text": "The command is in the previous messages: " + str(state["messages"])}
        ]
    }]
    
    # Add images to messages
    for image_id, image in state["images"].items():
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image.base64}"
                    }
                },
                {
                    "type": "text",
                    "text": f"Image dimensions: {image.dimensions}"
                },
                {
                    "type": "text",
                    "text": f"Image id: {image_id}"
                }
            ]
        })

    # Get response from LLM
    response = llm.invoke(messages)
    print(response.content)
    
    try:
        # Clean the response - remove any potential markdown or extra text
        content = response.content.strip()
        
      
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end != 0:
            content = content[start:end]
        
        # Parse the JSON response
        plan_data = json.loads(content)
        
        # Create Plan object with proper Step objects
        steps = [Step(step=s["step"], image_id=s["image_id"]) for s in plan_data["plan"]]
        state["plan"] = Plan(theme=plan_data["theme"], steps=steps)
        state["current_step_index"] = 0
        
    except json.JSONDecodeError as e:
        print("Failed to parse response:", content)
        # For debugging, print the problematic character
        if isinstance(e, json.JSONDecodeError):
            pos = e.pos
            print(f"Error at position {pos}")
            print(f"Characters around error: {content[max(0, pos-10):min(len(content), pos+10)]}")
        raise ValueError(f"Failed to parse agent response as JSON: {e}")
        
    return state


