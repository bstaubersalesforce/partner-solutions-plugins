# Rebuild — Slack intake + deep research + 13 artifacts + slide format

**Date:** 2026-06-24
**Effort:** `summer-26 / agentforce-healthcare-oem` (rebuilt from enriched sources)
**Trigger:** Brandon — capture Slack channel detail (Template ID via #temp-aug26-npi-af4hc) + link
decks/resources; do fresh deep research from the ISV-program + Salesforce-positioning lens (NOT the
hand brief), build out all resources even if pending; add a slide render format; add two new
artifacts (solution infographic + marketecture, modeled on pov-builder) with canvas sections; async.

## What changed in the skill (committed before the rebuild)

- **Registry 11 -> 13:** added `11-solution-infographic` and `12-marketecture` (templates modeled on
  pov-builder's infographic/marketecture, following the shared gap-banner/footer/VOICE grammar). New
  diagram tokens `{{INFOGRAPHIC_DIAGRAM}}` / `{{MARKETECTURE_DIAGRAM}}` wired into render-safety,
  the mermaid ref, and the canvas LABEL/KIND/SUMMARY. (commit 77906b8)
- **Slide render format:** new `scripts/slide_deck.py` — an SLDS slide deck (cover + one slide per H2
  section, 1280x720, print-to-PDF, mermaid live via CDN), modeled on pov-builder's
  pov-presentation.html. `02-slide-summary` renders both a document HTML and a `-slides.html` deck.
  Gated by R-SLIDE-01; documented in refs/render-and-canvas.md sec 2b + SKILL.md. (commit 7c0cb56)
- **Suite 40 -> 41** (R-SLIDE-01 net-new; R-MD2H-02 / R-MERMAID-01 / R-RENDER-REF-01 extended).
  Batching guidance updated 11 -> 13 artifacts.

## Intake (new sources, captured to the effort)

- **`sources/slack-intake.md`** — via Slack MCP (live read) + Brandon's pasted channel summary:
  - `#temp-aug26-npi-af4hc` (C0B8ZLM8MEJ): **Template ID = a standard Health Cloud EE+UE template,
    IN PROGRESS** (Manish Jiandani / John Chung), provided to ISVs for DevHub/org creation with the
    full SKU definition, to provision orgs + TSOs. Plus the **scratch-org def feature-parameter
    starting set** (`EnableSetPasswordInApi, EinsteinGPT, EnableAIGenerative, SalesforceAgent,
    Einstein1AIPlatform` + `aiSettings: enableEinsteinGPT/enableAgentforce`) — this fills the #08 gap
    the prior build flagged, marked best-guess to confirm.
  - Harvested **real resource links** from `#help-sell-health-cloud` (Agentforce Health Resources
    Canvas, Enablement Hub, Summer '26 release notes on help.salesforce.com, First Call Deck, public
    pricing page + datasheet, external demo, use-case pages) — linked into the artifacts.
- **`sources/deep-research.md`** — fresh ISV/OEM + Salesforce-positioning research (199 lines,
  grounding-tagged [SOURCED]/[INFERRED]/[PENDING], ~55 named resources). Key findings: the 2GP
  managed-package OEM motion (`healthcloudext`, FHIR R4) with the **Agent-Script-not-yet-packageable**
  caveat; OEM-vs-ISVforce is a licensing (CRM-object) distinction; **standard OEM SKUs likely do NOT
  include Health Cloud entitlement by default** (the key NPI commercial question); the whitespace
  thesis grounded in Deloitte/KLAS + FQHC/SDOH/behavioral-health/RPM segment data; conservative
  HIPAA-ready/Trust-Layer framing.
- Org62 (live, read-only): OEM editions + Community add-on SKUs + entitlement composition (unchanged
  from prior pull, refreshed).

## Batched generation — no timeout

Per the batching discipline (refs/quality-loops.md): **four sequential batches**, each writing files
immediately, updating only its own manifest slots — A (01/06/07), B (04/08/09), C (02/03/05/10),
D (11/12 then 00 last). All completed cleanly; **no timeout** (the original failure mode).

## Golden signals — verified in the bytes

- **13/13 artifacts** generated; only the intended placeholders (`*_DIAGRAM`, price) remain unfilled.
- Overall confidence **0.35** (floor = #09); all four loop verdicts set on every artifact.
- **Template-ID blocker** (now grounded in the real channel facts) traces #08 + #09 -> #00's register
  as the #1 blocker (owner Manish Jiandani / John Chung); #09 BLOCKED.
- **#08 scratch-org features** now carry the Slack-sourced starting feature set (prior build's gap).
- **#06** surfaces the "does the OEM SKU include Health Cloud entitlement?" question as the key
  human-confirm item, with the real Org62 grants + naming-churn delta.
- **#01 / #05** link the real resources (official cited; #05 a clean safe subset, public links only).
- **New artifacts:** #11 infographic (problem/solution/outcomes/market/built-on panels) and #12
  marketecture (partner/agent/platform/data/trust layers) both grounded in the research, with their
  diagram slots pending.

## Render + canvas

Rendered 10 document HTML + the **#02 slide deck** (`02-slide-summary-slides.html`, 5 slides);
`04/08/09` stay MD-only. The canvas assembles **13 cards** (incl. the two new artifacts, with the
sibling card chrome), cards above the blocker register, #09 at the 0.35 floor, escaping intact. The
named diagram slots render as "pending" markers (regenerate-before-final per B9).

## Verdict

**PASS.** The skill now ingests Slack channel detail and research-grounded sourcing, produces a
13-artifact family (incl. infographic + marketecture) plus a slide-deck render, and assembles the
canvas with the new sections — all batched without timeout, every uncertainty flagged. Suite 41/41.

## Follow-ups (BACKLOG)
- The named diagrams (#00/#06/#07/#10/#11/#12) populate on a generate-cycle run; for a final canvas,
  regenerate them so real diagrams replace the "pending" markers (B9).
- The Template ID + the OEM-SKU-Health-Cloud-entitlement question are the two live NPI blockers to
  close with Manish/John + PAM.
