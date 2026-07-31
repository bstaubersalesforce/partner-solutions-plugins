# [Partner Name] — Consumption Opportunities
**Date:** [YYYY-MM-DD] · **Org62 Opportunity Stage:** [stage] · **Built on Salesforce**
**Scope:** Consumption-growth opportunities only (Agentforce, Data Cloud, other Salesforce SKUs). For Flex Credit cost sizing see the **sf-flex-estimator** skill; for core-solution architecture see the **Technical & Architectural Assessment** (Stage 16); for license pull-through see the POV's **ISV Commercial Model**.

---

## Sizing-Band Anchor
**Target customer band:** [S | M | L | XL] — [why, e.g. "typical targets fall into the M band; estimates below assume M"]
**Scaling driver (#Entities):** [unit — e.g. branches / hubs / sites / seats] = [count or stated assumption]
> Estimates below are **directional and credits-only** — they seed the official calculator, they are not authoritative pricing (size with **sf-flex-estimator**). Bands are relative: to estimate another band, scale **#Entities** (and optionally U/F); the formulas are unchanged.

---

## Consumption Opportunity Map

| # | Opportunity | Type | Value driver | Priority | Consumption signal | Est. credits/yr (directional) |
|---|-------------|------|--------------|----------|--------------------|-------------------------------|
| 1 | [name] | Agent | [value] | [H/M/L] | [qualitative signal — e.g. "high-volume inference"] | [low–high credits, or — for SKU rows] |
| 2 | [name] | Data | [value] | [H/M/L] | [qualitative signal — e.g. "large external ingest"] | [low–high credits] |
| 3 | [name] | SKU | [value] | [H/M/L] | [qualitative signal] | — |

> "Consumption signal" is a qualitative note, never a dollar figure. Size with the sf-flex-estimator skill.

---

## Agentforce Agents

### Agent Opportunity 1: [name] `[confirmed | proposed — confirm | TBD]`
**Purpose / trigger:** [what this agent does and what invokes it]
**Topics & actions:** [named agent topics and actions]
**Objects read/written:** [Salesforce objects]
**Supporting components:** [Flow / Apex / prompt templates]
**Build steps:**
1. [step]
2. [step]
3. [step]
**Directional Estimate (credits only — [band] band):**
- Assumptions: U=[users/entity] × F=[runs/user/mo] × A=[actions/run] × #Entities=[count]; prompts=[n] @ [Basic 2 | Standard 4 | Advanced 16]
- Volume: [U×F×A×#Entities] actions/mo → [×12] actions/yr
- Credits/yr: [annual actions ×20] action + [annual prompts × tier] prompt = **[low–high] credits/yr** (directional; ×0.8 if sandbox)

### Agent Opportunity 2: [name] `[label]`
**Purpose / trigger:** [...]
**Topics & actions:** [...]
**Objects read/written:** [...]
**Supporting components:** [...]
**Build steps:**
1. [step]
2. [step]
3. [step]
**Directional Estimate (credits only — [band] band):**
- Assumptions: U=[users/entity] × F=[runs/user/mo] × A=[actions/run] × #Entities=[count]; prompts=[n] @ [Basic 2 | Standard 4 | Advanced 16]
- Volume: [U×F×A×#Entities] actions/mo → [×12] actions/yr
- Credits/yr: [annual actions ×20] action + [annual prompts × tier] prompt = **[low–high] credits/yr** (directional; ×0.8 if sandbox)

---

## Data Cloud

### Data Opportunity 1: [name] `[label]`
**Purpose / value:** [why this data asset grows value]
**DMOs / data streams / sources:** [data model objects, streams, source objects]
**Mapping & identity resolution:** [mapping notes, unification keys]
**Activation target:** [where the unified data is activated]
**Build steps:**
1. [step]
2. [step]
3. [step]
**Directional Estimate (credits only — [band] band):**
- Assumptions: data volume=[M rows] × run frequency=[runs/yr] × usage-type=[type @ multiplier from rate card]
- Credits/yr: [volume × frequency × multiplier] = **[low–high] credits/yr** (directional; ×0.8 if sandbox)

### Data Opportunity 2: [name] `[label]`
**Purpose / value:** [...]
**DMOs / data streams / sources:** [...]
**Mapping & identity resolution:** [...]
**Activation target:** [...]
**Build steps:**
1. [step]
2. [step]
3. [step]
**Directional Estimate (credits only — [band] band):**
- Assumptions: data volume=[M rows] × run frequency=[runs/yr] × usage-type=[type @ multiplier from rate card]
- Credits/yr: [volume × frequency × multiplier] = **[low–high] credits/yr** (directional; ×0.8 if sandbox)

---

## Other Salesforce SKU Opportunities

| SKU / Capability | Trigger in this solution | Value | Resellable by partner? |
|------------------|--------------------------|-------|------------------------|
| Shield (Platform Encryption / Event Monitoring) | [trigger] | [value] | [Y/N/TBD] |
| Backup & Archive | [trigger] | [value] | [Y/N/TBD] |
| Sandboxes (Partial/Full) | [trigger] | [value] | [Y/N/TBD] |
| [other resellable product] | [trigger] | [value] | [Y/N/TBD] |

---

## Notes
- **Sizing:** Use the **sf-flex-estimator** skill to model Flex Credit consumption cost for the Agentforce and Data Cloud opportunities above.
- **Deeper architecture:** The **Technical & Architectural Assessment** (Stage 16) covers core-solution build-readiness; this artifact covers only consumption-growth opportunities.
