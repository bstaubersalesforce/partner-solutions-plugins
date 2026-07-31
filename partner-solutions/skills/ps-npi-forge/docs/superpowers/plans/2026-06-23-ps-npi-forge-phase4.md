# PS-NPI-FORGE Phase 4 — Live Org62 entitlement composition (#06/#07) + sections.py hardening

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Phase-3b placeholder entitlement schema with the real Org62 model — parse `sfbase__EntitlementDefinitionMap__c` grant rows (two-step resolve→compose with a pinned-Id escape hatch) into a faithful #06 entitlement-grant table with a derived category column — and harden `sections.py` footer detection so a human's in-body `---` can't silently drop edits. Closes BACKLOG **B1**.

**Architecture:** Mechanical→Python (`org62.py` parsers, `sections.py` split, tested against real scrubbed fixtures), judgment→refs (`org62-entitlements.md` query spine). The #06 template is revised to the real grant shape while preserving the shared gap-banner/footer/VOICE conventions the suite enforces. The live pull stays capability-gated/manual; CI tests parsers against committed fixtures.

**Tech Stack:** Python 3 stdlib only; the existing `tests/validate_skill.py` harness (`@check`, `_load_script`, `read`, `exists`, fixtures under `tests/fixtures/`); markdown templates.

## Global Constraints

- **Skill location:** `~/.claude/skills/ps-npi-forge/` (own git repo; remote `origin` → private `github.com/bstaubersalesforce/ps-npi-forge`).
- **Python:** stdlib only. Suite runs `python3 tests/validate_skill.py`; must stay green and grow. Scripts are side-effect-free libraries — **`org62.py` NEVER invokes `sf`/network**; it parses already-captured `--json` output. Parsers NEVER raise (degrade on empty/malformed, carrying the Phase-3b `isinstance`/non-dict guards).
- **Real Org62 schema (confirmed live, the single source of truth for this phase):**
  - Composition = `sfbase__EntitlementDefinitionMap__c` rows, one per grant, fields: `EntitlementDefinitionName__c`, `sfbase__Quantity__c`, `sfbase__ServiceEnabling__c`, `EntitlementTreatment__c`, `UsageModel__c`, `AddOnSKU__r.Name`, and `sfbase__EntitlementDefinition__r.RecordType.Name` (the *cloud*: Sites/force.com/Mulesoft/Slack/…) + `sfbase__EntitlementDefinition__r.UsageType__r.Name`.
  - Real OEM SKUs: `Health Cloud - Service - Enterprise Edition - OEM` (`OPT-SS-EE-HLS-OEM-ASP`), `Health Cloud - Service - Unlimited Edition - OEM` (`OPT-SS-UE-HLS-OEM-ASP`), Family `Custom Cloud`.
  - Composition is **sparse** (~1 grant row per SKU). Names are **ambiguous** (a human must pin the right Product2 Id).
- **Derived category** ∈ {`License`, `PSL`, `Feature`, `Storage`, `Add-on`, `Other`} — our interpretation of cloud/name, surfaced as a column, never claimed as Org62's native shape.
- **#06 template change** preserves verbatim: the `<!-- VOICE: reference … -->` comment, the gap-banner header block (`> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}` / `>` / `> {{GAP_BANNER}}`), and the footer block (`---` / `**Sources:** {{SOURCES}}` / `**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}`). New body tokens are UPPER_SNAKE.
- **Refusal rules unchanged:** official docs only; never assert entitlements without human confirmation (pin-before-assert); pricing out of scope (placeholders); Org62 read-only; never publish to Slack w/o confirm; never silently drop an uncertainty.
- **Effort data** lives outside the repo at `/Users/bstauber/claude-projects/ps-npi-efforts/…`; nothing there is committed.

## File Structure

