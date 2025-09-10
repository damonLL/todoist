#!/usr/bin/env python3
"""
Barcelona Trip Planning Workflow using Todoist Toolkit

This script demonstrates how to use the Todoist toolkit with LangGraph to create
a project and tasks for planning a family trip to Barcelona.

Required environment variables:
- ARCADE_API_KEY: Your Arcade.dev API key
- OPENAI_API_KEY: Your OpenAI API key  
- TODOIST_API_TOKEN: Your Todoist API token
- ARCADE_USER_ID: Your Arcade.dev user ID

Usage:
    python project_workflow.py

"""

import os

from langchain_arcade import ArcadeToolManager
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# 1) Set API keys (place your real keys in env variables)
arcade_api_key = os.environ.get("ARCADE_API_KEY", "YOUR_ARCADE_API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
todoist_api_token = os.environ.get("TODOIST_API_TOKEN", "YOUR_TODOIST_API_TOKEN")

# Validate required API keys
if arcade_api_key == "YOUR_ARCADE_API_KEY":
    print("ERROR: Please set ARCADE_API_KEY environment variable")
    exit(1)
if openai_api_key == "YOUR_OPENAI_API_KEY":
    print("ERROR: Please set OPENAI_API_KEY environment variable")
    exit(1)
if todoist_api_token == "YOUR_TODOIST_API_TOKEN":
    print("ERROR: Please set TODOIST_API_TOKEN environment variable")
    exit(1)

# 2) Create a ArcadeToolManager and fetch/add tools/toolkits
manager = ArcadeToolManager(api_key=arcade_api_key)

# Initialize the Todoist toolkit
manager.init_tools(toolkits=["todoist"])
print("Available Todoist tools:", manager.tools)

# 3) Get StructuredTool objects for langchain
lc_tools = manager.get_tools(toolkits=["todoist"])

# 4) Create a ChatOpenAI model and bind the Arcade tools.
model = ChatOpenAI(model="gpt-4o", api_key=openai_api_key)
bound_model = model.bind_tools(lc_tools)

# 5) Use MemorySaver for checkpointing.
memory = MemorySaver()

# 6) Create a ReAct-style agent from the prebuilt function.
graph = create_react_agent(model=bound_model, tools=lc_tools, checkpointer=memory)

# 7) Provide basic config and a user query.
# Note: user_id is required for the tool to be authorized
user_id = os.environ.get("ARCADE_USER_ID", "user@example.com")
config = {"configurable": {"thread_id": "1", "user_id": user_id}}

print("\nYou will be prompted for a project request. Feel free to make one up, or use the following example:")
print("\nI need a project and some tasks to manage my upcoming trip to Barcelona with my family in 6 weeks.\n")
# prompt user for a project request
project_request = input("What project-related prompt do you have? ")

# Add system message to guide date handling
system_message = """You are a helpful assistant for creating Todoist projects and tasks. 

IMPORTANT DATE GUIDELINES:
- Always use relative date expressions (e.g., "next month", "in 2 weeks", "tomorrow") instead of specific dates with years
- When users mention "next month", "in December", etc., use those exact relative expressions
- Do NOT use specific dates with years (e.g., avoid "November 15th, 2023" or "December 1st, 2024")
- Ensure you understand the current date context, so if it is September then "next month" means October 2025
- Use natural language date expressions that Todoist can parse correctly

When creating tasks, use due_string parameters with relative dates like:
- "next month" for tasks due next month
- "in 2 weeks" for tasks due in two weeks  
- "tomorrow" for tasks due tomorrow
- "next week" for tasks due next week
- "in December" for tasks due in December (current year)

Due dates and ordering:
- When using due_string parameters, assign an "order" parameter to the tasks based on when it is due. For instance, if task A is due in 2 weeks and task B is due in 1 week, then task B should have an order of 1 and task A should have an order of 2.
- You should work backwards if given a due date. Base the due dates and order on the complexity of the task and provide a reasonable time if possible between tasks.

This ensures dates are always current and relevant."""

user_input = {
    "messages": [
        ("system", system_message),
        ("user", project_request)
    ]
}

print("Starting project and tasks workflow...")
print("=" * 50)

# 8) Stream the agent's output. If the tool is unauthorized, it may trigger interrupts
for chunk in graph.stream(user_input, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

# 9) Check for interrupts in state
current_state = graph.get_state(config)
if current_state.tasks:
    for task in current_state.tasks:
        if hasattr(task, "interrupts"):
            for interrupt in task.interrupts:
                print(f"Interrupt: {interrupt.value}")
                print("Please follow the authorization link to continue...")

print("=" * 50)
print("Workflow complete.")