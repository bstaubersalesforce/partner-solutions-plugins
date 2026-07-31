# ps-npi-forge — Demand Plan & GTM Enhancements (Design)

**Date:** 2026-06-25
**Status:** Approved for planning
**Branch:** `npi-demand-plan-enhancements`
**Scope:** Four enhancements from initial NPI-tool feedback, built as one coherent pass over the
artifact family.

## Summary

Four enhancements, two of which add new artifacts and two of which edit existing templates in place:

1. **(Item 3) Required-licensing summary** — a summary table of the *required* SKUs (EE, UE for org
   matching, CC, CC+) added near the **top** of `06-license-entitlements`, mirroring the original
   quip table, as a human-authored licensing summary above the Org62-derived composition.
2. **(Item 1) Standard ISV add-on catalog** — a new section in `07-addon-tiering` listing standard
   ISV add-on SKUs partners commonly attach (the cross-sell menu), distinct from this SKU's
   Required/Recommended/Optional tiers.
3. **(Item 2) Demand plan grid** — a **new artifact #13** (`13-demand-plan`): a commercial-discussion
   framework grid keyed to the Ideal Partner Profile, identified segments, and research-estimated TAM.
4. **(Item 4) Exec infographic** — a **new artifact #14** (`14-exec-infographic`): an exec/GTM
   single-screen covering Vision → Value Prop → Key Use Cases → Ideal Partners → TAM.

Net effect: the artifact registry grows **13 → 15**.

## Decisions (from brainstorming)

- **Item 1 placement:** new *section* inside `07-addon-tiering` (not a standalone artifact). Keeps the
  cross-sell menu adjacent to this SKU's own add-on tiering.
- **Item 4:** new artifact #14, not a reshape of #11. #11 keeps telling the solution-architecture
  story (problem → solution → outcomes → built-on-Salesforce); #14 is the "why invest / who for" exec
  story. Different audiences.
- **Item 2 TAM source:** TAM is **estimated in the research/intake phase using internal Salesforce
  insights**, captured once as effort data (flagged as an estimate with confidence), then reused by
  #13, #14, and the existing #00/#11 panels — a single source of truth, flagged pending/estimate until
  confirmed.
- **Build scope:** all four in one plan (they share registry / manifest / render-fill-set / count-guard
  / IPP+TAM wiring; one pass over the family is cleaner than four).
- **Demand-plan grid orientation:** **segments as rows × SKU-bundle columns**, TAM sized per
  segment-row, with an IPP-fit column.
- **Demand-plan voice:** **narrative** (it is a strategic discussion framework, not a factual lookup).

## Architecture & conventions (must match the existing skill)

These four changes touch the skill's systemic invariants. Every one of the following must move in
lockstep or the registry-derived test suite / count-drift guard will (correctly) fail:

- **`ARTIFACT_REGISTRY`** (in `scripts/manifest.py`) — add `13-demand-plan`, `14-exec-infographic`.
  Registry order = generation/registry order; #00-last batching guidance (B11) still applies.
- **`templates/<slug>.md`** — new skeletons for #13 and #14 following the shared grammar
  (`refs/artifact-templates.md`): top voice comment, gap-banner header blockquote with
  `{{STATUS}}/{{CONFIDENCE}}/{{CONFIDENCE_RATIONALE}}/{{GAP_BANNER}}`, body `{{UPPER_SNAKE}}` tokens,
  footer rule + `{{SOURCES}}` + confidence line. Edits to #06 and #07 add tokens in place.
- **`render.py` fill-set** — the authoritative token fill (B6 / R-RENDER-01). Every new token across
  #06, #07, #13, #14 must be added so a complete fill leaves zero surviving `{{TOKEN}}`. Pricing cells
  stay literal `{{PRICE_PENDING}}` / `{{DISCOUNT_PENDING}}`; diagram slots use the `*_DIAGRAM`
  convention so `md_to_html.py` `INTENTIONAL_PLACEHOLDERS` renders a visible "pending" marker, exit 0.
- **`templates/manifest.yaml`** — add the two new artifact blocks (status/confidence/rationale/
  sources/placeholders/four loops/last_generated), matching the existing block shape exactly.
- **`refs/artifact-templates.md` registry table** — add the two rows with register (narrative) + notes.
- **`refs/voice-and-style.md`** — classify #13 and #14 as narrative.
- **R-DOC-01 count-drift guard** — the family-size claim moves 13 → 15 across SKILL.md / refs / README.
  Audit every "13 artifacts/deliverables" string; the guard pins prose to `len(ARTIFACT_REGISTRY)`.
