"""
Gemini API client for all agent calls (uses google-genai SDK).
"""

from __future__ import annotations

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

_client: genai.Client | None = None


def is_demo_mode() -> bool:
    return not bool(os.getenv("GEMINI_API_KEY", "").strip())


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY not set. Copy .env.example to .env and add your key."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def call_claude(
    system_prompt: str,
    user_message: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
    use_cache: bool = True,
) -> str:
    """
    Call Gemini with a system prompt and user message.
    Signature kept compatible with agent code that calls call_claude().
    """
    client = get_client()
    response = client.models.generate_content(
        model=model,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text


def call_claude_json(
    system_prompt: str,
    user_message: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
) -> str:
    """
    Call Gemini expecting a JSON response.
    """
    json_system = (
        system_prompt
        + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown fences, no explanation."
    )
    return call_claude(json_system, user_message, model=model, max_tokens=max_tokens)
