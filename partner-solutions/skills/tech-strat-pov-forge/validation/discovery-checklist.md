# Discovery Document Pre-Delivery Validation Checklist

Run every check before delivering the Discovery Document. If any check fails, repair before delivering.

## Part I — Dimensions (all 10 present, each with four blocks)
- [ ] Users, Personas & Journeys — four blocks present (incl. ➕ Discussion capture slot)
- [ ] Operational Process Flows — four blocks present (incl. ➕ Discussion capture slot)
- [ ] Pain & Friction Points — four blocks present (incl. ➕ Discussion capture slot)
- [ ] Success Metrics & Desired Outcomes — four blocks present (incl. ➕ Discussion capture slot)
- [ ] Technical Architecture & Readiness — four blocks present (incl. ➕ Discussion capture slot)
- [ ] Salesforce Ecosystem Footprint — four blocks present (incl. ➕ Discussion capture slot)
- [ ] Data Landscape & Sources — four blocks present (incl. ➕ Discussion capture slot)
- [ ] Business Alignment — four blocks present (incl. ➕ Discussion capture slot)
- [ ] Decision-Making & Stakeholders — four blocks present (incl. ➕ Discussion capture slot)
- [ ] Competitive Landscape & Alternatives — four blocks present (incl. ➕ Discussion capture slot)

## Content Rules
- [ ] Every *What we know* line carries a confidence label (`[confirmed]` / `[proposed — confirm]` / `[TBD]`)
- [ ] Every `[TBD]` item has a corresponding *What to ask* question
- [ ] Every *How Might We* line is a reframe ("How might we…"), not a solution statement
- [ ] No dimension is silently omitted — a thin dimension renders fully `[TBD]` with questions, never blank

## Part II — Canvases
- [ ] Value Proposition Canvas present with all six cells (Jobs, Pains, Gains, Products & Services, Pain Relievers, Gain Creators) — each filled or explicitly `[TBD]`
- [ ] Business Model Canvas present with all nine blocks — each filled or explicitly `[TBD]`
- [ ] No canvas block is invented — every non-`[TBD]` entry traces to a dimension finding

## Part III — Opportunity Backlog
- [ ] At least one How Might We statement, each with impact, evidence, and source dimension
- [ ] Backlog is ranked by impact × evidence (not an unordered dump)

## Part IV — POV Feed & Open Gaps
- [ ] Findings → POV section mapping present
- [ ] Open gaps listed with an owner (name or "TBD — owner: [name]") — never an empty owner
- [ ] Discovery confidence score (0.0–1.0) present in both the header and the Confidence & Assumptions section, with at least one named assumption

## Failure → Repair Instructions
**Invented canvas block:** remove it or replace with `[TBD]`. A canvas entry must trace to a dimension finding; if no finding supports it, it is a guess.
**Missing confidence label on a *What we know* line:** add `[confirmed]` / `[proposed — confirm]` / `[TBD]` based on the source. If unsure, it is `[proposed — confirm]`.
**Empty owner on an open gap:** assign the most likely owner from Decision-Making & Stakeholders, or write "TBD — owner: [role]". Never leave it blank.
**Solution disguised as an HMW:** rewrite as a question. "Build a scheduling bot" → "How might we cut scheduling time without adding headcount?"
**Backlog not ranked by impact × evidence:** score each HMW on impact and evidence, then order high-to-low. An alphabetical or as-captured order does not satisfy the check.
**Missing findings → POV mapping:** for each material finding, name the POV section it feeds (Problem Space / Vision / Solution / Use Cases / Personas / Target Markets / Commercial / Architecture). If a finding maps to no POV section, drop it or flag why it is retained.

## Auto-Capture Mode (when produced in a package)

- [ ] Header shows `Mode: Auto-capture` and a `Discussion capture:` status (pending on first generation)
- [ ] All 10 dimensions are pre-filled from research/POV with confidence labels — no question was asked
- [ ] Value Proposition Canvas and Business Model Canvas are pre-filled; cells without evidence show `[TBD]` (not blank)
- [ ] Every dimension ends with a **➕ Discussion capture** slot carrying the `Discussion capture: [pending]` sentinel
- [ ] HTML carries the standardized home-page back-link pill (`{{HOME_HREF}}` → `{SLUG}-index.html`); removed if standalone
- [ ] No `{{PLACEHOLDER}}` tokens remain in the rendered output

## Capture Readback (re-invocation)

- [ ] Filled (non-`[pending]`) capture slots are presented as a confirms/contradicts/adds diff to the POV
- [ ] `[pending]` slots are skipped; a doc with no filled slots yields a no-op
- [ ] On apply, the header flips to `captured {date}, applied to POV`
