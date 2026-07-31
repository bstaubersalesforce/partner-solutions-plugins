# MVP Build Plan Output Template

Required output structure for the MVP Build Plan.
Sections marked [REQUIRED] must be present and non-empty.
Sections marked [REQUIRED if known] must be present or explicitly flagged TBD with a named owner.
Source mapping notes (in brackets) show which POV section to draw from — remove them from final output.

---

# [Partner Name] — MVP Build Plan
**POV Reference:** [POV document date or link]
**Build Plan Date:** [YYYY-MM-DD]
**Prepared by:** [name, role]
**Target Audience:** [Partner engineering/product team | Salesforce stakeholders | Both]
**Org62 Opportunity Stage:** [00-Prospect / 01-Qualify / 02-Assess / 03-Contract / 04-Build / 05-In Market / 06-First Report — from POV]

---

## Executive Summary [REQUIRED]
[2–3 sentences. Source: POV Vision Statement + Solution Statement.]

**Problem:** [One sentence. Source: POV Problem Statement.]
**Solution:** [One sentence. Source: POV Solution Statement.]
**MVP Goal:** [One sentence. Source: POV MVP scope.]

---

## MVP Scope [REQUIRED]

### In Scope
[Source: POV MVP section. List features/capabilities included in the first release.]
- [Feature 1]
- [Feature 2]
- [Feature 3]

### Out of Scope (Post-MVP)
[Source: POV Horizon 1 + Horizon 2 + Horizon 3. What is explicitly deferred.]

**Horizon 1:**
- [Deferred capability 1]
- [Deferred capability 2]

**Horizon 2:**
- [Longer-term deferred capability — from POV H2]
- [Deferred capability 2]

**Horizon 3:**
- [Strategic expansion — ecosystem play, AI/ML maturation, or platform extension — from POV H3]
- [Deferred capability — or "Not yet defined — from POV"]

---

## Feature Breakdown & User Stories [REQUIRED]

[One feature block per use case from the POV. Minimum 1, target 3. Include one block per POV use case — remove unused Feature blocks entirely rather than leaving them empty.]

### Feature 1: [Title — from POV Use Case 1]
**Source Use Case:** [POV Use Case 1 title]
**Persona:** [Admin / Internal User / External User]

**User Story:**
> As a [persona], I want to [capability], so that [measurable outcome].

**Acceptance Criteria:**
- [ ] Given [context], when [user action], then [system response / outcome]
- [ ] [KPI-based criterion — source: POV KPIs]
- [ ] [Edge case or error condition if applicable]

---

### Feature 2: [Title — from POV Use Case 2]
**Source Use Case:** [POV Use Case 2 title]
**Persona:** [persona]

**User Story:**
> As a [persona], I want to [capability], so that [measurable outcome].

**Acceptance Criteria:**
- [ ] Given [context], when [user action], then [outcome]
- [ ] [KPI-based criterion]

---

### Feature 3: [Title — from POV Use Case 3]
**Source Use Case:** [POV Use Case 3 title]
**Persona:** [persona]

**User Story:**
> As a [persona], I want to [capability], so that [measurable outcome].

**Acceptance Criteria:**
- [ ] Given [context], when [user action], then [outcome]
- [ ] [KPI-based criterion]

---

## Technical Requirements [REQUIRED]

### Salesforce Platform Requirements
[Source: POV Partner App Strategy & Technical Summary + SF Cloud/SKU Dependencies]

