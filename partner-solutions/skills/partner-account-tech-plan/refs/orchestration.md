# Orchestration — dispatching the forge family as subagents

This skill is an **orchestrator**. It never re-implements a forge skill; it dispatches each as
a subagent, passes the partner context, and synthesizes the returned artifact into the plan.

## The subagents it composes

| Capability | Skill invoked | Stage |
|------------|---------------|-------|
| Blocker diagnosis (claimed-vs-real, case-verified) | `partner-blocker-forge` | 3 |
| Tech Strategy POV | `tech-strat-pov-forge` | 4 |
| Commercial / consumption opportunities | `tech-strat-pov-forge` **Stage 18** | 4 |
| Red Team assessment | `tech-strat-pov-forge` **Stage 9** | 4 |
| Partner Readiness Scorecard | `tech-strat-pov-forge` **Stage 12** | 4 |
| Current-state architecture assessment | `tech-strat-pov-forge` **Stage 16** | 2 |
| Installable PoC package | `pie-poc-forge` | 5 |
| Enablement labs / kit | `workshop-forge` | 6 |

## Dispatch pattern

1. **Intake once (Stage 0), centrally.** Resolve partner, Org62 Account ID, Slack channels,
   PDF/notes, PAM, and tooling (Org62 alias, Slack MCP) before any fan-out. Every subagent
   inherits this context so none of them re-interrogates the user.
2. **Fan out the independent stages.** Profile (1), blocker scan (3), and the POV (4) do not
   depend on each other — run them as concurrent subagents. Current-state (2) can run with
   them. Pass each subagent the Stage-0 context block plus the specific lens it owns.
3. **Gate the dependent stages.** Roadmap + gap closure (7) consumes the gaps surfaced by
   assessment (2), blockers (3), and red team (4) — it runs *after* those return. Governance
   (8) and assembly (9) are last.
4. **One synthesis owner.** The orchestrator (not a subagent) writes the Theory of Growth,
   the V2MOM assembly, the gap-closure matrix, and the owners list — these require the whole
   picture.

## Context block passed to every subagent

- Partner name, Org62 Account ID, vertical, commercial model (ISVforce / OEM).
- The partner's own strategic frame if known (e.g. an "AI in Product/Practice/Platform"
  north star) so workstreams map to the partner's language.
- The trust/relationship posture (see `trust-posture.md`) — elevation-not-encroachment.
- Which Slack channels and background docs are authoritative.

## Graceful degradation

A subagent skill may be unavailable in a given runtime. **Never block the plan on it and never
re-implement it.** Instead:
- Note the section as `[section not generated — <skill> unavailable this run]` in the plan.
- Fill what the orchestrator can from research/Org62 directly, flagged with lower confidence.
- Record the gap so a later run can complete it (the plan is living — see `best-practice-frames.md`).

## Living, multi-session runs

Account plans accrete over quarters. When re-running against an existing plan, do not
regenerate from scratch — refresh the current-state RAG, re-score gap closure (how many moved
🔴→🟡→🟢), and append new blockers/consumption signals. The re-review cadence is defined in
`best-practice-frames.md`; the gap-closure KPI lives in `stage-07-roadmap-gaps.md`.
