from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from typing import List
import json
from prompts import END_CONDITION_PROMPT
from langchain.agents import create_react_agent
from dotenv import load_dotenv
load_dotenv()


def determine_end_condition(state):
    """Determine the end condition based on the current state."""
    # Initialize chat model
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    # Convert PIL Image to base64 string
    import base64
    from io import BytesIO

    # Save the canvas to a bytes buffer
    buffer = BytesIO()
    state["canvas"].canvas.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    messages = [
        {"role": "system", "content": END_CONDITION_PROMPT},
        {"role": "user", "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_str}"
                }
            },
            {
                "type": "text",
                "text": "The plan is: " + state["plan"].theme + " and the steps are: " + str(state["plan"].steps)
            },
            {"type": "text", "text": "Based on this canvas and the plan, determine if the game should end."}
        ]}
    ]
    
    response = llm.invoke(messages)
    return response.content

