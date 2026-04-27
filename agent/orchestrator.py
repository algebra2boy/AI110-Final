"""
MoodArc Orchestrator — coordinates the 5-step agent pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from agent.emotion_parser import ParsedEmotion, parse_emotion
from agent.arc_planner import EmotionalArc, plan_arc
from agent.music_retriever import RetrievalResult, retrieve_songs
from agent.playlist_synth import SynthesizedPlaylist, synthesize_playlist
from agent.evaluator import EvaluationResult, evaluate_arc
from utils.logger import log_journey


@dataclass
class JourneyResult:
    emotion: ParsedEmotion
    arc_plan: EmotionalArc
    retrieval: RetrievalResult
    playlist: SynthesizedPlaylist
    evaluation: EvaluationResult
    user_input: str

    def to_log_dict(self) -> dict:
        return {
            "arc": self.playlist.arc,
            "confidence": self.evaluation.overall_confidence,
            "playlist": [
                {"title": s.title, "artist": s.artist}
                for s in self.playlist.flat()
            ],
        }


StepCallback = Callable[[str, Any], None]

STEPS = [
    "emotion_parsed",
    "arc_planned",
    "songs_retrieved",
    "playlist_synthesized",
    "evaluated",
]


class MoodArcOrchestrator:
    def run(
        self,
        user_input: str,
        on_step: StepCallback | None = None,
    ) -> JourneyResult:
        def emit(event: str, data: Any) -> None:
            if on_step:
                on_step(event, data)

        emotion = parse_emotion(user_input)
        emit("emotion_parsed", emotion)

        arc_plan = plan_arc(emotion)
        emit("arc_planned", arc_plan)

        retrieval = retrieve_songs(arc_plan, n_per_step=arc_plan.num_songs_per_step)
        emit("songs_retrieved", retrieval)

        playlist = synthesize_playlist(emotion, arc_plan, retrieval)
        emit("playlist_synthesized", playlist)

        evaluation = evaluate_arc(emotion, playlist)
        emit("evaluated", evaluation)

        result = JourneyResult(
            emotion=emotion,
            arc_plan=arc_plan,
            retrieval=retrieval,
            playlist=playlist,
            evaluation=evaluation,
            user_input=user_input,
        )
        log_journey(user_input, result.to_log_dict())
        return result
