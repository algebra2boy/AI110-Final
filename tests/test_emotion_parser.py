"""
Tests for EmotionParser — these run against the real parsing logic
without calling the LLM (we test the output parsing and dataclass).
"""

import pytest
from unittest.mock import patch
from agent.emotion_parser import ParsedEmotion, parse_emotion


MOCK_SAD_JSON = """{
  "current_mood": "sad",
  "target_mood": "hopeful",
  "intensity": 0.8,
  "themes": ["heartbreak", "longing"],
  "context": "User just went through a breakup.",
  "needs_gradual_transition": true
}"""

MOCK_ANXIOUS_JSON = """{
  "current_mood": "anxious",
  "target_mood": "calm",
  "intensity": 0.9,
  "themes": ["exams", "pressure", "stress"],
  "context": "User is overwhelmed by upcoming exams.",
  "needs_gradual_transition": false
}"""

MOCK_HAPPY_JSON = """{
  "current_mood": "happy",
  "target_mood": "euphoric",
  "intensity": 0.6,
  "themes": ["celebration", "success"],
  "context": "User is in a good mood and wants to feel amazing.",
  "needs_gradual_transition": false
}"""


@patch("agent.emotion_parser.call_claude_json", return_value=MOCK_SAD_JSON)
def test_parse_sad_to_hopeful(mock_call):
    result = parse_emotion("I feel heartbroken after my breakup")
    assert result.current_mood == "sad"
    assert result.target_mood == "hopeful"
    assert result.intensity == 0.8
    assert "heartbreak" in result.themes
    assert result.needs_gradual_transition is True


@patch("agent.emotion_parser.call_claude_json", return_value=MOCK_ANXIOUS_JSON)
def test_parse_anxious_to_calm(mock_call):
    result = parse_emotion("I'm really anxious about my exams")
    assert result.current_mood == "anxious"
    assert result.target_mood == "calm"
    assert result.intensity == 0.9
    assert result.needs_gradual_transition is False


@patch("agent.emotion_parser.call_claude_json", return_value=MOCK_HAPPY_JSON)
def test_parse_happy_escalation(mock_call):
    result = parse_emotion("I'm happy, want to feel amazing")
    assert result.current_mood == "happy"
    assert result.target_mood == "euphoric"


def test_mood_gap_format():
    emotion = ParsedEmotion(
        current_mood="sad",
        target_mood="hopeful",
        intensity=0.7,
        themes=["loss"],
        context="Feeling down.",
        needs_gradual_transition=True,
    )
    assert emotion.mood_gap() == "sad → hopeful"


@patch("agent.emotion_parser.call_claude_json")
def test_parse_handles_fenced_json(mock_call):
    """Parser should strip markdown fences if model returns them."""
    mock_call.return_value = "```json\n" + MOCK_SAD_JSON + "\n```"
    result = parse_emotion("some input")
    assert result.current_mood == "sad"


@patch("agent.emotion_parser.call_claude_json", return_value=MOCK_SAD_JSON)
def test_parse_returns_parsed_emotion_dataclass(mock_call):
    result = parse_emotion("test")
    assert isinstance(result, ParsedEmotion)
    assert isinstance(result.themes, list)
    assert isinstance(result.intensity, float)
