# Design Spec — Parallel-Instruction-Files Performance Refactor

**Date:** 2026-05-30
**Skill:** pov-builder
**Status:** Approved design — pending implementation plan
**Branch (planned):** `parallel-instruction-files`

## Background

The pov-builder skill is an instruction corpus read by a single Claude agent. Today the
instruction content lives in two monolithic files — `SKILL.md` (262 lines, always loaded) and
`refs/output-stages.md` (212 lines, loaded as one blob whenever *any* downstream output is
requested). The skill's text says "run in parallel" / "run simultaneously" in several places
(Stage 1 research, Stages 8–14 artifact generators), but a single agent emits tokens
sequentially, so that language is largely aspirational. True wall-clock parallelism on
*generation* requires concurrent subagents.

This is "idea 3" — the third and final sequenced effort for pov-builder, following the Discovery
Framework (Stage 15) and the Technical & Architectural Assessment (Stage 16).

## Goals

Optimize for **both** wall-clock latency and token utilization, recognizing these two axes
diverge for parallelism but align for modularization:

| Technique | Latency | Token utilization |
|---|---|---|
| Modularize files (lazy-load smaller units) | Slightly better | **Better** (load only what's needed) |
| Concurrent subagents | **Much better** for independent heavy work | **Worse** (each spawn cold-starts, duplicates input) |

The naive "split everything into parallel subagents" trap optimizes latency while inflating token
cost — every spawned agent re-derives context from cold. The design therefore applies each
technique only where it pays.

## Non-goals

- No within-stage decomposition (e.g., splitting Stage 15's 3 discovery themes or Stage 16's 7
  architecture layers into separately-dispatched sub-units). Each of those artifacts is one
  cohesive narrative; fanning out its internal sections risks incoherence for little gain. YAGNI.
- No restructuring of Stages 1–7 (the core research→draft flow). They are sequential,
  interdependent, gated by a human review at Stage 7, and always needed — lazy-loading them saves
  little and adds indirection. Stage 1's "parallel" research is already achievable via batched
  tool calls in a single message; it needs no subagents.
- No change to the delivery voice, refusal conditions, or the POV contract.

## Design

### Part 1 — File architecture (modularization)

**Split the downstream-output monolith; keep the base lean.**

- Create a new directory **`refs/stages/`** with one self-contained file per downstream stage:
  - `stage-08-mvp-build-plan.md`
  - `stage-09-red-team.md`
  - `stage-10-investor-presentation.md`
  - `stage-11-solution-infographic.md`
  - `stage-12-partner-readiness-scorecard.md`
  - `stage-13-output-home-page.md`
  - `stage-14-marketecture.md`
  - `stage-15-discovery-framework.md`
  - `stage-16-architecture-assessment.md`
- Stages 15 & 16 already have deep definitions in `refs/discovery-framework.md` and
  `refs/architecture-assessment.md`. Those files **stay unchanged**; the new `stage-15` /
  `stage-16` files are **thin loaders** that carry the menu-facing summary and point to the
  existing deep-definition refs. This preserves the structure validated by the existing
  discovery/architecture checks.
- **`SKILL.md`** keeps the always-loaded core: Delivery Voice, Refusal Conditions, Execution
  Principles, Stages 1–7, and the post-POV output menu (the three `AskUserQuestion` questions).
  Its existing stage list (currently SKILL.md lines 261–262) becomes the **router**: each stage
  number maps to its `refs/stages/stage-NN-*.md` file path.
- The instruction at SKILL.md line 259 changes from "load `refs/output-stages.md` and follow the
  matching stage" to **"load only the specific `refs/stages/stage-NN-*.md` file(s) for the
  selected output(s)."** This selective load is the token win: a single-artifact request loads
  ~one stage file (~30 lines) instead of the whole 212-line blob.
- **`refs/output-stages.md` is removed.** Its router role is absorbed by SKILL.md; its per-stage
  content moves into `refs/stages/`.

### Part 2 — Dispatch protocol (surgical parallelism)

Create a new lazily-loaded **`refs/parallel-dispatch.md`** holding the full protocol. SKILL.md's
Stage 7 gains a short pointer: *"When ≥3 independent artifacts are selected, load
`refs/parallel-dispatch.md` and follow it."*

The protocol specifies:

1. **Dispatch threshold.** Counts only independent **downstream artifacts** — Stages 8, 9, 10, 11,
   12, 14, 16. It excludes Stage 13 (the home-page stitch, always orchestrator-run last) and Stage
   15 (Discovery, an upstream refinement that runs as its own separate pass, never inside the
   concurrent waves). When ≥3 such artifacts are selected (i.e., "All outputs + home page," or a
   multi-select of 3 or more) → fan out to concurrent subagents, one per artifact. For 1–2
   artifacts → run inline sequentially (today's behavior). Below the threshold, single-agent
   sequential is both faster (no cold-start) and cheaper, so the machinery is skipped entirely.

2. **Compact shared payload (caps the token tax).** On Stage 7 Approve, the orchestrator writes
   the approved POV to a working file. Each dispatched subagent receives **only**:
   `[approved POV file path] + [its one stage file path] + [output directory]`
   — never the conversation history. The subagent reads those two files, generates its artifact to
   the output directory, and returns the output file path. This bounds input duplication to the
   compact POV (small) rather than re-deriving full context N times.

3. **Dependency-aware waves.** Stage 16 (Architectural Assessment) feeds Stage 8 (MVP Build Plan),
   so they cannot be in the same concurrent wave:
   - **Wave 0:** Stage 16, if selected (it is an input to Stage 8).
   - **Wave 1:** all other selected independent artifacts — Stages 8, 9, 10, 11, 12, 14 — dispatched
     concurrently.
   - **Final step:** Stage 13 (output home page), run by the **orchestrator** (not a subagent)
     after every artifact file exists, since it needs all the output paths. Runs whenever ≥2
     artifacts were produced.

4. **Graceful fallback.** If the runtime exposes no subagent/Task capability, fall back to
   sequential inline generation (today's behavior). The skill must never break in a non-subagent
   context. The dispatch protocol leads with this capability check.

### Expected effect

- **Common case** (POV + ≤1 artifact): only modularization applies → strictly fewer input tokens
  (load one stage file, not the blob), slightly faster, zero subagent overhead.
- **"All outputs" case:** total output tokens ~unchanged (same artifacts generated); input tokens
  rise modestly, bounded by the compact POV payload per subagent; wall-clock collapses from ~7
  sequential heavy generations into ~2 waves plus the home-page stitch.

### Part 3 — Validator, tests, docs

**Validator (`tests/validate_skill.py`), currently 24 checks:**
- Update existing checks that currently scan `refs/output-stages.md` to scan `refs/stages/`
  instead (e.g., the menu↔stage parity checks `menu-discovery`, `menu-architecture`, and any
  stage-content greps).
- Teach the orphan check that `refs/stages/*.md` and `refs/parallel-dispatch.md` are legitimate
  referenced files.
- **New invariants (target ~24 → ~28):**
  - **stage-router-parity:** bidirectional parity between the SKILL.md stage router and the files
    present in `refs/stages/` — every router entry has a file; every file is referenced.
  - **menu-stage-file:** every option in the three post-POV `AskUserQuestion` menus maps to an
    existing `refs/stages/` file.
  - **dispatch-protocol-tokens:** `refs/parallel-dispatch.md` contains the required protocol
    elements — threshold (≥3), compact-payload, Stage-13-last, Stage-16-before-8, graceful
    fallback.
  - **stage-file-schema:** each `refs/stages/stage-NN-*.md` carries the minimum expected structure
    (stage heading + the menu-facing summary; thin loaders for 15/16 reference their deep-def ref).
- The validator already treats SKILL.md + refs as one corpus for some checks — extend that
  consistently so relocated content is still found. Keep the suite stdlib-only.

**Behavioral tests (subagent-driven, per prior efforts):**
- A 3+ artifact selection triggers fan-out: subagent briefs are correctly formed (compact payload
  only), wave ordering holds (Stage 16 before 8; Stage 13 last).
- A single-artifact selection does **not** fan out (runs inline).
- Graceful fallback path produces the same artifacts sequentially when no subagent capability is
  assumed.

**README:**
- Refresh the file tree (`refs/stages/`, `refs/parallel-dispatch.md`; remove `refs/output-stages.md`).
- Document the dispatch threshold, compact-payload behavior, and dependency-aware waves.
- Update the validation description for the new check count.

## Implementation pipeline

Same pipeline as Stages 15 and 16:
spec (this doc) → writing-plans → subagent-driven TDD (fresh implementer + code-quality review per
task) → behavioral subagent tests → finishing (merge to `main` + push). Specs and plans live under
`docs/superpowers/`.

## Success criteria

- Validator green at the new check count (~28/28).
- `refs/output-stages.md` removed; `refs/stages/` populated with all 9 stage files; SKILL.md
  router updated; `refs/parallel-dispatch.md` present.
- Behavioral tests confirm: fan-out at ≥3 artifacts, inline below threshold, correct wave
  ordering, graceful fallback.
- README reflects the new architecture.
- No regression to the POV contract, delivery voice, or Stages 1–7 behavior.
