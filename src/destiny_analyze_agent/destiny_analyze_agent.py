import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from .tools import think_tool, RAG_Search 
from .prompts import Destiny_Analyze_Prompt
from typing_extensions import Annotated, Literal

load_dotenv()

model = ChatOpenAI(
    model="qwen3.6-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://coding-intl.dashscope.aliyuncs.com/v1",
)

# sub-agent 
# destiny_analyze_agent = {
#     "name": "destiny_analyze_agent",
#     "description": "",
#     "system_prompt": Destiny_Analyze_Prompt,
#     "tools": [think_tool, RAG_Search],
#     "model": model
# }

# Test agnet state
agent = create_agent(
    model=model,
    system_prompt=Destiny_Analyze_Prompt
)

# Run the agent
input = ""

agent.invoke(
    {"messages": [{"role": "user", "content": input}]}
)