- `scripts/org62.py` — **rewrite**: drop `parse_entitlements`; add `parse_candidates`, `parse_composition`, `categorize`.
- `tests/fixtures/org62/parent-entitlements.json` — **delete** (wrong placeholder schema).
- `tests/fixtures/org62/product2-candidates.json` — **create** (real Step-1 envelope, IDs scrubbed).
- `tests/fixtures/org62/entitlement-composition.json` — **create** (real Step-2 envelope, IDs scrubbed).
- `scripts/sections.py` — **modify**: footer = the `---` immediately preceding `**Sources:**`.
- `templates/06-license-entitlements.md` — **rewrite body**: grant table + derived category; keep banner/footer/VOICE.
- `refs/org62-entitlements.md` — **rewrite**: real two-step schema (closes B1).
- `tests/validate_skill.py` — **modify**: rewrite R-ENT-01 + R-ORG62-01; add R-ENT-02 + R-SECT-02.
- `SKILL.md` — **modify**: entitlements line → two-step/pinned-Id.
- `BACKLOG.md` — **modify**: close B1; mark Phase 4 done.
- `docs/superpowers/acceptance/2026-06-23-phase4-org62-composition.md` — **create**.

---

### Task 1: Real fixtures + org62.py parsers (parse_candidates, parse_composition, categorize)

**Files:**
- Delete: `tests/fixtures/org62/parent-entitlements.json`
- Create: `tests/fixtures/org62/product2-candidates.json`, `tests/fixtures/org62/entitlement-composition.json`
- Rewrite: `scripts/org62.py`
- Modify: `tests/validate_skill.py` (rewrite R-ENT-01; add R-ENT-02)

**Interfaces:**
- Consumes: nothing (pure parsers).
- Produces: `parse_candidates(sf_json) -> list[{id,name,product_code,family}]`; `parse_composition(sf_json) -> list[{grant,cloud,usage_type,quantity,service_enabling,treatment,usage_model,addon_sku,category}]`; `categorize(grant_name, cloud) -> str`. All degrade to `[]`/`"Other"` on empty/malformed; never raise.

- [ ] **Step 1: Create the two real scrubbed fixtures** (IDs redacted to `0`-padded placeholders; values preserved).

`tests/fixtures/org62/product2-candidates.json`:

```json
{
  "status": 0,
  "result": {
    "records": [
      {
        "attributes": {"type": "Product2"},
        "Id": "01tXX00000000E1OEM",
        "Name": "Health Cloud - Service - Enterprise Edition - OEM",
        "ProductCode": "OPT-SS-EE-HLS-OEM-ASP",
        "Family": "Custom Cloud"
      },
      {
        "attributes": {"type": "Product2"},
        "Id": "01tXX00000000U1OEM",
        "Name": "Health Cloud - Service - Unlimited Edition - OEM",
        "ProductCode": "OPT-SS-UE-HLS-OEM-ASP",
        "Family": "Custom Cloud"
      }
    ],
    "totalSize": 2,
    "done": true
  },
  "warnings": []
}
```

`tests/fixtures/org62/entitlement-composition.json`:

```json
{
  "status": 0,
  "result": {
    "records": [
      {
        "attributes": {"type": "sfbase__EntitlementDefinitionMap__c"},
        "sfbase__Product__r": {"attributes": {"type": "Product2"}, "Name": "Health Cloud - Service - Unlimited Edition - OEM"},
        "EntitlementDefinitionName__c": "UE Sites",
        "sfbase__EntitlementDefinition__r": {
          "attributes": {"type": "sfbase__EntitlementDefinition__c"},
          "RecordType": {"attributes": {"type": "RecordType"}, "Name": "Sites"},
          "UsageType__r": null
        },
        "sfbase__Quantity__c": 1000000,
        "sfbase__ServiceEnabling__c": true,
        "EntitlementTreatment__c": "None",
        "UsageModel__c": "N/A",
        "AddOnSKU__r": null
      }
    ],
    "totalSize": 1,
    "done": true
  },
  "warnings": []
}
```

- [ ] **Step 2: Rewrite R-ENT-01 and add R-ENT-02** in `tests/validate_skill.py` — replace the existing `t_org62_parse` (R-ENT-01) function entirely with the two below (find the `@check("R-ENT-01: …")` block and replace through the end of its function):

