from langchain_openai import ChatOpenAI
from typing import List
import json
from prompts import PLANNING_PROMPT
from dotenv import load_dotenv
from schema import Plan, Step
import os
from datetime import datetime
from langchain.agents import create_react_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
load_dotenv()


def run_planning(state):
    """Planning agent that creates a collage plan based on input images."""
    # Initialize chat model
    llm = ChatOpenAI(model="gpt-4o", temperature=1.0)
    
    # Create messages list with system prompt and images
    messages = [{
        "role": "system",
        "content": PLANNING_PROMPT
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
        if content.startswith("```json"):
            content = content.split("```json")[1]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
            
        # Parse the JSON response
        plan_data = json.loads(content.strip())
        
        # Create Plan object with proper Step objects
        steps = [Step(step=s["step"], image_id=s["image_id"]) for s in plan_data["plan"]]
        state["plan"] = Plan(theme=plan_data["theme"], steps=steps)
        state["current_step_index"] = 0
        
    except json.JSONDecodeError as e:
        print("Failed to parse response:", content)
        raise ValueError(f"Failed to parse agent response as JSON: {e}")
        
    return state


