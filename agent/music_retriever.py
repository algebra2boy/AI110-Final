"""
Agent Step 3 — Music Retriever (RAG)
Selects songs for each arc step by combining:
  1. Module 3's content-based scoring algorithm
  2. Music psychology knowledge retrieval (RAG)
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from agent.arc_planner import EmotionalArc
from utils.logger import AgentStepLogger

DATA_DIR = Path(__file__).parent.parent / "data"

MOOD_ENERGY_MAP: dict[str, float] = {
    "grieving": 0.10,
    "sad": 0.20,
    "lonely": 0.22,
    "melancholic": 0.22,
    "anxious": 0.65,
    "stressed": 0.60,
    "introspective": 0.25,
    "bittersweet": 0.30,
    "nostalgic": 0.38,
    "neutral": 0.45,
    "calm": 0.20,
    "peaceful": 0.18,
    "serene": 0.18,
    "content": 0.40,
    "focused": 0.45,
    "hopeful": 0.55,
    "uplifting": 0.68,
    "motivated": 0.82,
    "energetic": 0.88,
    "happy": 0.80,
    "euphoric": 0.92,
    "empowered": 0.82,
    "dramatic": 0.70,
}

# Mood similarity clusters — moods close together get partial credit
MOOD_CLUSTERS: list[list[str]] = [
    ["sad", "melancholic", "grieving", "lonely"],
    ["anxious", "stressed"],
    ["nostalgic", "bittersweet", "introspective"],
    ["calm", "peaceful", "serene"],
    ["content", "neutral"],
    ["hopeful", "uplifting"],
    ["motivated", "energetic", "empowered"],
    ["happy", "euphoric"],
    ["focused"],
    ["dramatic"],
]


def _mood_cluster_score(song_mood: str, target_mood: str) -> float:
    if song_mood == target_mood:
        return 2.0
    for cluster in MOOD_CLUSTERS:
        if song_mood in cluster and target_mood in cluster:
            return 1.0
    return 0.0


def _tag_overlap_score(song_tags: list[str], target_mood: str) -> float:
    if target_mood in song_tags:
        return 0.5
    return 0.0


def _energy_score(song_energy: float, target_energy: float) -> float:
    return 1.0 - abs(song_energy - target_energy)


def score_song(song: dict, target_mood: str) -> float:
    target_energy = MOOD_ENERGY_MAP.get(target_mood, 0.5)
    return (
        _mood_cluster_score(song["mood"], target_mood)
        + _tag_overlap_score(song.get("tags", []), target_mood)
        + _energy_score(song["energy"], target_energy)
    )


@dataclass
class SongSelection:
    song: dict
    score: float
    target_mood: str
    psychology_snippet: str = ""
    step_index: int = 0


@dataclass
class RetrievalResult:
    arc: list[str]
    selections: list[list[SongSelection]] = field(default_factory=list)

    def flat_playlist(self) -> list[SongSelection]:
        return [s for step in self.selections for s in step]


def _load_songs() -> list[dict]:
    with open(DATA_DIR / "songs.json") as f:
        return json.load(f)


def _load_psychology() -> list[dict]:
    with open(DATA_DIR / "music_psychology.json") as f:
        return json.load(f)


def _retrieve_psychology(mood: str, psychology: list[dict]) -> str:
    relevant = [
        p for p in psychology
        if mood in p.get("mood_relevance", [])
    ]
    if not relevant:
        return ""
    best = relevant[0]
    return f"{best['principle']}: {best['description']}"


def retrieve_songs(arc_plan: EmotionalArc, n_per_step: int = 2) -> RetrievalResult:
    with AgentStepLogger("MusicRetriever", str(arc_plan.arc)):
        songs = _load_songs()
        psychology = _load_psychology()
        used_ids: set[str] = set()
        result = RetrievalResult(arc=arc_plan.arc)

        for step_idx, target_mood in enumerate(arc_plan.arc):
            scored = [
                (s, score_song(s, target_mood))
                for s in songs
                if s["id"] not in used_ids
            ]
            scored.sort(key=lambda x: x[1], reverse=True)

            step_selections = []
            for song, score in scored[:n_per_step]:
                used_ids.add(song["id"])
                psych = _retrieve_psychology(target_mood, psychology)
                step_selections.append(
                    SongSelection(
                        song=song,
                        score=round(score, 3),
                        target_mood=target_mood,
                        psychology_snippet=psych,
                        step_index=step_idx,
                    )
                )
            result.selections.append(step_selections)

        return result
