# Parallel-Instruction-Files Performance Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modularize the pov-builder downstream-output monolith into per-stage instruction files and add surgical concurrent-subagent dispatch at the Stage 8–16 fan-out, optimizing both token utilization and wall-clock latency.

**Architecture:** Split `refs/output-stages.md` into one self-contained file per stage under `refs/stages/`, loaded selectively. SKILL.md's stage list becomes a router. A new lazily-loaded `refs/parallel-dispatch.md` defines a dispatch protocol — a ≥3-downstream-artifact threshold, a compact-POV payload per subagent, dependency-aware waves (Stage 16 → Stage 8; Stage 13 home page last), and graceful fallback to sequential when no subagent capability exists. The structural validator (`tests/validate_skill.py`) is rewired so its instruction corpus spans SKILL.md + the new stage files, plus four new invariant checks (24 → 28).

**Tech Stack:** Markdown instruction files; Python 3 stdlib validator (`tests/validate_skill.py`); git with a tracked pre-commit hook (`.githooks/pre-commit`) that runs the validator on every commit.

---

## Context for the implementer (read first)

- This skill is an **instruction corpus**, not application code. "Tests" are the structural-invariant checks in `tests/validate_skill.py`. The TDD rhythm is: add/modify a check → run it and watch it fail (RED) → make the structural change → run and watch it pass (GREEN) → commit.
- **Run the validator** anytime with: `python3 tests/validate_skill.py` (exit 0 = all pass). The pre-commit hook runs it automatically and **blocks** failing commits. If the hook isn't active in a fresh clone, activate once: `git config core.hooksPath .githooks`.
- The validator's `instructions()` helper joins `INSTRUCTION_FILES` into one string. Many checks (`t_stage_contiguous`, `t_menu_stage_refs`, `t_refs_exist`, `t_no_orphans`) operate on that joined corpus. **Keeping the corpus complete across the split is the central risk** — this plan sequences edits so the suite stays green at every commit.
- Current downstream-stage source content lives in `refs/output-stages.md`. Each stage is a block beginning with a bold heading line `**Stage N — …**`. You will move these blocks **verbatim** into per-stage files.
- The branch `parallel-instruction-files` already exists and holds the design spec commit. Work on it.

**Stage → new-file name map (use these exact paths):**

| Stage | New file |
|---|---|
| 8  | `refs/stages/stage-08-mvp-build-plan.md` |
| 9  | `refs/stages/stage-09-red-team.md` |
| 10 | `refs/stages/stage-10-investor-presentation.md` |
| 11 | `refs/stages/stage-11-solution-infographic.md` |
| 12 | `refs/stages/stage-12-partner-readiness-scorecard.md` |
| 13 | `refs/stages/stage-13-output-home-page.md` |
| 14 | `refs/stages/stage-14-marketecture.md` |
| 15 | `refs/stages/stage-15-discovery-framework.md` |
| 16 | `refs/stages/stage-16-architecture-assessment.md` |

---

## Task 1: Split the monolith into `refs/stages/` (checks-first)

**Files:**
- Modify: `tests/validate_skill.py` (add two checks)
- Create: all nine `refs/stages/stage-*.md` files (see map above)
- Modify: `SKILL.md` (add the router block; existing lines 261–262)

- [ ] **Step 1: Write the two new failing checks**

Add these two checks to `tests/validate_skill.py`. Place them after `t_well_architected_parity` (around line 160), and add the supporting constant near the other module-level lists (after `ARCH_FILES`, ~line 119):

```python
# ---- 1e. stage-file architecture integrity ------------------------------
# The downstream optional stages (8-16) each live in their own file under
# refs/stages/; SKILL.md's router must point to each, bidirectionally.
DOWNSTREAM_STAGES = {
    8:  "refs/stages/stage-08-mvp-build-plan.md",
    9:  "refs/stages/stage-09-red-team.md",
    10: "refs/stages/stage-10-investor-presentation.md",
    11: "refs/stages/stage-11-solution-infographic.md",
    12: "refs/stages/stage-12-partner-readiness-scorecard.md",
    13: "refs/stages/stage-13-output-home-page.md",
    14: "refs/stages/stage-14-marketecture.md",
    15: "refs/stages/stage-15-discovery-framework.md",
    16: "refs/stages/stage-16-architecture-assessment.md",
}
```

