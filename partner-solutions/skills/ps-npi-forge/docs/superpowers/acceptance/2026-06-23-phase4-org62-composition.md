# Phase 4 Acceptance — Live Org62 entitlement composition for the pinned Healthcare OEM SKU

**Date:** 2026-06-23
**Effort:** `summer-26 / agentforce-healthcare-oem`
**Run mode:** Standard (B), controller-driven. Org62 live (read-only, `org62` alias, as `bstauber@salesforce.com`).
**Effort data:** `/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/`
(outside the skill repo).

## What ran — the real two-step pull

**Step 1 — resolve (live).** Queried active OEM Health Cloud `Product2` candidates:

```
SELECT Id, Name, ProductCode, Family FROM Product2
WHERE Name LIKE 'Health Cloud - Service%OEM' AND IsActive=true ORDER BY Name
```

Returned **1 candidate**, which the controller pinned (the human-pin step):
`Health Cloud - Service - Unlimited Edition - OEM` — Id `01t0M0000074j9BQAQ`,
ProductCode `OPT-SS-UE-HLS-OEM-ASP`, Family `Custom Cloud`. (Note: The plan assumed EE and
anticipated 2 candidates [EE+UE]; the live result set returned only the UE OEM SKU, which was
pinned — the human-pin step adapting to real data. Fixtures still carry both EE+UE samples.)

**Step 2 — compose (live).** Pulled the grant rows for the pinned Id from
`sfbase__EntitlementDefinitionMap__c` (saved to `sources/org62-entitlement-composition-ue-oem.json`),
then parsed via the real `scripts/org62.py` `parse_composition`:

| Grant | Category (derived) | Cloud | Quantity | Service-enabling | Add-on SKU |
|-------|--------------------|-------|---------:|------------------|------------|
| UE Sites | Feature | Sites | 1,000,000 | True | -- |

**Composition is genuinely sparse — one grant row.** This is how Org62 models this OEM SKU at the
Product2 level; it is not a parser failure. The design anticipated this: the thinness is flagged for
human confirmation, never papered over.

## #06 regenerated through the cycle — golden signals (verified in the rendered bytes)

- The **entitlement-grant table renders** with the derived **Category** column (UE Sites -> Feature,
  cloud Sites) and the pinned product code `OPT-SS-UE-HLS-OEM-ASP`. `render` left **no surviving
  `{{TOKEN}}`** (`unfilled == []`).
- The **sparse composition is flagged for human confirmation, not asserted** as complete: the
  completeness and uncertainty quality loops both record `flag`; the gap banner and
  Human-confirmation checklist call out "1 grant pulled -- confirm completeness; owner PMO/licensing".
- The **naming delta** "Health Cloud" -> "Agentforce for Healthcare" still flags (DELTAS_AND_NAMING).
- **No price/discount asserted** (pricing out of scope).
- **#06 confidence 0.55** (status `drafted`) -- a confirmed-but-thin pull, up from the Phase-3b
  flagged-gap baseline (0.45), still < 1.0 pending human confirmation. The effort's overall
  `overall_confidence` stays **0.35** (the weighted floor, driven by #09's Template-ID blocker -- #06
  is no longer the floor concern).

## Category derivation (our interpretation, surfaced as a column)

`org62.py` `categorize(grant_name, cloud)` derived `Feature` for "UE Sites"/cloud "Sites" via the
documented cloud->category map. This is explicitly **our interpretation** surfaced as a column, not
Org62's native classification (Org62 classifies by cloud/RecordType). Labelled as derived in the #06
template body.

## Verdict

**PASS.** The real two-step Org62 pull (resolve -> human-pin -> compose) works end-to-end against live
production data; `parse_composition` maps the real `sfbase__EntitlementDefinitionMap__c` shape; #06
renders a faithful grant table with the derived category column; the sparse composition and naming
delta are flagged for human confirmation rather than asserted. B1 is closed: the schema is pinned, the
parser is real-fixture-tested in CI, and a live pull is the capability-gated manual step. The mechanical
parsers/template/sections.py are CI-gated by the 30-check suite; this run is the live acceptance.

## Rough edges / follow-ups (for BACKLOG)

- **Composition is sparse at the Product2 level.** A single SKU often carries 1-2 grant rows; the rich
  per-product license/PSL/feature/storage breakdown the original spec imagined is not how Org62 models
  this. A future enhancement could walk a product *bundle* (related products) to assemble a fuller
  composition -- noted as out of Phase 4 scope (§9 of the spec). For now, sparse-and-flagged is the
  honest behavior.
- The `categorize` cloud->category map is small and deliberate; if more clouds appear in real pulls,
  extend the documented table (it degrades to "Other", never crashes).
