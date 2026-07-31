# ps-npi-forge

**Version: 0.2.2** — the 15-artifact family with the demand-plan grid and exec infographic, a commercial
business-case layer (internal ASP/penetration/attrition + cross-cloud halo ACV, anchor partner, AE
channel-conflict), a dark visual **merged exec poster** (Vision→Problem→Solution→Outcomes→TAM→Ideal
Partners→Built on Salesforce, projected from #14+#11), clickable/new-tab external links, and a reordered
Key Resources canvas with poster-primary linking. Live diagrams; clean canvas.

Builds a consistent family of Partner-Solutions-owned NPI artifacts (executive summary, brief,
FAQs, license/entitlement details, setup guide, add-on tiering, ideal-partner POV, solution
infographic, marketecture, demand-plan framework, exec infographic) plus a synced Key Resources
canvas, for a single new NPI product (typically an Embedded/OEM SKU modeled on a directly-sold
parent). Built on the skill-forge Tier-3 pattern; sibling to pie-poc-forge.

- **Design spec (0.x reference):** [docs/design-spec.md](docs/design-spec.md)
- **Backlog / next additions:** [BACKLOG.md](BACKLOG.md)
- **Latest end-to-end run:** [docs/superpowers/acceptance/2026-06-24-rebuild-slack-research-13-artifacts.md](docs/superpowers/acceptance/2026-06-24-rebuild-slack-research-13-artifacts.md)

## Using the skill

Start with a one-line request naming the parent SKU you want to base the Embedded/OEM product on:

> **"I'd like to create an ISV Embedded SKU based on the standard Health Cloud SKU."**

The skill opens an effort and asks a short set of follow-ups (one at a time) — none of them block;
an unanswered question becomes a flagged gap, not a stop:

1. **Planned name of the ISV Embedded SKU?** — e.g. *Agentforce for Healthcare*.
2. **Which edition(s)?** — e.g. *EE and UE*.
3. **Required add-ons?** — e.g. *Community Cloud and Community Cloud Plus* (patient/caregiver portals).
4. **Any other add-ons?** — e.g. *none expected*.
5. **Slack channel(s) for the parent SKU?** — e.g. *#help-sell-health-cloud*.
6. **Resource links?** — actual FCD / release-deck / enablement / official-doc URLs. Real links are
   included in the artifacts (official links cited; non-official links recorded as flagged sources).
7. **Anything else to consider?** — shared-org constraints, packageability timing, a pilot customer,
   related efforts, known gaps.

From there the skill drafts → refines → validates the 15 artifacts and assembles the Key Resources
canvas. Full intake detail: [refs/intake-source-map.md](refs/intake-source-map.md). Pricing is out of
scope (left as flagged placeholders); entitlements are drafted from the parent and flagged for human
confirmation. The skill never publishes to Slack without confirmation.

**Single source of record (no duplicated authoring).** Several artifacts are *derived* — generated
FROM another artifact rather than independently researched — so the family tells one story across many
surfaces without drift. The map lives in `scripts/manifest.py` as `DERIVES_FROM`, and
`manifest.generation_order()` orders generation so every source is built before its derivatives:
- **01-brief** (narrative of record) → **00** executive-summary (rollup + manifest blockers/confidence),
  **02** slide-summary, **11** solution-infographic, **14** exec-infographic
- **04**-internal-faq → **05**-external-faq (partner-safe subset)
- **06**-license-entitlements → **07**-addon-tiering (Required tier)

A derived artifact transforms its source (does not re-research it); where the source is silent it flags
a gap. `12`-marketecture, `13`-demand-plan, `03`, `08`, `09`, `10` are authored, not derived. See
[refs/quality-loops.md](refs/quality-loops.md) (Derivation contract) and
[refs/artifact-templates.md](refs/artifact-templates.md) (derivation map).

## Status — 0.2.0 (open for review/testing)

Phases 1–5 are implemented and dogfooded end-to-end (intake → generate → refine → validate → HTML
render → Key Resources canvas), grounded in live Org62 data. **Phase 6** (Slack sync + publish gate)
and **Phase 7** (Deep Build C-mode) are pending — see [BACKLOG.md](BACKLOG.md). This beta is shared
so others can run it and give feedback before those phases land. The validation suite is green (61
checks); the pre-commit hook + CI run it on every change.

### What to test

- Run the intake conversation (above) against a real parent SKU and confirm the 15 artifacts + the
  Key Resources canvas generate, with gaps flagged (not silently dropped).
- Check the artifacts read true to the parent product and the OEM/Embedded motion, and that the
  Next Steps & Blockers register in the executive summary rolls up the real open items with owners.
- Open the **merged exec poster** (`<effort>/canvas/14-exec-infographic-poster.html`) — a dark-themed
  visual "fancy image" poster with 7 panels (Vision → Problem → Solution → Outcomes → Market·TAM →
  Ideal Partners → Built on Salesforce) projected from the #14 and #11 markdown. On the canvas it's the
  primary link on the **Executive Overview** card, with a small "(document)" secondary link.
- Open the **#02 slide deck** (`<effort>/canvas/02-slide-summary-slides.html`) and the **#12
  marketecture** — confirm they read cleanly and the deck renders one slide per section. (#11 solution
  infographic and #14 exec overview also have plain document views; their visual treatment is the merged
  poster above.)
- Confirm external links in the rendered HTML are clickable and open in a new tab (e.g. the official-doc
  URLs in #08 setup guide).
- Confirm pricing stays as flagged placeholders (never an invented number) and that entitlements are
  presented for human confirmation, not asserted.

### Known gaps (beta — feedback wanted)

- **License & entitlement detail (#06 / #07) is thinner than ideal.** Org62 models a SKU's
  entitlement composition sparsely — a single Product2 often returns only one or two grant rows
  (e.g. "EE Sites") — so #06's grant table and #07's tiering are **drafted from what Org62 returns +
  the parent brief, and flagged for human confirmation** rather than asserted as complete. A future
  enhancement may walk a product *bundle* for fuller composition. **This is the area most in need of
  reviewer eyes** — confirm the entitlement/license picture against your own knowledge of the parent
  SKU and flag what's missing.
- **Diagrams populate on a generate-cycle run, not on render** — an un-regenerated diagram slot shows
  a visible "pending" marker rather than the diagram.
- Slack publish and Deep Build are not yet implemented (Phases 6–7).

## Validation

```bash
python3 tests/validate_skill.py
```

Activate the pre-commit hook once per clone:

```bash
git config core.hooksPath .githooks
```
