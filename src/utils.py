"""Utility functions for displaying messages and prompts in Jupyter notebooks."""

import json

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console()


def format_message_content(message):
    """Convert message content to displayable string."""
    parts = []
    tool_calls_processed = False

    # Handle main content
    if isinstance(message.content, str):
        parts.append(message.content)
    elif isinstance(message.content, list):
        # Handle complex content like tool calls (Anthropic format)
        for item in message.content:
            if item.get("type") == "text":
                parts.append(item["text"])
            elif item.get("type") == "tool_use":
                parts.append(f"\n🔧 Tool Call: {item['name']}")
                parts.append(f"   Args: {json.dumps(item['input'], indent=2)}")
                parts.append(f"   ID: {item.get('id', 'N/A')}")
                tool_calls_processed = True
    else:
        parts.append(str(message.content))

    # Handle tool calls attached to the message (OpenAI format) - only if not already processed
    if (
        not tool_calls_processed
        and hasattr(message, "tool_calls")
        and message.tool_calls
    ):
        for tool_call in message.tool_calls:
            parts.append(f"\n🔧 Tool Call: {tool_call['name']}")
            parts.append(f"   Args: {json.dumps(tool_call['args'], indent=2)}")
            parts.append(f"   ID: {tool_call['id']}")

    return "\n".join(parts)


def format_messages(messages):
    """Format and display a list of messages with Rich formatting."""
    for m in messages:
        msg_type = m.__class__.__name__.replace("Message", "")
        content = format_message_content(m)

        if msg_type == "Human":
            console.print(Panel(content, title="🧑 Human", border_style="blue"))
        elif msg_type == "Ai":
            console.print(Panel(content, title="🤖 Assistant", border_style="green"))
        elif msg_type == "Tool":
            console.print(Panel(content, title="🔧 Tool Output", border_style="yellow"))
        else:
            console.print(Panel(content, title=f"📝 {msg_type}", border_style="white"))


def format_message(messages):
    """Alias for format_messages for backward compatibility."""
    return format_messages(messages)


def stream_agent(agent, user_content: str):
    """Stream agent execution with real-time Rich display.

    Shows each step as it happens: Human input → AI thinking → Tool calls → Tool output → Final answer.
    """
    from langchain_core.messages import AIMessageChunk, ToolMessage

    console.print(Panel(user_content, title="🧑 Human", border_style="blue"))

    current_text = ""
    live = None
    seen_tool_names: set = set()

    def _close_live():
        nonlocal live, current_text
        if live:
            live.stop()
            live = None
        if current_text:
            console.print(Panel(current_text, title="🤖 Assistant", border_style="green"))
            current_text = ""

    try:
        for chunk, _ in agent.stream(
            {"messages": [{"role": "user", "content": user_content}]},
            stream_mode="messages",
        ):
            # ── Streaming AI text ──────────────────────────────────────────
            if isinstance(chunk, AIMessageChunk):
                if chunk.content:
                    if live is None:
                        live = Live(console=console, refresh_per_second=15)
                        live.start()
                    current_text += chunk.content
                    live.update(
                        Panel(current_text, title="🤖 Assistant", border_style="green")
                    )

                # ── Tool call announced (name arrives in first chunk) ───────
                for tc in chunk.tool_call_chunks or []:
                    if tc.get("name") and tc["name"] not in seen_tool_names:
                        seen_tool_names.add(tc["name"])
                        _close_live()
                        console.print(
                            Panel(
                                f"[bold cyan]{tc['name']}[/bold cyan]",
                                title="📝 AI → Tool Call",
                                border_style="cyan",
                            )
                        )

            # ── Tool output ────────────────────────────────────────────────
            elif isinstance(chunk, ToolMessage):
                _close_live()
                content = chunk.content
                if len(content) > 800:
                    content = content[:800] + "\n[dim]... (truncated)[/dim]"
                console.print(Panel(content, title="🔧 Tool Output", border_style="yellow"))

    finally:
        _close_live()


def show_prompt(prompt_text: str, title: str = "Prompt", border_style: str = "blue"):
    """Display a prompt with rich formatting and XML tag highlighting.

    Args:
        prompt_text: The prompt string to display
        title: Title for the panel (default: "Prompt")
        border_style: Border color style (default: "blue")
    """
    # Create a formatted display of the prompt
    formatted_text = Text(prompt_text)
    formatted_text.highlight_regex(r"<[^>]+>", style="bold blue")  # Highlight XML tags
    formatted_text.highlight_regex(
        r"##[^#\n]+", style="bold magenta"
    )  # Highlight headers
    formatted_text.highlight_regex(
        r"###[^#\n]+", style="bold cyan"
    )  # Highlight sub-headers

    # Display in a panel for better presentation
    console.print(
        Panel(
            formatted_text,
            title=f"[bold green]{title}[/bold green]",
            border_style=border_style,
            padding=(1, 2),
        )
    )