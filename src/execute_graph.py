from typing import Dict
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolExecutor
from operator import itemgetter
from agent_canvas import Canvas
from PIL import Image
from schema import Plan, Img, AgentState
from planning import run_planning
from langchain_openai import ChatOpenAI
import os
from datetime import datetime
from langchain.prompts import ChatPromptTemplate
from prompts import EXECUTION_PROMPT
from langgraph.prebuilt import ToolNode
from constants import IMAGE_WIDTH, IMAGE_HEIGHT
from typing import TypedDict
from langchain.tools import Tool
import json
from typing import Sequence
from langchain.schema import BaseMessage
from langchain.schema.runnable.config import RunnableConfig
from typing import Annotated
from langgraph.graph import add_messages
from langchain.schema import AIMessage
import tiktoken


def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if "DONE" in last_message.content:
        return END
    return "tools"

def call_model(state: AgentState, llm, tools):
    sys_message = [
        {
            "type": "system",
            "content": EXECUTION_PROMPT
        },
    ]
    history_messages = []
    for msg in state["messages"]:
        if hasattr(msg, "content") and not isinstance(msg.content, list):
            history_messages.append({
                "role": "assistant" if isinstance(msg, AIMessage) else "human",
                "content": msg.content
            })
    canvas_messages = [
        {
            "type": "human",
            "content": [
                {
                    "type": "text",
                    "text": "Current canvas state:"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{state['canvas'].get_canvas_base64()}"
                    }
                },
                {
                    "type": "text",
                    "text": f"Current design step: {state['plan'].steps[state['current_step_index']].step}\n"
                    f"Image asset ID: {state['plan'].steps[state['current_step_index']].image_id}\n"
                    f"Layer ID for editing: {state['canvas'].current_layer_id}\n"
                    f"Available tools: {[tool.name for tool in tools]}"
                }
            ]
        }
    ]

    messages = sys_message + history_messages + canvas_messages
    
    enc = tiktoken.encoding_for_model("gpt-4o")
    print(f"Token length of messages: {len(enc.encode(str(messages)))}")

    response = llm.invoke(messages)
    print(response.content)
    return {"messages": [response]}

def create_agent_node(llm, tools):
    """Create an agent node that uses the provided agent"""
    def _call_model(state: AgentState):
        return call_model(state, llm, tools)
    return _call_model

def graph(state: AgentState):
    workflow = StateGraph(AgentState)

    llm = ChatOpenAI(model="gpt-4o", temperature=0.0)  # Changed to vision model
    tools = [
        Tool(
            name="add_layer",
            func=lambda input_str: state["canvas"].add_layer(**json.loads(input_str) if isinstance(input_str, str) else input_str),
            description="Add an image layer to the canvas. Input should be JSON string with: {\"img_id\": \"string\", \"x\": number, \"y\": number}"
        ),  
        Tool(
            name="move_layer",
            func=lambda input_str: state["canvas"].move_layer(**json.loads(input_str) if isinstance(input_str, str) else input_str),
            description="Move a layer on the canvas. Input should be JSON string with: {\"layer_id\": \"string\", \"x\": number, \"y\": number}"
        ),
        Tool(
            name="scale_layer",
            func=lambda input_str: state["canvas"].scale_layer(**json.loads(input_str) if isinstance(input_str, str) else input_str),
            description="Scale a layer. Input should be JSON string with: {\"layer_id\": \"string\", \"scale\": number}"
        ),
        Tool(
            name="rotate_layer",
            func=lambda input_str: state["canvas"].rotate_layer(**json.loads(input_str) if isinstance(input_str, str) else input_str),
            description="Rotate a layer. Input should be JSON string with: {\"layer_id\": \"string\", \"angle\": number}"
        ),
        Tool(
            name="add_text",
            func=lambda input_str: state["canvas"].add_text(**json.loads(input_str) if isinstance(input_str, str) else input_str),
            description="Add text to the canvas. Input should be JSON string with: {\"text\": \"string\", \"x\": number, \"y\": number, \"color\": \"string\", \"font_size\": number}"
        )
    ]
    
    llm_with_tools = llm.bind_tools(tools)

    tool_node = ToolNode(tools=tools)

    # Define the two nodes we will cycle between
    workflow.add_node("agent", create_agent_node(llm_with_tools, tools))
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")

    app = workflow.compile()

    return app


def run_execute(state: AgentState) -> Dict:
    """
    Run the workflow with initial messages
    """
    app = graph(state)
    result = None
    try:
        result = app.invoke(state, config={"recursion_limit": 100})
    except Exception as e:
        print(f"Error: {e}")
        os.makedirs("results", exist_ok=True)
        if result and result.get("canvas") is not None:
            result["canvas"].canvas.save(f"results/output_at_limit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        raise

    state["current_step_index"] += 1

    return state
        
        