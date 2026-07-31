# Technical & Architectural Assessment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Technical & Architectural Assessment (Stage 16) to the pov-builder skill — a build-guiding artifact that assesses current-state architecture against Salesforce Well-Architected, prescribes the target-state Salesforce architecture, and emits a build-ready metadata blueprint + skeleton stubs, chaining into the MVP Build Plan (Stage 8).

**Architecture:** Follows the skill's established Stage-15 pattern exactly. Full Stage 16 definition lives in a new lazily-loaded `refs/architecture-assessment.md`; a pointer in `refs/output-stages.md` registers Stage 16 and names the new template/checklist files (so the validator's reference/orphan checks pass). `SKILL.md` restructures the post-POV output menu from two `AskUserQuestion` questions into three (to fit the new option within the 4-options-per-question cap) and adds run-before-Stage-8 sequencing. Two new templates (`technical-architecture-assessment.{md,html}`) and one checklist follow the `{{TOKEN}}` fill pipeline. `tests/validate_skill.py` gains Well-Architected parity, RAG-token, and menu checks.

**Tech Stack:** Markdown skill content, HTML templates (Salesforce design-system CSS), Python 3 stdlib structural validator, git pre-commit hook (`.githooks/pre-commit`) + GitHub Actions CI.

---

## Critical Constraint: Every Commit Must Pass the Validator

The repo's pre-commit hook runs `python3 tests/validate_skill.py` and **blocks any commit that fails**. The same coupled checks as the Stage-15 work apply: `t_refs_exist`, `t_no_orphans`, and `t_stage_contiguous`. A new file and the instruction text referencing it must land in the **same commit**, and the contiguity range must bump in the commit Stage 16 first appears. "Watch the test fail" (RED) is done by **running the validator locally before committing** — never by committing a red state. Run `python3 tests/validate_skill.py` from `~/.claude/skills/pov-builder` (exit 0 = pass). The suite starts at **21 checks** on this branch.

Activate the hook in this clone if needed: `git config core.hooksPath .githooks`.

---

## Canonical Constants (used across tasks)

**Salesforce Well-Architected — 3 pillars → 8 qualities (exact strings):**
- Pillars: `Trusted`, `Easy`, `Adaptable`
- Qualities: `Secure`, `Compliant`, `Reliable` (Trusted) · `Intentional`, `Automated`, `Engaging` (Easy) · `Resilient`, `Composable` (Adaptable)

**The seven target-architecture layers (Part 2):** App type & packaging · Data architecture · Integration architecture · Component architecture · Security & sharing model · Scale & multi-tenancy · AI & data layer.

**Document parts:** Part 0 Executive Readiness Summary · Part 1 Current-State Assessment · Part 2 Target-State Architecture · Part 3 Build-Ready Spec & Stubs · Part 4 Gap-Closing Roadmap → MVP Build Plan handoff.

**Confidence labels (reuse existing convention):** `[confirmed]` / `[proposed — confirm]` / `[TBD]`.

**HTML RAG token keys (uppercase quality):** `SECURE`, `COMPLIANT`, `RELIABLE`, `INTENTIONAL`, `AUTOMATED`, `ENGAGING`, `RESILIENT`, `COMPOSABLE`. Each quality has tokens `{{WA_<KEY>_RAG}}` (status class) and `{{WA_<KEY>_NOTE}}` (one-line finding).

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `refs/architecture-assessment.md` | Create | Full Stage 16 definition: process, Well-Architected method, 7 target layers, stub construction + traceability rules |
| `templates/technical-architecture-assessment.md` | Create | Markdown output (Header + Parts 0–4 + Confidence); source of truth for Part 3 stubs |
| `templates/technical-architecture-assessment.html` | Create | HTML render: RAG grid, layer cards, roadmap, read-only `<pre>` stubs |
| `validation/architecture-checklist.md` | Create | Pre-delivery contract |
| `refs/output-stages.md` | Modify | Register Stage 16 pointer; title → "8–16" |
| `SKILL.md` | Modify | 3-question menu restructure; Stage 16 in pointer/index; run-before-Stage-8 sequencing |
| `tests/validate_skill.py` | Modify | Contiguity 1..16; WA-quality parity; RAG-token; menu-architecture checks; register HTML |

---

## Task 1: Register Stage 16 + create wired skeletons (green foundation)

**Files:**
- Modify: `tests/validate_skill.py` (stage contiguity)
- Modify: `refs/output-stages.md` (Stage 16 pointer + title)
- Create: `refs/architecture-assessment.md`, `templates/technical-architecture-assessment.md`, `templates/technical-architecture-assessment.html`, `validation/architecture-checklist.md`

- [ ] **Step 1: Bump contiguity and watch it fail (RED).** In `tests/validate_skill.py`, update `t_stage_contiguous`:

```python
@check("Stages are contiguous 1..16 across the instructions (no gaps or duplicates)")
def t_stage_contiguous():
    nums = sorted(int(n) for n in re.findall(r"^\*\*Stage (\d+)", instructions(), re.M))
    assert nums == list(range(1, 17)), f"stage sequence is {nums}"
```

Run `python3 tests/validate_skill.py` → FAIL ("stage sequence is [1..15]"). Don't commit yet.

- [ ] **Step 2: Update the output-stages title and append the Stage 16 pointer.** In `refs/output-stages.md`, change the H1 `# Optional Output Stages (8–15)` → `# Optional Output Stages (8–16)`. Then append at the end:

