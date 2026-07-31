# Critic Loops for the Asset-Creation Fan-Out — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two bounded QA loops to the pov-builder package fan-out — a per-artifact `generate → critic → repair` pipeline on the three heavy artifacts (Stages 8/9/16) and a Wave-2 package completeness-critic over the whole package — both detect→auto-repair (1 round), independent subagents, gated to the fan-out path.

**Architecture:** Both loops are **behavioral prose** added to `refs/parallel-dispatch.md` (the file that already owns fan-out orchestration). No new stages, templates, refs, or `validation/*.md` checklists. The skill has no behavioral unit tests of LLM output; its "tests" are the structural invariants in `tests/validate_skill.py` (file existence, reference integrity, protocol-element presence). The suite is therefore the failing test we drive against: Task 1 encodes the new protocol-element expectations into the suite (red), and Tasks 2–6 make it green by writing the prose. The pre-commit hook blocks any commit while the suite fails, so commits land only at green checkpoints.

**Tech Stack:** Markdown instruction files, Python 3 validation suite (`tests/validate_skill.py`, stdlib-only), git with a pre-commit hook that runs the suite.

**Why the validation suite drives this plan:** The two features are prose, not code — their runtime catch-rate is not unit-testable (the suite docstring says so). What *is* testable is whether `refs/parallel-dispatch.md` carries the protocol elements: the pipeline naming, the four defect classes, the independence principle, the scoped-edit + re-validation guardrails, and the widened critic payload. Five new checks plus one extended check assert exactly that. A future edit that drops a loop, weakens a guardrail, or "simplifies" the critic payload back to artifact+POV will turn the suite red.

**Branch:** Create and work on `feature/critic-loops` (mirrors the competitive-assessment precedent). Task 0 covers this.

**Baseline:** The suite is green at **62/62** before this plan. It ends at **67/67** (5 new checks; `t_dispatch_protocol_tokens` is extended, not added).

---

## File Structure

**Modified files (no new files):**
- `tests/validate_skill.py` — 5 new `@check` functions + 2 new needles in the existing `t_dispatch_protocol_tokens` required-map.
- `refs/parallel-dispatch.md` — two new sections appended after "After the waves": **"Per-artifact critic (heavy artifacts: Stages 8, 9, 16)"** and **"Package completeness-critic (Wave 2)"**.
- `SKILL.md` — one sentence added to the Stage 7 **Dispatch rule** bullet, pointing at the new critic sections.
- `README.md` — one sentence added to the fan-out paragraph (line ~102) describing the two loops.

**Mutual-invariant note:** `t_dispatch_protocol_tokens` (extended in Task 1) and the new `t_per_artifact_critic` / `t_package_critic` / `t_critic_independence` / `t_repair_safety` / `t_critic_payload` all read `refs/parallel-dispatch.md`. They only return green once the prose in Tasks 2–3 is complete. Task 1 commits the red suite with `--no-verify` (the only such commit); Task 5 lands the green commit normally through the hook.

---

## Task 0: Create the feature branch

**Files:** none (git only)

- [ ] **Step 1: Create and switch to the branch**

```bash
cd ~/.claude/skills/pov-builder
git checkout -b feature/critic-loops
```

- [ ] **Step 2: Confirm a clean green baseline before any edits**

Run: `python3 tests/validate_skill.py | tail -1`
Expected: `62/62 passed`

---

## Task 1: Encode the critic-loop expectations into the validation suite (the failing tests)

**Files:**
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Extend the existing `t_dispatch_protocol_tokens` required-map with the two loop needles**

In `tests/validate_skill.py`, find the `required` dict inside `t_dispatch_protocol_tokens` (it ends with the `"fill-script sweep": "_fill",` line). Add two entries before the closing brace so the dict reads:

```python
    required = {
        "threshold (>=3)":   "3 or more",
        "compact payload":   "compact payload",
        "wave order 16->8":  "wave 0",
        "home page last":    "stage 13",
        "graceful fallback": "fall back",
        "pov persisted":     "persist the approved pov",
        "package date":      "package_date",      # one date fixed by orchestrator, passed to every subagent
        "confidence anchor": "anchor to the pov",  # analytical artifacts anchor confidence to the POV
        "fill-script sweep": "_fill",             # orchestrator sweeps stray fill scripts before the home page
        "per-artifact critic": "per-artifact critic",     # Feature 1 — heavy-artifact generate→critic→repair loop
        "package critic":      "completeness-critic",     # Feature 2 — Wave-2 cross-artifact critic
    }
```

