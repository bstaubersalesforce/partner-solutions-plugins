# Competitive Assessment Pre-Delivery Validation Checklist

Run every check before delivering the Competitive Assessment artifact (.md + .html).

## Structure
- [ ] All four dimensions present: Commercial Model, Ecosystem, GTM Program, Technology
- [ ] Each dimension has a scorecard comparing Salesforce + all three categories (app/low-code, hyperscalers, AI providers)
- [ ] Each dimension has both layers: "for the partner building on it" AND "for the customer buying the result"
- [ ] Each dimension has an in-line Objection → Response pair
- [ ] Synthesis present: strongest arguments + objections likely to land + the honesty note
- [ ] HTML carries the standardized home-page back-link pill (`{{HOME_HREF}}` → `{SLUG}-index.html`); removed if standalone
- [ ] No `{{PLACEHOLDER}}` tokens or `[bracketed placeholder]` text remain in the rendered output

## Fairness (credibility gates — HARD FAIL)
- [ ] **Per-dimension concession:** each of the 4 dimensions names at least one area where a competitor is genuinely stronger — FAIL if any dimension lacks one
- [ ] **Concede-then-counter:** each objection's response concedes the valid part before countering
- [ ] Synthesis includes the honesty note ("where Salesforce is genuinely not the right choice")
- [ ] No vendor-pitch language or unsourced superlatives ("best-in-class", "world-class", "next-gen", "revolutionary") — per SKILL.md Delivery Voice
- [ ] Every scorecard claim is confidence-labeled (`[confirmed from research]` / `[proposed — confirm]` / `[TBD — clarification needed]`) and sourced/attributed
- [ ] POV-named specific competitors appear inside each category (not just generic category names)

## Scope discipline (no overlap)
- [ ] Does not restate Red Team threats (Stage 9 attacks the solution; this compares platforms)
- [ ] Does not restate the partner's license pull-through economics (POV ISV Commercial Model)
- [ ] No dollar/Flex-Credit sizing (that is sf-flex-estimator) — commercial comparison is qualitative
- [ ] Does not restate the core-solution target architecture (Stage 16)

## Failure → Repair
**Missing concession in a dimension:** add a genuine competitor-strength line; if none is real, the dimension's framing is biased — rebalance it.
**Objection without concession:** rewrite the response to acknowledge the valid part first.
**Unfilled token / placeholder:** fill from POV + `refs/competitive-landscape.md` or mark `[TBD — clarification needed]`.
**Vendor-pitch language:** replace superlatives with a number, a named source, or explicit uncertainty.
