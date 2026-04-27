"""
Gemini API client for all agent calls.
"""

from __future__ import annotations

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_configured = False


def is_demo_mode() -> bool:
    return not bool(os.getenv("GEMINI_API_KEY", "").strip())


def _ensure_configured() -> None:
    global _configured
    if not _configured:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY not set. Copy .env.example to .env and add your key."
            )
        genai.configure(api_key=api_key)
        _configured = True


def call_claude(
    system_prompt: str,
    user_message: str,
    model: str = "gemini-1.5-flash",
    max_tokens: int = 1024,
    use_cache: bool = True,
) -> str:
    """
    Call Gemini with a system prompt and user message.
    Signature kept compatible with agent code that calls call_claude().
    """
    _ensure_configured()
    m = genai.GenerativeModel(
        model_name=model,
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(max_output_tokens=max_tokens),
    )
    response = m.generate_content(user_message)
    return response.text


def call_claude_json(
    system_prompt: str,
    user_message: str,
    model: str = "gemini-1.5-flash",
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
