import os
import sys
import argparse
from pathlib import Path
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
from utils import show_prompt, stream_agent

load_dotenv()

model = ChatOpenAI(
    model="qwen3.6-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://coding-intl.dashscope.aliyuncs.com/v1",
)

Main_agent = create_deep_agent(
    model=model,
    tools=[],
    system_prompt=Main_Agent_Prompt,
    subagents=[destiny_analyze_agent, visual_analyze_agent],
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wuxing face analysis agent")
    parser.add_argument("image", nargs="?", help="Path to face image file")
    parser.add_argument("--text", "-t", help="Text message or face description")
    args = parser.parse_args()

    image_path = None
    text_input = args.text

    if args.image:
        image_path = str(Path(args.image).resolve())
        if not Path(image_path).exists():
            print(f"Error: image file not found: {image_path}")
            sys.exit(1)

    # Interactive mode when no args given
    if not image_path and not text_input:
        print("=== Wuxing Face Analysis ===")
        print("Input modes: image only | text only | image + text")
        img = input("Image path (press Enter to skip): ").strip()
        if img:
            image_path = str(Path(img).resolve())
            if not Path(image_path).exists():
                print(f"Error: image file not found: {image_path}")
                sys.exit(1)
        text_input = input("Text / face description (press Enter to skip): ").strip() or None

        if not image_path and not text_input:
            # NOTE: OpenCV webcam capture disabled — face detection unreliable on macOS.
            # To re-enable in a future version:
            #   from capture import capture_face
            #   image_path = capture_face()
            print("No input provided. Exiting.")
            sys.exit(0)

    # Build user_content from whichever inputs were provided
    parts = []
    if image_path:
        parts.append(f"image_path: {image_path}")
    if text_input:
        parts.append(f"text: {text_input}")
    user_content = "\n".join(parts)

    show_prompt(Main_Agent_Prompt)
    stream_agent(Main_agent, user_content)