```python
@check("SKILL.md router and refs/stages/ are in bidirectional sync (stages 8-16)")
def t_stage_router_parity():
    skill = read("SKILL.md")
    on_disk = {f"refs/stages/{f}" for f in os.listdir(os.path.join(SKILL, "refs/stages"))
               if f.endswith(".md")}
    expected = set(DOWNSTREAM_STAGES.values())
    missing_files = sorted(expected - on_disk)          # router maps a stage to a missing file
    orphan_files  = sorted(on_disk - expected)          # stage file not in the canonical map
    assert not missing_files, f"router stages with no file on disk: {missing_files}"
    assert not orphan_files, f"refs/stages files absent from the stage map: {orphan_files}"
    not_routed = sorted(p for p in expected if p not in skill)  # file exists but SKILL.md never links it
    assert not not_routed, f"stage files not referenced by the SKILL.md router: {not_routed}"

@check("Every refs/stages/ file carries its '**Stage N —' heading")
def t_stage_file_schema():
    bad = {}
    for n, rel in DOWNSTREAM_STAGES.items():
        if not exists(rel):
            bad[rel] = "missing file"; continue
        if not re.search(rf"^\*\*Stage {n} ", read(rel), re.M):
            bad[rel] = f"no '**Stage {n} ' heading"
    assert not bad, f"stage files failing schema: {bad}"
```

- [ ] **Step 2: Run the suite and confirm the two new checks FAIL**

Run: `python3 tests/validate_skill.py`
Expected: FAIL on `t_stage_router_parity` and `t_stage_file_schema` (the `refs/stages` directory does not exist yet — an `os.listdir` `FileNotFoundError` surfaces as ERROR, which is also non-passing). The other 24 checks still PASS. The summary line reads `24/26 passed` or shows ERRORs for the two new ones.

> If `os.listdir` raising `FileNotFoundError` bothers you, that's expected for this RED step — it goes away in Step 3 once the directory exists.

- [ ] **Step 3: Create the nine stage files (verbatim content move)**

Create `refs/stages/` and, for each stage, create its file. Each file starts with this two-line header, then the stage's block copied **verbatim** from `refs/output-stages.md`:

Header template (substitute N and the title):
```markdown
# Stage N — <Title>

> Optional output stage, lazily loaded by pov-builder. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles + HTML Output Method in `SKILL.md`.

```

Then paste the corresponding block from `refs/output-stages.md` **exactly as written**, preserving the bold `**Stage N — …**` heading line and all body text:
- Stage 8 → the block from `**Stage 8 — Generate MVP Build Plan (optional)**` up to (not including) `**Stage 9 —`.
- Stage 9 → `**Stage 9 — Red Team Assessment (optional)**` up to `**Stage 10 —`.
- Stage 10 → `**Stage 10 — Investor Presentation (optional)**` up to `**Stage 11 —`.
- Stage 11 → `**Stage 11 — Solution Infographic (optional)**` up to `**Stage 12 —`.
- Stage 12 → `**Stage 12 — Partner Readiness Scorecard (optional)**` up to `**Stage 13 —`.
- Stage 13 → `**Stage 13 — Output Home Page / Solution Package (optional)**` up to `**Stage 14 —`.
- Stage 14 → `**Stage 14 — Marketecture (optional)**` up to `**Stage 15 —`.
- Stage 15 → `**Stage 15 — Discovery Framework (optional)**` up to `**Stage 16 —`.
- Stage 16 → `**Stage 16 — Technical & Architectural Assessment (optional)**` through end of file.

Do **not** edit the block text in this step — a pure relocation keeps the diff reviewable. (`refs/output-stages.md` itself is removed in Task 2, not here.)

- [ ] **Step 4: Add the router block to SKILL.md**

In `SKILL.md`, replace the existing stage list (currently the last two bullet lines, ~261–262):

