from typing import Dict, TypedDict, Annotated, List
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolExecutor
from operator import itemgetter
from canvas import Canvas


# Define the state schema
class AgentState(TypedDict):
    messages: list[str]
    current_step: str
    tool_output: str | None
    tools_output: List[Dict] | None



# Create tool executor with multiple tools
tools = [Canvas()]
tool_executor = ToolExecutor(tools)

# Initialize the state graph
workflow = StateGraph(AgentState)

def planning(state: AgentState) -> AgentState:
    # Example processing step
    return state

# Define nodes/steps that will be added to the graph
def reasoning(state: AgentState) -> AgentState:
    # Example processing step
    return state


## TODO: Add more fine-grained end conditions
def end_condition(state: AgentState) -> str:
    return "END" if state["tools_output"] is not None else "tools"

# Add nodes to the graph
workflow.add_node("reasoning", reasoning)
workflow.add_node("tools", tool_executor)

# Define edges between nodes
workflow.set_entry_point("planning")
workflow.add_edge("planning", "reasoning")
workflow.add_conditional_edges(
    "reasoning",
    end_condition,
    {
        "END": END,
        "tools": "tools"
    }
)
workflow.add_edge("tools", "reasoning")

# Compile the graph
app = workflow.compile()

def run_workflow(messages: list[str]) -> Dict:
    """
    Run the workflow with initial messages
    """
    result = app.run({
        "messages": messages,
        "current_step": "planning",
        "tool_output": None,
        "tools_output": None
    })
    return result


