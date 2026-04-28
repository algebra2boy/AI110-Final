"""
Agent Step 4 — Playlist Synthesizer
Generates personalized explanations for each song choice using Gemini.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from agent.emotion_parser import ParsedEmotion
from agent.arc_planner import EmotionalArc
from agent.music_retriever import RetrievalResult, SongSelection
from utils.llm_client import call_claude_json
from utils.logger import AgentStepLogger

SYSTEM_PROMPT = """You are a compassionate music therapist writing personalized playlist notes.
For each song in the journey, write a brief but deeply personal explanation:
- Why this song belongs at THIS moment in the emotional arc
- What the listener might feel or experience
- A specific musical element (rhythm, key, lyrics, texture) that serves the therapeutic goal

Tone: warm, direct, second-person ("you"), never clinical.
Length: 1-2 sentences per song. No fluff.

Return ONLY a JSON array of objects, one per song, in the same order as the input:
[
  {
    "song_id": "<id>",
    "personal_note": "<1-2 sentence personalized explanation>",
    "why_now": "<one phrase: why this song belongs at this arc step>"
  }
]"""


@dataclass
class AnnotatedSong:
    song: dict
    score: float
    target_mood: str
    psychology_snippet: str
    step_index: int
    personal_note: str
    why_now: str
    spotify_url: str

    @property
    def title(self) -> str:
        return self.song["title"]

    @property
    def artist(self) -> str:
        return self.song["artist"]

    @property
    def mood(self) -> str:
        return self.song["mood"]

    @property
    def energy(self) -> float:
        return self.song["energy"]


@dataclass
class SynthesizedPlaylist:
    arc: list[str]
    steps: list[list[AnnotatedSong]]
    arc_narrative: str

    def flat(self) -> list[AnnotatedSong]:
        return [s for step in self.steps for s in step]

    def total_songs(self) -> int:
        return sum(len(step) for step in self.steps)


def synthesize_playlist(
    emotion: ParsedEmotion,
    arc_plan: EmotionalArc,
    retrieval: RetrievalResult,
) -> SynthesizedPlaylist:
    flat = retrieval.flat_playlist()

    with AgentStepLogger("PlaylistSynth", f"{len(flat)} songs"):
        song_list = [
            {
                "song_id": sel.song["id"],
                "title": sel.song["title"],
                "artist": sel.song["artist"],
                "mood": sel.song["mood"],
                "energy": sel.song["energy"],
                "arc_step": sel.target_mood,
                "psychology_context": (
                    sel.psychology_snippet[:200] if sel.psychology_snippet else ""
                ),
            }
            for sel in flat
        ]

        user_msg = (
            f"User's emotional journey: {emotion.context}\n"
            f"Arc: {' → '.join(arc_plan.arc)}\n\n"
            f"Songs to annotate:\n{json.dumps(song_list, indent=2)}"
        )

        raw = call_claude_json(
            system_prompt=SYSTEM_PROMPT, user_message=user_msg, max_tokens=2048
        )

        try:
            annotations = json.loads(raw)
        except json.JSONDecodeError:
            import re

            match = re.search(r"\[.*\]", raw, re.DOTALL)
            annotations = json.loads(match.group()) if match else []

        annotation_map = {a["song_id"]: a for a in annotations}

        steps_annotated: list[list[AnnotatedSong]] = []
        for step_selections in retrieval.selections:
            step_songs = []
            for sel in step_selections:
                ann = annotation_map.get(sel.song["id"], {})
                query = sel.song.get(
                    "spotify_query", f"{sel.song['title']} {sel.song['artist']}"
                )
                spotify_url = (
                    f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
                )
                step_songs.append(
                    AnnotatedSong(
                        song=sel.song,
                        score=sel.score,
                        target_mood=sel.target_mood,
                        psychology_snippet=sel.psychology_snippet,
                        step_index=sel.step_index,
                        personal_note=ann.get("personal_note", ""),
                        why_now=ann.get("why_now", ""),
                        spotify_url=spotify_url,
                    )
                )
            steps_annotated.append(step_songs)

        return SynthesizedPlaylist(
            arc=arc_plan.arc,
            steps=steps_annotated,
            arc_narrative=arc_plan.arc_narrative,
        )
