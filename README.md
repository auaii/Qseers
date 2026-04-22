# Alibaba Hackathon — Qseer

**Qseer** is a multimodal AI agent system for facial destiny analysis based on traditional Chinese divination (黃局五行相面 / Huang Jui).

## Overview

Given a face image or text description, Qseer extracts facial features and interprets them through the lens of traditional five-element (五行) philosophy, producing a personalized destiny reading across five domains: career, finance, love, destiny, and legacy.

## Architecture

```
User Input (image / text / both)
    ↓
Main Orchestrator Agent
    ├── Visual Analyze Agent  →  Extracts 6 facial dimensions (face shape, forehead,
    │                            eyebrows, nose, lips, chin) with confidence scoring
    └── Destiny Analyze Agent →  Maps features to fate domains via RAG knowledge base,
                                 returns Thai-language markdown report
```

- **Framework**: `deepagents` for hierarchical multi-agent orchestration
- **Model**: Alibaba Qwen3.6-plus via DashScope (multimodal vision + text)
- **Language**: Output in Thai (ภาษาไทย)
- **Knowledge Base**: Traditional divination knowledge (`Knowledge.pdf`) via ChromaDB RAG

## Project Structure

```
Alibaba_Hackathon/
├── web/
│   └── app.py                        # Streamlit web UI (modernized, streaming)
│
├── src/
│   ├── orchestrate_agent/
│   │   ├── Main_agent.py             # Orchestrator — entry point (CLI + agent object)
│   │   └── prompts.py                # Main agent system prompt
│   │
│   ├── visual_analyze_agent/
│   │   ├── visual_analyze_agent.py   # Agent definition
│   │   ├── tools.py                  # analyze_face_image, Visual_Structure tools
│   │   └── prompts.py
│   │
│   ├── destiny_analyze_agent/
│   │   ├── destiny_analyze_agent.py  # Agent definition
│   │   ├── tools.py                  # RAG_Search, think_tool
│   │   └── prompts.py
│   │
│   ├── capture.py                    # OpenCV webcam capture (disabled, future version)
│   └── utils.py                      # Rich streaming console helpers
│
├── tests/
│   └── test_main_agent.py            # Unit tests for Main_agent (20 tests)
│
├── chroma_db/                        # ChromaDB vector store (knowledge embeddings)
├── Knowledge.pdf                     # Wuxing face-reading knowledge source
├── pyproject.toml
└── requirements.txt
```

## Agents

| Agent | Role |
|---|---|
| `Main_agent` | Orchestrator — routes input through pipeline, enforces confidence gate (≥ 0.7), synthesizes final report |
| `visual_analyze_agent` | Vision agent — analyzes face image, returns structured JSON with 6 facial dimensions |
| `destiny_analyze_agent` | Knowledge agent — searches RAG, maps features to five fate domains, produces Thai reading |

## Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Add your DASHSCOPE_API_KEY to .env
```

> **First run will download the HuggingFace embedding model** (~120 MB) for the RAG knowledge base. This happens once and is cached automatically.

## Run

### Web UI (recommended)

```bash
uv run streamlit run web/app.py
```

Opens at **http://localhost:8501**

The web app supports all three input modes with live streaming:

| Mode | How to use |
|---|---|
| Image only | Upload a face photo → click **✨ Analyze Destiny** |
| Text only | Describe facial features in the text box → click **✨ Analyze Destiny** |
| Image + Text | Upload a photo and add context in the text box |

**What you see while it runs:**
- **Agent Pipeline** panel — opens automatically and streams each tool call (🔍 Visual Analysis → 📚 Knowledge Search → 🧠 Reasoning) as cards in real time. Collapses with ✅ when done.
- **Destiny Reading** panel — streams the final Thai analysis character-by-character below the pipeline.

> Agents and the HuggingFace embedding model are loaded once on first run and cached for the entire session — no reload between analyses.

---

### CLI

```bash
# Image only
uv run python src/orchestrate_agent/Main_agent.py /path/to/face.jpg

# Text only — skips visual analysis, goes straight to destiny reading
uv run python src/orchestrate_agent/Main_agent.py --text "ใบหน้ารูปไข่ หน้าผากกว้าง จมูกโด่ง"

# Image + text
uv run python src/orchestrate_agent/Main_agent.py /path/to/face.jpg --text "คิ้วหนาตรง"

# Interactive — prompts you for image path and/or text
uv run python src/orchestrate_agent/Main_agent.py
```

> **Note:** Webcam capture via OpenCV (`capture.py`) is currently disabled due to face detection reliability issues on macOS. It is preserved for re-enablement in a future version.

## Tests

```bash
uv run pytest tests/ -v
# 20 tests — covers input parsing, arg handling, image validation, prompt integrity
```

## Tech Stack

| Package | Purpose |
|---|---|
| `deepagents` | Multi-agent orchestration |
| `langchain-openai` | OpenAI-compatible wrapper for Qwen |
| `langchain-chroma` | ChromaDB vector store integration |
| `langchain-huggingface` | Sentence embedding for RAG |
| `streamlit` | Web UI |
| `python-dotenv` | Environment config |
| `rich` | CLI streaming output |
| `opencv-python` | Webcam capture (future) |
