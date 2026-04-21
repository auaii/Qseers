import os
from dotenv import load_dotenv
from .tools import Visual_Structure, analyze_face_image
from langchain_openai import ChatOpenAI
from .prompts import Visual_Analyze_Agent_Prompt

load_dotenv()

model = ChatOpenAI(
    model="qwen3.6-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://coding-intl.dashscope.aliyuncs.com/v1",
)

visual_analyze_agent = {
    "name": "visual_analyze_agent",
    "description": (
        "วิเคราะห์ใบหน้าจากไฟล์รูปภาพ โดยรับ image_path แล้วคืน face_features JSON "
        "ที่มี face_shape, forehead, eyebrows, nose, lips, chin, confidence_score"
    ),
    "system_prompt": Visual_Analyze_Agent_Prompt,
    "tools": [analyze_face_image, Visual_Structure],
    "model": model,
}