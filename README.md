# 🎵 MoodArc — AI Emotional Music Journey Planner

> **Base Project:** AI110 Module 3 — Music Recommender Simulation  
> A content-based filtering system that scored songs against user preferences (genre, mood, energy) using a weighted scoring algorithm.

MoodArc extends the Module 3 recommender into a **5-step agentic AI system** that takes your emotional state in plain English and plans a personalized musical journey to shift your mood — grounded in music therapy research and transparent AI reasoning at every step.

**Demo Walkthrough**

If you have a recorded walkthrough you can link it here. Two common approaches:

- Host the video on Loom or YouTube and paste a link (GitHub will show a clickable link and sometimes a preview thumbnail):

       Example: https://www.loom.com/share/your-video-id

- Add a small MP4 to the `assets/` folder and embed it directly in the README (GitHub will render the player):

       ```html
       <video controls width="720">
              <source src="assets/demo.mp4" type="video/mp4">
              Your browser does not support the video tag.
       </video>
       ```

Or, embed a YouTube preview thumbnail that links to the video (recommended):

[![Watch the demo on YouTube](https://img.youtube.com/vi/8KWkmGRaHUo/hqdefault.jpg)](https://youtu.be/8KWkmGRaHUo)

Note: GitHub strips iframes, so embedding a Loom iframe won't work in a README — use a direct link, a thumbnail image that links to YouTube, or host a small MP4 inside the repo.

---

## What's New vs. Module 3

| Feature | Module 3 | MoodArc |
|---|---|---|
| Input | Genre/mood dropdowns | Free-text emotional description |
| AI | Pure algorithm | 5-step Gemini agent pipeline |
| Retrieval | Catalog scoring only | RAG from music psychology research |
| Explanation | Score breakdown | Personalized therapeutic notes |
| Reliability | Unit tests | AI self-evaluation + confidence scoring |
| Safety | None | Crisis detection + guardrails |

---

## System Architecture

```
User Input (natural language emotional description)
         │
         ▼
  ┌─────────────┐
  │  Guardrails  │ ── crisis language → crisis resources
  └──────┬──────┘    prompt injection → blocked
         │
         ▼
  ┌─────────────────────────────────────────────────────┐
  │              MoodArc Agent Pipeline                  │
  │                                                     │
  │  Step 1: EmotionParser                              │
  │    Gemini → { current_mood, target_mood,            │
  │               intensity, themes, context }          │
  │                    │                                │
  │  Step 2: ArcPlanner                                 │
  │    Gemini → { arc: [mood₁ → mood₂ → ... → moodN],  │
  │               iso-principle transitions }           │
  │                    │                                │
  │  Step 3: MusicRetriever (RAG)                       │
  │    Catalog scoring (Module 3 algo)                  │
  │    + Music psychology knowledge base retrieval      │
  │    → top songs per arc step                         │
  │                    │                                │
  │  Step 4: PlaylistSynthesizer                        │
  │    Gemini → personalized notes per song             │
  │                    │                                │
  │  Step 5: ArcEvaluator                               │
  │    Gemini → confidence score (0–1)                  │
  │             arc coherence, song fit, therapy logic  │
  └─────────────────────────────────────────────────────┘
         │
         ▼
  Interactive Streamlit UI
  • Emotional arc visualization (Plotly)
  • Annotated song cards with Spotify search links
  • AI self-evaluation panel
  • Structured logging
```

![System Architecture](assets/architecture.png)

---

## AI Features Implemented

### 1. Agentic Workflow ✅ (required + stretch)
A 5-step pipeline where each Gemini call informs the next. The agent:
- Parses unstructured emotion text into structured data
- Plans a music therapy arc using the ISO principle
- Retrieves songs scored against each arc step
- Generates personalized explanations for each song
- Self-evaluates the full arc for coherence and therapeutic logic

Intermediate steps are visible in the Streamlit UI via `st.status()`.

### 2. RAG Enhancement ✅ (required + stretch)
The `MusicRetriever` combines:
- **Content-based scoring** (Module 3's algorithm: mood matching, energy proximity, acoustic bonus)
- **Psychology knowledge retrieval**: a curated database of 13 music therapy research principles. For each arc step, relevant principles are retrieved by mood tag and injected into the song explanations.

### 3. Reliability & Evaluation System ✅ (required + stretch)
- **AI confidence scoring**: The evaluator agent rates `arc_coherence`, `song_fit`, and `therapeutic_logic` (each 0–1)
- **Structured logging**: Every journey is logged with timing per step to `logs/moodarc_YYYYMMDD.log`
- **Unit test suite**: 26 tests across 4 test files (no LLM calls required)
- **Eval harness**: `eval_harness.py` runs 8 predefined test cases with pass/fail + confidence summary

---

## Setup Instructions

### 1. Clone and set up environment

```bash
git clone https://github.com/yongyetan1209/moodarc.git
cd moodarc
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure your API key

```bash
cp .env.example .env
# Edit .env and set your GEMINI_API_KEY
```

Get a key at: https://aistudio.google.com/app/apikey

### 3. Run the app

```bash
streamlit run app.py
```

### 4. Run tests

```bash
pytest                             # all 26 tests (no API key needed)
```

### 5. Run the evaluation harness

```bash
python eval_harness.py --quick     # guardrails only, no API calls
python eval_harness.py             # full pipeline (requires API key)
```

---

## Sample Interactions

### Example 1 — Heartbreak to empowerment
**Input:** *"I just went through a really painful breakup. I feel devastated and alone. I want to feel strong and empowered again."*

**Arc generated:** `sad → melancholic → nostalgic → hopeful → empowered`

**Narrative:** *"We start where you are — in the raw ache of loss — and move through the beauty of reflection before stepping into your own power."*

**Songs selected (partial):**
1. Someone Like You — Adele *(sad: "This song meets you exactly where you are — feeling that specific ache of watching someone you love move on.")*
2. Hallelujah — Jeff Buckley *(nostalgic: "Sitting with the bittersweet beauty of what was, before letting it go.")*
3. Rise Up — Andra Day *(empowered: "Now you're ready. This is your anthem.")*

**AI Confidence: 87% (Excellent)**

---

### Example 2 — Exam anxiety to calm focus
**Input:** *"I have finals tomorrow and I'm spiraling with anxiety. I can't focus at all. I want to feel calm and focused."*

**Arc generated:** `anxious → stressed → calm → focused`

**Songs selected (partial):**
1. Weightless — Marconi Union *(anxious: "Scientifically designed to reduce anxiety by 65% — the 60 BPM rhythm will physically slow your heart rate.")*
2. Gymnopédie No. 1 — Erik Satie *(calm: "The gentle, unhurried pace signals safety to your nervous system.")*
3. Lose Yourself — Eminem *(focused: "Once calm, this will lock you into sharp, determined focus.")*

**AI Confidence: 82% (Good)**

---

### Example 3 — Guardrail trigger
**Input:** *"I want to end my life"*

**Output:** Crisis resources displayed immediately. No music generated.

---

## Design Decisions

**Why 5 pipeline steps instead of one big prompt?**  
Each step has a distinct concern (parse → plan → retrieve → explain → evaluate). Separating them allows independent testing, better error isolation, and the ability to see intermediate reasoning.

**Why the ISO principle for arc design?**  
Music therapy research shows that matching the listener's current emotional state before transitioning is more effective than immediately offering "happier" music. A sad person who receives only upbeat songs often rejects them.

**Why Gemini Flash for most steps?**  
Cost and speed. Gemini Flash is fast enough for real-time Streamlit streaming and accurate enough for structured JSON tasks. The eval harness uses it for all 5 steps.

**Why real songs with Spotify links vs. fictional ones?**  
Module 3 used fictional songs for simplicity. MoodArc uses real songs to make the output immediately actionable — users can actually listen.

**Trade-offs:**  
- Real songs means our energy/mood data is hand-labeled, not from Spotify's API. This introduces inaccuracy.
- The 60-song catalog is small; some arc steps may return suboptimal matches.
- No memory across sessions — each journey starts fresh.

---

## Testing Summary

| Test File | Tests | Coverage |
|---|---|---|
| `test_guardrails.py` | 9 | Crisis detection, injection, edge cases |
| `test_music_retriever.py` | 10 | Scoring algorithm, retrieval, deduplication |
| `test_emotion_parser.py` | 6 | JSON parsing, dataclass, fence stripping |
| `test_arc_planner.py` | 6 | Arc structure, rationale length, song count |
| **Total** | **31** | — |

**Eval harness results (full mode):**
- 5/5 LLM test cases passed
- 3/3 guardrail cases passed
- Average AI confidence: **0.74** (Good)
- One case ("Already happy → euphoric") scored lower (0.60) because the small mood gap produced a 3-step arc where 2 songs sometimes repeat genre

**What didn't work at first:**  
The arc planner initially ignored the ISO principle and jumped straight to uplifting songs. Fixed by explicitly including the ISO principle definition in the system prompt and requiring `arc[0] == current_mood`.

---

## Reflection

See [model_card.md](model_card.md) for the full ethics and AI collaboration reflection.

---

## Project Structure

```
moodarc/
├── app.py                     # Streamlit UI
├── eval_harness.py            # Evaluation + test harness script
├── requirements.txt
├── .env.example
├── agent/
│   ├── orchestrator.py        # Pipeline coordinator
│   ├── emotion_parser.py      # Step 1: NLP emotion parsing
│   ├── arc_planner.py         # Step 2: Emotional arc design
│   ├── music_retriever.py     # Step 3: RAG song selection
│   ├── playlist_synth.py      # Step 4: Personalized explanations
│   └── evaluator.py           # Step 5: Self-evaluation + confidence
├── data/
│   ├── songs.json             # 60-song real catalog
│   └── music_psychology.json  # 13 music therapy research principles (RAG KB)
├── utils/
│   ├── llm_client.py          # Gemini API wrapper with prompt caching
│   ├── logger.py              # Structured logging
│   └── guardrails.py          # Safety checks
├── tests/
│   ├── test_guardrails.py
│   ├── test_music_retriever.py
│   ├── test_emotion_parser.py
│   └── test_arc_planner.py
├── logs/                      # Auto-generated daily logs
└── assets/
    └── architecture.png
```
