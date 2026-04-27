"""
Agent Step 2 — Arc Planner
Designs an N-step emotional transition arc using the iso principle from music therapy.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from agent.emotion_parser import ParsedEmotion
from utils.llm_client import call_claude_json
from utils.logger import AgentStepLogger

SYSTEM_PROMPT = """You are a music therapist specializing in emotional arc design.
Your job is to create a step-by-step emotional journey through music using the ISO principle:
- Start where the listener IS emotionally, not where they want to be
- Move gradually, in 3-5 steps, toward the target emotional state
- Each step should feel like a natural progression, not a jarring jump

Valid moods to use in arc steps:
sad, melancholic, nostalgic, anxious, stressed, lonely, grieving, bittersweet,
neutral, content, calm, peaceful, serene, introspective,
hopeful, uplifting, motivated, energetic, happy, euphoric, empowered, focused

Return ONLY a JSON object with this exact schema:
{
  "arc": [<list of 3-5 mood strings>],
  "arc_narrative": "<1-2 sentences describing the emotional journey>",
  "num_songs_per_step": <int, 1 or 2>,
  "transition_rationale": [<one short reason per transition, e.g. "grounding before shift">]
}

Rules:
- arc[0] MUST equal or closely match the current_mood
- arc[-1] MUST equal or closely match the target_mood
- For large gaps (needs_gradual_transition=true), use 5 steps
- For small gaps (needs_gradual_transition=false), use 3 steps
- transition_rationale should have len = len(arc) - 1"""


@dataclass
class EmotionalArc:
    arc: list[str]
    arc_narrative: str
    num_songs_per_step: int
    transition_rationale: list[str]

    def total_songs(self) -> int:
        return len(self.arc) * self.num_songs_per_step


def plan_arc(emotion: ParsedEmotion) -> EmotionalArc:
    with AgentStepLogger("ArcPlanner", emotion.mood_gap()):
        user_msg = (
            f"Current mood: {emotion.current_mood} (intensity: {emotion.intensity})\n"
            f"Target mood: {emotion.target_mood}\n"
            f"Themes: {', '.join(emotion.themes)}\n"
            f"Context: {emotion.context}\n"
            f"Needs gradual transition: {emotion.needs_gradual_transition}"
        )
        raw = call_claude_json(system_prompt=SYSTEM_PROMPT, user_message=user_msg)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            data = json.loads(match.group()) if match else {}

        return EmotionalArc(
            arc=data.get("arc", [emotion.current_mood, emotion.target_mood]),
            arc_narrative=data.get("arc_narrative", ""),
            num_songs_per_step=int(data.get("num_songs_per_step", 1)),
            transition_rationale=data.get("transition_rationale", []),
        )
