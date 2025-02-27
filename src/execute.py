from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from prompts import EXECUTION_PROMPT
from agent_canvas import Canvas
from dotenv import load_dotenv
import json
from constants import IMAGE_WIDTH, IMAGE_HEIGHT
from langchain.schema import AIMessage
import os
from datetime import datetime
from langchain.tools import tool
from visual_tool import VisualTool
load_dotenv()






def run_execute(state):
    """Execution agent that follows the collage plan step by step."""
    # Initialize chat model and canvas
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    
    if state.get("canvas") is None:
        state["canvas"] = Canvas(state["images"])
    
    canvas = state["canvas"]


    # Create tools from canvas methods with proper parameter handling
    tools = [
        Tool(
            name="add_layer",
            func=lambda input_str: canvas.add_layer(**json.loads(input_str)),
            description="Add an image layer to the canvas. Input should be JSON string with: {\"img_id\": \"string\", \"x\": number, \"y\": number}"
        ),
        Tool(
            name="move_layer",
            func=lambda input_str: canvas.move_layer(**json.loads(input_str)),
            description="Move a layer on the canvas. Input should be JSON string with: {\"layer_id\": \"string\", \"x\": number, \"y\": number}"
        ),
        Tool(
            name="scale_layer",
            func=lambda input_str: canvas.scale_layer(**json.loads(input_str)),
            description="Scale a layer. Input should be JSON string with: {\"layer_id\": \"string\", \"scale\": number}"
        ),
        Tool(
            name="rotate_layer",
            func=lambda input_str: canvas.rotate_layer(**json.loads(input_str)),
            description="Rotate a layer. Input should be JSON string with: {\"layer_id\": \"string\", \"angle\": number}"
        ),
        Tool(
            name="add_text",
            func=lambda input_str: canvas.add_text(**json.loads(input_str)),
            description="Add text to the canvas. Input should be JSON string with: {\"text\": \"string\", \"x\": number, \"y\": number, \"color\": \"string\", \"font_size\": number}"
        )
    ]

    # Create prompt template
    prompt = ChatPromptTemplate.from_template(EXECUTION_PROMPT)
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)



    
    
    
    # If you want to add custom messages to the memory
    # memory.chat_memory.add_user_message("Remember to place images carefully.")
    # memory.chat_memory.add_ai_message("I'll make sure to create a balanced composition.")
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools,
        handle_parsing_errors=True,
        max_iterations=5,
        verbose=True,
    )

    # Get current step from plan
    step_index = state.get("current_step_index", 0)
    print(f"Step index: {step_index}")
    if step_index >= len(state["plan"].steps):
        return state  # or handle end of execution
    current_step = state["plan"].steps[step_index]
    print(f"Current step: {current_step}")
    # Execute the current step
    result = agent_executor.invoke({
        "input": current_step.step,
        "image_id": current_step.image_id,
        "agent_scratchpad": "",
        "tools": str(tools),
        "layer_id": state["canvas"].current_layer_id,
        "width": IMAGE_WIDTH,
        "height": IMAGE_HEIGHT,
    })

    state["current_step_index"] += 1
    return state
    
 