| Requirement | Details | MVP / Post-MVP |
|-------------|---------|----------------|
| Application Type | [Native managed package / Composite / Hybrid] | MVP |
| Salesforce Edition | [Minimum edition required] | MVP |
| [SF Cloud 1] | [How it's used] | [MVP / H1] |
| [SF Cloud 2] | [How it's used] | [MVP / H1] |
| [Add-On SKU] | [How it's used] | [MVP / H1] |

### Integration Requirements
[Source: POV Partner App Strategy & Technical Summary — Integrations]

| External System | Integration Type | Data Direction | MVP / Post-MVP |
|----------------|-----------------|----------------|----------------|
| [System 1] | [REST API / Batch / Event] | [In / Out / Bi] | [MVP / H1] |
| [System 2] | [type] | [direction] | [MVP / H1] |

*Direction is relative to Salesforce: In = data flowing into SF, Out = data from SF, Bi = bidirectional.*

### Data Requirements
[Source: POV Partner App Strategy & Technical Summary — Data Model]
- **Standard Objects used:** [list]
- **Custom Objects required:** [list or "None identified"]
- **Data sync strategy:** [description or "N/A"]
- **Data volume considerations:** [if known]

### UI Requirements
[Source: POV Partner App Strategy & Technical Summary — User Interface]
- **UI approach:** [Native LWC / Canvas / Custom portal / Other]
- **Key screens/components:** [list]

---

## Dependencies & Blockers [REQUIRED]

### Salesforce Dependencies
[Source: POV SF Cloud/SKU Dependencies]

| Dependency | Type | Customer Must Have | Status |
|------------|------|-------------------|--------|
| [SF Cloud 1] | License | Yes | [Confirmed / TBD] |
| [SF Cloud 2] | License | Yes | [Confirmed / TBD] |
| [Feature/SKU] | Configuration | [Yes / No] | [Confirmed / TBD] |

### External Dependencies
[Source: POV Partner App Strategy & Technical Summary — External Dependencies field]

| System / Party | Dependency Type | Risk | Owner |
|----------------|----------------|------|-------|
| [System 1] | [API availability / data access / contract] | [High / Med / Low] | [owner] |
| [Party] | [approval / contract / timeline] | [risk level] | [owner] |

### Open Blockers
[List anything that must be resolved before MVP build can start]
- [ ] **[Blocker description]** — Owner: [name] — Target: [YYYY-MM-DD]
- [ ] [Or: "No open blockers identified"]

---

## Risks [REQUIRED if known]

[Source: POV Problem Space — Risks bullets + Partner App Strategy & Technical Summary + red-team assessment if run.
Include at least one risk from each category: Competitive, Platform/Technical, Market/Regulatory.
Every mitigation must name a specific action and owner — "monitor" alone is not a mitigation.]

| Risk | Source | Likelihood | Impact | Mitigation | Owner |
|------|--------|-----------|--------|-----------|-------|
| [Risk 1] | [POV / Competitive / Churn / Platform / Market] | [H/M/L] | [H/M/L] | [specific action — not just "monitor"] | [Partner / Salesforce / Both] |
| [Risk 2] | [source] | [H/M/L] | [H/M/L] | [action] | [owner] |
| [Risk 3 — platform/API dependency] | Platform | [H/M/L] | [H/M/L] | [action] | [owner] |

**Competitive Positioning Note:**
[Source: red-team assessment Framework 1, or "Competitive analysis not yet run — schedule red team assessment before 03-Contract"]
[What makes this solution defensible against the top 2–3 competitive threats? Name the moat: unique data, workflow lock-in, domain expertise, distribution advantage, or other.]

---

## Phase Plan [REQUIRED]

[Source: POV MVP + Horizon 1 + Horizon 2 + Horizon 3]

| Phase | Scope Summary | Key Features | Target Timeframe |
|-------|--------------|-------------|-----------------|
| MVP | [One-sentence scope boundary — core validated use case, design partner pilot-ready] | [Feature 1, Feature 2] | [Q/date or TBD] |
| Horizon 1 | [Near-term expansion — integrations, additional personas, or secondary use case] | [deferred features] | [Q/date or TBD] |
| Horizon 2 | [Platform deepening — AI/ML maturation, advanced analytics, or scaled deployment] | [longer-term] | [Q/date or TBD] |
| Horizon 3 | [Strategic expansion — ecosystem play, new vertical, or marketplace positioning] | [long-range] | [Q/date or TBD] |

---

## Commercial Context [REQUIRED if known]
[Source: POV ISV Commercial Model + refs/pull-through-gtm.md]

**App Type:** [ISVforce / OEM/Embedded / Mixed/OSP / Reseller / Consumption — from POV]
**Licensing Model:** [PUPM / POPM / Tiered / Other — from POV]

### Pull-Through Opportunity
[Source: refs/pull-through-gtm.md — map this solution to specific Salesforce SKUs. "TBD" is not acceptable here — name the SKUs or flag as a required decision with an owner.]

| Salesforce SKU | Pull-Through Trigger | Est. ACV Impact | Timeline |
|----------------|---------------------|-----------------|----------|
| [Edition upgrade / Industry Cloud / Einstein / Data Cloud / Other] | [What in this solution requires or drives this SKU] | [$/user/year or deal-level estimate] | [MVP / H1] |
| [SKU 2] | [trigger] | [impact] | [timeline] |

### Go-to-Market Motion
[Select the primary motion and describe how it operates for this partner. Source: refs/pull-through-gtm.md.]

**Primary GTM:** [AppExchange Co-Sell / Marketplace Self-Serve / SI Channel / Co-Marketing / OEM Direct]
**Co-sell approach:** [How partner seller + Salesforce AE divide the deal — who owns what]
**Target deal profile:** [Existing Salesforce customer adding this app / New Salesforce + ISVforce together / OEM bundle]

### Sales Activation Plan
[What must be in place before co-sell can launch. Flag each item as Ready / In Progress / Not Started.]

| Activation Asset | Status | Owner | Target Date |
|-----------------|--------|-------|-------------|
| PADA signed with revenue share % defined | [Ready / In Progress / Not Started] | [owner] | [date] |
| AE one-pager complete | [status] | [owner] | [date] |
| Deal registration enabled in Partner Community | [status] | [owner] | [date] |
| SPIFF structure confirmed with PAM | [status] | [owner] | [date] |
| Partner sellers trained on co-sell process | [status] | [owner] | [date] |
| Target AE list and account overlap identified | [status] | [owner] | [date] |

---

## Program Alignment [REQUIRED if known]
[Source: POV Solution Alignment]

**Salesforce Blueprint Gap(s) Addressed:** [Specific capability gap(s) — from POV, or "TBD — owner: [name]"]
**Sales Play Alignment:** [Named Sales Play — from POV, or "Not identified"]
**Salesforce Stakeholder Needs:** [Product / Advisory / Sales stated needs — from POV, or "Not yet validated"]

---

## Industry Alignment [REQUIRED if known]

[Source: matched refs/verticals/ file (via refs/industry-alignment.md router) + POV Problem Space + partner research.
Every market data figure must name a source. If figures are unverified estimates, label them "Estimated." Do not assert market size without a named source.]

**Target Vertical:** [Healthcare & Life Sciences / Financial Services / Manufacturing / Retail & Consumer Goods / Public Sector / Energy & Utilities / Other — name it]
**Salesforce Industry Cloud:** [Health Cloud / FSC / Manufacturing Cloud / etc.]
**Relevant Industry Blueprint Gap:** [Specific capability gap this solution fills in the Salesforce vertical playbook]

### Market Context
[Lead with the conclusion: one sentence on why the market timing makes this solution urgent now.]

| Dimension | Detail | Source |
|-----------|--------|--------|
| Market Size | [$ figure and year] | [Analyst / publication] |
| Growth Rate | [CAGR %] | [Source] |
| Problem Cost | [$ cost of the unresolved problem — per org, per event, or at market scale] | [Source] |
| Regulatory Driver | [Named regulation or mandate creating urgency] | [Regulatory body] |

### Focus Areas & Aligned Use Cases

| Focus Area | Industry Priority | This Solution's Use Case | Strategic Fit |
|------------|------------------|------------------------|--------------|
| [Focus Area 1 — from matched refs/verticals/ file] | [Why it's a top priority in this vertical] | [How this solution addresses it] | [Strong / Moderate / Adjacent] |
| [Focus Area 2] | [priority rationale] | [use case] | [fit rating] |
| [Focus Area 3] | [priority rationale] | [use case] | [fit rating] |

**Positioning note:**
[One sentence on why this solution fits the Salesforce industry narrative for this vertical — what it adds to the story a Salesforce AE is already telling a customer in this space.]

---

## Success Metrics [REQUIRED]

[Source: POV KPIs — translate each KPI into a measurable target with a measurement method]

| KPI | Target | How Measured | Phase |
|-----|--------|-------------|-------|
| [KPI 1 from POV] | [specific target] | [measurement method] | MVP |
| [KPI 2] | [target] | [method] | MVP |
| [KPI 3] | [target] | [method] | H1 |

---

## Confidence & Open Items

**Confidence:** [0.0–1.0. Start from POV confidence score. Lower if any REQUIRED section is TBD or technical requirements are unconfirmed. Raise only if eng team has reviewed and confirmed architecture details.]

**Assumptions this plan rests on:**
1. [Assumption 1]
2. [Assumption 2]

**Open Items (TBD):**
- [Section or item flagged TBD — owner — target date]
- [Or: "No open items — all required sections complete"]

---

## Next Steps & Decisions Required [REQUIRED]
[What must happen before the MVP build can be green-lit or the next OG Tech Strategy Framework milestone reached.]

| Action | Owner | Target Date | Status |
|--------|-------|-------------|--------|
| [Decision or commitment needed — e.g., "Partner eng team to confirm architecture feasibility"] | [name] | [YYYY-MM-DD] | [Open / In Progress / Done] |
| [e.g., "Pilot customer [Name] to confirm participation"] | [name] | [YYYY-MM-DD] | [Open] |
| [e.g., "PAM to complete PADA with partner"] | [name] | [YYYY-MM-DD] | [Open] |
