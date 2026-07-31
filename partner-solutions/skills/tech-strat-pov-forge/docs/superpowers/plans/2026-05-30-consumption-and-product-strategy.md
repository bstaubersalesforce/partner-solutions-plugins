# Consumption Opportunities + Product Strategy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new Consumption Opportunities artifact (Stage 18 — build-oriented map of Agentforce/Data Cloud/other-SKU consumption-growth opportunities with named-component blueprints) and a Product Strategy section to the POV plus two slides to the POV Presentation deck.

**Architecture:** This is a documentation/template skill validated by `tests/validate_skill.py` (Python 3 stdlib structural checks) with a pre-commit hook that blocks failing commits. Stage 18 is an independent downstream artifact (own `.md` + styled `.html` template, own checklist, own stage file), dispatched in Wave 1 and linked from the home page. Product Strategy is a new POV section (after Vision) and two new deck slides (after the Vision slide, deck 10→12). TDD rhythm: add the validator check first (RED — fails because feature absent), implement the instruction/template change (GREEN — check passes), commit.

**Tech Stack:** Markdown instruction/template files, HTML templates with `{{TOKEN}}` placeholders, Python 3 stdlib validator, git + pre-commit hook.

---

## File Structure

**New (Feature A — Consumption / Stage 18):**
- `refs/stages/stage-18-consumption-opportunities.md` — stage instructions (carries `**Stage 18 —` heading).
- `templates/consumption-opportunities.md` — Markdown template.
- `templates/consumption-opportunities.html` — own styled HTML template (standardized back-link pill, token glossary).
- `validation/consumption-checklist.md` — pre-delivery checklist.

**Modified:**
- `templates/pov-output.md` — Product Strategy section after Vision.
- `templates/pov-presentation.html` — 2 strategy slides after Vision; renumber all footers to `/ 12`.
- `refs/stages/stage-17-pov-presentation.md` — slide mapping + 12-slide structure.
- `validation/pov-presentation-checklist.md` — 12 slides + strategy faithfulness.
- `SKILL.md` — menu rebalance (Q2 rename + Consumption), Stage 18 orchestration/router, Stage 5 Contradict check.
- `refs/parallel-dispatch.md` — Stage 18 in Wave 1 + threshold + brief note.
- `refs/stages/stage-13-output-home-page.md` — Consumption card + filename.
- `README.md` — outputs row + Product Strategy + stage count.
- `tests/validate_skill.py` — 4 new checks.

**Conventions to match (verbatim):**
- Standardized back-link pill (one per HTML template, immediately after `<body>`):
  `<a href="{{HOME_HREF}}" style="position:fixed;top:14px;left:14px;z-index:9999;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:12px;font-weight:700;letter-spacing:0.04em;text-decoration:none;color:#fff;background:#0070d2;padding:7px 14px;border-radius:100px;box-shadow:0 2px 8px rgba(0,0,0,0.25);">&#8592; All artifacts</a>`
  preceded by the comment: `<!-- Home-page back-link. Fill the HOME_HREF token in the anchor below with {SLUG}-index.html when part of a package; remove this entire <a> line for a standalone artifact (no home page). The token is intentionally not repeated in this comment so a plain string-replace fills only the anchor. -->`