- **Test suite** — registry-derived checks (R-TPL-01 slug∈registry, R-TPL-02 structure, R-RENDER-01
  full-fill, R-CANVAS-03 no raw tokens) extend automatically once registry + templates + fill-set are
  in sync; add targeted asserts where a new token or section has a structural contract (below).
- **`canvas.py`** — the two new artifacts render as cards (status + confidence badges); pending →
  labeled gap cards. No code change expected beyond registry-driven inclusion; verify.
- **`refs/intake-source-map.md`** — add **TAM + segments** as a research-channel output (estimated via
  internal Salesforce insights), degrading gracefully to `pending`/`estimate` when not provided.

## Item 3 — Required-licensing summary (edit `06-license-entitlements`)

Add a section near the **top** of the template, above "Entitlement composition (from Org62 …)":

```
## Required licensing summary
{{REQUIRED_LICENSING_TABLE}}
```

- **Voice:** reference (factual/precise).
- **Content:** the quip-sourced required-SKU table — columns: SKU/edition, role/why-required, notes.
  Rows for this product family: **EE**, **UE (for org matching)**, **CC**, **CC+**. (The exact rows
  are effort data; the template ships the token + a one-line framing sentence.)
- **Relationship to the existing composition section:** this is the *human-authored required-licensing
  summary* (what a partner must license); the Org62 `EntitlementDefinitionMap__c` grant table below it
  remains the *system-pulled composition detail*. The summary frames; the composition substantiates.
- **Fill-set:** add `{{REQUIRED_LICENSING_TABLE}}` to `render.py`; cover in R-RENDER-01. If unprovided,
  it surfaces as a gap in the banner (per shared convention) — not a silent blank.

## Item 1 — Standard ISV add-on catalog (edit `07-addon-tiering`)

Add a new section positioned **after** the existing "SKU reference" table (so the document reads:
this-SKU tiers → this-SKU SKU reference → then the cross-sell catalog as a clearly-separate final
section):

```
## Standard ISV add-ons partners may attach
{{STANDARD_ISV_ADDONS}}
```

- **Voice:** reference.
- **Content:** a catalog/menu of *standard* ISV add-on SKUs partners commonly attach on top of the new
  SKU (e.g., Data Cloud, Agentforce, Slack, Industry clouds — effort-specific). Columns: Add-on SKU,
  Why relevant to this partner motion, Typical attach trigger, Price (`{{PRICE_PENDING}}`).
