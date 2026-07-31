# Discovery Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional, hybrid Discovery Framework (Stage 15) to the pov-builder skill that researches and pre-fills 10 discovery dimensions across 3 themes, reframes gaps as *How Might We* statements, renders a Value Proposition Canvas + Business Model Canvas, and emits a Discovery Document that feeds the POV.

**Architecture:** Follows the skill's existing lazy-load + template + validation pattern. The full Stage 15 instructions live in a new lazily-loaded `refs/discovery-framework.md`. A pointer in `refs/output-stages.md` registers Stage 15 and names the new template/checklist files (so the validator's reference/orphan checks pass). `SKILL.md` gains a Stage 1 intake fork (Quick POV vs. Full Discovery) and a Discovery entry in the output menu. Two new templates (`discovery-document.md`, `discovery-document.html`) and one checklist (`discovery-checklist.md`) follow existing naming and the `{{TOKEN}}` fill pipeline. `tests/validate_skill.py` gains parity checks.

**Tech Stack:** Markdown skill content, HTML templates (Salesforce design-system CSS), Python 3 stdlib structural validator, git pre-commit hook (`.githooks/pre-commit`) + GitHub Actions CI.

---

## Critical Constraint: Every Commit Must Pass the Validator

The repo's pre-commit hook runs `python3 tests/validate_skill.py` and **blocks any commit that fails**. Three existing checks are tightly coupled:

- `t_refs_exist` — every `templates|refs|validation|scripts/...` path named in `SKILL.md` or `refs/output-stages.md` must exist.
- `t_no_orphans` — every file in `templates/`, `validation/`, `scripts/`, and top-level `refs/` must be named somewhere in `SKILL.md` or `refs/output-stages.md`.
- `t_stage_contiguous` — `**Stage N` headings in those two files must be exactly `1..14` (becomes `1..15`).

**Consequence:** a new file and the instruction text that references it must land in the **same commit**, and the contiguity range must be bumped in the same commit Stage 15 first appears. "Watch the test fail" (RED) is done by **running the validator locally before committing** — never by committing a red state. Run `python3 tests/validate_skill.py` from `~/.claude/skills/pov-builder` (the script resolves the skill root from its own path).

Before starting, activate the hook in this clone: `git config core.hooksPath .githooks`.

---

## Canonical Constants (used across multiple tasks)

**The 10 dimension titles (exact strings, used by the parity check and all three text files):**

1. `Users, Personas & Journeys`
2. `Operational Process Flows`
3. `Pain & Friction Points`
4. `Success Metrics & Desired Outcomes`
5. `Technical Architecture & Readiness`
6. `Salesforce Ecosystem Footprint`
7. `Data Landscape & Sources`
8. `Business Alignment`
9. `Decision-Making & Stakeholders`
10. `Competitive Landscape & Alternatives`

**Themes:** A = dimensions 1–4 (feeds Value Proposition Canvas); B = 5–7 (feeds future Architectural Assessment); C = 8–10 (feeds Business Model Canvas).

**Three-block shape inside every dimension:** `What we know` / `How Might We…` / `What to ask`.

**Confidence labels (reuse existing convention):** `[confirmed]` / `[proposed — confirm]` / `[TBD]`.

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `refs/discovery-framework.md` | Create | Full Stage 15 instructions: process logic, 10 dimensions, HMW method, canvas construction rules |
| `templates/discovery-document.md` | Create | Markdown output template (Header + Parts I–IV; text-form VPC + BMC) |
| `templates/discovery-document.html` | Create | HTML render with VPC two-panel grid + BMC 9-block grid |
| `validation/discovery-checklist.md` | Create | Pre-delivery contract for the Discovery Document |
| `refs/output-stages.md` | Modify | Register Stage 15 pointer; name the new template/checklist files |
| `SKILL.md` | Modify | Stage 1 intake fork; Discovery menu entry; reorder "All outputs + home page" first |
| `scripts/discovery-questions.md` | Modify | Bidirectional cross-reference note (no content duplication) |
| `tests/validate_skill.py` | Modify | Bump contiguity to 1..15; add dimension-parity, canvas-token, menu-parity checks; add HTML to `TEMPLATE_HTML` |

---

## Task 1: Register Stage 15 + create wired skeletons (green foundation)

**Files:**
- Modify: `tests/validate_skill.py:208-211` (stage contiguity)
- Modify: `refs/output-stages.md` (add Stage 15 pointer)
- Create: `refs/discovery-framework.md`
- Create: `templates/discovery-document.md`
- Create: `templates/discovery-document.html`
- Create: `validation/discovery-checklist.md`

- [ ] **Step 1: Bump the contiguity range and watch it fail (RED)**

