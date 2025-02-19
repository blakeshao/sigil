from typing import Dict, TypedDict, Annotated, List
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolExecutor
from operator import itemgetter

# Define the state schema
class AgentState(TypedDict):
    messages: list[str]
    current_step: str
    tool_output: str | None
    tools_output: List[Dict] | None

# Define sample tools
class Calculator:
    def add(self, a: int, b: int) -> int:
        """Add two numbers"""
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a"""
        return a - b

class TextProcessor:
    def count_words(self, text: str) -> int:
        """Count words in a text"""
        return len(text.split())
    
    def to_uppercase(self, text: str) -> str:
        """Convert text to uppercase"""
        return text.upper()

# Create tool executor with multiple tools
tools = [Calculator(), TextProcessor()]
tool_executor = ToolExecutor(tools)

# Initialize the state graph
workflow = StateGraph(AgentState)

# Define nodes/steps that will be added to the graph
def process_step(state: AgentState) -> AgentState:
    # Example processing step
    return state

def multi_tool_step(state: AgentState) -> AgentState:
    # Example of multiple tool executions
    results = []
    
    # Example calculator tool usage
    calc_result = tool_executor.invoke({
        "name": "Calculator.add",
        "arguments": {"a": 1, "b": 2}
    })
    results.append({"tool": "Calculator.add", "result": calc_result})
    
    # Example text processor tool usage
    text_result = tool_executor.invoke({
        "name": "TextProcessor.count_words",
        "arguments": {"text": "Hello world"}
    })
    results.append({"tool": "TextProcessor.count_words", "result": text_result})
    
    state["tools_output"] = results
    return state

# Add nodes to the graph
workflow.add_node("process", process_step)
workflow.add_node("tools", multi_tool_step)

# Define edges between nodes
workflow.set_entry_point("process")
workflow.add_edge("process", "tools")

# Compile the graph
app = workflow.compile()

def run_workflow(messages: list[str]) -> Dict:
    """
    Run the workflow with initial messages
    """
    result = app.run({
        "messages": messages,
        "current_step": "process",
        "tool_output": None,
        "tools_output": None
    })
    return result