```markdown
- **Stage 8** — MVP Build Plan · **Stage 9** — Red Team Assessment · **Stage 10** — Investor Presentation
- **Stage 11** — Solution Infographic · **Stage 12** — Partner Readiness Scorecard · **Stage 13** — Output Home Page / Solution Package · **Stage 14** — Marketecture · **Stage 15** — Discovery Framework · **Stage 16** — Technical & Architectural Assessment
```

with this router table:

```markdown
| Stage | Output | Instruction file |
|---|---|---|
| 8  | MVP Build Plan | `refs/stages/stage-08-mvp-build-plan.md` |
| 9  | Red Team Assessment | `refs/stages/stage-09-red-team.md` |
| 10 | Investor Presentation | `refs/stages/stage-10-investor-presentation.md` |
| 11 | Solution Infographic | `refs/stages/stage-11-solution-infographic.md` |
| 12 | Partner Readiness Scorecard | `refs/stages/stage-12-partner-readiness-scorecard.md` |
| 13 | Output Home Page / Solution Package | `refs/stages/stage-13-output-home-page.md` |
| 14 | Marketecture | `refs/stages/stage-14-marketecture.md` |
| 15 | Discovery Framework | `refs/stages/stage-15-discovery-framework.md` |
| 16 | Technical & Architectural Assessment | `refs/stages/stage-16-architecture-assessment.md` |
```

Leave line 259's "load `refs/output-stages.md`" wording untouched for now (Task 2 rewires it). At this point both `refs/output-stages.md` and the stage files exist — the corpus is unchanged, so the other checks stay green.

- [ ] **Step 5: Run the suite and confirm 26/26**

Run: `python3 tests/validate_skill.py`
Expected: PASS all 26 (the two new checks now pass; the original 24 unaffected). Summary: `26/26 passed`.

- [ ] **Step 6: Commit**

```bash
git add tests/validate_skill.py refs/stages/ SKILL.md
git commit -m "Split downstream stages into refs/stages/ + router + parity checks"
```

---

## Task 2: Cut the corpus over to the stage files; remove the monolith

**Files:**
- Modify: `tests/validate_skill.py` (`INSTRUCTION_FILES` definition, ~line 33)
- Modify: `SKILL.md` (line ~259 load instruction; line ~257 parallel-execution note)
- Delete: `refs/output-stages.md`

- [ ] **Step 1: Make `INSTRUCTION_FILES` span SKILL.md + the stage files**

In `tests/validate_skill.py`, replace the static definition (~line 31–35):

```python
# SKILL.md + the lazily-loaded optional-output stage definitions form one
# instruction corpus; reference/stage checks must span both.
INSTRUCTION_FILES = ["SKILL.md", "refs/output-stages.md"]
def instructions():
    return "\n".join(read(f) for f in INSTRUCTION_FILES if exists(f))
```

with a computed corpus that includes every `refs/stages/` file:

```python
# SKILL.md (core flow) + every per-stage file under refs/stages/ form one
# instruction corpus; reference/stage checks must span all of them.
def _instruction_files():
    files = ["SKILL.md"]
    stages_dir = os.path.join(SKILL, "refs/stages")
    if os.path.isdir(stages_dir):
        files += sorted(f"refs/stages/{f}" for f in os.listdir(stages_dir) if f.endswith(".md"))
    return files
INSTRUCTION_FILES = _instruction_files()
def instructions():
    return "\n".join(read(f) for f in INSTRUCTION_FILES if exists(f))
```

- [ ] **Step 2: Run the suite — still green (content is duplicated right now)**

Run: `python3 tests/validate_skill.py`
Expected: PASS 26/26. The corpus now contains stages 8–16 from the stage files (and `refs/output-stages.md`, still present and still referenced by SKILL.md line 259, is not an orphan). `t_stage_contiguous` sees 1..16.

- [ ] **Step 3: Rewire SKILL.md to selective-load and drop the monolith reference**

In `SKILL.md`, find the optional-stages loader paragraph (currently ~line 259):

```markdown
**Stages 8–16 — Optional outputs (lazily loaded).** Their full definitions live in `refs/output-stages.md` — keeping them out of the base context. When the user selects any option from the menu above, or asks for an output by name, **load `refs/output-stages.md`** and follow the matching stage:
```

Replace with:

