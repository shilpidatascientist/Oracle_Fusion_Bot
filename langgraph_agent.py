#from pydantic import BaseModel
from collections import defaultdict
from typing import Literal
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph_purchase_order import *
from langgraph_invoice import *
from langgraph.graph import MessagesState, StateGraph, START,END
from langgraph.types import Command
from langchain.tools import tool
from langgraph.errors import GraphRecursionError
from dotenv import load_dotenv
import os
import requests
import json
import markdown
from requests.auth import HTTPBasicAuth
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
import warnings
warnings.filterwarnings('ignore')
from PIL import Image
import io
from langgraph_supervisor import create_supervisor

# Load environment variables from the .env file
load_dotenv()

# Access environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = os.getenv("model", "gpt-4")

# Initialize the OpenAI LLM using LangChain
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name=model,
    temperature=0
)

checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "2"}}
max_iterations = 3

purchase_order_agent = create_react_agent(
    model=llm,
    tools=purchase_order_tools,
    prompt=purchase_order_prompt,
    checkpointer=checkpointer,
    name="purchase_order_agent"
)

invoice_agent = create_react_agent(
    model=llm,
    tools=invoice_tools,
    prompt=invoice_prompt,
    checkpointer=checkpointer,
    name="invoice_agent"
)

supervisor = create_supervisor(model=llm,
                            agents=[purchase_order_agent, invoice_agent],
                            prompt="""You are a supervisor managing task routing and coordination between agents:
                            - Purchase order agent: Assign purchase order related tasks to this agent.
                            - Invoice agent: Assign invoice related tasks to this agent.
                            Asign work to one agent at a time, do not call agents in parallel. Do not do any work yourself.
                            Aggregate the results from the agents and return them in a single message.""",
                            add_handoff_back_messages = True,
                            output_mode="full_history",
).compile(checkpointer=checkpointer,name="supervisor",)


def plot():
    """Plot the graph."""
    image_bytes = supervisor.get_graph().draw_mermaid_png()
    image = Image.open(io.BytesIO(image_bytes))
    image.show()
"""
from pprint import pprint
final_result = supervisor.invoke(
    {"messages": [("user", "Show me purchase orders.")]},
    config={"recursion_limit": 2 * max_iterations + 1, **config}
)

for m in final_result["messages"]:
    m.pretty_print()
"""