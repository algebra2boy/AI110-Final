# Model Card — MoodArc

## System Overview

**System name:** MoodArc — AI Emotional Music Journey Planner  
**Base model:** Gemini Flash 4.5 (`gemini-1.5-flash`) via Google AI Studio  
**Task:** Multi-step agentic music recommendation with emotional arc planning  
**Base project:** AI110 Module 3 — Music Recommender Simulation

---

## Limitations and Biases

### Catalog bias
The 60-song catalog is hand-curated with significant recency and English-language bias. Songs are predominantly Western pop, rock, classical, and indie. Listeners who prefer K-pop, hip-hop, Latin, or world music will receive worse recommendations. The "energy" and "mood" labels are manually assigned, not derived from audio analysis, introducing subjectivity.

### Mood label reductiveness
Human emotional states are infinitely complex. Forcing them into ~20 mood categories (sad, anxious, hopeful, etc.) erases nuance. A person grieving a death and a person sad about a bad grade are both "sad" — but they need very different music. The system has no way to distinguish these.

### The ISO principle is not universal
Music therapy's ISO principle (start where the listener is) works for many people but not all. Some listeners explicitly want music that is emotionally opposite to their current state as a distraction strategy. The system forces the ISO approach regardless.

### Gemini's cultural defaults
Gemini may reflect biases from its training data when writing personalized notes — defaulting to Western cultural references, assuming certain experiences are universal, or using language that doesn't resonate across cultures or age groups.

### Intensity scoring is uncalibrated
The "intensity" field (0–1) is estimated by Gemini from natural language. There's no ground truth for whether a 0.8 intensity description is truly more intense than 0.6 — this is inherently subjective and uncalibrated.

---

## Potential Misuse and Prevention

**Risk 1: Someone in crisis receives music recommendations instead of help.**  
Mitigation: Keyword-based crisis detection in `guardrails.py` blocks processing and surfaces crisis hotline numbers (988, Crisis Text Line) before any music is shown.

**Risk 2: Manipulative use for emotional nudging.**  
A malicious actor could use the system to design music sequences that gradually shift a listener's mood toward increased anxiety, sadness, or susceptibility. Mitigation: The current system is user-initiated and single-session; there is no persistent profiling or automated delivery mechanism.

**Risk 3: Users treating AI music notes as professional mental health advice.**  
Mitigation: A disclaimer is shown at the bottom of every journey result: "MoodArc is not a mental health service."

**Risk 4: Over-reliance on AI-generated "therapeutic" explanations.**  
Gemini's personalized notes sound authoritative but are generated from pattern matching, not clinical assessment. Users should treat them as creative suggestions, not diagnoses.

---

## What Surprised Me About Reliability Testing

The biggest surprise was how often the arc planner initially **violated the ISO principle** despite being explicitly instructed to follow it. Early runs frequently started with hopeful or neutral songs even when the user described deep sadness — Gemini appeared to be optimizing for "helpfulness" (getting to positive music quickly) over therapeutic correctness.

Fix: The system prompt was revised to explicitly define the ISO principle and add a hard rule: `arc[0] MUST equal or closely match the current_mood`.

Second surprise: the evaluator agent was **more critical than expected** — it flagged weak transitions in 40% of test runs, which was actually useful for identifying catalog gaps (the system has very few "stressed" songs and several arc steps involving stress got poor song-fit scores).

Third surprise: short emotional descriptions ("I'm sad, cheer me up") produced dramatically worse arcs than detailed ones. The emotion parser had insufficient signal to infer meaningful themes or context, leading to generic 3-step arcs with no therapeutic nuance.

---

## AI Collaboration — What Helped and What Was Flawed

### Helpful
When designing the `ArcPlanner` system prompt, I asked Gemini to explain the ISO principle and how it should be operationalized in music therapy. The response was detailed and accurate, directly shaping the system prompt I wrote — in particular the rule that `arc[0]` must match the current mood. This was a case where AI expertise genuinely improved the system's therapeutic grounding.

### Flawed
During early testing, Gemini's evaluator consistently rated arcs as higher quality than they deserved — scores of 0.85+ even when the arc jumped illogically from "sad" directly to "euphoric" in three steps. This was a classic **sycophancy failure**: the evaluator seemed to give high scores for aesthetically pleasing narratives regardless of therapeutic logic.

This was partially mitigated by changing the evaluator prompt to ask Gemini to evaluate *each dimension separately with explicit criteria* before computing the overall score, rather than estimating the overall score first. But the issue was never fully eliminated — the evaluator still tends to rate higher on qualitative outputs, suggesting AI self-evaluation is useful but not fully reliable without human review.

---

## What This Project Taught Me About AI and Problem-Solving

Building MoodArc taught me that **the hardest part of applied AI is prompt engineering at the interface between steps** — not the code. The orchestrator code is simple; what required the most iteration was getting each Gemini step to reliably return parseable JSON with the right schema, and to respect therapeutic constraints it didn't naturally prioritize.

It also reinforced that **AI systems inherit the assumptions baked into their data and prompts**. My 60-song catalog reflects my musical taste and cultural context. My mood taxonomy reflects my vocabulary. Gemini's personalized notes reflect its training distribution. These are not neutral choices, and a more rigorous version of this system would involve diverse human reviewers at every layer.

Finally, I learned that **AI self-evaluation is a useful early warning system, not a replacement for human judgment**. The confidence scores caught genuine arc quality issues in testing — but they also missed others. The right use is: treat low confidence as a definite flag, but don't treat high confidence as a guarantee.

---

## Short Portfolio Reflection

*"What this project says about me as an AI engineer:"*

MoodArc shows that I can move from a functional prototype (Module 3's recommender) to a production-style system with real-world concerns: safety guardrails, structured logging, agent pipeline design, and honest evaluation. More importantly, I tried to build something that respects the person on the other end — not just technically correct, but therapeutically thoughtful and emotionally honest. That tension between "does it work?" and "does it do right by people?" is the one I want to keep wrestling with as an AI engineer.
