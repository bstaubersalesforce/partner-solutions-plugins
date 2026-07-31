# ps-npi-forge — Artifact Consolidation (Design)

**Date:** 2026-07-16
**Status:** Approved (brainstorming) → ready for implementation plan
**Baseline:** `main` @ `68e2bf7`, suite green (44+ checks — trust the live run), 15 artifacts (00–14).

## Problem

The artifact family grew to **15** (00–14; memory recorded 13 — it's two behind: #13 demand-plan
and #14 exec-infographic plus the merged-poster/visual-infographics work landed after the last
memory update). Growth concentrated redundancy: the **executive narrative** is now spread across
four artifacts (00/01/02/14) and there are **three HTML visual siblings** (11/12/14). Several
artifacts are independently *authored* while covering substantially the same substance, creating
drift risk and duplicate maintenance.

## Goal

**Fewer authoring points + single-sourced content, with NO surfaces lost.** Keep all 15 artifacts
(they serve distinct upstream NPI/PAM/exec consumers), but make derived artifacts **generate FROM
a single source of record**, grounded in that source rather than independently researched. Net:
one story, many surfaces; drift eliminated on the derived set.

This respects the skill's premise — artifacts are *authoritative feeders* to the larger NPI team,
and the different formats (doc / slide / infographic / poster) exist because different upstream
consumers want different surfaces.

## Source-of-record model (the core change)

| Source of record | Derived artifacts (generated FROM the source) | Notes |
|------------------|-----------------------------------------------|-------|
| **01-brief** (narrative of record) | **00**-executive-summary, **02**-slide-summary, **11**-solution-infographic, **14**-exec-infographic | 00 = `rollup(01) + manifest state` (blockers register + confidence rollup — unique to 00). 02/11/14 = format renders of 01's narrative. |
| **04-internal-faq** | **05**-external-faq | 05 = partner-safe subset; internal-only sections tagged in 04. |
| **06-license-entitlements** | **07**-addon-tiering "Required" tier | 07's Required tier grounded in 06's entitlement table (Recommended/Optional stay 07-authored). |

**Independently authored (NOT derived — left as-is):**
- **01-brief** — the narrative source of record (authored from effort sources).
- **03-internal-enablement** — positioning/motion voice; shares *topics* with 04 but distinct treatment.
- **04-internal-faq** — a source of record (for 05).
- **06-license-entitlements** — a source of record (for 07); Org62-grounded.
- **08-setup-guide** / **09-org-provisioning-validation** — sequential workflow pair, not redundant.
- **10-partner-profile-pov** — whitespace POV, distinct substance.
- **12-marketecture** — architecture view, genuinely distinct from 11/14.
- **13-demand-plan** — business case, distinct substance.

**Derivation graph (must stay acyclic):**
```
01 → {00, 02, 11, 14}
04 → {05}
06 → {07(Required tier)}
```

## Design

This is a **refs + manifest + validator** change. **No template is created, merged, or deleted.**
Derived templates gain a source-naming header comment; that's the only template edit.

### 1. Machine-readable derivation (`scripts/manifest.py`)

Add a module-level parallel structure (do NOT restructure `ARTIFACT_REGISTRY` — it's a flat list
referenced by many registry-derived checks):

```python
# Derivation graph: derived-artifact-slug -> source-artifact-slug.
# Derived artifacts are generated FROM their source (grounded, not re-researched).
# 00 is a special derivation: rollup(01) PLUS manifest state (blockers/confidence).
DERIVES_FROM = {
    "00-executive-summary": "01-brief",
    "02-slide-summary":      "01-brief",
    "11-solution-infographic":"01-brief",
    "14-exec-infographic":   "01-brief",
    "05-external-faq":        "04-internal-faq",
    "07-addon-tiering":       "06-license-entitlements",
}
```

Add a helper `generation_order()` that returns artifact slugs topologically sorted so every source
precedes its derivatives (stable secondary sort by registry order). This drives batch ordering and
is what the new validator asserts against.

Every key and value in `DERIVES_FROM` must be a member of `ARTIFACT_REGISTRY`; the graph must be
acyclic (it is — sources 01/04/06 are never themselves derived).

Note on 07: `DERIVES_FROM["07-addon-tiering"] = "06-license-entitlements"` captures the dependency,
but 07 is only *partially* derived (Required tier from 06; Recommended/Optional authored). The refs
carry that nuance; the manifest just records the dependency edge for ordering + validation.

### 2. Derivation contract in the generate cycle (`refs/quality-loops.md`)

The generate→refine→validate cycle gains a **derivation contract** for derived artifacts:

- A derived artifact's generate brief takes **its already-generated source artifact as explicit
  input** and is instructed to **transform, not re-research**: "Render/condense/subset THIS source
  into {slide | poster | infographic | safe-subset | Required-tier}. Do not introduce claims absent
  from the source. Where the source is silent, flag a gap — do not invent."
- **05-external-faq** specifically: consume 04, emit only partner-safe content; never include a
  section 04 marks internal-only. (Judgment step — generation, not a mechanical strip.)
- **07-addon-tiering**: the Required tier is grounded in 06's entitlement table; Recommended/Optional
  remain 07's own analysis.
- **00-executive-summary**: rollup of 01's narrative PLUS the manifest-fed Next Steps & Blockers
  register and confidence rollup (unchanged behavior for the manifest part).

**Batching guidance update** (currently arbitrary groupings): batches must respect
`generation_order()` — a source artifact is generated in an **earlier or same-earlier batch** than
its derivatives, never after. Concretely: 01, 04, 06 (and independents) generate before 00/02/11/14,
05, 07. The refs give an explicit dependency-ordered batch grouping to replace today's arbitrary
A/B/C/D grouping.

### 3. Document the relationships (`refs/artifact-templates.md`)

Formalize the derivation map: for each derived artifact, state its source and what transform
produces it. Several templates already have "DERIVED from" comments (05, 02); this makes the whole
graph explicit in one place and cross-references `DERIVES_FROM`.

### 4. Template header comments (the only template edits)

Each derived template (00, 02, 05, 07, 11, 14) carries a header comment naming its source, e.g.:
`<!-- DERIVED: generated from 01-brief; render its narrative as a one-screen slide. Do not
re-research. -->`. 05 and 02 already have derivation comments — extend/normalize to all six. No
body/token changes.

### 5. New guardrails (`tests/validate_skill.py`)

The validator is the skill's contract; add checks:

- **R-DERIVE-01** — every `DERIVES_FROM` key and value is in `ARTIFACT_REGISTRY`; the graph is
  acyclic; no source is also a derivative of one of its own derivatives.
- **R-DERIVE-02** — the batch/generation guidance in `refs/quality-loops.md` respects the derivation
  order: assert that the documented batch grouping places each source no later than its derivatives
  (parse the batch grouping the same way existing R-LOOPS-01 reads batching guidance; if that's not
  machine-parseable, assert instead that quality-loops.md contains the dependency-order statement and
  that `generation_order()` exists and is topologically valid — pick the enforceable form during
  implementation and state which).
- **R-DERIVE-03** — every derived template (the six in `DERIVES_FROM`) carries the source-naming
  header comment referencing its actual source slug.
- Keep existing registry-derived checks green (they operate on `ARTIFACT_REGISTRY`, unaffected).

## Verification

Dogfood against the existing effort at
`~/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/`:
1. Regenerate the derived artifacts (00, 02, 05, 07, 11, 14) from their sources per the new contract.
2. Confirm in bytes: (a) each derivative's narrative is consistent with its source (no contradictory
   claims); (b) **05 leaks no internal-only content** from 04; (c) **07 Required tier == 06 required
   entitlements** (no restated/diverging SKU list); (d) 00 still carries the manifest blockers
   register + confidence rollup; (e) 14/02/11 tell 01's story in their format.
3. Full suite + R-DERIVE-01/02/03 green.
4. Re-render canvas; confirm 15/15 still linked, no regressions.

## Success criteria

- `DERIVES_FROM` + `generation_order()` in manifest.py; graph acyclic; all slugs valid.
- Derivation contract in quality-loops.md; batching dependency-ordered.
- artifact-templates.md documents the full derivation map; six derived templates carry source headers.
- R-DERIVE-01/02/03 added and green; existing suite still green.
- Dogfood: derived artifacts regenerate from source, no drift, 05 safe, 07 Required==06, canvas 15/15.
- **No artifact created, merged, or deleted** (surfaces preserved).

## Risks / mitigations

- **Generation variance** (LLM-derived artifacts drift from source anyway) → the derivation contract
  mandates "transform not re-research" + the dogfood byte-checks consistency; refine loop
  (claim-verification) already guards fact drift.
- **Batch-ordering regression** (a derivative generated before its source) → R-DERIVE-02 +
  `generation_order()` make the order machine-checkable, not prose-only.
- **07 partial-derivation nuance lost** (someone auto-derives all of 07 from 06) → refs explicitly
  scope the derivation to the Required tier; DERIVES_FROM edge is for ordering/validation only.
- **Scope creep into merging/deleting templates** → explicitly out of scope; verification asserts
  the registry count is unchanged.
- **Memory drift** (memory says 13) → update memory to 15 + the consolidation model as part of the
  effort close-out.
