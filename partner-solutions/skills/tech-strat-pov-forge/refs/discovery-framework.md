# Discovery Framework (Stage 15)

Lazily loaded by the tech-strat-pov-forge skill. Follow the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`. Produces the Discovery Document via `templates/discovery-document.md` and `templates/discovery-document.html`; validate against `validation/discovery-checklist.md` before delivering.

## Overview
The Discovery Framework is a hybrid discovery instrument: it researches and pre-fills structured discovery dimensions, reframes gaps as *How Might We* statements, renders a Value Proposition Canvas and a Business Model Canvas, and emits a Discovery Document that feeds the POV.

## Mode Resolution (resolve first, never ask)

Discovery runs in one of two modes, chosen by **how it was invoked** — never by prompting the user:

- **Auto-capture mode** — invoked via the package/parallel-dispatch run, or any brief containing an "auto-capture" / "non-interactive" directive. Pre-fill all 10 dimensions and both canvases from research + the approved POV using the confidence labels (`[confirmed]` / `[proposed — confirm]` / `[TBD]`). Ask **no** questions. Emit each dimension's **➕ Discussion capture** slot as the sentinel `Discussion capture: [pending]`. Set the header to `Mode: Auto-capture · Discussion capture: pending`. Do **not** run the POV handshake now — it is deferred to a later re-invocation.
- **Workshop mode** — invoked via the explicit "Discovery Framework" menu pick, the phrases "run discovery / discovery workshop / refine the POV with discovery", or the Full Discovery intake fork. Ask the 10-dimension questions, fill the capture slots from the answers, set the header to `Mode: Workshop · Discussion capture: captured YYYY-MM-DD`, and run the confirms/contradicts/adds POV handshake immediately.

Default in any non-interactive or dispatched context: **auto-capture**. Never block a package run waiting for answers.

## Process

1. **Research sweep.** Reuse the Stage 1 research engine (URL fetch + targeted searches), extended with discovery queries: org structure, named systems/tooling, public process signals, named competitors, customer reviews. Lazy-load the matched `refs/verticals/` file for industry process flows, KPIs, and regulatory drivers. Output one plain-English status line per action (see Execution Principles).
2. **Pre-fill dimensions.** Populate every dimension's *What we know* block from research; tag each line `[confirmed]` / `[proposed — confirm]` / `[TBD]`.
3. **HMW synthesis.** For each dimension, convert friction/gaps into 1–3 *How Might We* statements (reframes, not solutions).
4. **Build canvases.** Assemble the Value Proposition Canvas from Theme A and the Business Model Canvas from Theme C (cross-referencing B). Any block lacking evidence is `[TBD]` — never invented.
5. **Gap questions.** Fill each dimension's *What to ask* with only the still-missing questions. Cross-reference `scripts/discovery-questions.md` to reuse wording.
6. **Rank the Opportunity Backlog.** Consolidate all HMW statements; rank by impact × evidence.
7. **POV handshake (Part IV).**
   - **Full Discovery path (from Stage 1 fork):** feed pre-fills straight into Stage 2 — the POV starts populated, with fewer Stage 3 questions.
   - **Anytime path, POV exists:** present findings as a diff (confirms / contradicts / adds) and offer to apply.
   - **Anytime path, no POV:** deliver the Discovery Document standalone; offer to start a POV from it.

**No refusal conditions.** Unlike the POV, discovery is legitimately the pre-discovery step — proceed even with thin inputs. Failed fetches/searches are noted inline and skipped.

**Delivery follows the Stage 7 Interactive Review process:**
1. Present the Markdown draft first — do not generate HTML.
2. Prompt: "Review the draft above. Reply with specific changes, or reply **Approve** when ready to commit the HTML version."
3. Apply feedback, show only changed sections, repeat until Approve.
4. On Approve: run `validation/discovery-checklist.md`, then fill `templates/discovery-document.html` via the HTML Output Method (`refs/html-output-method.md`) and deliver the file path.
5. Append: discovery confidence score (0.0–1.0), named assumptions, explicit open-gap list with owners.

## Capture Readback (re-invocation)

When discovery is re-invoked **explicitly** (menu pick / "run discovery again" / "apply discovery captures") and a `{SLUG}-discovery-document.md` already exists in the output directory with at least one filled (non-`[pending]`) capture slot, do not regenerate blindly — read the captures back into the POV:

1. Read the existing `{SLUG}-discovery-document.md`. For each dimension, parse the text under its `Discussion capture:` marker.
2. Skip any slot still reading `[pending]` (nothing captured).
3. For slots with real content, run the standard POV handshake: present the captured insights as a **confirms / contradicts / adds** diff against the current POV; offer to apply.
4. On apply: update the POV's affected sections, then set the discovery doc header to `Mode: <mode> · Discussion capture: captured YYYY-MM-DD, applied to POV`.
5. **Idempotent:** if no slot has new content, report "nothing new to apply" and make no changes.

**Marker dependency:** readback finds notes by the `Discussion capture:` marker line. Tell users to type **under** the marker, not delete it — a removed marker means that dimension's notes are not auto-detected.

**The `.md` is the source of truth** for capture; the `.html` is the shareable view. Readback always parses the `.md`.

## Dimensions

Ten dimensions across three themes. For **each** dimension, produce four blocks:
- **What we know** — research-filled, each line tagged `[confirmed]` / `[proposed — confirm]` / `[TBD]`.
- **How Might We…** — 1–3 reframes turning this dimension's friction/gaps into opportunity statements. Reframes, never solutions ("How might we…", not "Build a…").
- **What to ask** — targeted discovery-call questions for the remaining gaps. Reuse wording from `scripts/discovery-questions.md` where a matching question already exists; do not duplicate it verbatim into this file.
- **➕ Discussion capture** — in auto-capture mode, emit the sentinel `Discussion capture: [pending]` for insights added live or async during the POV discussion; in workshop mode, fill it from the discussion. Keep the `Discussion capture:` marker so a later run can read it back (see Capture Readback).

A dimension with zero research evidence still renders — fully `[TBD]` in *What we know*, with a populated *What to ask* block and a `Discussion capture: [pending]` slot. Always renders, never invents.

### Theme A — Customer & Value (feeds the Value Proposition Canvas)

**1. Users, Personas & Journeys** — who the customer's users are (roles, volumes), their end-to-end journeys, and the moments that matter. Prompts: primary/secondary user roles; the journey from trigger to outcome; where handoffs and waiting occur.

**2. Operational Process Flows** — the key operational processes the solution touches, step by step, with systems and owners per step. Prompts: the 2–3 highest-value process flows; manual vs. automated steps; cycle time and volume.

**3. Pain & Friction Points** — concrete pains in those journeys/processes, severity, and current workarounds. Prompts: where work breaks or slows; cost of each pain (time, error, $, risk); what they do instead today.

**4. Success Metrics & Desired Outcomes** — current baseline metrics and target outcomes ("what good looks like"). Prompts: what they measure today and the current number; the target and by when; how success is judged internally.

### Theme B — Technical Readiness (feeds the future Architectural Assessment)

**5. Technical Architecture & Readiness** — current and planned architecture, scale headroom, and known debt. Prompts: current stack and integration style; what breaks first at 10× load; planned changes in the next 12 months.

**6. Salesforce Ecosystem Footprint** — Salesforce products/licenses/clouds the partner and their customers already run, and ecosystem maturity. Prompts: editions and clouds owned; AppExchange/ISV tooling in use; Agentforce/Data Cloud/Einstein adoption.

**7. Data Landscape & Sources** — systems of record, data quality, and the integration surface. Prompts: where the authoritative data lives; data quality and ownership; sync/latency requirements and PII/regulated data.

### Theme C — Business & Commercial (feeds the Business Model Canvas)

**8. Business Alignment** — strategic priorities, sponsoring initiatives, budget context, and org-change readiness. Prompts: the business goal this ladders to; the funding/initiative behind it; appetite and capacity for change.

**9. Decision-Making & Stakeholders** — who decides, the budget owner, the champion, and the buying process. Prompts: economic buyer vs. champion vs. user; procurement/approval steps; what could stall the decision.

**10. Competitive Landscape & Alternatives** — what customers use today and why, named alternatives, switching costs/lock-in, and "why us over [named alternative]." Draws from the `scripts/discovery-questions.md` *Risks & Competitive Threats* block. Surfaces the raw landscape only — adversarial analysis stays in the Red Team artifact (Stage 9). Prompts: incumbent tools and satisfaction; switching cost/lock-in; the one capability no alternative offers.

## Canvas Construction

**Value Proposition Canvas** (from Theme A):
- *Customer Jobs* ← Users/Journeys + Operational Process Flows (the jobs users are trying to get done).
- *Pains* ← Pain & Friction Points.
- *Gains* ← Success Metrics & Desired Outcomes.
- *Products & Services / Pain Relievers / Gain Creators* ← the partner's solution capabilities mapped against the above. Mark `[TBD]` where the solution side is unknown.

**Business Model Canvas** (from Theme C, cross-referencing A/B) — the 9 blocks:
Customer Segments, Value Propositions, Channels, Customer Relationships, Revenue Streams, Key Resources, Key Activities, Key Partnerships, Cost Structure. Fill each from evidence; `[TBD]` where none exists. Customer Segments/Relationships/Channels draw from Decision-Making & Stakeholders and Users; Revenue Streams/Cost Structure from Business Alignment; Key Partnerships/Resources from Salesforce Ecosystem Footprint and Technical Architecture.

Never invent a canvas block. An evidence-free block renders as `[TBD]`. Industry-pattern priors are **not** evidence: when a canvas block's source dimensions are entirely `[TBD]`, the block is `[TBD]` too. If an illustrative industry pattern genuinely helps the discovery call, you may include it labelled `[proposed — confirm]` with a one-line note of its source — but never present it as a partner-specific fact.
