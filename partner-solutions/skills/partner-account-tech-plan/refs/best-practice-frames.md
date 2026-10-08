# Best-practice frames — why the plan is structured this way

The plan borrows the parts of established account/architecture-planning frameworks that make a
technical account plan **actionable and living**, mapped onto the Salesforce V2MOM.

## Microsoft Cloud Adoption Framework (CAF)

CAF's lifecycle — **Strategy → Plan → Ready → Adopt → Govern → Secure → Manage** — maps to the
plan as:
- *Strategy* → Theory of Growth + V2MOM Vision/Values.
- *Plan* → Methods (workstreams) + the time-phased H0/H1/H2 roadmap (Stage 7).
- *Ready / Adopt* → PoC (Stage 5) + Enablement/workshop (Stage 6).
- *Govern / Secure / Manage* → Governance & Measures (Stage 8), run as **influence, not
  ownership** — the PAM/account team owns the RoB; we advise via ADRs and readiness reviews.

## AWS Well-Architected

Two signature moves adopted directly:
1. **Pillar-scored review** — the Current-State Assessment (Stage 2) scores the partner's
   architecture by pillar with a RAG rating, reusing `tech-strat-pov-forge` Stage 16. A score
   per pillar makes gaps concrete and comparable quarter over quarter.
2. **Periodic re-review** — the plan is **living, not point-in-time.** Set a re-review cadence
   (default: each QBR). On re-review, refresh the RAG, re-score gap closure, and append new
   blockers/consumption signals. This is what separates a plan from a one-time deck.

## The living-plan contract

A plan is only "living" if two things are true:
- There is a **cadence** (the governance RoB / QBR) at which it is re-reviewed, and
- There is a **movement metric** — the Go-Forward Gap-Closure KPI (# gaps moved
  🔴→🟡→🟢 per QBR, Stage 7). Without a movement metric, "living" is just a label.

Carry both into Stage 8 (Governance) and Stage 9 (assembly).
