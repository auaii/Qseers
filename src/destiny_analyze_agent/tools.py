"""Testing Destiny Analyze Tools.

This module provides external search and strategic planning utilities 
for the Testing Protocol Agent, using Tavily for external context discovery
and internal reflection for quality assurance planning.
"""
import os
import httpx
from typing import Literal
from dotenv import load_dotenv
from markdownify import markdownify
from langchain_core.tools import tool


load_dotenv()

@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on testing protocol design and decision-making.

    Use this tool after each step (e.g., after finding IPC standards or searching external context) 
    to analyze findings, assess gaps, and plan the next mandatory testing steps systematically.
    This ensures quality and completeness in the final testing protocol.

    Reflection should address:
    1. Analysis of current findings - What mandatory standards (IPC) or external best practices have I gathered?
    2. Gap assessment - What crucial testing steps or compliance checks are still missing?
    3. Quality evaluation - Is the current protocol robust enough for the PCB class?
    4. Strategic decision - Should I use RAG, use external search, or finalize the protocol?

    Args:
        reflection: Your detailed reflection on protocol progress, findings, gaps, and next steps

    Returns:
        Confirmation that reflection was recorded for strategic decision-making
    """
    return f"Reflection recorded for Protocol Agent: {reflection}"


@tool(parse_docstring=True)
def RAG_Search():
    return