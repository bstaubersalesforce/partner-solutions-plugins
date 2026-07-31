# Artifact templates

The 15 artifact skeletons live in `templates/<slug>.md`, one per `ARTIFACT_REGISTRY` slug. Each is
a markdown file with `{{UPPER_SNAKE}}` tokens the generator (Phase 3b) fills from the effort
manifest and sources. This ref documents the shared conventions; the per-artifact grammar is in
each template file.

## Shared conventions (every template)

- **Voice comment** (top, HTML comment): narrative artifacts (00, 01, 02, 03, 05, 10, 11, 12) declare
  the first-person exec/architect McKinsey register; reference artifacts (04, 06, 07, 08, 09) declare
  the factual register. See [voice-and-style.md](voice-and-style.md).
- **Gap-banner header** (after the H1): a blockquote carrying `{{STATUS}}`, `{{CONFIDENCE}}`,
  `{{CONFIDENCE_RATIONALE}}`, and `{{GAP_BANNER}}`. `{{GAP_BANNER}}` renders "No open gaps." or a
  bulleted list, each `Gap: <item> -- <next step>; owner: <owner>`. Gaps are first-class: a missing
  Template ID, a PENDING price, an ungrounded claim each surface here and roll up into 00's Next
  Steps & Blockers register.
- **Footer**: a horizontal rule, then `{{SOURCES}}` and the confidence line again. Sources are what
  the claim-verification loop checks against (Phase 3b).
- **Tokens are UPPER_SNAKE.** Price/discount cells are literal `{{PRICE_PENDING}}` /
  `{{DISCOUNT_PENDING}}` -- pricing is out of scope, never a computed number.

## The registry

| Slug | Register | Notes |
|------|----------|-------|
| 00-executive-summary | narrative | front door: vision, messaging hierarchy (key message → product → 4 pillars → features), top 3-6 use cases, IPP summary, Next Steps & Blockers, rollup |
| 01-brief | narrative | the product narrative + the Key Use Cases grid (Category/Opportunity/Example/Key Features/What Partners Package) |
| 02-slide-summary | narrative | one-screen summary derived from 01 |
| 03-internal-enablement | narrative | positioning, motion rules, entitlement implications + AE channel-conflict |
| 04-internal-faq | reference | PS/NPI Q&A incl. OEM/VAR/shared-org/packageability + AE channel-conflict |
| 05-external-faq | narrative | partner-facing, safe subset derived from 04 |
| 06-license-entitlements | reference | licenses/PSLs/features/storage from parent, deltas flagged |
| 07-addon-tiering | reference | Required/Recommended/Optional, minimalist + standard ISV add-on / halo-ACV catalog |
| 08-setup-guide | reference | Basic Info/TrialForce/2GP scratch/managed-pkg; official docs only |
| 09-org-provisioning-validation | reference | static Template-ID check + optional live org diff |
| 10-partner-profile-pov | narrative | whitespace POV; Tier B always, Tier C opt-in + anchor partner |
| 11-solution-infographic | narrative | single-screen visual: problem -> solution -> outcomes -> market -> built-on-Salesforce |
| 12-marketecture | narrative | layered marketecture: partner solution over the agent/platform/data/trust layers |
| 13-demand-plan | narrative | segments × SKU-bundle grid; IPP+TAM-keyed; conditional add-ons only-if-required + internal business case (ASP/penetration/attrition est.) |
| 14-exec-infographic | narrative | exec single-screen: vision → value prop → use cases → ideal partners → TAM |

## Derivation map

Six artifacts are **derived** -- they transform a single source artifact rather than re-researching:

- **00-executive-summary** -- rollup of 01-brief + manifest Next Steps & Blockers + confidence
- **02-slide-summary** -- condense 01-brief to one-screen slide deck
- **05-external-faq** -- partner-safe subset of 04-internal-faq (internal-only content excluded)
- **07-addon-tiering** -- Required tier grounded in 06-license-entitlements; Recommended/Optional are 07-authored
- **11-solution-infographic** -- render 01-brief's problem/solution/outcomes/built-on
- **14-exec-infographic** -- render 01-brief's exec narrative as leadership poster

Machine-readable source: `scripts/manifest.py` constant `DERIVES_FROM`. The generator respects this: sources are drafted before their derivatives (via `generation_order()`), so a derivative can read its source's locked sections.

## How the generator uses these

The generator cycle (draft → refine → validate, per [refs/quality-loops.md](quality-loops.md))
fills the tokens: draft from knowledge, refine against sources (recording them in `{{SOURCES}}`),
then the quality loops set `{{CONFIDENCE}}` + `{{CONFIDENCE_RATIONALE}}` and populate
`{{GAP_BANNER}}`.
