# Critic Loops for the Asset-Creation Fan-Out — Design Spec

**Date:** 2026-06-08
**Status:** Approved (brainstorming)
**Skill:** pov-builder

## Overview

Two bounded QA loops added to the package **fan-out** (`refs/parallel-dispatch.md`), to
catch the **semantic / judgment** defects that the skill's deterministic patches and a
subagent's one-pass self-grading cannot:

1. **Per-artifact critic** — a `generate → critic → repair` pipeline on the three
   analytically heavy artifacts (Stage 8 MVP Build Plan, Stage 9 Red Team, Stage 16
   Architectural Assessment). Catches **internal analytical rigor** defects within one
   artifact.
2. **Package completeness-critic** — a single Wave-2 pass over the approved POV + every
   produced artifact, after the mechanical cleanups and before Stage 13. Catches
   **cross-artifact** semantic defects (contradiction, confidence drift, anti-overlap
   violations).

Both are **detect → auto-repair, capped at one round**, both run on **independent
subagents** (never the generator grading its own work), and both are **gated to the
fan-out path only** (3+ artifacts / "All outputs + home page"). The inline 1–2-artifact
path is unchanged — the user is watching those generate.

This is a single, self-contained feature: behavioral prose added to `refs/parallel-dispatch.md`,
wiring acknowledgements in `SKILL.md` and `README.md`, and new structural invariants in
`tests/validate_skill.py`. **No new stages, templates, or checklists.**

---

## Motivation

`refs/parallel-dispatch.md` has accreted a list of one-off patches, each a band-aid for a
recurring fan-out defect observed in production:

- mixed dates across artifacts (`:33`),
- stripped home-link pills (`:57-62`, "~half the artifacts in production"),
- silent confidence divergence from the POV (`:82-88`),
- stale HTML left by a subagent that regenerated only its `.md` (`:134`).

These split into two kinds:

- **Mechanical / deterministic** — date pinned by the orchestrator, the
  `ensure-home-link.py` pill sweep, the stale-HTML re-render. These are fast, free, and
  100% reliable. **They stay exactly as they are.** An LLM critic re-checking them would be
  slower and *less* reliable — a strict downgrade.
- **Semantic / judgment** — does an artifact contradict the POV or another artifact? Did a
  subagent actually explain its confidence delta (the `:82-88` patch only *instructs* it to;
  nothing *verifies* it did)? Did an artifact violate its anti-overlap guard? **Nothing
  checks these today.**

The critic loops generalize the semantic class into a principled mechanism. The division of
labour is explicit and non-overlapping:

| Layer | Owns | Mechanism |
|---|---|---|
| Mechanical patches (existing) | dates, pills, stale HTML | deterministic scripts / orchestrator |
| Per-artifact critic (new) | internal analytical rigor (one artifact) | independent critic subagent, per heavy artifact |
| Package completeness-critic (new) | cross-artifact semantics | one independent critic subagent over the whole package |

---

## Architecture & placement

Everything lives in `refs/parallel-dispatch.md`'s wave model. The critics are new waves:

```
Wave 0 — Stage 16 (Arch Assessment), if selected   ─┐ heavy artifacts (8, 9, 16) each run
Wave 1 — all other selected artifacts               ─┘ as a generate → critic → repair pipeline
         (per-artifact critic fires here, only on 8/9/16; others generate once as today)
─────────── all selected artifacts now exist on disk ───────────
Mechanical cleanups (EXISTING, unchanged):
  - rm -f _fill*.py
  - re-render Markdown-native HTML (POV, Red Team) from current .md
Wave 2 — PACKAGE COMPLETENESS-CRITIC (new):
  - read POV + every artifact; emit structured defect list
  - auto-repair each offending artifact via a fresh repair subagent (concurrent), 1 round
  - re-apply the mechanical cleanups to any repaired artifact
Final — Stage 13 home page (EXISTING) — stitches the repaired artifacts
```

**Ordering rationale:**
- The package critic runs **after** the mechanical cleanups, so it never wastes a finding on
  a pill/date/stale-HTML defect a script already fixed.
- It runs **before** Stage 13, so the home page links the repaired artifacts.
- Any artifact the package critic repairs gets the mechanical cleanups re-applied to it
  before Stage 13 (a repair regenerates HTML, which could re-strip the pill or drift the date).

**Heavy-artifact wave placement is unchanged.** Stage 16 stays in Wave 0 (Stage 8 depends on
it); Stages 8 and 9 stay in Wave 1. The per-artifact pipeline is internal to each of those
dispatches — it does not change which wave an artifact belongs to.

---

## Feature 1 — Per-artifact critic (Stages 8, 9, 16)

