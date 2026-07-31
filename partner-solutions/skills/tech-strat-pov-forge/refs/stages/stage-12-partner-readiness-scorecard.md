# Stage 12 — Partner Readiness Scorecard

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 12 — Partner Readiness Scorecard (optional)**
Triggered when the user requests a readiness scorecard, partner readiness assessment, partner scorecard, or a fit/readiness rating across the 18 strategy attributes.

Load both `templates/partner-readiness-scorecard.md` (Markdown output) and `templates/partner-readiness-scorecard.html` (HTML output).
Load `validation/scorecard-checklist.md`.
The 18 attributes and their definitions are fixed — they also appear in `refs/og-tech-strategy-framework.md` (Readiness Scorecard Attributes). Never drop, rename, or reorder them.

**Status / Rank scale:** 🟢 Strong · 3 / 🟡 Emerging · 2 / 🔴 Gap · 1. In the HTML, map to `rag-strong` / `rag-emerging` / `rag-gap` classes; blank = `rag-na` with an em dash.

**Population rule (evidence or blank — never guess):** Fill Status/Rank, Owner, and Notes only where the POV or research provides evidence, and cite that source in the Notes cell. Where there is no basis, leave the row blank — do not write "TBD" or a guessed rank in the table body. "Not yet assessed" attributes are listed only in the Assessment Basis block.

Map POV sections / research to attributes:
1. Solution Tier → Solution Alignment (owner: ISV Sales Lead + Tech Strategy Lead — often blank early)
2. Executive Sponsor → research / discovery (named sponsor each side)
3. Sales Fit → Target Markets named customers + Significance market size / TAM
4. Sales ACV Potential → Commercial Context pull-through SKUs
5. Commercial Model - ACV / PNR Potential → ISV Commercial Model (app type, licensing)
6. Product Fit → Solution Alignment Blueprint Gaps
7. Industry Fit → Industry Alignment + Problem Significance
8. ISV Team Fit → ISV Commercial Model + AppExchange listing signal
9. ISV Tech Alignment → Architecture Summary (native/composite, named SF deps)
10. Executive Alignment Sponsorship → research / discovery (named execs both sides)
11. Industry Value Chain Alignment → Industry Alignment value chain
12. Salesforce Blueprint Alignment → Solution Alignment (named Blueprint + capability)
13. Partner's Ability to Execute → research (alliance team, prior partnerships)
14. Partner's Ability to Sell → research (sales leadership, channel capability)
15. Customer & Target Account Alignment → Target Markets named customers vs. Salesforce accounts
16. Partner's ISV Tooling Readiness → research (PBO/COA/LMA usage; AppExchange listing implies some activation)
17. Partner's Technical Engagement → research / discovery (named architects, active API work)
18. Partner's Executive Engagement → research / discovery (named exec, documented commitment)

After scoring, compute the Readiness Snapshot from the table: Assessed count (non-blank rows), 🟢/🟡/🔴 tallies, average rank over assessed rows only, and name the 🔴/🟡 attributes most material to reaching 03-Contract.

Run every check in `validation/scorecard-checklist.md` before delivering. If any check fails, repair before delivering.

**Interactive vs. non-interactive delivery — pick based on how this stage was invoked:**

- **Non-interactive (fanned-out subagent, or any brief that says "generate to disk / run non-interactively").** There is no user in the loop to approve. Skip the review loop entirely: run validation, produce the final Markdown **and** HTML in one pass, and return the file paths. Do not present a draft and do not wait for an Approve that will never come. The orchestrator already holds the user's Stage 7 POV approval, which covers this downstream artifact.
- **Interactive (generated inline in a live conversation).** Follow the Stage 7 Interactive Review process below.

**Interactive Review process (interactive mode only) — mirrors the SKILL.md Stage 7 loop:**
1. Present the Markdown draft first — do not generate HTML
2. Prompt: "Review the draft above. Reply with specific changes, or reply **Approve** when ready to commit the HTML version."
3. Apply feedback, show only changed sections, repeat until Approve
4. On Approve: run validation checks, then fill `templates/partner-readiness-scorecard.html` via the HTML Output Method (`refs/html-output-method.md`) and deliver the file path
5. Append to final output: confidence score (0.0–1.0), named assumptions, and the list of attributes left blank with the owner who should close each before 03-Contract

---

> **Fast-follow (not wired in v1):** Slack evidence from `refs/slack-insights.md` can drive the **Executive Sponsor**, **Executive Alignment Sponsorship**, and **Partner's Technical Engagement** attributes — a named sponsor or active technical thread in a partner/deal channel is direct RAG evidence. Planned as a fast-follow; the scorecard does not consume Slack in v1.
