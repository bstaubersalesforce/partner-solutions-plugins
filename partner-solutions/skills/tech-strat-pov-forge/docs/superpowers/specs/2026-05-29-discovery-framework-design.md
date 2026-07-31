# Discovery Framework — Design Spec

**Date:** 2026-05-29
**Skill:** pov-builder
**Status:** Approved design, ready for implementation planning

## Summary

Add an optional **Discovery Framework** to the pov-builder skill: a hybrid discovery
instrument that researches and pre-fills structured discovery dimensions, reframes gaps
as design-thinking *How Might We* statements, renders a Strategyzer **Value Proposition
Canvas** and **Business Model Canvas**, and produces a **Discovery Document** that feeds
richer input into the POV.

It is invokable two ways:
- **Intake fork** at Stage 1 — Quick POV (current lean flow, the default) vs. Full
  Discovery (run the framework first, then feed the POV).
- **Anytime** — via the post-POV output menu, or a direct request, including with no POV
  present at all.

It becomes **Stage 15** in the skill's stage model.

This is the first of three sequenced improvements. The other two (a downstream Technical &
Architectural Assessment artifact, and a parallel-instruction-files performance refactor)
get their own spec → plan → build cycles later. The Discovery Framework's three themes are
designed to become natural parallelization units for that future refactor.

## Goals

- Provide a deeper, structured discovery capability without compromising the skill's lean
  default flow (2 inputs → research → pre-fill → ≤5 questions).
- Produce a Discovery Document that is simultaneously an internal synthesis and a
  partner-facing discovery-call agenda.
- Feed discovery findings cleanly into the POV (pre-fill on the full path; diff-and-apply
  when a POV already exists).
- Follow existing skill conventions exactly: lazy-loaded refs, MD+HTML template pipeline,
  validation checklist, validator parity checks.

## Non-Goals

- The Technical & Architectural Assessment artifact (separate, later effort).
- The parallel-instruction-files refactor (separate, later effort).
- Replacing `scripts/discovery-questions.md` — it stays as the reactive, POV-section-axis
  gap filler and coexists with the new dimensional-axis framework.
- Adversarial competitive analysis — that remains the Red Team artifact's job. Discovery
  only surfaces the raw competitive landscape.

## Document Structure

The Discovery Document has four parts.

**Header** — Partner, date, prepared by, discovery confidence score, link to associated POV
(if any).

**Part I — Discovery Dimensions (10, across 3 themes).** Each dimension carries a
consistent three-block shape:
- **What we know** — research pre-filled, with confidence labels (`[confirmed]` /
  `[proposed — confirm]` / `[TBD]`), reusing the skill's existing labeling convention.
- **How Might We…** — 1–3 design-thinking reframes turning the dimension's friction/gaps
  into opportunity statements (reframes, not solutions).
- **What to ask** — targeted discovery-call questions for the remaining gaps
  (partner-facing half).

Themes and dimensions:

*Theme A — Customer & Value* (feeds the Value Proposition Canvas)
1. Users, Personas & Journeys
2. Operational Process Flows
3. Pain & Friction Points
4. Success Metrics & Desired Outcomes

*Theme B — Technical Readiness* (feeds the future Architectural Assessment)
5. Technical Architecture & Readiness (current + planned)
6. Salesforce Ecosystem Footprint
7. Data Landscape & Sources

*Theme C — Business & Commercial* (feeds the Business Model Canvas)
8. Business Alignment
9. Decision-Making & Stakeholders
10. Competitive Landscape & Alternatives — what customers use today and why, named
    alternatives, switching costs/lock-in, "why us over [named alternative]." Draws from
    the existing `discovery-questions.md` *Risks & Competitive Threats* block; feeds POV
    differentiation checks and the Red Team without duplicating adversarial work.

**Part II — Synthesis Canvases**
- **Value Proposition Canvas** — customer jobs / pains / gains ↔ products & services / pain
  relievers / gain creators. Drawn from Theme A.
- **Business Model Canvas** — the 9 blocks. Drawn mainly from Theme C, cross-referencing
  A and B.
- Any block with no evidence is marked `[TBD]`, never invented.

**Part III — Opportunity Backlog** — HMW statements from all dimensions, consolidated and
ranked by impact × evidence. Feeds the POV's Problem Space / Vision / Use Cases.

**Part IV — POV Feed & Open Gaps** — explicit mapping of discovery findings → POV sections,
plus the open-question list with named owners (the "feeds the POV" handshake).

## Integration & Invocation

- **New lazy ref:** `refs/discovery-framework.md` holds the full Stage 15 definition
  (process logic, the 10 dimensions with dimension-specific prompts, HMW method, VPC/BMC
  construction rules). Lazily loaded like `refs/output-stages.md`; base `SKILL.md` stays
  lean.
- **Intake fork (Stage 1):** add a single early branch — Quick POV vs. Full Discovery.
  Default is Quick if the user just provides name + URL.
- **Anytime invocation:** add **Discovery Framework** to the post-POV output menu
  (`AskUserQuestion`), and honor a direct request ("run discovery for X") with no POV
  present.
- **Stage number:** Stage 15 (current stages end at 14), registered in
  `refs/output-stages.md` with the intake hook in `SKILL.md` pointing to it.
