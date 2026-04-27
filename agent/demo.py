"""
Demo mode: pre-built JourneyResult objects for all 5 example prompts.
Used when ANTHROPIC_API_KEY is not set so the app runs without any API calls.
"""

from __future__ import annotations
from agent.emotion_parser import ParsedEmotion
from agent.arc_planner import EmotionalArc
from agent.music_retriever import RetrievalResult, SongSelection
from agent.playlist_synth import SynthesizedPlaylist, AnnotatedSong
from agent.evaluator import EvaluationResult
from agent.orchestrator import JourneyResult

# ─── Shared song dicts (subset of data/songs.json) ────────────────────────────

_SONGS = {
    "s001": {"id":"s001","title":"Clair de Lune","artist":"Claude Debussy","genre":"classical","mood":"peaceful","energy":0.15,"tags":["calm","introspective","gentle","melancholic"]},
    "s002": {"id":"s002","title":"Someone Like You","artist":"Adele","genre":"pop","mood":"sad","energy":0.38,"tags":["sad","heartbreak","longing","emotional"]},
    "s003": {"id":"s003","title":"Fix You","artist":"Coldplay","genre":"rock","mood":"hopeful","energy":0.52,"tags":["hopeful","comforting","emotional","uplifting"]},
    "s005": {"id":"s005","title":"Weightless","artist":"Marconi Union","genre":"ambient","mood":"calm","energy":0.08,"tags":["anxiety-relief","calm","serene","meditative"]},
    "s006": {"id":"s006","title":"Don't Stop Me Now","artist":"Queen","genre":"rock","mood":"euphoric","energy":0.95,"tags":["euphoric","energetic","exhilarating","fun"]},
    "s007": {"id":"s007","title":"The Night We Met","artist":"Lord Huron","genre":"indie","mood":"nostalgic","energy":0.28,"tags":["nostalgic","melancholic","longing","reflective"]},
    "s009": {"id":"s009","title":"Gymnopédie No. 1","artist":"Erik Satie","genre":"classical","mood":"melancholic","energy":0.12,"tags":["melancholic","introspective","gentle","serene"]},
    "s011": {"id":"s011","title":"Here Comes the Sun","artist":"The Beatles","genre":"pop rock","mood":"hopeful","energy":0.58,"tags":["hopeful","warm","optimistic","uplifting"]},
    "s013": {"id":"s013","title":"Lose Yourself","artist":"Eminem","genre":"hip-hop","mood":"motivated","energy":0.91,"tags":["motivated","intense","focused","determined"]},
    "s017": {"id":"s017","title":"Eye of the Tiger","artist":"Survivor","genre":"rock","mood":"motivated","energy":0.89,"tags":["motivated","determined","triumphant","powerful"]},
    "s018": {"id":"s018","title":"Bloom","artist":"The Paper Kites","genre":"indie folk","mood":"content","energy":0.25,"tags":["content","warm","gentle","romantic"]},
    "s019": {"id":"s019","title":"Dog Days Are Over","artist":"Florence + The Machine","genre":"indie","mood":"uplifting","energy":0.75,"tags":["uplifting","triumphant","cathartic","energetic"]},
    "s020": {"id":"s020","title":"Mad World","artist":"Gary Jules","genre":"alternative","mood":"melancholic","energy":0.18,"tags":["melancholic","existential","sad","reflective"]},
    "s021": {"id":"s021","title":"Good as Hell","artist":"Lizzo","genre":"pop","mood":"empowered","energy":0.82,"tags":["empowered","confident","joyful","self-love"]},
    "s022": {"id":"s022","title":"Holocene","artist":"Bon Iver","genre":"indie folk","mood":"introspective","energy":0.20,"tags":["introspective","vast","melancholic","beautiful"]},
    "s024": {"id":"s024","title":"Hallelujah","artist":"Jeff Buckley","genre":"folk","mood":"bittersweet","energy":0.25,"tags":["bittersweet","spiritual","emotional","tender"]},
    "s025": {"id":"s025","title":"Golden Hour","artist":"JVKE","genre":"indie pop","mood":"hopeful","energy":0.60,"tags":["hopeful","romantic","warm","uplifting"]},
    "s026": {"id":"s026","title":"Let Her Go","artist":"Passenger","genre":"folk pop","mood":"nostalgic","energy":0.32,"tags":["nostalgic","regret","reflective","heartfelt"]},
    "s027": {"id":"s027","title":"September","artist":"Earth, Wind & Fire","genre":"funk","mood":"euphoric","energy":0.90,"tags":["euphoric","joyful","danceable","nostalgic-happy"]},
    "s028": {"id":"s028","title":"Yesterday","artist":"The Beatles","genre":"folk pop","mood":"melancholic","energy":0.20,"tags":["melancholic","wistful","tender","reflective"]},
    "s033": {"id":"s033","title":"Walking on Sunshine","artist":"Katrina and the Waves","genre":"pop rock","mood":"happy","energy":0.88,"tags":["happy","exuberant","classic","upbeat"]},
    "s035": {"id":"s035","title":"Stressed Out","artist":"Twenty One Pilots","genre":"indie pop","mood":"anxious","energy":0.65,"tags":["anxious","nostalgic","relatable","generational"]},
    "s036": {"id":"s036","title":"Experience","artist":"Ludovico Einaudi","genre":"neoclassical","mood":"serene","energy":0.16,"tags":["serene","transcendent","beautiful","meditative"]},
    "s039": {"id":"s039","title":"Beautiful Day","artist":"U2","genre":"rock","mood":"uplifting","energy":0.72,"tags":["uplifting","hopeful","anthemic","joyful"]},
    "s044": {"id":"s044","title":"Banana Pancakes","artist":"Jack Johnson","genre":"acoustic pop","mood":"content","energy":0.35,"tags":["content","cozy","lazy","happy"]},
    "s047": {"id":"s047","title":"Vienna","artist":"Billy Joel","genre":"pop rock","mood":"introspective","energy":0.38,"tags":["introspective","wisdom","calm-down","reassuring"]},
    "s049": {"id":"s049","title":"Rise Up","artist":"Andra Day","genre":"soul","mood":"uplifting","energy":0.58,"tags":["uplifting","resilient","powerful","soulful"]},
    "s057": {"id":"s057","title":"This Is Me","artist":"Keala Settle","genre":"pop","mood":"empowered","energy":0.80,"tags":["empowered","triumphant","self-acceptance","anthemic"]},
    "s060": {"id":"s060","title":"The Scientist","artist":"Coldplay","genre":"alternative","mood":"bittersweet","energy":0.32,"tags":["bittersweet","regret","reflective","heartfelt"]},
}


