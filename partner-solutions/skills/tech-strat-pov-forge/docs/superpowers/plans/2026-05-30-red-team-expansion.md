# Red Team Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand pov-builder's Stage 9 Red Team from 4 adversarial frameworks to 6 (adding Salesforce Investment Teardown and Commercial Model Pressure Test) plus a Biggest Blind Spot element in the synthesis.

**Architecture:** Documentation/template skill validated by `tests/validate_skill.py` (Python 3 stdlib structural checks) with a pre-commit hook that blocks failing commits. The Red Team is Markdown-native: it has a lenses reference (`refs/red-team-lenses.md`), a Markdown template (`templates/red-team-assessment.md` — no `{{TOKEN}}` placeholders; rendered to HTML via `scripts/md-to-html.py` + document-shell at Stage 13), a checklist, and a stage instruction file. The new validator check `t_red_team_frameworks` keeps the three core red-team files (lenses, template, checklist) in sync — so those three changes plus the check land together in one commit (the check is RED until all three carry the new framework names). TDD: add the check (RED), make the three files satisfy it (GREEN), commit; then peripheral wiring (stage doc, SKILL menu, README) in follow-up tasks.

**Tech Stack:** Markdown instruction/template files, Python 3 stdlib validator, git + pre-commit hook.

---

## File Structure

- `refs/red-team-lenses.md` — adversarial lens definitions; add Framework 5 + 6, update intro count.
- `templates/red-team-assessment.md` — Markdown output template; add Framework 5 + 6 sections + Biggest Blind Spot in Synthesis.
- `validation/red-team-checklist.md` — pre-delivery checks; update framework list to 6, add specificity + blind-spot checks.
- `refs/stages/stage-09-red-team.md` — stage instructions; "4 frameworks" → "6 frameworks", add lines 5+6, note Biggest Blind Spot.
- `SKILL.md` — Red Team menu option description: add the two new lens names.
- `README.md` — Red Team row + repo-tree comment: "4" → "6 adversarial frameworks".
- `tests/validate_skill.py` — new `t_red_team_frameworks` check.

**Conventions to match:**
- The existing 4 lenses in `refs/red-team-lenses.md` each have: `## Framework N: Name`, an **Adversarial role**, attack vectors/categories, and an **Output contract — must produce** numbered list. Match that structure exactly for 5 and 6.
- Ground-rule on named entities: "Named competitors must be real — if none known, write 'No verified comparable identified — flag as TBD'." Framework 5's named-failure element must honor this.
- The template's existing frameworks use `## Framework N: Name` headings with bold field labels and `[bracket]` fill guides; no `{{TOKEN}}` placeholders (it's Markdown-native).
- Run validator: `python3 tests/validate_skill.py` from skill root. Branch: `red-team-expansion`. All work under `/Users/bstauber/.claude/skills/pov-builder`.

---

## Task 1: Add Frameworks 5 & 6 to the lenses, template, checklist + validator (one commit)

**Files:**
- Modify: `refs/red-team-lenses.md`
- Modify: `templates/red-team-assessment.md`
- Modify: `validation/red-team-checklist.md`
- Modify: `tests/validate_skill.py`

These four change together because the new validator check is RED until the three content files all carry the new framework names. Make ONE commit at the end when the validator is GREEN.

- [ ] **Step 1: Write the failing validator check**

Add to `tests/validate_skill.py`, near the other multi-file-parity checks (e.g. after the discovery dimension-parity check `t_discovery_dimension_parity`, search for it). Use the existing `@check` decorator and `read()` helper:

```python
@check("Red team lenses, template, and checklist list the same 6 frameworks")
def t_red_team_frameworks():
    lenses = read("refs/red-team-lenses.md")
    template = read("templates/red-team-assessment.md")
    checklist = read("validation/red-team-checklist.md")
    for name in ("Salesforce Investment Teardown", "Commercial Model Pressure Test"):
        assert name in lenses, f"red-team-lenses.md missing framework '{name}'"
        assert name in template, f"red-team-assessment.md missing framework '{name}'"
        assert name in checklist, f"red-team-checklist.md missing framework '{name}'"
    assert "## Framework 5:" in template, "template missing '## Framework 5:' heading"
    assert "## Framework 6:" in template, "template missing '## Framework 6:' heading"
    assert "Biggest Blind Spot" in template, "template Synthesis missing 'Biggest Blind Spot'"
    assert "6 frameworks" in checklist, "checklist does not say '6 frameworks'"
    assert "4 frameworks" not in checklist, "checklist still says '4 frameworks'"
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL — `Red team lenses, template, and checklist list the same 6 frameworks` (red-team-lenses.md missing framework 'Salesforce Investment Teardown'). Count drops one (e.g. 42/43).

- [ ] **Step 3: Add Framework 5 & 6 to `refs/red-team-lenses.md`**

First update the intro line. Find:
`Four adversarial frameworks adapted for ISV partner evaluation in the Salesforce OG Tech Strategy Framework.`
Replace with:
`Six adversarial frameworks adapted for ISV partner evaluation in the Salesforce OG Tech Strategy Framework.`

Then, after the `## Framework 4: 18-Month Invalidation Scenarios` section (which ends just before the file ends — append at the end of the file), add:

```markdown

---

## Framework 5: Salesforce Investment Teardown

**Adversarial role:** You are the Salesforce investment committee / GTP review board. You have seen many ISV partner pitches and you are looking for reasons to **pass** on committing OG Tech Strategy Framework resources to this one. You are not the partner's market competitor — you are the internal funder deciding whether this partnership earns Salesforce's investment.

**Attack vectors to consider:**
- **Thin proof:** No named pilot, no reference account willing to go on record, KPIs that are targets not results
- **Undifferentiated bet:** The partner's value could be replicated by three other ISVs in the same vertical, or by Salesforce natively
- **Commercial fragility:** The pull-through case rests on assumptions the install base does not support (see also Framework 6)
- **Execution doubt:** The team cannot demonstrably build and support at the scale of the enterprise prospects named in the POV
- **Precedent of failure:** A comparable ISV pursued this exact play and did not make it — and the same mechanism could repeat here

**Output contract — must produce:**
1. The 3 biggest holes in the partner case that would justify a "no" — specific, not "needs more traction"
2. The single question the partner most likely cannot answer yet (the one that ends the meeting)
3. A **named comparable ISV that attempted this and failed** (real, from research) and the specific failure mechanism that could repeat here. If no verified comparable is known, write "No verified comparable identified — flag as TBD" and state what kind of precedent would need checking.

---

## Framework 6: Commercial Model Pressure Test

**Adversarial role:** You are a skeptic attacking the partner's commercial and pull-through model. You accept the product works — you do not accept that the money works. Your job is to find where the commercial premise breaks.

**Attack vectors to consider:**
- **Pull-through math break:** The point where the pull-through revenue case collapses — a price point, an attach-rate assumption, or a Salesforce edition/SKU the target install base does not already own
- **Revenue-share viability:** Whether the PADA / revenue-share economics are real at the partner's actual scale, or only work at a customer count they do not have
- **Buyer alternative:** A cheaper competitor, a Salesforce-native path, or "do nothing" that makes the partner's commercial premise hard to defend to a budget-constrained buyer
- **Edition dependency:** If the solution requires Enterprise/Unlimited edition or specific add-on SKUs, is that already in the target customer's stack — or is it a hidden cost that shrinks the real TAM?

**Output contract — must produce:**
1. The specific point where the pull-through math breaks — name the price point, attach-rate, or edition/SKU dependency (not "pricing is risky")
2. Revenue-share viability verdict: at what customer count / ACV does the PADA economics actually work, and does the partner have it?
3. One named alternative (cheaper competitor, Salesforce-native path, or do-nothing) that makes the partner's commercial premise hard to defend — and the one change that would make the model defensible
```

- [ ] **Step 4: Add Framework 5 & 6 sections + Biggest Blind Spot to `templates/red-team-assessment.md`**

The template currently ends Framework 4 (with Scenarios A/B/C) then has `## Synthesis: Top Vulnerabilities & Recommended Actions`. Insert two new framework sections BETWEEN the end of Framework 4 and the `## Synthesis` heading:

```markdown
## Framework 5: Salesforce Investment Teardown

[Adversarial role: the Salesforce investment committee looking for reasons to pass.]

**Three biggest holes (a "no" rests on these):**
1. [Specific hole — not "needs traction"]
2. [Specific hole]
3. [Specific hole]

**The question the partner can't answer yet:** [The single meeting-ending question]

**Named comparable that tried this and failed:** [Real named ISV + the specific failure mechanism that could repeat here — or "No verified comparable identified — flag as TBD" with what precedent to check]

---

## Framework 6: Commercial Model Pressure Test

[Adversarial role: a skeptic who accepts the product works but attacks whether the money works.]

**Where the pull-through math breaks:** [Specific price point, attach-rate assumption, or edition/SKU dependency the target install base lacks]

**Revenue-share viability:** [At what customer count / ACV the PADA economics actually work, and whether the partner has it]

**Buyer's best alternative:** [Named cheaper competitor / Salesforce-native path / do-nothing that undercuts the commercial premise] — **the one change that makes the model defensible:** [specific change]

---

```