- [ ] **Step 2: Add the five new check functions**

In `tests/validate_skill.py`, immediately after the `t_dispatch_competitive` function (it ends with the `assert ... "parallel-dispatch.md missing Stage 19 / competitive assessment"` line), add the following five checks:

```python
@check("Per-artifact critic pipeline (Stages 8/9/16) is defined with a 1-round cap")
def t_per_artifact_critic():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "per-artifact critic" in low, "missing the 'per-artifact critic' section"
    # the generate → critic → repair pipeline, named
    assert "generate" in low and "critic" in low and "repair" in low, \
        "per-artifact pipeline must name generate / critic / repair"
    assert "generate → critic → repair" in low or "generate, critic, repair" in low, \
        "per-artifact section must name the 'generate → critic → repair' pipeline explicitly"
    # scoped to the three heavy artifacts
    for s in ("stage 8", "stage 9", "stage 16"):
        assert s in low, f"per-artifact critic must name {s} as in scope"
    # one-round cap
    assert "one round" in low or "1 round" in low or "one-round" in low, \
        "per-artifact critic must state the one-round repair cap"

@check("Package completeness-critic (Wave 2) defines its 4 defect classes and ordering")
def t_package_critic():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "completeness-critic" in low, "missing the 'completeness-critic' (Wave 2) section"
    assert "wave 2" in low, "package critic must be labelled Wave 2"
    # four defect classes
    classes = {
        "contradiction with the pov": "contradiction with the pov",
        "contradiction between artifacts": "contradiction between artifacts",
        "confidence drift": "confidence drift",
        "anti-overlap": "anti-overlap",
    }
    missing = sorted(label for label, needle in classes.items() if needle not in low)
    assert not missing, f"package critic missing defect classes: {missing}"
    # ordering: after the mechanical cleanups, before Stage 13
    assert "after the mechanical cleanup" in low, \
        "package critic must state it runs AFTER the mechanical cleanups"
    assert "before stage 13" in low, "package critic must state it runs BEFORE Stage 13"
    # detect → auto-repair, one round
    assert "auto-repair" in low, "package critic must state detect → auto-repair"
    assert "one round" in low or "1 round" in low or "one-round" in low, \
        "package critic must state the one-round cap"

@check("Both critics are independent subagents; repair is a fresh subagent")
def t_critic_independence():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "independent" in low or "separate subagent" in low, \
        "protocol must state the critic is independent of the generator"
    assert "fresh repair subagent" in low or "fresh subagent" in low, \
        "protocol must state repair runs on a fresh subagent"
    # the principle: do not let the author grade its own work
    assert "grade" in low or "grading" in low or "attacks the artifact" in low, \
        "protocol must state the don't-grade-your-own-work rationale"

@check("Repair safety: scoped-edit constraint + post-repair re-validation gate")
def t_repair_safety():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    # scoped-edit constraint
    assert "edit" in low and "in place" in low, "repair must state 'edit in place'"
    assert "do not regenerate" in low, \
        "repair must forbid regeneration ('do not regenerate')"
    # post-repair re-validation gate
    assert "post-repair" in low or "re-validation" in low or "re-run" in low, \
        "protocol must state a post-repair re-validation step"
    assert "previously-passing" in low or "previously passing" in low, \
        "re-validation gate must discard a repair that regresses a previously-passing check"
    assert "discard the repair" in low, \
        "re-validation gate must say discard the repair and keep the pre-repair version"

@check("Per-artifact critic payload is widened (stage file + framework + vertical + discovery) with the build-detail exclusion")
def t_critic_payload():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    # the four context inputs beyond artifact + POV
    assert "stage instruction file" in low or "its stage file" in low or "stage-nn" in low, \
        "critic payload must include the artifact's own stage instruction file"
    assert "og-tech-strategy-framework.md" in low, "critic payload must include the framework spine"
    assert "vertical file" in low or "refs/verticals/" in low, \
        "critic payload must include the matched vertical file"
    assert "discovery-document" in low or "discovery document" in low, \
        "critic payload must include the package discovery document when present"
    # the mandated-build-detail exclusion
    assert "by mandate" in low or "mandated" in low, \
        "critic lens must carry the mandated-build-detail exclusion"
    assert "do not flag" in low, \
        "exclusion must instruct the critic NOT to flag mandated build detail as ungrounded"
```

