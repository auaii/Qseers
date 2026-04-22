"""Unit tests for Main_agent input parsing and user_content building logic."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Add src paths so imports work without running as __main__
_src = Path(__file__).parent.parent / "src"
_orchestrate = _src / "orchestrate_agent"
sys.path.insert(0, str(_orchestrate))
sys.path.insert(0, str(_src))


# ---------------------------------------------------------------------------
# Helpers — replicate the user_content building logic from Main_agent.py
# ---------------------------------------------------------------------------

def build_user_content(image_path: str | None, text_input: str | None) -> str:
    parts = []
    if image_path:
        parts.append(f"image_path: {image_path}")
    if text_input:
        parts.append(f"text: {text_input}")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Tests: user_content building
# ---------------------------------------------------------------------------

class TestBuildUserContent:
    def test_image_only(self):
        result = build_user_content("/tmp/face.jpg", None)
        assert result == "image_path: /tmp/face.jpg"
        assert "text:" not in result

    def test_text_only(self):
        result = build_user_content(None, "ใบหน้ารูปไข่ หน้าผากกว้าง")
        assert result == "text: ใบหน้ารูปไข่ หน้าผากกว้าง"
        assert "image_path:" not in result

    def test_image_and_text(self):
        result = build_user_content("/tmp/face.jpg", "คิ้วหนาตรง")
        assert "image_path: /tmp/face.jpg" in result
        assert "text: คิ้วหนาตรง" in result
        # image_path line should come first
        assert result.index("image_path:") < result.index("text:")

    def test_both_none_returns_empty(self):
        result = build_user_content(None, None)
        assert result == ""


# ---------------------------------------------------------------------------
# Tests: argument parsing (argparse)
# ---------------------------------------------------------------------------

class TestArgParsing:
    def _parse(self, argv):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("image", nargs="?")
        parser.add_argument("--text", "-t")
        return parser.parse_args(argv)

    def test_image_arg_only(self):
        args = self._parse(["/tmp/face.jpg"])
        assert args.image == "/tmp/face.jpg"
        assert args.text is None

    def test_text_flag_only(self):
        args = self._parse(["--text", "ใบหน้ากลม"])
        assert args.image is None
        assert args.text == "ใบหน้ากลม"

    def test_short_text_flag(self):
        args = self._parse(["-t", "ใบหน้ากลม"])
        assert args.text == "ใบหน้ากลม"

    def test_image_and_text(self):
        args = self._parse(["/tmp/face.jpg", "--text", "คิ้วหนา"])
        assert args.image == "/tmp/face.jpg"
        assert args.text == "คิ้วหนา"

    def test_no_args(self):
        args = self._parse([])
        assert args.image is None
        assert args.text is None


# ---------------------------------------------------------------------------
# Tests: image file validation
# ---------------------------------------------------------------------------

class TestImageValidation:
    def test_valid_image_path_resolves(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
            resolved = str(Path(f.name).resolve())
            assert Path(resolved).exists()

    def test_missing_image_path_detected(self):
        fake = "/tmp/does_not_exist_12345.jpg"
        assert not Path(fake).exists()

    def test_image_path_is_resolved_to_absolute(self):
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            resolved = str(Path(f.name).resolve())
            assert Path(resolved).is_absolute()


# ---------------------------------------------------------------------------
# Tests: Main_agent module-level objects can be imported and have correct shape
# ---------------------------------------------------------------------------

class TestMainAgentModule:
    def test_prompt_imported(self):
        from prompts import Main_Agent_Prompt
        assert isinstance(Main_Agent_Prompt, str)
        assert len(Main_Agent_Prompt) > 0

    def test_prompt_covers_image_mode(self):
        from prompts import Main_Agent_Prompt
        assert "image_path" in Main_Agent_Prompt

    def test_prompt_covers_text_only_mode(self):
        from prompts import Main_Agent_Prompt
        assert "text" in Main_Agent_Prompt.lower()

    def test_prompt_covers_confidence_gate(self):
        from prompts import Main_Agent_Prompt
        assert "confidence_score" in Main_Agent_Prompt or "0.7" in Main_Agent_Prompt

    def test_prompt_covers_both_subagents(self):
        from prompts import Main_Agent_Prompt
        assert "visual_analyze_agent" in Main_Agent_Prompt
        assert "destiny_analyze_agent" in Main_Agent_Prompt

    def test_main_agent_object_exists(self):
        # Patch heavy dependencies so import doesn't call the network
        with patch("langchain_openai.ChatOpenAI"), \
             patch("deepagents.create_deep_agent") as mock_create:
            mock_create.return_value = MagicMock()
            # Re-import with mocks active
            import importlib
            import orchestrate_agent.Main_agent as ma
            # Just verify the module-level agent attribute is present
            assert hasattr(ma, "Main_agent")


# ---------------------------------------------------------------------------
# Tests: interactive-mode guard — no image + no text → empty content
# ---------------------------------------------------------------------------

class TestInteractiveModeGuard:
    def test_no_input_produces_empty_content(self):
        content = build_user_content(None, None)
        assert content == ""

    def test_empty_string_text_treated_as_none(self):
        # strip() + "or None" pattern used in Main_agent.py
        raw = "   "
        text_input = raw.strip() or None
        content = build_user_content(None, text_input)
        assert content == ""
