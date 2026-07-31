# Investor Presentation Pre-Delivery Validation Checklist

Run every check before delivering the Investor Presentation HTML.
If any check fails, repair before delivering.

## Structure
- [ ] All 10 slides present: Cover, Problem, Solution, Market, Product, Traction, Business Model, Team, Partnership, Next Steps/Ask
- [ ] No unfilled `{{PLACEHOLDER}}` tokens remain (scan the output)
- [ ] Opportunity-stage tokens correct: `{{OPPORTUNITY_STAGE}}` is the code+name (e.g. `02-Assess`), not a number; `{{OPPORTUNITY_STAGE_LABEL}}` is <5 words; `{{CONTRACT_TARGET_DATE}}` is a date or "TBD"

## Content integrity (no invented investor claims)
- [ ] Market slide cites a named analyst source for the size/CAGR figure — not an unattributed number
- [ ] Traction slide lists only real named customers/awards from research — no fabricated logos
- [ ] Business Model names the commercial type and pull-through SKUs; ACV ranges are labeled as estimates if not confirmed
- [ ] Any POV gap is shown as "TBD" with an owner — never filled with a guessed figure
- [ ] Team slide uses real founder names/credentials from research

## Failure → Repair
**Unfilled token:** Fill from POV data, or set to "TBD" with owner attribution.
**Unattributed market figure:** Pull the sourced figure from the matched `refs/verticals/` file or flag "TBD — owner."
**Fabricated traction:** Remove. Only named, sourced customers/awards may appear.