def _song(sid: str) -> dict:
    return _SONGS[sid]


def _sel(sid: str, mood: str, step: int, psych: str = "") -> SongSelection:
    s = _song(sid)
    return SongSelection(song=s, score=round(2.0 + s["energy"], 3),
                         target_mood=mood, psychology_snippet=psych, step_index=step)


def _ann(sid: str, mood: str, step: int, note: str, why: str, psych: str = "") -> AnnotatedSong:
    s = _song(sid)
    query = f"{s['title']} {s['artist']}".replace(" ", "%20")
    return AnnotatedSong(
        song=s, score=round(2.0 + s["energy"], 3),
        target_mood=mood, psychology_snippet=psych,
        step_index=step, personal_note=note, why_now=why,
        spotify_url=f"https://open.spotify.com/search/{query}",
    )


# ── Journey 1: Anxious → Calm/Focused ─────────────────────────────────────────
def _journey_anxious(user_input: str) -> JourneyResult:
    arc = ["anxious", "calm", "serene", "focused"]
    emotion = ParsedEmotion(
        current_mood="anxious", target_mood="focused", intensity=0.85,
        themes=["stress", "overwhelm", "pressure"],
        context="User is overwhelmed and anxious, seeking calm and focus.",
        needs_gradual_transition=True,
    )
    arc_plan = EmotionalArc(
        arc=arc,
        arc_narrative="We start by meeting your anxiety where it lives, then guide your nervous system down through calm waters before locking you into clear, determined focus.",
        num_songs_per_step=1,
        transition_rationale=["acknowledge the spiral", "slow the heart rate", "settle into stillness", "activate sharp focus"],
    )
    psych_anxious = "Iso Principle: music therapy starts where the listener IS emotionally before guiding them elsewhere."
    psych_calm = "Tempo Entrainment: 60 BPM music synchronizes with resting heart rate and promotes calm."
    psych_focused = "Rhythmic Auditory Stimulation: strong rhythmic music pre-activates motor cortex and mental readiness."

    retrieval = RetrievalResult(arc=arc, selections=[
        [_sel("s035", "anxious", 0, psych_anxious)],
        [_sel("s005", "calm",    1, psych_calm)],
        [_sel("s036", "serene",  2, psych_calm)],
        [_sel("s013", "focused", 3, psych_focused)],
    ])
    playlist = SynthesizedPlaylist(arc=arc, arc_narrative=arc_plan.arc_narrative, steps=[
        [_ann("s035","anxious",0,
              "This song meets you in the spiral — the fast tempo and relatable lyrics say 'I feel this too', which is exactly where you need to start.",
              "mirroring your current state", psych_anxious)],
        [_ann("s005","calm",1,
              "Weightless was literally designed to reduce anxiety by 65%. Its 60 BPM rhythm will physically slow your heart rate — let your breath follow it.",
              "nervous system reset", psych_calm)],
        [_ann("s036","serene",2,
              "Einaudi's piano asks nothing of you. Just let the notes wash over — this is the stillness before clarity arrives.",
              "settling into quiet", psych_calm)],
        [_ann("s013","focused",3,
              "Now you're ready. Eminem's relentless drive activates everything you've just calmed down into — pure locked-in focus.",
              "channeling calm into power", psych_focused)],
    ])
    evaluation = EvaluationResult(
        arc_coherence=0.92, song_fit=0.88, therapeutic_logic=0.95,
        overall_confidence=0.91, weak_transitions=[],
        evaluator_note="Strong iso-principle adherence; Weightless→Experience is a textbook anxiety-reduction sequence.",
    )
    return JourneyResult(emotion=emotion, arc_plan=arc_plan, retrieval=retrieval,
                         playlist=playlist, evaluation=evaluation, user_input=user_input)


