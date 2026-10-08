---
name: partner-account-tech-plan
description: Use when you need a comprehensive technical account plan for a strategic ISV/OEM partner — orchestrates partner-blocker-forge, tech-strat-pov-forge (and its commercial/red-team/readiness/architecture stages), pie-poc-forge, and workshop-forge as subagents, adds a built-in Org62 case scan and a trust/relationship-posture overlay, and binds them into one living, V2MOM-framed Partner Account Tech Plan.
---

# partner-account-tech-plan

Assembles a **Partner Account Tech Plan** for a Tier-1 / strategic ISV or OEM partner. It
does not re-build the deliverable-forge family — it **orchestrates** the existing skills as
subagents and synthesizes their outputs into one coherent, executive-ready, *living* plan
framed as a Salesforce **V2MOM**, grounded in the partner's real Org62 support cases.

Output is one internal plan document (`templates/account-tech-plan.md`), optionally posted as
an internal Slack canvas. It leads with a **Theory of Growth** and closes every gap with a
named owner and horizon.

## Refusal conditions

Stop and clarify, or decline, when:
- **No named partner** — there is no account to plan. Ask for the partner name and (ideally)
  the Org62 Account ID.
- The request is for a **single deliverable** (just a POV, just a blocker diagnosis, just a
  PoC) — route the user straight to that forge skill; this orchestrator is for the *composite*
  account plan, and spinning up the full flow for one artifact is waste.
- The partner is **not a Salesforce ISV/OEM/platform partner** — this plans the *technical
  partnership*; it is not a generic customer account plan or a sales close plan.
- You **cannot confirm a load-bearing fact** (a case root cause, a consumption claim) from a
  primary source — flag it as an open item; do not assert it.
- Do **not** share any output before the data-safety gate: raw case captures and any live
  credentials go to gitignored `.notes/` only, and partner-facing versions are scrubbed first.
- Do **not** inflate blockers, accept the partner's crisis framing as fact, or claim the
  partnership is resourced without named owners per workstream.

## Inputs

Required: the **partner name**. Strongly preferred: the **Org62 Account ID** (enables the
case scan + consumption read), any **Slack deal channels**, a **background PDF / notes**, and
the **PAM** (owns forecast/pipeline). Missing pieces are flagged, not blocking — see
`refs/stages/stage-00-intake.md`.

## How it works

A 10-stage flow. Intake first; the independent research stages (profile, blocker scan, POV)
fan out as subagents in parallel; synthesis stages bind the results. Dispatch mechanics and
graceful degradation (when a subagent skill is unavailable) are in `refs/orchestration.md`.

| Stage | File | Produces |
|-------|------|----------|
| 0 — Intake & scope | `refs/stages/stage-00-intake.md` | partner/Org62/Slack/PAM captured; tooling resolved; scope gate |
| 1 — Profile & trust posture | `refs/stages/stage-01-profile.md` | profile + ICP + consumed-tech + stakeholder/power map + elevation posture |
| 2 — Current-state assessment | `refs/stages/stage-02-current-state.md` | pillar-scored RAG (living) |
| 3 — Blocker scan | `refs/stages/stage-03-blocker-scan.md` | Org62 case scan + blocker diagnoses |
| 4 — Tech Strategy POV (+commercial/red-team/readiness) | `refs/stages/stage-04-pov.md` | POV + consumption + red team + readiness scorecard |
| 5 — PoC opportunities (optional) | `refs/stages/stage-05-poc.md` | installable PoC package candidates |
| 6 — Enablement / workshop (optional) | `refs/stages/stage-06-workshop.md` | lab/kit plan |
| 7 — Roadmap & gap closure | `refs/stages/stage-07-roadmap-gaps.md` | H0/H1/H2 roadmap + Go-Forward Gap-Closure matrix |
| 8 — Governance & measures | `refs/stages/stage-08-governance.md` | RoB cadence, decision rights, joint KPIs (influence-not-own) |
| 9 — Assemble | `refs/stages/stage-09-assemble.md` | the V2MOM-framed plan document (+ optional canvas) |

## Shared references (load lazily, when a stage calls for it)

- `refs/orchestration.md` — subagent dispatch pattern, parallelism, context-passing, degradation.
- `refs/v2mom-frame.md` — the V2MOM top frame; **Measures are children of their Method**; `[proposed]` KPI tagging.
- `refs/org62-case-scan.md` — reusable case-scan SOQL + deep-dive routing + the data-safety gate.
- `refs/trust-posture.md` — elevation-not-encroachment overlay, stakeholder activation, Bullhorn/nCino lessons.
- `refs/best-practice-frames.md` — Microsoft CAF + AWS Well-Architected mapping; periodic re-review (living plan).

## Output

The composite internal plan from `templates/account-tech-plan.md`. A partner-facing version is
produced only on request, after the data-safety scrub.

## Validation

`python3 tests/validate_skill.py` (also run by `.githooks/pre-commit` and CI). Design + plan
archived under `docs/superpowers/specs/` and `docs/superpowers/plans/`.
