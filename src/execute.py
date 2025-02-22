from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from prompts import REASONING_PROMPT
from canvas import Canvas

def execute(state):
    """Execution agent that follows the collage plan step by step."""
    # Initialize chat model and canvas
    llm = ChatOpenAI(model="gpt-4", temperature=0.3)
    
    if state.get("canvas") is None:
        state["canvas"] = Canvas()
    
    canvas = state["canvas"]
    
    # Create tools from canvas methods
    tools = [
        Tool(
            name="add_layer",
            func=canvas.add_layer,
            description="Add an image layer to the canvas at specified coordinates"
        ),
        Tool(
            name="move_layer", 
            func=canvas.move_layer,
            description="Move a layer to new coordinates"
        ),
        Tool(
            name="scale_layer",
            func=canvas.scale_layer, 
            description="Scale a layer by x and y factors"
        ),
        Tool(
            name="rotate_layer",
            func=canvas.rotate_layer,
            description="Rotate a layer by specified angle"
        ),
        Tool(
            name="inspect_canvas",
            func=canvas.inspect_canvas,
            description="View the current state of the canvas"
        )
    ]

    # Create prompt template
    prompt = ChatPromptTemplate.from_template(REASONING_PROMPT)
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)

    # Get current step from plan
    current_step = state["plan"].steps[state.get("current_step_index", 0)]
    
    # Execute the step
    result = agent_executor.invoke({
        "input": f"Step description: {current_step.step}\nImage description: {current_step.image}"
    })
    
    # Update state
    state["current_step_index"] += 1
    state["tools_output"] = result
    
    return state
