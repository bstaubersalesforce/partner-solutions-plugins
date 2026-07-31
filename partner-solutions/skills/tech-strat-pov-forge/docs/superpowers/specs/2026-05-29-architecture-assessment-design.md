# Technical & Architectural Assessment — Design Spec

**Date:** 2026-05-29
**Skill:** pov-builder
**Status:** Approved design, ready for implementation planning

## Summary

Add a **Technical & Architectural Assessment** as **Stage 16** of the pov-builder skill: a
comprehensive, build-guiding artifact that (a) evaluates the partner's current-state
architecture against the Salesforce **Well-Architected** framework, (b) prescribes the
target-state Salesforce architecture, and (c) emits a build-ready metadata blueprint plus
skeleton stubs concrete enough for Claude Code (or an engineer) to build from. It chains
into the existing **MVP Build Plan (Stage 8)** as an upstream feeder.

This is the second of three sequenced pov-builder improvements (the Discovery Framework /
Stage 15 shipped first; a parallel-instruction-files refactor is the third). It is a
downstream artifact built from an approved POV, alongside Stages 8–14.

## Goals

- Give the skill a constructive, build-guiding architecture artifact distinct from the
  adversarial Red Team (Stage 9), the visual Marketecture (Stage 14), the sprint-oriented
  MVP Build Plan (Stage 8), and the discovery-level Theme B of Stage 15.
- Anchor the current-state assessment on Salesforce Well-Architected (3 pillars, 8
  qualities) used as a "decision compass" with patterns / anti-patterns.
- Produce a target-state Salesforce architecture and a build-ready spec + stubs detailed
  enough to drive a build, then hand off to the MVP Build Plan.
- Serve a dual audience: an exec-readable readiness summary (Part 0) over a deep technical
  body (Parts 1–3) for architects and builders.
- Follow the skill's established conventions: lazy-loaded ref, MD+HTML template pipeline,
  validation checklist, validator parity checks, Stage 7 interactive review.

## Non-Goals

- The parallel-instruction-files performance refactor (separate, later effort).
- Replacing or absorbing the MVP Build Plan — the Assessment feeds it; Stage 8 stays the
  sprint/feature execution layer.
- Adversarial analysis — that remains the Red Team's job (the Assessment is constructive).
- Finished, runnable code — Part 3 produces signatures/scaffolding only, never business
  logic bodies.

## Source: Salesforce Well-Architected

Three pillars → eight qualities (used verbatim):
- **Trusted** (protect stakeholders): **Secure**, **Compliant**, **Reliable**
- **Easy** (deliver value fast): **Intentional**, **Automated**, **Engaging**
- **Adaptable** (evolve with the business): **Resilient**, **Composable**

The framework is a prescriptive "decision compass" using patterns / anti-patterns per
quality. Refs: architect.salesforce.com/docs/architect/well-architected/guide/overview.html
and the trusted/easy/adaptable overview pages.

## Document Structure (five parts)

**Header** — Partner, date, prepared by, associated POV/Discovery refs, overall
Well-Architected readiness score.

**Part 0 — Executive Readiness Summary** *(exec layer)*
- Well-Architected RAG table: the 8 qualities, each 🟢/🟡/🔴 + a one-line finding, with
  pillar rollups (Trusted / Easy / Adaptable).
- Top 3 technical risks (each tied to a quality + severity).
- Build-readiness verdict: go / conditional-go / not-ready signal for proceeding to build.

