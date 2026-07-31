# Consumption Opportunities Artifact + Product Strategy — Design Spec

**Date:** 2026-05-30
**Status:** Approved (brainstorming)
**Skill:** pov-builder

## Overview

Two independent features shipped in one spec:

- **Feature A — Consumption Opportunities artifact (new Stage 18).** A build-oriented opportunity map showing where Agentforce agents, Data Cloud, and other Salesforce SKUs grow consumption on the partner's solution, with named-component build blueprints per opportunity. Dual-format (`.md` + own styled `.html`). Produced in every "All outputs" package (Wave 1) and available as a standalone pick.
- **Feature B — Product Strategy.** A new POV section (after Vision, before Solution) plus two slides in the POV Presentation deck (after the Vision slide).

The two features are independent: A is a new artifact; B edits the core POV template and the POV Presentation. They share one spec, plan, and branch.

---

## Feature A — Consumption Opportunities (Stage 18)

### Purpose & boundaries

A **consumption-growth-scoped, build-oriented** artifact. It identifies where to grow consumption (agents, data, other SKUs) on this partner's solution and gives named-component build blueprints to start each. It is **independent** — stands alone, may run without Stage 16.

**Anti-overlap guard (must be stated in the instructions):**
- Not the core-solution architecture — that is Stage 16 (Technical & Architectural Assessment). This artifact covers only agent/data/SKU *consumption-growth* opportunities.
- Not the license pull-through commercial model — that is the POV's ISV Commercial Model section + `refs/pull-through-gtm.md`.
- Not Flex Credit dollar sizing — that is the `sf-flex-estimator` skill. This artifact gives a qualitative "consumption signal" per opportunity and points to `sf-flex-estimator` for cost modeling.

### Document structure (both `.md` and `.html`)

1. **Header** — partner name, date, Org62 stage, "Built on Salesforce" badge, standardized home-page back-link pill (`{{HOME_HREF}}`).
2. **Consumption Opportunity Map (ranked table)** — every opportunity in one table:
   `# | Opportunity | Type (Agent / Data / SKU) | Value driver | Priority (H/M/L) | Consumption signal`
   "Consumption signal" is a one-phrase qualitative note (e.g., "high-volume inference", "large external data ingest") — never a dollar figure.
3. **Agentforce Agents** — 2–4 opportunities. Each is a named-component blueprint: agent purpose/trigger; **topics & actions**; **objects it reads/writes**; supporting **Flow / Apex / prompt** components; 3–5 build steps. Confidence-labeled (`[confirmed]` / `[proposed — confirm]` / `[TBD]`).
4. **Data Cloud** — 2–4 opportunities. Each: purpose/value; **DMOs / data streams / source objects**; mapping & identity-resolution notes; activation target; 3–5 build steps. Confidence-labeled.
5. **Other Salesforce SKU Opportunities** — table:
   `SKU / Capability | Trigger in this solution | Value | Resellable by partner? (Y/N/TBD)`
   Covers Shield, Backup & Archive, sandboxes, and other partner-resellable products/capabilities.
6. **Footer note** — pointer to `sf-flex-estimator` for Flex Credit cost sizing, and to Stage 16 for deeper core-solution architecture.

### Files (Feature A)

- **New:** `refs/stages/stage-18-consumption-opportunities.md` (instructions, with the `**Stage 18 —` heading), `templates/consumption-opportunities.md`, `templates/consumption-opportunities.html` (own styled template, standardized back-link pill, token glossary), `validation/consumption-checklist.md`.

### Dispatch, filename, home page (Feature A)

- **Filename (Stage 13 convention):** `{SLUG}-consumption-opportunities.md` + `{SLUG}-consumption-opportunities.html`.
- **Dispatch:** Stage 18 joins **Wave 1** of `refs/parallel-dispatch.md` (independent; needs only the approved POV). Threshold-count list adds 18. Its subagent brief runs non-interactively (produce `.md` + `.html` in one pass).
- **Home page (Stage 13):** new **"Consumption"** card (View ↗ + Markdown ↓), placed last in card order: POV, Presentation, Discovery, Build, Risk, Sales, Visual, Readiness, Architecture, **Consumption**.

---

## Feature B — Product Strategy

### POV section (`templates/pov-output.md`)

Inserted **after Vision, before Solution Description**. Marked `[REQUIRED if known]` (not hard-required — a thin POV still validates; consistent with Solution Alignment / MVP gating). It is **not** added to the Stage 6 contract checklist's hard-required-sections list.

```
## Product Strategy [REQUIRED if known]

**Strategic Thesis:** [Where the product is heading and why now — 2-3 sentences. Governing direction, not a feature list.]

**Product Pillars:** [3-4 capability themes the product is built around, each with the strategic bet behind it and a rough now/next/later.]

**Market Positioning:** [Competitive positioning, target-segment strategy, and pricing/packaging direction.]

**Horizon Sequencing to Moat:** [How the pillars sequence across horizons toward a defensible position — cross-references, does not duplicate, MVP & Roadmap.]

**Platform Bet:** [Why build deeper on Salesforce — the strategic rationale for the platform dependency.]
```

**Boundary vs. neighbors:** Solution = *what it does*; Product Strategy = *where it's heading & why*; MVP & Roadmap = *concrete build sequence*. The Horizon Sequencing line cross-references MVP rather than repeating it.

**Stage 5 (Contradict) addition:** one new failure pattern — "Product Strategy uses vague language ('be the leader', 'best-in-class', 'world-class') with no specific thesis, named pillar, or positioning" — consistent with the existing anti-vagueness checks.

### POV Presentation slides (`templates/pov-presentation.html`)

Two new slides inserted **after the Vision slide (slide 3), before Solution**. Deck grows **10 → 12 slides**; Solution becomes slide 6 and every subsequent slide's number + footer shifts by 2 (footers become `N / 12`).