Converts each heavy artifact from one self-grading subagent into a **3-stage pipeline**, each
stage a fresh subagent with compact context.

**Stage A — Generate** (existing behavior): the stage subagent produces `.md` + `.html` and
returns the path(s). Unchanged, including its own `validation/*-checklist.md` self-grade.

**Stage B — Critic** (new): a fresh subagent reads, under an **artifact-specific adversarial
prompt**, and returns a **structured verdict** — a defects array (each defect: location + what
is wrong + why it matters) or "clean." It repairs nothing.

**Critic payload (empirically determined — see Validation Evidence below).** The critic must
receive the same grounding context the generator had, *not* a lean artifact+POV payload:

- the artifact under review,
- the approved POV file,
- **the artifact's own stage instruction file** (`refs/stages/stage-NN-*.md`) — without it the
  critic cannot distinguish *mandated synthesis* (the metadata blueprint, component inventory,
  and integration design Stage 16 is *required* to produce) from *invention* (a defect),
- `refs/og-tech-strategy-framework.md` (the framework spine — carries the Well-Architected
  rating rules the critic must check ratings against),
- the matched vertical file from `refs/verticals/` (the same one the generator loaded),
- the package's discovery document (`{SLUG}-discovery-document.md`) if one exists — artifacts
  legitimately cite "Discovery Theme …"; a critic blind to it false-flags those citations.

Per-artifact adversarial lenses:

- **Red Team (Stage 9)** — "Does this actually attack? Flag every threat stated then
  immediately softened, every framework that concludes 'low risk' without evidence, and a
  missing Biggest Blind Spot. A Red Team that reassures has failed its job."
- **Architectural Assessment (Stage 16)** — "Is every architecture claim grounded in the POV's
  stated architecture, the framework, or the vertical file — or invented? Flag Well-Architected
  ratings that violate the framework's rules (e.g. a quality rated 🔴 on evidence its own line
  marks `[TBD]` — the framework says an unevidenced quality is `[TBD]`, never invented) and any
  recommendation that **contradicts** the POV. **Exclusion:** the metadata blueprint, component
  inventory, and integration design are synthesized *by mandate* — do NOT flag them as
  ungrounded merely because the POV does not enumerate them; flag them only if they contradict
  the POV's stated architecture or commercial model (e.g. a 2GP managed package recommended for
  an OEM-embedded product, or a paid SKU absent from the POV's stated SKU set)."
- **MVP Build Plan (Stage 8)** — "Does the scope match the named design partner and the POV's
  MVP definition? Flag scope creep beyond the pilot, user stories with no acceptance criteria,
  and phases with no commitment anchor. Same exclusion: build detail synthesized by the stage's
  mandate is not a defect unless it contradicts the POV."

**Stage C — Repair** (new, conditional): runs **only if** Stage B returned defects. A fresh
repair subagent receives the artifact path, the critic's defect list, and a **scoped-edit
instruction**: "Edit the `.md` **in place** to fix exactly these defects. Do **not** regenerate
the artifact from the template or from scratch. Preserve every section, claim, and
`{{TOKEN}}`-filled value not named in a defect — especially the metadata blueprint and
component inventory. Then re-render the `.html` from the repaired `.md`." The explicit
"edit in place, do not regenerate" wording is load-bearing: an unconstrained repair re-derives
the whole artifact and re-introduces the mechanical defects (pill/date) the cleanups already
fixed, and can flatten correct content. **One round only.** If B returns clean, C is skipped.

**Post-repair re-validation (mandatory gate).** After Stage C, re-run the artifact's own
`validation/*-checklist.md`. If the repaired artifact now **fails a check it previously
passed**, the repair regressed the artifact — **discard the repair and keep the pre-repair
version**, and note it. This is the guardrail that makes unattended auto-repair safe: a critic's
judgment call that removes a required section can never ship. (The critic itself does not run the
checklist — Stage A and this gate do.)

**Boundaries (state in the protocol):**
- The per-artifact critic judges **internal rigor only** — never cross-artifact concerns
  (that is the package critic's job). This keeps the two critics from overlapping.
- Stage B (critic) does **not** re-run the artifact's `validation/*-checklist.md` — it attacks
  *analytical quality*, which the checklist cannot measure. The checklist re-run is Stage C's
  post-repair gate, above.

**Independence rationale:** the skill's whole QA stance (Stage 5 Contradict, Stage 6 Validate,
the Red Team itself) distrusts single-pass self-assessment. A subagent that just wrote the
analysis is primed to defend it. A fresh critic attacks the *artifact*, not its own reasoning.
Cost is bounded: ≤3 extra critic subagents + ≤3 repair subagents, only on heavy artifacts,
running concurrently inside the existing waves — little added wall-clock. Each critic's payload
is a few extra reference files (the same context the generator loaded); the empirical test showed
that cost buys out a 36–53% false-positive repair rate — far cheaper than an unattended loop that
degrades artifacts.