- **Output-menu refinement:** move **"All outputs + home page"** to the **first position**
  in the Package question so it reads as the default expectation; confirm wording so the
  "supersedes individual selections" note still reads clearly when on top.
- **Discovery is NOT part of "All outputs."** "All outputs" builds downstream *artifacts*
  (decks, infographic, marketecture, home page); Discovery is an upstream *refinement* pass
  that changes the POV itself. It gets its own menu entry.

## Process Logic

When invoked (either path):

1. **Research sweep** — reuse Stage 1's research engine (URL fetch + targeted searches),
   extended with discovery-oriented queries (org structure, named systems, public
   process/tooling signals). Lazy-load the matched `refs/verticals/` file for
   industry-specific process flows, KPIs, and regulatory drivers.
2. **Pre-fill dimensions** — populate every dimension's *What we know* block from research,
   each line carrying a confidence label.
3. **HMW synthesis** — per dimension, convert friction/gaps into 1–3 *How Might We*
   statements.
4. **Build canvases** — assemble the VPC from Theme A and the BMC from Theme C
   (cross-referencing B). Evidence-free blocks → `[TBD]`, never invented.
5. **Gap questions** — populate each dimension's *What to ask* block with only the
   still-missing questions. Cross-reference `scripts/discovery-questions.md` to reuse
   existing wording rather than duplicating.
6. **Rank the Opportunity Backlog** — consolidate and rank HMW statements by
   impact × evidence.
7. **POV handshake (Part IV):**
   - **Full Discovery path:** pre-fills flow into Stage 2 — the POV starts populated, with
     fewer Stage 3 questions.
   - **Anytime path, POV exists:** present findings as a *diff* (confirms / contradicts /
     adds) and offer to apply.
   - **Anytime path, no POV:** deliver the Discovery Document standalone; offer to start a
     POV from it.

**Error handling:** failed fetches/searches noted inline and skipped (existing
convention). A dimension with zero research evidence still renders — fully `[TBD]` with its
*What to ask* block — so the document is always a usable call agenda even with thin
research. **No refusal conditions** (unlike the POV): discovery is legitimately the
*pre-discovery* step.

**Core rule: always renders, never invents.**

## Files

**New**
- `refs/discovery-framework.md` — full Stage 15 definition (lazy-loaded).
- `templates/discovery-document.md` — Markdown output template (header + Parts I–IV;
  text-form VPC + BMC).
- `templates/discovery-document.html` — HTML render with the two canvases as visual grids
  (VPC two-panel; BMC 9-block), using the existing `{{TOKEN}}` + fill-script pipeline.
- `validation/discovery-checklist.md` — delivery contract.

**Edited**
- `SKILL.md` — Stage 1 intake fork; add Discovery Framework to the output menu; reorder
  "All outputs + home page" to first in the Package question.
- `refs/output-stages.md` — register Stage 15. (Open planning choice: full text in
  `output-stages.md` vs. its own `discovery-framework.md` — pick the cheaper token option.)
- `scripts/discovery-questions.md` — light cross-reference note linking the two axes (no
  content duplication).

**Naming:** `discovery-framework` / `discovery-document` / `discovery-checklist`,
consistent with existing kebab-case artifact naming.

## Validation Contract (`validation/discovery-checklist.md`)

- All 10 dimensions present.
- Every canvas block evidence-backed or explicitly `[TBD]` — none invented.
- Every `[TBD]` line has a corresponding *What to ask* entry.
- HMW statements are reframes, not solutions.
- Part IV POV-mapping present.

## Structural Tests (`tests/validate_skill.py`, currently 18 checks)

Extend the suite so the new files are first-class:
- New files exist and aren't orphaned: `refs/discovery-framework.md`,
  `templates/discovery-document.{md,html}`, `validation/discovery-checklist.md`.
- **Token parity:** every `{{TOKEN}}` in `discovery-document.html` is documented/fillable
  (same pattern as other HTML templates).
- **Dimension parity:** the 10 dimension headings are consistent across
  `refs/discovery-framework.md`, the MD template, and the checklist (mirrors the existing
  `VERTICAL_HEADINGS` schema check).
- **Menu parity:** Stage 15 / Discovery appears in the `SKILL.md` output menu and is
  registered in `refs/output-stages.md`.

Pre-commit hook + CI already run `validate_skill.py`, so the new checks gate commits
automatically — no hook changes needed.

## Behavioral Testing (required during implementation)

Per the writing-skills discipline, structural validation is not enough. Implementation MUST
include subagent pressure scenarios verifying an agent actually:
- Takes the intake fork correctly (defaults to Quick; runs Full Discovery when chosen).
- Pre-fills dimensions with honest confidence labels and never invents canvas blocks.
- Produces HMW reframes (not solutions).
- Executes all three POV-handshake variants correctly.
- Renders a usable document even under thin/failed research.

## Open Decisions (defer to planning)

1. Stage 15 full text location: inline in `refs/output-stages.md` vs. dedicated
   `refs/discovery-framework.md` (token-cost tradeoff). Leaning dedicated file for lean
   base context.
2. Exact wording of the reordered output menu so the "supersedes" note stays clear on top.

## Future Alignment (out of scope here)

- The three themes are designed as the parallelization units for the later
  parallel-instruction-files refactor (idea 3).
- Theme B (Technical Readiness) is the primary upstream feed for the later Technical &
  Architectural Assessment artifact (idea 1).
