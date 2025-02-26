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
load_dotenv()







# def handle_canvas_inspection(canvas, memory):
#     """Handle the canvas inspection results."""
#     memory.chat_memory.add_ai_message(AIMessage(
#         content=[
#             {
#                 "type": "text",
#                 "text": "Here is the current state of the canvas:"
#             },
#             {
#                 "type": "image_url",
#                 "image_url": {
#                     "url": f"data:image/png;base64,{canvas.inspect_canvas()}"
#                 }
#             }
#         ]
#     ))
#     print("memory", memory)
    

 

# def run_execute(state):
#     """Execution agent that follows the collage plan step by step."""
#     # Initialize chat model and canvas
#     llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    
#     if state.get("canvas") is None:
#         state["canvas"] = Canvas(state["images"])
    
#     canvas = state["canvas"]
#     memory = ConversationBufferMemory(
#         return_messages=True,
#         input_key="input",
#         memory_key="chat_history",
#         output_key="output"
#     )

#     # Create tools from canvas methods with proper parameter handling
#     tools = [
#         Tool(
#             name="add_layer",
#             func=lambda x, **kwargs: {canvas.add_layer(**(json.loads(x[x.find('{'): x.rfind('}')+1]) if '{' in x else json.loads(x)))},
#             description="Add an image layer to the canvas at specified coordinates"
#         ),
#         Tool(
#             name="move_layer", 
#             func=lambda x, **kwargs: {canvas.move_layer(**(json.loads(x[x.find('{'): x.rfind('}')+1]) if '{' in x else json.loads(x)))},
#             description="Move a layer to new coordinates"
#         ),
#         Tool(
#             name="scale_layer",
#             func=lambda x, **kwargs: {canvas.scale_layer(**(json.loads(x[x.find('{'): x.rfind('}')+1]) if '{' in x else json.loads(x)))},
#             description="Scale a layer by x and y factors"
#         ),
#         Tool(
#             name="rotate_layer",
#             func=lambda x, **kwargs: {canvas.rotate_layer(**(json.loads(x[x.find('{'): x.rfind('}')+1]) if '{' in x else json.loads(x)))},
#             description="Rotate a layer by specified angle"
#         ),
#         Tool(
#             name="add_text",
#             func=lambda x, **kwargs: {canvas.add_text(**(json.loads(x[x.find('{'): x.rfind('}')+1]) if '{' in x else json.loads(x)))},
#             description="Add text to the canvas at specified coordinates"
#         )
#     ]

#     # Create prompt template
#     prompt = ChatPromptTemplate.from_template(EXECUTION_PROMPT)
    
#     # Create the agent
#     agent = create_react_agent(llm, tools, prompt)


#     class CanvasAwareAgentExecutor(AgentExecutor):
#         def _take_next_step(self, *args, **kwargs):
#             result = super()._take_next_step(*args, **kwargs)
            
#             canvas_state = state["canvas"].inspect_canvas()
#             self.memory.chat_memory.add_ai_message(AIMessage(
#                 content=[
#                     {"type": "text", "text": "Current canvas state after the action:"},
#                     {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{canvas_state}"}}
#                 ]
#             ))
            
#             return result
    
    
    
#     # If you want to add custom messages to the memory
#     # memory.chat_memory.add_user_message("Remember to place images carefully.")
#     # memory.chat_memory.add_ai_message("I'll make sure to create a balanced composition.")
    
#     agent_executor = CanvasAwareAgentExecutor(
#         agent=agent, 
#         tools=tools,
#         handle_parsing_errors=True,
#         max_iterations=5,
#         verbose=True,
#         memory=memory
#     )

#     # Get current step from plan
#     step_index = state.get("current_step_index", 0)
#     if step_index >= len(state["plan"].steps):
#         return state  # or handle end of execution
#     current_step = state["plan"].steps[step_index]
    
#     # Execute the current step
#     result = agent_executor.invoke({
#         "input": current_step.step,
#         "image_id": current_step.image_id,
#         "agent_scratchpad": "",
#         "tools": str(tools),
#         "tool_names": ", ".join(t.name for t in tools),
#         "layer_id": state["canvas"].current_layer_id,
#         "canvas_width": IMAGE_WIDTH,
#         "canvas_height": IMAGE_HEIGHT,
#     })

#     # Save memory to logs folder with timestamp
#     os.makedirs("logs", exist_ok=True)
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     with open(f"logs/memory_{timestamp}.txt", "w") as f:
#         f.write(str(memory))
#     # Increment step index
#     state["current_step_index"] += 1
    
 