---

## Feature 2 — Package completeness-critic (Wave 2)

One subagent, once, after all artifacts exist and the mechanical cleanups have run. It reads
**the approved POV + every produced artifact** and hunts the cross-artifact semantic defects no
script and no per-artifact critic can see. The **four defect classes**:

1. **Contradiction with the POV** — an artifact asserts something the approved POV does not
   support or directly contradicts (e.g. the MVP names a design partner the POV says does not
   exist).
2. **Contradiction between artifacts** — two artifacts disagree on a fact (e.g. Consumption
   assumes Data Cloud while the Arch Assessment scopes it out).
3. **Unexplained confidence drift** — an artifact's stated confidence differs from the POV's
   with no one-line rationale. This is the *verification* the `:82-88` patch lacks: that patch
   instructs each subagent to explain drift; the critic checks it actually did.
4. **Anti-overlap violation (advisory)** — an artifact restates content its scope guard forbids
   (Competitive restating Red Team threats; Consumption doing dollar sizing; an artifact
   restating the core Stage 16 architecture). **Reported, not auto-repaired** — see below.

**Output:** structured — a defects array, each tagged with the **single offending artifact** and
the specific fix.

**Auto-repair, 1 round — classes 1–3 only:** dispatch a **fresh repair subagent** per class-1–3
defect, with the same **scoped-edit instruction** as the per-artifact repair ("edit the `.md` in
place to fix only this defect; do not regenerate; preserve all other content; re-render the
`.html`") plus the disclosed-gap exclusion. Repairs run **concurrently**. After each repair,
re-apply the mechanical cleanups **and** the **post-repair re-validation gate** (re-run that
artifact's `validation/*-checklist.md`; if it now fails a previously-passing check, discard the
repair and keep the pre-repair version, and note it). Then proceed to Stage 13. **No second
critic pass** — one round, then ship.

**Class 4 (anti-overlap) is advisory — reported, never auto-repaired** *(dogfood-driven, 2026-06-08)*.
Across two dogfood packages (CitNOW, nCino) the anti-overlap judgment proved run-to-run unstable —
the same unchanged text flipped between "violation" and "resolved", and the critic self-hedged its
class-4 calls — whereas classes 1–3 were deterministic and verifiable. Auto-repairing an unstable
"is this a forbidden restatement?" judgment risks trimming legitimate content the structural
re-validation gate cannot protect (it tests structure, not whether a paragraph should exist). So
class-4 findings are surfaced for a human to weigh, not acted on by a repair subagent.

**Disclosed-gap exclusion (both critics)** *(dogfood-driven, 2026-06-08)*. Neither critic flags —
and the loop never auto-repairs — a gap the POV or artifact **already discloses** as a known
unknown (a `[TBD]`, "no committed pilot", an unpapered term, a stated open risk). An
honestly-disclosed gap is correct reporting, not a defect (nCino's "post-MVP phases have no
commitment anchor" is true because the POV states no pilot is committed). The remedy for a real
disclosed gap is to **surface** it, **never to fabricate** a value (pilot name, date, SKU, metric)
the POV does not support. This closes a fabrication risk the re-validation gate would not catch —
a manufactured anchor passes the structural checklist fine.

**Failure handling** (inherits the existing dispatch resilience):
- If the critic subagent itself fails — log one status line and proceed to Stage 13 with the
  unrepaired package. The critic is an enhancement, **never a gate** that can sink a package.
- If a repair subagent fails — keep the original artifact, note it, continue. Never block
  sibling repairs or Stage 13 on one failure.

---

## Gating

Both loops run **only on the parallel-dispatch path** (the ≥3-artifact threshold, or "All
outputs + home page"). For 1–2 inline artifacts, **skip both** — the user is watching those
generate and can eyeball them, and the patches the loops generalize were all written for
fan-out (non-interactive, unwatched) defects. The gate is the same one that already governs
whether `refs/parallel-dispatch.md` is loaded at all, so no new branch is introduced in
`SKILL.md`.

---

## Validation Evidence (why the payload is wide, not lean)

The original design gave the per-artifact critic a lean **artifact + POV** payload to bound
token cost. Before writing the plan, that assumption was tested empirically: the Stage 16
critic was run in two modes — **lean** (artifact + POV) vs. **wide** (+ stage file, framework,
vertical, discovery) — against two real packages on disk (`citnow`, automotive; `particle-health`,
healthcare).

| Package | Lean flagged | Wide flagged | Lean false-positive rate |
|---|---|---|---|
| citnow | 14 | 9 | ~36% (5 of 14) |
| particle-health | 15 | 7 | ~53% (8 of 15) |

The false positives were **systematic, not random**: in both packages the lean critic flagged
the artifact's **mandated build output** (custom-object/metadata blueprint, LWC/Flow/Apex
component inventory, integration design) as "invented" — content Stage 16 is *required* to
synthesize. citnow's lean critic even flagged the artifact's legitimate `Discovery Theme`
citations as unverifiable, because it could not see the discovery document sitting in the same
package. An auto-repair loop fed these false positives would **delete the artifact's most
valuable content.**

The lean critic also produced a **false negative** the wide critic caught: a Well-Architected
quality rated 🔴 on evidence its own line marked `[TBD]`, violating the framework rule that an
unevidenced quality renders `[TBD]` — invisible without the framework in context.

Both critics, robustly, caught the **real** target defects in both packages: unexplained
confidence derivation, a confidence *misgrounding* (artifact cited "POV 0.72" when the POV says
0.70 — the 0.72 was the cap), invented paid SKUs (Shield) and a 2GP package recommended against
an OEM-embedded model, and "ARR growth implies technical scale" category errors. **The critic
concept is validated; the lean payload is not.** Hence the widened payload and the
mandated-build-detail exclusion in Feature 1.

---

## Files

| File | Status | Purpose |
|---|---|---|
| `refs/parallel-dispatch.md` | edit | Add the per-artifact pipeline (Stages 8/9/16), the Wave-2 package critic, ordering, independence, and failure handling |
| `SKILL.md` | edit | One-line acknowledgement in the Stage 7 dispatch-rule prose that the package path runs critic loops (keeps the router honest; no new stage) |
| `README.md` | edit | Document the two critic loops under the fan-out / "How it works" prose |
| `tests/validate_skill.py` | edit | New structural invariants (below) + extend `t_dispatch_protocol_tokens` |

No new stages, templates, refs, or checklists.

---

## Validation contract (drives the implementation)

Both features are behavioral prose; the suite asserts **presence and wiring**, not runtime
catch-rate (not unit-testable — the suite docstring already says so). New checks, written red
first, then made green by the prose edits:

- **`t_per_artifact_critic`** — `parallel-dispatch.md` defines the per-artifact
  `generate → critic → repair` pipeline, names the three heavy stages (8, 9, 16) as its scope,
  and states the one-round cap.
- **`t_package_critic`** — `parallel-dispatch.md` defines the Wave-2 completeness-critic: names
  its four defect classes, states it runs *after* the mechanical cleanups and *before* Stage 13,
  and states detect → auto-repair with a one-round cap.
- **`t_critic_independence`** — the protocol states critics are *separate subagents* from the
  generator, and repair is a *fresh* subagent (the independence principle).
- **`t_repair_safety`** — the protocol states both the **scoped-edit** repair constraint
  ("edit in place, do not regenerate") and the **post-repair re-validation gate** (re-run the
  checklist; discard a repair that regresses a previously-passing check). These are the
  guardrails that make unattended auto-repair safe; a future edit that drops them must fail.
- **`t_critic_payload`** — the per-artifact critic section names its widened payload (stage
  instruction file + framework + vertical + discovery) and the mandated-build-detail exclusion.
  Encodes the empirically-determined fix so a later "simplify to artifact+POV" regression fails.
- **`t_disclosed_gap_exclusion`** *(dogfood-driven)* — the protocol defines the disclosed-gap
  exclusion (key off a gap the POV/artifact "already discloses"; "never fabricate"/"never invent"
  a value to close it). A future edit that drops the anti-fabrication guard must fail.
- **`t_class4_advisory`** *(dogfood-driven)* — the protocol marks class-4 anti-overlap "advisory"
  and "reported, not auto-repaired". Locks in the dogfood finding that anti-overlap is too unstable
  to auto-repair.
- **Extend `t_dispatch_protocol_tokens`** — add the new required protocol markers (e.g.
  `"completeness critic"`, `"per-artifact critic"`) to the existing required-elements map so a
  careless edit that drops a loop fails.

The pre-commit hook + CI run the suite, so commits land only at green.

---

## Out of scope (YAGNI)

- No new stages, templates, refs, or validation checklists.
- No behavioral test that a critic *actually* catches a planted defect — not unit-testable;
  would require live LLM runs. The suite asserts the protocol *carries* the mechanism, the same
  standard as the rest of the file.
- Critics do **not** touch the inline 1–2-artifact path — gated to fan-out only.
- **No second critic round** anywhere — one repair pass, then ship.
- The mechanical patches are **not** modified, removed, or duplicated by the critics.
- The per-artifact critic does **not** re-run the artifact's own checklist.