Then, in the `## Synthesis` section, add a **Biggest Blind Spot** line. Insert it immediately after the `**Governing finding:**` line and before the vulnerability table:

```markdown
**Biggest Blind Spot:** [The one risk that sits outside the partner's normal frame and was NOT surfaced by Frameworks 1–6 — something they are almost certainly not thinking about. Must not restate a finding already in the table.]
```

- [ ] **Step 5: Update `validation/red-team-checklist.md`**

Find the structure check line:
`- [ ] All 4 frameworks present: Competitive War Game, Customer Exit Simulation, Platform Dependency Scan, 18-Month Invalidation Scenarios`
Replace with:
`- [ ] All 6 frameworks present: Competitive War Game, Customer Exit Simulation, Platform Dependency Scan, 18-Month Invalidation Scenarios, Salesforce Investment Teardown, Commercial Model Pressure Test`

In the "## Specificity" section, add two checks:
```markdown
- [ ] Salesforce Investment Teardown names a real comparable ISV that failed (or explicitly flags "No verified comparable identified — flag as TBD") — not a hypothetical
- [ ] Commercial Model Pressure Test names the specific break point (price point, attach-rate, or edition/SKU dependency) — not "pricing is a risk"
```

In the "## Structure" section (near the Synthesis/Stopping-Rule checks), add:
```markdown
- [ ] Synthesis includes a **Biggest Blind Spot** — a risk not surfaced by any of Frameworks 1–6 (not a restatement of a table row)
```

- [ ] **Step 6: Run the validator to verify GREEN + commit**

Run: `python3 tests/validate_skill.py`
Expected: PASS — `Red team lenses, template, and checklist list the same 6 frameworks`, and all existing checks still pass (count = prior 42 + 1 = 43).

