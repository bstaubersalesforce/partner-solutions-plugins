# Org62 entitlement intake (parent-SKU modeling)

Feeds artifact **#06 license & entitlement details** (and, via #06, **#07 add-on tiering**). The skill
reads Org62 **read-only** through the `sf` CLI against the `org62` alias (env `ORG62_ALIAS`, default
`org62`) using the logged-in session identity -- the same pattern as the `team-projects` skill. It
**never writes** to Org62.

## The real schema

Entitlement composition is **not** four clean buckets. In Org62 it is a set of grant rows on
**`sfbase__EntitlementDefinitionMap__c`**, one per grant, linked to the parent `Product2` via
`sfbase__Product__c`. Each row carries: `EntitlementDefinitionName__c` (the grant, e.g. "UE Sites"),
`sfbase__Quantity__c`, `sfbase__ServiceEnabling__c`, `EntitlementTreatment__c`, `UsageModel__c`,
`AddOnSKU__r.Name` (when the grant maps to an add-on SKU), and the definition's
`sfbase__EntitlementDefinition__r.RecordType.Name` -- the *cloud* (Sites, force.com, ExactTarget,
Mulesoft, CommerceCloud, Slack, DMP / Data Studio, Tableau) -- plus `UsageType__r.Name`.

**Composition is often sparse** (an OEM SKU may carry only one or two grant rows). That is normal;
flag the thinness as a gap for human confirmation rather than inventing entitlements.

## The two-step pull (resolve -> compose)

**Step 1 -- resolve.** Product2 names are ambiguous (plain "Health Cloud - Enterprise Edition" carries
no entitlement-map rows; the entitlement-bearing SKU is the specific "...Service... - OEM" variant). So
query candidates and let a **human pin the right Id** -- never auto-pick:

```bash
sf data query --target-org "$ORG62_ALIAS" --json --query "
  SELECT Id, Name, ProductCode, Family
  FROM Product2 WHERE Name LIKE 'Health Cloud%' AND IsActive = true ORDER BY Name"
```

`scripts/org62.py` `parse_candidates()` parses this into `{id, name, product_code, family}` rows.

**Pinned-Id escape hatch:** when the right `Product2` Id is already known, skip Step 1 and pass it
straight to Step 2.

**Step 2 -- compose.** Pull the grant rows for the pinned product:

```bash
sf data query --target-org "$ORG62_ALIAS" --json --query "
  SELECT EntitlementDefinitionName__c, sfbase__Quantity__c, sfbase__ServiceEnabling__c,
         EntitlementTreatment__c, UsageModel__c, AddOnSKU__r.Name,
         sfbase__EntitlementDefinition__r.RecordType.Name,
         sfbase__EntitlementDefinition__r.UsageType__r.Name
  FROM sfbase__EntitlementDefinitionMap__c WHERE sfbase__Product__c = '<pinned pId>'"
```

`scripts/org62.py` `parse_composition()` parses this into grant dicts and adds a **derived `category`**
(`License`/`PSL`/`Feature`/`Storage`/`Add-on`/`Other`) via `categorize()`. The category is **our
interpretation** of the cloud + grant name, surfaced as a column in #06 -- it is *not* Org62's native
classification (Org62 classifies by cloud/RecordType). Keep it labelled as derived.

## Graceful degradation

No org reachable (no auth, headless CI, offline) -> **#06 is not blocked**: it falls back to paste +
model knowledge at lower confidence and the missing pull is surfaced as a flagged gap (owner + next
step). A live pull is a **capability-gated manual step**, never a hard dependency.

## Parent-SKU modeling (draft + flag; human confirms)

1. Resolve + pin the parent `Product2` (Step 1, or a known Id).
2. Compose its grant rows (Step 2); render the #06 grant table with the derived category column.
3. Propose the Embedded/OEM equivalent, **flagging naming differences** ("Health Cloud" ->
   "Agentforce for Healthcare") and **deltas** (OEM vs. direct); note real OEM/VAR SKUs exist
   (e.g. `OPT-SS-EE-HLS-OEM-ASP`).
4. Derive the minimalist Required/Recommended/Optional add-on tiers for #07.

The skill **drafts and flags** every entitlement; it never silently asserts one. A human pins the
product and confirms the composition before #06 reaches `verified`. **Pricing is out of scope** -- #07
surfaces which SKUs/add-ons exist and tiers them; price/discount cells stay as marked placeholders.
