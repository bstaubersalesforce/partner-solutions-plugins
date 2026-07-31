# POV Presentation Pre-Delivery Validation Checklist

Run every check before delivering the POV Presentation HTML. If any check fails, repair before delivering.

## Structure
- [ ] All 12 slides present: Cover, Problem Space, Vision, Strategic Direction, Product Pillars & Positioning, Solution, Use Cases, Target Markets & Personas, Solution Alignment, MVP & Roadmap, Commercial Model & Architecture, Recommendation
- [ ] No unfilled `{{PLACEHOLDER}}` tokens remain (scan the output)
- [ ] `{{OPPORTUNITY_STAGE}}` is the code+name (e.g. `03-Contract`), not a number
- [ ] Home-page back-link present (`class="home-link"`) when part of a package; the anchor line is removed entirely when the deck is standalone

## Faithfulness to the approved POV (this is a render, not a rewrite)
- [ ] Vision slide quotes the POV Vision Statement verbatim — no new vague language ("transform," "revolutionize")
- [ ] Strategic Direction + Product Pillars slides render only what the POV's **Product Strategy** section states (thesis, pillars, positioning, moat, platform bet) — no invented pillars or vague "be the leader" claims
- [ ] Use-case slides preserve the persona + outcome of each POV use case; do not invent a 3rd use case if the POV has fewer (drop the unused card instead)
- [ ] Benefits, KPIs, and market figures match the POV — no metric is inflated or presented as achieved when the POV labels it a target
- [ ] Named proof points on the Recommendation slide are the POV's actual named pilot/sponsor — never fabricated
- [ ] Confidence score matches the POV's stated confidence
- [ ] Architecture pills name specific SF clouds/SKUs from the POV (never "Salesforce platform"); drop unused pills rather than inventing one
- [ ] Any POV gap appears as "TBD" with owner — never filled with a guess

## Failure → Repair
**Unfilled token:** Fill from the POV, or set to "TBD" with owner attribution.
**Invented content:** Remove. The deck may only render what the approved POV states.
**Fewer than 3 use cases / 3 SF deps:** Delete the unused card/pill `<div>`/`<span>` — never leave a `{{...}}` token.