- [ ] **Step 3: Run the suite to verify it now fails for exactly the expected reasons**

Run: `python3 tests/validate_skill.py`
Expected: FAIL. The summary should read `62/67 passed` (5 new checks fail; the 62 prior checks still pass because `t_dispatch_protocol_tokens` now also needs the two new needles — so actually expect `61/67`, see note). The failing checks must be: `Per-artifact critic pipeline...`, `Package completeness-critic...`, `Both critics are independent...`, `Repair safety...`, `Per-artifact critic payload is widened...`, and `refs/parallel-dispatch.md defines the dispatch protocol elements` (the extended `t_dispatch_protocol_tokens`, now missing `per-artifact critic` / `completeness critic`). This confirms the suite is demanding the new prose.

> **Count note:** the suite grows from 62 to 67 registered checks. With the prose absent, 6 checks fail (the 5 new + the extended `t_dispatch_protocol_tokens`), so the summary reads `61/67 passed`. Tasks 2–4 drive it to `67/67`.

- [ ] **Step 4: Commit the failing tests (the only `--no-verify` commit in this plan)**

```bash
cd ~/.claude/skills/pov-builder
git add tests/validate_skill.py
git commit --no-verify -m "test: require critic loops in the dispatch protocol

Encodes the per-artifact critic, package completeness-critic, independence,
repair-safety, and widened-payload invariants before the prose exists; suite
is intentionally red (61/67) until the parallel-dispatch.md prose lands."
```

---

## Task 2: Write the per-artifact critic section in parallel-dispatch.md

**Files:**
- Modify: `refs/parallel-dispatch.md`

- [ ] **Step 1: Append the per-artifact critic section**

The file currently ends with the "After the waves" section (its last numbered item is "3. **Guarantee the home-link pill on every artifact.**"). Append the following new section at the very end of `refs/parallel-dispatch.md`:

````markdown

## Per-artifact critic (heavy artifacts: Stages 8, 9, 16)

The three analytically heavy artifacts — Stage 8 (MVP Build Plan), Stage 9 (Red Team), and
Stage 16 (Architectural Assessment) — are generated as a **generate → critic → repair**
pipeline instead of a single self-grading pass. The other artifacts generate once, as today.
This does not change which wave an artifact belongs to (Stage 16 stays in Wave 0; Stages 8 and 9
stay in Wave 1) — the pipeline runs *inside* that artifact's dispatch.

Each critic and each repair runs on a **separate, independent subagent** — never the generator
grading its own work. The skill's whole QA stance (Stage 5 Contradict, Stage 6 Validate, the Red
Team itself) distrusts single-pass self-assessment: a subagent that just wrote the analysis is
primed to defend it. A fresh critic **attacks the artifact**, not its own reasoning.

**Stage A — Generate** (unchanged): the stage subagent produces `.md` + `.html` and returns the
path(s), including its own `validation/*-checklist.md` self-grade.

**Stage B — Critic** (new): a fresh critic subagent reads the artifact under an
artifact-specific adversarial prompt and returns a **structured verdict** — a defects array
(each defect: `location`, `what is wrong`, `why it matters`) or `clean`. It repairs nothing.

The critic's payload must give it the **same grounding context the generator had** — not a lean
artifact-plus-POV payload (an empirical test showed lean produces a 36–53% false-positive rate,
systematically flagging mandated build detail as "invented"). Hand the critic subagent:
- the artifact under review and the approved POV file;
- **the artifact's own stage instruction file** (`refs/stages/stage-NN-*.md`) — without it the
  critic cannot tell *mandated synthesis* (the metadata blueprint, component inventory, and
  integration design Stage 16 is required to produce) from *invention*;
- `refs/og-tech-strategy-framework.md` — the framework spine, which carries the Well-Architected
  rating rules the critic checks ratings against;
- the matched **vertical file** from `refs/verticals/` (the same one the generator loaded);
- the package **discovery document** (`{SLUG}-discovery-document.md`) if one exists — artifacts
  legitimately cite "Discovery Theme …"; a critic blind to it false-flags those citations.

Per-artifact adversarial lenses (state the matching one in the critic brief):
- **Red Team (Stage 9)** — "Does this actually attack? Flag every threat stated then immediately
  softened, every framework that concludes 'low risk' without evidence, and a missing Biggest
  Blind Spot. A Red Team that reassures has failed its job."
