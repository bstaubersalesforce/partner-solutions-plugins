# Stage 19 — Competitive Assessment

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 19 — Competitive Assessment (optional)**
Triggered when the user selects "Competitive Assessment" from the output menu, or asks for a competitive analysis, platform comparison, "Salesforce vs [AWS/Azure/OpenAI/Anthropic]", or objection-handling material.

Load `refs/competitive-landscape.md` (the curated platform-facts spine — note its "last reviewed" date).
Load `templates/competitive-assessment.md` and `templates/competitive-assessment.html`.
Load `validation/competitive-checklist.md`.

**What it is — and its boundaries.** A balanced, four-dimension comparison of Salesforce vs. three competitor categories, viewed through two layers — the **partner's** build-platform choice and the **customer's** solution choice. It makes the Salesforce case and handles objections in line, dimension by dimension. It is **independent** (may run without Stage 16). It must NOT:
- restate Red Team threats — Stage 9 attacks *the partner's solution*; this compares *platforms* (opposite direction);
- restate the partner's license pull-through economics — that is the POV's ISV Commercial Model section + `refs/pull-through-gtm.md`;
- produce Flex Credit dollar sizing — that is the `sf-flex-estimator` skill. Give qualitative commercial comparison only;
- restate the core-solution target architecture — that is Stage 16.

**Competitor categories (fixed, with POV-named specifics).** Always compare against all three for completeness, and inside each, name the specific competitors this partner actually faces (from Stage 1 research and the POV's competitive-differentiation section):
- **App / low-code platforms** (e.g. Microsoft Power Platform, ServiceNow, OutSystems)
- **Hyperscalers** (AWS, Azure, GCP)
- **AI providers** (OpenAI, Anthropic, Google Gemini/Vertex)

**Sourcing.** Use `refs/competitive-landscape.md` for durable platform-level facts; top up fast-moving specifics (AI-model capabilities, recent program/pricing changes) with live research. Confidence-label every claim (`[confirmed from research]` / `[proposed — confirm]` / `[TBD — clarification needed]`). On research failure, apply the SKILL.md degradation rule (log one status line, mark the claim `[TBD]`, proceed).

**Procedure — for each of the four dimensions (Commercial Model, Ecosystem, GTM Program, Technology):**
1. Build the scorecard: Salesforce + the three categories, each with a qualitative rating and a one-line rationale.
2. Write the two-layer read: "for the partner building on it" and "for the customer buying the result."
3. Write one in-line Objection → Response — the response must **concede the valid part before countering**.
4. Name at least one area where a competitor is genuinely stronger in this dimension (the **mandatory concession** — validation fails without it).

Then write the **Synthesis**: the 3–4 strongest Salesforce arguments, the 2–3 objections most likely to land, and one honest line on where Salesforce is genuinely not the right choice.

**Fairness gate (required).** Before delivering, confirm each dimension contains a genuine competitor-strength concession and each objection concedes-then-counters. If any dimension reads one-sided, rebalance it — a competitive piece that never concedes reads as a pitch and loses credibility.

Fill both templates via the HTML Output Method (`refs/html-output-method.md`); fill every `{{TOKEN}}`; do not invent comparisons the POV/research/landscape ref does not support. Run every check in `validation/competitive-checklist.md` before delivering.

**Home-page back-link.** Set `{{HOME_HREF}}` to `{SLUG}-index.html` when part of a package; remove the back-link `<a>` line when standalone.

**Filename (Stage 13 convention):** `{SLUG}-competitive-assessment.md` + `{SLUG}-competitive-assessment.html`.

Deliver the file path(s); surface the Synthesis before appending the full assessment. When run non-interactively (package dispatch), produce both `.md` and `.html` in one pass — do not pause for approval.
