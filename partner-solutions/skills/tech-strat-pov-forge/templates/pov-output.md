# POV Output Template

Required output structure. All sections marked [REQUIRED] must be present and non-empty before delivery.
Sections marked [REQUIRED if known] must be present or explicitly flagged as TBD with a named owner.

---

# [Partner Name] — Point of View
**Org62 Opportunity Stage:** [00-Prospect / 01-Qualify / 02-Assess / 03-Contract / 04-Build / 05-In Market / 06-First Report]
**Date:** [YYYY-MM-DD]
**Prepared by:** [name, role]

---

## Problem Space [REQUIRED]

**Problem Statement:**
> [Specific persona] struggles with [specific pain] in [context], leading to [measurable consequence].

**Significance:**
[Why this matters at scale — market size, customer/patient impact, cost of inaction]

**Challenges:**
- [Barrier 1 — organizational, technical, or regulatory]
- [Barrier 2]
- [Barrier 3]

**Risks:**
- [Risk 1 — what could prevent success]
- [Risk 2]

---

## Vision [REQUIRED]

**Vision Statement:**
> [Solution name] enables [specific persona] to [specific capability] so that [measurable outcome].

---

## Product Strategy [REQUIRED if known]

**Strategic Thesis:** [Where the product is heading and why now — 2-3 sentences. The governing direction, not a feature list.]

**Product Pillars:** [3-4 capability themes the product is built around, each with the strategic bet behind it and a rough now/next/later.]

**Market Positioning:** [Competitive positioning, target-segment strategy, and pricing/packaging direction.]

**Horizon Sequencing to Moat:** [How the pillars sequence across horizons toward a defensible position — cross-references, does not duplicate, MVP & Roadmap.]

**Platform Bet:** [Why build deeper on Salesforce — the strategic rationale for the platform dependency.]

---

## Solution Description [REQUIRED]

**Solution Statement:**
[Plain-language description of what the solution does. No jargon.]

**Benefits:**
1. [Measurable benefit 1]
2. [Measurable benefit 2]
3. [Measurable benefit 3]

**KPIs:**
- [Metric 1 customers use to evaluate success]
- [Metric 2]
- [Metric 3]

**Product-Market Fit:**
- **Viable:** [Commercial model, revenue potential, ACV opportunity]
- **Feasible:** [Technical buildability on Salesforce — native, composite, dependencies]
- **Desirable:** [Customer demand evidence — named customers, requests, market signals]
- **Ethical:** [Data privacy, patient safety, compliance considerations — or "No ethical flags identified"]

---

## Use Case Summary [REQUIRED — minimum 1, target 3]

### Use Case 1: [Title]
When [persona] needs to [job-to-be-done], [solution] provides [specific capability], resulting in [measurable outcome].

### Use Case 2: [Title]
When [persona] needs to [job-to-be-done], [solution] provides [specific capability], resulting in [measurable outcome].

### Use Case 3: [Title]
When [persona] needs to [job-to-be-done], [solution] provides [specific capability], resulting in [measurable outcome].

---

## Target Markets [REQUIRED]

**Primary Market:** [market description]
**Pilot/Target Customers:** [named customer(s) or "TBD — owner: [name]"]

**Secondary Market:** [market description — or "Not yet identified"]
**Pilot/Target Customers:** [named customer(s) or "TBD"]

**Potential Adjacent Market(s):** [description — or "Not yet assessed"]

---

## Personas & Value Delivered [REQUIRED]

**Persona 1 — Admin/Configuration User:**
[Role description] — [What they gain from this solution]

**Persona 2 — Internal Operational User:**
[Role description] — [What they gain from this solution]

**Persona 3 — External User (Customer/Patient/Partner):**
[Role description — or "Not applicable"] — [What they gain, or N/A]

---

## Solution Alignment [REQUIRED if known]

**Sales Play Alignment:** [Named Sales Play — or "TBD — owner: [name]"]

**Blueprint Gap(s) Addressed:**
- [Specific Blueprint capability this solution fills]
- [Additional gap if applicable]

**Identified Needs from Stakeholders:**
- Product: [stated need — or "Not yet validated"]
- Advisory: [stated need — or "Not yet validated"]
- Sales: [stated need — or "Not yet validated"]

---

## MVP & Development Priorities [REQUIRED if known]

**MVP:** [Minimum viable scope]
**Horizon 1:** [Near-term roadmap — or "TBD"]
**Horizon 2:** [Longer-term roadmap — or "TBD"]
**Architectural Runway / Technical Debt:** [What needs to be retired — or "None identified"]

---

## ISV Commercial Model [REQUIRED]

**App Type:** [ISVforce / OEM / Mixed/OSP / Reseller / Consumption]
**Licensing Model:** [PUPM / POPM / Tiered / Other — describe]
**Pull-through Potential:** [Which Salesforce SKUs this drives — or "Not yet quantified"]

---

## Partner App Strategy & Technical Summary [REQUIRED]

**Application Type:** [Native managed package / Composite / Hybrid — describe]
**Integrations:** [Key APIs, endpoints, integration frameworks]
**User Interface:** [Native LWC / Canvas / Custom portal / Other]
**Data Model:** [Standard objects, custom objects, sync strategy]
**Salesforce Cloud/SKU Dependencies:** [List — e.g., Service Cloud, Health Cloud, Data Cloud]
**External Dependencies:** [Integrated systems, competing initiatives, API readiness requirements]

---

## Confidence & Assumptions

**Confidence:** [0.0–1.0]

**This score rests on the following assumptions:**
1. [Named assumption 1]
2. [Named assumption 2]
3. [Named assumption 3]

**Incomplete Sections (TBD):**
- [List any sections flagged TBD, with owner and target date if known]
- [Or: "All required sections complete"]

---

## Research Provenance [REQUIRED if any source was blocked or any fact is partner-confirmed]

> Standardized record of where the POV's facts came from — so confidence is auditable and a blocked source is visible, not buried. Omit this section only when every fact came from a clean primary-source fetch and nothing was partner-confirmed.

**Source coverage:** [One line — which research threads succeeded vs. failed, e.g. "5 of 6 research threads succeeded; partner site (primary) returned 403."]

**Blocked sources & fallback used:** [For any blocked source, name it and the fallback that supplied the facts — e.g. "citnow.com 403 → facts sourced from DuckDuckGo results, am-online trade press, G2." Or "None."]

**Partner-confirmed facts:** [List facts supplied by the user in Stage 3 rather than research — e.g. "Pilot (Al Naghi), exec sponsor (Brian Landsman), PADA signed." These are high-trust but unverifiable from public sources.]

**Net effect on confidence:** [One line — e.g. "Primary-source block did not reduce confidence; decisive facts corroborated across multiple sources + partner confirmation." Or state the reduction and why.]