- Confidence labels: `[confirmed]` / `[proposed — confirm]` / `[TBD]`.
- Per-stage file schema: `# Stage N — Title` H1, then a `> Optional output stage…` blockquote loader note, then a `**Stage N — <Title> (optional)**` bold heading (load-bearing — the validator's `t_stage_file_schema` requires the `**Stage N —` line).
- Run validator: `python3 tests/validate_skill.py` from skill root. Work on branch `consumption-and-product-strategy`.
- All work under `/Users/bstauber/.claude/skills/pov-builder`.

---

## Task 1: Product Strategy section in the POV template

**Files:**
- Modify: `templates/pov-output.md`
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Write the failing validator check**

Add to `tests/validate_skill.py` near the other POV/template checks (search for a `read("templates/pov-output.md")` usage, or place it after the discovery checks):

```python
@check("POV template + presentation carry the Product Strategy section/slides")
def t_pov_product_strategy():
    pov = read("templates/pov-output.md")
    deck = read("templates/pov-presentation.html")
    assert "## Product Strategy" in pov, "pov-output.md missing ## Product Strategy section"
    assert "Strategic Thesis" in pov, "pov-output.md missing Strategic Thesis"
    assert "{{STRATEGIC_THESIS}}" in deck, "pov-presentation.html missing {{STRATEGIC_THESIS}} slide token"
    assert "{{PILLAR_1_NAME}}" in deck, "pov-presentation.html missing pillar slide token"
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL — `POV template + presentation carry the Product Strategy section/slides` (pov-output.md missing ## Product Strategy section).

- [ ] **Step 3: Insert the Product Strategy section after Vision**

In `templates/pov-output.md`, the Vision section ends just before `## Solution Description [REQUIRED]`. Insert this new section (with its surrounding `---` separators) immediately before the `## Solution Description` line:

```markdown
## Product Strategy [REQUIRED if known]

**Strategic Thesis:** [Where the product is heading and why now — 2-3 sentences. The governing direction, not a feature list.]

**Product Pillars:** [3-4 capability themes the product is built around, each with the strategic bet behind it and a rough now/next/later.]

**Market Positioning:** [Competitive positioning, target-segment strategy, and pricing/packaging direction.]

**Horizon Sequencing to Moat:** [How the pillars sequence across horizons toward a defensible position — cross-references, does not duplicate, MVP & Roadmap.]

**Platform Bet:** [Why build deeper on Salesforce — the strategic rationale for the platform dependency.]

---

```

(Place it so the order is: Vision → `---` → Product Strategy → `---` → Solution Description. Match the existing `---`-separator style used between other sections.)

- [ ] **Step 4: Run the validator**

Run: `python3 tests/validate_skill.py`
Expected: still FAILS, now on `pov-presentation.html missing {{STRATEGIC_THESIS}} slide token` — confirms the POV half is done. (Task 2 adds the slides.)

- [ ] **Step 5: Commit**

```bash
git add templates/pov-output.md tests/validate_skill.py
git commit -m "POV template: add Product Strategy section after Vision"
```

---

## Task 2: Product Strategy slides in the POV Presentation deck

**Files:**
- Modify: `templates/pov-presentation.html`

- [ ] **Step 1: Confirm the failing assertion**

Run: `python3 tests/validate_skill.py`
Expected: FAIL — `pov-presentation.html missing {{STRATEGIC_THESIS}} slide token` (from Task 1's check). RED for this task.

- [ ] **Step 2: Insert the two new slides after the Vision slide**

In `templates/pov-presentation.html`, find the Vision slide — it ends with `<span class="slide-num" style="color:white;">3 / 10</span>` and its closing `</section>`. The next slide is Solution (`4 / 10`). Insert these TWO new `<section>` slides between the Vision slide's closing `</section>` and the Solution slide's opening `<section>`. Reuse the existing slide markup conventions in this file (the `.slide`, `.eyebrow`, `.divider`, `.slide-footer`, `.slide-num` classes already defined). Use a dark and a light theme to alternate, matching the deck's existing pattern:

```html
  <!-- ── SLIDE 4: STRATEGIC DIRECTION ──────────────── -->
  <section class="slide slide-dark">
    <div class="eyebrow" style="color:var(--sf-blue);">Product Strategy</div>
    <h2 class="title" style="color:white;max-width:880px;">Strategic Direction</h2>
    <div class="divider"></div>
    <p class="body-lg" style="opacity:0.9;max-width:900px;margin-bottom:28px;">{{STRATEGIC_THESIS}}</p>
    <div class="two-col" style="gap:40px;">
      <div>
        <div class="eyebrow" style="color:var(--sf-blue);margin-bottom:8px;">Horizon sequencing to moat</div>
        <p class="body-md" style="opacity:0.85;">{{HORIZON_TO_MOAT}}</p>
      </div>
      <div>
        <div class="eyebrow" style="color:var(--sf-blue);margin-bottom:8px;">Platform bet</div>
        <p class="body-md" style="opacity:0.85;">{{PLATFORM_BET}}</p>
      </div>
    </div>
    <div class="slide-footer"></div>
    <span class="slide-num" style="color:white;">4 / 12</span>
  </section>

  <!-- ── SLIDE 5: PRODUCT PILLARS & POSITIONING ─────── -->
  <section class="slide slide-light">
    <div class="eyebrow" style="color:var(--sf-blue);">Product Strategy</div>
    <h2 class="title">Product Pillars &amp; Positioning</h2>
    <div class="divider"></div>
    <div class="two-col" style="gap:40px;">
      <div>
        <div class="eyebrow" style="margin-bottom:12px;">Product pillars</div>
        <div style="margin-bottom:14px;"><strong>{{PILLAR_1_NAME}}</strong><br><span style="opacity:0.8;">{{PILLAR_1_BET}}</span></div>
        <div style="margin-bottom:14px;"><strong>{{PILLAR_2_NAME}}</strong><br><span style="opacity:0.8;">{{PILLAR_2_BET}}</span></div>
        <div style="margin-bottom:14px;"><strong>{{PILLAR_3_NAME}}</strong><br><span style="opacity:0.8;">{{PILLAR_3_BET}}</span></div>
      </div>
      <div>
        <div class="eyebrow" style="margin-bottom:12px;">Market positioning</div>
        <p class="body-md" style="opacity:0.85;">{{MARKET_POSITIONING}}</p>
      </div>
    </div>
    <div class="slide-footer"></div>
    <span class="slide-num">5 / 12</span>
  </section>
```

- [ ] **Step 3: Renumber every subsequent slide and all footers to /12**

The deck now has 12 slides. Update the `slide-num` spans of the SHIFTED slides (everything after the two new ones) and change ALL `/ 10` to `/ 12`. Read the file; the slides previously numbered 4–10 become 6–12:
- Solution slide: `4 / 10` → `6 / 12`
- (next) `5 / 10` → `7 / 12`
- `6 / 10` → `8 / 12`
- `7 / 10` → `9 / 12`
- `8 / 10` → `10 / 12`
- `9 / 10` → `11 / 12`
- `10 / 10` → `12 / 12`
Also update the Cover/Problem/Vision footers `1 / 10`, `2 / 10`, `3 / 10` → `1 / 12`, `2 / 12`, `3 / 12`.

After editing, verify the deck has exactly 12 distinct slide numbers, each `/ 12`:
Run: `grep -o '[0-9]\+ / 12' templates/pov-presentation.html | sort -t/ -k1 -n | uniq`
Expected: `1 / 12` through `12 / 12`, one each. And `grep -c '/ 10<' templates/pov-presentation.html` → `0`.

- [ ] **Step 4: Run the validator to verify it passes**

Run: `python3 tests/validate_skill.py`
Expected: PASS — `POV template + presentation carry the Product Strategy section/slides`. Confirm no `{{...}}` brace imbalance check regressed.

- [ ] **Step 5: Verify back-link token still single**

Run: `grep -c '{{HOME_HREF}}' templates/pov-presentation.html`
Expected: `1` (the existing pill; the new slides add no HOME_HREF).

- [ ] **Step 6: Commit**

```bash
git add templates/pov-presentation.html
git commit -m "POV presentation: add Strategic Direction + Pillars/Positioning slides (deck 10->12)"
```

---

## Task 3: Update Stage 17 instructions + presentation checklist

**Files:**
- Modify: `refs/stages/stage-17-pov-presentation.md`
- Modify: `validation/pov-presentation-checklist.md`

- [ ] **Step 1: Read both files**

Read `refs/stages/stage-17-pov-presentation.md` (the slide-to-POV-section mapping list) and `validation/pov-presentation-checklist.md` (slide count + faithfulness checks).

- [ ] **Step 2: Update the Stage 17 slide mapping**

In `refs/stages/stage-17-pov-presentation.md`, the slide mapping currently lists 10 slides (Cover, Problem Space, Vision, Solution, Use Cases, Markets, Alignment, MVP/Roadmap, Commercial/Arch, Recommendation). Insert two entries after Vision and before Solution, and note the deck is now 12 slides. Add these two mapping bullets in the correct position:

```markdown
4. Strategic Direction → POV **Product Strategy**: Strategic Thesis (headline) + Horizon Sequencing to Moat + Platform Bet
5. Product Pillars & Positioning → POV **Product Strategy**: the 3–4 Product Pillars with their bets + Market Positioning
```

Renumber the subsequent mapping entries (Solution becomes 6, … Recommendation becomes 12). Update any sentence that says "10-slide" to "12-slide".

- [ ] **Step 3: Update the presentation checklist**

In `validation/pov-presentation-checklist.md`, update the structure check that lists the slides. Change the slide enumeration to include the two new slides and the 12-slide count. Find the line listing all slides (e.g. "All 10 slides present: Cover, Problem Space, Vision, Solution, ...") and replace with:

```markdown
- [ ] All 12 slides present: Cover, Problem Space, Vision, Strategic Direction, Product Pillars & Positioning, Solution, Use Cases, Target Markets & Personas, Solution Alignment, MVP & Roadmap, Commercial Model & Architecture, Recommendation
```

Then add a faithfulness check under the existing faithfulness section:

```markdown
- [ ] Strategic Direction + Product Pillars slides render only what the POV's **Product Strategy** section states (thesis, pillars, positioning, moat, platform bet) — no invented pillars or vague "be the leader" claims
```

- [ ] **Step 4: Verify the Stage 17 heading is intact**

Run: `grep -c '^\*\*Stage 17 —' refs/stages/stage-17-pov-presentation.md`
Expected: `1` (load-bearing heading — do not alter it).

- [ ] **Step 5: Run the validator**

Run: `python3 tests/validate_skill.py`
Expected: all PASS (no new check here; this aligns instructions/checklist with Task 2).

- [ ] **Step 6: Commit**

```bash
git add refs/stages/stage-17-pov-presentation.md validation/pov-presentation-checklist.md
git commit -m "Stage 17 + checklist: map the 2 Product Strategy slides, deck is 12 slides"
```

---

## Task 4: Stage 5 Contradict check for vague Product Strategy

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: Locate the Stage 5 Contradict failure-pattern list**

Read `SKILL.md` and find the Stage 5 "Contradict" section — a bullet list of failure patterns (it starts with "Vision Statement uses vague language..."). 

- [ ] **Step 2: Add one failure-pattern bullet**

Add this bullet to the Stage 5 failure-pattern list (place it near the Vision-vagueness bullet, since it is the same class of check):

```markdown
- Product Strategy uses vague language ("be the leader," "best-in-class," "world-class," "next-gen") with no specific thesis, named product pillar, or concrete market positioning — strategy without specifics is not a strategy
```

- [ ] **Step 3: Run the validator**

Run: `python3 tests/validate_skill.py`
Expected: all PASS (prose addition; no check keys off this, but confirm nothing regressed).

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "SKILL.md Stage 5: add Product Strategy vagueness contradiction check"
```

---

## Task 5: Consumption Opportunities Markdown template

**Files:**
- Create: `templates/consumption-opportunities.md`

- [ ] **Step 1: Create the Markdown template**

Create `templates/consumption-opportunities.md` with this content:

```markdown
# [Partner Name] — Consumption Opportunities
**Date:** [YYYY-MM-DD] · **Org62 Opportunity Stage:** [stage] · **Built on Salesforce**
**Scope:** Consumption-growth opportunities only (Agentforce, Data Cloud, other Salesforce SKUs). For Flex Credit cost sizing see the **sf-flex-estimator** skill; for core-solution architecture see the **Technical & Architectural Assessment** (Stage 16); for license pull-through see the POV's **ISV Commercial Model**.

---

## Consumption Opportunity Map

| # | Opportunity | Type | Value driver | Priority | Consumption signal |
|---|-------------|------|--------------|----------|--------------------|
| 1 | [name] | Agent | [value] | [H/M/L] | [qualitative signal — e.g. "high-volume inference"] |
| 2 | [name] | Data | [value] | [H/M/L] | [qualitative signal — e.g. "large external ingest"] |
| 3 | [name] | SKU | [value] | [H/M/L] | [qualitative signal] |

> "Consumption signal" is a qualitative note, never a dollar figure. Size with the sf-flex-estimator skill.

---

## Agentforce Agents

### Agent Opportunity 1: [name] `[confirmed | proposed — confirm | TBD]`
**Purpose / trigger:** [what this agent does and what invokes it]
**Topics & actions:** [named agent topics and actions]
**Objects read/written:** [Salesforce objects]
**Supporting components:** [Flow / Apex / prompt templates]
**Build steps:**
1. [step]
2. [step]
3. [step]

### Agent Opportunity 2: [name] `[label]`
**Purpose / trigger:** [...]
**Topics & actions:** [...]
**Objects read/written:** [...]
**Supporting components:** [...]
**Build steps:**
1. [step]
2. [step]
3. [step]

---

## Data Cloud

### Data Opportunity 1: [name] `[label]`
**Purpose / value:** [why this data asset grows value]
**DMOs / data streams / sources:** [data model objects, streams, source objects]
**Mapping & identity resolution:** [mapping notes, unification keys]
**Activation target:** [where the unified data is activated]
**Build steps:**
1. [step]
2. [step]
3. [step]

### Data Opportunity 2: [name] `[label]`
**Purpose / value:** [...]
**DMOs / data streams / sources:** [...]
**Mapping & identity resolution:** [...]
**Activation target:** [...]
**Build steps:**
1. [step]
2. [step]
3. [step]

---

## Other Salesforce SKU Opportunities

| SKU / Capability | Trigger in this solution | Value | Resellable by partner? |
|------------------|--------------------------|-------|------------------------|
| Shield (Platform Encryption / Event Monitoring) | [trigger] | [value] | [Y/N/TBD] |
| Backup & Archive | [trigger] | [value] | [Y/N/TBD] |
| Sandboxes (Partial/Full) | [trigger] | [value] | [Y/N/TBD] |
| [other resellable product] | [trigger] | [value] | [Y/N/TBD] |

---

## Notes
- **Sizing:** Use the **sf-flex-estimator** skill to model Flex Credit consumption cost for the Agentforce and Data Cloud opportunities above.
- **Deeper architecture:** The **Technical & Architectural Assessment** (Stage 16) covers core-solution build-readiness; this artifact covers only consumption-growth opportunities.
```

- [ ] **Step 2: Verify it exists**

Run: `test -f templates/consumption-opportunities.md && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add templates/consumption-opportunities.md
git commit -m "Add consumption-opportunities Markdown template"
```

---

## Task 6: Consumption Opportunities HTML template

**Files:**
- Create: `templates/consumption-opportunities.html`

- [ ] **Step 1: Create the styled HTML template**

Create `templates/consumption-opportunities.html`. Model the styling on `templates/partner-readiness-scorecard.html` (table-heavy, same palette: navy `#032d60`, blue `#0070d2`, slate `#54698d`, light `#f4f6fb`). Include: the standardized back-link pill right after `<body>` (verbatim, see Conventions), a header with `{{PARTNER_NAME}}` / `{{GENERATED_DATE}}` / `{{OPPORTUNITY_STAGE}}`, the ranked opportunity table (`{{OPPORTUNITY_ROWS}}`), the Agents section (`{{AGENT_BLOCKS}}`), the Data section (`{{DATA_BLOCKS}}`), the Other-SKU table (`{{SKU_ROWS}}`), and a footer note. Use this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{PARTNER_NAME}} — Consumption Opportunities</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: "Salesforce Sans","Helvetica Neue",Helvetica,Arial,sans-serif; font-size: 15px; line-height: 1.6; color: #1a1a1a; background: #f4f6fb; }
  .page-wrapper { max-width: 1000px; margin: 32px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 16px rgba(3,45,96,0.10); overflow: hidden; }
  .doc-header { background: #032d60; color: #fff; padding: 32px 44px 26px; }
  .doc-header .eyebrow { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #7db8f7; margin-bottom: 6px; }
  .doc-header h1 { font-size: 26px; font-weight: 700; margin-bottom: 12px; }
  .doc-meta { font-size: 12.5px; color: #cfe2fb; }
  .content { padding: 32px 44px 48px; }
  .content h2 { font-size: 19px; color: #032d60; margin: 30px 0 12px; padding-bottom: 6px; border-bottom: 2px solid #0070d2; }
  .content h3 { font-size: 15px; color: #032d60; margin: 20px 0 6px; }
  .scope-note { background: #eef4fc; border-left: 4px solid #0070d2; padding: 10px 14px; font-size: 13px; color: #54698d; margin-bottom: 8px; border-radius: 0 4px 4px 0; }
  table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13.5px; margin: 0 0 18px; border: 1px solid #d8e0ec; border-radius: 6px; overflow: hidden; }
  thead tr { background: #032d60; color: #fff; }
  thead th { padding: 9px 13px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
  tbody tr:nth-child(even) { background: #f0f5ff; }
  tbody td { padding: 8px 13px; border-bottom: 1px solid #e8edf5; vertical-align: top; }
  .opp-block { border: 1px solid #d8e0ec; border-radius: 6px; padding: 14px 16px; margin-bottom: 14px; background: #fbfdff; }
  .opp-block .lbl { font-weight: 700; color: #0070d2; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; }
  .footer-note { font-size: 12px; color: #54698d; border-top: 1px solid #e0e6f0; padding-top: 14px; margin-top: 8px; }
  @media print { body { background: #fff; } .page-wrapper { box-shadow: none; border-radius: 0; margin: 0; max-width: 100%; } }
</style>
</head>
<body>
<!-- Home-page back-link. Fill the HOME_HREF token in the anchor below with {SLUG}-index.html when part of a package; remove this entire <a> line for a standalone artifact (no home page). The token is intentionally not repeated in this comment so a plain string-replace fills only the anchor. -->
<a href="{{HOME_HREF}}" style="position:fixed;top:14px;left:14px;z-index:9999;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:12px;font-weight:700;letter-spacing:0.04em;text-decoration:none;color:#fff;background:#0070d2;padding:7px 14px;border-radius:100px;box-shadow:0 2px 8px rgba(0,0,0,0.25);">&#8592; All artifacts</a>
<div class="page-wrapper">
  <header class="doc-header">
    <div class="eyebrow">Salesforce ISV Partner · Consumption Opportunities</div>
    <h1>{{PARTNER_NAME}}</h1>
    <div class="doc-meta">{{GENERATED_DATE}} · {{OPPORTUNITY_STAGE}} · Built on Salesforce</div>
  </header>
  <main class="content">
    <div class="scope-note">Consumption-growth opportunities only (Agentforce, Data Cloud, other Salesforce SKUs). Flex Credit sizing → sf-flex-estimator skill; core-solution architecture → Technical &amp; Architectural Assessment (Stage 16); license pull-through → POV ISV Commercial Model.</div>

    <h2>Consumption Opportunity Map</h2>
    <table>
      <thead><tr><th>#</th><th>Opportunity</th><th>Type</th><th>Value driver</th><th>Priority</th><th>Consumption signal</th></tr></thead>
      <tbody>
{{OPPORTUNITY_ROWS}}
      </tbody>
    </table>

    <h2>Agentforce Agents</h2>
{{AGENT_BLOCKS}}

    <h2>Data Cloud</h2>
{{DATA_BLOCKS}}

    <h2>Other Salesforce SKU Opportunities</h2>
    <table>
      <thead><tr><th>SKU / Capability</th><th>Trigger in this solution</th><th>Value</th><th>Resellable?</th></tr></thead>
      <tbody>
{{SKU_ROWS}}
      </tbody>
    </table>

    <div class="footer-note">Sizing: use the sf-flex-estimator skill for Flex Credit cost modeling of the Agentforce and Data Cloud opportunities. Deeper architecture: see the Technical &amp; Architectural Assessment (Stage 16).</div>
  </main>
</div>

<!-- =====================================================================
     TOKEN REFERENCE — every token used in this template (fill all):
     {{PARTNER_NAME}} {{GENERATED_DATE}} {{OPPORTUNITY_STAGE}} {{HOME_HREF}}
     {{OPPORTUNITY_ROWS}} — <tr><td>…</td>…</tr> rows for the ranked map
     {{AGENT_BLOCKS}} — one <div class="opp-block">…</div> per agent opportunity
     {{DATA_BLOCKS}}  — one <div class="opp-block">…</div> per data opportunity
     {{SKU_ROWS}}     — <tr>…</tr> rows for the other-SKU table
===================================================================== -->
</body>
</html>
```

- [ ] **Step 2: Verify exactly one back-link token + balanced braces**

Run: `grep -c '{{HOME_HREF}}' templates/consumption-opportunities.html`
Expected: `1`
Run: `python3 -c "s=open('templates/consumption-opportunities.html').read(); print('braces', s.count('{{'), s.count('}}'))"`
Expected: equal counts.

- [ ] **Step 3: Commit**

```bash
git add templates/consumption-opportunities.html
git commit -m "Add consumption-opportunities styled HTML template"
```

---

## Task 7: Consumption checklist + Stage 18 instructions + validator wiring

**Files:**
- Create: `validation/consumption-checklist.md`
- Create: `refs/stages/stage-18-consumption-opportunities.md`
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Write the failing validator check**

Add to `tests/validate_skill.py`. First add the stage to the `DOWNSTREAM_STAGES` map (the dict mapping stage numbers to files — find it; it currently ends at `17: "refs/stages/stage-17-pov-presentation.md"`):

```python
    18: "refs/stages/stage-18-consumption-opportunities.md",
```

Add `"templates/consumption-opportunities.html"` to BOTH the `TEMPLATE_HTML` list and the `HOME_LINK_TEMPLATES` list.

Then add the check:

```python
@check("Consumption stage 18 files exist and are wired")
def t_consumption_stage_files():
    assert exists("refs/stages/stage-18-consumption-opportunities.md"), "stage-18 file missing"
    assert exists("templates/consumption-opportunities.md"), "consumption md template missing"
    assert exists("templates/consumption-opportunities.html"), "consumption html template missing"
    assert exists("validation/consumption-checklist.md"), "consumption checklist missing"
    skill = read("SKILL.md")
    assert "refs/stages/stage-18-consumption-opportunities.md" in skill, "SKILL.md router missing stage 18"
    stage = read("refs/stages/stage-18-consumption-opportunities.md")
    assert re.search(r"^\*\*Stage 18 —", stage, re.M), "stage-18 missing '**Stage 18 —' heading"
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL — `Consumption stage 18 files exist and are wired` (and possibly the stage-router-parity / contiguity checks complain about stage 18 — that is expected until SKILL.md is wired in Task 8; this task creates the files + checklist + stage doc, Task 8 wires SKILL.md). NOTE: if `t_stage_router_parity` or contiguity fails because SKILL.md does not yet list stage 18, that is acceptable mid-task — but to keep the pre-commit hook from blocking, this task and Task 8 must both be done before committing the validator change. To avoid a blocked commit, DO Steps 3–5 (create files), then Task 8 (wire SKILL.md), and commit the validator change at the END of Task 8. Therefore: in THIS task, create the files but do NOT commit the validate_skill.py change yet — leave it staged. (See Step 6.)

- [ ] **Step 3: Create the consumption checklist**

Create `validation/consumption-checklist.md`:

```markdown
# Consumption Opportunities Pre-Delivery Validation Checklist

Run every check before delivering the Consumption Opportunities artifact (.md + .html).

## Structure
- [ ] Consumption Opportunity Map table present and ranked (Priority H/M/L)
- [ ] Agentforce Agents section: 2–4 opportunities, each with topics & actions, objects, supporting components, and build steps
- [ ] Data Cloud section: 2–4 opportunities, each with DMOs/streams/sources, mapping & identity resolution, activation target, and build steps
- [ ] Other Salesforce SKU Opportunities table present (Shield, Backup & Archive, sandboxes, other resellable products) with resellable-by-partner column
- [ ] HTML carries the standardized home-page back-link pill (`{{HOME_HREF}}` → `{SLUG}-index.html`); removed if standalone
- [ ] No `{{PLACEHOLDER}}` tokens remain in the rendered output

## Scope discipline (no overlap)
- [ ] "Consumption signal" entries are qualitative — NO dollar figures (sizing belongs to sf-flex-estimator)
- [ ] Does not restate the core-solution architecture (that is Stage 16) — only consumption-growth components
- [ ] Does not restate the license pull-through commercial model (that is the POV ISV Commercial Model)
- [ ] Every opportunity is confidence-labeled (`[confirmed]` / `[proposed — confirm]` / `[TBD]`); nothing invented beyond what the POV/vertical supports

## Failure → Repair
**Unfilled token:** Fill from POV/vertical data or mark `[TBD]` with an owner.
**Dollar figure in consumption signal:** Replace with a qualitative signal; point to sf-flex-estimator for sizing.
**Invented opportunity:** Remove. Only opportunities grounded in the POV or matched vertical may appear.
```

- [ ] **Step 4: Create the Stage 18 instructions**

Create `refs/stages/stage-18-consumption-opportunities.md`:

```markdown
# Stage 18 — Consumption Opportunities

> Optional output stage, lazily loaded by pov-builder. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 18 — Consumption Opportunities (optional)**
Triggered when the user selects "Consumption Opportunities" from the output menu, or asks for a consumption map, agent/data opportunity map, or where-to-grow-consumption analysis.

Load `templates/consumption-opportunities.md` and `templates/consumption-opportunities.html`.
Load `validation/consumption-checklist.md`.

**What it is — and its boundaries.** A build-oriented map of where to grow consumption on the partner's solution via Agentforce agents, Data Cloud, and other Salesforce SKUs, with named-component build blueprints to start each. It is **consumption-growth-scoped and independent** (may run without Stage 16). It must NOT:
- restate the core-solution architecture — that is the Technical & Architectural Assessment (Stage 16);
- restate the license pull-through commercial model — that is the POV's ISV Commercial Model section + `refs/pull-through-gtm.md`;
- produce Flex Credit dollar sizing — that is the `sf-flex-estimator` skill. Give a qualitative "consumption signal" per opportunity and point to sf-flex-estimator for cost modeling.

Map the POV (and matched vertical) to the artifact:
1. Use cases + Solution + Architecture Summary → candidate Agentforce agent opportunities (2–4): name, purpose/trigger, topics & actions, objects read/written, supporting Flow/Apex/prompt components, 3–5 build steps. Confidence-label each.
2. Data Model + integrations + external data → Data Cloud opportunities (2–4): DMOs/data streams/source objects, mapping & identity resolution, activation target, 3–5 build steps. Confidence-label each.
3. Solution + compliance/scale needs → Other Salesforce SKU opportunities (Shield, Backup & Archive, sandboxes, other partner-resellable products): trigger, value, resellable-by-partner (Y/N/TBD).
4. Rank all opportunities into the Consumption Opportunity Map table with a qualitative consumption signal each.

Fill both templates via the HTML Output Method (`refs/html-output-method.md`); fill every `{{TOKEN}}`; do not invent opportunities the POV/vertical does not support. Run every check in `validation/consumption-checklist.md` before delivering.

**Home-page back-link.** Set `{{HOME_HREF}}` to `{SLUG}-index.html` when part of a package; remove the back-link `<a>` line when standalone.

**Filename (Stage 13 convention):** `{SLUG}-consumption-opportunities.md` + `{SLUG}-consumption-opportunities.html`.

Deliver the file path(s). When run non-interactively (package dispatch), produce both `.md` and `.html` in one pass — do not pause for approval.
```

- [ ] **Step 5: Verify the files exist**

Run: `test -f validation/consumption-checklist.md && test -f refs/stages/stage-18-consumption-opportunities.md && echo OK`
Expected: `OK`

- [ ] **Step 6: Stage everything but defer commit to Task 8**

Run: `git add tests/validate_skill.py validation/consumption-checklist.md refs/stages/stage-18-consumption-opportunities.md templates/consumption-opportunities.md templates/consumption-opportunities.html`
(Do not commit yet — the validator's router-parity/contiguity checks require SKILL.md's router to list Stage 18, which Task 8 adds. Committing now would be blocked by the pre-commit hook. Task 8 finishes the wiring and commits.)

---

## Task 8: Wire Stage 18 into SKILL.md (router, menu, orchestration)

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: Add the router-table row**

In `SKILL.md`, find the router table (rows like `| 17 | POV Presentation | refs/stages/stage-17-pov-presentation.md |`). Add:

```markdown
| 18 | Consumption Opportunities | `refs/stages/stage-18-consumption-opportunities.md` |
```

- [ ] **Step 2: Rebalance the menu — rename Q2 + add Consumption option**

Find the second `AskUserQuestion` question (`header: "Architecture & Build"`). Change its header to `"Architecture & Growth"`. Then add a third option to that question's `options` array (it currently has Technical & Architectural Assessment + Marketecture):

```javascript
        {
          label: "Consumption Opportunities",
          description: "Build-oriented map of where Agentforce agents, Data Cloud, and other Salesforce SKUs (Shield, Backup, sandboxes) grow consumption — with named-component build blueprints per opportunity (Stage 18). Consumption-growth-scoped; points to sf-flex-estimator for cost sizing."
        }
```

(Keep "Technical & Architectural Assessment" and its "(Stage 16)" citation, and "Marketecture", intact. Q2 now has 3 options — still ≤4.)

- [ ] **Step 3: Update the "All outputs + home page" description**

Find the `All outputs + home page` option description (lists "Stages 8–12, 14, 15 (auto-capture discovery), 16, 17"). Update the stage list to include 18: `Stages 8–12, 14, 15 (auto-capture discovery), 16, 17, 18`.

- [ ] **Step 4: Update the dispatch-rule and ordering prose**

In the post-POV orchestration block: in the dispatch-rule bullet, add 18 to the independent-downstream-artifacts stage list. In the ordering bullet, add 18 to the Wave-1 concurrent list. (Stage 18 is independent — no upstream feeder — so it belongs with the Wave 1 generators.)

- [ ] **Step 5: Run the validator (now everything is wired)**

Run: `python3 tests/validate_skill.py`
Expected: ALL pass. Specifically: `Consumption stage 18 files exist and are wired`, the stage-router-parity check (now includes 18), stage-contiguity (now 1..18), `t_home_link_token_once` (now covers consumption-opportunities.html), `t_pov_product_strategy`. Count = prior 38 + 2 new so far (t_pov_product_strategy from Task 1, t_consumption_stage_files from Task 7) = 40 — plus Tasks 9/10 add 2 more → final 42.

- [ ] **Step 6: Commit (this commit includes Task 7's staged files)**

```bash
git add SKILL.md tests/validate_skill.py validation/consumption-checklist.md refs/stages/stage-18-consumption-opportunities.md templates/consumption-opportunities.md templates/consumption-opportunities.html
git commit -m "Stage 18 Consumption Opportunities: files, checklist, validator, SKILL.md router+menu+orchestration"
```

---

## Task 9: Stage 18 in parallel dispatch (Wave 1)

**Files:**
- Modify: `refs/parallel-dispatch.md`
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Write the failing validator check**

Add to `tests/validate_skill.py`:

```python
@check("Parallel dispatch includes Stage 18 (Consumption) in Wave 1")
def t_dispatch_consumption():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "stage 18" in low or "consumption" in low, "parallel-dispatch.md missing Stage 18 / consumption"
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL — `Parallel dispatch includes Stage 18 (Consumption) in Wave 1`.

- [ ] **Step 3: Add Stage 18 to the threshold and Wave 1 lists**

In `refs/parallel-dispatch.md`:
Find the threshold-count line (currently `... 8, 9, 10, 11, 12, 14, 15 (auto-capture), 16, 17.`) and add `, 18`:
`Count only the independent **downstream artifact** stages: 8, 9, 10, 11, 12, 14, 15 (auto-capture), 16, 17, 18.`
Find the Wave 1 bullet (`(Stages 8, 9, 10, 11, 12, 14, 15, 17)`) and change to `(Stages 8, 9, 10, 11, 12, 14, 15, 17, 18)`.

- [ ] **Step 4: Add a Stage 18 brief note**

In the "## Compact shared payload" section, after the Discovery brief paragraph, add:

```markdown
**Consumption (Stage 18) brief.** Stage 18 is independent (needs only the approved POV) and runs in Wave 1. Its brief states: "Produce the Consumption Opportunities artifact (.md + .html) in one pass, non-interactively. Consumption-growth-scoped only — do not restate the core architecture (Stage 16) or the license pull-through (POV Commercial Model); give qualitative consumption signals, not dollar sizing."
```

- [ ] **Step 5: Run the validator to verify it passes**

Run: `python3 tests/validate_skill.py`
Expected: PASS — `Parallel dispatch includes Stage 18 (Consumption) in Wave 1`.

- [ ] **Step 6: Commit**

```bash
git add refs/parallel-dispatch.md tests/validate_skill.py
git commit -m "Dispatch: Stage 18 Consumption Opportunities in Wave 1"
```

---

## Task 10: Stage 13 home-page card + filename for consumption

**Files:**
- Modify: `refs/stages/stage-13-output-home-page.md`
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Write the failing validator check**

Add to `tests/validate_skill.py`:

```python
@check("Stage 13 references the consumption-opportunities filename")
def t_stage13_consumption_filename():
    s = read("refs/stages/stage-13-output-home-page.md")
    assert "consumption-opportunities" in s, "Stage 13 does not reference {SLUG}-consumption-opportunities"
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL — `Stage 13 references the consumption-opportunities filename`.

- [ ] **Step 3: Add the filename to the convention list**

In `refs/stages/stage-13-output-home-page.md`, add to the filename-convention bullet list (place it last, after the discovery/architecture entries):

```markdown
- `SLUG-consumption-opportunities.md` + `SLUG-consumption-opportunities.html`
```

- [ ] **Step 4: Add the card to the ordering rule**

Find the card-ordering line (currently `Order cards: POV (Core) first, then Presentation, Discovery, Build, Risk, Sales, Visual, Readiness, Architecture — listing only what exists.`). Change to:
`Order cards: POV (Core) first, then Presentation, Discovery, Build, Risk, Sales, Visual, Readiness, Architecture, Consumption — listing only what exists.` Then append, after that line:

```markdown
   (Consumption = the Consumption Opportunities artifact; View ↗ + Markdown ↓.)
```

- [ ] **Step 5: Run the validator to verify it passes**

Run: `python3 tests/validate_skill.py`
Expected: PASS — `Stage 13 references the consumption-opportunities filename`. Full count now 42.

- [ ] **Step 6: Commit**

```bash
git add refs/stages/stage-13-output-home-page.md tests/validate_skill.py
git commit -m "Stage 13: consumption-opportunities card + filename"
```

---

## Task 11: README refresh + final verification

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Full validator run**

Run: `python3 tests/validate_skill.py`
Expected: ALL pass, count = 42 (baseline 38 + 4 new: t_pov_product_strategy, t_consumption_stage_files, t_dispatch_consumption, t_stage13_consumption_filename).

- [ ] **Step 2: Update the README outputs table + flow**

In `README.md`:
(a) Add a row to the "What it produces" table:
`| **Consumption Opportunities** (ranked agent/data/SKU consumption-growth map with named-component build blueprints) | Markdown + HTML | "All outputs" · "consumption" / "agent & data opportunities" — Stage 18 |`
(b) Update the prose that lists which stages are optional/in "All outputs" to include Stage 18 (and the Product Strategy section as a POV addition). Find the sentence listing "Stages 8–12, 14, 15, 16, and 17 ... make up 'All outputs'" and add 18. Add a mention that the POV now includes a **Product Strategy** section (after Vision) and the POV Presentation renders it as 2 slides (deck is 12 slides).

- [ ] **Step 3: Structural smoke test of both new/changed HTML templates**

```bash
python3 - <<'PYEOF'
c = open('/Users/bstauber/.claude/skills/pov-builder/templates/consumption-opportunities.html').read()
assert c.count('{{HOME_HREF}}') == 1, "consumption HOME_HREF not 1"
assert 'All artifacts</a>' in c, "consumption back-link missing"
assert c.count('{{') == c.count('}}'), "consumption brace imbalance"
d = open('/Users/bstauber/.claude/skills/pov-builder/templates/pov-presentation.html').read()
assert '{{STRATEGIC_THESIS}}' in d and '{{PILLAR_1_NAME}}' in d, "strategy slide tokens missing"
import re
nums = sorted(set(re.findall(r'(\d+) / 12', d)), key=int)
assert nums == [str(i) for i in range(1,13)], f"deck not 1..12: {nums}"
assert d.count('/ 10<') == 0, "stale /10 footers remain"
print("smoke test OK")
PYEOF
```
Expected: `smoke test OK`

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "README: Consumption Opportunities (Stage 18) + Product Strategy section"
```

---

## Self-Review Checklist (run before execution handoff)

- [ ] **Spec coverage:** Feature A artifact (T5 md, T6 html, T7 checklist+stage+validator, T8 SKILL wiring, T9 dispatch, T10 home page); Feature B (T1 POV section, T2 slides, T3 stage17+checklist, T4 contradict check); menu rebalance (T8); README (T11). All spec sections mapped.
- [ ] **Placeholder scan:** no TBD/TODO in plan steps; all template/code content shown verbatim. (The `[bracketed]` items inside the consumption-opportunities.md template are intentional fill-guides, matching how pov-output.md is written — they are template content, not plan placeholders.)
- [ ] **Type/name consistency:** token names consistent — `{{STRATEGIC_THESIS}}`, `{{HORIZON_TO_MOAT}}`, `{{PLATFORM_BET}}`, `{{PILLAR_1_NAME}}`/`{{PILLAR_1_BET}}` (×3), `{{MARKET_POSITIONING}}` (deck); `{{OPPORTUNITY_ROWS}}`, `{{AGENT_BLOCKS}}`, `{{DATA_BLOCKS}}`, `{{SKU_ROWS}}`, `{{PARTNER_NAME}}`, `{{GENERATED_DATE}}`, `{{OPPORTUNITY_STAGE}}`, `{{HOME_HREF}}` (consumption html). Filenames `{SLUG}-consumption-opportunities.{md,html}`. Validator check names unique: t_pov_product_strategy, t_consumption_stage_files, t_dispatch_consumption, t_stage13_consumption_filename.
- [ ] **Commit-ordering note:** Task 7 stages but does not commit (router parity needs Task 8); Task 8 commits both. This avoids a pre-commit-hook block. Flagged explicitly in T7 Step 6 and T8 Step 6.
- [ ] **Validator count:** 38 → 42 (4 new checks added in T1, T7, T9, T10).
