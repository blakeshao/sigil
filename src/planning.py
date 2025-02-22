from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from typing import List
import json
from prompts import PLANNING_PROMPT
from langchain_core.agents import create_react_agent

def planning(state):
    """Planning agent that creates a collage plan based on input images."""
    # Initialize chat model
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_template(PLANNING_PROMPT)
    
    # Format messages
    messages = prompt.format_messages()
    agent = create_react_agent(llm, prompt)

    # Convert images to base64 strings for the LLM
    image_messages = []
    for i, image in enumerate(state["images"]):
        image_messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image_bytes": image
                },
                {
                    "type": "text", 
                    "text": f"Image {i+1}"
                }
            ]
        })
    
    # Add image messages to the prompt messages
    messages.extend(image_messages)

    response = agent.invoke({"messages": messages})
    
    
    try:
        # Parse the JSON response
        plan = json.loads(response.content)
        
        # Update state with plan
        state["theme"] = plan["theme"]
        state["plan"] = plan["plan"]
        state["current_step_index"] = 0
        
    except json.JSONDecodeError:
        # Handle invalid JSON response
        state["error"] = "Failed to parse planning response"
        
    return state

