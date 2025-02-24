from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from prompts import EXECUTION_PROMPT
from agent_canvas import Canvas
from dotenv import load_dotenv
import json
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
            func=lambda x, **kwargs: canvas.add_layer(**(json.loads(x[x.find('{'): x.rfind('}')+1]) if '{' in x else json.loads(x))),
            description="Add an image layer to the canvas at specified coordinates"
        ),
        Tool(
            name="move_layer", 
            func=lambda x, **kwargs: canvas.move_layer(**(json.loads(x[x.find('{'): x.rfind('}')+1]) if '{' in x else json.loads(x))),
            description="Move a layer to new coordinates"
        ),
        Tool(
            name="scale_layer",
            func=lambda x, **kwargs: canvas.scale_layer(**(json.loads(x[x.find('{'): x.rfind('}')+1]) if '{' in x else json.loads(x))),
            description="Scale a layer by x and y factors"
        ),
        Tool(
            name="rotate_layer",
            func=lambda x, **kwargs: canvas.rotate_layer(**(json.loads(x[x.find('{'): x.rfind('}')+1]) if '{' in x else json.loads(x))),
            description="Rotate a layer by specified angle"
        ),
        Tool(
            name="inspect_canvas",
            func=lambda x, **kwargs: canvas.inspect_canvas(),
            description="View the current state of the canvas"
        )
    ]

    # Create prompt template
    prompt = ChatPromptTemplate.from_template(EXECUTION_PROMPT)
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools,
        handle_parsing_errors=True,
        max_iterations=5,
        verbose=True
    )

    # Get current step from plan
    step_index = state.get("current_step_index", 0)
    if step_index >= len(state["plan"].steps):
        return state  # or handle end of execution
    current_step = state["plan"].steps[step_index]
    
    # Execute the current step
    result = agent_executor.invoke({
        "input": current_step.step,
        "image_id": current_step.image_id,
        "agent_scratchpad": "",
        "tools": str(tools),
        "tool_names": ", ".join(t.name for t in tools)
    })
    
    # Increment step index
    state["current_step_index"] += 1
    
    return state
