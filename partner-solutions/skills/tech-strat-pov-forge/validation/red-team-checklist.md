# Red Team Assessment Pre-Delivery Validation Checklist

Run every check before delivering the Red Team Assessment.
If any check fails, repair before delivering.

## Structure
- [ ] All 6 frameworks present: Competitive War Game, Customer Exit Simulation, Platform Dependency Scan, 18-Month Invalidation Scenarios, Salesforce Investment Teardown, Commercial Model Pressure Test
- [ ] No `[placeholder]` text remains anywhere in the output
- [ ] Synthesis section present with top vulnerabilities and a recommended action per vulnerability
- [ ] Synthesis includes a **Biggest Blind Spot** — a risk not surfaced by any of Frameworks 1–6 (not a restatement of a table row)
- [ ] **Stopping Rule present** — the assessment is invalid without one

## Specificity (the core quality bar)
- [ ] Every finding names this partner's specifics (named competitor, named SF dependency, named customer/segment) — not generic ISV-in-this-vertical statements
- [ ] Competitive War Game names at least one real competitor and their concrete attack vector (pricing, distribution, native SF capability)
- [ ] Platform Dependency Scan names specific Salesforce APIs/features/SKUs the solution depends on, not "the platform"
- [ ] Each invalidation scenario is concrete enough to disprove — a date/trigger/event, not "the market could change"
- [ ] Salesforce Investment Teardown names a real comparable ISV that failed (or explicitly flags "No verified comparable identified — flag as TBD") — not a hypothetical
- [ ] Commercial Model Pressure Test names the specific break point (price point, attach-rate, or edition/SKU dependency) — not "pricing is a risk"

## Failure → Repair
**Generic finding:** Regenerate with the partner's named competitors, dependencies, and accounts from the POV. If the statement would be true for any ISV in the vertical, it is not a finding.
**Missing Stopping Rule:** Add one observable precondition that must be true before Salesforce commits significant resources (e.g. "Partner names an enterprise pilot willing to go on record before 03-Contract").
