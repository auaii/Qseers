"""
Core Face Structure Analyzer
Uses Qwen VLM via Alibaba Cloud DashScope (OpenAI-compatible).
"""
from __future__ import annotations

import base64
import os
import time
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

try:
    from .prompts import Visual_Analyze_Agent_Prompt, USER_PROMPT
except ImportError:
    from prompts import Visual_Analyze_Agent_Prompt, USER_PROMPT

load_dotenv()

_MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}


@dataclass
class AnalysisResult:
    image_path: Path
    model: str
    elapsed_sec: float
    prompt_tokens: int | None
    response_tokens: int | None
    content: str


class SinSaeAnalyzer:
    def __init__(
        self,
        model: str = "qwen3.6-plusg",
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model = model
        self._llm = ChatOpenAI(
            model=model,
            api_key=api_key or os.getenv("DASHSCOPE_API_KEY"),
            base_url=base_url or "https://coding-intl.dashscope.aliyuncs.com/v1",
        )

    def _ensure_image(self, image_path: Path) -> Path:
        path = Path(image_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        if path.suffix.lower() not in _MIME_MAP:
            raise ValueError(f"Unsupported image format: {path.suffix}")
        return path

    def _build_messages(self, path: Path) -> list:
        b64 = base64.b64encode(path.read_bytes()).decode()
        mime = _MIME_MAP[path.suffix.lower()]
        return [
            SystemMessage(content=Visual_Analyze_Agent_Prompt),
            HumanMessage(content=[
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                {"type": "text", "text": USER_PROMPT},
            ]),
        ]

    def analyze(self, image_path: str | Path, temperature: float = 0.4) -> AnalysisResult:
        path = self._ensure_image(Path(image_path))
        messages = self._build_messages(path)

        t0 = time.perf_counter()
        response = self._llm.invoke(messages, temperature=temperature)
        elapsed = time.perf_counter() - t0

        usage = response.usage_metadata or {}
        return AnalysisResult(
            image_path=path,
            model=self.model,
            elapsed_sec=elapsed,
            prompt_tokens=usage.get("input_tokens"),
            response_tokens=usage.get("output_tokens"),
            content=response.content,
        )

    def analyze_stream(self, image_path: str | Path, temperature: float = 0.4):
        """Yield content chunks as they arrive."""
        path = self._ensure_image(Path(image_path))
        messages = self._build_messages(path)

        for chunk in self._llm.stream(messages, temperature=temperature):
            if chunk.content:
                yield chunk.content


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze a single face image")
    parser.add_argument("image", help="Path to the image file")
    args = parser.parse_args()

    analyzer = SinSaeAnalyzer()
    result = analyzer.analyze(args.image)
    print(f"Model  : {result.model}")
    print(f"Elapsed: {result.elapsed_sec:.1f}s")
    print(f"Tokens : {result.prompt_tokens} in / {result.response_tokens} out")
    print("\n--- Result ---")
    print(result.content)
