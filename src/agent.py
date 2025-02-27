from typing import Dict, TypedDict, Annotated, List
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolExecutor
from operator import itemgetter
from agent_canvas import Canvas
from PIL import Image
from schema import Plan, Img
from planning import run_planning
from execute_graph import run_execute
from img_utils import convert_png_to_img
import os
from datetime import datetime

from langchain.schema import BaseMessage, HumanMessage
from typing import Sequence
from schema import AgentState



# Initialize the state graph
workflow = StateGraph(AgentState)

def plan(state: AgentState) -> AgentState:
    # Example processing step
    print("Planning...")
    state = run_planning(state)
    return state

# Define nodes/steps that will be added to the graph
def execute(state: AgentState) -> AgentState:
    # Example processing step
    print("Executing...")
    state = run_execute(state)
    return state


## TODO: Add more fine-grained end conditions
def end_condition(state: AgentState) -> str:
    if state["current_step_index"] == len(state["plan"].steps):
        return "END"
    return "NOT_END"

# Add nodes to the graph
workflow.add_node("execution_node", execute)
workflow.add_node("plan_node", plan)

# Define edges between nodes
workflow.set_entry_point("plan_node")
workflow.add_edge("plan_node", "execution_node")
workflow.add_conditional_edges(
    "execution_node",
    end_condition,
    {
        "END": END,
        "NOT_END": "execution_node"
    }
)


# Compile the graph
app = workflow.compile()

def run_workflow(images: dict[str, Img], messages: list[str]) -> Dict:
    """
    Run the workflow with initial messages
    """
    result = None  # Initialize result to None
    try:
        initial_state = {
            "images": images,
            "messages": messages,
            "canvas": Canvas({}, images, None),
            "plan": None,
            "current_step_index": 0,
        }
        result = app.invoke(initial_state, config={"recursion_limit": 100})
    except Exception as e:
        print(f"Error: {e}")
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)
        if result and result.get("canvas") is not None:  # Check if result exists and has canvas
            result["canvas"].canvas.save(f"results/output_at_limit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        raise
        
    # Save the final canvas
    if result and result.get("canvas") is not None:  # Add safety check here too
        result["canvas"].canvas.save(f"results/{result['plan'].theme}{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    return result

def main():
    images = {}
    for file in os.listdir("img"):
        if file.endswith(".png"):
            image_id = file.split(".")[0]
            images[image_id] = convert_png_to_img(f"img/{file}")
    messages = [  
        HumanMessage(content="Make a simple valentine's day poster for notion the company")
    ]
    print(images.keys())
    run_workflow(images, messages)


if __name__ == "__main__":
    main()

