"""
Agent Step 1 — Emotion Parser
Converts free-text emotional description into structured mood data using Claude.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from utils.llm_client import call_claude_json
from utils.logger import AgentStepLogger

SYSTEM_PROMPT = """You are an expert emotional intelligence analyst.
Your job is to parse natural language descriptions of emotional states into structured data.

Valid moods (choose the closest match):
sad, melancholic, nostalgic, anxious, stressed, lonely, grieving, bittersweet,
neutral, content, calm, peaceful, serene, introspective,
hopeful, uplifting, motivated, energetic, happy, euphoric, empowered, focused

Return ONLY a JSON object with this exact schema:
{
  "current_mood": "<mood from the list>",
  "target_mood": "<mood from the list — where the user wants to be>",
  "intensity": <float 0.0-1.0 — how intense the emotion is>,
  "themes": [<list of 2-4 keywords describing emotional context>],
  "context": "<one sentence summary of what the user is experiencing>",
  "needs_gradual_transition": <true if the emotional gap is large, false if small>
}

Rules:
- If the user doesn't state a target mood, infer a reasonable positive goal (e.g., "calm", "hopeful", "content")
- intensity 1.0 = overwhelming, 0.0 = barely there
- themes should be descriptive: e.g. ["heartbreak", "longing", "loss"] or ["burnout", "overwhelm", "pressure"]
- needs_gradual_transition = true when current and target are very different (e.g. sad→euphoric)"""


@dataclass
class ParsedEmotion:
    current_mood: str
    target_mood: str
    intensity: float
    themes: list[str]
    context: str
    needs_gradual_transition: bool

    def mood_gap(self) -> str:
        return f"{self.current_mood} → {self.target_mood}"


def parse_emotion(user_input: str) -> ParsedEmotion:
    with AgentStepLogger("EmotionParser", user_input[:60]):
        raw = call_claude_json(
            system_prompt=SYSTEM_PROMPT,
            user_message=f"Parse this emotional state: {user_input}",
        )
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback if model returns markdown fences despite instruction
            import re
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                raise ValueError(f"Could not parse JSON from emotion parser: {raw[:200]}")

        return ParsedEmotion(
            current_mood=data.get("current_mood", "neutral"),
            target_mood=data.get("target_mood", "content"),
            intensity=float(data.get("intensity", 0.5)),
            themes=data.get("themes", []),
            context=data.get("context", ""),
            needs_gradual_transition=bool(data.get("needs_gradual_transition", True)),
        )
