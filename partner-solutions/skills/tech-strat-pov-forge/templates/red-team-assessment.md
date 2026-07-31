# Red Team Assessment Output Template

Output structure for Stage 9. Fill every section from the framework outputs.
Do not leave [placeholder] text in delivered output — if a section is genuinely unknown, write "Not assessed — TBD" with a named owner.

---

# [Partner Name] — Partner Solution Red Team Assessment
**Assessment Date:** [YYYY-MM-DD]
**POV Reference:** [POV document date or link]
**Assessor:** [name, role]
**Scope:** [Which frameworks were run: all 6 / subset — list if partial]

---

## Framework 1: Competitive War Game

**Governing conclusion:** [One sentence — the single most important competitive finding. Lead with this.]

**Top 3 Competitive Threats:**

| Competitor / Threat | Attack Vector | Key Vulnerability Exploited | Timeline |
|--------------------|--------------|---------------------------|---------|
| [Named company or "Salesforce native"] | [Specific mechanism — not "undercut on price"; name how] | [Specific partner weakness] | [Months to threat materializing] |
| [Threat 2] | [mechanism] | [weakness] | [timeline] |
| [Threat 3] | [mechanism] | [weakness] | [timeline] |

**Biggest Competitive Vulnerability:**
[The one gap to close before MVP launch — specific and actionable]

**Recommended Action:**
[What the partner should do and by when — direct, not hedged]

---

## Framework 2: Customer Exit Simulation

**Governing conclusion:** [One sentence — the most likely churn pathway for this solution]

**Churn Trigger:** [The specific moment or event that causes the Salesforce platform owner / VP of CRM to cancel — not a general complaint]

**Exit Destination:** [Named competitor / Salesforce native feature / in-house build / do-nothing — and why that option wins]

**Retention Lever:** [The one specific change that would prevent this churn — not "better support" or "more features"]

**Churn Risk Rating:** [High / Medium / Low]
**Rationale:** [One sentence explaining the rating]

**Recommended Action:**
[What the partner should build, commit, or change to close this churn vector before launch]

---

## Framework 3: Platform Dependency Scan

**Governing conclusion:** [One sentence — the highest-severity platform dependency and what it means]

**Vulnerability Matrix:**

| Dependency | Category | Likelihood | Severity | Priority |
|-----------|---------|-----------|---------|---------|
| [API, feature, SKU, or capacity item] | [API Fragility / Feature Overlap / Licensing Dependency / Partner Capacity / Customer Concentration] | [H/M/L] | [Critical/H/M/L] | [1 = highest] |
| [Dependency 2] | [category] | [H/M/L] | [H/M/L] | [rank] |
| [Dependency 3] | [category] | [H/M/L] | [H/M/L] | [rank] |

**#1 Priority Vulnerability:**
[Top-ranked item — what it is, why it's highest priority, and what happens if it materializes]

**The Hidden Risk:**
[One vulnerability the partner has almost certainly not considered — often licensing dependency or feature overlap]

**Recommended Actions:**
1. [Action for #1 priority — owner and timeline]
2. [Action for hidden risk — owner and timeline]

---

## Framework 4: 18-Month Invalidation Scenarios

### Scenario A: Salesforce Native Capability
**What changes:** [Specific feature or product announcement — name it, don't generalize]
**Impact:** [Effect on this solution's value proposition, customer retention, and renewal conversations]
**Early warning signs:**
- [Observable signal 1 — something checkable today, e.g., "Salesforce Einstein blog post on [specific topic]"]
- [Observable signal 2]
**Probability:** [High / Medium / Low] — **Rationale:** [one sentence]
**If this happens:** [Specific partner response — pivot, differentiate, or exit gracefully]

### Scenario B: Vertical Regulation Shift
**What changes:** [Named regulation, guidance, or enforcement action]
**Impact:** [Customer compliance requirement, market access restriction, or new opportunity]
**Early warning signs:**
- [Observable signal 1]
- [Observable signal 2]
**Probability:** [High / Medium / Low] — **Rationale:** [one sentence]
**If this happens:** [Specific partner response]

### Scenario C: Market Consolidation
**What changes:** [Named acquirer or consolidation event — e.g., "Epic acquires [competitor]"]
**Impact:** [Distribution advantage shift, customer switching dynamics, pricing pressure]
**Early warning signs:**
- [Observable signal 1]
- [Observable signal 2]
**Probability:** [High / Medium / Low] — **Rationale:** [one sentence]
**If this happens:** [Specific partner response]

---

## Framework 5: Salesforce Investment Teardown

[Adversarial role: the Salesforce investment committee looking for reasons to pass.]

**Three biggest holes (a "no" rests on these):**
1. [Specific hole — not "needs traction"]
2. [Specific hole]
3. [Specific hole]

**The question the partner can't answer yet:** [The single meeting-ending question]

**Named comparable that tried this and failed:** [Real named ISV + the specific failure mechanism that could repeat here — or "No verified comparable identified — flag as TBD" with what precedent to check]

---

## Framework 6: Commercial Model Pressure Test

[Adversarial role: a skeptic who accepts the product works but attacks whether the money works.]

**Where the pull-through math breaks:** [Specific price point, attach-rate assumption, or edition/SKU dependency the target install base lacks]

**Revenue-share viability:** [At what customer count / ACV the PADA economics actually work, and whether the partner has it]

**Buyer's best alternative:** [Named cheaper competitor / Salesforce-native path / do-nothing that undercuts the commercial premise] — **the one change that makes the model defensible:** [specific change]

---

## Synthesis: Top Vulnerabilities & Recommended Actions

[Lead with the conclusion — the one thing Salesforce needs to know before committing OG Tech Strategy Framework resources]

**Governing finding:** [One sentence — the most important thing this red team assessment surfaced]

**Biggest Blind Spot:** [The one risk that sits outside the partner's normal frame and was NOT surfaced by Frameworks 1–6 — something they are almost certainly not thinking about. Must not restate a finding already in the table.]

| Rank | Vulnerability | Source | Likelihood | Severity | Recommended Action | Owner |
|------|-------------|--------|-----------|---------|-------------------|-------|
| 1 | [Most critical vulnerability] | [Framework #] | [H/M/L] | [Critical/H] | [Specific action with timeline] | [Partner / Salesforce / Both] |
| 2 | [Second vulnerability] | [Framework #] | [H/M/L] | [H/M] | [Action] | [owner] |
| 3 | [Third vulnerability] | [Framework #] | [H/M/L] | [H/M] | [Action] | [owner] |

**Stopping Rule:**
[One specific, observable precondition that must be true before Salesforce invests significant OG Tech Strategy Framework resources in this partner. This is not optional — do not omit it. Example: "Partner must name at least one enterprise pilot customer willing to go on record before 03-Contract resources are committed."]

**Confidence:** [0.0–1.0 — calibrate: start at 0.7, lower if information about competitive landscape or partner financials was unavailable]

**Assumptions this assessment rests on:**
1. [Named assumption 1]
2. [Named assumption 2]
3. [Named assumption 3]

**What would change this assessment:**
[Specific new information — e.g., "Named pilot customer commitment," "Partner architecture review confirms no deprecated API dependency" — that would raise confidence or materially change the top vulnerability ranking]
