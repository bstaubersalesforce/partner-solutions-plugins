# ps-npi-forge — Calibration Morning List (2026-06-23 overnight pass)

> **STATUS: ALL ITEMS RESOLVED (2026-06-23 overnight, autonomous).** After the first calibration
> pass (canvas cards, render-safety, doc-consistency A1-A5), Brandon approved the remaining items —
> "pending docs may be linked as long as they are tagged as such; proceed with M1 + M2/M3/M4/M5/M6."
> All six are now implemented, verified, and pushed. Suite 36 -> **38/38**. The full Healthcare
> dogfood re-ran clean (8/8 render, all golden signals pass) with every fix integrated. Resolution
> notes are inline under each item below. Nothing here is outstanding; this file is now a record.

Prioritized fixes/enhancements surfaced by the overnight validate+calibrate+dogfood pass. The
**obvious low-hanging items were fixed in the first pass** (see `acceptance/2026-06-23-calibration-dogfood.md`):
canvas calibrated to sibling cards (cards-above-tasklist + summaries), render-safety for intentional
placeholders, and doc-consistency A1–A5. The decision/enhancement items below were then resolved.

## Resolution summary (commits)
- **M1+M5** (`67fa870`): cards link whenever a doc is RENDERED regardless of status, but a non-verified
  linked doc is TAGGED "— {status}, not yet final" (amber); un-rendered docs stay no-link gap cards
  relabeled "— not yet rendered". (Brandon's "linked pending is OK if tagged" call.)
- **M3** (`993c9be` + de-noise `a46cfd3`): canonical pending-price markers `$xx (pending)` / `xx% (pending)`
  render visibly AND are flagged by `scan.py` as a "pricing pending (out of scope)" gap that rolls into
  #00's register; span-based suppression prevents generic-pattern duplicate rows.
- **M2+M4** (`f5e675b`): added loadable `refs/render-and-canvas.md` (the render recipe for Phase-7
  subagents; closes the spec's never-created canvas-assembly ref) + R-RENDER-REF-01; trimmed the SKILL
  description 491 -> 265 chars.
- **M6** (`819e88f`): R-RENDER-SAFE-01 locks the render-safety + pricing render/scan path end-to-end
  (subprocess test) so the calibrated behaviors can't regress.

---

## P1 — Decisions that gate going outward / interact with Phase 6

### M1. Confirm tonight's render-safety behavior call (FYI — verify you agree)
**What I did:** the 4 `*_DIAGRAM` slots + `{{PRICE_PENDING}}`/`{{DISCOUNT_PENDING}}` now render as
visible "pending" markers (`md_to_html.py` `INTENTIONAL_PLACEHOLDERS`) instead of hard-failing the
artifact; genuine unknown tokens still hard-fail. **Decision to confirm:** is "render with a visible
*pending* marker" the right outward behavior, or would you rather a pending diagram/price BLOCK the
render so an artifact can never go out half-baked? My recommendation: keep render-safe (a PAM-facing
artifact with one "pending" cell is more useful than no artifact), and let the **publish gate (Phase 6)**
be where "don't push artifacts with open pending markers without explicit OK" is enforced. If you
disagree, it's a one-line revert of the placeholder set.

### M2. (Audit B2) Add `refs/render-and-canvas.md` — the render recipe has no loadable ref
**Issue:** `md_to_html.py`/`canvas.py` are referenced nowhere in `refs/`. The recipe (CLI invocation,
the §6 which-artifacts-get-HTML rule, the regenerate-diagrams-before-render ordering) lives only in
SKILL.md prose. The siblings put this in a loadable ref (pov-builder's `refs/html-output-method.md`)
**precisely so fanned-out subagents have it** — and ps-npi-forge's Phase 7 Deep Build fans to
subagents that won't carry SKILL.md's blurb. **Recommendation:** create `refs/render-and-canvas.md`
before Phase 7 (closes the spec's never-created `canvas-assembly.md`). Could fold into Phase 6.

### M3. (Audit B4 residual) Settle the canonical "pending price" representation
**Issue:** tonight made `{{PRICE_PENDING}}` render-safe (renders as "pending"), but there are still two
price-gap conventions in the codebase: the template tokens vs. `scan.py`'s `$xx` detector (the
uncertainty loop greps for `$xx`, not for the rendered "pending"). So a pending price renders fine but
may not be FLAGGED by the uncertainty loop unless the generator also emits a `$xx`-style marker.
**Recommendation:** pick one — either (a) teach `scan.py` to treat the "pending" price marker as a
price gap, or (b) have the generator fill price cells with `$xx — pending` so the existing scanner
catches it. Low effort once decided; affects whether pricing gaps roll into #00's blocker register.

---

## P2 — Polish / parity (no outward-quality risk, do when convenient)

### M4. (Audit B3) SKILL.md frontmatter description is 491 chars (siblings: 217 / 267)
It enumerates all 11 artifacts inline. Skill descriptions are the matcher signal; both siblings keep
them ~2x tighter. **Recommendation:** trim to the Embedded/OEM-NPI trigger + "family of PS-owned
artifacts + Key Resources canvas," drop the inline 11-artifact list (~250 chars). Light touch.

### M5. Gap-card badge/label pairing reads oddly
A gap card (no `.html` rendered) can show a non-`pending` status badge (e.g. #04 `drafted`) next to
"— not yet generated." Correct behavior (no dead link, real manifest status), but the pairing could
confuse. **Options:** (a) label gap cards by render-state ("not yet rendered" vs "not yet generated"
depending on status), or (b) leave it — it's accurate. Minor.

### M6. (Audit B5) Add validation gates that lock in tonight's decisions
Once M1/M3 are settled, add: (i) a check pinning `md_to_html`'s behavior on an unfilled `*_DIAGRAM`
slot (render-safe), and (ii) a check that the chosen price-pending convention is both render-safe and
scanner-caught. These would prevent regression of tonight's fixes. (Hold until M1/M3 decided so the
checks assert the intended behavior, not today's.)

---

## P3 — Forward (already tracked, listed for completeness)
- **B9 (re-scoped tonight):** Phase 6/7 should ensure #06/#07/#10 diagrams are actually regenerated so
  the canvas shows real diagrams, not perpetual "pending" markers.
- **B3 (price-list spike), B4 (manifest status-validation on load), B5 (ref↔registry slug check):**
  pre-existing backlog, unchanged.
- **Phase-4 note:** entitlement composition is sparse at the Product2 level; a future bundle-walk could
  enrich #06.

---

### What's solid (don't re-investigate — verified tonight)
Voice/register split consistent across all 11 templates + refs + spec; SLDS palette + Salesforce Sans +
Mermaid `%%{init}%%` directive match style-conventions and the siblings exactly; manifest constants ↔
validation registry ↔ template in sync; CI + pre-commit match the sibling pattern; the full effort
renders 8/8 with the calibrated canvas and render-safety working. Suite 36/36, `main` in sync with
origin.
