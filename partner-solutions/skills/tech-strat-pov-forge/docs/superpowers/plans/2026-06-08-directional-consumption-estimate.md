# Directional Consumption Pre-Estimate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a directional, credits-only consumption pre-estimate to pov-builder's Stage 18 (Consumption Opportunities) that seeds the official Agentforce/Data 360 calculators without replacing `sf-flex-estimator`.

**Architecture:** Stage 18 is a content-driven artifact (Markdown + HTML templates, a stage instruction file, a validation checklist), guarded by a structural test suite (`tests/validate_skill.py`). This feature adds a new rate-card reference, refines the stage instructions, extends both templates with a single new scalar token (`{{SIZING_BAND_NOTE}}`) + per-opportunity estimate fields rendered inside the existing `{{AGENT_BLOCKS}}`/`{{DATA_BLOCKS}}` injected content, adds checklist guards, and adds structural assertions. The per-opportunity estimate is LLM-generated prose/tables (not deterministic code), so the "test" is the structural guard + the checklist self-validation, consistent with the skill's posture on generated content (BACKLOG R6).

**Tech Stack:** Markdown, HTML templates with `{{TOKEN}}` block-injection, Python 3 structural validator (`tests/validate_skill.py`, run via the `.githooks` pre-commit hook).

**TDD rhythm for this skill:** Because the deliverable is content, each task's "failing test" is a new assertion added to `tests/validate_skill.py` that fails against the *unedited* content, then passes once the content is filled. Run the whole suite with `python3 tests/validate_skill.py` (exit 0 = all pass). All paths below are relative to the skill root `/Users/bstauber/.claude/skills/pov-builder`.

**Spec:** `docs/superpowers/specs/2026-06-08-directional-consumption-estimate-design.md`

---

### Task 1: New rate-card reference `refs/consumption-estimation.md`

**Files:**
- Create: `refs/consumption-estimation.md`
- Modify: `tests/validate_skill.py` (add one `@check`)
- Test: `tests/validate_skill.py` (same file — structural assertion)

- [ ] **Step 1: Write the failing test**

Add this check near the other consumption checks (after `t_consumption_stage_files`, around line 263 in `tests/validate_skill.py`):

```python
@check("Consumption estimation rate-card ref exists, is wired, and carries the model")
def t_consumption_estimation_ref():
    assert exists("refs/consumption-estimation.md"), "refs/consumption-estimation.md missing"
    ref = read("refs/consumption-estimation.md")
    # core credit rules (from the Agentforce Credit Estimator + Questionnaire)
    assert "20" in ref and re.search(r"action", ref, re.I), "ref missing 20-credit action rule"
    assert re.search(r"\b2\b.*basic|basic.*\b2\b", ref, re.I), "ref missing basic-prompt (2) rule"
    assert re.search(r"\b4\b.*standard|standard.*\b4\b", ref, re.I), "ref missing standard-prompt (4) rule"
    # Data 360 model + a known meter
    assert re.search(r"run frequency", ref, re.I), "ref missing Data 360 run-frequency lever"
    assert "100,000" in ref or "100000" in ref, "ref missing Profile Unification meter"
    # abstract bands (no reference ranges) + sync note
    assert re.search(r"\bS/M/L/XL\b|abstract", ref, re.I), "ref missing abstract band model"
    assert re.search(r"sf-flex-estimator", ref), "ref missing authoritative-owner sync note"
    # stage 18 must load it
    assert "refs/consumption-estimation.md" in read("refs/stages/stage-18-consumption-opportunities.md"), \
        "stage-18 does not load the rate-card ref"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -5`
Expected: FAIL — `refs/consumption-estimation.md missing` (file not created yet). Suite count rises to 70 with this failure.

- [ ] **Step 3: Create the rate-card reference**

Create `refs/consumption-estimation.md` with this exact content:

```markdown
# Consumption Estimation — Directional Rate Card

> **Directional only.** This ref lets Stage 18 produce order-of-magnitude
> consumption pre-estimates that *seed* the official Agentforce Credit Estimator
> and Data 360 calculator. It does **not** produce dollar / PUPM / contract
> pricing — `sf-flex-estimator` owns authoritative Flex-Credit cost sizing. If a
> rate here ever diverges from `sf-flex-estimator`, that skill wins; keep the two
> in sync.

## Agentforce — action / prompt credits

| Component | Credits | Note |
|-----------|--------:|------|
| 1 Agentforce Action (production) | 20 | Covers the whole action execution, including any Flow/Apex/prompt bundled inside it |
| 1 Agentforce Action (sandbox) | 16 | 20% off production |
| 1 standalone prompt — Basic | 2 | LLM inference not initiated by an action |
| 1 standalone prompt — Standard | 4 | Higher-performance models |
| 1 standalone prompt — Advanced | 16 | Advanced-tier models |

**Volume → credits (per opportunity, per anchored band):**

```
Total monthly actions = U × F × A × #Entities
Total annual actions   = Total monthly actions × 12
Annual action credits  = Total annual actions × 20         (× 0.8 for sandbox)
Annual prompt credits  = Total annual prompts × (2 | 4 | 16 by tier)
Directional credit band = low–high across reasonable A / prompt-tier assumptions
```

- `U` = est. users per entity
- `F` = monthly invocations per user
- `A` = internal actions per invocation
- `#Entities` = count of the scaling unit (branches, hubs, sites, seats, …)

## Data 360 — volume × frequency × multiplier

```
Annual credits = (Data Volume in millions of rows) × Run Frequency × Usage-Type Multiplier
```

Run Frequency = number of runs per year (e.g. 365 daily, 26 bi-weekly, 12 monthly).
Sandbox usage = 20% off.

**Usage-type multipliers — credits per million rows processed:**

| Usage type | Credits / 1M rows |
|------------|------------------:|
| Profile Unification | 100,000 |
| Streaming Data Pipeline | 5,000 |
| Batch Data Pipeline | 2,000 |
| Streaming Calculated Insights | 800 |
| Streaming Actions | 800 |
| Real-Time Profile API | 900 |
| Batch Data Transforms | 400 |
| Data Federation | 70 |
| Data Shares | 70 |
| Unstructured Data Processed | 60 |
| Segmentation | 20 |
| Batch Calculated Insights | 15 |
| Batch Activation | 10 |
| Data Queries | 2 |
| Internal Data Pipeline | 0 |

## Bottom-up method (journey → step → component)

