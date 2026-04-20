import os
from typing import Literal
from dotenv import load_dotenv
from prompts import Main_Agent_Prompt
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from src.visual_analyze_agent import visual_analyze_agent
from src.destiny_analyze_agent import destiny_analyze_agent
# formats messages 
from src.utils import show_prompt, format_messages

load_dotenv()
# Antropic 
model = ChatOpenAI(
    model="qwen3.6-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://coding-intl.dashscope.aliyuncs.com/v1",
)

Main_agent = create_deep_agent(
    model=model,
    tools=[
        # call_face_analyzer,   # ส่ง image ไปให้ Sub-Agent 1
        # call_rag_agent,       # ส่ง face_features ไปให้ Sub-Agent 2
        # request_new_image,    # แจ้ง user ถ้ารูปไม่ชัด
        
    ],
    system_prompt=Main_Agent_Prompt,
    subagents=[destiny_analyze_agent, visual_analyze_agent]
)

# Progress 
show_prompt(Main_Agent_Prompt)
messages = Main_agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})
print(format_messages(messages))