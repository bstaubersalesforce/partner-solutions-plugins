# ps-npi-forge — Visual Infographic Views for #11 & #14 (Design)

**Date:** 2026-06-25
**Status:** Approved for planning
**Branch:** `npi-visual-infographics`
**Depends on:** v0.2.1 (the 15-artifact family incl. #14-exec-infographic must exist — merged on `main`).

## Summary

Add a **visual "poster" HTML view** for the two infographic artifacts — `11-solution-infographic` and
`14-exec-infographic` — modeled on pov-builder's rich HTML-template approach but in the **SLDS-light
palette** the skill already uses. The artifact markdown stays the **source of truth**; the poster is a
**pure projection** of its H2 sections into a styled template, so there is no double-authoring. This
introduces a *second render path* to ps-npi-forge (rich HTML template + token-fill) alongside the
existing markdown→`document-shell` path, without disturbing the other 13 artifacts.

## Motivation

Review feedback (2026-06-25): the infographics should follow the visual "fancy image" format of the
pov-builder solution infographic, not read as text panels. pov-builder achieves this with self-contained
styled HTML templates (`templates/solution-infographic.html`, ~448 lines) carrying `{{TOKEN}}` slots,
filled by an ephemeral string/regex-replace script (see pov-builder `refs/html-output-method.md`).
ps-npi-forge currently renders *every* artifact through one path (markdown → `document-shell.html` via
`scripts/md_to_html.py`), which produces a document, not a poster.

## Decisions (from brainstorming)

- **MD stays the source of truth; add an HTML view** (not: replace the MD with an HTML-native artifact).
  Keeps registry/manifest/canvas-content/R-TPL untouched.
- **SLDS-light palette** (the skill's existing `#0176d3`/navy/white tokens), not pov-builder's dark
  1920px poster — so ps-npi-forge stays internally consistent with its other artifacts + canvas.
  **SUPERSEDED 2026-06-25 (Brandon):** the initial SLDS-light poster rendered correctly but read as
  underwhelming (white cards on navy). Decision reversed to the **full pov-builder dark poster
  treatment** — dark ground (`#0f1117`), gradient accent bar, navy header w/ 900-weight hero title,
  colored panel labels with accent bars, bordered dark panels in a 6-col grid. Render path, the
  `{{PANEL_*}}` token contract, and R-POSTER-01/02/03 are unchanged (the restyle is templates-only);
  only the visual treatment differs from this section's original "SLDS-light, not dark" call.
- **View is populated by extracting the MD's H2 sections** and projecting each into the matching panel
  slot — reuse `scripts/sections.py` (the proven H2 splitter) + `md_to_html`'s inline converter. Zero
  double-authoring; the poster is a derived projection.
- **Canvas card links BOTH views** (Document + Poster) for #11/#14; all other cards unchanged.
- **Family stays 15** — posters are *views* of #11/#14, not new registry artifacts.

## Architecture

### The second render path
- **Source (unchanged):** `templates/11-solution-infographic.md`, `templates/14-exec-infographic.md`
  remain the markdown templates. Effort artifacts (`artifacts/11-….md`, `artifacts/14-….md`) remain the
  filled markdown. The existing `md_to_html` path still produces the document `.html` for each.
- **New poster templates:** `templates/solution-infographic-poster.html` (for #11) and
  `templates/exec-infographic-poster.html` (for #14). Each is a self-contained styled HTML page in the
  SLDS-light palette with `{{PANEL_*}}` token slots (one per artifact H2 section) plus header-band
  metadata tokens. Structure modeled on pov-builder's solution-infographic.html; palette = the skill's
  `document-shell.html` tokens (`#0176d3`, navy `#032D60`, white, Salesforce Sans).
- **New render script:** `scripts/poster.py` (stdlib-only). Given an effort artifact `.md` + the matching
  poster template, it: (1) splits the MD by H2 via `sections.split(md)`; (2) maps each section body to its
  panel token via a per-artifact section→panel map; (3) converts each section **body** to HTML via the
  sanctioned converter `md_to_html.md_to_html(section_body)` — full block conversion (paragraphs, lists,
  inline bold/italic/links), NOT a new parser, and NOT just `_inline` (panels contain lists/multi-paragraph
  bodies); (4) fills header-band metadata tokens (title/label/release/date/home, and the `PANEL_HEADLINE`
  tagline for #11 from its "one-line story" section); (5) writes the filled poster; (6) reports any
  surviving `{{TOKEN}}`. Exit non-zero on a genuine unfilled slot; a TBD section simply renders its TBD
  text in-panel.

  *Note on reuse:* `sections.split` returns `{H2-title: section-text}` and `md_to_html.md_to_html` is the
  one sanctioned block converter (verified importable: `from md_to_html import md_to_html`; `_inline` is its
  inline helper, used internally). `poster.py` imports both rather than re-implementing markdown.

### Section → panel maps (the content contract)
- **#14 exec-infographic** panels: `PANEL_VISION` ← "Vision", `PANEL_VALUE_PROP` ← "Value proposition",
  `PANEL_USE_CASES` ← "Key use cases", `PANEL_IDEAL_PARTNERS` ← "Ideal partners",
  `PANEL_TAM` ← "Market opportunity (TAM)". (The "Executive overview (diagram)" H2 is NOT a panel — the
  poster is the visual; the diagram slot stays in the document view only.)
- **#11 solution-infographic** panels: `PANEL_PROBLEM` ← "The problem (why this matters)",
  `PANEL_SOLUTION` ← "The solution (what we built on Salesforce)", `PANEL_OUTCOMES` ← "Outcomes (the proof)",
  `PANEL_MARKET` ← "Market & who it's for", `PANEL_BUILT_ON` ← "Built on Salesforce (the OEM/Embedded stack)".
  (The "one-line story" H2 maps to the header-band tagline `PANEL_HEADLINE`; the diagram H2 is not a panel.)
- The map lives in `poster.py` keyed by artifact slug. If a mapped section is absent in the MD, that's a
  hard error (the contract is broken); if present-but-TBD, the panel shows the TBD text.

### Canvas (links both views)
`scripts/canvas.py` `_card` and `build_index` change so #11/#14 can show two links — **Document**
(`<slug>.html`) and **Poster** (`<slug>-poster.html`). Mechanics:
- `build_index` today takes `html_present: {slug: bool}`. Extend the presence signal so it also knows
  whether a poster file exists for a slug. Minimal-change approach: a second optional map
  `poster_present: {slug: bool}` (default empty); only #11/#14 are ever poster-bearing.
- `_card` for a poster-bearing slug renders both links, each gated on its own presence bool (no dead
  link — same rule as today, applied per link). Non-poster slugs render exactly as now (single link).
- The poster file naming is `<slug>-poster.html` (companion to the document `<slug>.html`), consistent
  with the existing `02-slide-summary-slides.html` companion precedent.

### Render-and-canvas ref
`refs/render-and-canvas.md` gains a short "poster view" subsection: #11/#14 also render a
`<slug>-poster.html` via `scripts/poster.py`; the canvas links both. (Additive; does not change the
existing format-rule list — the document views for #11/#14 still render as today.)

## Components (isolation)

| Unit | Responsibility | Depends on |
|------|----------------|------------|
| `templates/solution-infographic-poster.html` | #11 styled SLDS-light poster, `{{PANEL_*}}` + header slots | — |
| `templates/exec-infographic-poster.html` | #14 styled SLDS-light poster, `{{PANEL_*}}` + header slots | — |
| `scripts/poster.py` | MD→poster projection (split, map, inline-convert, fill, report) | `sections.py`, `md_to_html` inline converter |
| `scripts/canvas.py` (modified) | dual-link cards for poster-bearing slugs | `poster_present` map |
| `refs/render-and-canvas.md` (modified) | document the poster view + dual-link | — |

## Testing

New `R-POSTER-*` checks in `tests/validate_skill.py` (stdlib, registry-derived style):
- **R-POSTER-01:** both poster templates exist; their `{{TOKEN}}`s are UPPER_SNAKE; each carries the
  expected `PANEL_*` slots for its artifact.
- **R-POSTER-02:** `poster.py` fills a poster from a representative MD (the artifact template itself, or
  a fixture) leaving zero surviving `{{TOKEN}}`; a missing mapped section raises; a TBD section renders
  its text.
- **R-POSTER-03:** the section→panel map in `poster.py` covers every `PANEL_*` slot in each template
  (no orphan slot, no map entry without a slot) — the parity guard for this new parallel structure.
- **R-CANVAS (extend):** `build_index` with `poster_present={11…:True,14…:True}` emits two links for
  #11/#14 (Document + Poster), single links elsewhere, and still no dead link when a poster is absent.
- Existing suite stays green (MD templates, registry, manifest, document-shell render path all untouched).
- **Dogfood:** render both posters for the HC effort (TBD content), eyeball the SLDS-light visual, and
  confirm the canvas shows the dual links.

## Out of scope

- No change to the markdown templates, the registry (stays 15), the manifest, or the other 13 artifacts.
- No dark-poster palette (SLDS-light only).
- Diagrams inside posters — the existing Mermaid diagram slots stay in the *document* view; the poster is
  the visual artifact itself.
- pov-builder changes — we model on its approach, we don't modify it.
- Retiring the document view for #11/#14 — both views coexist (canvas links both).

## Risks / watch-items

- **Parallel-structure drift** is the main risk: the poster templates' `PANEL_*` slots, `poster.py`'s
  section→panel map, and the artifact MD's H2 headings must agree. R-POSTER-03 guards slot↔map parity;
  the map keys on the exact H2 text, so if an artifact's H2 heading is reworded the map must update —
  call this out in the ref and guard with R-POSTER-02 (missing-section raises). This is the same drift
  class as B30 (canvas dicts) / B29 (render-ref list); keep the map in one place (`poster.py`).
- **Canvas dual-link** is the one model complication (the brainstorm's flagged tradeoff) — contained to
  `_card`/`build_index`; non-poster cards are byte-unchanged.
- **Inline-converter reuse:** `poster.py` must call `md_to_html`'s inline-formatting function, not
  re-implement markdown — avoids a second divergent parser (the plan pins the exact function).
