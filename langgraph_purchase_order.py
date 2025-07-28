from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
#from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from dotenv import load_dotenv
import os
import requests
import json
from requests.auth import HTTPBasicAuth
from langgraph.prebuilt import create_react_agent
from requests.auth import HTTPBasicAuth

# Load environment variables from the .env file
load_dotenv()

# Access environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = os.getenv("model", "gpt-4")
username = os.getenv("fa_username")
password = os.getenv("fa_password")
auth = HTTPBasicAuth(username, password)

# Initialize the OpenAI LLM using LangChain
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name=model,
    temperature=0
)

# Define Tool 1
@tool
def generate_purchase_order_filters(user_query: str) -> list:
    """Generate filters based on user query."""
    instruction = """
You are a Purchase Order assistant. Your task is to determine the appropriate filters for purchase orders based on the user's input.

Use only the following filter names:
- OrderNumber
- CurrencyCode
- Supplier
- Buyer
- Status

Return a JSON array like this:
[{"name": "CurrencyCode", "value": "USD"}, {"name": "Status", "value": "Approved"}]

If no filters are found, return a JSON array like this: 
[{'name': 'None', 'value': 'None'}]
"""
    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": user_query}
    ]

    response = llm.invoke(messages)
    try:
        return json.loads(response.content)
    except Exception as e:
        return [{"error": f"Invalid JSON from LLM: {str(e)}", "raw": response.content}]
#print(generate_purchase_order_filters("Show me purchase orders."))

@tool
def apply_purchase_order_filters(filters: list) -> dict:
    """Apply filters to fetch purchase order details."""
    if filters == [{'name': 'None', 'value': 'None'}]:
        return {
            "error": "No filters provided or invalid filters."
        }
    query_parts = []
    for f in filters:
        if f['name'] and f['value'].strip() not in ['None', '', '?']:
            value = f['value'].replace("'", " ").replace(" ", "+")
            query_parts.append(f"{f['name']}='{value}'")

    q_parameter = " and ".join(query_parts)
    fields = "POHeaderId,OrderNumber,Supplier,ProcurementBU,Total,Status,Buyer,CurrencyCode,CreationDate"
    limit = 3

    headers = {"REST-Framework-Version": "2"}

    url = f"https://fa-esfe-dev11-saasfademo1.ds-fa.oraclepdemos.com/fscmRestApi/resources/11.13.18.05/purchaseOrders?q={q_parameter}&fields={fields}&limit={limit}&onlyData=true"
    #print(url)

    #print("Auth type:", type(auth))
    response = requests.get(url, headers=headers, auth=auth, verify = False)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        return {
            "error": "Unauthorized. Please check your authentication credentials.",
            "details": response.text
        }
    else:
        return {
            "error": f"Failed to call API. Status: {response.status_code}",
            "details": response.text
        }

""""
po_input = (apply_purchase_order_filters.invoke({
    "filters": [{"name": "None", "value": "None"}]
}))

print(apply_purchase_order_filters.invoke({
    "filters": [{"name": "Supplier", "value": "Lee Supplies"}]
}))"""

# Define prompt template
purchase_order_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """You are a purchase order agent designed to respond to queries related to purchase orders.Call tools as needed to extract filters and retrieve purchase orders. Always call the tools—never answer directly.

If there are no filters or invalid filters provided by the tool,please ask user:

It would be great if you can provide some more information on either of the below to process your request:
- OrderNumber
- CurrencyCode
- Supplier
- Buyer
- Status

If the user query is specific about a particular filter then please provide that specific information only,in lines."""
    ),
    #MessagesPlaceholder(variable_name="agent_scratchpad"),
    #MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{messages}")    
])

# Register tools
purchase_order_tools = [generate_purchase_order_filters, apply_purchase_order_filters]

"""
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
"""