- **Slide 4 — "Strategic Direction":** strategic thesis (headline), horizon-sequencing-to-moat, and the platform bet. New tokens e.g. `{{STRATEGIC_THESIS}}`, `{{HORIZON_TO_MOAT}}`, `{{PLATFORM_BET}}`.
- **Slide 5 — "Product Pillars & Positioning":** 3–4 product pillars with their bets (cards), plus competitive positioning / target segment. New tokens e.g. `{{PILLAR_1_NAME}}`/`{{PILLAR_1_BET}}` … and `{{MARKET_POSITIONING}}`.

`refs/stages/stage-17-pov-presentation.md` and `validation/pov-presentation-checklist.md` update: slide-to-POV-section mapping for the two new slides; checklist becomes 12 slides; faithfulness checks (strategy slides render only what the POV's Product Strategy section states; no invented pillars).

---

## Menu rebalance (`SKILL.md`)

Adding Consumption Opportunities would push a menu question past the tool's 4-option cap. Rebalance to three questions, each ≤4, with one header rename:

- **Q1 "Analysis & Readiness":** MVP Build Plan · Red Team Assessment · Partner Readiness Scorecard · Discovery Framework *(unchanged)*
- **Q2 "Architecture & Growth"** *(renamed from "Architecture & Build")*: Technical & Architectural Assessment · Marketecture · **Consumption Opportunities** *(new)*
- **Q3 "Package" (unchanged):** currently holds 4 options — All outputs + home page · POV Presentation · Investor Presentation · Solution Infographic. Already at the 4-option cap; no change, and nothing is added here.

Only Q2 changes: rename its header "Architecture & Build" → "Architecture & Growth" and add the **Consumption Opportunities** option (Q2 goes from 2 → 3 options). Q1 and Q3 are untouched.

(Implementation note: read the current three questions before editing. Do not disturb the existing option labels the validator checks for: "All outputs + home page", "Discovery Framework" + "(Stage 15)", "Technical & Architectural Assessment" + "(Stage 16)".)

---

## Wiring summary (all files touched)

**New (Feature A):**
- `refs/stages/stage-18-consumption-opportunities.md`
- `templates/consumption-opportunities.md`
- `templates/consumption-opportunities.html`
- `validation/consumption-checklist.md`

**Modified:**
- `templates/pov-output.md` — Product Strategy section (after Vision).
- `templates/pov-presentation.html` — 2 strategy slides after Vision; renumber all slides to `/ 12`.
- `refs/stages/stage-17-pov-presentation.md` — slide mapping for the 2 new slides; 12-slide structure.
- `validation/pov-presentation-checklist.md` — 12 slides; strategy-slide faithfulness checks.
- `SKILL.md` — menu rebalance (Q2 rename + Consumption option), Stage 18 in "All outputs" description + dispatch rule + ordering prose, router table row for Stage 18, Stage 5 Contradict Product-Strategy-vagueness check.
- `refs/parallel-dispatch.md` — Stage 18 in Wave 1 + threshold list; Stage 18 non-interactive brief note.
- `refs/stages/stage-13-output-home-page.md` — Consumption card + filename in convention list and card ordering.
- `README.md` — outputs table row (Consumption Opportunities) + Product Strategy mention; stage count/flow updated.
- `tests/validate_skill.py` — new checks (below).

## Validation Additions (`tests/validate_skill.py`)

1. `t_consumption_stage_files` — `refs/stages/stage-18-consumption-opportunities.md` exists, carries the `**Stage 18 —` heading, is in the router table; `templates/consumption-opportunities.{md,html}` and `validation/consumption-checklist.md` exist and are referenced.
2. `t_consumption_template_tokens` — `consumption-opportunities.html` has balanced `{{ }}` braces, exactly one `{{HOME_HREF}}`, and is added to `HOME_LINK_TEMPLATES` and `TEMPLATE_HTML`.
3. `t_dispatch_consumption` — `refs/parallel-dispatch.md` lists Stage 18 in Wave 1.
4. `t_pov_product_strategy` — `templates/pov-output.md` contains `## Product Strategy`; `templates/pov-presentation.html` contains the two strategy-slide tokens (e.g. `{{STRATEGIC_THESIS}}` and a pillar token).

**Existing checks that must stay green:** stage contiguity (now 1..18), router↔stages parity, menu-stage-ref, `t_home_link_token_once` (now covering the new template), HTML brace/token checks, dimension/scorecard parity (unaffected).

## Testing Approach

TDD against `validate_skill.py` (add check → RED → implement → GREEN → commit), per-task subagent execution with spec + code-quality review, final whole-feature review. Plus a structural smoke-fill of the two new/changed HTML templates: zero unfilled tokens, back-link present, correct slide count (`/ 12`).

## Out of Scope (YAGNI)

- Flex Credit dollar sizing in the consumption artifact (points to `sf-flex-estimator`).
- Any change to Stage 16.
- Agent/data content beyond what the POV + matched vertical research support (no invented opportunities).

## Success Criteria

- An "All outputs + home page" run produces `{SLUG}-consumption-opportunities.{md,html}` with the ranked table, Agents + Data named-component blueprints, the Other-SKU table, a working back-link, and zero unfilled tokens; it's linked from the home page (Consumption card).
- The consumption artifact is also available as a standalone "Consumption Opportunities" menu pick (Q2 "Architecture & Growth").
- The POV gains a Product Strategy section after Vision; the POV Presentation gains 2 strategy slides after the Vision slide and renumbers to 12 slides; both render only what the POV states.
- The output menu has three questions, each ≤4 options, with all validator-checked labels intact.
- Validator passes with the 4 new checks; stage contiguity is 1..18.
