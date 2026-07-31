# Calibration Dogfood — full end-to-end render + canvas (overnight, autonomous)

**Date:** 2026-06-23 (overnight calibration pass)
**Effort:** `summer-26 / agentforce-healthcare-oem`
**Trigger:** Brandon — "validate and calibrate the current build before pushing artifacts out; run a
full end-to-end dogfood autonomously, fix the named + low-hanging items, leave a prioritized morning
list." Run on Opus 4.8.

## What this pass did

Two parallel Opus audits (a card/canvas **calibration reference** vs. pov-builder/pie-poc-forge, and a
**cross-skill consistency audit**), then a sequential set of fixes, then this full dogfood.

### Fixes applied tonight (each committed, suite green at each step)

1. **Canvas calibrated to the sibling skills** (`scripts/canvas.py`, commit 4591f05): adopted the
   pov/poc card chrome (kind pill -> navy titled link -> one-line summary -> status/confidence meta;
   `1px solid #d8e0ec` border, hover lift, `minmax(280px,1fr)` grid). **Cards now render ABOVE the
   Next Steps & Blockers task list** (was below). Added per-artifact `_SUMMARY` + `_KIND` dicts (11
   slugs, sibling-style hardcoded blurbs). Gap-card-no-dead-link behavior preserved.
2. **Render-safety for intentional placeholders** (`scripts/md_to_html.py`, commit f11d59d): the four
   `*_DIAGRAM` slots + `{{PRICE_PENDING}}`/`{{DISCOUNT_PENDING}}` are now declared
   `INTENTIONAL_PLACEHOLDERS` and render as visible "pending" markers (exit 0) instead of hard-failing
   the whole artifact; a genuine unknown token still hard-fails (exit 1) with a clearer message. New
   check R-MD2H-02. **This was the foundation-threatening bug** — before it, a render of #06/#07/#10
   with un-regenerated diagrams or pending pricing would have blocked entirely.
3. **Doc consistency** (commit 240ba10): corrected BACKLOG B9 (it mis-described the code), cleared
   stale "Phase N not yet implemented" notes in `refs/intake-source-map.md` + `refs/artifact-templates.md`,
   annotated spec field-drift (`last_verified` -> `loops{}`+`last_generated`) and the never-created
   planned refs, fixed the `section-diff`->`sections` script-name label in SKILL.md.

Suite grew 35 -> 36 (R-MD2H-02). All checks green.

## The dogfood (full effort render + canvas)

Re-generated **#07** from its current template leaving price + tier-diagram as intentional
placeholders (exactly what a real cycle produces), then rendered the §6 HTML set
(00,01,02,03,05,06,07,10 -> HTML; 04,08,09 MD-only) and assembled `canvas/index.html`.

**Render result: 8/8 artifacts rendered, zero failures.** #07 (pending price + tier diagram) rendered
cleanly with a placeholder NOTE instead of the pre-fix hard failure.

**Golden signals — verified in the rendered bytes:**
- **Calibration:** `<h2>Artifacts</h2>` (cards) appears BEFORE `Next Steps & Blockers` (task list). ✓
- **Sibling card chrome:** each card is `kind pill -> navy titled link -> one-line summary -> status +
  confidence meta`. Example (#00): kind `Summary`, links `00-executive-summary.html`, summary "The
  front door: vision, top use cases, ideal-partner summary, and the rolled-up Next Steps & Blockers
  register.", badge `drafted` + `conf 0.50`. ✓
- **Gap cards:** MD-only artifacts (#04/#08/#09) render as dashed gap cards with NO `.html` link
  ("— not yet rendered", per the M5 relabel). ✓
- **#09 at the floor:** `conf 0.35` badge; overall effort confidence 0.35 (weighted floor). ✓
- **Blocker register (below the cards):** Template-ID gap with owner "Manish Jiandani / John Chung",
  plus the entitlement + pricing gaps. ✓
- **Render-safety in the artifact:** #07's HTML shows "Diagram pending — populated on the next
  generate cycle." and `pending` price/discount cells. ✓

## Verdict

**PASS.** The foundation is internally consistent and consistent with the sibling skills: the canvas
matches the pov/poc card look with cards-above-tasklist and per-card summaries, and the render no
longer hard-fails on legitimately-pending content. The build is sound to continue from. A prioritized
morning list of remaining decisions/enhancements is in `docs/superpowers/calibration-morning-list.md`.

## Note for the morning (minor)
A gap card can show a non-`pending` status badge (e.g. #04 `drafted`) while labeled "not yet
generated" — because the artifact has a manifest status but no `.html` view rendered yet. Correct
behavior (no dead link), but the badge/label pairing could read oddly; see morning list item.
