# Stage 17 — POV Presentation

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 17 — POV Presentation (optional)**
Triggered when the user requests a POV presentation, POV deck, slide version of the POV, stakeholder deck, or "present the POV."

**What it is — and how it differs from the Investor Presentation (Stage 10).** This is the *approved POV rendered as a stakeholder slide deck* — the same content and conclusions, formatted for a live readout to the partner's or Salesforce's review team. It is a **faithful render, not a rewrite**: it presents the POV's problem, vision, solution, use cases, markets, alignment, roadmap, commercial model, and recommendation. The Investor Presentation (Stage 10) is a *fundraising pitch* — traction-and-ask framed, with team/market/business-model beats aimed at investors. When the user wants "the POV as slides," that is Stage 17; when they want "a pitch deck," that is Stage 10.

Load `templates/pov-presentation.html`.
Load `validation/pov-presentation-checklist.md`.

Map the approved POV to slides in this order:
1. Cover → Partner name + solution tagline (one line from the Vision/Solution) + Org62 stage + app-type badge + vertical/Industry Cloud
2. Problem Space → Problem Statement + 3 Challenges + Significance stat + market CAGR (sourced) + one headline risk
3. Vision → the POV **Vision Statement verbatim** (single full-bleed quote slide)
4. Strategic Direction → POV **Product Strategy**: Strategic Thesis (headline) + Horizon Sequencing to Moat + Platform Bet
5. Product Pillars & Positioning → POV **Product Strategy**: the **top 3** Product Pillars with their bets + Market Positioning (the slide has 3 pillar slots; if the POV lists 4 pillars, present the top 3)
6. Solution → Solution Statement + top 3 Benefits with their metrics
7. Use Cases → one card per POV use case (persona + outcome). Fewer than 3 use cases → delete the unused card `<div>`; never leave `{{UC_*}}` tokens
8. Target Markets & Personas → Primary / Secondary / Adjacent markets + the 3 personas
9. Solution Alignment → Blueprint gap + Sales Play + stakeholder needs (Product/Advisory/Sales)
10. MVP & Roadmap → MVP scope + Horizon 1/2/3 + Architectural runway (preserve each horizon distinctly)
11. Commercial Model & Architecture → App type, licensing, pull-through SKUs + architecture (app type, integrations, named SF clouds/SKUs as pills). Fewer than 3 SF deps → delete the unused pill `<span>`
12. Recommendation → recommendation headline + 3 next steps + confidence score + named proof points + open TBDs

Fill `templates/pov-presentation.html` via the HTML Output Method (`refs/html-output-method.md`) — do not regenerate the HTML inline and do not produce a Markdown intermediate. Fill every `{{PLACEHOLDER}}` from the approved POV; use "TBD" with owner attribution where the POV has a gap. **Render only what the POV states — do not invent content, inflate a target into an achieved result, or fabricate a proof point.** Run every check in `validation/pov-presentation-checklist.md` before delivering.

**Home-page back-link.** Set `{{HOME_HREF}}` to `{SLUG}-index.html` when this deck is part of a package. When generated standalone (no home page), remove the `home-link` anchor line on the cover slide entirely (see the comment in the template).

**Filename (Stage 13 convention):** write to `{SLUG}-pov-presentation.html`.

Deliver the HTML file path. Output a one-line summary of each slide after generation.
