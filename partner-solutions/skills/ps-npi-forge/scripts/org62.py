#!/usr/bin/env python3
"""
Org62 entitlement parsers for ps-npi-forge. Stdlib-only, side-effect-free.

Parses the JSON produced by `sf data query ... --json` against live Org62 into the #06 payload.
This module NEVER invokes `sf` or the network -- the live pull is a capability-gated manual step
documented in refs/org62-entitlements.md; these parsers consume its already-captured output so they
stay testable. The skill drafts and flags entitlements; a human always confirms (refusal rule).

Two-step model (the real Org62 schema):
  1. resolve  -> parse_candidates(): Product2 candidates for the parent SKU (a human pins the right Id)
  2. compose  -> parse_composition(): sfbase__EntitlementDefinitionMap__c grant rows for the pinned product

categorize() derives a familiar category (License/PSL/Feature/Storage/Add-on/Other) from the grant's
cloud (RecordType) + name. The category is OUR interpretation surfaced as a column -- not Org62's
native classification, which is by cloud/RecordType.
"""

def _records(sf_json):
    """Return the result.records list, or [] for any empty/malformed envelope (never raises)."""
    if not isinstance(sf_json, dict):
        return []
    res = sf_json.get("result", sf_json)
    if not isinstance(res, dict):
        return []
    recs = res.get("records")
    return recs if isinstance(recs, list) else []

def parse_candidates(sf_json):
    out = []
    for r in _records(sf_json):
        if not isinstance(r, dict):
            continue
        out.append({
            "id": r.get("Id"),
            "name": r.get("Name"),
            "product_code": r.get("ProductCode"),
            "family": r.get("Family"),
        })
    return out

# cloud (RecordType.Name) / grant-name signals -> derived category. Documented, deliberately small.
_CATEGORY_BY_CLOUD = {
    "Sites": "Feature",
    "force.com": "License",
    "ExactTarget": "Feature",
    "Mulesoft": "Feature",
    "CommerceCloud": "Feature",
    "Slack": "Feature",
    "DMP / Data Studio": "Feature",
    "Tableau": "Feature",
}

def categorize(grant_name, cloud):
    """
    Derive a familiar category (License/PSL/Feature/Storage/Add-on/Other) from grant name + cloud.

    This is OUR interpretation surfaced as a column, not Org62's native classification.
    Note: "Add-on" is applied in parse_composition when addon_sku is present; categorize itself
    never returns "Add-on" as it only sees name+cloud (addon linkage is in a different field).
    """
    name = (grant_name or "").lower()
    if "storage" in name:
        return "Storage"
    if "permission set" in name or name.endswith(" psl") or " psl " in f" {name} ":
        return "PSL"
    if "license" in name:
        return "License"
    return _CATEGORY_BY_CLOUD.get(cloud, "Other")

def parse_composition(sf_json):
    out = []
    for r in _records(sf_json):
        if not isinstance(r, dict):
            continue
        ed = r.get("sfbase__EntitlementDefinition__r") or {}
        ed = ed if isinstance(ed, dict) else {}
        rt = ed.get("RecordType") or {}
        cloud = rt.get("Name") if isinstance(rt, dict) else None
        ut = ed.get("UsageType__r") or {}
        usage_type = ut.get("Name") if isinstance(ut, dict) else None
        addon = r.get("AddOnSKU__r") or {}
        addon_sku = addon.get("Name") if isinstance(addon, dict) else None
        grant = r.get("EntitlementDefinitionName__c")
        # Derive base category; override to "Add-on" when there IS an add-on linkage
        category = "Add-on" if addon_sku else categorize(grant, cloud)
        out.append({
            "grant": grant,
            "cloud": cloud,
            "usage_type": usage_type,
            "quantity": r.get("sfbase__Quantity__c"),
            "service_enabling": r.get("sfbase__ServiceEnabling__c"),
            "treatment": r.get("EntitlementTreatment__c"),
            "usage_model": r.get("UsageModel__c"),
            "addon_sku": addon_sku,
            "category": category,
        })
    return out
