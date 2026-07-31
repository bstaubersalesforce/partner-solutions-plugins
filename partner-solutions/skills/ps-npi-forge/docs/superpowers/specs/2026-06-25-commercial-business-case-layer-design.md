# ps-npi-forge — Commercial Business-Case Layer (Design)

**Date:** 2026-06-25
**Status:** Approved for planning
**Depends on:** the demand-plan & GTM enhancements increment (`2026-06-25-demand-plan-enhancements`,
family 13→15) must land and review clean first — this increment edits #07, #13, #14 which that work
creates/changes.
**Source:** review feedback from Harman (PAM, commercial team) on the Healthcare OEM effort, 2026-06-25.

## Summary

Five enhancements that turn the artifact family from a *demand/GTM* set into one that carries a real
**commercial business case** for the PAM/commercial team. All five either deepen artifacts the prior
increment is building (#07, #13, #14) or touch adjacent existing artifacts (#10, #03/#04). **No new
artifacts** — the family stays at 15. (Harman's sixth point — FSC/AutoCloud NPI *precedent/lessons* —
is deliberately held as backlog item **B21** for its own cross-effort design; it is NOT in this spec.)

| Ref | Feedback (Harman) | Change | Artifact(s) |
|-----|-------------------|--------|-------------|
| B22 | Business case is TAM-only; missing internal ASP, penetration, attrition | Add ASP / penetration / attrition so #13 models TAM × ASP × penetration − attrition, not just TAM | #13 |
| B23 | No cross-cloud halo-revenue story | Frame standard ISV add-ons as **halo ACV the PAM gets credit for** (Data Cloud / MuleSoft / Tableau Next); add a halo column to the demand grid | #07, #13 |
| B24 | Proof points are existing SF customers | Proof/outcomes must be **partner-driven forecasted deals**, not existing direct-SF logos | #14, #00, #11 |
| B25 | No anchor partner | Add an **anchor / gold-standard partner archetype** (the FSC/nCino model) | #10 |
| B26 | AE channel-conflict risk unaddressed | Add **non-compliant-resale risk + get-ahead guidance** for the account team | #03, #04 |

## Decisions (from this morning's clarification)

- **Pricing guardrail boundary (the key design decision).** The skill's hard rule stays: **list /
  quote / discount pricing is out of scope and always renders as `{{PRICE_PENDING}}` /
  `{{DISCOUNT_PENDING}}`.** This increment adds a *narrow, explicit* carve-out: **internal
  business-case inputs — ASP, penetration rate, customer attrition, and halo ACV — are permitted as
  flagged estimates**, confined to the demand-plan / business-case artifact (#13), sourced from
  internal Salesforce insights, and always carrying an `estimate` flag + confidence. They are
  *planning inputs*, not a partner-facing quote. `refs` and the R-REF-02 wording are updated to draw
  this line precisely so the guardrail stays coherent.
- **No new artifacts.** Family stays 15. All changes are sections/columns/tokens in existing templates.
- **Point 6 (NPI precedent/lessons) is out of scope** — held as B21 (cross-effort lessons layer;
  FSC OEM + AutoCloud-for-Dealer + others).
- **Sequencing:** spec now (no file edits); execute after the 13→15 increment lands clean.

## The pricing-guardrail carve-out (precise wording)

Today R-REF-02 asserts SKILL.md's refusal section contains the literal strings `pricing`,
`non-official`, `read-only`, `without confirmation`. SKILL.md currently says pricing is out of scope.

**New rule to encode** (SKILL.md refusal/scope section, and `refs/intake-source-map.md` /
`refs/artifact-templates.md` where pricing-scope is described):

> **Pricing & financial inputs.** Partner-facing **list, quote, and discount pricing remain out of
> scope** — those cells always render as `{{PRICE_PENDING}}` / `{{DISCOUNT_PENDING}}`. **Internal
> business-case planning inputs** — average selling price (ASP), penetration rate, customer
> attrition, and cross-cloud halo ACV — **are in scope as flagged estimates** in the demand-plan /
> business-case artifact (#13) only, sourced from internal Salesforce insights, each carrying an
> `estimate` flag and a confidence. They are planning inputs, never a partner quote.

R-REF-02 must continue to find its four literal needles — keep the word `pricing` and the phrase
`out of scope`; add the carve-out sentence after them. (No test rule is *removed*; one is refined and
a new assertion is added — see Testing.)

## B22 — Internal business case in #13 (ASP / penetration / attrition)

`templates/13-demand-plan.md` gains a business-case section after "Segment & TAM basis":

```
## Internal business case (estimates)

Internal planning inputs — flagged estimates from internal Salesforce insights, not partner-facing
pricing. Each is an estimate pending commercial-team confirmation.

{{BUSINESS_CASE_TABLE}}
```

- `{{BUSINESS_CASE_TABLE}}` columns: Segment | TAM (est.) | ASP (est.) | Penetration % (est.) |
  Attrition % (est.) | Modeled ACV (est.). The modeled figure is explicitly an estimate
  (TAM × penetration × ASP, net of attrition) — narrative, not a computed guarantee.
- Voice: narrative (the artifact's register).
- All values carry the `estimate` framing; absent values surface as gap-banner items, per convention.

## B23 — Halo revenue (#07 framing + #13 column)

- **#07** (`templates/07-addon-tiering.md`): the standard-ISV-add-on catalog section (added in the
  prior increment) gets a framing line and a column making explicit these are **halo ACV the PAM is
  credited for** — e.g., the FSC-at-AgFirst precedent generated ~$400k MuleSoft + ~$150k Tableau ACV
  alongside the OEM licenses. Add a "Halo ACV (est.)" column to that catalog table (`{{PRICE_PENDING}}`
  stays for list price; halo ACV is an internal estimate per the carve-out).
- **#13**: the demand grid (`{{DEMAND_GRID}}`) gains a **Halo ACV (est.)** column so each segment row
  shows the cross-cloud pull (Data Cloud / MuleSoft / Tableau Next) alongside the core/required and
  add-on columns. Updated full row shape documented in the template's grid intro.

## B24 — Proof points = forecasted partner deals (#14 + #00 + #11)

- **#14** (`templates/14-exec-infographic.md`): no token rename, but the section framing / template
  guidance for the use-cases and (if present) any proof content states proof points must be
  **partner-driven forecasted deals**, not existing direct-Salesforce customer logos.
- **#11** (`templates/11-solution-infographic.md`) `{{OUTCOMES_PANEL}}` and **#00**
  (`templates/00-executive-summary.md`) outcomes/proof content: same guidance — frame outcomes as
  forecasted partner-sourced deals. This is **guidance/framing in the template prose**, not a
  structural token change, so it does not disturb R-RENDER-01 fill-set or R-TPL-02.

## B25 — Anchor partner archetype (#10)

`templates/10-partner-profile-pov.md` gains an anchor-partner subsection (or extends
`{{ARCHETYPES}}`) naming the **gold-standard / anchor partner** the cloud should model — for HC, the
FSC/nCino precedent. New token `{{ANCHOR_PARTNER}}` if a dedicated section is added; if folded into
`{{ARCHETYPES}}`, no new token. **Decision for the plan:** add a dedicated
`## Anchor partner (the model to replicate)` section + `{{ANCHOR_PARTNER}}` token (cleaner, explicit,
and the anchor-partner concept is reusable across efforts).

## B26 — AE channel-conflict guidance (#03 + #04)

- **#03** (`templates/03-internal-enablement.md`): add a section on **AE channel conflict** — the risk
  that the direct account team is already positioning SKUs for non-compliant resale, and get-ahead
  guidance (engage early, clarify OEM-vs-direct motion boundaries). New token
  `{{CHANNEL_CONFLICT}}`.
- **#04** (`templates/04-internal-faq.md`): add a Q&A entry on the same — "What if the AE is already
  positioning these SKUs for resale?" Reference voice. Likely folds into the existing FAQ token if #04
  uses a single body token; otherwise a new `{{CHANNEL_CONFLICT_FAQ}}` token.
  (The plan will confirm #04's token structure before deciding new-token vs. in-body.)

## Architecture & invariants (unchanged from the skill's model)

Every change rides the same registry-derived discipline:
- **No registry change** (family stays 15) — so R-TPL-01, R-MANIFEST-01/05/06, R-DOC-01 counts are
  untouched. (This is why the increment is lighter than the 13→15 one.)
- **New tokens** (`{{BUSINESS_CASE_TABLE}}`, halo-ACV columns, `{{ANCHOR_PARTNER}}`,
  `{{CHANNEL_CONFLICT}}`, possibly `{{CHANNEL_CONFLICT_FAQ}}`) must be added to `render.py`'s fill in
  the R-RENDER-01 test loop (it auto-covers any UPPER_SNAKE token in a template, so the generic
  full-fill assertion catches them; add explicit presence pins as in the prior increment's Task 7).
- **No new `*_DIAGRAM` tokens** anticipated (reuse existing diagram slots) — so `INTENTIONAL_PLACEHOLDERS`
  is unchanged. If the plan adds a business-case diagram, it must be registered there (B-class rule).
- **R-TPL-02** shared-convention lines stay verbatim in every edited template.
- **Token hygiene (R-TEST-02)**: all new tokens UPPER_SNAKE.
- **Voice**: #13/#14/#11/#00/#10 narrative (unchanged); #03/#04 reference (unchanged).

## Testing

- **Refine R-REF-02**: keep the four literal needles; add an assertion that SKILL.md's pricing rule
  states BOTH that list/quote pricing is out of scope AND that internal business-case inputs (ASP /
  penetration / attrition / halo) are allowed as flagged estimates — so the carve-out can't silently
  revert.
- **R-RENDER-01**: extend the new-token presence pins (as the prior increment did) for
  `{{BUSINESS_CASE_TABLE}}`, `{{ANCHOR_PARTNER}}`, `{{CHANNEL_CONFLICT}}`, and the halo columns.
- **New targeted assert** (business-case discipline): #13 carries the ASP / penetration / attrition /
  halo-ACV columns AND the "estimates / not partner-facing pricing" framing — so the guardrail intent
  survives future edits.
- Full suite green (`python3 tests/validate_skill.py`) + dogfood render of the edited artifacts on the
  Healthcare effort (zero surviving tokens; #13 business-case + halo render; canvas cards intact).

## Out of scope

- Partner-facing list/quote/discount pricing (stays `PENDING`).
- New artifacts (family stays 15).
- **NPI precedent / cross-effort lessons layer (B21)** — held for separate design.
- Phase 6/7.

## Risks / watch-items

- **Guardrail coherence is the central risk.** The carve-out must be unambiguous: planning *estimates*
  in #13 only, vs. partner-facing *pricing* everywhere (PENDING). The refined R-REF-02 is the guard;
  the template framing lines are the reinforcement.
- **Sequencing:** this spec references #07/#13/#14 as the prior increment leaves them. Plan-writing
  must read those templates *after* the 13→15 branch merges/lands, so token names and section anchors
  are real, not assumed.
- **#04 token structure** (single body token vs. per-section) is unconfirmed until plan-time; the plan
  resolves new-token-vs-in-body by reading the actual template.
