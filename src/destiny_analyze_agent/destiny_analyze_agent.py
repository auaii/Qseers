import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from .tools import think_tool, RAG_Search
from .prompts import Destiny_Analyze_Prompt

load_dotenv()

model = ChatOpenAI(
    model="qwen3.6-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://coding-intl.dashscope.aliyuncs.com/v1",
)

destiny_analyze_agent = {
    "name": "destiny_analyze_agent",
    "description": (
        "วิเคราะห์โหง่วเฮ้ง (五行相面) จาก face_features JSON โดยค้นหาความรู้จาก "
        "vector knowledge base และคืนรายงานการวิเคราะห์ดวงชะตาเป็นภาษาไทย"
    ),
    "system_prompt": Destiny_Analyze_Prompt,
    "tools": [think_tool, RAG_Search],
    "model": model,
}

# if __name__ == "__main__":
#     agent = create_agent(
#         model=model,
#         tools=[think_tool, RAG_Search],
#         system_prompt=Destiny_Analyze_Prompt
#     )

#     test_input = """{
#   "face_shape": "oval",
#   "forehead": "wide and high",
#   "eyebrows": "thick and straight",
#   "nose": "broad with rounded tip",
#   "mouth": "full lips, wide",
#   "chin": "rounded",
#   "confidence_score": 0.85
# }"""

#     result = agent.invoke(
#         {"messages": [{"role": "user", "content": test_input}]}
#     )
#     print(result)