# PIE Engagement Decks — Kickoff (11) + Engagement Review (12)

Produces the `11-kickoff-deck` and `12-engagement-review-deck` canvas artifacts. These mirror the official PIE deck templates (`PIE-Partner Kickoff [TEMPLATE].pdf`, `PIE-Partner Engagement Review [TEMPLATE].pdf` — partner-supplied, in the downloads folder). The artifacts are slide-by-slide content outlines a PIE can paste into the branded decks.

> **Voice:** where a slide IS sourced, write its prose in the **Delivery Voice** (SKILL.md) — lead with the point, quantify or qualify, no hedging. The source-or-pending rule below WINS over the voice: never fabricate or "advisor-ify" an uncovered slide into a confident claim — mark it `[Pending]`.

## Source-or-pending rule (STRICT — straight facts only)
- Populate a slide ONLY from the POV, MVP build plan, gaps document, or Technical & Architectural Assessment actually provided.
- Where the input does not cover a slide, emit `[Pending — <exactly what input is needed> — owner: <role>]`. Do NOT invent content, metrics, names, dates, or results.
- Where the build gives partial signal, provide **guidance** (what to fill in and from where) rather than a fabricated value, e.g. "Guidance: pull the measured cycle-time delta from the pilot; POV target is ≥35%."
- **Never present a POV target as a proven/measured result.** On the Engagement Review "Proven Business Outcomes" slide, an unmeasured KPI is the POV *target* + `[Pending measurement]`.

## Kickoff deck (11) — slide sourcing
- PIE Team / Points of Contact / Team / Meetings → `[Pending — name+title+roster — owner: PIE lead]` unless provided.
- Program Overview / Approach / Expectations → static PIE program content (not partner-specific); keep verbatim.
- Partnership Vision → POV Vision/Solution Statement.
- Primary Use Cases → POV use cases / build plan features (target 3).
- Appendix Risks & Blockers → build plan Risks + gaps (Description/Impact/Mitigation/Priority/Date/Due).
- Appendix Sample Timeline → build plan Phase Plan (workstream · status · phased activities).
- Appendix Agentforce Readiness Review → map build/gaps to Organization / Process / Technical; `[Pending]` per uncovered line.

## Engagement Review deck (12) — slide sourcing
- Innovation Team → `[Pending — roster — owner: PIE lead]` unless provided.
- Value Thesis → POV Vision/Solution Statement (2–3 sentences).
- Solution POC Demo → engagement artifact (video/screenshot/link); `[Pending — demo asset — owner: PIE pod]`.
- Proven Business Outcomes → POV KPIs; unmeasured → target + `[Pending measurement]`.
- Solution Architecture & "The Moat" → Core Tech (build plan), Innovation Highlights (what's unique), Deployment Readiness (G/Y/R + narrative).
- 30-60-90 Day Plan → build plan Phase Plan + Next Steps + gaps, bucketed.
- Innovation Signal: Technical Readiness & Gaps → gaps document → Resource Gap / Infrastructure / Feature Requests.
- Next Steps → build plan Next Steps + standard PIE close (CSAT/NPS, success story).

## Rendering
Both render via the standard recipe in `refs/workflow-dispatch.md` (skill-filled body tokens → `md-to-html.py` → `ensure-home-link.py`). They are content outlines, not the branded slides themselves; the PIE transfers the content into the official PDF/Slides template.