```markdown
**Stages 8–16 — Optional outputs (lazily loaded).** Each stage's full definition lives in its own file under `refs/stages/` (see the router table below) — keeping them out of the base context. When the user selects any option from the menu above, or asks for an output by name, **load only the matching `refs/stages/stage-NN-*.md` file(s)** for the selected output(s) and follow them. Load only what was selected — never the whole set.
```

Then update the "Parallel execution note" paragraph (currently ~line 257) so it no longer implies a single agent runs them simultaneously inline, and points to the dispatch protocol added in Task 3:

```markdown
**Parallel execution.** Stages 8, 9, 10, 11, 12, 14, and 16 are independent artifact generators that all draw from the same approved POV. When **3 or more** of them are requested together (e.g. "All outputs + home page"), do not generate them sequentially — load `refs/parallel-dispatch.md` and fan them out to concurrent subagents per that protocol. For 1–2 artifacts, generate inline sequentially. Stage 16 (Architectural Assessment) feeds the MVP Build Plan (Stage 8), so when both run it goes first. Stage 13 (home page) always runs **last**, after the artifacts it links exist. Stage 15 (Discovery) is an upstream refinement — it runs as its own separate pass, never inside the concurrent waves.
```

Confirm no remaining literal reference to `refs/output-stages.md` exists in `SKILL.md` (search for it). There must be none.

- [ ] **Step 4: Run the suite — confirm the monolith is now flagged as an orphan (RED)**

Run: `python3 tests/validate_skill.py`
Expected: FAIL on `t_no_orphans` → `present but never referenced: ['refs/output-stages.md']`. This RED confirms the cutover is complete: nothing references the monolith anymore.

- [ ] **Step 5: Delete the monolith**

```bash
git rm refs/output-stages.md
```

- [ ] **Step 6: Run the suite — back to green**

Run: `python3 tests/validate_skill.py`
Expected: PASS 26/26.

- [ ] **Step 7: Commit**

```bash
git add tests/validate_skill.py SKILL.md
git commit -m "Cut instruction corpus over to refs/stages/; remove output-stages.md monolith"
```

---

## Task 3: Dispatch protocol file + SKILL pointer (two new checks)

**Files:**
- Modify: `tests/validate_skill.py` (two new checks)
- Create: `refs/parallel-dispatch.md`
- Modify: `SKILL.md` (Stage 7 dispatch pointer)

- [ ] **Step 1: Write the two new failing checks**

Add to `tests/validate_skill.py`, after `t_stage_file_schema`:

```python
@check("refs/parallel-dispatch.md defines the dispatch protocol elements")
def t_dispatch_protocol_tokens():
    if not exists("refs/parallel-dispatch.md"):
        raise AssertionError("refs/parallel-dispatch.md is missing")
    s = read("refs/parallel-dispatch.md").lower()
    required = {
        "threshold (>=3)": "3 or more",
        "compact payload": "compact",
        "wave order 16->8": "stage 16",
        "home page last":   "stage 13",
        "graceful fallback": "fallback",
    }
    missing = sorted(label for label, needle in required.items() if needle not in s)
    assert not missing, f"parallel-dispatch.md missing protocol elements: {missing}"

@check("SKILL.md Stage 7 points to the dispatch protocol with the >=3 threshold")
def t_dispatch_pointer():
    skill = read("SKILL.md")
    assert "refs/parallel-dispatch.md" in skill, "SKILL.md never references refs/parallel-dispatch.md"
    assert "3 or more" in skill, "SKILL.md does not state the '3 or more' dispatch threshold"
```

- [ ] **Step 2: Run the suite and confirm the two new checks FAIL**

Run: `python3 tests/validate_skill.py`
Expected: FAIL on `t_dispatch_protocol_tokens` (file missing) and `t_dispatch_pointer` (SKILL.md has no reference / threshold string yet). Summary: `26/28 passed`.

- [ ] **Step 3: Create `refs/parallel-dispatch.md`**

