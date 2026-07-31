# Directional Consumption Pre-Estimate — Design

**Date:** 2026-06-08
**Status:** Approved design — ready for implementation plan
**Scope:** Enhancement to pov-builder **Stage 18 — Consumption Opportunities**

---

## Problem

Stage 18 maps *where* consumption grows (Agentforce agents, Data Cloud flows,
other SKUs) but deliberately stops at a **qualitative** "consumption signal" and
hands all cost math to the `sf-flex-estimator` skill. In practice, a partner
preparing a POV wants a **directional, order-of-magnitude pre-estimate** of how
much Agentforce and Data 360 consumption a use case will drive — a number they
can carry *into* the official Agentforce Credit Estimator and Data 360 calculator
to seed them, not a replacement for those tools.

The gap: today Stage 18 gives no quantity at all, so the reader starts the
calculator from zero. We want to inform the calculator with pre-estimates.

## Goal

Add a **directional consumption estimate** to each Agentforce and Data Cloud
opportunity in the Stage 18 artifact:

- Express it in **credits** (and the volume drivers behind them), **not dollars**.
  Dollar / PUPM / contract pricing remains owned by `sf-flex-estimator`. This
  keeps the "inform the calculator, don't replace it" boundary crisp.
- Anchor all estimates to a **single customer-size band** (S/M/L/XL) chosen for
  the target customer, with a clear note stating the anchor and the scaling
  driver so a reader can scale to other bands.
- Make every number **auditable**: show the U / F / A and entity-count
  assumptions behind it, so it can be edited directly in the real calculator.

## Non-Goals

- **Not** replacing `sf-flex-estimator` — that skill still owns authoritative
  Flex-Credit cost, dollar sizing, PUPM, tiering, and Private Connect.
- **Not** producing dollar figures in the artifact. Credits only.
- **Not** a four-band comparison table. One anchored band + scaling note.
- **Not** referencing any specific partner, customer, or deal (no CaixaBank, no
  nCino, no named bank). The skill stays generic; the worked example is synthetic.

---

## Estimation Model (codified from the source calculators)

Three composable formulas, all directional:

### Agentforce — action/prompt volume → credits
Per opportunity, per anchored size band:

```
Total monthly actions  = U × F × A × #Entities
Total annual actions   = monthly × 12
Annual action credits  = annual actions × 20
Annual prompt credits  = annual prompts × (2 basic | 4 standard)
Directional credit band = low–high across reasonable A / tier assumptions
Sandbox usage           = × 0.8 (20% off) — noted, not the headline figure
```

Where:
- `U` = est. users per entity
- `F` = monthly invocations per user
- `A` = internal actions per invocation
- `#Entities` = count of the scaling unit for the anchored band (e.g. branches,
  hubs, sites, seats)

Credit rules (from the Agentforce Credit Estimator + Questionnaire):
- 1 Agentforce Action = **20 credits** (covers the whole action execution,
  including any Flow/Apex/prompt bundled inside it)
- 1 standalone prompt / LLM inference = **2** (basic) or **4** (standard) credits
- Sandbox actions = **16 credits** (20% off the 20-credit production rate)

### Data 360 — volume × frequency × multiplier → credits
Per data opportunity, per anchored band:

```
Annual credits = (Data Volume in M rows) × Run Frequency × Usage-Type Multiplier
```

Key usage-type multipliers (credits per **million rows** processed):
Profile Unification 100,000 · Batch Data Pipeline 2,000 · Streaming Data
Pipeline 5,000 · Batch Calculated Insights 15 · Streaming Calculated Insights 800 ·
Data Queries 2 · Segmentation 20 · Batch Activation 10 · Streaming Actions 800 ·
Real-Time Profile API 900 · Batch Data Transforms 400 · Unstructured Data 60 ·
Data Federation 70 · Data Shares 70 · Internal Data Pipeline 0.
Sandbox usage = 20% off.

