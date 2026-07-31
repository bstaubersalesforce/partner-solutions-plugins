# MVP Build Plan Pre-Delivery Validation Checklist

Run every check before delivering the MVP Build Plan.
If any check fails, repair before delivering — do not deliver a failing build plan.

## Required Sections Present

- [ ] Executive Summary — present and ≤ 3 sentences
- [ ] MVP Scope — In Scope list present and non-empty
- [ ] MVP Scope — Out of Scope section present (or explicitly states "No deferred items at this time")
- [ ] Feature Breakdown — at least 1 feature block complete; unused Feature 2 and Feature 3 blocks removed
- [ ] Each feature block has: title, persona, user story in As a/I want/so that format, at least 1 acceptance criterion
- [ ] Technical Requirements — Salesforce Platform Requirements table present with app type specified
- [ ] Technical Requirements — Integration Requirements present (or "No external integrations in MVP scope")
- [ ] Dependencies — Salesforce Dependencies table present
- [ ] Dependencies — Open Blockers section present (or "No open blockers identified")
- [ ] Risks — at least 1 risk named, or section explicitly states "No risks identified at this stage"
- [ ] Phase Plan — MVP row complete with scope and key features; H1, H2, and H3 rows present (H3 may state "Not yet defined — from POV" but must not be silently omitted)
- [ ] Industry Alignment — target vertical named, Salesforce Industry Cloud identified, at least 2 market data figures present with named sources
- [ ] Industry Alignment — at least 2 focus areas mapped with aligned use cases and strategic fit ratings
- [ ] Commercial Context — app type and licensing model present (or TBD with named owner)
- [ ] Program Alignment — Blueprint gap identified (or TBD with named owner)
- [ ] Success Metrics — at least 2 KPIs present with targets and measurement methods
- [ ] Confidence score stated (0.0–1.0) with at least 1 named assumption; score is calibrated (not 0.9+ when any REQUIRED section is TBD)
- [ ] Next Steps & Decisions Required — at least 1 action with owner and target date
- [ ] No unfilled `{{PLACEHOLDER}}` tokens remain in the output (HTML or Markdown)
- [ ] Header metadata filled: Partner Name, Build Plan Date, POV Reference are not placeholder text

## Quality Checks

### User Stories
- [ ] Each user story follows exactly: "As a [specific persona], I want to [specific capability], so that [measurable outcome]"
- [ ] No user story names a generic persona ("a user," "customers," "users")
- [ ] No user story ends without a measurable outcome — "so that [they can do X better]" is not measurable; "so that [processing time drops by 30%]" is
- [ ] No user story is a restatement of the Solution Statement from the POV

### Acceptance Criteria
- [ ] Each Given/When/Then criterion has all three parts: Given [context], when [specific action], then [specific system response or outcome]
- [ ] At least one AC per feature is directly traceable to a KPI from the POV (not invented)
- [ ] No AC is a restatement of the user story in different words

### Scope
- [ ] MVP In Scope items are buildable — specific enough to hand to an engineer (not "add AI capabilities" or "improve efficiency")
- [ ] Horizon 1 and Horizon 2 items are named where they exist in the POV — not silently omitted
- [ ] No MVP scope item depends on an external system flagged as High risk in the Dependencies section without that dependency being called out

### Technical Requirements
- [ ] Salesforce cloud/SKU dependencies name specific clouds (not "various Salesforce products" or "Salesforce platform")
- [ ] Integration table names specific external systems (not "third-party systems" or "existing tools")

### Risk Coverage
- [ ] Risks table includes at least one risk from each category: Competitive, Platform/Technical, Market/Regulatory (or explicitly states "Not yet assessed — schedule red team assessment")
- [ ] No risk row has "monitor" as its only mitigation — every mitigation names a specific action and owner
- [ ] Competitive Positioning Note is present — either names the moat or explicitly states "Competitive analysis not yet run"
- [ ] If a red team assessment was run, the #1 vulnerability from the Synthesis section appears in the Risks table or is documented as a deferred action with a named owner
- [ ] App type is one of: Native managed package, Composite, Hybrid (with description) — not left as a placeholder

### Traceability
- [ ] Every feature can be traced to a named POV use case (Source Use Case field is filled, not placeholder text)
- [ ] Every KPI in Success Metrics can be traced to a KPI from the POV
- [ ] The Blueprint Gap in Program Alignment matches the gap named in the POV Solution Alignment section

## Failure → Repair Instructions

**Generic user story:**
Return to the POV personas section. Pick the specific named persona (Admin, Internal User, or External User role description). Reframe the user story using their specific job-to-be-done from the POV use case.

**Vague measurable outcome in user story:**
Anchor the "so that" clause to a KPI from the POV. If no KPI maps to this feature, surface that gap explicitly rather than writing a vague outcome.