```markdown

**Stage 16 — Technical & Architectural Assessment (optional)**
Triggered when the user selects "Technical & Architectural Assessment" from the output menu, or asks for an architecture assessment / technical assessment / build-guiding architecture / Well-Architected review.

Load `refs/architecture-assessment.md` and follow it end to end — it carries the full process, the Salesforce Well-Architected evaluation method (3 pillars / 8 qualities), the seven target-architecture layers, and the build-ready spec + stub construction rules.
It produces `templates/technical-architecture-assessment.md` (Markdown output and the build-consumable source of truth) and, on Approve, `templates/technical-architecture-assessment.html` (shareable HTML view).
Run every check in `validation/architecture-checklist.md` before delivering.

Requires an approved POV. It is a downstream artifact (built from the POV) and **feeds the MVP Build Plan (Stage 8)**: when both the Assessment and the MVP Build Plan are generated in one session, run the Assessment **first**. Include it in "All outputs + home page".
```

Run validator → now FAIL on `t_refs_exist` (the 3 new files referenced here don't exist yet). RED.

- [ ] **Step 3: Create the four skeleton files** with exactly this content.

`refs/architecture-assessment.md`:
```markdown
# Technical & Architectural Assessment (Stage 16)

Lazily loaded by the pov-builder skill. Follow the Execution Principles and HTML Output Method defined in `SKILL.md`. Produces the assessment via `templates/technical-architecture-assessment.md` (the build-consumable source of truth) and `templates/technical-architecture-assessment.html`; validate against `validation/architecture-checklist.md` before delivering.

## Overview
A build-guiding artifact: it evaluates the partner's current-state architecture against Salesforce Well-Architected (3 pillars / 8 qualities), prescribes the target-state Salesforce architecture, and emits a build-ready metadata blueprint plus skeleton stubs. It requires an approved POV and feeds the MVP Build Plan (Stage 8).

## Process
(Defined in Task 3.)

## Well-Architected Assessment Method
(Defined in Task 2.)

## Target-State Architecture
(Defined in Task 3.)

## Build-Ready Spec & Stubs
(Defined in Task 4.)
```

`templates/technical-architecture-assessment.md`:
```markdown
# [Partner Name] — Technical & Architectural Assessment

(Structure defined in Tasks 2–4.)
```

`templates/technical-architecture-assessment.html`:
```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{{PARTNER_NAME}} — Architecture Assessment</title></head>
<body><!-- structure defined in Task 5 --></body></html>
```

`validation/architecture-checklist.md`:
```markdown
# Technical & Architectural Assessment Pre-Delivery Validation Checklist

Run every check before delivering the assessment. If any check fails, repair before delivering.

(Contract defined in Tasks 2–4.)
```

Run validator → PASS (all referenced files exist; Stage 16 present; contiguity 1..16). Suite count still **21** (Step 1 renamed an existing check).

- [ ] **Step 4: Commit.**
```bash
git add tests/validate_skill.py refs/output-stages.md refs/architecture-assessment.md \
        templates/technical-architecture-assessment.md templates/technical-architecture-assessment.html \
        validation/architecture-checklist.md
git commit -m "Register Technical & Architectural Assessment as Stage 16 with wired skeletons"
```
Expected: hook prints `21/21 passed`, commit succeeds. Do NOT add the HTML to `TEMPLATE_HTML` yet (Task 5). Do NOT flesh out skeletons (later tasks).

---

## Task 2: Well-Architected assessment (Part 1) + quality-parity check

**Files:**
- Modify: `tests/validate_skill.py` (add `WELL_ARCHITECTED` constants + parity check)
- Modify: `refs/architecture-assessment.md` (`## Well-Architected Assessment Method`)
- Modify: `templates/technical-architecture-assessment.md` (Header + Part 1)
- Modify: `validation/architecture-checklist.md` (Part 1 checks)

- [ ] **Step 1: Add the parity check and watch it fail (RED).** In `tests/validate_skill.py`, after the discovery constants block (the `# ---- 1c.` section), add:

```python
# ---- 1d. architecture assessment integrity ------------------------------
# The architecture-assessment ref, its template, and its checklist must all
# carry the Well-Architected pillars/qualities; t_well_architected_parity guards it.
WA_PILLARS = ["Trusted", "Easy", "Adaptable"]
WA_QUALITIES = ["Secure", "Compliant", "Reliable", "Intentional",
                "Automated", "Engaging", "Resilient", "Composable"]
ARCH_FILES = [
    "refs/architecture-assessment.md",
    "templates/technical-architecture-assessment.md",
    "validation/architecture-checklist.md",
]
```

Then add this check after `t_discovery_dimension_parity`:

```python
@check("Architecture ref, template, and checklist carry the Well-Architected pillars + 8 qualities")
def t_well_architected_parity():
    bad = {}
    for rel in ARCH_FILES:
        s = read(rel)
        missing = [w for w in WA_PILLARS + WA_QUALITIES if w not in s]
        if missing:
            bad[rel] = missing
    assert not bad, f"files missing Well-Architected terms: {bad}"
```

Run validator → FAIL on "Architecture ref, template, and checklist carry the Well-Architected pillars + 8 qualities" (skeletons lack the terms). RED. Suite is now 22.

- [ ] **Step 2: Write the assessment method into `refs/architecture-assessment.md`.** Replace the `## Well-Architected Assessment Method` placeholder with:

```markdown
## Well-Architected Assessment Method

Assess the partner's current-state architecture against the Salesforce **Well-Architected** framework, used as a decision compass. Three pillars, eight qualities:

- **Trusted** (protect stakeholders): **Secure** · **Compliant** · **Reliable**
- **Easy** (deliver value fast): **Intentional** · **Automated** · **Engaging**
- **Adaptable** (evolve with the business): **Resilient** · **Composable**

For **each** of the eight qualities, produce four elements:
- **Finding** — what the current architecture actually does for this quality.
- **Evidence** — sourced from the POV, Discovery (Theme B if present), or research; tag each line `[confirmed]` / `[proposed — confirm]` / `[TBD]`.
- **Pattern / Anti-pattern** — name the Well-Architected pattern the partner follows, or the anti-pattern they exhibit (compass language; be specific, not generic).
- **Gap** — what is missing to be Salesforce-grade for this quality.

A quality with no evidence still renders — **Finding** `[TBD]` with a "what to confirm" note. Never invent a finding or a rating.

**Quality reference (what each quality covers):**
- **Secure** — access control, data protection, org/credential security.
- **Compliant** — legal/ethical/regulatory obligations and data residency.
- **Reliable** — efficient, dependable operation; error handling; governor-limit headroom.
- **Intentional** — delivers business value now and over time; aligned to the POV use cases.
- **Automated** — gets work done faster and at scale; minimal manual intervention.
- **Engaging** — delights users and drives adoption; UX quality.
- **Resilient** — handles change well; loosely coupled; tolerant of platform/API change.
- **Composable** — adjusts quickly with stability; packageability, modularity, reuse.
```

- [ ] **Step 3: Write the Header + Part 1 into `templates/technical-architecture-assessment.md`.** Replace the entire file with:

```markdown
# [Partner Name] — Technical & Architectural Assessment
**Date:** [YYYY-MM-DD] · **Prepared by:** [name, role]
**Associated POV:** [link or "none"] · **Associated Discovery:** [link or "none"]
**Overall Well-Architected Readiness:** [0.0–1.0]

---

## Part 0 — Executive Readiness Summary

<!-- Part 0 content added in Task 3 -->

---

## Part 1 — Current-State Assessment

> Evaluated against Salesforce Well-Architected. Each quality has a Finding, Evidence (confidence-labeled), Pattern/Anti-pattern, and Gap. A quality with no evidence renders fully `[TBD]` with a "what to confirm" note — never invented.

### Trusted

#### Secure
**Finding:** [what the current architecture does] `[confirmed | proposed — confirm | TBD]`
**Pattern / Anti-pattern:** [named pattern or anti-pattern]
**Gap:** [what's missing for Salesforce-grade]

#### Compliant
**Finding:** [finding] `[label]`
**Pattern / Anti-pattern:** [named]
**Gap:** [gap]

#### Reliable
**Finding:** [finding] `[label]`
**Pattern / Anti-pattern:** [named]
**Gap:** [gap]

### Easy

#### Intentional
**Finding:** [finding] `[label]`
**Pattern / Anti-pattern:** [named]
**Gap:** [gap]

#### Automated
**Finding:** [finding] `[label]`
**Pattern / Anti-pattern:** [named]
**Gap:** [gap]

#### Engaging
**Finding:** [finding] `[label]`
**Pattern / Anti-pattern:** [named]
**Gap:** [gap]

### Adaptable

#### Resilient
**Finding:** [finding] `[label]`
**Pattern / Anti-pattern:** [named]
**Gap:** [gap]

#### Composable
**Finding:** [finding] `[label]`
**Pattern / Anti-pattern:** [named]
**Gap:** [gap]

---

<!-- Part 2 (Target-State Architecture), Part 4 (Roadmap) added in Task 3; Part 3 (Build-Ready Spec & Stubs) added in Task 4 -->
```

- [ ] **Step 4: Write Part 1 checks into `validation/architecture-checklist.md`.** Replace the entire file with:

```markdown
# Technical & Architectural Assessment Pre-Delivery Validation Checklist

Run every check before delivering the assessment. If any check fails, repair before delivering.

## Part 1 — Current-State Assessment (Well-Architected)
All eight qualities present, each with Finding / Pattern-Anti-pattern / Gap; grouped under their pillars (Trusted / Easy / Adaptable).
- [ ] Trusted — Secure assessed (Finding, Pattern/Anti-pattern, Gap)
- [ ] Trusted — Compliant assessed
- [ ] Trusted — Reliable assessed
- [ ] Easy — Intentional assessed
- [ ] Easy — Automated assessed
- [ ] Easy — Engaging assessed
- [ ] Adaptable — Resilient assessed
- [ ] Adaptable — Composable assessed

## Content Rules
- [ ] Every Finding carries a confidence label (`[confirmed]` / `[proposed — confirm]` / `[TBD]`)
- [ ] A quality with no evidence renders `[TBD]` with a "what to confirm" note — never invented
- [ ] Every Pattern/Anti-pattern is named specifically (not "good architecture" / "bad design")

<!-- Part 0 / 2 / 3 / 4 checks added in Tasks 3–4 -->
```

- [ ] **Step 5: Run validator (GREEN).** `python3 tests/validate_skill.py` → `22/22 passed`.
- [ ] **Step 6: Commit.**
```bash
git add tests/validate_skill.py refs/architecture-assessment.md \
        templates/technical-architecture-assessment.md validation/architecture-checklist.md
git commit -m "Add Well-Architected current-state assessment (Part 1) and parity check"
```

---

## Task 3: Process logic + Parts 0, 2, 4 (RAG, target architecture, roadmap)

**Files:**
- Modify: `refs/architecture-assessment.md` (`## Process`, `## Target-State Architecture`)
- Modify: `templates/technical-architecture-assessment.md` (Part 0, Part 2, Part 4, Confidence)
- Modify: `validation/architecture-checklist.md` (Part 0/2/4 checks)

No new validator check this task (content-only; the parity check from Task 2 still guards the qualities). Validator must stay `22/22`.

- [ ] **Step 1: Write the process logic in `refs/architecture-assessment.md`.** Replace the `## Process` placeholder with:

```markdown
## Process

1. **Load inputs.** Read the approved POV (always) — especially "Partner App Strategy & Technical Summary," "MVP & Development Priorities," and architecture-related sections. If a Discovery Document exists, load its Theme B (Technical Architecture & Readiness, Salesforce Ecosystem Footprint, Data Landscape & Sources). If the POV's technical sections are thin and no Discovery exists, pull from `scripts/discovery-questions.md` (Technical Assessment block) and flag `[TBD]`s.
2. **Targeted technical research.** Fill gaps the POV/Discovery did not cover — current stack, named integration systems, public API/security signals, scale indicators. Output one plain-English status line per action; note and skip failed fetches.
3. **Current-state assessment (Part 1).** Walk the eight Well-Architected qualities per the method above.
4. **Score the RAG (Part 0).** Derive each quality's 🟢/🟡/🔴 **from its Part 1 finding** (never guessed) — 🟢 Strong, 🟡 Emerging, 🔴 Gap. Roll up to the three pillars, surface the top 3 technical risks (quality + severity), and state the build-readiness verdict (go / conditional-go / not-ready).
5. **Design target state (Part 2).** Map POV use cases, solution, and KPIs onto the seven architecture layers. Name concrete Salesforce capabilities; `[TBD]` where the POV under-specifies.
6. **Build-ready spec & stubs (Part 3).** Per the Build-Ready Spec & Stubs rules.
7. **Roadmap + handoff (Part 4).** Sequence the gap-closing work, map each item to the quality it closes, and frame the explicit handoff to the MVP Build Plan (Stage 8).

**Requires an approved POV.** If none exists, tell the user to build the POV first (do not fabricate one). Otherwise proceed even under thin input, surfacing `[TBD]`s. No other refusal conditions.

**Delivery follows the Stage 7 Interactive Review process:**
1. Present the Markdown draft first — do not generate HTML.
2. Prompt: "Review the draft above. Reply with specific changes, or reply **Approve** when ready to commit the HTML version."
3. Apply feedback, show only changed sections, repeat until Approve.
4. On Approve: run `validation/architecture-checklist.md`, then fill `templates/technical-architecture-assessment.html` via the HTML Output Method and deliver the file path.
5. Append: overall Well-Architected readiness score (0.0–1.0), named assumptions, explicit `[TBD]` list.

**Core rule: every finding, RAG rating, target-state decision, and stub traces to evidence or is marked `[TBD]` — never invented.**
```

Then replace the `## Target-State Architecture` placeholder with:

```markdown
## Target-State Architecture

Prescribe the Salesforce target architecture across seven layers. Each layer: the recommendation, the POV use case(s)/quality it serves, and `[TBD]` where the POV under-specifies. Name concrete Salesforce capabilities — never "the Salesforce platform" generically.

1. **App type & packaging** — managed package vs. composite vs. hybrid; namespace strategy; 2GP considerations (serves Composable).
2. **Data architecture** — standard vs. custom objects; large-data-volume strategy; Data Cloud where relevant; data residency (serves Reliable, Compliant).
3. **Integration architecture** — named external systems; API style (REST/Platform Events/CDC/Bulk); auth (Named Credentials, OAuth); sync vs. async; middleware if any (serves Resilient).
4. **Component architecture** — division across LWC / Apex / Flow; where logic lives; why (serves Automated, Engaging).
5. **Security & sharing model** — permission sets, sharing model, field/object security, Shield/encryption if needed (serves Secure).
6. **Scale & multi-tenancy** — governor-limit strategy, bulkification, async patterns, horizontal scale for enterprise volume (serves Reliable, Resilient).
7. **AI & data layer** — Agentforce / Einstein / Data Cloud usage and the licenses they require, where applicable (serves Intentional).
```

- [ ] **Step 2: Write Part 0, Part 2, Part 4, and Confidence into `templates/technical-architecture-assessment.md`.** Replace the `<!-- Part 0 content added in Task 3 -->` line with:

```markdown
**Well-Architected Readiness (RAG):**

| Pillar | Quality | Rating | Finding |
|---|---|---|---|
| Trusted | Secure | [🟢/🟡/🔴] | [one line] |
| Trusted | Compliant | [🟢/🟡/🔴] | [one line] |
| Trusted | Reliable | [🟢/🟡/🔴] | [one line] |
| Easy | Intentional | [🟢/🟡/🔴] | [one line] |
| Easy | Automated | [🟢/🟡/🔴] | [one line] |
| Easy | Engaging | [🟢/🟡/🔴] | [one line] |
| Adaptable | Resilient | [🟢/🟡/🔴] | [one line] |
| Adaptable | Composable | [🟢/🟡/🔴] | [one line] |

**Pillar rollup:** Trusted [🟢/🟡/🔴] · Easy [🟢/🟡/🔴] · Adaptable [🟢/🟡/🔴]

**Top 3 technical risks:**
1. [risk] — quality: [name] · severity: [Critical/High/Medium/Low]
2. [risk] — quality: [name] · severity: [...]
3. [risk] — quality: [name] · severity: [...]

**Build-readiness verdict:** [Go / Conditional-Go / Not-ready] — [one-line justification]
```

Then replace the trailing `<!-- Part 2 ... Part 3 ... Task 4 -->` comment with:

```markdown
## Part 2 — Target-State Architecture

**1. App type & packaging:** [recommendation — or `[TBD]`] _(serves: Composable)_
**2. Data architecture:** [recommendation] _(serves: Reliable, Compliant)_
**3. Integration architecture:** [named systems, API style, auth, sync/async] _(serves: Resilient)_
**4. Component architecture:** [LWC / Apex / Flow division] _(serves: Automated, Engaging)_
**5. Security & sharing model:** [perm sets, sharing, protection] _(serves: Secure)_
**6. Scale & multi-tenancy:** [governor-limit + scale strategy] _(serves: Reliable, Resilient)_
**7. AI & data layer:** [Agentforce / Einstein / Data Cloud + licenses — or "Not applicable"] _(serves: Intentional)_

---

<!-- Part 3 (Build-Ready Spec & Stubs) added in Task 4 -->

---

## Part 4 — Gap-Closing Roadmap → MVP Build Plan handoff

| # | Gap-closing work item | Closes quality | Priority | Notes |
|---|---|---|---|---|
| 1 | [item] | [quality] | [H/M/L] | [note] |
| 2 | [item] | [quality] | [H/M/L] | [note] |

**Handoff to MVP Build Plan (Stage 8):** the build sequence above feeds Stage 8 — each target-state component and gap-closing item becomes a build task. Generate the MVP Build Plan next to turn this into sprint-ready user stories and a phase plan.

---

## Confidence & Assumptions
**Overall Well-Architected Readiness:** [0.0–1.0]
**Assumptions this rests on:**
1. [assumption]
**Open `[TBD]`s:** [list, or "All sections evidenced"]
```

- [ ] **Step 3: Add Part 0/2/4 checks to `validation/architecture-checklist.md`.** Replace the trailing `<!-- Part 0 / 2 / 3 / 4 checks added in Tasks 3–4 -->` comment with:

```markdown
## Part 0 — Executive Readiness Summary
- [ ] RAG table present with all 8 qualities rated, each with a one-line finding
- [ ] Pillar rollup present (Trusted / Easy / Adaptable)
- [ ] Every RAG rating traces to the matching Part 1 finding (no orphan scores)
- [ ] Top 3 technical risks present, each tied to a quality + severity
- [ ] Build-readiness verdict present (Go / Conditional-Go / Not-ready)

## Part 2 — Target-State Architecture
- [ ] All seven layers present (packaging, data, integration, component, security, scale, AI/data) — each a recommendation or explicit `[TBD]`
- [ ] Salesforce capabilities named specifically (not "the Salesforce platform")

## Part 4 — Roadmap & Handoff
- [ ] Gap-closing items listed, each mapped to the quality it closes, with priority
- [ ] Explicit handoff to the MVP Build Plan (Stage 8) present
- [ ] Overall Well-Architected readiness score (0.0–1.0) with at least one named assumption

<!-- Part 3 checks added in Task 4 -->
```

- [ ] **Step 4: Run validator (GREEN).** `python3 tests/validate_skill.py` → `22/22 passed` (qualities still present in all 3 files).
- [ ] **Step 5: Commit.**
```bash
git add refs/architecture-assessment.md templates/technical-architecture-assessment.md \
        validation/architecture-checklist.md
git commit -m "Add assessment process, RAG summary, target architecture, and roadmap (Parts 0/2/4)"
```

---

## Task 4: Build-Ready Spec & Stubs (Part 3) + guardrails

**Files:**
- Modify: `refs/architecture-assessment.md` (`## Build-Ready Spec & Stubs`)
- Modify: `templates/technical-architecture-assessment.md` (insert Part 3)
- Modify: `validation/architecture-checklist.md` (Part 3 checks)

Content-only; validator stays `22/22`.

- [ ] **Step 1: Write the stub rules in `refs/architecture-assessment.md`.** Replace the `## Build-Ready Spec & Stubs` placeholder with:

```markdown
## Build-Ready Spec & Stubs

The Markdown output is the build-consumable source of truth. From the Part 2 target state, produce:

- **Metadata blueprint** — a table of custom objects → fields (API name, type, description) → relationships, plus a short ERD-style block. Standard objects reused are named, not redefined.
- **Component inventory** — each LWC / Apex class / Flow with a one-line responsibility and the use case/quality it serves.
- **Integration contracts** — per external system: named API, auth method, sync/async, the Salesforce-side mechanism (e.g., Named Credential + External Service, Platform Event), and the data exchanged.
- **Skeleton stubs** — fenced code blocks: Apex class + method signatures with doc-comment intent (no bodies; bodies are `// TODO (build): …`), LWC component shells (`@api` props + skeleton template), and declarative object/field definitions. Every stub carries the header `// STUB — scaffolding from Architecture Assessment; flesh out in build`.

**Guardrails (so stubs stay scaffolding, not invented product):**
- **Traceability** — every object/field/class/Flow traces to a named POV use case or a Part 2 decision (a Traceability note/column). If it can't be traced, do not emit it.
- **Scaffolding only** — signatures and shells, never fabricated business-logic bodies or invented algorithms.
- **Under-specification** — emit `[TBD — confirm in build]` rather than guessing.
```

- [ ] **Step 2: Insert Part 3 into `templates/technical-architecture-assessment.md`.** Replace the `<!-- Part 3 (Build-Ready Spec & Stubs) added in Task 4 -->` line with:

````markdown
## Part 3 — Build-Ready Spec & Stubs

> Markdown is the build-consumable source of truth. Every artifact below traces to a POV use case or a Part 2 decision (Traceability column). Stubs are signatures/scaffolding only — no business-logic bodies.

**Metadata blueprint — custom objects & fields:**

| Object (API name) | Field (API name) | Type | Description | Traceability |
|---|---|---|---|---|
| [Object__c] | [Field__c] | [Text/Lookup/…] | [purpose] | [use case / Part 2 decision] |

**Relationships / ERD:**
```
[Object_A__c] 1──* [Object_B__c]   (master-detail / lookup)
```

**Component inventory:**

| Component | Type | Responsibility | Serves (use case / quality) |
|---|---|---|---|
| [Name] | [LWC / Apex / Flow] | [one line] | [traceability] |

**Integration contracts:**

| External system | API | Auth | Sync/Async | SF-side mechanism | Data exchanged |
|---|---|---|---|---|---|
| [System] | [named API] | [Named Credential / OAuth] | [sync/async] | [Platform Event / External Service / …] | [data] |

**Skeleton stubs:**

```apex
// STUB — scaffolding from Architecture Assessment; flesh out in build
public with sharing class [ClassName] {
    // Serves: [use case / quality]
    public [ReturnType] [methodName]([Type] [param]) {
        // TODO (build): [intent in one line]
    }
}
```

```javascript
// STUB — scaffolding from Architecture Assessment; flesh out in build
// LWC: [componentName] — serves [use case]
import { LightningElement, api } from 'lwc';
export default class [ComponentName] extends LightningElement {
    @api [propName]; // [purpose]
    // TODO (build): [intent]
}
```

---
````

- [ ] **Step 3: Add Part 3 checks to `validation/architecture-checklist.md`.** Replace the trailing `<!-- Part 3 checks added in Task 4 -->` comment with:

```markdown
## Part 3 — Build-Ready Spec & Stubs
- [ ] Metadata blueprint present (objects → fields → relationships); standard objects named, not redefined
- [ ] Component inventory present, each with responsibility + traceability
- [ ] Integration contracts present for each named external system (or "No external integrations")
- [ ] Skeleton stubs are signatures/scaffolding only — no business-logic bodies (bodies are `// TODO (build): …`)
- [ ] Every object/field/class/Flow traces to a POV use case or Part 2 decision — untraceable artifacts removed
- [ ] Under-specified items marked `[TBD — confirm in build]`, not guessed

## Failure → Repair Instructions
**Orphan RAG score (no matching Part 1 finding):** every Part 0 rating must derive from a Part 1 finding. Either add the finding to Part 1 or correct the rating; do not score a quality that was not assessed.
**Stub contains business logic:** strip the body to a `// TODO (build): …` line with the intent. The assessment scaffolds; the build implements.
**Untraceable metadata artifact:** remove it, or add the POV use case / Part 2 decision it serves. If it serves nothing, it does not belong in the spec.
**Generic Salesforce reference:** replace "the Salesforce platform" with the specific cloud/SKU/API/capability (e.g., "Service Cloud + Platform Events").
```

- [ ] **Step 4: Run validator (GREEN).** `python3 tests/validate_skill.py` → `22/22 passed`.
- [ ] **Step 5: Commit.**
```bash
git add refs/architecture-assessment.md templates/technical-architecture-assessment.md \
        validation/architecture-checklist.md
git commit -m "Add build-ready spec & stubs (Part 3) with traceability guardrails"
```

---

## Task 5: HTML render + RAG-token check + TEMPLATE_HTML registration

**Files:**
- Modify: `tests/validate_skill.py` (add HTML to `TEMPLATE_HTML`; add RAG-token check)
- Modify: `templates/technical-architecture-assessment.html` (full render)

- [ ] **Step 1: Build `templates/technical-architecture-assessment.html`.** Replace the skeleton with a full render. READ `templates/discovery-document.html` and COPY its shared CSS verbatim (the `*`, `body`, `.page`, `.header`, `.header h1`, `.header .meta`, `.section`, `.section-title`, `.styled-table`, `.confidence-block`, and `@media print` rules — same Salesforce palette). Then add the CSS below. All dynamic values are `{{UPPER_SNAKE_CASE}}` tokens; keep `{{ }}` balanced.

Required header tokens: `{{PARTNER_NAME}}`, `{{GENERATED_DATE}}`, `{{PREPARED_BY}}`, `{{READINESS_SCORE}}`.

RAG-grid + layer + stub CSS to add:
```html
  /* Well-Architected RAG grid */
  .wa-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .wa-pillar { border: 1px solid #d8dde6; border-radius: 8px; padding: 14px; }
  .wa-pillar h4 { font-size: 0.8rem; color: #0070d2; margin-bottom: 10px; }
  .wa-quality { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 0.8rem; }
  .rag { width: 12px; height: 12px; border-radius: 50%; flex: none; }
  .rag-strong { background: #2e844a; } .rag-emerging { background: #dd7a01; }
  .rag-gap { background: #ea001e; } .rag-na { background: #c9c9c9; }
  /* Target-architecture layer cards */
  .layer { border-left: 3px solid #0070d2; padding: 8px 14px; margin-bottom: 10px; background: #f8fafc; }
  .layer .layer-name { font-weight: 700; font-size: 0.82rem; color: #032d60; }
  /* Read-only stub blocks */
  pre.stub { background: #1b1b2f; color: #e6e6f0; padding: 14px; border-radius: 6px;
             overflow-x: auto; font-size: 0.78rem; line-height: 1.5; }
```

Body structure (each Part in its own `.section` inside `<div class="page">`), using EXACTLY these tokens:
- Header: `{{PARTNER_NAME}}`, meta spans for `{{GENERATED_DATE}}`, `{{PREPARED_BY}}`, `{{READINESS_SCORE}}`.
- **Part 0** `.section` — a `.wa-grid` with three `.wa-pillar` cards (Trusted/Easy/Adaptable). Each quality row: `<span class="rag {{WA_<KEY>_RAG}}"></span>` + the quality name + `{{WA_<KEY>_NOTE}}`. The eight KEYs: SECURE, COMPLIANT, RELIABLE (Trusted); INTENTIONAL, AUTOMATED, ENGAGING (Easy); RESILIENT, COMPOSABLE (Adaptable). Plus `{{TOP_RISKS_HTML}}` and `{{BUILD_VERDICT}}`.
- **Part 1** `.section` — `{{ASSESSMENT_HTML}}` (rebuilt by fill script).
- **Part 2** `.section` — `{{TARGET_ARCH_HTML}}` (rebuilt; rendered as `.layer` cards).
- **Part 3** `.section` — `{{BLUEPRINT_HTML}}` (tables) and stubs rendered as `<pre class="stub">{{STUBS_HTML}}</pre>`.
- **Part 4** `.section` — `{{ROADMAP_HTML}}`.
- **Confidence** `.section` — `<div class="confidence-block">{{CONFIDENCE_HTML}}</div>`.

End the file with a trailing HTML comment documenting every token (mirror the discovery template's convention). Example for one quality: `{{WA_SECURE_RAG}}` is one of `rag-strong` / `rag-emerging` / `rag-gap` / `rag-na`; `{{WA_SECURE_NOTE}}` is the one-line finding.

- [ ] **Step 2: Register the HTML and add the RAG-token check (RED first).** In `tests/validate_skill.py`, add `"templates/technical-architecture-assessment.html",` to the `TEMPLATE_HTML` list. Then add after `t_discovery_canvas_tokens`:

```python
@check("Architecture HTML carries the Well-Architected RAG token families")
def t_architecture_rag_tokens():
    s = read("templates/technical-architecture-assessment.html")
    keys = ["SECURE","COMPLIANT","RELIABLE","INTENTIONAL","AUTOMATED","ENGAGING","RESILIENT","COMPOSABLE"]
    missing = []
    for k in keys:
        for suffix in ("RAG", "NOTE"):
            if f"{{{{WA_{k}_{suffix}}}}}" not in s:
                missing.append(f"WA_{k}_{suffix}")
    assert not missing, f"architecture HTML missing RAG tokens: {missing}"
```

Run validator BEFORE writing the HTML body (or with the skeleton) to observe FAIL on this check (RED). After Step 1's HTML is in place, it passes. The brace/UPPER_SNAKE checks now also apply to the new HTML — confirm they pass. Suite is now 23.

- [ ] **Step 3: Run validator (GREEN).** `python3 tests/validate_skill.py` → `23/23 passed`.
- [ ] **Step 4: Commit.**
```bash
git add tests/validate_skill.py templates/technical-architecture-assessment.html
git commit -m "Add architecture assessment HTML render and RAG-token check"
```

---

## Task 6: SKILL.md 3-question menu restructure + sequencing + menu-parity check

**Files:**
- Modify: `tests/validate_skill.py` (add menu-architecture check)
- Modify: `SKILL.md` (menu, sequencing, pointer/index)

- [ ] **Step 1: Restructure the output menu into three questions.** In `SKILL.md`, change the line "Present the options as **two** `multiSelect` questions in a single `AskUserQuestion` call — the tool caps each question at 4 options, so do not put all six in one list." to "Present the options as **three** `multiSelect` questions in a single `AskUserQuestion` call — the tool caps each question at 4 options."

Then replace the entire `AskUserQuestion({ ... })` block (the fenced block currently holding two questions) with this three-question block:

```
AskUserQuestion({
  questions: [
    {
      question: "Which analysis & readiness outputs would you like?",
      header: "Analysis & Readiness",
      multiSelect: true,
      options: [
        {
          label: "MVP Build Plan",
          description: "Sprint-ready feature breakdown with user stories, technical requirements, phase plan, and commercial context (Stage 8)"
        },
        {
          label: "Red Team Assessment",
          description: "Adversarial analysis: competitive threats, customer churn scenarios, platform dependency scan, and 18-month invalidation scenarios (Stage 9)"
        },
        {
          label: "Partner Readiness Scorecard",
          description: "18-attribute readiness assessment (RAG + 1–3 rank) across sales, product, industry, commercial, and partner-capability fit (Stage 12)"
        },
        {
          label: "Discovery Framework",
          description: "Run structured discovery (10 dimensions, How Might We, Value Proposition + Business Model canvases) and produce a Discovery Document that refines the POV (Stage 15)"
        }
      ]
    },
    {
      question: "Which architecture & build outputs would you like?",
      header: "Architecture & Build",
      multiSelect: true,
      options: [
        {
          label: "Technical & Architectural Assessment",
          description: "Build-guiding assessment vs. Salesforce Well-Architected + target-state architecture + build-ready metadata blueprint & stubs; feeds the MVP Build Plan (Stage 16)"
        },
        {
          label: "Marketecture",
          description: "HTML architecture diagram from the POV Architecture Summary — only when architecture is populated (Stage 14)"
        }
      ]
    },
    {
      question: "Which presentation outputs, or the full package?",
      header: "Package",
      multiSelect: true,
      options: [
        {
          label: "All outputs + home page",
          description: "Generate every downstream artifact (Stages 8–12, 14, 16) plus an HTML home page that links them all (Stage 13). This is the usual choice. Supersedes the individual Analysis/Architecture/Package picks — but does NOT include Discovery (Stage 15), which is an upstream refinement."
        },
        {
          label: "Investor Presentation",
          description: "10-slide HTML pitch deck covering problem, solution, market, traction, business model, team, and Salesforce partnership (Stage 10)"
        },
        {
          label: "Solution Infographic",
          description: "Single-page visual overview: problem stats, solution flow, proven outcomes, and market context (Stage 11)"
        }
      ]
    }
  ]
})
```

- [ ] **Step 2: Update the routing prose and sequencing.** Edit the prose after the block:
  - In the "**All outputs + home page** selected:" line, change "run Stages 8–12 and Stage 14 ... then run Stage 13" to also include Stage 16 **before** Stage 8, i.e.: "run Stage 16 (Technical & Architectural Assessment) first since it feeds the MVP Build Plan, then Stages 8–12 and Stage 14 (Marketecture, if architecture is populated), then run Stage 13 to build the home page. This does NOT include Discovery (Stage 15)."
  - Add a new routing line after the "Discovery Framework selected" line:
    `**"Technical & Architectural Assessment" selected:** load \`refs/architecture-assessment.md\` and run Stage 16. It requires an approved POV and feeds the MVP Build Plan (Stage 8) — if the user also wants the build plan, run the Assessment first, then Stage 8.`
  - In the **Parallel execution note**, add Stage 16 to the independent generators and note the ordering dependency: "Stage 16 (Technical & Architectural Assessment) feeds the MVP Build Plan — when both run, Stage 16 runs before Stage 8."

- [ ] **Step 3: Update the lazy-load pointer + stage index.** Change "**Stages 8–15 — Optional outputs (lazily loaded).**" → "**Stages 8–16 — Optional outputs (lazily loaded).**". Append to the stage-index list line (the one ending "· **Stage 15** — Discovery Framework"): " · **Stage 16** — Technical & Architectural Assessment".

- [ ] **Step 4: Add the menu-architecture check (RED first).** In `tests/validate_skill.py`, add after `t_menu_discovery_option`:

```python
@check("Output menu offers the Technical & Architectural Assessment and cites Stage 16")
def t_menu_architecture_option():
    skill = read("SKILL.md")
    assert "Technical & Architectural Assessment" in skill, "menu missing the Assessment option"
    assert "(Stage 16)" in skill, "menu does not cite (Stage 16)"
```

Run validator before the SKILL.md edits to observe RED. After Steps 1–3, it passes. Confirm these still pass: `t_menu_all_option` ("All outputs + home page" still present), `t_menu_discovery_option` ("Discovery Framework" + "(Stage 15)" still present), `t_menu_stage_refs` (every "(Stage N)" maps to a real stage — the Assessment option cites "(Stage 16)", which exists in output-stages.md), and `t_stage_contiguous`. Suite is now 24.

- [ ] **Step 5: Run validator (GREEN).** `python3 tests/validate_skill.py` → `24/24 passed`.
- [ ] **Step 6: Commit.**
```bash
git add tests/validate_skill.py SKILL.md
git commit -m "Restructure output menu into three questions; add Stage 16 routing + sequencing"
```

---

## Task 7: Behavioral testing with subagents (writing-skills discipline)

Structural checks prove wiring; they cannot prove an agent uses the assessment correctly. Per superpowers:writing-skills, run pressure scenarios with fresh subagents (read-only: they read the files and produce output inline; no repo writes). If a scenario reveals a fix, return to the relevant task's files and repeat its RED→GREEN→commit cycle.

- [ ] **Step 1: RAG-from-findings scenario.** Dispatch a subagent: read `refs/architecture-assessment.md` + `templates/technical-architecture-assessment.md`; run Stage 16 for a fictional partner with a moderately detailed POV (you supply a short POV). Verify every Part 0 RAG rating maps to a Part 1 finding — no orphan scores. PASS if all 8 ratings trace to findings.

- [ ] **Step 2: Stub-discipline scenario.** Same setup. Verify Part 3 stubs are signatures/scaffolding only (no business-logic bodies; bodies are `// TODO (build):`), and every object/field/class traces to a use case or Part 2 decision. PASS if no fabricated logic and all artifacts trace. This is the highest-risk behavior — if the agent writes real method bodies or invents objects with no traceable source, tighten the stub rules in `refs/architecture-assessment.md` and the checklist repair note, then re-run.

- [ ] **Step 3: Thin-POV scenario.** Give a partner whose POV technical sections are mostly empty and no Discovery. Verify the assessment proceeds (no refusal beyond requiring a POV), marks unknowns `[TBD]`, invents no metadata, and still produces a usable structure. PASS if honest and complete.

- [ ] **Step 4: Requires-a-POV scenario.** Invoke Stage 16 with NO POV present. Verify it tells the user to build the POV first rather than fabricating one. PASS if it declines to fabricate.

- [ ] **Step 5: Sequencing scenario.** Simulate "All outputs + home page" selection. Verify the agent runs Stage 16 BEFORE Stage 8 (because the Assessment feeds the Build Plan). PASS if ordering is correct.

- [ ] **Step 6: Record results + update memory.** Document pass/fail and any fixes. Update `~/.claude/projects/-Users-bstauber-claude-projects/memory/pov-builder-skill.md` to note Stage 16 (Technical & Architectural Assessment) exists, the validator is now 24 checks, and the output menu is now three questions.

---

## Self-Review (completed during planning)

**Spec coverage:**
- 5-part document (0–4) → Tasks 2 (Part 1), 3 (Parts 0/2/4), 4 (Part 3) ✓
- Well-Architected spine (3 pillars/8 qualities) → Task 2 ✓
- Target-state 7 layers → Task 3 ✓
- Build-ready blueprint + stubs + traceability guardrails → Task 4 ✓
- Dual-layer (Part 0 exec / Parts 1–3 technical) → Tasks 2–4 ✓
- RAG derived from findings → Task 3 process + checklist + Task 7 behavioral ✓
- Stage 16 registration → Task 1 ✓
- 3-question menu restructure + Marketecture move → Task 6 ✓
- "All outputs" includes it, runs before Stage 8 → Task 6 ✓
- Requires-a-POV, else proceed with TBDs → Task 3 process + Task 7 ✓
- MD source-of-truth / HTML read-only stubs → Task 4 (MD) + Task 5 (HTML `<pre>`) ✓
- Validation checklist + parity/RAG/menu checks → Tasks 2, 5, 6 ✓
- Behavioral testing → Task 7 ✓
- Open decisions (menu wording, RAG class naming) → resolved: labels fixed in Task 6; HTML uses the scorecard's `rag-strong/emerging/gap/na` classes (Task 5) ✓

**Placeholder scan:** Bracketed `[finding]`, `[recommendation]`, `[Object__c]`, etc. are intentional **template** placeholders (the skill's own convention, as in `pov-output.md`), not plan gaps. All validator code, the WA constants, the output-stages pointer, the menu block, the checklist, and the MD template content are given in full. HTML reuses explicitly-cited existing CSS plus given new CSS/markup tokens.

**Type/name consistency:** `WA_PILLARS` / `WA_QUALITIES` / `ARCH_FILES` defined once (Task 2). HTML RAG token keys in Task 5 Step 1 exactly match the check in Task 5 Step 2 (`WA_<KEY>_RAG` / `WA_<KEY>_NOTE`, 8 keys). Suite count progression: 21 → 22 (Task 2) → 22 (Tasks 3–4, content-only) → 23 (Task 5) → 24 (Task 6). The eight qualities are spelled identically everywhere (`Secure, Compliant, Reliable, Intentional, Automated, Engaging, Resilient, Composable`).