- **Distinction (must be explicit in the section's framing line):** the Required/Recommended/Optional
  tiers above describe **this product's own** add-on dependencies; this catalog is the **cross-sell
  menu** of standard SKUs partners often also buy. Do not conflate.
- **Reuse:** this catalog is a named input to the demand plan (#13) "Standard add-ons" column.
- **Fill-set:** add `{{STANDARD_ISV_ADDONS}}`; R-RENDER-01 coverage.

## Item 2 — Demand plan grid (new artifact `13-demand-plan`)

A framework grid for discussion with commercial teams. **Narrative voice.**

**Template sections:**

```
<!-- VOICE: narrative — first-person exec/architect McKinsey register -->
# {{PRODUCT_NAME}} — Demand Plan Framework
> gap-banner header (status/confidence/rationale/gap)

## How to use this framework
{{FRAMEWORK_INTRO}}            # what this grid is for; a discussion scaffold, not a forecast

## The demand grid
{{DEMAND_GRID}}               # segments(rows) × SKU-bundle(cols); see structure below

## Segment & TAM basis
{{SEGMENT_TAM_BASIS}}         # the segments, their TAM estimate, and the IPP-fit rationale per row

## Conditional (NPI-dependent) add-ons — inclusion rule
{{CONDITIONAL_ADDONS_NOTE}}   # the discipline: only-if-identified-required; names the CC/CC+ example

## Demand logic (diagram)
{{DEMAND_DIAGRAM}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

**Grid structure (`{{DEMAND_GRID}}`):**
- **Rows:** identified segments. Each row also carries two leading descriptor cells — a **TAM estimate**
  and an **IPP-fit** indicator (drawn from #10) — ahead of the SKU-bundle columns.
- **SKU-bundle columns:** `Core / Required SKUs` | `Standard add-ons (if applicable)` | `Conditional
  (NPI-dependent) add-ons`. (Full row shape: Segment | TAM | IPP-fit | Core/Required | Standard add-ons |
  Conditional add-ons.)
- **Core/Required column:** populated from the Item-3 required-licensing summary (EE/UE/CC/CC+).
- **Standard add-ons column:** populated from the Item-1 standard ISV add-on catalog (#07) — only where
  applicable to that segment.
- **Conditional add-ons column — the key discipline:** a cell is filled **only when the NPI process has
  identified that add-on as required** for that segment (e.g., the CC / CC+ Agentforce-for-Healthcare
  elements). Otherwise the cell is **empty**, not speculatively populated. The template's
  `{{CONDITIONAL_ADDONS_NOTE}}` states this rule explicitly and uses CC/CC+ as the worked example.
- Pricing stays out of scope (`PENDING`); the grid is about *what to discuss*, not a quote.

**Inputs:** IPP (#10), identified segments (effort data), TAM estimate (research-derived, reused). All
flagged pending/estimate if absent, surfacing in the gap banner and #00 rollup.

## Item 4 — Exec infographic (new artifact `14-exec-infographic`)

Exec/GTM single-screen. **Narrative voice.** Renders to HTML via `document-shell.html` + a Mermaid slot
(like #11).

**Template sections:**

```
<!-- VOICE: narrative -->
# {{PRODUCT_NAME}} — Executive Overview
> gap-banner header

## Vision
{{VISION_PANEL}}

## Value proposition
{{VALUE_PROP_PANEL}}

## Key use cases
{{USE_CASES_PANEL}}

## Ideal partners
{{IDEAL_PARTNERS_PANEL}}      # condensed from #10 IPP

## Market opportunity (TAM)
{{TAM_PANEL}}                 # research-estimated TAM, flagged as estimate

## Executive overview (diagram)
{{EXEC_DIAGRAM}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- **Distinction from #11:** #11 = solution architecture story (problem→solution→outcomes→built-on-SF);
  #14 = investment/audience story (vision→value→use cases→who→market). Both single-screen, both narrative.
- Pulls Ideal Partners from #10 and TAM from the shared research-derived estimate.

## Cross-cutting — TAM/segments as research-derived reused input

- TAM is **estimated during research/intake using internal Salesforce insights** (TAM is not a clean
  Org62 pull; it's an analyst estimate). Captured once in the effort manifest/effort-data as a value +
  basis + confidence + an `estimate` flag.
- Referenced by #13 (segment-row TAM), #14 (TAM panel), and the existing #00 + #11 panels — single
  source of truth; if not yet estimated, all consumers show a `pending` gap rather than diverging guesses.
- `refs/intake-source-map.md` gains TAM + segments as a research-channel output with graceful
  degradation.

## Testing

Extend the existing registry-derived suite; do not invent a parallel harness.

- **R-TPL-01 / R-TPL-02** auto-cover #13 and #14 once registered (slug∈registry; gap-banner +
  footer structure). Add the two slugs to any fixture lists.
- **R-RENDER-01** (full-fill, zero surviving tokens) must be extended with every new token:
  `{{REQUIRED_LICENSING_TABLE}}`, `{{STANDARD_ISV_ADDONS}}`, and the #13/#14 body tokens. This is the
  highest-value gate — it's what catches a template token with no fill-set entry.
- **R-DOC-01** count-drift: assert the family-size prose now reads 15 and is pinned to
  `len(ARTIFACT_REGISTRY)`. Update SKILL.md/refs/README strings in the same change so the guard passes.
- **R-CANVAS-03** (no raw `{{TOKEN}}` on the canvas) covers the new artifacts' cards automatically;
  verify the two new artifacts appear as cards (or labeled gap cards when pending).
- **New targeted assert (demand grid):** the #13 template carries the three required column labels
  (`Core / Required`, `Standard add-ons`, `Conditional`) and the conditional-add-on inclusion-rule note
  — a structure check so the discipline can't be silently dropped on a future edit.
- **Diagram-fill verification** must check fence CONTENT, not just `<pre class="mermaid">` presence
  (per B18) for the two new `*_DIAGRAM` slots.
- Run the full suite + a dogfood render of all 15 artifacts (HTML + canvas) on the existing Healthcare
  effort to verify zero surviving tokens and correct cards.

## Out of scope

- Pricing numbers (always `PENDING`).
- Live TAM data fetch / automated market sizing (TAM is an analyst estimate, entered as effort data).
- Phase 6 Slack sync / Phase 7 Deep Build — unaffected; not part of this change.
- Reshaping #11 (explicitly kept as-is).

## Risks / watch-items

- **Fill-set drift** is the main risk: a new template token without a `render.py` entry. R-RENDER-01
  is the backstop; add tokens to the fill-set in the same commit as the template.
- **Count-drift guard** will fail loudly until every "13" string is updated — intended; update prose
  with the registry change.
- **#06 vs #07 conceptual bleed:** the required-licensing summary (#06) and the standard-ISV-add-on
  catalog (#07) must each carry an explicit framing line so they're not confused with the Org62
  composition (#06) or this-SKU add-on tiers (#07) respectively.
- **back-port note (B12):** unrelated, but the `md_to_html.py` pipe-in-prose fix back-port to
  pie-poc-forge remains open; not in scope here.