**AC missing Given/When/Then structure:**
Apply the format strictly. "Given [the work order is assigned and open], when [the dispatcher clicks Schedule], then [the system returns the top 3 available field technicians ranked by proximity and skill match]."

**AC that is a restatement of the user story:**
The user story describes the goal. The AC describes a specific verifiable condition. They should not use the same language.

**Vague MVP scope item:**
Make it buildable: name the Salesforce object, page, component, or flow. "AI scheduling" → "Einstein Next Best Action recommendations on the Work Order record page, using Field Service Lightning scheduling rules."

**Missing SF cloud specifics:**
Return to POV Partner App Strategy & Technical Summary. List each cloud dependency with how it is used. If unknown, flag as TBD — do not write "Salesforce platform."

**Missing traceability (feature to use case):**
Fill in the Source Use Case field from the POV. If no use case maps to this feature, the feature should not be in the MVP Build Plan without a clear rationale.

**KPI in Success Metrics not traceable to POV:**
Return to the POV KPIs section. Each row in the Success Metrics table must map to a KPI already named in the POV. If the build plan introduced a new KPI not in the POV, either remove it or flag it as "Not in POV — proposed addition, needs validation with partner." Do not invent KPI targets that have no basis in the POV.

**Blueprint Gap doesn't match POV Solution Alignment:**
Return to the POV Solution Alignment section — Blueprint Gap(s) Addressed field. Copy the exact capability gap language from the POV into Program Alignment. Do not rephrase or generalize. If the POV says "Care Gap in Care Management Blueprint — post-discharge follow-up workflow," the build plan must say the same, not "Healthcare workflow improvement."

**Confidence score missing or has no named assumptions:**
Set the confidence score based on this rubric: start at 0.7 as a baseline. Lower by 0.1 for each REQUIRED section flagged TBD. Lower by 0.1 if technical requirements have not been confirmed with the partner's engineering team. Raise to 0.85+ only if the partner has demonstrated the solution and named pilot customers. Name at least 2 assumptions the score rests on (e.g., "Partner's engineering team can deliver the integration with [System X]," "Pilot customer [Name] will confirm commitment at next call").

**Horizon 1 / Horizon 2 items silently omitted:**
If the POV has Horizon 1 or Horizon 2 items, they must appear in the Out of Scope section. Return to the POV MVP & Development Priorities section and copy each Horizon item into the appropriate Out of Scope subsection. If the POV says "TBD" for a horizon, write "Not yet defined — from POV" rather than omitting the subsection entirely.

**AC not traceable to a POV KPI:**
At least one AC per feature must be verifiable against a KPI from the POV. To fix: find the KPI from the POV that most closely relates to this feature's outcome. Write an AC whose "then" clause specifies a threshold or result tied to that KPI. Example: if the POV KPI is "Reduce scheduling time by 30%," a valid AC is: "Given a new work order is created, when the dispatcher clicks Schedule, then the system returns a ranked list of available technicians within 5 seconds (supporting the 30% scheduling time reduction KPI)."

**Risks table missing a category (Competitive / Platform / Market):**
For Competitive: Surface the top named competitor from the POV or discovery questions. Name the specific attack vector (pricing, distribution, native SF capability). Assign mitigation to Partner.
For Platform: Name the specific Salesforce API or feature this solution depends on. Rate likelihood of change. Assign mitigation to Partner + Salesforce tech review.
For Market: Name the most likely regulatory or consolidation event in the partner's vertical. State the probability and one early warning sign to watch. If genuinely unknown, flag as TBD with a named owner and target date.

**"Monitor" as the only mitigation:**
Replace with a specific action: who does what, by when, and what triggers escalation. Example: replace "Monitor Salesforce roadmap" with "Partner's CTO reviews Salesforce release notes on [specific topic] at each quarterly release; escalates to Salesforce PAM if [X feature] ships."

**H3 row missing from Phase Plan:**
H3 is not optional. If the POV has no H3 content, write "Strategic expansion — not yet defined" and flag it as TBD with a named owner and target date. Do not silently omit the row. The absence of a H3 vision is itself a signal worth surfacing.

**Industry Alignment section missing or incomplete:**
Load refs/industry-alignment.md (the router) and identify the partner's primary vertical from the POV Problem Space and Target Markets sections, then load the matching file from refs/verticals/. If a matching vertical file exists, populate market size, CAGR, problem cost, and regulatory driver from it — cite the source. If the vertical is not covered, flag each missing figure as TBD with: "No analyst data sourced — owner: [name], target: [date]." Do not leave market data fields empty or filled with generic assertions.

**Focus areas not mapped to use cases:**
Return to the matched refs/verticals/ file. For the partner's vertical, identify which named focus areas the solution addresses. Map each to a specific POV use case. If no use case maps to a named focus area, that is a positioning gap — surface it explicitly rather than forcing a weak mapping.
