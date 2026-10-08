# Stage 2 — Current-state assessment

A **pillar-scored RAG** read of the partner's current technical state — the baseline every gap
is measured against. This is a Well-Architected-style move; see `../best-practice-frames.md`.

## How
Dispatch `tech-strat-pov-forge` **Stage 16** (architecture assessment) as a subagent with the
Stage-0 context. Score by pillar (architecture, packaging/distribution, data, security/trust,
operations/enablement — adapt to the partner) with a 🔴/🟡/🟢 rating and a one-line rationale
each.

## Make it living
Record the assessment **date** and a **re-review cadence** (default: each QBR). On a re-run,
refresh the RAG rather than regenerating — the deltas are the story. The movement metric lives
in the gap-closure matrix (`stage-07-roadmap-gaps.md`).

## Hand-off
Every 🔴/🟡 pillar becomes a candidate **Obstacle** in the V2MOM and a row in the Go-Forward
Gap-Closure matrix. Pass the scored pillars to Stage 7.
