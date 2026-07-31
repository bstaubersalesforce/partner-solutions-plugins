# ps-npi-forge — Content & Render Upgrades (Design Spec)

**Date:** 2026-07-01
**Skill:** ps-npi-forge (Tier 3)
**Trigger:** New requirements + rendering issues raised by Brandon, grounded in three
Agentforce-for-Healthcare-for-ISVs reference slides (Key Use Cases, Messaging Hierarchy,
Additional Resources) and two nCino POV HTML references (marketecture, solution infographic).

## Baseline (RED reference)

- `python3 tests/validate_skill.py` → **50/50 green** at start of this effort.
- Diagram bug reproduced with real Mermaid 11 CLI: `#12`'s `·`-joined node label
  ("Data 360 · MuleSoft · Zero-Copy · EHR/FHIR") **clips** at the node boundary. All six
  effort diagrams parse without error, so the defect is **container overflow / node-label
  width**, not syntax. The browser CDN view is the surface the user actually sees.
- `#11`/`#12` `.html` files exist but render through `templates/document-shell.html`
  (generic H2 + paragraph), NOT a rich layout.

## Scope

### Part 1 — New content requirements

- **1A. Key Use Cases table (#01 brief).** Add a REQUIRED section with a 5-column table:
  `Category | Opportunity | Example Use Case | Key Features | What Partners Package`.
  Required-but-gap-flagged: the section is always present; if sources are thin it renders a
  single PENDING row and raises a gap in the banner (owner + next step), never omitted.
- **1B. Messaging Hierarchy (#00 executive summary).** Add a REQUIRED section carrying the
  four content tiers from the slide (we generate content, not the slide graphic):
  **Key Message** → **Product positioning statement** → **four Pillars** (title + 1-line
  each) → **Features** (supporting bullets grouped under each pillar). Required-but-gap-flagged.
- **1C. Highlight-card mentions (canvas).** `_SUMMARY` blurbs for `00` and `01` in
  `scripts/canvas.py` must name the new component so it is discoverable on the Key Resources hub.
- **1D. Additional-resources grammar (#01 brief).** Enrich the existing "Additional resources"
  section grammar (informational, from the Additional Resources slide) to prompt for: product
  FCDs (Agentforce 360 / Provider / Payer / Public Health), COA ordering process (guide + demo),
  and Trial & Scratch org setup. No new artifact; grammar only.

### Part 2 — Rendering & styling fixes

- **2A. Rich HTML for #11 and #12.** Reuse the `poster.py` section→panel projection.
  Introduce a `RICH_VIEWS` registry keyed by slug → `{template, sources, panels}`. `#11` and
  `#12` each get a single-source rich template rendered as their **primary `<slug>.html`**
  (replacing the generic doc-shell render for those two slugs). `#14` merged poster is unchanged.
  - `#11` = **light** SFDC 3-column infographic (problem / solution / outcomes + market footer),
    modeled on `ncino-solution-infographic.html` but in the light scheme.
  - `#12` = **light** layered marketecture (stacked `.arch-layer` blocks + the live Mermaid
    diagram), modeled on `ncino-marketecture.html`.
  - Consolidation guards stay green: neither #11 nor #12 gets a `-poster.html`; #14 remains the
    only `-poster.html`.
- **2B. Diagram overflow/clipping.** Fix in the render surface, not the source:
  - `mermaid.initialize` in `document-shell.html` (and the rich templates + slide deck) gains
    `flowchart: { useMaxWidth: true, htmlLabels: true }`.
  - CSS: `.mermaid svg { max-width: 100%; height: auto; }` so the injected SVG scales to its
    container instead of clipping.
  - `refs/mermaid-diagrams.md` gains an authoring note: keep node labels short; break long
    `·`-joined lists across `<br/>` lines.
  - Automated test asserts the config + CSS are present (structural). A **manual browser check**
    is included because true render fidelity is browser-only (headless CLI cannot prove it).
- **2C. Table consistency (light SFDC scheme).** One shared light styled-table treatment across
  `document-shell.html`, the two rich templates, and `canvas.py`: light header row (tint bg,
  navy text) OR navy header — chosen consistently — with rounded 1px border, zebra rows. Applied
  everywhere so every artifact's tables look identical.

## Non-goals

- No new artifact slugs (registry stays 15).
- No change to the generate→refine→validate cycle or the manifest model.
- Marketecture table-enrichment (Component Inventory / Platform Requirements tables like the
  nCino reference) is deferred to BACKLOG — #12's rich view projects its current 6 sections.

## Test strategy

Every task ends by running `python3 tests/validate_skill.py`. New `@check` functions are added
for each new invariant (new tokens present, canvas mentions, rich-view registry parity, table
style presence, mermaid config presence). R-DOC-01 count-drift guard: no doc hardcodes a check
count today, so adding checks is safe; the "15 deliverables" claims stay correct (no new artifacts).
