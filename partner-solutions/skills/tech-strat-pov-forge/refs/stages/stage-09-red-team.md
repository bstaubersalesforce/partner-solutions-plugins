# Stage 9 — Red Team Assessment

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 9 — Red Team Assessment (optional)**
Triggered when the user asks for adversarial analysis, threat assessment, "how would this fail," risk deep-dive, or preparation for a skeptical internal stakeholder review.

Load `refs/red-team-lenses.md`.
Load `templates/red-team-assessment.md`.
Load `validation/red-team-checklist.md`.

Run all 6 frameworks in sequence:
1. Competitive War Game — who steals this partner's customers in 12–18 months
2. Customer Exit Simulation — why the Salesforce platform owner / VP of CRM stops using this solution after 6 months
3. Platform Dependency Scan — single points of failure in the Salesforce ISV context
4. 18-Month Invalidation Scenarios — 3 specific scenarios that make this solution obsolete
5. Salesforce Investment Teardown — why the Salesforce investment committee would pass; force a named comparable ISV that tried this and failed
6. Commercial Model Pressure Test — where the pull-through math and revenue-share viability break

**Specificity gate (required after each framework):** Ask — does this output apply only to this partner, or could it apply to any ISV in this vertical? If generic, regenerate with the partner's specific details before continuing.

Fill in `templates/red-team-assessment.md` completely. Do not leave [placeholder] text in output.

Run every check in `validation/red-team-checklist.md` before delivering. If any check fails, repair before delivering.

Deliver:
- The red team assessment as a standalone Markdown document
- Surface the Synthesis section's top vulnerabilities with recommended actions before appending the full assessment
- The Synthesis must include a **Biggest Blind Spot** — a risk not surfaced by any of the 6 frameworks
- The Stopping Rule is mandatory — do not deliver a red team assessment without one

**This is a Markdown-native artifact — do not hand-build its HTML.** If an HTML view is needed (it is, whenever a home page is built), render it with `scripts/md-to-html.py` into `templates/document-shell.html` (`--label "Red Team Assessment"`), exactly as Stage 13 specifies. That shell carries the home-page back-link and guarantees zero unfilled tokens; a hand-rolled HTML page will silently omit the back-link. Always keep the `.md` — it is the download.