```python
# ---- R-ENT-01: Org62 composition parser ---------------------------------
@check("R-ENT-01: parse_composition maps the real entitlement-map fixture to grant rows with a derived category, and degrades on empty/malformed")
def t_org62_composition():
    o = _load_script("scripts/org62.py", "org62_mod1")
    import json
    with open(os.path.join(SKILL, "tests/fixtures/org62/entitlement-composition.json"), encoding="utf-8") as f:
        grants = o.parse_composition(json.load(f))
    assert isinstance(grants, list) and len(grants) == 1, grants
    g = grants[0]
    assert g["grant"] == "UE Sites", g
    assert g["cloud"] == "Sites", g
    assert g["quantity"] == 1000000, g
    assert g["service_enabling"] is True, g
    assert g["addon_sku"] is None, g
    assert g["category"] in ("License", "PSL", "Feature", "Storage", "Add-on", "Other"), g
    # empty + malformed degrade to [] without raising
    for bad in [{"result": {"records": []}}, {"result": {"records": "oops"}},
                {"result": {"records": [None]}}, None, {}]:
        assert o.parse_composition(bad) == [], f"must degrade to [] on {bad}"

# ---- R-ENT-02: Org62 candidate-resolve parser ---------------------------
@check("R-ENT-02: parse_candidates maps the product2-candidates fixture and degrades on empty/malformed")
def t_org62_candidates():
    o = _load_script("scripts/org62.py", "org62_mod2")
    import json
    with open(os.path.join(SKILL, "tests/fixtures/org62/product2-candidates.json"), encoding="utf-8") as f:
        cands = o.parse_candidates(json.load(f))
    assert isinstance(cands, list) and len(cands) == 2, cands
    names = [c["name"] for c in cands]
    assert "Health Cloud - Service - Enterprise Edition - OEM" in names, cands
    assert cands[0]["product_code"] == "OPT-SS-EE-HLS-OEM-ASP", cands
    assert all(set(c.keys()) >= {"id", "name", "product_code", "family"} for c in cands), cands
    for bad in [{"result": {"records": []}}, {"result": {"records": "oops"}},
                {"result": {"records": [None]}}, None, {}]:
        assert o.parse_candidates(bad) == [], f"must degrade to [] on {bad}"
```

- [ ] **Step 3: Run the suite to verify it FAILS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on R-ENT-01 (`parse_composition` not found — old parser is `parse_entitlements`) and R-ENT-02 (`parse_candidates` not found).

- [ ] **Step 4: Rewrite `scripts/org62.py`** (replace the whole file):

```python
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
        out.append({
            "grant": grant,
            "cloud": cloud,
            "usage_type": usage_type,
            "quantity": r.get("sfbase__Quantity__c"),
            "service_enabling": r.get("sfbase__ServiceEnabling__c"),
            "treatment": r.get("EntitlementTreatment__c"),
            "usage_model": r.get("UsageModel__c"),
            "addon_sku": addon_sku,
            "category": categorize(grant, cloud),
        })
    return out
```

- [ ] **Step 5: Delete the stale placeholder fixture**

Run: `cd ~/.claude/skills/ps-npi-forge && git rm tests/fixtures/org62/parent-entitlements.json`

- [ ] **Step 6: Run the suite to verify PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `29/29 checks passed`, exit 0 (28 prior + R-ENT-02; R-ENT-01 rewritten in place). If a check references the deleted fixture, that surfaces here.