**Part 1 — Current-State Assessment** *(spine = Well-Architected)*
One block per pillar; per quality: **Finding** (what the current architecture does) ·
**Evidence** (from POV/Discovery/research, confidence-labeled) · **Pattern / Anti-pattern**
(named, compass language) · **Gap** (what's missing for Salesforce-grade). Evidence-free →
`[TBD]` with a "what to confirm" note. Never invent.

**Part 2 — Target-State Architecture** *(seven layers)*
1. App type & packaging (managed package / namespace strategy)
2. Data architecture (model approach, standard vs. custom, large-data/Data Cloud)
3. Integration architecture (named APIs, auth, sync/async patterns, middleware)
4. Component architecture (LWC / Apex / Flow division of responsibility)
5. Security & sharing model (perm sets, sharing, data protection)
6. Scale & multi-tenancy / governor-limit strategy
7. AI & data layer (Agentforce / Einstein / Data Cloud where applicable)
Name concrete SF capabilities; `[TBD]` where the POV under-specifies.

**Part 3 — Build-Ready Spec & Stubs** *(the Claude-Code-buildable layer; Markdown is the
source of truth)*
- **Metadata blueprint**: custom objects → fields (API name, type, description) →
  relationships (table + ERD block); standard objects reused are named, not redefined.
- **Component inventory**: each LWC / Apex class / Flow with a one-line responsibility and
  the use case/quality it serves.
- **Integration contracts**: per external system — named API, auth method, sync/async, the
  SF-side mechanism (e.g., Named Credential + External Service, Platform Event), data
  exchanged.
- **Skeleton stubs**: fenced code blocks — Apex class + method signatures with doc-comment
  intent (no bodies; bodies are `// TODO (build): …`), LWC component shells (`@api` props +
  skeleton template), declarative object/field definitions. Every stub carries a header
  `// STUB — scaffolding from Architecture Assessment; flesh out in build`.

**Part 4 — Gap-Closing Roadmap → MVP Build Plan handoff**
Prioritized remediation + build sequence, each item mapped to the quality it closes, with
an explicit "feeds Stage 8 MVP Build Plan" handshake (current-state gaps → build tasks).

**Confidence & Assumptions** — score, named assumptions, open TBDs.

## Build-Stub Guardrails

- **Traceability**: every object/field/class/Flow traces to a named POV use case or a Part
  2 decision (a Traceability column/note). If it can't be traced, no stub is emitted.
- **Scaffolding only**: signatures and shells, never fabricated business-logic bodies or
  invented algorithms.
- **Under-specification**: emit `[TBD — confirm in build]` rather than guessing.

## Integration & Invocation

- **New lazy ref**: `refs/architecture-assessment.md` (full Stage 16 definition). Base
  `SKILL.md` stays lean.
- **Stage 16**, registered in `refs/output-stages.md` (title becomes "8–16").
- **Output-menu restructure into three questions** (tool caps at 4 options/question; the
  current 2 questions are both full):
  - Q1 "Analysis & Readiness": MVP Build Plan · Red Team · Partner Readiness Scorecard ·
    Discovery Framework
  - Q2 "Architecture & Build": Technical & Architectural Assessment · Marketecture
    (Marketecture moves here — both are architecture)
  - Q3 "Presentation / Package": All outputs + home page · Investor Presentation · Solution
    Infographic
- **Inputs**: the POV (required) + Discovery **Theme B** if it was run + targeted research.
  If the POV's technical sections are thin and no Discovery exists, pull from the
  `discovery-questions.md` *Technical Assessment* block and flag `[TBD]`s.
- **"All outputs + home page" includes the Assessment** (it is a downstream artifact, unlike
  upstream Discovery). **Sequencing**: because the Assessment feeds the MVP Build Plan, when
  both run the **Assessment runs before Stage 8**.
- **Anytime/standalone**: invokable from the menu or by direct request; chains into Stage 8
  via its Part 4 handoff.
- **Requires a POV**: if none exists, point the user to build one first; otherwise proceed,
  surfacing `[TBD]`s under thin input. No other refusal conditions.

## Process Logic

1. **Load inputs** — approved POV (always; esp. "Partner App Strategy & Technical Summary,"
   "MVP & Development Priorities," architecture sections); Discovery Theme B if present;
   `refs/architecture-assessment.md` for the method.
2. **Targeted technical research** — fill gaps (current stack, named integration systems,
   public API/security signals, scale indicators). Status line per action; failed fetches
   noted and skipped.
3. **Current-state assessment (Part 1)** — walk the 8 qualities; per quality: finding +
   confidence-labeled evidence + pattern/anti-pattern + gap; `[TBD]` where no evidence.
4. **Score the RAG (Part 0)** — derive each quality's RAG **from the Part 1 findings** (not
   guessed), roll up to pillars, surface top 3 risks + build-readiness verdict.
5. **Design target state (Part 2)** — map POV use cases/solution/KPIs onto the seven SF
   architecture layers; `[TBD]` where under-specified.
6. **Generate build-ready spec & stubs (Part 3)** — enumerate metadata blueprint + emit
   traceable skeleton stubs (signatures/shells only).
