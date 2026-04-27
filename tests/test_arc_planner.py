"""
Tests for ArcPlanner output parsing and structure.
"""

import pytest
from unittest.mock import patch
from agent.arc_planner import EmotionalArc, plan_arc
from agent.emotion_parser import ParsedEmotion


MOCK_LONG_ARC = """{
  "arc": ["sad", "melancholic", "nostalgic", "hopeful", "happy"],
  "arc_narrative": "Starting in sadness, we move through reflective nostalgia before rising to joy.",
  "num_songs_per_step": 2,
  "transition_rationale": ["grounding", "bridging", "shifting", "elevating"]
}"""

MOCK_SHORT_ARC = """{
  "arc": ["anxious", "calm", "content"],
  "arc_narrative": "Quick de-escalation from anxiety to contentment.",
  "num_songs_per_step": 1,
  "transition_rationale": ["de-escalate", "settle"]
}"""


def make_emotion(current: str, target: str, gradual: bool = True) -> ParsedEmotion:
    return ParsedEmotion(
        current_mood=current,
        target_mood=target,
        intensity=0.7,
        themes=["test"],
        context="Test context.",
        needs_gradual_transition=gradual,
    )


@patch("agent.arc_planner.call_claude_json", return_value=MOCK_LONG_ARC)
def test_long_arc_has_5_steps(mock_call):
    emotion = make_emotion("sad", "happy", gradual=True)
    arc = plan_arc(emotion)
    assert len(arc.arc) == 5
    assert arc.arc[0] == "sad"
    assert arc.arc[-1] == "happy"


@patch("agent.arc_planner.call_claude_json", return_value=MOCK_SHORT_ARC)
def test_short_arc_has_3_steps(mock_call):
    emotion = make_emotion("anxious", "content", gradual=False)
    arc = plan_arc(emotion)
    assert len(arc.arc) == 3


@patch("agent.arc_planner.call_claude_json", return_value=MOCK_LONG_ARC)
def test_arc_total_songs(mock_call):
    emotion = make_emotion("sad", "happy")
    arc = plan_arc(emotion)
    assert arc.total_songs() == 10  # 5 steps × 2 songs


@patch("agent.arc_planner.call_claude_json", return_value=MOCK_LONG_ARC)
def test_arc_has_narrative(mock_call):
    emotion = make_emotion("sad", "happy")
    arc = plan_arc(emotion)
    assert len(arc.arc_narrative) > 10


@patch("agent.arc_planner.call_claude_json", return_value=MOCK_LONG_ARC)
def test_transition_rationale_length(mock_call):
    emotion = make_emotion("sad", "happy")
    arc = plan_arc(emotion)
    assert len(arc.transition_rationale) == len(arc.arc) - 1


def test_emotional_arc_dataclass():
    arc = EmotionalArc(
        arc=["sad", "hopeful"],
        arc_narrative="Brief journey",
        num_songs_per_step=1,
        transition_rationale=["shift"],
    )
    assert arc.total_songs() == 2
