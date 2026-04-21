import os
import sys
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv

# Allow running as a script: add src/orchestrate_agent and src to sys.path
_here = Path(__file__).parent
sys.path.insert(0, str(_here))          # for: prompts
sys.path.insert(0, str(_here.parent))   # for: visual_analyze_agent, destiny_analyze_agent, utils

from prompts import Main_Agent_Prompt
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from visual_analyze_agent import visual_analyze_agent
from destiny_analyze_agent import destiny_analyze_agent
# formats messages 
from utils import show_prompt, stream_agent

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

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        # Image path provided directly
        image_path = str(Path(sys.argv[1]).resolve())
        if not Path(image_path).exists():
            print(f"Error: image file not found: {image_path}")
            sys.exit(1)
    else:
        # No argument — open webcam capture
        from capture import capture_face
        image_path = capture_face()
        if not image_path:
            sys.exit(0)

    show_prompt(Main_Agent_Prompt)
    stream_agent(Main_agent, image_path)