- [ ] **Step 7: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add scripts/org62.py tests/validate_skill.py tests/fixtures/org62/
git commit -m "feat(org62): real two-step composition parser (candidates + grants + derived category); real fixtures (closes B1 parser)"
```

---

### Task 2: Rewrite refs/org62-entitlements.md to the real two-step schema

**Files:**
- Rewrite: `refs/org62-entitlements.md`
- Modify: `tests/validate_skill.py` (rewrite R-ORG62-01 needles)

**Interfaces:**
- Consumes: `read`, `exists`.
- Produces: a ref documenting the real schema, gated by R-ORG62-01.

- [ ] **Step 1: Rewrite R-ORG62-01** in `tests/validate_skill.py` — replace the body of `t_org62_ref` with real-schema needles:

```python
@check("R-ORG62-01: org62-entitlements ref exists, is referenced by SKILL.md, and pins the real two-step read-only schema + human-confirm")
def t_org62_ref():
    path = "refs/org62-entitlements.md"
    assert exists(path), f"missing {path}"
    body = read(path).lower()
    for needle in ["sfbase__entitlementdefinitionmap__c", "product2", "sf data query", "--json",
                   "org62", "read-only", "resolve", "compose", "pinned", "category",
                   "naming difference", "delta", "human"]:
        assert needle in body, f"org62 ref missing: {needle}"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"
```

- [ ] **Step 2: Run the suite to verify it FAILS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on R-ORG62-01 (the current ref lacks `sfbase__entitlementdefinitionmap__c`, `resolve`, `compose`, `pinned`, `category`).

- [ ] **Step 3: Rewrite `refs/org62-entitlements.md`** (replace the whole file):

```markdown
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
```

- [ ] **Step 4: Run the suite to verify PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `29/29 checks passed`, exit 0 (R-ORG62-01 satisfied; R-ARCH-02/03/04 still green — ref path unchanged).

- [ ] **Step 5: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add refs/org62-entitlements.md tests/validate_skill.py
git commit -m "docs(org62): rewrite entitlements ref to the real two-step schema (closes B1)"
```

---

### Task 3: Revise the #06 template to the entitlement-grant table

**Files:**
- Rewrite (body): `templates/06-license-entitlements.md`

**Interfaces:**
- Consumes: shared conventions (banner/footer/VOICE).
- Produces: a #06 template whose body is a grant table + derived category, with new UPPER_SNAKE tokens added to the render fill-set.

- [ ] **Step 1: Rewrite `templates/06-license-entitlements.md`** (replace the whole file — banner/footer/VOICE preserved verbatim, body replaced):

```markdown
<!-- VOICE: reference — factual/precise; do not editorialize; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — License & Entitlement Details

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

**Parent product:** {{PARENT_SKU}} · **Embedded/OEM product:** {{PRODUCT_NAME}}
**Pinned Org62 Product2:** {{PINNED_PRODUCT}} ({{PINNED_PRODUCT_CODE}})

## Entitlement composition (from Org62 `sfbase__EntitlementDefinitionMap__c`)

The grant rows below are the parent SKU's entitlement composition as modeled in Org62. **Category is
derived** (our interpretation of cloud + grant name), not Org62's native classification. Composition is
often sparse; unconfirmed or missing grants are flagged for human confirmation.

{{ENTITLEMENT_GRANTS_TABLE}}

## Naming differences & deltas vs. parent
{{DELTAS_AND_NAMING}}

## Human-confirmation checklist
{{CONFIRMATION_CHECKLIST}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 2: Run the suite to verify PASS** (the template change must keep every template-gating check green)

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `29/29 checks passed`, exit 0. Specifically:
- R-TEST-02 (token hygiene): new tokens `{{PINNED_PRODUCT}}`, `{{PINNED_PRODUCT_CODE}}`, `{{ENTITLEMENT_GRANTS_TABLE}}` are UPPER_SNAKE.
- R-TPL-01/R-TPL-02: slug unchanged; literal banner status line, `> {{GAP_BANNER}}`, and footer block preserved verbatim.
- R-RENDER-01: a complete fill of every template token leaves no surviving `{{TOKEN}}` (the new tokens are part of the fill-set automatically — `render` keys off whatever tokens the template contains).

- [ ] **Step 3: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add templates/06-license-entitlements.md
git commit -m "feat(06): entitlement-grant table + derived category column; retire the four-bucket sections"
```

---

