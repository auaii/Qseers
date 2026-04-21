"""Webcam face capture — live preview with face detection overlay.

Controls:
  SPACE  — capture current frame and proceed to analysis
  Q      — quit without capturing

macOS note: Grant camera permission to your terminal app at
  System Settings → Privacy & Security → Camera
"""

import sys
import tempfile

import cv2


def _open_camera() -> cv2.VideoCapture:
    """Try multiple backends so macOS permission prompt fires correctly."""
    backends = []
    if sys.platform == "darwin":
        backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_ANY]
    else:
        backends = [cv2.CAP_ANY]

    for backend in backends:
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            # warm-up: let auto-exposure settle (black frames otherwise)
            import time
            time.sleep(1.5)
            for _ in range(20):
                cap.read()
            return cap
        cap.release()

    raise RuntimeError(
        "Cannot open webcam.\n\n"
        "macOS fix:\n"
        "  System Settings → Privacy & Security → Camera\n"
        "  → enable your terminal app (Terminal / iTerm2 / VS Code)\n\n"
        "Then re-run the script."
    )


def capture_face() -> str | None:
    """Open webcam, show live preview, capture on SPACE.

    Returns the path to the saved JPEG, or None if the user quits.
    """
    cap = _open_camera()

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    saved_path: str | None = None

    print("Webcam open — press SPACE to capture, Q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Warning: failed to read frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        display = frame.copy()
        h, w = display.shape[:2]

        for x, y, fw, fh in faces:
            cv2.rectangle(display, (x, y), (x + fw, y + fh), (0, 220, 0), 2)
            cv2.putText(display, "Face detected", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 0), 1)

        status = f"{len(faces)} face(s) detected" if faces else "No face — align camera"
        color = (0, 220, 0) if len(faces) > 0 else (0, 80, 220)
        cv2.putText(display, status, (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(display, "SPACE: capture   Q: quit", (10, h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        cv2.imshow("Wuxing Face Capture", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(" "):
            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            cv2.imwrite(tmp.name, frame)
            saved_path = tmp.name
            print(f"Captured → {saved_path}")
            break
        elif key == ord("q"):
            print("Capture cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return saved_path
