"""
Tests for MusicRetriever — pure algorithmic scoring, no LLM calls needed.
"""

import pytest
from agent.music_retriever import (
    score_song,
    retrieve_songs,
    _mood_cluster_score,
    _energy_score,
    MOOD_ENERGY_MAP,
)
from agent.arc_planner import EmotionalArc


# ─── Unit tests for scoring helpers ───────────────────────────────────────────

def test_exact_mood_match_scores_2():
    song = {"mood": "sad", "energy": 0.2, "tags": ["sad", "melancholic"], "id": "x"}
    score = _mood_cluster_score("sad", "sad")
    assert score == 2.0


def test_cluster_mood_partial_credit():
    # sad and melancholic are in the same cluster
    score = _mood_cluster_score("melancholic", "sad")
    assert score == 1.0


def test_different_cluster_zero():
    score = _mood_cluster_score("euphoric", "sad")
    assert score == 0.0


def test_energy_score_perfect():
    score = _energy_score(0.5, 0.5)
    assert score == 1.0


def test_energy_score_opposite():
    score = _energy_score(0.0, 1.0)
    assert score == 0.0


def test_energy_score_partial():
    score = _energy_score(0.3, 0.5)
    assert abs(score - 0.8) < 0.001


def test_score_song_full():
    song = {"mood": "sad", "energy": 0.20, "tags": ["sad", "heartbreak"], "id": "s1"}
    total = score_song(song, "sad")
    # mood cluster = 2.0, tag overlap = 0.5, energy = ~1.0
    assert total > 3.0


def test_score_song_mismatch():
    song = {"mood": "euphoric", "energy": 0.95, "tags": ["euphoric", "energetic"], "id": "s1"}
    total = score_song(song, "sad")
    # no mood match, no tag overlap, bad energy
    assert total < 1.0


# ─── Integration-style retrieval tests ────────────────────────────────────────

def make_arc(arc_list: list[str]) -> EmotionalArc:
    return EmotionalArc(
        arc=arc_list,
        arc_narrative="Test arc",
        num_songs_per_step=2,
        transition_rationale=["test"] * (len(arc_list) - 1),
    )


def test_retrieve_returns_correct_number_of_steps():
    arc = make_arc(["sad", "hopeful", "happy"])
    result = retrieve_songs(arc, n_per_step=2)
    assert len(result.selections) == 3


def test_retrieve_no_duplicate_songs():
    arc = make_arc(["sad", "melancholic", "nostalgic", "hopeful", "happy"])
    result = retrieve_songs(arc, n_per_step=2)
    ids = [s.song["id"] for s in result.flat_playlist()]
    assert len(ids) == len(set(ids)), "Duplicate songs found in playlist"


def test_retrieve_flat_playlist_length():
    arc = make_arc(["anxious", "calm"])
    result = retrieve_songs(arc, n_per_step=1)
    assert len(result.flat_playlist()) == 2


def test_retrieve_songs_have_required_fields():
    arc = make_arc(["sad", "hopeful"])
    result = retrieve_songs(arc, n_per_step=1)
    for sel in result.flat_playlist():
        assert "title" in sel.song
        assert "artist" in sel.song
        assert "energy" in sel.song
        assert "mood" in sel.song
        assert sel.score >= 0


def test_mood_energy_map_coverage():
    important_moods = ["sad", "anxious", "calm", "happy", "motivated", "hopeful"]
    for mood in important_moods:
        assert mood in MOOD_ENERGY_MAP, f"Missing mood: {mood}"
