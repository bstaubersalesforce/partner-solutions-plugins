# partner-account-tech-plan — Design Spec

**Date:** 2026-10-08
**Status:** Built (dogfood-proven before authoring — Riskonnect, internal canvas F0C7D2GD119)
**Tier:** 3 (Platform) — multi-stage router, subagent orchestration, multiple distinct artifacts

## Intended outcome

A single orchestrator skill that assembles a **Partner Account Tech Plan** for a Tier-1 /
strategic ISV or OEM partner. It does not re-implement the deliverable-forge family — it
**composes** the existing skills as subagents and binds their outputs into one coherent,
executive-ready, *living* plan framed as a Salesforce **V2MOM**.

Who it is for: a Salesforce PIE / PS technical strategist (e.g. Brandon) who owns the
technical relationship with a strategic partner and needs one plan that a PAM, an account
team, and partner executives can all act from — grounded in the partner's real support
cases, not just narrative.

Success looks like: one run produces a plan whose every workstream carries nested KPIs
(Measures as children of Methods), whose gaps are each mapped to a closure action with an
owner and horizon, and whose evidence (blockers, consumption, red-team) is case-grounded
and source-attributed — ready to post as an internal canvas and re-reviewed each QBR.

## Why orchestration, not a monolith

The parts already exist and are independently maintained:
- `partner-blocker-forge` — adversarial claimed-vs-real blocker diagnosis + Org62 case verification.
- `tech-strat-pov-forge` — the POV against the OG Tech Strategy Framework, plus downstream
  stages: **Stage 18** Consumption/Commercial, **Stage 9** Red Team, **Stage 12** Readiness
  Scorecard, **Stage 16** Architecture Assessment, **Stage 14** Marketecture, etc.
- `pie-poc-forge` — installable PoC SFDX packages.
- `workshop-forge` — enablement labs/kits.

Re-implementing any of these would fork maintenance and drift from their validation suites.
The orchestrator's job is **sequencing, context-passing, and synthesis** — plus two things
none of the subagents own: a built-in Org62 **case scan** scoped to the partner Account, and
a **trust/relationship-posture overlay** (elevation-not-encroachment; stakeholder activation).

## Framing decisions (load-bearing)

1. **Top frame = V2MOM** (Vision · Values · Methods · Obstacles · Measures). Convention:
   **Measures are CHILDREN of their Method** — each Method/workstream carries its own KPIs
   nested beneath it. Only cross-cutting measures (partnership health) sit at the top-level
   Measures line. Propose KPIs tagged `[proposed]` where partner baselines are absent.
2. **Theory of Growth at the very top** — a short summary of where the partnership is going
   and its potential, before the V2MOM. This is the executive hook.
3. **Current-State Assessment is Well-Architected-style** (pillar-scored RAG) and the plan is
   **living** — a periodic re-review cadence, not a point-in-time artifact.
4. **Go-Forward Plan — Closing the Gaps** is a first-class element: a
   gap → closure-action → owner → horizon matrix mapping every Assessment / Blocker /
   Red-Team gap to how it closes. Closure KPI = # gaps moved RAG 🔴→🟡→🟢 per QBR.
5. **Governance = INFLUENCE, not OWN.** The PAM / account team owns the RoB; PIE/PS is the
   technical advisor (ADRs, upgrade/enforcement-readiness reviews, re-review rhythm).
6. **Data-safety gate inherited from partner-blocker-forge** — raw case captures and any live
   credentials go to gitignored `.notes/` only; nothing shareable ships unscrubbed.

## Plan sections → source

| # | Section | Fed by |
|---|---------|--------|
| 0 | Theory of Growth (summary) | orchestrator synthesis |
| 1 | Partner profile + ICP + consumed-tech + trust posture + stakeholder/power map | research + Org62 + trust overlay |
| 2 | Current-State Assessment (pillar-scored RAG, living) | pov-forge Stage 16 |
| 3 | Blocker Assessment | partner-blocker-forge + built-in Org62 case scan |
| 4 | Tech Strategy POV (problem/vision/solution/workstreams/architecture) | tech-strat-pov-forge |
| 5 | Commercial / Consumption Opportunities | pov-forge Stage 18 |
| 6 | Red Team Assessment | pov-forge Stage 9 |
| 7 | Partner Readiness Scorecard | pov-forge Stage 12 |
| 8 | PoC opportunities (optional) | pie-poc-forge |
| 9 | Enablement / Workshop (optional) | workshop-forge |
| 10 | Time-phased Roadmap (H0/H1/H2) + Go-Forward Gap-Closure matrix | orchestrator synthesis |
| 11 | Governance & Measures (influence-not-own) | orchestrator synthesis |
| 12 | V2MOM assembly + owners + next steps | orchestrator synthesis |

## Architecture

- **Router:** `SKILL.md` routes to `refs/stages/stage-NN-*.md` (10 stages). Each stage is
  self-contained so a subagent executing it has its instructions without the whole skill.
- **Shared refs** (lazy): `orchestration.md` (subagent dispatch + parallelism), `v2mom-frame.md`,
  `org62-case-scan.md`, `trust-posture.md`, `best-practice-frames.md`.
- **One template:** `templates/account-tech-plan.md` — the composite plan document.
- **No `scripts/`** — orchestrator is prompt+ref driven; R-TEST-04 is n-a.

## Non-goals

- Not a replacement for any forge skill — if a subagent is unavailable, the stage degrades
  gracefully (notes the gap) rather than re-implementing it.
- Not a CRM writer — read-only against Org62; the PAM owns forecast/pipeline records.
- Not an engagement tracker — it produces a plan; living-ness is the re-review cadence, not
  a ticketing loop.

## Validation

Tier 3 rubric IDs with checks: R-FM-01, R-REF-01, R-ARCH-01/02/03, R-TEST-01/02/03/04(n-a),
R-CI-01/02, R-PROC-01, R-DOC-01. `python3 tests/validate_skill.py` must be green; enforced by
`.githooks/pre-commit` and CI.
