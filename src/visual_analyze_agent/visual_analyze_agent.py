import os
from dotenv import load_dotenv
from langchain.tools import tool
from .tools import Visual_Structure
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from .prompts import Visual_Analyze_Agent_Prompt
from typing_extensions import Annotated, Literal

load_dotenv()

model = ChatOpenAI(
    model="qwen3.6-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://coding-intl.dashscope.aliyuncs.com/v1",
)

# sub-agent 
# visual_analyze_agent = {
#     "name": "visual_analyze_agent",
#     "description": "",
#     "system_prompt": Visual_Analyze_Agent_Prompt,
#     "tools": [Visual_Structure],
#     "model": model
# }

# Test state
agent = create_agent(
    model=model,
    system_prompt=Visual_Analyze_Agent_Prompt
)

# Run the agent
input = ""

agent.invoke(
    {"messages": [{"role": "user", "content": input}]}
)