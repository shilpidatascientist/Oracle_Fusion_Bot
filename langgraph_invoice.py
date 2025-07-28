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
def generate_invoice_filters(user_query: str) -> list:
    """Generate filters based on user query."""
    instruction = """
You are a Invoice query assistant. Your task is to determine the appropriate filters for invoices based on the user's input.

Use only the following filter names:
- InvoiceId
- BusinessUnit
- Supplier
- SupplierSite
- InvoiceNumber
- InvoiceAmount
- InvoiceCurrency
- InvoiceDate
- PayGroup

Return a JSON array like this:
[{"name": "InvoiceCurrency", "value": "USD"}, {"name": "InvoiceDate", "value": "2012-01-21"}]

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
    

@tool
def apply_invoice_filters(filters: list) -> dict:
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
    fields = "InvoiceId,BusinessUnit,Supplier,SupplierSite,InvoiceNumber,InvoiceAmount,InvoiceCurrency,InvoiceDate,PayGroup"
    
    headers = {"REST-Framework-Version": "2"}

    url = f"https://fa-esfe-dev11-saasfademo1.ds-fa.oraclepdemos.com/fscmRestApi/resources/11.13.18.05/invoices?q={q_parameter}&fields={fields}&onlyData=true"
    #print(url)

    response = requests.get(url, headers=headers, auth=auth, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Failed to call API. Status: {response.status_code}",
            "details": response.text
        }

"""
print(apply_invoice_filters.invoke({
    "filters": [{"name": "None", "value": "None"}]
}))"""

# Define prompt template
invoice_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """You are an invoice agent designed to respond to queries related to invoices.Call tools as needed to extract filters and retrieve invoices. Always call the tools—never answer directly.

If there are no filters or invalid filters provided by the tool,please ask user:

It would be great if you can provide some more information on either of the below to process your request:
- InvoiceId
- BusinessUnit
- Supplier
- SupplierSite
- InvoiceNumber
- InvoiceAmount
- InvoiceCurrency
- InvoiceDate
- PayGroup

If the user query is specific about a particular filter then please provide that specific information only,in lines."""
    ),
    #MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{messages}"),
    #MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Register tools
invoice_tools = [generate_invoice_filters, apply_invoice_filters]

