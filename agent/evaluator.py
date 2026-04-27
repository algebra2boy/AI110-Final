"""
Agent Step 5 — Arc Evaluator
Self-evaluates the generated playlist for coherence, therapeutic logic, and arc quality.
Returns a confidence score and flags any weak transitions.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from agent.emotion_parser import ParsedEmotion
from agent.playlist_synth import SynthesizedPlaylist
from utils.llm_client import call_claude_json
from utils.logger import AgentStepLogger

SYSTEM_PROMPT = """You are a senior music therapist reviewing a generated emotional arc playlist.
Evaluate the playlist on three dimensions and return a confidence score.

Scoring dimensions (each 0.0-1.0):
1. arc_coherence — Does the mood progression feel smooth and logical?
2. song_fit — Do the chosen songs actually serve their arc step's mood?
3. therapeutic_logic — Does the arc apply the iso principle correctly?

Return ONLY a JSON object:
{
  "arc_coherence": <float>,
  "song_fit": <float>,
  "therapeutic_logic": <float>,
  "overall_confidence": <float — weighted average>,
  "weak_transitions": [<list of step indices (0-based) where the transition feels rough>],
  "evaluator_note": "<one honest sentence about the arc's main strength or weakness>"
}"""


@dataclass
class EvaluationResult:
    arc_coherence: float
    song_fit: float
    therapeutic_logic: float
    overall_confidence: float
    weak_transitions: list[int] = field(default_factory=list)
    evaluator_note: str = ""

    def confidence_label(self) -> str:
        if self.overall_confidence >= 0.85:
            return "Excellent"
        elif self.overall_confidence >= 0.70:
            return "Good"
        elif self.overall_confidence >= 0.55:
            return "Fair"
        else:
            return "Needs Improvement"

    def confidence_color(self) -> str:
        if self.overall_confidence >= 0.85:
            return "#22c55e"
        elif self.overall_confidence >= 0.70:
            return "#84cc16"
        elif self.overall_confidence >= 0.55:
            return "#f59e0b"
        else:
            return "#ef4444"


def evaluate_arc(emotion: ParsedEmotion, playlist: SynthesizedPlaylist) -> EvaluationResult:
    flat = playlist.flat()

    with AgentStepLogger("ArcEvaluator", f"confidence check on {len(flat)} songs"):
        song_summary = [
            {
                "arc_step": s.target_mood,
                "title": s.title,
                "artist": s.artist,
                "mood": s.mood,
                "energy": s.energy,
                "score": s.score,
            }
            for s in flat
        ]

        user_msg = (
            f"User's current mood: {emotion.current_mood} (intensity: {emotion.intensity})\n"
            f"User's target mood: {emotion.target_mood}\n"
            f"Arc designed: {' → '.join(playlist.arc)}\n"
            f"Arc narrative: {playlist.arc_narrative}\n\n"
            f"Playlist:\n{json.dumps(song_summary, indent=2)}"
        )

        raw = call_claude_json(system_prompt=SYSTEM_PROMPT, user_message=user_msg)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            data = json.loads(match.group()) if match else {}

        return EvaluationResult(
            arc_coherence=float(data.get("arc_coherence", 0.7)),
            song_fit=float(data.get("song_fit", 0.7)),
            therapeutic_logic=float(data.get("therapeutic_logic", 0.7)),
            overall_confidence=float(data.get("overall_confidence", 0.7)),
            weak_transitions=data.get("weak_transitions", []),
            evaluator_note=data.get("evaluator_note", ""),
        )
