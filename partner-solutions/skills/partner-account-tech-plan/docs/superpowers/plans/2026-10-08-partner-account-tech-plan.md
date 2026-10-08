# partner-account-tech-plan — Implementation Plan

**Spec:** `docs/superpowers/specs/2026-10-08-partner-account-tech-plan-design.md`

## Build order

1. **Scaffold** the Tier 3 tree (done): `SKILL.md`, `refs/`, `refs/stages/`, `templates/`,
   `tests/`, `.githooks/`, `.github/workflows/`, `docs/superpowers/{specs,plans}/`.
2. **SKILL.md** — router: purpose, refusal conditions, tooling-resolution note, the 10-stage
   map (each as `refs/stages/stage-NN-*.md`), and the shared-ref index. Must link every stage
   file (R-TEST-03) and reference every shared ref + the template (R-ARCH-03).
3. **Shared refs:**
   - `orchestration.md` — how to dispatch each forge skill as a subagent; which run in
     parallel (profile/blocker/POV independent of each other once intake is done); context to
     pass; graceful degradation when a subagent is unavailable.
   - `v2mom-frame.md` — V2MOM structure, Measures-as-children-of-Methods, `[proposed]` KPIs.
   - `org62-case-scan.md` — reusable SOQL (RecordType IN Platform/App + Partner Program;
     scope AccountId; JSON for GROUP BY counts), deep-dive routing, data-safety gate.
   - `trust-posture.md` — elevation-not-encroachment overlay, stakeholder activation
     (single-thread risk), Bullhorn/nCino cross-pollination lessons.
   - `best-practice-frames.md` — CAF + AWS Well-Architected mapping, periodic re-review,
     living-plan discipline.
4. **Stage files (10):** 00 intake → 01 profile → 02 current-state → 03 blocker-scan →
   04 POV(+commercial/red-team/readiness) → 05 PoC → 06 workshop → 07 roadmap+gaps →
   08 governance → 09 assemble. Each self-contained; each references the shared refs it uses.
5. **Template:** `templates/account-tech-plan.md` — the composite plan with Theory-of-Growth
   at top, V2MOM frame, nested Measures, Gap-Closure matrix, governance, owners.
6. **tests/validate_skill.py** — assembled from check-library snippets for the Tier 3 IDs.
7. **README.md**, **.githooks/pre-commit**, **.github/workflows/validate.yml**.
8. **Self-validate** (`python3 tests/validate_skill.py`) — must be green.
9. **git init + first commit + activate hook.**
10. **Publish** `gh repo create partner-account-tech-plan --private --source . --remote origin --push`.

## Risks / watch-items

- Orphan/dangling refs break R-ARCH-03 / R-TEST-03 — every stage file must be linked from
  SKILL.md; every shared ref must be cited somewhere in the corpus.
- Keep stage files concise but self-contained (subagents execute them in isolation).
- Data-safety: live SR creds (seen in the Riskonnect dogfood) must never leave `.notes/`.
