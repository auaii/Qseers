"""Visual Analyze Agent Tools — face image analysis via Vision model."""

import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

_VISION_INSTRUCTION = """\
วิเคราะห์ใบหน้าในภาพนี้ตามหลักโหง่วเฮ้ง ตอบเป็น JSON เท่านั้น ไม่มีข้อความอื่น ไม่มี markdown:
{
  "face_shape": "oval|round|square|heart|long",
  "forehead": {"width":"narrow|medium|wide","height":"low|medium|high","prominence":"low|medium|high","note":"..."},
  "eyebrows": {"shape":"straight|arched|curved","thickness":"thin|medium|thick","length":"short|medium|long","symmetry":"low|medium|high","note":"..."},
  "nose": {"height":"low|medium|high","tip":"pointed|rounded|flat","wing_width":"narrow|medium|wide","note":"..."},
  "lips": {"fullness":"thin|medium|full","corners":"downward|neutral|upward","symmetry":"low|medium|high","note":"..."},
  "chin": {"shape":"pointed|rounded|square","prominence":"receding|medium|prominent","width":"narrow|medium|wide","note":"..."},
  "overall_impression": "...",
  "confidence_score": 0.85,
  "issues": []
}"""


@tool(parse_docstring=True)
def analyze_face_image(image_path: str) -> str:
    """Analyze a face image file and return structured face features as JSON.

    Reads the image from disk, sends it to the vision model, and returns
    face feature JSON ready for Wuxing (五行相面) destiny analysis.

    Args:
        image_path: Absolute or relative path to the face image file (jpg/png/webp).

    Returns:
        JSON string with face_shape, forehead, eyebrows, nose, lips, chin, confidence_score.
    """
    path = Path(image_path)
    if not path.exists():
        return f"Error: image file not found at {image_path}"

    suffix = path.suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    mime_type = mime_map.get(suffix, "image/jpeg")

    with open(path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    # resize to 640×480 to reduce payload size
    import cv2
    import numpy as np
    img_array = np.frombuffer(base64.b64decode(image_b64), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is not None:
        img = cv2.resize(img, (640, 480))
        _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        image_b64 = base64.b64encode(buf.tobytes()).decode()
        mime_type = "image/jpeg"

    vision_model = ChatOpenAI(
        model="qwen3.6-plus",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://coding-intl.dashscope.aliyuncs.com/v1",
    )

    response = vision_model.invoke([
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{image_b64}"},
                },
                {"type": "text", "text": _VISION_INSTRUCTION},
            ],
        }
    ])

    return response.content


@tool(parse_docstring=True)
def Visual_Structure(reflection: str) -> str:
    """Record a visual analysis reflection before or after each step.

    Args:
        reflection: Thoughts on the current visual analysis step.

    Returns:
        Confirmation that the reflection was recorded.
    """
    return f"Reflection recorded: {reflection}"