- **Architectural Assessment (Stage 16)** — "Is every architecture claim grounded in the POV's
  stated architecture, the framework, or the vertical file — or invented? Flag Well-Architected
  ratings that violate the framework's rules (e.g. a quality rated 🔴 on evidence its own line
  marks `[TBD]` — the framework says an unevidenced quality is `[TBD]`, never invented) and any
  recommendation that **contradicts** the POV. **Exclusion:** the metadata blueprint, component
  inventory, and integration design are synthesized **by mandate** — **do not flag** them as
  ungrounded merely because the POV does not enumerate them; flag them only if they contradict
  the POV's stated architecture or commercial model (e.g. a 2GP managed package recommended for
  an OEM-embedded product, or a paid SKU absent from the POV's stated SKU set)."
- **MVP Build Plan (Stage 8)** — "Does the scope match the named design partner and the POV's MVP
  definition? Flag scope creep beyond the pilot, user stories with no acceptance criteria, and
  phases with no commitment anchor. Same exclusion: build detail synthesized **by mandate** is
  not a defect unless it contradicts the POV — **do not flag** it merely for not being in the POV."

The critic judges **internal rigor only** — never cross-artifact concerns (those are the package
completeness-critic's job). It does **not** re-run the artifact's `validation/*-checklist.md` —
that is Stage A's job and the post-repair gate's job, below.

**Stage C — Repair** (new, conditional): runs **only if** Stage B returned defects; if the
verdict is `clean`, skip it. Dispatch a **fresh repair subagent** with the artifact path, the
critic's defect list, and this **scoped-edit instruction**, verbatim: **"Edit the `.md` in place
to fix exactly these defects. Do not regenerate the artifact from the template or from scratch.
Preserve every section, claim, and `{{TOKEN}}`-filled value not named in a defect — especially
the metadata blueprint and component inventory. Then re-render the `.html` from the repaired
`.md`."** The "edit in place, do not regenerate" wording is load-bearing: an unconstrained repair
re-derives the whole artifact, re-introduces the mechanical defects (pill/date) the cleanups
already fixed, and can flatten correct content. **One round only** — there is no second critic pass.

**Post-repair re-validation (mandatory gate).** After Stage C, re-run the artifact's own
`validation/*-checklist.md`. If the repaired artifact now **fails a check it was previously-passing**,
the repair regressed it — **discard the repair and keep the pre-repair version**, and note it
when you deliver. This guardrail makes unattended auto-repair safe: a critic's judgment call that
removes a required section can never ship.

**Failure handling.** If a critic or repair subagent crashes or times out, log one status line and
keep the pre-critic artifact — the loop is an enhancement, never a gate that can sink an artifact.
Re-dispatch once; if it fails again, ship the generated artifact unrepaired and note it.
````

- [ ] **Step 2: Verify the per-artifact checks now pass**

Run:
```bash
cd ~/.claude/skills/pov-builder
python3 - <<'PY'
import subprocess, sys
out = subprocess.run([sys.executable, "tests/validate_skill.py"], capture_output=True, text=True).stdout
for name in ("Per-artifact critic pipeline", "Repair safety", "Per-artifact critic payload is widened"):
    line = next((l for l in out.splitlines() if name in l), "MISSING")
    print(line)
PY
```
Expected: three lines, each starting `PASS`.

> Note: `t_package_critic`, `t_critic_independence`, and the extended `t_dispatch_protocol_tokens` are still red until Task 3 (the package-critic section names "completeness critic", "Wave 2", and the four defect classes). `t_critic_independence` may already pass if the independence wording above is detected — that is fine. Do **not** commit yet; the suite is not green until Task 3.

---

## Task 3: Write the package completeness-critic section in parallel-dispatch.md

**Files:**
- Modify: `refs/parallel-dispatch.md`

- [ ] **Step 1: Append the package completeness-critic section**

Append the following new section at the very end of `refs/parallel-dispatch.md` (immediately after the per-artifact critic section added in Task 2):

````markdown

## Package completeness-critic (Wave 2)

After every selected artifact exists **and the mechanical cleanups have run** (the `_fill*.py`
sweep and the Markdown-native HTML re-render in "After the waves"), run one **package
completeness-critic** as **Wave 2** — a single independent subagent that reads the approved POV
plus every produced artifact and hunts the **cross-artifact** semantic defects no script and no
per-artifact critic can see. It runs **after the mechanical cleanups** (so it never wastes a
finding on a pill/date/stale-HTML defect a script already fixed) and **before Stage 13** (so the
home page stitches the repaired artifacts).

The completeness-critic returns a **structured verdict** — a defects array, each tagged with the
**single offending artifact** and the specific fix — across exactly four classes:

1. **Contradiction with the POV** — an artifact asserts something the approved POV does not
   support or directly contradicts (e.g. the MVP names a design partner the POV says does not exist).
2. **Contradiction between artifacts** — two artifacts disagree on a fact (e.g. Consumption
   assumes Data Cloud while the Architectural Assessment scopes it out).
3. **Unexplained confidence drift** — an artifact's stated confidence differs from the POV's with
   no one-line rationale. This is the *verification* the confidence-anchoring brief lacks: that
   brief instructs each subagent to explain its delta; this critic checks it actually did.
4. **Anti-overlap violation** — an artifact restates content its scope guard forbids (Competitive
   restating Red Team threats; Consumption doing dollar sizing; an artifact restating the core
   Stage 16 architecture).

**Detect → auto-repair, one round.** For each defect, dispatch a **fresh repair subagent** scoped
to that one artifact (artifact path + POV path + the specific defect), with the same scoped-edit
instruction as the per-artifact repair: **"Edit the `.md` in place to fix only this defect. Do not
regenerate; preserve all other content; then re-render the `.html`."** Repairs run **concurrently**
(the artifacts are independent). After each repair, re-apply the mechanical cleanups to the touched
artifact **and** run the **post-repair re-validation gate** — re-run that artifact's
`validation/*-checklist.md`; if it now fails a **previously-passing** check, **discard the repair**
and keep the pre-repair version, and note it. Then proceed to Stage 13. **One round only** — there
is no second critic pass.

**Failure handling.** If the completeness-critic subagent itself fails, log one status line and
proceed to Stage 13 with the unrepaired package — the critic is an enhancement, **never a gate**
that can sink a package. If a repair subagent fails, keep the original artifact, note it, and
continue; never block sibling repairs or Stage 13 on one failure.

**Gating (both loops).** Both critic loops run **only on this fan-out path** (the ≥3-artifact
threshold / "All outputs + home page"). The inline 1–2-artifact path is unchanged — the user is
watching those generate, and the patches these loops generalize were all written for the
non-interactive, unwatched fan-out.
````

- [ ] **Step 2: Run the full suite — it must now be green**

Run: `python3 tests/validate_skill.py`
Expected: PASS — `67/67 passed`. In particular these now pass: `Package completeness-critic (Wave 2)...`, `Both critics are independent subagents...`, `Per-artifact critic pipeline...`, `Repair safety...`, `Per-artifact critic payload is widened...`, and `refs/parallel-dispatch.md defines the dispatch protocol elements` (the extended token check).

- [ ] **Step 3: If any check fails, repair the prose before continuing**

Read the named failure and fix the wording in `refs/parallel-dispatch.md`. Common causes: a needle the check expects is phrased differently (e.g. the check wants the literal `do not regenerate` / `previously-passing` / `after the mechanical cleanup` / `before stage 13` — match those exact substrings, case-insensitive). Re-run until `67/67`.

---

## Task 4: Wire the SKILL.md dispatch-rule acknowledgement

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: Add one sentence to the Stage 7 Dispatch rule bullet**

In `SKILL.md`, find the **Dispatch rule** bullet (it begins `- **Dispatch rule** — when the selection yields **3 or more** independent downstream artifacts ...` and ends `... load \`refs/parallel-dispatch.md\` and follow it to fan the work out to concurrent subagents. For 1–2 artifacts, generate inline sequentially.`). Replace that final sentence:

```
load `refs/parallel-dispatch.md` and follow it to fan the work out to concurrent subagents. For 1–2 artifacts, generate inline sequentially.
```

with:

```
load `refs/parallel-dispatch.md` and follow it to fan the work out to concurrent subagents — including its two QA critic loops (the per-artifact `generate → critic → repair` pipeline on Stages 8/9/16 and the Wave-2 package completeness-critic). For 1–2 artifacts, generate inline sequentially with no critic loops.
```

- [ ] **Step 2: Verify the SKILL.md edit and re-run the suite**

Run:
```bash
cd ~/.claude/skills/pov-builder
python3 - <<'PY'
s = open("SKILL.md", encoding="utf-8").read()
assert "two QA critic loops" in s, "SKILL.md dispatch rule not updated"
assert "completeness-critic" in s, "SKILL.md does not name the completeness-critic"
print("SKILL.md OK")
PY
python3 tests/validate_skill.py | tail -1
```
Expected: `SKILL.md OK` then `67/67 passed`. (No suite check asserts this sentence specifically; the run confirms nothing regressed.)

---

## Task 5: Commit the green feature

**Files:** none (verify + commit Tasks 2–4)

- [ ] **Step 1: Confirm the suite is green**

Run: `python3 tests/validate_skill.py | tail -1`
Expected: `67/67 passed`.

- [ ] **Step 2: Commit (normal commit — the pre-commit hook re-runs the suite)**

```bash
cd ~/.claude/skills/pov-builder
git add refs/parallel-dispatch.md SKILL.md
git commit -m "feat: add per-artifact + package critic loops to the fan-out

Per-artifact generate->critic->repair pipeline on Stages 8/9/16 with a
widened, generator-parity critic payload and a mandated-build-detail
exclusion; Wave-2 package completeness-critic over the whole package
(4 defect classes). Both detect->auto-repair (1 round), independent
subagents, scoped-edit repair + post-repair re-validation gate, gated
to the fan-out path. Validation suite green at 67/67."
```

The hook re-runs `tests/validate_skill.py`; the commit succeeds only if it passes, confirming green.

---

## Task 6: Document the critic loops in the README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add a sentence to the fan-out paragraph**

In `README.md`, find the fan-out paragraph that begins `When 3 or more independent downstream artifacts are requested together` (around line 102). It ends with:

```
If subagent dispatch is unavailable, the skill falls back to sequential generation automatically.
```

Replace that final sentence with:

```
Two QA critic loops run on this fan-out path: the three analytically heavy artifacts (MVP Build Plan, Red Team, Architectural Assessment) each run a `generate → critic → repair` pipeline where an independent critic subagent attacks the artifact's internal rigor, and a Wave-2 package completeness-critic checks every artifact against the POV and against each other for contradictions, unexplained confidence drift, and scope overlap. Both auto-repair in a single bounded round, with a post-repair re-validation gate that discards any repair which regresses an artifact's own checklist; both are skipped on the inline 1–2-artifact path. If subagent dispatch is unavailable, the skill falls back to sequential generation automatically.
```

- [ ] **Step 2: Run the suite (README is not asserted, but confirm no accidental edit elsewhere)**

Run: `python3 tests/validate_skill.py | tail -1`
Expected: `67/67 passed`.

- [ ] **Step 3: Commit the documentation**

```bash
cd ~/.claude/skills/pov-builder
git add README.md
git commit -m "docs: document the fan-out critic loops in the README"
```

---

## Task 7: Final verification and branch wrap-up

**Files:** none (verification only)

- [ ] **Step 1: Confirm the suite is green from a clean state**

Run: `python3 tests/validate_skill.py | tail -1`
Expected: `67/67 passed`.

- [ ] **Step 2: Confirm the tree is clean and everything is committed**

Run: `git status --short`
Expected: empty output.

- [ ] **Step 3: Confirm the commit history on the branch**

Run: `git log --oneline -4`
Expected: the failing-test commit, the green-feature commit, the docs commit (and Task 0's branch point) are present on `feature/critic-loops`.

- [ ] **Step 4: End-to-end sanity grep**

Run:
```bash
cd ~/.claude/skills/pov-builder
python3 - <<'PY'
ref = open("refs/parallel-dispatch.md", encoding="utf-8").read().lower()
# both loops present
assert "per-artifact critic" in ref and "completeness critic" in ref
# the guardrails
assert "do not regenerate" in ref and "previously-passing" in ref and "discard the repair" in ref
# widened payload + exclusion
assert "og-tech-strategy-framework.md" in ref and "by mandate" in ref and "do not flag" in ref
# ordering
assert "after the mechanical cleanup" in ref and "before stage 13" in ref
print("end-to-end critic-loop wiring OK")
PY
```
Expected: `end-to-end critic-loop wiring OK`.

- [ ] **Step 5: Hand off** — the feature is complete on `feature/critic-loops`. Use the `superpowers:finishing-a-development-branch` skill to choose merge / PR / cleanup.

---

## Self-Review

**Spec coverage** (checked against `docs/superpowers/specs/2026-06-08-critic-loops-design.md`):
- Feature 1 — per-artifact `generate → critic → repair` on Stages 8/9/16 → Task 2 prose; `t_per_artifact_critic` (Task 1). ✓
- Widened critic payload (stage file + framework + vertical + discovery) + mandated-build-detail exclusion → Task 2 prose; `t_critic_payload` (Task 1). ✓
- Per-artifact lenses (Red Team / Arch / MVP), verbatim → Task 2 prose. ✓
- Scoped-edit repair constraint + post-repair re-validation gate → Task 2 prose (per-artifact) and Task 3 prose (package); `t_repair_safety` (Task 1). ✓
- Independence (separate critic subagent; fresh repair subagent; don't-grade-your-own-work) → Task 2 prose; `t_critic_independence` (Task 1). ✓
- Feature 2 — package completeness-critic, Wave 2, four defect classes, after-cleanups/before-13 ordering, detect→auto-repair 1 round, concurrent repairs, fails-open → Task 3 prose; `t_package_critic` (Task 1). ✓
- Gating to the fan-out path → Task 3 prose (Gating subsection); SKILL.md sentence (Task 4); README sentence (Task 6). ✓
- Extend `t_dispatch_protocol_tokens` with the two loop needles → Task 1 Step 1. ✓
- "No new stages/templates/refs/checklists" → plan modifies only the 4 files named in the spec's Files table. ✓

**Placeholder scan:** No "TBD"/"TODO" in the plan's own steps. The `{{TOKEN}}`, `{SLUG}`, and `stage-NN-*` strings inside the appended prose are intentional skill-instruction content (runtime fill conventions / a stage-file glob), not plan placeholders.

**Type/name consistency:** Check-function names are unique and added once (`t_per_artifact_critic`, `t_package_critic`, `t_critic_independence`, `t_repair_safety`, `t_critic_payload`). The needles asserted in Task 1 are the exact case-insensitive substrings written into the prose in Tasks 2–3 — verified pairwise: `per-artifact critic`, `completeness critic`, `wave 2`, `generate → critic → repair`, `stage 8/9/16`, `one round`, the four defect-class phrases, `after the mechanical cleanup`, `before stage 13`, `auto-repair`, `independent`/`fresh repair subagent`/`attacks the artifact`, `edit`+`in place`, `do not regenerate`, `post-repair`/`re-run`, `previously-passing`, `discard the repair`, `og-tech-strategy-framework.md`, `vertical file`, `discovery-document`, `by mandate`, `do not flag`.

**Count note:** the suite grows from 62 to 67 registered checks (5 added in Task 1; `t_dispatch_protocol_tokens` extended in place). Tasks 3/5/6/7 expect `67/67`. The intermediate red state after Task 1 is `61/67` (6 failing: the 5 new + the extended token check).

---

## Addendum — dogfood-driven refinements (2026-06-08, post-merge-gate)

After the plan above landed green at 67/67, the feature was **dogfooded on two live packages**
(CitNOW, automotive; nCino, FinServ) before merging. The runs validated the core design (widened
payload held with zero false positives across four Stage-16 runs; confidence-drift detection was
the standout) and surfaced two refinements to the feature itself, applied in commit `a634f8a`
(validator 67→69):

1. **Disclosed-gap exclusion (both critics).** The nCino Stage-8 critic flagged "post-MVP phases
   have no commitment anchor" — which is *true and disclosed* (the POV states no committed pilot).
   Auto-repairing it would mean fabricating an anchor, and the re-validation gate would not catch
   a manufactured value (it passes the structural checklist). Fix: neither critic flags, and the
   loop never auto-repairs, a gap the POV/artifact already discloses as a known TBD — surface it,
   never fabricate. New check `t_disclosed_gap_exclusion`.
2. **Class 4 (anti-overlap) → advisory.** Anti-overlap findings proved run-to-run unstable
   (CitNOW's flipped to "resolved" on re-run with no edits; nCino's critic self-hedged them),
   unlike the deterministic classes 1–3. Auto-repairing an unstable judgment risks trimming
   legitimate content. Fix: class 4 is reported, not auto-repaired; classes 1–3 still auto-repair.
   New check `t_class4_advisory`.

These were applied directly to `refs/parallel-dispatch.md` and the spec (not re-run through the
full Task 1–7 TDD cycle, since the scaffold already existed) — both new checks were written
red-first, then made green by the prose, consistent with the plan's discipline. Final suite:
**69/69**.