Also confirm the red team template still has no `{{TOKEN}}` placeholders introduced (it's Markdown-native):
Run: `grep -c '{{' templates/red-team-assessment.md`
Expected: `0`

Commit:
```bash
git add refs/red-team-lenses.md templates/red-team-assessment.md validation/red-team-checklist.md tests/validate_skill.py
git commit -m "Red team: add Framework 5 (Investment Teardown) + 6 (Commercial Model Pressure Test) + Biggest Blind Spot"
```

---

## Task 2: Update the Stage 9 instructions

**Files:**
- Modify: `refs/stages/stage-09-red-team.md`

- [ ] **Step 1: Update the framework run-list**

In `refs/stages/stage-09-red-team.md`, find:
```
Run all 4 frameworks in sequence:
1. Competitive War Game — who steals this partner's customers in 12–18 months
2. Customer Exit Simulation — why the Salesforce platform owner / VP of CRM stops using this solution after 6 months
3. Platform Dependency Scan — single points of failure in the Salesforce ISV context
4. 18-Month Invalidation Scenarios — 3 specific scenarios that make this solution obsolete
```
Replace with:
```
Run all 6 frameworks in sequence:
1. Competitive War Game — who steals this partner's customers in 12–18 months
2. Customer Exit Simulation — why the Salesforce platform owner / VP of CRM stops using this solution after 6 months
3. Platform Dependency Scan — single points of failure in the Salesforce ISV context
4. 18-Month Invalidation Scenarios — 3 specific scenarios that make this solution obsolete
5. Salesforce Investment Teardown — why the Salesforce investment committee would pass; force a named comparable ISV that tried this and failed
6. Commercial Model Pressure Test — where the pull-through math and revenue-share viability break
```

- [ ] **Step 2: Note the Biggest Blind Spot in the deliver list**

Find the "Deliver:" list near the end. After the "Surface the Synthesis section's top vulnerabilities..." bullet, add:
```markdown
- The Synthesis must include a **Biggest Blind Spot** — a risk not surfaced by any of the 6 frameworks
```

- [ ] **Step 3: Verify heading intact + validator**

Run: `grep -c '^\*\*Stage 9 —' refs/stages/stage-09-red-team.md`
Expected: `1` (load-bearing heading — do not alter).
Run: `python3 tests/validate_skill.py`
Expected: all pass (43).

- [ ] **Step 4: Commit**

```bash
git add refs/stages/stage-09-red-team.md
git commit -m "Stage 9 instructions: 6 frameworks + Biggest Blind Spot"
```

---

## Task 3: Update the SKILL.md menu option + README

**Files:**
- Modify: `SKILL.md`
- Modify: `README.md`

- [ ] **Step 1: Update the Red Team menu option description**

In `SKILL.md`, find the Red Team Assessment menu option description:
`"Adversarial analysis: competitive threats, customer churn scenarios, platform dependency scan, and 18-month invalidation scenarios (Stage 9)"`
Replace with:
`"Adversarial analysis: competitive threats, customer churn scenarios, platform dependency scan, 18-month invalidation, Salesforce investment teardown, and commercial model pressure test (Stage 9)"`

- [ ] **Step 2: Update the README Red Team row**

In `README.md`, find the Red Team Assessment table row containing `(4 adversarial frameworks — competitive war game, customer-exit simulation, platform-dependency scan, 18-month invalidation — plus synthesis & stopping rule)`. Replace that parenthetical with:
`(6 adversarial frameworks — competitive war game, customer-exit simulation, platform-dependency scan, 18-month invalidation, Salesforce investment teardown, commercial-model pressure test — plus synthesis with blind spot & stopping rule)`

- [ ] **Step 3: Update the README repo-tree comment**

In `README.md`, find the tree comment line:
`│   ├── red-team-lenses.md            # 4 adversarial frameworks`
Replace `# 4 adversarial frameworks` with `# 6 adversarial frameworks`.

- [ ] **Step 4: Verify + commit**

Run: `grep -c '4 adversarial frameworks' README.md`
Expected: `0` (both updated).
Run: `python3 tests/validate_skill.py`
Expected: all pass (43).
Commit:
```bash
git add SKILL.md README.md
git commit -m "Red team: update menu option + README to 6 frameworks"
```

---

## Task 4: Final verification

**Files:** none (verification only)

- [ ] **Step 1: Full validator run**

Run: `python3 tests/validate_skill.py`
Expected: ALL pass, count = 43 (prior 42 + `t_red_team_frameworks`).

- [ ] **Step 2: Cross-file consistency sweep**

```bash
cd /Users/bstauber/.claude/skills/pov-builder
echo "lenses framework count line:"; grep -c 'Six adversarial frameworks' refs/red-team-lenses.md
echo "template framework headings (expect 6):"; grep -c '^## Framework [0-9]' templates/red-team-assessment.md
echo "stale '4 framework' anywhere (expect 0):"; grep -rc '4 framework\|Four adversarial\|all 4 framework' refs/ validation/ templates/ SKILL.md README.md refs/stages/ 2>/dev/null | grep -v ':0' || echo "none"
echo "Biggest Blind Spot present in template + checklist + stage doc:"; grep -l 'Biggest Blind Spot' templates/red-team-assessment.md validation/red-team-checklist.md refs/stages/stage-09-red-team.md
```
Expected: lenses count 1; template framework headings 6; no stale "4 framework" matches; Biggest Blind Spot in all three files.

- [ ] **Step 3: No commit needed** (verification only — if any check fails, return to the relevant task).

---

## Self-Review Checklist

- [ ] **Spec coverage:** Framework 5 (T1), Framework 6 (T1), Biggest Blind Spot (T1 template + T2 stage doc + T1 checklist), lenses intro count (T1), stage doc run-list (T2), checklist (T1), SKILL menu (T3), README ×2 (T3), validator check (T1). All spec sections mapped.
- [ ] **Placeholder scan:** all content shown verbatim; `[bracket]` items in the template are intentional fill-guides matching the existing template style, not plan placeholders.
- [ ] **Name consistency:** "Salesforce Investment Teardown" and "Commercial Model Pressure Test" used identically across lenses, template, checklist, stage doc, validator check, SKILL menu, README. "Biggest Blind Spot" consistent. Check name `t_red_team_frameworks` unique.
- [ ] **Validator count:** 42 → 43 (1 new check in T1).
- [ ] **Markdown-native confirmed:** no `{{TOKEN}}` work; red team HTML renders via document-shell at Stage 13 (unchanged).
