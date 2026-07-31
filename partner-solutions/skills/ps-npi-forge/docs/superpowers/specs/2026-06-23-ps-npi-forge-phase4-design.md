# PS-NPI-FORGE Phase 4 — Live Org62 entitlement composition (#06/#07) + sections.py hardening

**Date:** 2026-06-23
**Author:** Brandon Stauber (with Claude Code)
**Status:** Approved for planning
**Builds on:** Phase 3b (the generate->refine->validate cycle, `org62.py` parser stub, `refs/org62-entitlements.md` query-spine, the placeholder fixture). Closes design-spec.md §4 / §9 / BACKLOG **B1**, and folds in the `sections.py` footer-detection fix deferred from the Phase 3b final review.

---

## 1. Scope & boundary

Phase 4 closes **B1**: pull the *real* parent-SKU entitlement composition from live Org62 (read-only)
and feed artifacts **#06 (license & entitlement details)** and, via #06, **#07 (add-on tiering)** --
replacing the Phase-3b placeholder schema with the schema that actually exists in Org62. It also folds
in the deferred **`sections.py` footer-detection fix** (Phase 3b final-review Important #1).

**In scope:** the two-step Org62 pull (resolve -> compose), the parser extension, the #06 template
revision to a faithful entitlement-grant table, the `refs/org62-entitlements.md` rewrite to the real
schema, the `sections.py` hardening, validation growth, and a live-pull acceptance for the Healthcare
effort.

**Explicitly out of this phase (unchanged):** web research / Slack sync (Phase 6), canvas HTML/Mermaid
render (Phase 5), Deep Build C-mode (Phase 7), pricing/discount determination (out of scope entirely),
live Org62 *writes* (read-only always).

This is a focused phase. The live pull stays a **capability-gated manual step** (no org reachable ->
flagged gap, never blocked -- the Phase-3b graceful-degradation path is preserved).

## 2. The real Org62 schema (discovered live, read-only, this session)

The Phase-3b placeholder assumed four clean child relationships
(`Licenses__r`/`PermissionSetLicenses__r`/`Features__r`/`Storage__c`). **Those do not exist.** The
true model, confirmed against live Org62:

- **`Product2.sfbase__ProductEntitlements__r` -> `sfbase__EntitlementDefinitionMap__c`** is the
  composition. Each row is one *grant*, with fields:
  - `EntitlementDefinitionName__c` (the grant name, e.g. "EE Sites")
  - `sfbase__EntitlementDefinition__r.RecordType.Name` (the *cloud* / platform classification:
    `Sites`, `force.com`, `ExactTarget`, `Mulesoft`, `CommerceCloud`, `Slack`, `DMP / Data Studio`,
    `Tableau`, ...)
  - `sfbase__EntitlementDefinition__r.UsageType__r.Name`
  - `sfbase__Quantity__c` (e.g. 500000), `sfbase__ServiceEnabling__c` (bool)
  - `EntitlementTreatment__c`, `UsageModel__c`
  - `AddOnSKU__r.Name` (links a grant to an add-on SKU, when present)
- Classification is by **cloud/RecordType**, *not* by License/PSL/Feature/Storage.
- **Real OEM SKUs exist:** `Health Cloud - Service - Enterprise Edition - OEM`
  (ProductCode `OPT-SS-EE-HLS-OEM-ASP`), `Health Cloud - Service - Unlimited Edition - OEM`
  (`OPT-SS-UE-HLS-OEM-ASP`), plus VAR variants. Family `Custom Cloud`.
- **Composition is genuinely sparse:** an OEM Health Cloud SKU typically carries ~1-2 entitlement-map
  rows (e.g. "EE Sites", qty 500,000, cloud=Sites, service-enabling=true). The rich four-bucket payload
  the original spec imagined is not how Org62 models this at the SKU level. **The design treats
  thinness as normal and leans on gap-flagging + human confirmation.**
- **Names are ambiguous:** plain "Health Cloud - Enterprise Edition" returned **0** entitlement-map
  rows; the entitlement-bearing SKU is the specific "...Service... - OEM" variant. This is why a human
  must pin the right Product2 (see §3).

## 3. Two-step pull with a pinned-Id escape hatch

- **Step 1 -- resolve:** `sf data query --json` for candidate `Product2`
  (`SELECT Id, Name, ProductCode, Family FROM Product2 WHERE Name LIKE '<parent>%' AND IsActive=true`).
  Present the candidates so a **human picks the right SKU**. Because names are ambiguous, the skill
  must not auto-pick.
- **Pinned-Id escape hatch:** a known `Product2` Id can be passed directly, skipping Step 1 entirely.
- **Step 2 -- compose:** `sf data query --json` on `sfbase__EntitlementDefinitionMap__c`
  `WHERE sfbase__Product__c = '<pinned Id>'` (or `sfbase__Product__r.Name = '<resolved name>'`),
  selecting the §2 fields and traversing to `sfbase__EntitlementDefinition__r.RecordType.Name` /
  `UsageType__r.Name` / `AddOnSKU__r.Name`.
- Both calls are **read-only** against the `org62` alias (env `ORG62_ALIAS`, default `org62`), session
  identity -- the `team-projects` pattern. Capability-gated: no org -> #06 falls back to paste/knowledge
  at lower confidence with a flagged gap. **Pin-before-assert** also satisfies the refusal rule (a human
  confirms which product before the skill asserts its entitlements).

## 4. Parser & the #06 representation

### 4.1 `scripts/org62.py` (extend; stdlib-only, pure, never raises)

- `parse_candidates(sf_json) -> list[dict]` -- the Step-1 resolve parser. Each: `{id, name,
  product_code, family}`. Empty/malformed -> `[]`.
- `parse_composition(sf_json) -> list[dict]` -- the Step-2 parser. Each grant:
  `{grant, cloud, usage_type, quantity, service_enabling, treatment, usage_model, addon_sku, category}`.
  Empty/malformed -> `[]` (carry the Phase-3b `isinstance`/non-dict guards; never raises).
- `categorize(grant_name, cloud) -> str` -- **derived in Python** from a small, documented mapping
  table; returns one of `License` / `PSL` / `Feature` / `Storage` / `Add-on` / `Other`. This is
  explicitly *our interpretation* of Org62's cloud/RecordType + name, surfaced as a column -- not
  Org62's native shape. The mapping table lives in `org62.py` and is documented in the ref.
- The existing `parse_entitlements` (the four-bucket Phase-3b parser) is **removed/replaced** -- it
  encoded the wrong schema; keeping it would mislead. R-ENT-01 is rewritten accordingly.

### 4.2 #06 template revision

The Phase-3a `templates/06-license-entitlements.md` `## Licenses` / `## Permission Set Licenses`
/ `## Features` / `## Storage` sections are replaced by a faithful **entitlement-grant table** plus the
retained `## Naming differences & deltas vs. parent` and `## Human-confirmation checklist`. The grant
table columns: **Grant · Category (derived) · Cloud · Quantity · Service-enabling · Add-on SKU**. The
shared gap-banner header, sources/confidence footer, and the `VOICE: reference` comment are **preserved
verbatim** so R-TPL-01/R-TPL-02 stay green. New body tokens (e.g. `{{ENTITLEMENT_GRANTS_TABLE}}`)
follow the UPPER_SNAKE convention (R-TEST-02) and become part of the render fill-set (R-RENDER-01).
This is a Phase-3a template change: on the next effort run, #06 regenerates in the new shape (expected).

## 5. `sections.py` footer-detection hardening (deferred Phase-3b fix)

`split()` currently breaks at the **first** standalone `---`, so a human's in-body thematic break
truncates the split and can silently drop a later edited section (Phase-3b final review, Important #1).
Fix: the footer is the `---` that **immediately precedes the `**Sources:**` line** (the artifact footer
block), not merely the first `---`. Everything before it is body sections; everything from it on is the
tool-owned footer. A human's in-body `---` no longer truncates. New **R-SECT-02** regression: an artifact
with an in-body `---` preserves all sections through `split`, and `locked_sections` still flags exactly
the human-edited section. The duplicate-H2 caution stays a documented limit (genuinely ambiguous, not a
clear bug).

## 6. Testing & fixtures (real, scrubbed)

- **Replace** the wrong placeholder `tests/fixtures/org62/parent-entitlements.json` with **two real,
  scrubbed fixtures** captured from live Org62 (IDs redacted, values preserved):
  - `tests/fixtures/org62/product2-candidates.json` -- the Step-1 resolve envelope.
  - `tests/fixtures/org62/entitlement-composition.json` -- the Step-2
    `sfbase__EntitlementDefinitionMap__c` grant envelope (the real "EE Sites"/qty/cloud shape).
- **R-ENT-01 rewritten:** asserts `parse_composition` maps the real fixture (grant name, cloud,
  quantity, service-enabling, derived category) and degrades on empty/malformed without raising.
- **R-ENT-02 (new):** asserts `parse_candidates` maps the resolve fixture and degrades gracefully.
- CI tests the parsers against true fixtures; the live pull stays a capability-gated manual step.

## 7. `refs/org62-entitlements.md` rewrite (closes B1)

Rewrite to the real schema: the two-step query spine (resolve -> compose) with the actual SOQL against
`sfbase__EntitlementDefinitionMap__c`, the pinned-Id escape hatch, the real field list (§2), the
derived-category mapping table, the "composition is often sparse -> flag the gap, human confirms"
reality, and the preserved read-only / graceful-degradation / pricing-out-of-scope rules. This is what
truly closes B1 (the Phase-3b ref carried illustrative-and-flagged-unconfirmed SOQL; this ref carries
confirmed-live SOQL).

## 8. Validation additions & acceptance

**Suite grows from 28:** R-ENT-01 (rewritten), R-ENT-02 (new). R-SECT-02 (new). The #06 template
revision keeps R-TEST-02 / R-TPL-01 / R-TPL-02 / R-RENDER-01 green (new tokens are UPPER_SNAKE, banner/
footer/VOICE preserved, fill-set updated). R-ORG62-01 (ref content) updated to assert the real-schema
needles (`sfbase__EntitlementDefinitionMap__c`, two-step resolve/compose, pinned Id, derived category).
Target: **28 -> 30** checks (R-ENT-02 and R-SECT-02 are net-new; R-ENT-01 and R-ORG62-01 are rewritten in place, not added).

**Acceptance (manual, capability-gated):** re-run #06/#07 for the `summer-26 / agentforce-healthcare-oem`
effort against a live pull for a pinned OEM SKU (`Health Cloud - Service - Enterprise Edition - OEM`,
`OPT-SS-EE-HLS-OEM-ASP`). Assert: the grant table renders with the derived category column; the sparse
composition is **flagged for human confirmation, not asserted**; the naming-difference delta
("Health Cloud" -> "Agentforce for Healthcare") still flags; #06 confidence reflects the
confirmed-but-thin pull. Record in `docs/superpowers/acceptance/`.

## 9. Out of scope (explicit, this phase)

- Web research / Slack sync (Phase 6); canvas render (Phase 5); Deep Build (Phase 7).
- Pricing/discount determination (out of scope entirely -- placeholders only).
- Live Org62 *writes* (read-only always).
- Pulling entitlement composition for non-parent products, or aggregating across a product bundle
  (the pull is per pinned Product2; bundle-walking is a later enhancement if needed).

## 10. Anticipated task decomposition (~6 tasks)

1. `org62.py`: `parse_candidates` + `parse_composition` + `categorize` map; remove `parse_entitlements`;
   replace the placeholder fixture with the two real scrubbed fixtures; rewrite R-ENT-01, add R-ENT-02.
2. Rewrite `refs/org62-entitlements.md` to the real two-step schema; update R-ORG62-01 needles.
3. Revise `templates/06-license-entitlements.md` (grant table + derived category column; preserve
   banner/footer/VOICE; new UPPER_SNAKE tokens); keep R-TEST-02/R-TPL-01/R-TPL-02/R-RENDER-01 green.
4. `sections.py` footer-detection hardening + R-SECT-02.
5. SKILL.md entitlements line -> two-step/pinned-Id; BACKLOG close B1.
6. Acceptance: live re-pull of #06/#07 for the pinned Healthcare OEM SKU; record + verify golden signals.

(Exact task count/ordering finalized in the plan; ~6 tasks.)
