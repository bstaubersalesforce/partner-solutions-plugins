# ps-npi-forge — Consolidate the Two Posters into One Merged Exec Poster (Design)

**Date:** 2026-06-25
**Status:** Approved for planning
**Branch:** `npi-merged-poster`
**Depends on:** the visual-infographics increment (poster path, `poster.py`, R-POSTER-01/02/03, canvas
dual-link) and the dark-poster restyle — both merged on `main`.

## Summary

The two poster views (`11-solution-infographic`, `14-exec-infographic`) are structurally distinct but
read as "the same artifact" — identical dark styling plus overlapping prose (both carry a Solution/Value
story and a Market panel). Consolidate them into **one merged poster**, keyed to #14, that draws its
panels from **both** source artifacts and tells a single strong narrative. This is **poster-layer-only**:
both markdown artifacts and both *document* HTML views remain; only the duplicate *poster* (template +
map entry + canvas poster-link for #11) is removed. The artifact family stays 15; the registry is
untouched.

## Decisions (from brainstorming)

- **Consolidate** (not "differentiate" or "visual-only") — for an OEM NPI, one visual poster suffices.
- **Survivor: #14** — the merged poster lives on the `14-exec-infographic` card; `11-solution-infographic`
  reverts to a plain document card.
- **Merged, not single-source** — the poster pulls the best panels from BOTH artifacts (a bit of new
  code in `poster.py`: multi-source panel sourcing), rather than just deleting #11's poster.
- **Poster-layer-only blast radius** — registry/manifest/family unchanged (15); both MD artifacts +
  both *document* views stay. Only the #11 *poster* artifacts go.
- **Locked panel set + order** (7 panels): Vision (#14) → The Problem (#11) → The Solution (#11) →
  Outcomes (#11) → Market Opportunity · TAM (#14) → Ideal Partners (#14) → Built on Salesforce (#11).
  Dropped as redundant: #14 "Value Proposition" (folds into Solution), #14 "Key Use Cases" (TBD,
  overlaps Solution), #11 "Market & who it's for" (folds into Ideal Partners / TAM).

## Architecture

### Multi-source `poster.py` (the new code)
Today `poster.py` `SECTION_MAP[slug]` is `{H2-title: PANEL_TOKEN}` and `render_poster(slug, md_text,
template_text, meta)` splits a single `md_text`. Extend to let a poster draw panels from a primary
artifact plus one or more named secondary artifacts:

- **`SECTION_MAP` entry shape (merged poster):** instead of a flat `{H2: PANEL}`, the `14-exec-infographic`
  entry becomes a structure that records, per panel, **which source artifact** and **which H2** it comes
  from. Concrete shape (chosen for minimal change + readability):

  ```python
  SECTION_MAP = {
      "14-exec-infographic": {
          # panel_token: (source_slug, "H2 heading in that source")
          "PANEL_VISION":        ("14-exec-infographic", "Vision"),
          "PANEL_PROBLEM":       ("11-solution-infographic", "The problem (why this matters)"),
          "PANEL_SOLUTION":      ("11-solution-infographic", "The solution (what we built on Salesforce)"),
          "PANEL_OUTCOMES":      ("11-solution-infographic", "Outcomes (the proof)"),
          "PANEL_TAM":           ("14-exec-infographic", "Market opportunity (TAM)"),
          "PANEL_IDEAL_PARTNERS":("14-exec-infographic", "Ideal partners"),
          "PANEL_BUILT_ON":      ("11-solution-infographic", "Built on Salesforce (the OEM/Embedded stack)"),
      },
  }
  ```
  (#11's own `SECTION_MAP` entry is **removed** — #11 no longer has a poster.)

- **`render_poster` signature** gains the secondary sources. Chosen form:
  `render_poster(slug, sources, template_text, meta)` where `sources` is `{source_slug: md_text}` — a
  dict of every artifact markdown the poster needs (primary + secondaries). The function looks up each
  panel's `(source_slug, h2)`, pulls the section from `sources[source_slug]`, converts the body via
  `md_to_html`, and fills the panel. **Backward-compatibility note:** this changes the signature from the
  current `(slug, md_text, template_text, meta)`. The only caller is the dogfood driver + the tests;
  both are updated in the same plan. (No production caller exists — posters are rendered by a driver, not
  wired into a pipeline.) A panel whose `(source_slug, h2)` is missing from `sources` or whose H2 isn't in
  that source raises `ValueError` (the existing contract guard, now source-aware).

- **`PANELS_FOR(slug)`** continues to return the set of panel tokens for a slug (now read from the
  structured map's keys).

- **`SOURCES_FOR(slug)`** — new helper returning the set of distinct source slugs a poster needs
  (e.g. `{"14-exec-infographic", "11-solution-infographic"}`), so a driver knows which MDs to load.

### The merged template
`templates/exec-infographic-poster.html` becomes the 7-panel merged poster (dark treatment, unchanged
skin). Panel tokens in the locked order: `PANEL_VISION`, `PANEL_PROBLEM`, `PANEL_SOLUTION`,
`PANEL_OUTCOMES`, `PANEL_TAM`, `PANEL_IDEAL_PARTNERS`, `PANEL_BUILT_ON` + the metadata tokens
(`TITLE/LABEL/RELEASE/GENERATED_DATE/HOME_HREF`). Header sub-label updated from "Executive Overview" to
something that reflects the merged scope (e.g. "Executive & Solution Overview").

### Removed
- `templates/solution-infographic-poster.html` (deleted).
- `SECTION_MAP["11-solution-infographic"]` (removed).

### Canvas
`11-solution-infographic` is no longer poster-bearing: drop it from `poster_present` wherever the canvas
is built (the dogfood driver + any test). `_card`/`build_index` need **no code change** — they already
render a plain document card when `has_poster` is False. The merged poster stays on the #14 card
(poster-primary title + "(document)" secondary), exactly as today. Verify #11's card reverts to a normal
single document link.

### Ref
`refs/render-and-canvas.md` section 1b updated: one poster (`14-exec-infographic` → merged exec+solution
poster), multi-source (pulls panels from #14 and #11 markdown), `<slug>-poster.html`; #11 has a document
view only. Note the multi-source `SECTION_MAP` shape and that the section→panel contract keys on the
exact H2 headings of *each* source.

## Components touched

| Unit | Change |
|------|--------|
| `scripts/poster.py` | structured multi-source `SECTION_MAP`; `render_poster(slug, sources, template, meta)`; `SOURCES_FOR`; source-aware missing-section guard |
| `templates/exec-infographic-poster.html` | merged 7-panel template (locked order), updated sub-label |
| `templates/solution-infographic-poster.html` | **deleted** |
| `scripts/canvas.py` | no code change; verify #11 reverts to document-only card |
| `refs/render-and-canvas.md` | one multi-source poster; #11 document-only |
| `tests/validate_skill.py` | R-POSTER-01/02/03 + R-CANVAS updated to the merged/multi-source shape |

## Testing

- **R-POSTER-01:** the one poster template exists; tokens UPPER_SNAKE; it carries exactly the 7 merged
  panel slots. (`solution-infographic-poster.html` must NOT exist — assert its absence so a stale copy
  can't linger.)
- **R-POSTER-02:** `render_poster("14-exec-infographic", sources, template, meta)` with `sources` =
  {#14 md, #11 md} fills all 7 panels, zero surviving tokens; a panel whose source H2 is missing raises;
  metadata stays HTML-escaped (the prior increment's fix).
- **R-POSTER-03:** the merged template's `PANEL_*` slots exactly equal the merged `SECTION_MAP` keys for
  `14-exec-infographic`; and `SECTION_MAP` has no `11-solution-infographic` entry (the consolidation guard).
- **R-CANVAS-01:** #14 with `poster_present={14:True}` → poster-primary title + "(document)" secondary;
  #11 with no poster → plain single document card, no `-poster.html` link anywhere for #11.
- **Dogfood:** render the merged poster for the HC effort (loading both #11 and #14 markdown), confirm
  7 panels populate (mix of real + TBD content), the canvas shows the merged poster on #14 and #11 as a
  plain document card, and the stale `11-solution-infographic-poster.html` is removed from `canvas/`.

## Out of scope

- Registry / manifest / family change (stays 15) — both MD artifacts and both document views remain.
- Re-theming the poster (keep the dark treatment from the prior increment).
- Touching #11's or #14's markdown artifact content (the merge is at the poster projection layer; it
  reads the existing H2 sections as-is).
- Pricing / commercial numbers (still TBD in-content).

## Risks / watch-items

- **Signature change to `render_poster`** is the main churn. Mitigated: the only callers are the dogfood
  driver and the tests, both updated in the same plan; no production pipeline calls it. The plan must
  update every call site in lockstep.
- **Multi-source H2 contract:** the merged map keys on exact H2 strings in *two* artifacts now — an H2
  rewording in either #11 or #14 breaks a panel. R-POSTER-02's missing-section guard catches it at suite
  time (the test feeds representative MD for both sources). Keep the map in one place (`poster.py`).
- **Stale poster file:** deleting `solution-infographic-poster.html` from the skill is easy; the *effort*
  `canvas/11-solution-infographic-poster.html` must also be removed during dogfood so the canvas doesn't
  show a dead/duplicate. R-POSTER-01 asserts the template's absence; the dogfood step removes the effort copy.