### Task 4: Harden sections.py footer detection (deferred Phase-3b fix)

**Files:**
- Modify: `scripts/sections.py`
- Modify: `tests/validate_skill.py` (add R-SECT-02)

**Interfaces:**
- Consumes: nothing.
- Produces: `split()` whose footer boundary is the `---` immediately preceding `**Sources:**` (not the first `---`), so an in-body `---` no longer truncates the split. `locked_sections` unchanged in signature.

- [ ] **Step 1: Write the failing test** — append before `# ---- runner`:

```python
# ---- R-SECT-02: in-body --- does not truncate the split -----------------
@check("R-SECT-02: a standalone --- inside a body section does not drop later sections; the footer is the ---/**Sources:** block")
def t_sections_inbody_rule():
    s = _load_script("scripts/sections.py", "sections_mod2")
    md = ("<!-- VOICE -->\n# Title\n> banner\n\n"
          "## Overview\nintro\n\n---\n\nmid-section rule above\n\n"
          "## Details\nbody two\n\n"
          "---\n**Sources:** x\n**Confidence:** 0.5 — ok\n")
    secs = s.split(md)
    assert set(secs.keys()) == {"Overview", "Details"}, f"in-body --- truncated the split: {set(secs.keys())}"
    assert "mid-section rule above" in secs["Overview"], "content after an in-body --- was dropped"
    assert "body two" in secs["Details"], "a later section was dropped by an in-body ---"
    # footer (Sources/Confidence) is excluded from sections
    assert not any("Sources" in body for body in secs.values()), "footer leaked into a section"
    # edit detection still works across the in-body rule
    live = md.replace("body two", "HUMAN-EDITED body two")
    assert s.locked_sections(live, md) == {"Details"}, "edit after an in-body --- not detected"
```

- [ ] **Step 2: Run to verify it FAILS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on R-SECT-02 — current `split` breaks at the first `---`, so it returns only `{"Overview"}` (Details dropped).

