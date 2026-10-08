# {{PARTNER_NAME}} — Partner Account Tech Plan

*Internal. Org62 Account {{ORG62_ACCOUNT_ID}} · {{PARTNER_TIER}} · PAM {{PAM_NAME}} · Author {{AUTHOR}} · {{DATE}} · Re-review: {{REREVIEW_CADENCE}}*
<!-- PARTNER_TIER: e.g. "Tier-1 OEM / Security-Priority partner" — the account's standing flags. -->

> **Data safety:** cites cases by number + root cause only; no credentials/PII. Raw captures in gitignored `.notes/`.

---

## Theory of Growth

{{THEORY_OF_GROWTH}}
<!-- Where the partnership is going and its potential, in a few sentences. The executive hook. Written last, from the whole plan. -->

> **Posture (read first):** {{POSTURE_CALLOUT}}
<!-- The elevation-not-encroachment framing up front: the partner is the <domain> OS, Salesforce is the platform beneath it; our initiatives EXTEND their stack, they don't replace it. Name the exec-sponsor pairing (SF ↔ partner). See refs/trust-posture.md. -->

---

## V2MOM

**Vision** — {{VISION}}

**Values**
- Elevation, not encroachment — {{ELEVATION_STATEMENT}}
- {{VALUE_2}}

**Methods** (workstreams — each with its own nested Measures)
<!-- One ### Method block per workstream — add or remove blocks to match the plan (the dogfood used four: three workstreams + a GTM motion). Each Method carries its own Measures as children; only partnership-health measures sit in the cross-cutting line below. -->

### Method 1 — {{METHOD_1}}
{{METHOD_1_BODY}}
- **Measures:**
  - {{M1_KPI_1}} — baseline {{M1_BASELINE_1}} → target {{M1_TARGET_1}} by {{M1_HORIZON_1}} {{M1_PROPOSED_TAG_1}}
  - {{M1_KPI_2}} — …

### Method 2 — {{METHOD_2}}
{{METHOD_2_BODY}}
- **Measures:**
  - {{M2_KPI_1}} — …

### Method 3 — {{METHOD_3}}
{{METHOD_3_BODY}}
- **Measures:**
  - {{M3_KPI_1}} — …

**Obstacles** (each traced to a gap-closure row below)
- {{OBSTACLE_1}}
- {{OBSTACLE_2}}

**Measures — cross-cutting (partnership health)**
- Active executive relationships — current {{EXEC_REL_CURRENT}} → target ≥3 before H1
- Gaps moved RAG 🔴→🟡→🟢 per QBR — {{GAP_CLOSURE_TARGET}}
- Consumption growth / joint pipeline — {{CONSUMPTION_MEASURE}}

---

## 1. Partner Profile & Trust Posture
- **Profile:** {{PROFILE}}
- **ICP (Ideal Customer Profile):** {{ICP}}
- **Technology consumed from Salesforce:** {{CONSUMED_TECH}}
- **Pipeline / deals (from PAM forecast):** {{PIPELINE}}
- **Trust / relationship posture:** {{TRUST_POSTURE}}
- **Stakeholder / power map + activation plan:** {{STAKEHOLDER_MAP}}

## 2. Current-State Assessment (pillar-scored RAG · living)
*Assessed {{ASSESSMENT_DATE}} · re-review {{REREVIEW_CADENCE}}*

{{CURRENT_STATE_PILLARS}}
<!-- per pillar: RAG + one-line rationale -->

## 3. Blocker Assessment
- **Case scan:** {{CASE_SCAN_SHAPE}} <!-- Platform/App vs Partner-Program volume, # open, 18mo -->
- **Deep-dived (REAL) blockers:**
{{BLOCKER_DIAGNOSES}}
<!-- case # + one-line root cause each -->

## 4. Tech Strategy POV
{{POV_SUMMARY}}

### 4a. Commercial / Consumption Opportunities
{{CONSUMPTION_OPPORTUNITIES}}

### 4b. Red Team Assessment
{{RED_TEAM}}

### 4c. Partner Readiness Scorecard
{{READINESS_SCORECARD}}

## 5. PoC Opportunities
{{POC_OPPORTUNITIES}}

## 6. Enablement / Workshop
{{WORKSHOP_PLAN}}

## 7. Roadmap & Go-Forward Gap Closure

### Roadmap (H0 / H1 / H2)
{{ROADMAP}}

### Go-Forward Plan — Closing the Gaps
| Gap | Source | Closure action | Owner | Horizon | RAG |
|-----|--------|----------------|-------|---------|-----|
{{GAP_CLOSURE_MATRIX}}

*Closure KPI: # gaps moved RAG 🔴→🟡→🟢 per QBR.*

## 8. Governance & Measures (influence, not own)
- **RoB / QBR cadence (owned by PAM/account team):** {{CADENCE}}
- **Decision rights (PIE/PS advises · account team owns):** {{DECISION_RIGHTS}}
- **Joint success metrics:** {{JOINT_METRICS}}

## 9. Owners & Next Steps
- **Named driver per workstream:** {{OWNERS}}
- **Immediate next actions:** {{NEXT_STEPS}}

## Reusable lessons applied
<!-- Name the prior strategic-ISV engagements whose patterns this plan borrows (e.g. Bullhorn = packaging/tech-debt + off-platform-drift; nCino = elevation posture + 3 Moves). Pull only the lessons that match this partner's situation. See refs/trust-posture.md. -->
{{REUSABLE_LESSONS}}

---

### Confidence, assumptions & open items
- **Confidence:** {{CONFIDENCE}}
- **Assumptions:** {{ASSUMPTIONS}}
- **Open items / degraded sections:** {{OPEN_ITEMS}}

> **Sources:** {{SOURCES}}
> <!-- PDF/notes, partner site, Slack channels, Org62 case-scan date. -->
> **INTERNAL ONLY — scrub before any partner-facing use.** Raw detail incl. any credentials kept to gitignored `.notes/`, never shared.
