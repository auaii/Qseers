"""Visual_Analyze_Agent

"""
import os
import httpx
from typing import Literal
from dotenv import load_dotenv
from markdownify import markdownify
from langchain_core.tools import tool


load_dotenv()

@tool(parse_docstring=True)
def Visual_Structure(reflection: str) -> str:
    return