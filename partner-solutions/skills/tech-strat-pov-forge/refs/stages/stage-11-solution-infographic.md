# Stage 11 — Solution Infographic

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 11 — Solution Infographic (optional)**
Triggered when the user requests an infographic, visual summary, solution overview, one-pager visual, shareable visual, or leave-behind graphic.

Load `templates/solution-infographic.html`.
Load `validation/infographic-checklist.md`.

Map POV sections to infographic panels:
1. Problem panel → Problem Statement condensed to ≤15 words + top 2 Significance statistics (confirmed figures only)
2. Solution panel → Solution Statement (1 sentence) + 3-step simplified How It Works flow
3. Outcomes panel → Top 3 KPI benchmarks (confirmed metrics only — do not use proposed targets here)
4. Market panel → Market Size + CAGR + Target Vertical + one Regulatory Driver
5. Branding → Company name + "Built on Salesforce" badge + date
6. Integration-row badges (`{{INT_BADGE_1}}`–`{{INT_BADGE_4}}`) → the named Salesforce clouds/SKUs and key integrations from the POV's **Architecture Summary** (Salesforce Cloud/SKU Dependencies + Integrations) and the matched vertical file — e.g. the primary Industry Cloud, a key integration target, a relevant compliance/standard. Use only what the POV or vertical names; if fewer than four apply, drop the unused badge `<span>`s rather than inventing one. ("AppExchange" is a fixed badge — leave it.)

Fill `templates/solution-infographic.html` via the HTML Output Method (`refs/html-output-method.md`) — do not regenerate the HTML inline and do not produce a Markdown intermediate. Fill every `{{PLACEHOLDER}}` token. Use only confirmed metrics in the Outcomes panel — do not use proposed KPI targets as if they are achieved results. Run every check in `validation/infographic-checklist.md` before delivering.

Deliver the HTML file path to the user.
