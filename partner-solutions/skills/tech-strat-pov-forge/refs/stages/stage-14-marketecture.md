# Stage 14 — Marketecture

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 14 — Marketecture (optional)**
Triggered when the user requests a marketecture, architecture diagram, or a visual/shareable architecture overview — and the POV's **Architecture Summary** is populated. (Also generated when "All outputs + home page" is selected and architecture is populated.) Like the other downstream output stages, it is an independent artifact generator; when a home page is also being built, produce the marketecture **before** Stage 13 so the index can link it.

**Gate — do not generate from an empty Architecture Summary.** If the POV's Architecture Summary is missing or empty, do not produce a diagram and do not invent components. Report that the marketecture was skipped because the POV has no architecture to map, and stop. (This is the same gate the orchestrator applies in `refs/parallel-dispatch.md`; restated here so a fanned-out subagent that reads only this file still enforces it.)

Load `templates/marketecture.html`.
Load `validation/marketecture-checklist.md`.

Map the POV **Architecture Summary** to the diagram layers:
1. Application Type (Native / Composite / Hybrid) → app-type framing
2. User Interface (LWC / Canvas / custom) → UI layer
3. Data Model (standard objects, custom objects, sync strategy) → data layer
4. Integrations (API frameworks, endpoints) → integration layer
5. SF Cloud/SKU Dependencies (Platform, Sales, Service, Industry Cloud, Add-On SKUs) → Salesforce platform layer — name specific clouds/SKUs, never "Salesforce platform"
6. External Dependencies (integrated systems, competing initiatives) → external systems layer

Fill `templates/marketecture.html` via the HTML Output Method (`refs/html-output-method.md`) — do not regenerate the HTML inline. Fill every `{{PLACEHOLDER}}` token from the POV Architecture Summary; do not invent components the POV does not state. Run every check in `validation/marketecture-checklist.md` before delivering.

Deliver the HTML file path to the user.