```markdown
# Parallel Dispatch Protocol

Loaded only when the Stage 7 output menu yields **3 or more** independent downstream
artifacts. Its job: cut wall-clock latency by generating those artifacts on concurrent
subagents, while keeping token cost bounded. Below the threshold, ignore this file and
generate inline sequentially — the subagent cold-start cost is not worth it for 1–2 artifacts.

## Capability check (do this first)

If this runtime exposes no subagent/Task dispatch capability, **fall back** to sequential
inline generation of every selected artifact (the pre-refactor behavior). Never fail or stall
because subagents are unavailable. Everything below assumes the capability exists.

## What counts toward the threshold

Count only the independent **downstream artifact** stages: 8, 9, 10, 11, 12, 14, 16.
Do **not** count:
- **Stage 13** (output home page) — it is the stitch step and always runs last, by the orchestrator.
- **Stage 15** (Discovery Framework) — an upstream refinement that runs as its own separate pass,
  never inside the concurrent waves.

## Compact shared payload (caps the token cost)

Each subagent gets a **compact** brief — never the conversation history. On Stage 7 Approve, the
orchestrator has already written the approved POV to a working file. Hand each subagent exactly:
1. the **path to the approved POV file**,
2. the **path to its one** `refs/stages/stage-NN-*.md` instruction file,
3. the **output directory** + the partner `SLUG`.

The subagent reads those two files, generates its artifact to the output directory following the
stage instructions (including its own validation checklist), and returns the **output file path(s)**.
This bounds input duplication to the small compact POV instead of re-deriving full context N times.

## Dependency-aware waves

Stage 16 (Architectural Assessment) feeds Stage 8 (MVP Build Plan), so they cannot share a wave.

- **Wave 0 — Stage 16**, if selected. Wait for it to finish; its output is an input to Stage 8.
- **Wave 1 — all other selected artifacts** (Stages 8, 9, 10, 11, 12, 14), dispatched **concurrently**,
  one subagent each, each with its own compact payload. Wait for all to return.
- **Final — Stage 13** (home page), run by the **orchestrator** (not a subagent) once every artifact
  file exists, since it needs all the output paths. Run it whenever 2 or more artifacts were produced.

## After the waves

Collect every returned artifact path, confirm each file exists, then run Stage 13 to build the
home page that links them. Deliver the `SLUG-index.html` path as the primary entry point and list
the artifact files beneath it, exactly as Stage 13 specifies.
```

- [ ] **Step 4: Add the Stage 7 dispatch pointer in SKILL.md**

In `SKILL.md`, immediately after the "Run all selected outputs simultaneously…" paragraph (the one right below the `AskUserQuestion` code block, ~line 250), add:

```markdown
**Parallel dispatch.** When the selection yields **3 or more** independent downstream artifacts (Stages 8, 9, 10, 11, 12, 14, 16 — "All outputs + home page" always qualifies), load `refs/parallel-dispatch.md` and follow it to fan the work out to concurrent subagents. For 1–2 artifacts, generate inline sequentially as described above.
```

This satisfies both the `refs/parallel-dispatch.md` reference (orphan/exists checks) and the `3 or more` threshold string.

- [ ] **Step 5: Run the suite — confirm 28/28**

Run: `python3 tests/validate_skill.py`
Expected: PASS all 28. Summary: `28/28 passed`.

- [ ] **Step 6: Commit**

```bash
git add tests/validate_skill.py refs/parallel-dispatch.md SKILL.md
git commit -m "Add parallel-dispatch protocol + Stage 7 pointer + two guard checks"
```

---

## Task 4: README refresh

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the file tree and add the dispatch description**

Read `README.md` first to match its existing structure and tone. Then make these edits:
1. In the file-tree section, remove `refs/output-stages.md`; add the `refs/stages/` directory (list the nine `stage-NN-*.md` files) and `refs/parallel-dispatch.md`.
2. Where the optional-output flow is described, add a short paragraph: each downstream output now loads only its own `refs/stages/` file; when 3+ independent artifacts are requested, they fan out to concurrent subagents per `refs/parallel-dispatch.md`, with a compact-POV payload, dependency-aware waves (Stage 16 → Stage 8; Stage 13 last), and graceful fallback to sequential.
3. In the validation description, update the check count to **28**.

- [ ] **Step 2: Run the suite (docs change must not break it)**

