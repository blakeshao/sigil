from typing import Dict, TypedDict, Annotated, List
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolExecutor
from operator import itemgetter
from canvas import Canvas
from PIL import Image
from schema import Plan
# Define the state schema
class AgentState(TypedDict):
    images: list[Image.Image]
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
    return state

# Define nodes/steps that will be added to the graph
def execute(state: AgentState) -> AgentState:
    # Example processing step
    return state


## TODO: Add more fine-grained end conditions
def end_condition(state: AgentState) -> str:
    return "END" if state["tools_output"] is not None else "tools"

# Add nodes to the graph
workflow.add_node("execute", execute)
workflow.add_node("plan", plan)

# Define edges between nodes
workflow.set_entry_point("plan")
workflow.add_edge("plan", "execute")
workflow.add_conditional_edges(
    "execute",
    end_condition,
    {
        "END": END,
        "execute": "execute"
    }
)


# Compile the graph
app = workflow.compile()

def run_workflow(images: list[Image.Image], messages: list[str]) -> Dict:
    """
    Run the workflow with initial messages
    """
    result = app.run({
        "images": images,
        "messages": messages,
        "current_step": "plan",
        "tool_output": None,
        "tools_output": None,
        "canvas": Canvas(),
        "plan": None,
        "current_step_index": 0
    })
    return result