7. **Roadmap + handoff (Part 4)** — sequence gap-closing work, map to qualities, frame the
   Stage 8 handshake.

**Delivery follows the Stage 7 Interactive Review process** (present Markdown draft → review
loop → on Approve, run the checklist then fill the HTML).

**Core rule: every finding, score, target decision, and stub traces to evidence or is marked
`[TBD]` — never invented.**

## MD vs HTML

- **Markdown** is the primary build-consumable form and the source of truth for Part 3
  (fenced stubs + tables read directly by Claude Code / engineers).
- **HTML** is the shareable view: Well-Architected RAG grid (3 pillars × qualities),
  target-architecture layer cards, roadmap, and Part 3 as read-only syntax-styled `<pre>`
  blocks (same stub text injected by the fill script, not re-typed). Reuses the shared
  Salesforce-palette CSS.

## Files

**New**
- `refs/architecture-assessment.md` — full Stage 16 definition (lazy-loaded).
- `templates/technical-architecture-assessment.md` — Markdown output (Header + Parts 0–4 +
  Confidence).
- `templates/technical-architecture-assessment.html` — HTML render (RAG grid, layer cards,
  roadmap, read-only `<pre>` stubs), `{{TOKEN}}` + fill-script pipeline.
- `validation/architecture-checklist.md` — delivery contract.

**Edited**
- `refs/output-stages.md` — register Stage 16; title → "8–16".
- `SKILL.md` — restructure output menu into 3 questions; add Stage 16 to the lazy-load
  pointer ("Stages 8–16") and stage index; add run-before-Stage-8 sequencing; include Stage
  16 in "All outputs."
- `tests/validate_skill.py` — Stage 16 parity checks (below).

**Naming**: `architecture-assessment` (ref), `technical-architecture-assessment.{md,html}`
(templates), `architecture-checklist.md` (validation).

## Validation Contract (`architecture-checklist.md`)

- All 8 Well-Architected qualities present in Part 1 and in the Part 0 RAG; pillar rollups
  present.
- Every RAG rating traces to a Part 1 finding (no orphan scores).
- Every Part 3 metadata artifact/stub has a traceability link to a use case or Part 2
  decision; stubs are signatures/scaffolding only (no business-logic bodies).
- Build-readiness verdict present; Part 4 handoff to Stage 8 present.
- No invented facts — evidence-labeled or `[TBD]`.

## Structural Tests (`tests/validate_skill.py`)

- Stage contiguity bumped to **1..16**.
- New files exist and are non-orphaned (ref, both templates, checklist).
- Add `technical-architecture-assessment.html` to `TEMPLATE_HTML` (brace + token checks
  auto-apply).
- `WELL_ARCHITECTED_QUALITIES` constant (the 8 qualities) asserted present across
  `refs/architecture-assessment.md`, the MD template, and the checklist; the 3 pillar names
  present too.
- Menu parity: menu offers "Technical & Architectural Assessment" and cites `(Stage 16)`;
  `(Stage 16)` resolves to a real stage; the existing "All outputs + home page" and
  "Discovery Framework" menu checks still pass after the 3-question regrouping.
- RAG token family: the HTML carries the RAG status tokens for the 8 qualities.

Pre-commit hook + CI run the validator, so these gate every commit.

## Behavioral Testing (required during implementation)

Per the writing-skills discipline, structural validation is not enough. Implementation MUST
include subagent pressure scenarios verifying an agent:
- derives the RAG strictly from Part 1 findings (no orphan scores);
- emits stubs as signatures/scaffolding with traceability and NO fabricated business logic;
- proceeds under thin POV input with honest `[TBD]`s and no invented metadata;
- produces the Stage 8 handoff;
- and (integration) that "All outputs" runs the Assessment before the MVP Build Plan.

## Open Decisions (defer to planning)

1. Whether the menu regrouping keeps exactly the labels above or tweaks wording for clarity
   once rendered (confirm during planning).
2. Exact RAG token naming in the HTML (align with the scorecard's existing `rag-*` class
   convention).

## Future Alignment (out of scope here)

- The parallel-instruction-files refactor (idea 3) can later treat the seven
  target-architecture layers and/or the assessment phases as parallel units.
