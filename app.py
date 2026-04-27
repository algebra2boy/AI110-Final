"""
MoodArc — AI Emotional Music Journey Planner
Streamlit interactive UI
"""

import streamlit as st
import plotly.graph_objects as go
import time

from agent.orchestrator import MoodArcOrchestrator, JourneyResult
from utils.guardrails import check_input

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MoodArc — Music for Your Journey",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .hero-title {
    font-size: 3rem; font-weight: 700; text-align: center;
    background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem;
  }
  .hero-sub {
    text-align: center; color: #9ca3af; font-size: 1.1rem; margin-bottom: 2rem;
  }
  .song-card {
    background: #1e1e2e; border: 1px solid #2d2d3d; border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 0.75rem;
    transition: border-color 0.2s;
  }
  .song-card:hover { border-color: #6366f1; }
  .song-title { font-size: 1.05rem; font-weight: 600; color: #e2e8f0; }
  .song-artist { color: #94a3b8; font-size: 0.9rem; }
  .song-note { color: #cbd5e1; font-size: 0.88rem; margin-top: 0.5rem; line-height: 1.5; }
  .song-why { color: #818cf8; font-size: 0.8rem; font-style: italic; margin-top: 0.3rem; }
  .mood-badge {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600; margin-right: 6px;
    background: #312e81; color: #a5b4fc;
  }
  .energy-bar-bg {
    background: #374151; border-radius: 4px; height: 6px; width: 100%;
    margin-top: 6px;
  }
  .step-header {
    font-size: 0.85rem; font-weight: 600; color: #6366f1;
    text-transform: uppercase; letter-spacing: 0.05em;
    margin: 1.25rem 0 0.5rem;
  }
  .confidence-pill {
    display: inline-block; padding: 4px 14px; border-radius: 20px;
    font-size: 0.85rem; font-weight: 600;
  }
  .psych-note {
    background: #0f172a; border-left: 3px solid #6366f1;
    padding: 0.6rem 0.9rem; border-radius: 0 8px 8px 0;
    color: #94a3b8; font-size: 0.8rem; margin-top: 0.5rem;
  }
  .stat-box {
    background: #1e1e2e; border-radius: 10px; padding: 1rem;
    text-align: center; border: 1px solid #2d2d3d;
  }
  .stat-num { font-size: 1.8rem; font-weight: 700; color: #a5b4fc; }
  .stat-label { font-size: 0.8rem; color: #64748b; }
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🎵 MoodArc</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Tell me how you feel. I\'ll plan a musical journey to where you want to be.</div>',
    unsafe_allow_html=True,
)

# ─── Example prompts ───────────────────────────────────────────────────────────
EXAMPLES = [
    "I've been feeling really anxious and overwhelmed about exams. I just want to feel calm and focused.",
    "I'm heartbroken after a breakup. I want to eventually feel empowered and ready to move on.",
    "Super tired and unmotivated on a Monday morning. Need to get pumped up for work.",
    "Feeling nostalgic and a bit sad thinking about old friends. Would love to end up feeling content and warm.",
    "I'm angry and frustrated after a bad day. I want to wind down and feel peaceful.",
]

col_input, col_tips = st.columns([3, 1])

with col_input:
    # Seed textarea if an example was clicked
    if "example_text" not in st.session_state:
        st.session_state.example_text = ""

    user_input = st.text_area(
        "How are you feeling? Where do you want to be?",
        value=st.session_state.example_text,
        placeholder="e.g. 'I'm feeling really sad and lonely tonight. I want to feel a little more hopeful by the end.'",
        height=120,
        key="main_input",
    )
    generate_btn = st.button("🎵 Generate My Journey", type="primary", use_container_width=True)

with col_tips:
    st.markdown("**Try an example:**")
    for i, ex in enumerate(EXAMPLES):
        if st.button(f"Example {i+1}", key=f"ex_{i}", use_container_width=True):
            st.session_state.example_text = ex
            st.rerun()

st.divider()

# ─── Main logic ────────────────────────────────────────────────────────────────
if generate_btn and user_input.strip():
    guard = check_input(user_input)
    if guard.blocked:
        if guard.reason == "crisis_language":
            st.error(guard.message, icon="💙")
        else:
            st.warning(guard.message, icon="⚠️")
        st.stop()

    # ── Agent pipeline with live step display ──────────────────────────────────
    result_holder: list[JourneyResult] = []
    step_data: dict = {}

    st.markdown("### 🤖 Agent Pipeline Running...")

    with st.status("Running MoodArc Agent Pipeline", expanded=True) as status_box:
        step_labels = {
            "emotion_parsed": "Step 1 — Parsing your emotional state",
            "arc_planned": "Step 2 — Designing your emotional arc",
            "songs_retrieved": "Step 3 — Retrieving songs (RAG)",
            "playlist_synthesized": "Step 4 — Writing personalized notes",
            "evaluated": "Step 5 — Self-evaluating arc quality",
        }

        def on_step(event: str, data):
            step_data[event] = data
            label = step_labels.get(event, event)
            st.write(f"✅ {label}")

        try:
            orchestrator = MoodArcOrchestrator()
            journey = orchestrator.run(user_input, on_step=on_step)
            result_holder.append(journey)
            status_box.update(label="Journey ready!", state="complete", expanded=False)
        except Exception as e:
            status_box.update(label=f"Error: {e}", state="error")
            st.error(f"Something went wrong: {e}")
            st.stop()

    journey = result_holder[0]

    # ── Journey header ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"## Your Journey: `{' → '.join(journey.playlist.arc)}`")
    st.markdown(f"*{journey.playlist.arc_narrative}*")

    # ── Stats row ─────────────────────────────────────────────────────────────
    eval_ = journey.evaluation
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-box">
          <div class="stat-num">{len(journey.playlist.arc)}</div>
          <div class="stat-label">Arc Steps</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-box">
          <div class="stat-num">{journey.playlist.total_songs()}</div>
          <div class="stat-label">Songs</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        conf_pct = int(eval_.overall_confidence * 100)
        st.markdown(f"""
        <div class="stat-box">
          <div class="stat-num" style="color:{eval_.confidence_color()}">{conf_pct}%</div>
          <div class="stat-label">AI Confidence</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-box">
          <div class="stat-num">{eval_.confidence_label()}</div>
          <div class="stat-label">Arc Quality</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # ── Arc visualization ─────────────────────────────────────────────────────
    MOOD_VALENCE: dict[str, float] = {
        "grieving": 0.05, "sad": 0.15, "lonely": 0.20, "melancholic": 0.22,
        "anxious": 0.28, "stressed": 0.30, "bittersweet": 0.38, "nostalgic": 0.42,
        "neutral": 0.50, "introspective": 0.45, "calm": 0.55, "peaceful": 0.60,
        "serene": 0.62, "content": 0.68, "focused": 0.65,
        "hopeful": 0.72, "uplifting": 0.78, "motivated": 0.82,
        "happy": 0.86, "energetic": 0.88, "empowered": 0.90, "euphoric": 0.96, "dramatic": 0.50,
    }

    arc_moods = journey.playlist.arc
    arc_y = [MOOD_VALENCE.get(m, 0.5) for m in arc_moods]
    arc_x = list(range(len(arc_moods)))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=arc_x, y=arc_y,
        mode="lines+markers+text",
        text=arc_moods,
        textposition="top center",
        line=dict(color="#6366f1", width=3),
        marker=dict(
            size=14,
            color=arc_y,
            colorscale=[[0, "#ef4444"], [0.4, "#f59e0b"], [0.65, "#84cc16"], [1.0, "#22c55e"]],
            line=dict(color="white", width=2),
        ),
        textfont=dict(color="#e2e8f0", size=12),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.08)",
    ))

    # Mark weak transitions
    for wi in eval_.weak_transitions:
        if wi < len(arc_x) - 1:
            fig.add_shape(
                type="line",
                x0=arc_x[wi], x1=arc_x[wi + 1],
                y0=arc_y[wi], y1=arc_y[wi + 1],
                line=dict(color="#ef4444", width=2, dash="dot"),
            )

    fig.update_layout(
        title="Your Emotional Arc",
        title_font=dict(color="#e2e8f0", size=16),
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="#94a3b8"),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, title="Journey"),
        yaxis=dict(
            range=[0, 1.1], showgrid=True, gridcolor="#1e293b",
            tickvals=[0.1, 0.3, 0.5, 0.7, 0.9],
            ticktext=["Very Low", "Low", "Neutral", "Positive", "Euphoric"],
            title="Emotional Positivity",
        ),
        height=320,
        margin=dict(l=60, r=20, t=50, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)

    if eval_.weak_transitions:
        st.caption(
            f"⚠️ Dashed red lines mark transitions the AI flagged as potentially rough "
            f"(steps {[t+1 for t in eval_.weak_transitions]})."
        )

    # ── Playlist ──────────────────────────────────────────────────────────────
    st.markdown("## 🎶 Your Playlist")

    MOOD_EMOJIS = {
        "sad": "😢", "melancholic": "🌧️", "anxious": "😰", "stressed": "😤",
        "lonely": "🌙", "nostalgic": "📷", "bittersweet": "🍂", "grieving": "💔",
        "neutral": "😌", "calm": "🌊", "peaceful": "🕊️", "serene": "✨",
        "content": "☕", "introspective": "🌿", "focused": "🎯",
        "hopeful": "🌱", "uplifting": "🌤️", "motivated": "⚡",
        "happy": "😊", "energetic": "🔥", "euphoric": "🎉", "empowered": "💪",
    }

    for step_idx, (step_mood, step_songs) in enumerate(
        zip(journey.playlist.arc, journey.playlist.steps)
    ):
        emoji = MOOD_EMOJIS.get(step_mood, "🎵")
        is_weak = step_idx in eval_.weak_transitions

        st.markdown(
            f'<div class="step-header">'
            f'{emoji} Step {step_idx + 1} — {step_mood.title()}'
            f'{" ⚠️" if is_weak else ""}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Show transition rationale if available
        if step_idx < len(journey.arc_plan.transition_rationale):
            rat = journey.arc_plan.transition_rationale[step_idx]
            st.caption(f"Why here: *{rat}*")

        for song in step_songs:
            energy_pct = int(song.energy * 100)
            st.markdown(f"""
            <div class="song-card">
              <div style="display:flex; justify-content:space-between; align-items:flex-start">
                <div>
                  <span class="song-title">{song.title}</span>
                  <span class="song-artist"> — {song.artist}</span>
                </div>
                <span class="mood-badge">{song.mood}</span>
              </div>
              <div class="energy-bar-bg">
                <div style="background:linear-gradient(90deg,#6366f1,#a855f7);
                  width:{energy_pct}%;height:100%;border-radius:4px;"></div>
              </div>
              <div style="font-size:0.72rem;color:#475569;margin-top:2px">
                Energy {energy_pct}% &nbsp;·&nbsp; Score {song.score}
              </div>
              {f'<div class="song-note">{song.personal_note}</div>' if song.personal_note else ''}
              {f'<div class="song-why">Why now: {song.why_now}</div>' if song.why_now else ''}
              {f'<div class="psych-note">📚 {song.psychology_snippet[:180]}...</div>' if song.psychology_snippet else ''}
            </div>
            """, unsafe_allow_html=True)

            col_spot, _ = st.columns([1, 3])
            with col_spot:
                st.markdown(
                    f'<a href="{song.spotify_url}" target="_blank" '
                    f'style="text-decoration:none; color:#1db954; font-size:0.85rem;">'
                    f'▶ Search on Spotify</a>',
                    unsafe_allow_html=True,
                )

    # ── Evaluator panel ───────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("🔍 AI Self-Evaluation Report", expanded=False):
        ecol1, ecol2, ecol3 = st.columns(3)
        with ecol1:
            st.metric("Arc Coherence", f"{int(eval_.arc_coherence * 100)}%")
        with ecol2:
            st.metric("Song Fit", f"{int(eval_.song_fit * 100)}%")
        with ecol3:
            st.metric("Therapeutic Logic", f"{int(eval_.therapeutic_logic * 100)}%")

        st.info(f"**Evaluator note:** {eval_.evaluator_note}")

        if eval_.weak_transitions:
            st.warning(
                f"Weak transitions at arc steps: {[t + 1 for t in eval_.weak_transitions]}. "
                "Consider manually adjusting those songs if the transition feels off."
            )
        else:
            st.success("No weak transitions detected — the arc flows well.")

    # ── Emotion analysis panel ────────────────────────────────────────────────
    with st.expander("🧠 Emotion Analysis Details", expanded=False):
        em = journey.emotion
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Detected mood:** `{em.current_mood}`")
            st.markdown(f"**Target mood:** `{em.target_mood}`")
            st.markdown(f"**Intensity:** {int(em.intensity * 100)}%")
        with col_b:
            st.markdown(f"**Themes:** {', '.join(em.themes)}")
            st.markdown(f"**Context:** {em.context}")
            st.markdown(f"**Gradual transition needed:** {'Yes' if em.needs_gradual_transition else 'No'}")

    st.markdown("")
    st.caption(
        "MoodArc is not a mental health service. If you're struggling, please reach out to a professional. "
        "Crisis support: call or text **988** (US)."
    )

elif generate_btn and not user_input.strip():
    st.warning("Please describe how you're feeling first.")

# ─── Sidebar info ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎵 MoodArc")
    st.markdown("""
    **How it works:**

    1. **Emotion Parser** — Claude reads your description and extracts current + target mood
    2. **Arc Planner** — Designs a step-by-step emotional transition using music therapy's ISO principle
    3. **Music Retriever (RAG)** — Scores 60 real songs using content-based filtering + psychology knowledge base
    4. **Playlist Synthesizer** — Claude writes personalized notes for each song
    5. **Arc Evaluator** — Claude rates its own output for coherence and therapeutic logic

    ---
    **Base project:** AI110 Module 3 — Music Recommender Simulation

    **New features:**
    - 🤖 5-step agentic pipeline
    - 📚 RAG from music psychology research
    - 🛡️ Safety guardrails
    - 📊 AI self-evaluation + confidence scoring
    - 📈 Arc visualization
    """)