- [ ] **Step 3: Harden `scripts/sections.py`** — replace the `split` function (keep the module docstring and `locked_sections` as-is, but update the docstring's footer sentence):

```python
def _footer_start(lines):
    """Index of the '---' line that begins the artifact footer (the one immediately preceding a
    '**Sources:**' line), or len(lines) if there is no such footer. Only this '---' is the footer
    delimiter; standalone '---' rules inside a body section are NOT footers."""
    for i, line in enumerate(lines):
        if line.strip() == "---":
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].lstrip().startswith("**Sources:**"):
                return i
    return len(lines)

def split(md):
    lines = md.splitlines()
    end = _footer_start(lines)
    sections = {}
    cur = None
    buf = []
    for line in lines[:end]:
        m = H2_RE.match(line)
        if m:
            if cur is not None:
                sections[cur] = "\n".join(buf)
            cur = m.group(1).strip()
            buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        sections[cur] = "\n".join(buf)
    return sections
```

Also update the module docstring line that says "the footer from the standalone '---' rule onward" to: "the footer (the '---' immediately preceding '**Sources:**' onward)".

- [ ] **Step 4: Run to verify PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `30/30 checks passed`, exit 0 (R-SECT-01 still passes — its fixtures have the `---`/`**Sources:**` footer; R-SECT-02 now passes).

- [ ] **Step 5: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add scripts/sections.py tests/validate_skill.py
git commit -m "fix(sections): footer = ---/**Sources:** block, so in-body --- can't drop sections (Phase-3b deferred fix)"
```

---

### Task 5: SKILL.md entitlements line + BACKLOG B1 closure

**Files:**
- Modify: `SKILL.md`
- Modify: `BACKLOG.md`

**Interfaces:**
- Produces: SKILL.md describing the two-step/pinned-Id pull; BACKLOG with B1 closed + Phase 4 marked done.

- [ ] **Step 1: Update the SKILL.md entitlements line** — replace the current line:

```markdown
**Entitlements:** #06/#07 model the parent SKU's composition from Org62 (read-only) per
[refs/org62-entitlements.md](refs/org62-entitlements.md); the skill drafts and flags, a human confirms.
```

with:

```markdown
**Entitlements:** #06/#07 model the parent SKU's composition from Org62 (read-only) via a two-step
resolve→compose pull (a human pins the right `Product2`, or passes a known Id) over
`sfbase__EntitlementDefinitionMap__c`, per [refs/org62-entitlements.md](refs/org62-entitlements.md);
the skill drafts and flags, a human confirms.
```

- [ ] **Step 2: Close B1 and mark Phase 4 done in `BACKLOG.md`**

Change the B1 line (currently `[~]`) to:

```markdown
- [x] **B1 — Org62 entitlement query:** CLOSED in Phase 4. Real schema pinned: composition =
  `sfbase__EntitlementDefinitionMap__c` grant rows (cloud/RecordType + quantity + service-enabling +
  add-on SKU), pulled two-step (resolve candidates → compose for a human-pinned Product2 Id).
  `org62.py` `parse_candidates`/`parse_composition`/`categorize` + real scrubbed fixtures + rewritten
  `refs/org62-entitlements.md`. #06 renders a faithful grant table with a derived category column.
```

Under the roadmap, change `- [ ] Phase 4 — …` to:

```markdown
- [x] Phase 4 — Org62 entitlement intake (real two-step schema) + #06 grant table + sections.py hardening
```

- [ ] **Step 3: Run the suite (no regression)**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `30/30 checks passed`, exit 0 (R-ARCH-02 still green — SKILL.md ref paths unchanged).

- [ ] **Step 4: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add SKILL.md BACKLOG.md
git commit -m "docs: SKILL.md two-step entitlement pull; close B1; mark Phase 4 done"
```

---

### Task 6: Acceptance — live re-pull of #06/#07 for the pinned Healthcare OEM SKU

This task is **manual + controller-driven**, not a unit test. The mechanical sub-steps (both parsers, the template, sections.py) are CI-covered by Tasks 1–4. The deliverable is a committed acceptance record verified against real output.

**Files:**
- Create: `docs/superpowers/acceptance/2026-06-23-phase4-org62-composition.md`

- [ ] **Step 1: Resolve + pin the parent Product2** (live, read-only) — run Step-1 resolve and pick the OEM SKU:

```bash
ORG="${ORG62_ALIAS:-org62}"
sf data query --target-org "$ORG" --json --query "SELECT Id, Name, ProductCode, Family FROM Product2 WHERE Name LIKE 'Health Cloud - Service%OEM' AND IsActive=true ORDER BY Name"
```
Pin `Health Cloud - Service - Enterprise Edition - OEM` (`OPT-SS-EE-HLS-OEM-ASP`) — capture its Id.

- [ ] **Step 2: Compose** — run Step-2 for the pinned Id and save to the effort's `sources/`:

```bash
EFF=/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem
sf data query --target-org "$ORG" --json --query "SELECT EntitlementDefinitionName__c, sfbase__Quantity__c, sfbase__ServiceEnabling__c, EntitlementTreatment__c, UsageModel__c, AddOnSKU__r.Name, sfbase__EntitlementDefinition__r.RecordType.Name, sfbase__EntitlementDefinition__r.UsageType__r.Name FROM sfbase__EntitlementDefinitionMap__c WHERE sfbase__Product__c = '<pinned Id>'" > "$EFF/sources/org62-entitlement-composition-ee-oem.json"
```

- [ ] **Step 3: Regenerate #06 (and re-tier #07)** through the cycle: `org62.parse_composition` the saved JSON → build the grant table fills (Grant · Category · Cloud · Qty · Service-enabling · Add-on) → render `templates/06-license-entitlements.md` → run `scan.py` → write the artifact + baseline + manifest verdicts. Because composition is sparse, flag the thin/unconfirmed grants in the gap banner and `CONFIRMATION_CHECKLIST`; keep the "Health Cloud → Agentforce for Healthcare" naming delta. #07 add-on tiering re-references the grant rows + the candidate SKUs.

- [ ] **Step 4: Assert the golden signals** (verify in the rendered #06 bytes, not by assumption):
  - #06 renders the entitlement-grant table with the **derived category column** and the pinned product code.
  - The sparse composition is **flagged for human confirmation**, not asserted as complete (gap banner + checklist).
  - The naming-difference delta still flags.
  - #06 confidence reflects a confirmed-but-thin pull (higher than the Phase-3b flagged-gap baseline, still < 1.0).
  - No price/discount asserted (pricing out of scope).

- [ ] **Step 5: Write the acceptance record** `docs/superpowers/acceptance/2026-06-23-phase4-org62-composition.md`: the pinned SKU + Id, the real grant rows pulled, the rendered #06 table (or an excerpt), the derived-category mapping applied, and any rough edges (feed BACKLOG).

- [ ] **Step 6: Run the suite and commit**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `30/30 checks passed`, exit 0.

```bash
cd ~/.claude/skills/ps-npi-forge
git add docs/superpowers/acceptance/2026-06-23-phase4-org62-composition.md
git commit -m "docs: Phase 4 acceptance — live Org62 composition pull for pinned Healthcare OEM SKU"
```

---

## Self-Review

**Spec coverage (Phase 4 scope):**
- Real schema discovered + documented (spec §2) → Task 2 ref rewrite + R-ORG62-01. ✅
- Two-step resolve→compose with pinned-Id escape hatch (spec §3) → Task 1 parsers (`parse_candidates`/`parse_composition`) + Task 2 ref. ✅
- Faithful grant table + derived category column (spec §4) → Task 1 `categorize` + Task 3 #06 template. ✅
- `parse_entitlements` removed, R-ENT-01 rewritten (spec §4.1) → Task 1. ✅
- Real scrubbed fixtures replace the placeholder (spec §6) → Task 1 Steps 1+5. ✅
- sections.py footer hardening (spec §5) → Task 4 + R-SECT-02. ✅
- Ref rewrite closes B1 (spec §7) → Task 2; B1 marked closed Task 5. ✅
- Validation 28→30: R-ENT-02 (+1, Task 1) and R-SECT-02 (+1, Task 4) are the two net-new checks; R-ENT-01 + R-ORG62-01 are rewritten in place (spec §8). All per-task "expected" lines read 30. ✅
- Acceptance, live pull, golden signals (spec §8) → Task 6. ✅
- **Deferred (correctly out of Phase 4):** web/Slack (Phase 6), canvas render (Phase 5), Deep Build (Phase 7), pricing, bundle-walking.

**Placeholder scan:** All code, fixtures, ref, and template written in full. Real JSON values are from live Org62 (IDs scrubbed to `01tXX…`/omitted). `<pinned Id>` / `<pinned pId>` / `<parent>` in shell/SOQL examples are intentional runtime values, not plan gaps. Task 6 is explicitly manual/controller-driven (no fabricated unit-test code for the non-deterministic live step). ✅

**Type consistency:** `parse_candidates(sf_json)->list[{id,name,product_code,family}]`, `parse_composition(sf_json)->list[{grant,cloud,usage_type,quantity,service_enabling,treatment,usage_model,addon_sku,category}]`, `categorize(grant_name,cloud)->str`, `_records(sf_json)->list`, `split(md)->dict`, `_footer_start(lines)->int`, `locked_sections(live,base)->set` — names/signatures consistent across defining and consuming tasks. New #06 tokens (`{{PINNED_PRODUCT}}`, `{{PINNED_PRODUCT_CODE}}`, `{{ENTITLEMENT_GRANTS_TABLE}}`) are UPPER_SNAKE and appear only in the template (render keys off the template's own tokens). ✅

**Check-count:** the canonical end state is **30** (R-ENT-02 + R-SECT-02 net-new; R-ENT-01/R-ORG62-01 rewritten in place). Every per-task "expected" line (Tasks 1–6) reads 30 consistently.
```
