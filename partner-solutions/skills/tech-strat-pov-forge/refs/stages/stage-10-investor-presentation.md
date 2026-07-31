# Stage 10 — Investor Presentation

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 10 — Investor Presentation (optional)**
Triggered when the user requests an investor deck, pitch deck, investor presentation, or fundraising materials.

Load `templates/investor-presentation.html`.
Load `validation/investor-checklist.md`.

Map POV sections to slides in this order:
1. Cover → Partner Name + solution tagline + "Built on Salesforce" badge
2. Problem → Problem Statement (condensed) + top 2 Significance stats + Problem Cost
3. Solution → Solution Statement (plain English, ≤2 sentences) + top 3 Benefits as headline stats
4. Market Opportunity → Market Size + CAGR + Problem Cost from Industry Alignment; include named analyst source
5. Product → 3-step "How It Works" from Use Cases (one sentence each); App type badge (ISVforce / OEM)
6. Traction → Named customers (logos or text blocks) + top 3 confirmed KPI benchmarks + any awards
7. Business Model → Commercial model type + ACV range + pull-through SKUs with estimated ACV impact
8. Team → Founder names, titles, and one-line credential from research
9. Partnership → Org62 Opportunity stage + pull-through opportunity + co-sell motion summary
10. Next Steps / Ask → MVP scope + design partner status + 3 specific next steps

Fill `templates/investor-presentation.html` via the HTML Output Method (`refs/html-output-method.md`) — do not regenerate the HTML inline and do not produce a Markdown intermediate. Fill every `{{PLACEHOLDER}}` token from POV data; use "TBD" with owner attribution if the POV has a gap. Run every check in `validation/investor-checklist.md` before delivering.

**Product-slide badges:** `{{CLOUD_DEP_1}}` and `{{CLOUD_DEP_2}}` are the partner's primary Salesforce cloud/SKU dependencies — fill from the POV's **Salesforce Cloud/SKU Dependencies** (e.g. "Salesforce Health Cloud", "Data Cloud"). `{{COMPLIANCE_BADGE}}` is the one most relevant compliance standard for the vertical, from the matched vertical file's Regulatory drivers (e.g. "HIPAA Compliant", "FedRAMP Authorized"). Name only what the POV/vertical supports; if a standard does not apply, fill the most relevant cloud/SKU instead rather than inventing a certification.

**Opportunity-stage tokens (Partnership slide):** `{{OPPORTUNITY_STAGE}}` is the current Org62 Opportunity stage as code+name (e.g. `02-Assess`) — use the exact stage value from the POV's "Org62 Opportunity Stage" field, not a number. `{{OPPORTUNITY_STAGE_LABEL}}` is a short plain-English status descriptor for that stage (e.g. "POV validation in progress" for 02-Assess, "Contract initiated" for 03-Contract) — keep it under 5 words. `{{CONTRACT_TARGET_DATE}}` is the target date to reach 03-Contract; the slide renders "targeting 03-Contract by {{CONTRACT_TARGET_DATE}}", so fill a date (e.g. "Q3 FY26") or "TBD".

Deliver the HTML file path to the user. Output a summary of what each slide contains after generation.