1. Document each user journey the solution drives.
2. Segment each journey into discrete steps.
3. Map the Agentforce component to each step (Action = 20, standalone prompt = 2/4/16; an action's bundled prompt is already inside the 20).
4. Sum to credits-per-journey-run; multiply by monthly volume, then ×12.

## Customer-size bands (abstract)

S / M / L / XL are **relative labels** for the target customer's size — they carry
**no reference entity-count ranges**. Anchor every estimate to the single band
that fits the POV's target customer, and state it. The concrete `#Entities`
figure comes from the target customer in the POV (or a stated assumption), **not**
from a band lookup. To scale to another band, change `#Entities` (and optionally
U/F); the formula is unchanged.

## Worked example (synthetic — illustration only)

A retail bank operating **N branches** runs a lifecycle-handoff agent:
6 users/branch × 2 runs/user/month × 5 actions = 60 actions/branch/month.
Across N branches → 60 × N monthly actions → ×12 annual → ×20 credits.
For N = 3,000: 180,000 monthly actions → 2,160,000 annual → 43,200,000 action
credits/year (directional). Scale N for a smaller/larger band; rates unchanged.
```

- [ ] **Step 4: Wire the ref into Stage 18 (minimal, so the test's last assertion passes)**

This is completed fully in Task 2; for now add the load line so the test passes. In `refs/stages/stage-18-consumption-opportunities.md`, after the existing line `Load \`validation/consumption-checklist.md\`.` (line 9), add:

```markdown
Load `refs/consumption-estimation.md` (directional rate card + estimation model).
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -3`
Expected: `70/70 passed`.

- [ ] **Step 6: Commit**

```bash
cd /Users/bstauber/.claude/skills/pov-builder
git add refs/consumption-estimation.md refs/stages/stage-18-consumption-opportunities.md tests/validate_skill.py
git commit -m "feat(stage-18): add directional consumption rate-card ref + guard

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Refine Stage 18 instructions to produce the directional estimate

**Files:**
- Modify: `refs/stages/stage-18-consumption-opportunities.md`
- Modify: `tests/validate_skill.py` (add one `@check`)

- [ ] **Step 1: Write the failing test**

Add after the Task 1 check in `tests/validate_skill.py`:

```python
@check("Stage 18 instructs the directional estimate (anchored band, credits, no $)")
def t_stage18_directional_instructions():
    s = read("refs/stages/stage-18-consumption-opportunities.md")
    assert re.search(r"directional", s, re.I), "stage-18 missing directional-estimate instruction"
    assert re.search(r"sizing-band anchor|anchored band|anchor.*band", s, re.I), \
        "stage-18 missing the Sizing-Band Anchor instruction"
    assert re.search(r"U\s*[×x]\s*F\s*[×x]\s*A", s), "stage-18 missing the U×F×A volume formula"
    # boundary still credits-only: no dollar sizing produced here
    assert re.search(r"credits?, not (a )?dollar|no dollar|not produce.*dollar", s, re.I), \
        "stage-18 must keep the credits-only (no dollar) boundary"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | grep -A1 directional`
Expected: FAIL — `stage-18 missing directional-estimate instruction`.

- [ ] **Step 3: Edit the stage instructions**

In `refs/stages/stage-18-consumption-opportunities.md`, replace the boundary bullet about Flex Credit sizing. Find this exact line (line 14):

```markdown
- produce Flex Credit dollar sizing — that is the `sf-flex-estimator` skill. Give a qualitative "consumption signal" per opportunity and point to sf-flex-estimator for cost modeling.
```

Replace it with:

```markdown
- produce Flex Credit **dollar** sizing — that is the `sf-flex-estimator` skill. This stage may give a **directional, credits-only** pre-estimate (below) to seed the calculator, but never dollars/PUPM/contract pricing; point to sf-flex-estimator for authoritative cost modeling.
```

Then, immediately after the numbered mapping list (after the line `4. Rank all opportunities into the Consumption Opportunity Map table with a qualitative consumption signal each.`, line 20), insert this new section:

```markdown

**Directional consumption pre-estimate (credits only).** Using `refs/consumption-estimation.md`, add a directional estimate to **each Agentforce and Data Cloud opportunity**. This seeds the official calculator — it is not authoritative pricing.

1. **Sizing-Band Anchor.** Pick the single customer-size band (S/M/L/XL) that fits the POV's target customer. Write one anchor note (fills `{{SIZING_BAND_NOTE}}` in the templates) that: (a) names the band and why (e.g. "Typical targets fall into the M band; estimates below assume M"); (b) names the **scaling driver** — the `#Entities` unit (branches, hubs, sites, seats); (c) tells the reader to scale `#Entities` (and optionally U/F) for other bands. Bands are abstract — no reference entity-count ranges; the `#Entities` figure comes from the target customer or a stated assumption.
2. **Per Agentforce opportunity** — state the assumptions `U`, `F`, `A`, prompt count + tier, and `#Entities`; compute `U × F × A × #Entities` → monthly actions → ×12 annual → annual action credits (×20) + annual prompt credits (×2/4/16); express the result as a directional **credit band** (low–high). Note the sandbox 0.8 factor only if relevant.
3. **Per Data Cloud opportunity** — state the assumptions: data volume (millions of rows), run frequency (runs/year), and usage-type; compute `volume × frequency × multiplier` → directional annual **credit band**.
4. Keep every figure **directional and credits-only**. Show the assumptions so the reader can edit them in the real calculator. Do not output dollars.
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -3`
Expected: `71/71 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/bstauber/.claude/skills/pov-builder
git add refs/stages/stage-18-consumption-opportunities.md tests/validate_skill.py
git commit -m "feat(stage-18): instruct directional credits-only pre-estimate

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Extend the Markdown template with the anchor note + per-opportunity estimate

**Files:**
- Modify: `templates/consumption-opportunities.md`
- Modify: `tests/validate_skill.py` (add one `@check`)

- [ ] **Step 1: Write the failing test**

Add after the Task 2 check in `tests/validate_skill.py`:

```python
@check("Consumption MD template carries the anchor note + per-opportunity estimate fields")
def t_consumption_md_estimate_fields():
    md = read("templates/consumption-opportunities.md")
    assert "Sizing-Band Anchor" in md, "md template missing Sizing-Band Anchor note"
    assert re.search(r"Directional [Ee]stimate", md), "md template missing per-opportunity Directional Estimate block"
    assert re.search(r"U\s*[×x]\s*F\s*[×x]\s*A", md), "md template missing U×F×A assumptions line"
    assert re.search(r"credit", md, re.I), "md template missing credit-band field"
    # map table gains a directional-credits column
    assert re.search(r"Est\. credits|Directional credits", md), "md map table missing directional-credits column"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | grep -A1 "MD template"`
Expected: FAIL — `md template missing Sizing-Band Anchor note`.

- [ ] **Step 3: Edit the Markdown template**

In `templates/consumption-opportunities.md`:

**(a)** After the `**Scope:** ...` line and its following `---` (i.e. before `## Consumption Opportunity Map`), insert the anchor note:

```markdown
## Sizing-Band Anchor
**Target customer band:** [S | M | L | XL] — [why, e.g. "typical targets fall into the M band; estimates below assume M"]
**Scaling driver (#Entities):** [unit — e.g. branches / hubs / sites / seats] = [count or stated assumption]
> Estimates below are **directional and credits-only** — they seed the official calculator, they are not authoritative pricing (size with **sf-flex-estimator**). Bands are relative: to estimate another band, scale **#Entities** (and optionally U/F); the formulas are unchanged.

---
```

**(b)** Change the map table header row to add a directional-credits column. Find:

```markdown
| # | Opportunity | Type | Value driver | Priority | Consumption signal |
|---|-------------|------|--------------|----------|--------------------|
| 1 | [name] | Agent | [value] | [H/M/L] | [qualitative signal — e.g. "high-volume inference"] |
| 2 | [name] | Data | [value] | [H/M/L] | [qualitative signal — e.g. "large external ingest"] |
| 3 | [name] | SKU | [value] | [H/M/L] | [qualitative signal] |
```

Replace with:

```markdown
| # | Opportunity | Type | Value driver | Priority | Consumption signal | Est. credits/yr (directional) |
|---|-------------|------|--------------|----------|--------------------|-------------------------------|
| 1 | [name] | Agent | [value] | [H/M/L] | [qualitative signal — e.g. "high-volume inference"] | [low–high credits, or — for SKU rows] |
| 2 | [name] | Data | [value] | [H/M/L] | [qualitative signal — e.g. "large external ingest"] | [low–high credits] |
| 3 | [name] | SKU | [value] | [H/M/L] | [qualitative signal] | — |
```

**(c)** Add a Directional Estimate block to each Agent opportunity. Find the `### Agent Opportunity 1` block's `**Build steps:**` list and add, immediately after its three steps (before `### Agent Opportunity 2`):

```markdown
**Directional Estimate (credits only — [band] band):**
- Assumptions: U=[users/entity] × F=[runs/user/mo] × A=[actions/run] × #Entities=[count]; prompts=[n] @ [Basic 2 | Standard 4 | Advanced 16]
- Volume: [U×F×A×#Entities] actions/mo → [×12] actions/yr
- Credits/yr: [annual actions ×20] action + [annual prompts × tier] prompt = **[low–high] credits/yr** (directional; ×0.8 if sandbox)
```

Repeat the identical block (same field labels) after `### Agent Opportunity 2`'s build steps.

**(d)** Add a Directional Estimate block to each Data opportunity. After `### Data Opportunity 1`'s `**Build steps:**` three steps (before `### Data Opportunity 2`):

```markdown
**Directional Estimate (credits only — [band] band):**
- Assumptions: data volume=[M rows] × run frequency=[runs/yr] × usage-type=[type @ multiplier from rate card]
- Credits/yr: [volume × frequency × multiplier] = **[low–high] credits/yr** (directional; ×0.8 if sandbox)
```

Repeat the identical block after `### Data Opportunity 2`'s build steps.

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -3`
Expected: `72/72 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/bstauber/.claude/skills/pov-builder
git add templates/consumption-opportunities.md tests/validate_skill.py
git commit -m "feat(stage-18): add anchor note + directional estimate to MD template

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Extend the HTML template (one new scalar token + map column)

**Files:**
- Modify: `templates/consumption-opportunities.html`
- Modify: `tests/validate_skill.py` (add one `@check`)

- [ ] **Step 1: Write the failing test**

Add after the Task 3 check in `tests/validate_skill.py`:

```python
@check("Consumption HTML carries the sizing-band note token + directional-credits column")
def t_consumption_html_estimate():
    html = read("templates/consumption-opportunities.html")
    assert "{{SIZING_BAND_NOTE}}" in html, "html missing {{SIZING_BAND_NOTE}} token"
    # scalar token must appear exactly once (block-doubling guard covers _ROWS/_BLOCKS/_HTML;
    # this scalar must also not be duplicated in the token-reference comment as a fillable copy)
    assert html.count("{{SIZING_BAND_NOTE}}") == 1, "{{SIZING_BAND_NOTE}} must appear exactly once"
    # map table gained the directional-credits column header
    assert re.search(r"Est\. credits|Directional credits", html), "html map table missing directional-credits header"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | grep -A1 "HTML carries"`
Expected: FAIL — `html missing {{SIZING_BAND_NOTE}} token`.

- [ ] **Step 3: Edit the HTML template**

In `templates/consumption-opportunities.html`:

**(a)** After the `<div class="scope-note">…</div>` line (line 40) and its blank line, before `<h2>Consumption Opportunity Map</h2>`, insert the anchor-note token wrapped in the existing `scope-note` style:

```html
    <div class="scope-note">{{SIZING_BAND_NOTE}}</div>
```

**(b)** Add the directional-credits column to the map table header. Find (line 44):

```html
      <thead><tr><th>#</th><th>Opportunity</th><th>Type</th><th>Value driver</th><th>Priority</th><th>Consumption signal</th></tr></thead>
```

Replace with:

```html
      <thead><tr><th>#</th><th>Opportunity</th><th>Type</th><th>Value driver</th><th>Priority</th><th>Consumption signal</th><th>Est. credits/yr (directional)</th></tr></thead>
```

**(c)** Update the TOKEN REFERENCE comment block (lines 68–78) so the new scalar token is documented WITHOUT braces (the comment lists names brace-free by design). Find the line:

```
     PARTNER_NAME · GENERATED_DATE · OPPORTUNITY_STAGE · HOME_HREF
```

Replace with:

```
     PARTNER_NAME · GENERATED_DATE · OPPORTUNITY_STAGE · HOME_HREF · SIZING_BAND_NOTE
```

> Note: the per-opportunity directional estimate renders **inside** the existing `{{AGENT_BLOCKS}}` / `{{DATA_BLOCKS}}` injected content — the engine fills each `opp-block` with the estimate fields per the stage instructions. No new block token is added (keeps the block-doubling guard green). The `OPPORTUNITY_ROWS` injection now also supplies the extra `<td>` for the directional-credits column.

- [ ] **Step 4: Run the test to verify it passes (and the brace/doubling guards stay green)**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -3`
Expected: `73/73 passed`. (Confirms `t_braces_balanced`, `t_token_convention`, and `t_no_block_token_doubling` still pass with the new scalar token.)

- [ ] **Step 5: Commit**

```bash
cd /Users/bstauber/.claude/skills/pov-builder
git add templates/consumption-opportunities.html tests/validate_skill.py
git commit -m "feat(stage-18): add sizing-band token + credits column to HTML template

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Add validation-checklist guards

**Files:**
- Modify: `validation/consumption-checklist.md`
- Modify: `tests/validate_skill.py` (add one `@check`)

- [ ] **Step 1: Write the failing test**

Add after the Task 4 check in `tests/validate_skill.py`:

```python
@check("Consumption checklist guards the directional estimate (present, credits-only)")
def t_consumption_checklist_estimate_guards():
    cl = read("validation/consumption-checklist.md")
    assert re.search(r"Sizing-Band Anchor", cl), "checklist missing anchor-note check"
    assert re.search(r"directional", cl, re.I), "checklist missing directional-estimate check"
    assert re.search(r"assumption", cl, re.I), "checklist missing assumptions-shown check"
    # the no-dollar guard must still be present (now also covers the directional estimate)
    assert re.search(r"no dollar|NO dollar|never.*dollar|credits?-only", cl, re.I), \
        "checklist lost the no-dollar guard"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | grep -A1 "checklist guards"`
Expected: FAIL — `checklist missing anchor-note check`.

- [ ] **Step 3: Edit the checklist**

In `validation/consumption-checklist.md`, under the `## Structure` section, after the existing line about the Data Cloud section, add:

```markdown
- [ ] Sizing-Band Anchor note present: names the band, the reason, and the #Entities scaling driver
- [ ] Every Agentforce and Data Cloud opportunity has a Directional Estimate: assumptions (U/F/A/#Entities or volume/frequency/usage-type) → volume → credit band
- [ ] Directional estimates are credits-only and labeled directional; assumptions are shown so they can be edited in the real calculator
```

Then in the `## Scope discipline (no overlap)` section, change the existing dollar guard to cover the estimate too. Find:

```markdown
- [ ] "Consumption signal" entries are qualitative — NO dollar figures (sizing belongs to sf-flex-estimator)
```

Replace with:

```markdown
- [ ] No dollar figures anywhere — "Consumption signal" entries are qualitative and the Directional Estimate is credits-only (dollar/PUPM/contract sizing belongs to sf-flex-estimator)
```

Finally, in the `## Failure → Repair` section, after the existing `**Dollar figure in consumption signal:**` line, add:

```markdown
**Dollar figure in directional estimate:** Convert to a credit band; remove the dollar amount. Point to sf-flex-estimator for cost.
**Missing directional estimate on an Agent/Data opportunity:** Add the assumptions → volume → credit-band block per `refs/consumption-estimation.md`, or mark the assumptions `[TBD]` if the POV lacks the inputs.
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -3`
Expected: `74/74 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/bstauber/.claude/skills/pov-builder
git add validation/consumption-checklist.md tests/validate_skill.py
git commit -m "feat(stage-18): checklist guards for directional estimate

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Update SKILL.md (Stage 7 menu description + boundary line)

**Files:**
- Modify: `SKILL.md`
- Modify: `tests/validate_skill.py` (add one `@check`)

- [ ] **Step 1: Write the failing test**

Add after the Task 5 check in `tests/validate_skill.py`:

```python
@check("SKILL.md Stage 7 menu mentions the directional consumption pre-estimate")
def t_skill_menu_directional():
    s = read("SKILL.md")
    # the Consumption Opportunities menu option description should mention the directional pre-estimate
    m = re.search(r"Consumption Opportunities.*?\n.*?directional", s, re.S | re.I)
    assert m, "SKILL.md Consumption Opportunities menu option does not mention the directional pre-estimate"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | grep -A1 "menu mentions"`
Expected: FAIL — `SKILL.md Consumption Opportunities menu option does not mention the directional pre-estimate`.

- [ ] **Step 3: Edit SKILL.md**

In `SKILL.md`, find the "Consumption Opportunities" menu option description (lines 245–246):

```
          label: "Consumption Opportunities",
          description: "Build-oriented map of where Agentforce agents, Data Cloud, and other Salesforce SKUs (Shield, Backup, sandboxes) grow consumption — with named-component build blueprints per opportunity (Stage 18). Consumption-growth-scoped; points to sf-flex-estimator for cost sizing."
```

Replace the description string with:

```
          description: "Build-oriented map of where Agentforce agents, Data Cloud, and other Salesforce SKUs (Shield, Backup, sandboxes) grow consumption — with named-component build blueprints and a directional, credits-only consumption pre-estimate per opportunity to seed the calculator (Stage 18). Consumption-growth-scoped; authoritative dollar sizing stays with sf-flex-estimator."
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -3`
Expected: `75/75 passed`.

- [ ] **Step 5: Commit**

```bash
cd /Users/bstauber/.claude/skills/pov-builder
git add SKILL.md tests/validate_skill.py
git commit -m "docs(stage-18): mention directional pre-estimate in Stage 7 menu

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: Document the feature in README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Find the Stage 18 documentation in the README**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && grep -n "Consumption Opportunities\|Stage 18" README.md`
Expected: one or more line numbers where Stage 18 is described.

- [ ] **Step 2: Add a sentence describing the directional pre-estimate**

At the Stage 18 description location found in Step 1, append to that paragraph (preserve surrounding prose; match its style):

```markdown
As of 2026-06-08, each Agentforce and Data Cloud opportunity also carries a **directional, credits-only consumption pre-estimate** anchored to a single customer-size band (S/M/L/XL), with the U/F/A and entity-count assumptions shown so the figures can be carried into the official Agentforce Credit Estimator / Data 360 calculator. Rates live in `refs/consumption-estimation.md`. This seeds the calculator; authoritative dollar sizing stays with the `sf-flex-estimator` skill.
```

- [ ] **Step 3: Run the full suite (README changes can affect the README-coverage checks)**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -3`
Expected: `75/75 passed` (no new check; README edit must not break existing ones).

- [ ] **Step 4: Commit**

```bash
cd /Users/bstauber/.claude/skills/pov-builder
git add README.md
git commit -m "docs: document Stage 18 directional consumption pre-estimate

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: Full-suite verification + parallel-dispatch sanity

**Files:**
- Read-only verification (no edits expected; fix-forward if a check fails)

- [ ] **Step 1: Run the entire validation suite**

Run: `cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py`
Expected: `75/75 passed`, exit 0.

- [ ] **Step 2: Confirm the no-orphan + ref-exists checks cover the new ref**

The new `refs/consumption-estimation.md` is a top-level `refs/` file. Confirm it is referenced by the instruction corpus (it is loaded in Stage 18) so `t_no_orphans` passes — already covered by Task 1 Step 4. Run:

`cd /Users/bstauber/.claude/skills/pov-builder && grep -rn "consumption-estimation.md" refs/stages/ SKILL.md`
Expected: at least one hit in `refs/stages/stage-18-consumption-opportunities.md`.

- [ ] **Step 3: Confirm parallel-dispatch still treats Stage 18 as a Wave-1 artifact**

No change needed (the directional estimate is produced inline within Stage 18, not a new stage). Confirm the existing dispatch check still passes:

`cd /Users/bstauber/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | grep -i "Stage 18"`
Expected: `PASS  Parallel dispatch includes Stage 18 (Consumption) in Wave 1`.

- [ ] **Step 4: Final commit (only if Steps 1–3 required any fix)**

If everything passed with no edits, there is nothing to commit — the feature is complete. If a fix was needed:

```bash
cd /Users/bstauber/.claude/skills/pov-builder
git add -A
git commit -m "fix(stage-18): resolve validation gap surfaced in final verification

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage:**
- Rate card (action/prompt rules, Data 360 meters, sandbox, method, abstract bands, synthetic example) → Task 1 ✓
- Stage 18 boundary refinement + estimation steps → Task 2 ✓
- MD template (anchor note, per-opportunity estimate, map column) → Task 3 ✓
- HTML template (scalar token, map column) → Task 4 ✓
- Checklist guards (present, credits-only, assumptions) → Task 5 ✓
- SKILL.md menu + boundary → Task 6 ✓
- README → Task 7 ✓
- `tests/validate_skill.py` structural assertions → one per Task 1–6 ✓
- Full verification → Task 8 ✓
- Credits-only (no $), single anchored band, abstract bands (no ranges), anonymous → enforced in Tasks 1/2/3/5 content and asserted in Tasks 2/5 ✓

**Placeholder scan:** No "TBD/TODO/handle appropriately" in the plan steps. The `[bracketed]` items inside template/checklist *content* are intentional fill-in tokens for the LLM at runtime (that is what a template is), not plan placeholders.

**Type/name consistency:** Token `{{SIZING_BAND_NOTE}}` named identically in Task 2 (instructions), Task 3 (MD reference), Task 4 (HTML). Column header text "Est. credits/yr (directional)" identical in Task 3(b) and Task 4(b); the test in Task 3/4 accepts `Est. credits|Directional credits` so both are safe. Check-name strings are unique. Suite count rises 69 → 75 (one check per Task 1–6), stated consistently in each task's expected output.