# ── Journey 2: Sad/Heartbreak → Empowered ─────────────────────────────────────
def _journey_heartbreak(user_input: str) -> JourneyResult:
    arc = ["sad", "melancholic", "nostalgic", "hopeful", "empowered"]
    emotion = ParsedEmotion(
        current_mood="sad", target_mood="empowered", intensity=0.90,
        themes=["heartbreak", "loss", "longing", "recovery"],
        context="User is processing a painful breakup and seeking to rebuild strength.",
        needs_gradual_transition=True,
    )
    arc_plan = EmotionalArc(
        arc=arc,
        arc_narrative="We begin in the raw ache of loss — let yourself feel it fully — then move through beautiful reflection and cautious hope before stepping into your own power.",
        num_songs_per_step=1,
        transition_rationale=["sit with the pain", "find the beauty in grief", "let memory soften the hurt", "glimpse the future", "claim it"],
    )
    psych_sad = "Cathartic Release: sad music when sad provides emotional validation before transition — more effective than immediately offering uplifting tracks."
    psych_nostalgic = "Autobiographical Memory: music triggers past positive experiences, softening present pain."
    psych_empowered = "Empowerment Anthems: songs with lyrical themes of agency measurably increase feelings of confidence."

    retrieval = RetrievalResult(arc=arc, selections=[
        [_sel("s002","sad",       0, psych_sad)],
        [_sel("s009","melancholic",1, psych_sad)],
        [_sel("s007","nostalgic", 2, psych_nostalgic)],
        [_sel("s003","hopeful",   3, "")],
        [_sel("s021","empowered", 4, psych_empowered)],
    ])
    playlist = SynthesizedPlaylist(arc=arc, arc_narrative=arc_plan.arc_narrative, steps=[
        [_ann("s002","sad",0,
              "Adele wrote this for exactly this moment. You don't need to skip this feeling — let it be witnessed.",
              "meeting you in the ache", psych_sad)],
        [_ann("s009","melancholic",1,
              "Satie's gentle piano gives grief a beautiful form. There's no urgency here — just space to breathe.",
              "finding beauty in sadness", psych_sad)],
        [_ann("s007","nostalgic",2,
              "Lord Huron holds the memory tenderly. You're allowed to miss what was good — it's part of moving through.",
              "honoring what was", psych_nostalgic)],
        [_ann("s003","hopeful",3,
              "Fix You doesn't promise everything is fine — it promises someone is there. That shift from grief to hope starts here.",
              "the first glimpse forward", "")],
        [_ann("s021","empowered",4,
              "Good as Hell is your arrival. Lizzo's confidence isn't performative — it's earned. So is yours.",
              "you made it through", psych_empowered)],
    ])
    evaluation = EvaluationResult(
        arc_coherence=0.94, song_fit=0.91, therapeutic_logic=0.96,
        overall_confidence=0.93, weak_transitions=[],
        evaluator_note="Textbook iso-principle execution — cathartic start, gradual lift, powerful finish.",
    )
    return JourneyResult(emotion=emotion, arc_plan=arc_plan, retrieval=retrieval,
                         playlist=playlist, evaluation=evaluation, user_input=user_input)


