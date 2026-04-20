import os
from dotenv import load_dotenv
from typing import Literal
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
# from .prompts import Main_Agent_Prompt

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
        call_face_analyzer,   # ส่ง image ไปให้ Sub-Agent 1
        call_rag_agent,       # ส่ง face_features ไปให้ Sub-Agent 2
        request_new_image,    # แจ้ง user ถ้ารูปไม่ชัด
    ],
    system_prompt=Main_Agent_Prompt,
)


# Langchain => DeepAgent 