Run: `python3 tests/validate_skill.py`
Expected: PASS 28/28.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "README: refresh for refs/stages/ split + parallel-dispatch protocol"
```

---

## Task 5: Behavioral verification (subagent-driven scenarios)

The structural validator proves the files and references are correct; it cannot prove the
**control flow** the instructions describe. Verify that behaviorally by dispatching a subagent to
execute the skill against mock inputs and checking what it does. Record results in a scratch file
(not committed unless useful).

**Files:**
- Create (scratch, optional): `docs/superpowers/plans/2026-05-30-behavioral-results.md`

- [ ] **Step 1: Scenario A — fan-out at the threshold**

Dispatch a subagent with: the pov-builder skill, a short **mock approved POV** (any partner, with a populated Architecture Summary so Stage 16/14 qualify), and the instruction that the user selected **"All outputs + home page."** Ask it to describe — without generating full artifacts — the exact execution plan it derives from SKILL.md + `refs/parallel-dispatch.md`.

Verify the plan it returns:
- Loads `refs/parallel-dispatch.md` (≥3 downstream artifacts).
- Wave 0 = Stage 16 alone; Wave 1 = Stages 8, 9, 10, 11, 12, 14 concurrently; Stage 13 last via the orchestrator.
- Each subagent brief is the **compact payload** (POV path + one stage file path + output dir/SLUG), not full context.
- Stage 15 is **not** in any wave.

- [ ] **Step 2: Scenario B — below threshold stays inline**

Dispatch a subagent with the same mock POV but selection = **only "Solution Infographic."**
Verify it does **not** load `refs/parallel-dispatch.md` and does **not** fan out — it generates Stage 11 inline.

- [ ] **Step 3: Scenario C — graceful fallback**

Dispatch a subagent told that **no subagent/Task capability is available**, with "All outputs" selected.
Verify it falls back to sequential inline generation (still honoring Stage 16-before-8 and Stage 13-last ordering) rather than failing.

- [ ] **Step 4: Record outcomes**

Note pass/fail for each scenario. If any scenario reveals an instruction ambiguity, fix the relevant
file (`SKILL.md`, `refs/parallel-dispatch.md`, or the stage file), re-run `python3 tests/validate_skill.py`
to confirm 28/28, and re-run the scenario. Commit any instruction fixes with a clear message.

---

## Task 6: Finish the branch

- [ ] **Step 1: Final full validation**

Run: `python3 tests/validate_skill.py`
Expected: `28/28 passed`.

- [ ] **Step 2: Confirm tree state**

Run: `git status -sb` (clean) and `git log --oneline -6` (review the task commits).

- [ ] **Step 3: Use the finishing-a-development-branch skill**

Invoke `superpowers:finishing-a-development-branch` to merge `parallel-instruction-files` into `main` and push, per the same pipeline used for the Discovery (Stage 15) and Architecture (Stage 16) efforts. Then update the `pov-builder-skill` memory note: idea 3 done, new `main` SHA, validator at 28, file tree change.

---

## Self-review against the spec

- **Modularize `output-stages.md` → `refs/stages/` per stage:** Task 1 (create + router) + Task 2 (cutover + delete). ✓
- **SKILL.md router + selective load:** Task 1 Step 4, Task 2 Step 3. ✓
- **Stages 15/16 stay thin loaders to existing deep-def refs:** preserved verbatim by the Task 1 Step 3 content move (their existing blocks already only load `refs/discovery-framework.md` / `refs/architecture-assessment.md`). ✓
- **`refs/parallel-dispatch.md` with threshold / compact payload / waves (16→8, 13 last) / fallback:** Task 3 Step 3, guarded by `t_dispatch_protocol_tokens`. ✓
- **≥3 downstream-artifact threshold; Stage 15 & 13 excluded from the count:** encoded in `refs/parallel-dispatch.md` and the SKILL.md note; behaviorally checked in Task 5 Scenarios A/B. ✓
- **Validator 24 → 28, corpus rewired:** Task 1 (+2), Task 2 (corpus), Task 3 (+2). ✓
- **Behavioral tests (fan-out, inline, ordering, fallback):** Task 5. ✓
- **README refresh:** Task 4. ✓
- **No regression to POV contract / voice / Stages 1–7:** none of those files are touched except the SKILL.md loader/menu region; the original 24 checks remain green throughout. ✓
```