# ── Journey 3: Low energy / Unmotivated → Motivated ───────────────────────────
def _journey_motivation(user_input: str) -> JourneyResult:
    arc = ["neutral", "content", "hopeful", "motivated"]
    emotion = ParsedEmotion(
        current_mood="neutral", target_mood="motivated", intensity=0.60,
        themes=["tiredness", "low energy", "needing a push"],
        context="User lacks energy and motivation and wants to get pumped up.",
        needs_gradual_transition=False,
    )
    arc_plan = EmotionalArc(
        arc=arc,
        arc_narrative="A gentle engine warm-up — we ease you from inertia through small sparks of good feeling before dropping the full-throttle motivation.",
        num_songs_per_step=1,
        transition_rationale=["break the inertia", "build a little warmth", "ignite forward momentum"],
    )
    psych_motor = "Rhythmic Auditory Stimulation: strong rhythmic music above 120 BPM activates the motor cortex and prepares for action."
    psych_dopamine = "Music and Dopamine: anticipated musical peaks trigger dopamine release — choose songs with strong builds."

    retrieval = RetrievalResult(arc=arc, selections=[
        [_sel("s044","neutral",   0, "")],
        [_sel("s011","content",   1, "")],
        [_sel("s039","hopeful",   2, psych_dopamine)],
        [_sel("s017","motivated", 3, psych_motor)],
    ])
    playlist = SynthesizedPlaylist(arc=arc, arc_narrative=arc_plan.arc_narrative, steps=[
        [_ann("s044","neutral",0,
              "Jack Johnson's easy warmth asks nothing of you — just exist here for a moment before we get moving.",
              "breaking inertia softly", "")],
        [_ann("s011","content",1,
              "The Beatles deliver pure, uncomplicated warmth. That gentle guitar says: today might actually be okay.",
              "building a small spark", "")],
        [_ann("s039","hopeful",2,
              "U2's anthemic build is your engine revving. By the chorus you'll feel that pull forward.",
              "the ramp-up begins", psych_dopamine)],
        [_ann("s017","motivated",3,
              "You know this riff. Your body responds to it before your brain does. That's the motor cortex doing its job — let it.",
              "full throttle", psych_motor)],
    ])
    evaluation = EvaluationResult(
        arc_coherence=0.88, song_fit=0.85, therapeutic_logic=0.87,
        overall_confidence=0.87, weak_transitions=[],
        evaluator_note="Clean energy escalation; Jack Johnson opener prevents jarring start for low-energy states.",
    )
    return JourneyResult(emotion=emotion, arc_plan=arc_plan, retrieval=retrieval,
                         playlist=playlist, evaluation=evaluation, user_input=user_input)


# ── Journey 4: Nostalgic/Sad → Content/Peaceful ───────────────────────────────
def _journey_nostalgic(user_input: str) -> JourneyResult:
    arc = ["nostalgic", "melancholic", "bittersweet", "content"]
    emotion = ParsedEmotion(
        current_mood="nostalgic", target_mood="content", intensity=0.65,
        themes=["nostalgia", "memory", "missing people", "acceptance"],
        context="User is feeling nostalgic and a little sad, seeking peaceful contentment.",
        needs_gradual_transition=False,
    )
    arc_plan = EmotionalArc(
        arc=arc,
        arc_narrative="We honor the nostalgia fully — sit with it, let it be beautiful — then gently release it into a warm, settled present.",
        num_songs_per_step=1,
        transition_rationale=["lean into the memory", "feel the bittersweet", "find the gratitude in it", "arrive in the present"],
    )
    psych_memory = "Autobiographical Memory: nostalgic music triggers vivid positive memories, providing emotional comfort before transition."

    retrieval = RetrievalResult(arc=arc, selections=[
        [_sel("s026","nostalgic",  0, psych_memory)],
        [_sel("s028","melancholic",1, "")],
        [_sel("s024","bittersweet",2, "")],
        [_sel("s018","content",    3, "")],
    ])
    playlist = SynthesizedPlaylist(arc=arc, arc_narrative=arc_plan.arc_narrative, steps=[
        [_ann("s026","nostalgic",0,
              "Passenger's gentle ache is the perfect companion for looking at old photos. You only miss what was truly worth having.",
              "sitting with the longing", psych_memory)],
        [_ann("s028","melancholic",1,
              "Yesterday transforms individual longing into something universal and tender — your feelings are deeply human.",
              "finding the beauty in it", "")],
        [_ann("s024","bittersweet",2,
              "Jeff Buckley holds the contradiction — joy and grief in the same breath. This is the pivot point between missing and accepting.",
              "the tender release", "")],
        [_ann("s018","content",3,
              "The Paper Kites bring you back to a quiet, warm present. The past was good — and so is right now.",
              "arriving in the present", "")],
    ])
    evaluation = EvaluationResult(
        arc_coherence=0.90, song_fit=0.87, therapeutic_logic=0.89,
        overall_confidence=0.88, weak_transitions=[],
        evaluator_note="Graceful arc — honors nostalgia before releasing it rather than suppressing it.",
    )
    return JourneyResult(emotion=emotion, arc_plan=arc_plan, retrieval=retrieval,
                         playlist=playlist, evaluation=evaluation, user_input=user_input)


