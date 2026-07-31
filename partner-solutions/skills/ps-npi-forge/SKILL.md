---
name: ps-npi-forge
description: Use when Partner Solutions is contributing to a Salesforce NPI effort for a new Embedded/OEM product modeled on a parent SKU — turns sources into a consistent family of PS-owned artifacts plus a synced Key Resources canvas, with confidence scoring and gap tracking.
---

# ps-npi-forge

Builds PS-owned NPI artifacts for one new product (one release), modeled on a directly-sold parent
SKU. Outputs feed upward into the larger NPI team's official deliverables, so they are
**authoritative-feeder quality**: consistent, source-grounded, and uncertainty-flagged.

See [docs/design-spec.md](docs/design-spec.md) for the full architecture.

## The effort lifecycle

An **effort** = one product for one release. Effort data lives **outside this repo** at
`/Users/bstauber/claude-projects/ps-npi-efforts/<release>/<product-slug>/`. The `manifest.yaml`
there is the state: per-artifact status, confidence, placeholders, sources, and the Slack channel.

**Intake:** the only required input is a parent direct SKU; six channels (paste, source-fetch,
Org62, Slack, price-list, web research) enrich it and each degrades gracefully. See
[refs/intake-source-map.md](refs/intake-source-map.md).

1. **Open / resume** an effort. The opening request is shaped like *"create an ISV Embedded SKU
   based on the standard `<parent>` SKU"* (parent SKU is the only required input). Then ask the
   intake follow-ups one at a time — planned Embedded SKU name, edition(s), required add-ons, other
   add-ons, the parent's Slack channel(s), any resource links (real FCD/doc URLs are included in the
   artifacts), and anything else to consider. See [refs/intake-source-map.md](refs/intake-source-map.md).
2. **Generate → refine → validate** each artifact (start from knowledge, fold in sources, run loops).
3. **Assemble** the Key Resources canvas (local HTML + optional Slack canvas).

Each artifact runs the three-pass **generate → refine → validate** cycle with four quality loops
(claim verification, completeness, uncertainty surfacing, partner-lens rules); per-section
edit-preservation carries human edits over verbatim on regeneration. See
[refs/quality-loops.md](refs/quality-loops.md). The mechanical steps run through `scripts/`
(render, sections, scan, Org62 parse, manifest); the judgment is the agent's.

**Outputs:** narrative/shareable artifacts render to MD + HTML via `scripts/md_to_html.py` into the
SLDS `templates/document-shell.html`; `02-slide-summary` also renders an SLDS **slide deck** via
`scripts/slide_deck.py` (one slide per H2 section); reference artifacts stay MD-only unless they carry a diagram.
`scripts/canvas.py` assembles the Key Resources `canvas/index.html` (artifact cards with status +
confidence badges, the Next Steps & Blockers register; pending artifacts render as labeled gap cards).
Mermaid diagrams render live via the CDN in the HTML; SVG export (`scripts/mermaid_export.py`) is
capability-gated on `mmdc`. The full render recipe -- the format rule, the exact `md_to_html.py`
invocation, the regenerate-diagrams-before-render ordering, and the canvas assembly -- is in
[refs/render-and-canvas.md](refs/render-and-canvas.md).

> Live Slack sync + publish gate (Phase 6) and Deep Build C-mode (Phase 7) are not yet implemented
> (see BACKLOG.md).

**Voice & style:** narrative artifacts use the first-person exec/architect McKinsey voice;
reference artifacts stay factual. See [refs/voice-and-style.md](refs/voice-and-style.md).
**Artifacts:** the 15 deliverables are generated from skeletons in `templates/` per the grammar in
[refs/artifact-templates.md](refs/artifact-templates.md).
**Entitlements:** #06/#07 model the parent SKU's composition from Org62 (read-only) via a two-step
resolve→compose pull (a human pins the right `Product2`, or passes a known Id) over
`sfbase__EntitlementDefinitionMap__c`, per [refs/org62-entitlements.md](refs/org62-entitlements.md);
the skill drafts and flags, a human confirms.
**Diagrams & canvas:** artifacts carry SLDS-themed Mermaid diagrams (live via CDN in the HTML view)
and assemble into a Key Resources `canvas/index.html`; see [refs/mermaid-diagrams.md](refs/mermaid-diagrams.md).

## Run modes

- **Standard** — interactive, per-artifact generate→refine→validate; quality loops single-pass.
- **Deep Build** — opt-in Workflow escalation (adversarial multi-agent verification + live
  target-partner research) writing back to the same effort. Triggered explicitly.

## Refusal & scope conditions

This skill **does not**:

- Determine or fill **partner-facing pricing or discounts** — out of scope; list/quote/discount
  cells are left as marked placeholders owned elsewhere. (Carve-out: **internal business-case
  inputs** — ASP, penetration, attrition, and cross-cloud halo ACV — are in scope as *flagged
  estimates* in the demand-plan artifact (#13) only, sourced from internal Salesforce insights;
  they are planning inputs, never a partner quote.)
- Cite **non-official documentation** for technical guidance — only official Salesforce sources
  (help/developer/architect.salesforce.com, Trailhead, Partner Community, Org62-internal tools).
  Non-official links are flagged and excluded, never silently included.
- **Assert entitlements** (licenses/PSLs/features/storage) without flagging them for human
  confirmation — it drafts and flags; a human confirms.
- **Write to Org62** — Org62 access is read-only.
- **Publish to Slack without confirmation** — it confirms before creating a Slack canvas, and
  external-FAQ content always requires an explicit OK.
- **Silently drop an uncertainty** — every PENDING/TBD/missing value is surfaced with an owner and
  a next step.
