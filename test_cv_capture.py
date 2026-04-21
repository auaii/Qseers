"""Test: webcam auto-capture (3-second countdown) → Main_agent pipeline.

Usage:
    uv run python test_cv_capture.py               # webcam capture
    uv run python test_cv_capture.py image.jpg     # use existing image

macOS fix if camera is blocked:
    System Settings → Privacy & Security → Camera → enable your terminal app

NOTE: Must be run directly in a terminal (not as a background process).
      The webcam requires a GUI display and camera permission.
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# src packages
_src = Path(__file__).parent / "src"
sys.path.insert(0, str(_src))
sys.path.insert(0, str(_src / "orchestrate_agent"))

import cv2


def capture_with_countdown(countdown_secs: int = 3) -> str | None:
    # --- open camera (tries AVFoundation first on macOS) ---
    backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_ANY] if sys.platform == "darwin" else [cv2.CAP_ANY]
    cap = None
    for backend in backends:
        c = cv2.VideoCapture(0, backend)
        if c.isOpened():
            cap = c
            break
        c.release()

    if cap is None:
        print(
            "\nERROR: Cannot open webcam.\n"
            "macOS fix:\n"
            "  System Settings → Privacy & Security → Camera\n"
            "  → enable your terminal app, then re-run.\n"
        )
        return None

    # warm-up frames
    for _ in range(5):
        cap.read()

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    print(f"Webcam open — auto-capturing in {countdown_secs} seconds. Press Q to quit.")
    start = time.time()
    saved_path = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        elapsed = time.time() - start
        remaining = max(0, countdown_secs - int(elapsed))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        display = frame.copy()
        h, w = display.shape[:2]

        for x, y, fw, fh in faces:
            cv2.rectangle(display, (x, y), (x + fw, y + fh), (0, 220, 0), 2)

        # face status
        status = f"{len(faces)} face(s)" if len(faces) > 0 else "No face — align camera"
        cv2.putText(display, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 220, 0) if len(faces) > 0 else (0, 80, 220), 2)

        # countdown or "Capturing..."
        if remaining > 0:
            label = str(remaining)
            fs = 5.0
            thick = 8
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, fs, thick)
            cv2.putText(display, label, ((w - tw) // 2, (h + th) // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, fs, (0, 220, 255), thick)
        else:
            cv2.putText(display, "Capturing...", (w // 2 - 140, h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 0), 3)

        cv2.putText(display, "Q: quit", (10, h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

        cv2.imshow("Wuxing — Face Capture", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print("Cancelled.")
            break

        if elapsed >= countdown_secs:
            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            cv2.imwrite(tmp.name, frame)
            saved_path = tmp.name
            print(f"Captured → {saved_path}")
            cv2.waitKey(600)
            break

    cap.release()
    cv2.destroyAllWindows()
    return saved_path


def run_agent(image_path: str):
    from prompts import Main_Agent_Prompt
    from langchain_openai import ChatOpenAI
    from deepagents import create_deep_agent
    from visual_analyze_agent import visual_analyze_agent
    from destiny_analyze_agent import destiny_analyze_agent
    from utils import show_prompt, stream_agent
    from dotenv import load_dotenv

    load_dotenv()

    model = ChatOpenAI(
        model="qwen3.6-plus",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://coding-intl.dashscope.aliyuncs.com/v1",
    )

    agent = create_deep_agent(
        model=model,
        tools=[],
        system_prompt=Main_Agent_Prompt,
        subagents=[destiny_analyze_agent, visual_analyze_agent],
    )

    show_prompt(Main_Agent_Prompt)
    stream_agent(agent, image_path)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        # Use provided image — skip webcam
        image_path = str(Path(sys.argv[1]).resolve())
        if not Path(image_path).exists():
            print(f"Error: file not found: {image_path}")
            sys.exit(1)
        print(f"Using image: {image_path}")
    else:
        # Webcam capture
        image_path = capture_with_countdown(countdown_secs=3)

    if image_path:
        run_agent(image_path)
