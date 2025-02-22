from typing import Dict, TypedDict, Annotated, List
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolExecutor
from operator import itemgetter
from agent_canvas import Canvas
from PIL import Image
from schema import Plan, Img
from planning import run_planning
from execute import run_execute
from end_condition import determine_end_condition
from utils import convert_png_to_img
import os
# Define the state schema
class AgentState(TypedDict):
    images: dict[str, Img]
    messages: list[str]
    current_step: str
    tool_output: str | None
    tools_output: List[Dict] | None
    canvas: Canvas | None
    plan: Plan | None
    current_step_index: int



# Initialize the state graph
workflow = StateGraph(AgentState)

def plan(state: AgentState) -> AgentState:
    # Example processing step
    state = run_planning(state)
    return state

# Define nodes/steps that will be added to the graph
def execute(state: AgentState) -> AgentState:
    # Example processing step
    state = run_execute(state)
    return state


## TODO: Add more fine-grained end conditions
def end_condition(state: AgentState) -> str:
    end_condition = determine_end_condition(state)
    return end_condition

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

def run_workflow(images: list[Img], messages: list[str]) -> Dict:
    """
    Run the workflow with initial messages
    """
    try:
        initial_state = {
            "images": images,
            "messages": messages,
            "current_step": "plan",
            "tool_output": None,
            "tools_output": None,
        "canvas": Canvas(images),
        "plan": None,
            "current_step_index": 0
        }
        result = app.invoke(initial_state, config={"recursion_limit": 100})
    except Exception as e:
        print(f"Error: {e}")
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)
        if result["canvas"] is not None:
            result["canvas"].canvas.save("output_at_limit.png")
        raise
        
    # Save the final canvas
    result["canvas"].canvas.save("results/final_collage.png")
    return result

def main():
    images = {"1": convert_png_to_img("img/1.png"), "2": convert_png_to_img("img/2.png")}
    messages = []
    run_workflow(images, messages)


if __name__ == "__main__":
    main()

