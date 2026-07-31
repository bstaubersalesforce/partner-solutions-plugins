# Stage 8 — MVP Build Plan

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 8 — Generate MVP Build Plan (optional)**
Triggered when the user requests a build plan, MVP plan, sprint-ready output, or feature breakdown from the POV.

Load both `templates/mvp-build-plan.md` (Markdown output) and `templates/mvp-build-plan.html` (HTML output).
Load `validation/mvp-checklist.md`.

Map POV sections to build plan sections in this order:
1. Problem Statement + Significance + Challenges → Executive Summary Problem line; also anchors the "why" of every user story
2. Vision Statement + Solution Statement → Executive Summary narrative (2–3 sentences)
3. MVP scope → In Scope list; Horizon 1 → Out of Scope / Horizon 1; Horizon 2 → Out of Scope / Horizon 2; Horizon 3 → Out of Scope / Horizon 3 (preserve each horizon distinctly — do not merge)
4. Use Cases × N → Feature Breakdown (one block per use case; for Markdown: delete placeholder Feature 2 and Feature 3 blocks if the POV has fewer than 3 use cases; for HTML: replace unused feature `<section>` elements with an empty string — never leave `{{FEATURE_N_*}}` tokens unfilled)
5. Personas + Use Cases → User Stories first (establish persona + job-to-be-done), then Acceptance Criteria (At least one AC per feature traceable to a POV KPI)
6. KPIs → Success Metrics table + anchor for AC traceability in step 5
7. Partner App Strategy section — Application Type, Integrations, UI, Data Model → Technical Requirements (SF platform, integrations, data, UI)
8. SF Cloud/SKU Dependencies → Salesforce Platform Requirements table
9. External Dependencies → Integration Requirements table + External Dependencies table
10. Problem Space — Risks bullets → Risks table
11. Horizon 1 → Phase Plan H1 row; Horizon 2 → Phase Plan H2 row; Horizon 3 → Phase Plan H3 row (MVP scope → MVP row)
12a. Industry vertical + market data + focus areas → Industry Alignment section (populate from the matched `refs/verticals/` file loaded in Stage 1, or load it now if generating the build plan standalone; if the vertical is not listed, flag TBD with a named owner and target date)
12. ISV Commercial Model → Commercial Context section
13. Solution Alignment → Program Alignment section (Blueprint gaps, Sales Play, stakeholder needs)
14. Identify open decisions needed to green-light the MVP → Next Steps & Decisions Required table (owner + target date for each)

Run every check in `validation/mvp-checklist.md` before delivering.
If any check fails, repair the output before delivering — do not deliver a failing build plan.

**Interactive vs. non-interactive delivery — pick based on how this stage was invoked:**

- **Non-interactive (fanned-out subagent, or any brief that says "generate to disk / run non-interactively").** There is no user in the loop to approve. Skip the review loop entirely: run validation, produce the final Markdown **and** HTML in one pass, and return the file paths. Do not present a draft and do not wait for an Approve that will never come. The orchestrator already holds the user's Stage 7 POV approval, which covers this downstream artifact.
- **Interactive (generated inline in a live conversation).** Follow the Stage 7 Interactive Review process below.

**Interactive Review process (interactive mode only) — mirrors the SKILL.md Stage 7 loop:**
1. Present the Markdown draft first — do not generate HTML
2. Prompt: "Review the draft above. Reply with specific changes, or reply **Approve** when ready to commit the HTML version."
3. Apply feedback, show only changed sections, repeat until Approve
4. On Approve: run validation checks, then fill `templates/mvp-build-plan.html` via the HTML Output Method (`refs/html-output-method.md`) and deliver the file path
5. Append to final output: confidence score (0.0–1.0 with rubric), named assumptions, explicit TBD list