# ── Journey 5: Happy → Euphoric ───────────────────────────────────────────────
def _journey_euphoric(user_input: str) -> JourneyResult:
    arc = ["happy", "uplifting", "euphoric"]
    emotion = ParsedEmotion(
        current_mood="happy", target_mood="euphoric", intensity=0.65,
        themes=["celebration", "good news", "joy"],
        context="User is already in a great mood and wants to amplify it.",
        needs_gradual_transition=False,
    )
    arc_plan = EmotionalArc(
        arc=arc,
        arc_narrative="You're already glowing — let's just turn it up. Three songs, pure escalation, no brakes.",
        num_songs_per_step=1,
        transition_rationale=["warm up the joy", "build the momentum", "peak"],
    )
    psych_dopamine = "Music and Dopamine: anticipated musical peaks trigger dopamine release. Use songs with strong builds and peaks."

    retrieval = RetrievalResult(arc=arc, selections=[
        [_sel("s033","happy",    0, "")],
        [_sel("s019","uplifting",1, psych_dopamine)],
        [_sel("s027","euphoric", 2, psych_dopamine)],
    ])
    playlist = SynthesizedPlaylist(arc=arc, arc_narrative=arc_plan.arc_narrative, steps=[
        [_ann("s033","happy",0,
              "Walking on Sunshine is exactly as advertised — pure, shameless joy. Let yourself have it.",
              "warm up the good mood", "")],
        [_ann("s019","uplifting",1,
              "Florence builds you up before she lets you fly. By the last chorus you'll feel unstoppable.",
              "momentum building", psych_dopamine)],
        [_ann("s027","euphoric",2,
              "Earth, Wind & Fire invented this feeling. September is 3 minutes and 35 seconds of the universe saying yes.",
              "peak euphoria", psych_dopamine)],
    ])
    evaluation = EvaluationResult(
        arc_coherence=0.95, song_fit=0.92, therapeutic_logic=0.90,
        overall_confidence=0.92, weak_transitions=[],
        evaluator_note="Short and tight — no padding needed for a small positive escalation.",
    )
    return JourneyResult(emotion=emotion, arc_plan=arc_plan, retrieval=retrieval,
                         playlist=playlist, evaluation=evaluation, user_input=user_input)


# ─── Keyword matcher ──────────────────────────────────────────────────────────

_RULES: list[tuple[list[str], object]] = [
    (["anxi", "stress", "exam", "overwhelm", "spiral", "panic", "focus", "calm down"], _journey_anxious),
    (["heartbreak", "breakup", "break up", "broke up", "devastat", "alone", "empower", "strong again", "move on"], _journey_heartbreak),
    (["tired", "unmotivat", "no motivation", "no energy", "monday", "pumped", "crush", "get going", "energy"], _journey_motivation),
    (["nostalgic", "nostalgia", "miss ", "old friend", "old times", "old photo", "content", "at peace", "peaceful"], _journey_nostalgic),
    (["happy", "celebrat", "great news", "amazing", "euphoric", "party"], _journey_euphoric),
]


def get_demo_journey(user_input: str) -> JourneyResult:
    lowered = user_input.lower()
    for keywords, factory in _RULES:
        if any(kw in lowered for kw in keywords):
            return factory(user_input)
    return _journey_heartbreak(user_input)  # default: most universally relatable
