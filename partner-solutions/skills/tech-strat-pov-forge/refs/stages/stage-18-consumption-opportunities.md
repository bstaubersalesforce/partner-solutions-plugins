# Stage 18 — Consumption Opportunities

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 18 — Consumption Opportunities (optional)**
Triggered when the user selects "Consumption Opportunities" from the output menu, or asks for a consumption map, agent/data opportunity map, or where-to-grow-consumption analysis.

Load `templates/consumption-opportunities.md` and `templates/consumption-opportunities.html`.
Load `validation/consumption-checklist.md`.
Load `refs/consumption-estimation.md` (directional rate card + estimation model).

**What it is — and its boundaries.** A build-oriented map of where to grow consumption on the partner's solution via Agentforce agents, Data Cloud, and other Salesforce SKUs, with named-component build blueprints to start each. It is **consumption-growth-scoped and independent** (may run without Stage 16). It must NOT:
- restate the core-solution architecture — that is the Technical & Architectural Assessment (Stage 16);
- restate the license pull-through commercial model — that is the POV's ISV Commercial Model section + `refs/pull-through-gtm.md`;
- produce Flex Credit **dollar** sizing — that is the `sf-flex-estimator` skill. This stage may give a **directional, credits-only** pre-estimate (below) to seed the calculator, but never dollars/PUPM/contract pricing; point to sf-flex-estimator for authoritative cost modeling.

Map the POV (and matched vertical) to the artifact:
1. Use cases + Solution + Architecture Summary → candidate Agentforce agent opportunities (2–4): name, purpose/trigger, topics & actions, objects read/written, supporting Flow/Apex/prompt components, 3–5 build steps. Confidence-label each.
2. Data Model + integrations + external data → Data Cloud opportunities (2–4): DMOs/data streams/source objects, mapping & identity resolution, activation target, 3–5 build steps. Confidence-label each.
3. Solution + compliance/scale needs → Other Salesforce SKU opportunities (Shield, Backup & Archive, sandboxes, other partner-resellable products): trigger, value, resellable-by-partner (Y/N/TBD).
4. Rank all opportunities into the Consumption Opportunity Map table with a qualitative consumption signal and the directional credits/yr estimate (from the pre-estimate below) for each Agent/Data row.

**Directional consumption pre-estimate (credits only).** Using `refs/consumption-estimation.md`, add a directional estimate to **each Agentforce and Data Cloud opportunity**. This seeds the official calculator — it is not authoritative pricing.

1. **Sizing-Band Anchor.** Pick the single customer-size band (S/M/L/XL) that fits the POV's target customer. Write one anchor note (fills `{{SIZING_BAND_NOTE}}` in the templates) that: (a) names the band and why (e.g. "Typical targets fall into the M band; estimates below assume M"); (b) names the **scaling driver** — the `#Entities` unit (branches, hubs, sites, seats); (c) tells the reader to scale `#Entities` (and optionally U/F) for other bands. Bands are abstract — no reference entity-count ranges; the `#Entities` figure comes from the target customer or a stated assumption. In the Markdown template fill the structured Sizing-Band Anchor fields (band line, scaling-driver line, prose note); in the HTML template `{{SIZING_BAND_NOTE}}` takes the same content condensed to 2–3 sentences of prose.
2. **Per Agentforce opportunity** — state the assumptions `U`, `F`, `A`, prompt count + tier, and `#Entities`; compute `U × F × A × #Entities` → monthly actions → ×12 annual → annual action credits (×20) + annual prompt credits (×2/4/16); express the result as a directional **credit band** (low–high). Note the sandbox 0.8 factor only if relevant.
3. **Per Data Cloud opportunity** — state the assumptions: data volume (millions of rows), run frequency (runs/year), and usage-type; compute `volume × frequency × multiplier` → directional annual **credit band**.
4. Keep every figure **directional and credits-only** (no dollars). Show the assumptions so the reader can edit them in the real calculator. Do not output dollars.

Fill both templates via the HTML Output Method (`refs/html-output-method.md`); fill every `{{TOKEN}}`; do not invent opportunities the POV/vertical does not support. Run every check in `validation/consumption-checklist.md` before delivering.

**Home-page back-link.** Set `{{HOME_HREF}}` to `{SLUG}-index.html` when part of a package; remove the back-link `<a>` line when standalone.

**Filename (Stage 13 convention):** `{SLUG}-consumption-opportunities.md` + `{SLUG}-consumption-opportunities.html`.

Deliver the file path(s). When run non-interactively (package dispatch), produce both `.md` and `.html` in one pass — do not pause for approval.