In `tests/validate_skill.py`, update the check name and assertion (lines ~208–211):

```python
@check("Stages are contiguous 1..15 across the instructions (no gaps or duplicates)")
def t_stage_contiguous():
    nums = sorted(int(n) for n in re.findall(r"^\*\*Stage (\d+)", instructions(), re.M))
    assert nums == list(range(1, 16)), f"stage sequence is {nums}"
```

Run: `python3 tests/validate_skill.py`
Expected: FAIL on "Stages are contiguous 1..15" with `stage sequence is [1, 2, ..., 14]` (Stage 15 doesn't exist yet). This proves the check is live.

- [ ] **Step 2: Add the Stage 15 pointer to `refs/output-stages.md`**

Append this block to the end of `refs/output-stages.md` (after Stage 14). It names the new files so `t_refs_exist`/`t_no_orphans` will be satisfied once the files exist, and supplies the `**Stage 15` heading the contiguity check needs:

```markdown

**Stage 15 — Discovery Framework (optional)**
Triggered when the user selects "Discovery Framework" from the output menu, asks to run discovery / a discovery workshop / refine the POV with discovery, or chooses the Full Discovery path at intake (Stage 1).

Load `refs/discovery-framework.md` and follow it end to end — it carries the full discovery process, the 10 dimensions, the *How Might We* method, and the Value Proposition Canvas + Business Model Canvas construction rules.
It produces `templates/discovery-document.md` (Markdown output) and, on Approve, `templates/discovery-document.html` (HTML output with both canvases).
Run every check in `validation/discovery-checklist.md` before delivering.

Unlike Stages 8–14, Discovery is an **upstream refinement** pass, not a downstream artifact built from a finished POV. It is therefore **not** included in "All outputs + home page"; it is offered as its own menu entry and can run with no POV present.
```

Run: `python3 tests/validate_skill.py`
Expected: now FAIL on "Every file path referenced in the instructions exists" listing `refs/discovery-framework.md`, `templates/discovery-document.md`, `templates/discovery-document.html`, `validation/discovery-checklist.md` (RED — files not created yet).

- [ ] **Step 3: Create the four skeleton files**

`refs/discovery-framework.md` (minimal skeleton — fleshed out in Tasks 2–3):

```markdown
# Discovery Framework (Stage 15)

Lazily loaded by the pov-builder skill. Follow the Execution Principles and HTML Output Method defined in `SKILL.md`. Produces the Discovery Document via `templates/discovery-document.md` and `templates/discovery-document.html`; validate against `validation/discovery-checklist.md` before delivering.

## Overview
The Discovery Framework is a hybrid discovery instrument: it researches and pre-fills structured discovery dimensions, reframes gaps as *How Might We* statements, renders a Value Proposition Canvas and a Business Model Canvas, and emits a Discovery Document that feeds the POV.

## Process
(Defined in Task 3.)

## Dimensions
(Defined in Task 2.)

## Canvas Construction
(Defined in Task 3.)
```

`templates/discovery-document.md` (skeleton):

```markdown
# [Partner Name] — Discovery Document

(Structure defined in Tasks 2–3.)
```

`templates/discovery-document.html` (skeleton — must have balanced braces; not yet in TEMPLATE_HTML so token checks don't apply yet):

```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{{PARTNER_NAME}} — Discovery</title></head>
<body><!-- structure defined in Task 3 --></body></html>
```

`validation/discovery-checklist.md` (skeleton):

```markdown
# Discovery Document Pre-Delivery Validation Checklist

Run every check before delivering the Discovery Document. If any check fails, repair before delivering.

(Contract defined in Tasks 2 and 5.)
```

Run: `python3 tests/validate_skill.py`
Expected: PASS — all checks green (files now exist and are referenced; Stage 15 present; contiguity 1..15).

- [ ] **Step 4: Commit**

```bash
git add tests/validate_skill.py refs/output-stages.md refs/discovery-framework.md \
        templates/discovery-document.md templates/discovery-document.html \
        validation/discovery-checklist.md
git commit -m "Register Discovery Framework as Stage 15 with wired skeletons"
```

Expected: hook runs the validator, prints `18/18 passed`, commit succeeds.
Note: the suite count stays **18** here (Step 1 renamed an existing check, added none). New checks arrive in later tasks (→ 19 in Task 2, 20 in Task 3, 21 in Task 4).

---

## Task 2: Discovery dimensions content + dimension-parity check

**Files:**
- Modify: `tests/validate_skill.py` (add `DISCOVERY_DIMENSIONS` + parity check)
- Modify: `refs/discovery-framework.md` (replace `## Dimensions` section)
- Modify: `templates/discovery-document.md` (add Part I)
- Modify: `validation/discovery-checklist.md` (add dimension-presence checks)

- [ ] **Step 1: Add the parity check and watch it fail (RED)**

In `tests/validate_skill.py`, after the `VERTICAL_HEADINGS` block (~line 84) add:

```python
DISCOVERY_DIMENSIONS = [
    "Users, Personas & Journeys",
    "Operational Process Flows",
    "Pain & Friction Points",
    "Success Metrics & Desired Outcomes",
    "Technical Architecture & Readiness",
    "Salesforce Ecosystem Footprint",
    "Data Landscape & Sources",
    "Business Alignment",
    "Decision-Making & Stakeholders",
    "Competitive Landscape & Alternatives",
]
DISCOVERY_FILES = [
    "refs/discovery-framework.md",
    "templates/discovery-document.md",
    "validation/discovery-checklist.md",
]
```

Then add a new check (place it after `t_vertical_schema`, ~line 105):

```python
@check("Discovery framework, template, and checklist list the same 10 dimensions")
def t_discovery_dimension_parity():
    bad = {}
    for rel in DISCOVERY_FILES:
        s = read(rel)
        missing = [d for d in DISCOVERY_DIMENSIONS if d not in s]
        if missing:
            bad[rel] = missing
    assert not bad, f"files missing discovery dimensions: {bad}"
```

Run: `python3 tests/validate_skill.py`
Expected: FAIL on "Discovery framework, template, and checklist list the same 10 dimensions" — skeleton files don't contain the dimension titles yet (RED). Suite count is now 19.

- [ ] **Step 2: Write the dimensions into `refs/discovery-framework.md`**

Replace the `## Dimensions` placeholder section with the full content. Each dimension uses the three-block shape. (Themes are grouping headers; the parity check only requires the 10 titles to appear.)

```markdown
## Dimensions

Ten dimensions across three themes. For **each** dimension, produce three blocks:
- **What we know** — research-filled, each line tagged `[confirmed]` / `[proposed — confirm]` / `[TBD]`.
- **How Might We…** — 1–3 reframes turning this dimension's friction/gaps into opportunity statements. Reframes, never solutions ("How might we…", not "Build a…").
- **What to ask** — targeted discovery-call questions for the remaining gaps. Reuse wording from `scripts/discovery-questions.md` where a matching question already exists; do not duplicate it verbatim into this file.

A dimension with zero research evidence still renders — fully `[TBD]` in *What we know*, with a populated *What to ask* block. Always renders, never invents.

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
```

- [ ] **Step 3: Write Part I into `templates/discovery-document.md`**

Replace the skeleton body with the full template (Header + Part I; Parts II–IV added in Task 3):

```markdown
# [Partner Name] — Discovery Document
**Date:** [YYYY-MM-DD] · **Prepared by:** [name, role]
**Discovery Confidence:** [0.0–1.0] · **Associated POV:** [link or "none — standalone"]

---

## Part I — Discovery Dimensions

> Each dimension has three blocks: **What we know** (with confidence labels), **How Might We…**, and **What to ask**. A dimension with no evidence still renders — fully `[TBD]` — with its questions populated.

### Theme A — Customer & Value

#### Users, Personas & Journeys
**What we know:**
- [finding] `[confirmed | proposed — confirm | TBD]`

**How Might We…**
- How might we [reframe of a gap/friction as opportunity]?

**What to ask:**
- [targeted gap question]

#### Operational Process Flows
**What we know:**
- [finding] `[label]`

**How Might We…**
- How might we [reframe]?

**What to ask:**
- [question]

#### Pain & Friction Points
**What we know:**
- [finding] `[label]`

**How Might We…**
- How might we [reframe]?

**What to ask:**
- [question]

#### Success Metrics & Desired Outcomes
**What we know:**
- [finding] `[label]`

**How Might We…**
- How might we [reframe]?

**What to ask:**
- [question]

### Theme B — Technical Readiness

#### Technical Architecture & Readiness
**What we know:**
- [finding] `[label]`

**How Might We…**
- How might we [reframe]?

**What to ask:**
- [question]

#### Salesforce Ecosystem Footprint
**What we know:**
- [finding] `[label]`

**How Might We…**
- How might we [reframe]?

**What to ask:**
- [question]

#### Data Landscape & Sources
**What we know:**
- [finding] `[label]`

**How Might We…**
- How might we [reframe]?

**What to ask:**
- [question]

### Theme C — Business & Commercial

#### Business Alignment
**What we know:**
- [finding] `[label]`

**How Might We…**
- How might we [reframe]?

**What to ask:**
- [question]

#### Decision-Making & Stakeholders
**What we know:**
- [finding] `[label]`

**How Might We…**
- How might we [reframe]?

**What to ask:**
- [question]

#### Competitive Landscape & Alternatives
**What we know:**
- [finding] `[label]`

**How Might We…**
- How might we [reframe]?

**What to ask:**
- [question]

---

<!-- Part II (Canvases), Part III (Opportunity Backlog), Part IV (POV Feed & Gaps) added in Task 3 -->
```

- [ ] **Step 4: Add dimension checks to `validation/discovery-checklist.md`**

Replace the skeleton body with:

```markdown
# Discovery Document Pre-Delivery Validation Checklist

Run every check before delivering the Discovery Document. If any check fails, repair before delivering.

## Part I — Dimensions (all 10 present, each with three blocks)
- [ ] Users, Personas & Journeys — What we know / How Might We / What to ask all present
- [ ] Operational Process Flows — three blocks present
- [ ] Pain & Friction Points — three blocks present
- [ ] Success Metrics & Desired Outcomes — three blocks present
- [ ] Technical Architecture & Readiness — three blocks present
- [ ] Salesforce Ecosystem Footprint — three blocks present
- [ ] Data Landscape & Sources — three blocks present
- [ ] Business Alignment — three blocks present
- [ ] Decision-Making & Stakeholders — three blocks present
- [ ] Competitive Landscape & Alternatives — three blocks present

## Content Rules
- [ ] Every *What we know* line carries a confidence label (`[confirmed]` / `[proposed — confirm]` / `[TBD]`)
- [ ] Every `[TBD]` item has a corresponding *What to ask* question
- [ ] Every *How Might We* line is a reframe ("How might we…"), not a solution statement
- [ ] No dimension is silently omitted — a thin dimension renders fully `[TBD]` with questions, never blank

<!-- Part II–IV checks added in Task 5 -->
```

- [ ] **Step 5: Run the validator (GREEN)**

Run: `python3 tests/validate_skill.py`
Expected: PASS — "Discovery framework, template, and checklist list the same 10 dimensions" now green; `19/19 passed`.

- [ ] **Step 6: Commit**

```bash
git add tests/validate_skill.py refs/discovery-framework.md \
        templates/discovery-document.md validation/discovery-checklist.md
git commit -m "Add the 10 discovery dimensions and dimension-parity check"
```

---

## Task 3: Process logic + canvases (MD + HTML) + canvas-token check

**Files:**
- Modify: `tests/validate_skill.py` (add `discovery-document.html` to `TEMPLATE_HTML`; add canvas-token check)
- Modify: `refs/discovery-framework.md` (`## Process` and `## Canvas Construction`)
- Modify: `templates/discovery-document.md` (append Parts II–IV)
- Modify: `templates/discovery-document.html` (full render)

- [ ] **Step 1: Write the process logic in `refs/discovery-framework.md`**

Replace the `## Process` placeholder:

```markdown
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
4. On Approve: run `validation/discovery-checklist.md`, then fill `templates/discovery-document.html` via the HTML Output Method and deliver the file path.
5. Append: discovery confidence score (0.0–1.0), named assumptions, explicit open-gap list with owners.
```

Replace the `## Canvas Construction` placeholder:

```markdown
## Canvas Construction

**Value Proposition Canvas** (from Theme A):
- *Customer Jobs* ← Users/Journeys + Operational Process Flows (the jobs users are trying to get done).
- *Pains* ← Pain & Friction Points.
- *Gains* ← Success Metrics & Desired Outcomes.
- *Products & Services / Pain Relievers / Gain Creators* ← the partner's solution capabilities mapped against the above. Mark `[TBD]` where the solution side is unknown.

**Business Model Canvas** (from Theme C, cross-referencing A/B) — the 9 blocks:
Customer Segments, Value Propositions, Channels, Customer Relationships, Revenue Streams, Key Resources, Key Activities, Key Partnerships, Cost Structure. Fill each from evidence; `[TBD]` where none exists. Customer Segments/Relationships/Channels draw from Decision-Making & Stakeholders and Users; Revenue Streams/Cost Structure from Business Alignment; Key Partnerships/Resources from Salesforce Ecosystem Footprint and Technical Architecture.

Never invent a canvas block. An evidence-free block renders as `[TBD]`.
```

- [ ] **Step 2: Append Parts II–IV to `templates/discovery-document.md`**

Replace the trailing comment with:

```markdown
## Part II — Synthesis Canvases

### Value Proposition Canvas
| Customer Profile | → | Value Map |
|---|---|---|
| **Jobs:** [list or TBD] | | **Products & Services:** [list or TBD] |
| **Pains:** [list or TBD] | | **Pain Relievers:** [list or TBD] |
| **Gains:** [list or TBD] | | **Gain Creators:** [list or TBD] |

### Business Model Canvas
| Key Partnerships | Key Activities | Value Propositions | Customer Relationships | Customer Segments |
|---|---|---|---|---|
| [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| | **Key Resources** | | **Channels** | |
| | [TBD] | | [TBD] | |

| Cost Structure | Revenue Streams |
|---|---|
| [TBD] | [TBD] |

---

## Part III — Opportunity Backlog
Consolidated *How Might We* statements, ranked by impact × evidence.

1. [HMW statement] — impact: [H/M/L] · evidence: [H/M/L] · source dimension: [name]
2. [HMW statement] — …

---

## Part IV — POV Feed & Open Gaps

**Findings → POV sections:**
| Discovery finding | POV section it feeds |
|---|---|
| [finding] | [Problem Space / Vision / Solution / Use Cases / Personas / Target Markets / Commercial / Architecture] |

**Open gaps (carry into the engagement):**
| Gap | Owner | Target date |
|---|---|---|
| [gap] | [name] | [date or TBD] |

---

## Confidence & Assumptions
**Discovery Confidence:** [0.0–1.0]
**Assumptions this rests on:**
1. [assumption]
**Open gaps:** [list, or "All dimensions evidenced"]
```

- [ ] **Step 3: Build `templates/discovery-document.html`**

Replace the skeleton with a full render. Reuse the Salesforce design-system CSS pattern from `templates/marketecture.html` (copy the `body`, `.page`, `.header`, `.header .meta`, `.section`, `.section-title` rules verbatim — same palette `#032d60` / `#0070d2` / `#f4f6f9`), then add the canvas-grid CSS and markup below. All dynamic values are `{{UPPER_SNAKE_CASE}}` tokens (required by `t_token_convention`). Keep `{{` and `}}` balanced (required by `t_braces_balanced`).

Required header tokens: `{{PARTNER_NAME}}`, `{{GENERATED_DATE}}`, `{{PREPARED_BY}}`, `{{DISCOVERY_CONFIDENCE}}`.

Canvas-grid CSS to add:

```html
<style>
  /* Value Proposition Canvas — two panels */
  .vpc { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .vpc-panel { border: 1px solid #d8dde6; border-radius: 8px; padding: 16px; }
  .vpc-panel h4 { font-size: 0.8rem; color: #0070d2; margin-bottom: 8px; }
  .vpc-cell { margin-bottom: 12px; }
  .vpc-cell .label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; color: #54698d; }

  /* Business Model Canvas — 9 blocks */
  .bmc { display: grid; grid-template-columns: repeat(5, 1fr); grid-auto-rows: minmax(80px, auto); gap: 8px; }
  .bmc-block { border: 1px solid #d8dde6; border-radius: 6px; padding: 10px; background: #fff; }
  .bmc-block .label { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; color: #54698d; margin-bottom: 6px; }
  .bmc-kp { grid-row: span 2; }   /* Key Partnerships spans two rows */
  .bmc-cs { grid-row: span 2; }   /* Customer Segments spans two rows */
  .bmc-cost { grid-column: span 2; }   /* Cost Structure (bottom row, left) */
  .bmc-rev  { grid-column: span 3; }   /* Revenue Streams (bottom row, right) */
</style>
```

Canvas markup (inside `<div class="page">`, each in its own `.section`). The VPC and BMC cell tokens:

```html
<div class="section">
  <div class="section-title">Value Proposition Canvas</div>
  <div class="vpc">
    <div class="vpc-panel"><h4>Customer Profile</h4>
      <div class="vpc-cell"><div class="label">Jobs</div>{{VPC_JOBS}}</div>
      <div class="vpc-cell"><div class="label">Pains</div>{{VPC_PAINS}}</div>
      <div class="vpc-cell"><div class="label">Gains</div>{{VPC_GAINS}}</div>
    </div>
    <div class="vpc-panel"><h4>Value Map</h4>
      <div class="vpc-cell"><div class="label">Products &amp; Services</div>{{VPC_PRODUCTS}}</div>
      <div class="vpc-cell"><div class="label">Pain Relievers</div>{{VPC_RELIEVERS}}</div>
      <div class="vpc-cell"><div class="label">Gain Creators</div>{{VPC_CREATORS}}</div>
    </div>
  </div>
</div>

<div class="section">
  <div class="section-title">Business Model Canvas</div>
  <div class="bmc">
    <div class="bmc-block bmc-kp"><div class="label">Key Partnerships</div>{{BMC_PARTNERSHIPS}}</div>
    <div class="bmc-block"><div class="label">Key Activities</div>{{BMC_ACTIVITIES}}</div>
    <div class="bmc-block bmc-cs" style="grid-column:3"><div class="label">Value Propositions</div>{{BMC_VALUE_PROPS}}</div>
    <div class="bmc-block"><div class="label">Customer Relationships</div>{{BMC_RELATIONSHIPS}}</div>
    <div class="bmc-block bmc-cs"><div class="label">Customer Segments</div>{{BMC_SEGMENTS}}</div>
    <div class="bmc-block"><div class="label">Key Resources</div>{{BMC_RESOURCES}}</div>
    <div class="bmc-block"><div class="label">Channels</div>{{BMC_CHANNELS}}</div>
    <div class="bmc-block bmc-cost"><div class="label">Cost Structure</div>{{BMC_COSTS}}</div>
    <div class="bmc-block bmc-rev"><div class="label">Revenue Streams</div>{{BMC_REVENUE}}</div>
  </div>
</div>
```

Also render Part I dimensions, Part III backlog, and Part IV tables as `.section` blocks using tokens (e.g. `{{DIMENSIONS_HTML}}`, `{{BACKLOG_HTML}}`, `{{POV_FEED_HTML}}`, `{{OPEN_GAPS_HTML}}`) — these are rebuilt by the fill script (variable-length, per the HTML Output Method). End the file with a trailing HTML comment documenting every token (mirrors the convention other templates use).

- [ ] **Step 4: Add canvas-token check + register the HTML template (RED first)**

In `tests/validate_skill.py`, add `"templates/discovery-document.html",` to the `TEMPLATE_HTML` list (~line 37–42). Then add a check after `t_token_convention` (~line 123):

```python
@check("Discovery HTML carries the VPC and BMC canvas token families")
def t_discovery_canvas_tokens():
    s = read("templates/discovery-document.html")
    vpc = [f"VPC_{x}" for x in ("JOBS","PAINS","GAINS","PRODUCTS","RELIEVERS","CREATORS")]
    bmc = [f"BMC_{x}" for x in ("PARTNERSHIPS","ACTIVITIES","VALUE_PROPS","RELATIONSHIPS",
                                "SEGMENTS","RESOURCES","CHANNELS","COSTS","REVENUE")]
    missing = [t for t in vpc + bmc if f"{{{{{t}}}}}" not in s]
    assert not missing, f"discovery HTML missing canvas tokens: {missing}"
```

Run: `python3 tests/validate_skill.py`
Expected (run **before** writing Step 3's HTML if working strictly TDD, otherwise it passes): if the HTML lacks any token it FAILs listing them (RED); once Step 3's markup is in place it PASSes. Also confirm the brace/convention checks now include the discovery HTML and pass.

- [ ] **Step 5: Run the full validator (GREEN)**

Run: `python3 tests/validate_skill.py`
Expected: `20/20 passed` (Task 2 added 1 → 19; this task adds 1 → 20).

- [ ] **Step 6: Commit**

```bash
git add tests/validate_skill.py refs/discovery-framework.md \
        templates/discovery-document.md templates/discovery-document.html
git commit -m "Add discovery process logic, VPC/BMC canvases, and canvas-token check"
```

---

## Task 4: SKILL.md intake fork + output menu + menu-parity check

**Files:**
- Modify: `tests/validate_skill.py` (add menu-parity check)
- Modify: `SKILL.md` (Stage 1 intake fork; output menu — add Discovery entry, reorder "All outputs + home page" first)

- [ ] **Step 1: Add the intake fork to `SKILL.md` Stage 1**

At the top of **Stage 1 — Intake** (after asking for the two inputs, before the research actions), insert:

```markdown
**Intake fork — Quick POV vs. Full Discovery.**
After capturing the two inputs, offer one choice:
- **Quick POV (default)** — proceed with the lean flow below (research → pre-fill → ≤5 questions).
- **Full Discovery** — run the Discovery Framework first (load `refs/discovery-framework.md`, Stage 15), then feed its pre-fills into Stage 2 so the POV starts populated.

If the user only provides name + URL with no preference, default to Quick POV. Do not block on this choice — state the default and proceed.
```

- [ ] **Step 2: Add Discovery to the output menu and reorder "All outputs" first**

In the post-delivery `AskUserQuestion` block, edit the second question (`header: "Package"`). Move the `"All outputs + home page"` option to the **first** position in the `options` array, and add a `"Discovery Framework"` option. The reordered Package `options` array:

```
options: [
  {
    label: "All outputs + home page",
    description: "Generate every downstream artifact (Stages 8–12, 14) plus an HTML home page that links them all (Stage 13). This is the usual choice. Supersedes the individual Analysis/Package picks below — but does NOT include Discovery (Stage 15), which is an upstream refinement, not a downstream artifact."
  },
  {
    label: "Investor Presentation",
    description: "10-slide HTML pitch deck covering problem, solution, market, traction, business model, team, and Salesforce partnership (Stage 10)"
  },
  {
    label: "Solution Infographic",
    description: "Single-page visual overview: problem stats, solution flow, proven outcomes, and market context (Stage 11)"
  },
  {
    label: "Marketecture",
    description: "HTML architecture diagram from the POV Architecture Summary — only when architecture is populated (Stage 14)"
  }
]
```

Add a `"Discovery Framework"` option to the **first** question (`header: "Analysis"`) so it sits with the analysis/refinement choices (that question currently has 3 options; this makes 4, the tool max):

```
{
  label: "Discovery Framework",
  description: "Run structured discovery (10 dimensions, How Might We, Value Proposition + Business Model canvases) and produce a Discovery Document that refines the POV (Stage 15)"
}
```

Update the prose under the menu so the routing still reads correctly: note that selecting "All outputs + home page" runs Stages 8–12 + 14 then 13, and that "Discovery Framework" runs Stage 15 separately (it is not part of "All outputs").

- [ ] **Step 3: Add the menu-parity check (RED first)**

In `tests/validate_skill.py`, add after `t_menu_all_option` (~line 223):

```python
@check("Output menu offers the Discovery Framework and cites Stage 15")
def t_menu_discovery_option():
    skill = read("SKILL.md")
    assert "Discovery Framework" in skill, "menu missing 'Discovery Framework' option"
    assert "(Stage 15)" in skill, "menu does not cite (Stage 15)"
```

Run **before** Step 2's edits to observe RED: FAIL on "Output menu offers the Discovery Framework and cites Stage 15". After Step 2, it passes.

Note: `t_menu_stage_refs` requires every `(Stage N)` cited to map to a real `**Stage N` heading — Stage 15 exists in `output-stages.md` (Task 1), so `(Stage 15)` is valid. `t_menu_all_option` still passes (the "All outputs + home page" string remains present).

- [ ] **Step 4: Run the validator (GREEN)**

Run: `python3 tests/validate_skill.py`
Expected: `21/21 passed`.

- [ ] **Step 5: Commit**

```bash
git add tests/validate_skill.py SKILL.md
git commit -m "Add Stage 1 intake fork and Discovery output-menu entry; reorder package menu"
```

---

## Task 5: Cross-reference discovery-questions.md + finalize checklist

**Files:**
- Modify: `scripts/discovery-questions.md` (cross-reference note)
- Modify: `validation/discovery-checklist.md` (Part II–IV checks)

- [ ] **Step 1: Add a cross-reference note to `scripts/discovery-questions.md`**

Insert after the file's intro line (line 3):

```markdown
> **Two discovery axes.** This file is organized by **POV output section** and is used reactively (Stage 3) to fill gaps in a specific POV section. The **Discovery Framework** (`refs/discovery-framework.md`, Stage 15) is organized by **discovery dimension** and is used proactively. When running Stage 15, reuse the question wording here rather than duplicating it; when filling a POV gap, this file is the source.
```

- [ ] **Step 2: Finalize `validation/discovery-checklist.md`**

Replace the trailing `<!-- Part II–IV checks added in Task 5 -->` comment with:

```markdown
## Part II — Canvases
- [ ] Value Proposition Canvas present with all six cells (Jobs, Pains, Gains, Products & Services, Pain Relievers, Gain Creators) — each filled or explicitly `[TBD]`
- [ ] Business Model Canvas present with all nine blocks — each filled or explicitly `[TBD]`
- [ ] No canvas block is invented — every non-`[TBD]` entry traces to a dimension finding

## Part III — Opportunity Backlog
- [ ] At least one How Might We statement, each with impact, evidence, and source dimension
- [ ] Backlog is ranked (not an unordered dump)

## Part IV — POV Feed & Open Gaps
- [ ] Findings → POV section mapping present
- [ ] Open gaps listed with an owner (name or "TBD — owner: [name]") — never an empty owner
- [ ] Discovery confidence score (0.0–1.0) stated with at least one named assumption

## Failure → Repair Instructions
**Invented canvas block:** remove it or replace with `[TBD]`. A canvas entry must trace to a dimension finding; if no finding supports it, it is a guess.
**Missing confidence label on a *What we know* line:** add `[confirmed]` / `[proposed — confirm]` / `[TBD]` based on the source. If unsure, it is `[proposed — confirm]`.
**Empty owner on an open gap:** assign the most likely owner from Decision-Making & Stakeholders, or write "TBD — owner: [role]". Never leave it blank.
**Solution disguised as an HMW:** rewrite as a question. "Build a scheduling bot" → "How might we cut scheduling time without adding headcount?"
```

- [ ] **Step 3: Run the validator (GREEN)**

Run: `python3 tests/validate_skill.py`
Expected: `21/21 passed` (no new checks; content still satisfies dimension-parity since the 10 titles remain present in the checklist).

- [ ] **Step 4: Commit**

```bash
git add scripts/discovery-questions.md validation/discovery-checklist.md
git commit -m "Cross-reference discovery axes; finalize discovery checklist contract"
```

---

## Task 6: Behavioral testing with subagents (writing-skills discipline)

The structural validator proves files are wired correctly; it cannot prove an agent *uses* the framework correctly. Per superpowers:writing-skills, run pressure scenarios with fresh subagents.

**Files:** none committed unless a scenario reveals a fix. If a fix is needed, return to the relevant task's files, repeat its RED→GREEN→commit micro-cycle.

- [ ] **Step 1: Intake-fork default scenario**

Dispatch a subagent with only: *"Use the pov-builder skill. Partner: Acme Health. URL: https://example.com."* Provide the skill content.
Expected: agent states the Quick-POV default and proceeds without blocking. PASS if it does not silently run full discovery or stall waiting for the fork choice.

- [ ] **Step 2: Full-discovery path scenario**

Dispatch a subagent: *"Run the pov-builder skill in Full Discovery mode for partner Acme Health (https://example.com)."*
Expected: loads `refs/discovery-framework.md`; produces all 10 dimensions each with three blocks; renders both canvases; never invents a canvas block (thin-research blocks are `[TBD]`); ends with Part IV POV feed. PASS if all hold.

- [ ] **Step 3: Thin-research / always-renders scenario**

Dispatch a subagent with a partner whose URL yields almost nothing.
Expected: every dimension still renders (fully `[TBD]` *What we know* + populated *What to ask*); no refusal. PASS if the document is a usable call agenda despite no data.

- [ ] **Step 4: HMW-is-a-reframe scenario**

Inspect the generated *How Might We* lines from Steps 2–3.
Expected: each is a question/reframe, not a solution. If any are solutions, tighten the instruction in `refs/discovery-framework.md` (Dimensions intro + Canvas rules) and the checklist repair note, then re-run.

- [ ] **Step 5: POV-handshake-diff scenario**

Dispatch a subagent with an existing draft POV present, then run Discovery anytime.
Expected: findings presented as a confirms/contradicts/adds diff and offered to apply — not a silent overwrite. PASS if it diffs.

- [ ] **Step 6: Record results**

Document pass/fail and any fixes in the commit message of the final fix (if any), or note "behavioral scenarios passed, no fixes needed" in a short commit amending nothing (skip if clean). Update the memory file `pov-builder-skill.md` index entry to note Stage 15 / Discovery Framework exists and the validator is now 21 checks.

---

## Self-Review (completed during planning)

**Spec coverage:**
- Document structure (4 parts, 10 dims/3 themes, three-block shape) → Tasks 2–3 ✓
- Intake fork + anytime invocation → Task 4 ✓
- Stage 15 registration → Task 1 ✓
- VPC + BMC, never-invent rule → Task 3 + checklist Task 5 ✓
- HMW reframes → Tasks 2–3, behavioral Task 6 ✓
- Three POV-handshake variants → Task 3 (process) + Task 6 (test) ✓
- "All outputs" excludes Discovery; reorder first → Task 4 ✓
- Coexist with discovery-questions.md → Task 5 ✓
- Validation checklist + validator parity (dimension, token, menu) → Tasks 2,3,4 ✓
- Behavioral subagent testing → Task 6 ✓
- Open decision (Stage 15 location): resolved — full text in `refs/discovery-framework.md`, pointer in `output-stages.md` (the pointer also names the template/checklist files so the orphan/reference checks pass). ✓

**Placeholder scan:** Bracketed tokens like `[finding]`, `[label]`, `[name]` are intentional **template** placeholders (the skill's own convention — see existing `templates/pov-output.md`), not plan gaps. All validator code, the dimension list, the output-stages pointer, the checklist, and the MD template are given in full. The HTML reuses an explicitly-cited existing CSS block plus full new canvas markup.

**Type/name consistency:** `DISCOVERY_DIMENSIONS` / `DISCOVERY_FILES` defined once (Task 2) and reused. Canvas token names in the HTML (Task 3 Step 3) exactly match the check (Task 3 Step 4): `VPC_{JOBS,PAINS,GAINS,PRODUCTS,RELIEVERS,CREATORS}`, `BMC_{PARTNERSHIPS,ACTIVITIES,VALUE_PROPS,RELATIONSHIPS,SEGMENTS,RESOURCES,CHANNELS,COSTS,REVENUE}`. Final validator count: 18 → 19 (Task 2) → 20 (Task 3) → 21 (Task 4).
