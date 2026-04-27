"""
Claude API client with prompt caching for all agent calls.
"""

from __future__ import annotations

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def call_claude(
    system_prompt: str,
    user_message: str,
    model: str = "claude-haiku-4-5-20251001",
    max_tokens: int = 1024,
    use_cache: bool = True,
) -> str:
    """
    Call Claude with optional prompt caching on the system prompt.
    Returns the text content of the first response block.
    """
    client = get_client()

    system_content = (
        [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]
        if use_cache
        else system_prompt
    )

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_content,
        messages=[{"role": "user", "content": user_message}],
    )

    return response.content[0].text


def call_claude_json(
    system_prompt: str,
    user_message: str,
    model: str = "claude-haiku-4-5-20251001",
    max_tokens: int = 1024,
) -> str:
    """
    Call Claude expecting a JSON response. Appends JSON-only instruction to the system prompt.
    """
    json_system = (
        system_prompt
        + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown fences, no explanation."
    )
    return call_claude(json_system, user_message, model=model, max_tokens=max_tokens)