### Customer-size segmentation (S/M/L/XL)
The estimate is anchored to **one** band — the target customer's segment. The
artifact carries a **Sizing-Band Anchor** note that:
1. names the anchored band and why (e.g. *"Typical targets fall into the M band;
   estimates below assume M"*),
2. names the **scaling driver** (the `#Entities` unit),
3. tells the reader to scale `#Entities` (and optionally U/F) for other bands.

Bands are **abstract** — S/M/L/XL are relative labels with **no reference
entity-count ranges**. The rate card describes what a band *means* (a relative
size of the target customer, scaled via `#Entities`) but assigns no numeric
ranges to any band. The concrete `#Entities` figure comes from the specific
target customer in the POV, not from a band lookup.

---

## Components

| # | File | Change |
|---|------|--------|
| 1 | `refs/consumption-estimation.md` | **NEW** — rate card: action/prompt credit rules, Data 360 multiplier table, sandbox discount, journey→step→component method, **abstract** S/M/L/XL band model (relative labels, no reference ranges), one **synthetic** worked example (generic retail-bank-style: N branches / M hubs). Header states "directional; sf-flex-estimator owns authoritative rates — keep in sync." |
| 2 | `refs/stages/stage-18-consumption-opportunities.md` | Refine boundary (qualitative signal → **may** include directional credit estimate, still no $); add estimation steps; load the new ref. |
| 3 | `templates/consumption-opportunities.md` | Add Sizing-Band Anchor note; add per-opportunity **Directional Estimate** block (assumptions + volume + credit band); add credit-band column to the map. |
| 4 | `templates/consumption-opportunities.html` | Mirror the .md changes via the block-injection token pattern (`{{SIZING_BAND_NOTE}}`, extend `{{AGENT_BLOCKS}}`/`{{DATA_BLOCKS}}`, map column). |
| 5 | `validation/consumption-checklist.md` | New checks: anchor note present; every Agent/Data opportunity has assumptions + volume + credit band; bands cite rate-card rules; **still no dollar figures**. |
| 6 | `SKILL.md` | Update Stage 18 boundary line + Stage 7 menu description (mention directional pre-estimate that informs the calculator). |
| 7 | `tests/validate_skill.py` | Adjust structural assertions for new template tokens / checklist items; assert the new ref exists and is referenced by Stage 18. |
| 8 | `README.md` | Document the feature under Stage 18 / "How it works". |

---

## Data Flow

```
Approved POV use cases + matched vertical + target-customer size
        │
        ▼
Stage 18 maps opportunities (existing) ──► for each Agent / Data opportunity:
        │                                      derive U, F, A, #Entities (anchored band)
        │                                      apply credit rules → directional band
        ▼
Consumption Opportunities artifact (.md + .html)
   • Sizing-Band Anchor note
   • per-opportunity: assumptions → volume → directional credit band (no $)
        │
        ▼
Reader carries pre-estimates into the official calculator / sf-flex-estimator
   for authoritative cost sizing
```

## Boundary Reconciliation (the design's load-bearing decision)

- **sf-flex-estimator** keeps authoritative cost/$ sizing. Unchanged.
- **Stage 18** moves from *no quantity* to *directional credits + auditable
  volume drivers*, explicitly framed as calculator seed values.
- **Rate duplication risk:** `refs/consumption-estimation.md` restates rates that
  sf-flex-estimator also holds. Accepted deliberately (self-contained ref beats
  fragile cross-skill paths), and mitigated by a sync note in both the ref header
  and the checklist. If the two ever diverge, sf-flex-estimator wins.

## Testing

- Structural (`tests/validate_skill.py`): new ref exists and is loaded by Stage
  18; new template tokens present in both .md and .html; new checklist items
  present; the "no dollar figures" guard still asserted.
- Behavioral: no deterministic script changes (the estimate is LLM-generated
  prose/tables) — quality is caught at the Stage 7 approve gate and the
  consumption-checklist self-validation, consistent with the skill's existing
  posture on generated content (see BACKLOG R6).

## Open Questions

None blocking. Confirmed in brainstorming: credits-only (no $), single anchored
band + scaling note, **abstract bands with no reference ranges**, assumptions
shown, fully anonymous/generic.
