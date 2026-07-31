# Phase 5 Acceptance — Healthcare effort rendered to HTML + Key Resources canvas

**Date:** 2026-06-23
**Effort:** `summer-26 / agentforce-healthcare-oem`
**Run mode:** Standard (B), controller-driven. No external services (pure local render).
**Effort data:** `/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/`
(outside the skill repo).

## What ran

**HTML render (per the §6 format rule).** Rendered the 7 narrative/shareable artifacts + #06 (which
carries the entitlement table) to HTML via `scripts/md_to_html.py` into `templates/document-shell.html`:
`00-executive-summary`, `01-brief`, `02-slide-summary`, `03-internal-enablement`, `05-external-faq`,
`06-license-entitlements`, `10-partner-profile-pov` -> `canvas/<slug>.html`. The reference artifacts
`04-internal-faq`, `08-setup-guide`, `09-org-provisioning-validation` were left **MD-only** (no
diagram), per the format rule.

**Canvas assembly.** `scripts/canvas.py` `build_index(manifest, html_present)` wrote
`canvas/index.html` (8,371 bytes) from the live effort manifest, with `html_present` computed from
actual `.html` file existence (not a hardcoded list).

## Golden signals (verified in the rendered bytes, not assumed)

1. **Linked cards for rendered artifacts** -- e.g. `01-brief.html` is linked from its card.
2. **No dead links** -- the MD-only artifacts (#04/#08/#09) produce **zero** `<slug>.html` links in
   the canvas; they render as labeled gap cards. (`grep` for `04-internal-faq.html`/`08-setup-guide.html`
   in the index = 0.)
3. **Status + confidence badges** -- #09 shows `conf 0.35` with its `drafted` badge (the effort floor);
   verified artifacts (#01 @ 0.75, #02, #03) carry their badges.
4. **Next Steps & Blockers register** -- aggregates the manifest placeholders; the **Template ID**
   gap appears with owner **"Manish Jiandani / John Chung"**, alongside the entitlement-composition and
   pricing gaps.
5. **Overall confidence** -- the canvas shows `Overall confidence: 0.35` (the weighted floor, driven by
   #09's Template-ID blocker).
6. **Mermaid live render** -- the document shell embeds the `mermaid@11` ESM CDN
   (`startOnLoad: true`) in every artifact HTML; `#00`'s rendered HTML carries a live
   `<pre class="mermaid">` block (the status-rollup fence the cycle filled), so it renders in a
   browser without a build step.
7. **`mmdc` capability-gated** -- `mermaid_export.mmdc_available()` is `False` on this machine;
   `export_svg(...)` returns `{ok: False, skipped: True, message: "...npm i -g @mermaid-js/mermaid-cli..."}`
   -- reports-and-skips, never blocks.

## Verdict

**PASS.** The two render scripts (`md_to_html.py`, `canvas.py`) turn the effort's artifact markdown
into a shareable SLDS-styled HTML set + a Key Resources hub that faithfully reflects the live manifest:
correct links for rendered artifacts, labeled gap cards (no dead links) for the rest, real
status/confidence badges, the aggregated blocker register with owners, and the weighted-floor
confidence. Mermaid renders live via the CDN; SVG export is capability-gated and skips cleanly with
`mmdc` absent. The mechanical pieces are CI-gated by the 35-check suite; this run is the live render
acceptance.

## Rough edges / follow-ups (for BACKLOG)

- **Diagram fences populate on a cycle run, not on render.** The named diagram slots
  (`{{STATUS_ROLLUP_DIAGRAM}}` etc.) are filled by the generator when an artifact is (re)generated.
  `#00` carried a live `class="mermaid"` block here because the earlier dogfood/regeneration filled it;
  artifacts whose diagram slot was not yet filled in a cycle run will show the slot only once
  regenerated. This is the intended staging (Phase 5 ships the slots + the render path; the cycle
  fills them), worth noting so a future run regenerates the remaining named diagrams (#06/#07/#10).
- **B3 (price-list fetchability)** remains an open intake spike, deferred from Phase 5 -- revisit
  alongside Phase 6 intake work.
- A future enhancement could have `canvas.py` also emit per-artifact SVG via `mermaid_export.py` when
  `mmdc` is present (currently the live-CDN path covers the in-browser case; SVG is for decks).
