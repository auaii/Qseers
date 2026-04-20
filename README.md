# Alibaba Hackathon — Qseer

**Qseer** is a multimodal AI agent system for facial destiny analysis based on traditional Chinese divination (黃局五行相面 / Huang Jui).

## Overview

Given a face image, Qseer extracts facial features and interprets them through the lens of traditional five-element (五行) philosophy, producing a personalized destiny reading across five domains: career, finance, love, destiny, and legacy.

## Architecture

```
User Image
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
- **Knowledge Base**: Traditional divination knowledge (`knowledge.pdf`) via RAG search

## Agents

| Agent | Role |
|-------|------|
| `Main_agent` | Orchestrator — routes image through pipeline, enforces confidence gate (≥ 0.7), synthesizes final report |
| `visual_analyze_agent` | Vision agent — analyzes face structure, returns structured JSON |
| `destiny_analyze_agent` | Knowledge agent — searches RAG, maps features to five fate domains, produces reading |

## Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Add your DASHSCOPE_API_KEY to .env
```

## Tech Stack

- `deepagents` — multi-agent orchestration
- `langchain-openai` — OpenAI-compatible wrapper for Qwen
- `python-dotenv` — environment config
- `rich` — console output formatting
