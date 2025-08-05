**AI-Powered Multi-Agent Automation for Oracle Fusion Application**

Introduction

Oracle AI Agent Studio is a development platform for Fusion Apps that lets us customize AI agents to automate business needs for ERP , HCM, SCM, and CX
Here we would explore a different approach that helps to interact directly with Oracle Fusion Applications through REST API’s and responds to user queries using intelligent reasoning, context-awareness, and dynamic orchestration between specialized agents like PO Agent, Invoice Agent, etc. This multi-agentic work-around eliminates the dependency of Oracle AI Agent Studio or Oracle Digital Assistant and can be used in general outside of Oracle Cloud Infrastructure for any use case.
AI Agents
AI agents combine large language models (LLMs) with external tools to understand user queries, generate plans, and execute tasks. They process tool outputs, refine their approach, and iterate this process in a loop until achieving the desired result, ensuring efficient and dynamic problem-solving and marking a significant evolution in automation capabilities.
In this solution, we have designed a Purchase Order Agent capable of addressing user queries related to purchase orders and an Invoice Agent to handle questions about invoices. Additionally, we have developed a Supervisor Agent that analyzes incoming user requests and determines the appropriate agent to delegate the task, ensuring efficient and accurate query resolution.
Agent Framework and LLM
This agentic framework leverages LangGraph’s prebuilt agent libraries, which are specifically designed to support multi-agent systems. At the core of this architecture is a Supervisor Agent, responsible for orchestrating the overall workflow and delegating tasks to specialized sub-agents. Each sub-agent is assigned a distinct role or "persona," tailored to a specific task using LangChain’s ChatPromptTemplate. Python functions are exposed as tools for the agents to use. The GPT-4 model powers the reasoning and communication capabilities of the agents.
Purchase Order Agent
The agent begins by executing the generate_purchase_order_filters tool, which takes the user's query as input and utilizes a prompt with the LLM to identify the relevant filters for selecting purchase orders. LLM will extract five predefined filters from the user input and return the results as a JSON schema or Python dictionary containing name-value pairs.
Next, the agent invokes apply_purchase_order_filters to convert the generated filters into a query (q) parameter and defines the desired purchase order fields. It then calls the Purchase Order REST API to fetch the purchase order details. Finally, the agent leverages the LLM to respond to the user query based on the output from the tools.
Invoice Agent
The agent begins by executing the generate_invoice_filters tool, which takes the user's query as input and utilizes a prompt with the LLM to identify the relevant filters for selecting invoice details. LLM will extract five predefined filters from the user input and return the results as a JSON schema or Python dictionary containing name-value pairs.
Next, the agent invokes apply_invoice_filters to convert the generated filters into a query (q) parameter and defines the desired invoice fields. It then calls the Invoice REST API to fetch the invoice details. Finally, the agent leverages the LLM to respond to the user query based on the output from the tools.
Supervisor Agent
The agent is equipped with LLM to execute the handoff execution to either the Purchase Order Agent or the Invoice Agent based on the user's query. The Supervisor Agent identifies the sub agent, and it seamlessly handoff the request to the specific agent to handle the user's query and respond the final output.

How It Works
1.User submits a natural language query. 
2.Supervisor Agent identifies the correct sub-agent (PO, Invoice, etc.).
3.Sub-agent extracts filters using LLM, calls Fusion APIs, and gathers data. 
4.GPT-4 formulates a user-friendly response from API output.
Check-out the code
Langgraph library is used for multi-agentic framework.
https://github.com/shilpidatascientist/Oracle_Fusion_Bot

Key Differentiators
1. No dependency on Oracle’s NLP engine (ODA or Oracle AI Agent Studio)
2. Cloud agnostic, portable python framework.
3. 
Future Enhancement
This can be scaled to many more agents each trained to perform exclusive tasks, like complete purchase order processing including creating, updating, canceling and similarly handling reimbursement etc.

References
[REST API for Oracle Fusion Cloud Procurement - Get all purchase orders](https://docs.oracle.com/en/cloud/saas/procurement/24b/fapra/op-purchaseorders-get.html)
https://docs.oracle.com/en/cloud/saas/financials/24b/farfa/op-invoices-get.html
