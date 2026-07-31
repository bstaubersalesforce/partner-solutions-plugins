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

Count only the independent **downstream artifact** stages: 8, 9, 10, 11, 12, 14, 15 (auto-capture), 16, 17, 18, 19.
Do **not** count:
- **Stage 13** (output home page) — it is the stitch step and always runs last, by the orchestrator.
- **Stage 15** (Discovery Framework) runs in Wave 1 in **auto-capture mode** (pre-fill, no questions);
  its brief must state auto-capture explicitly. Its **workshop** mode is a separate, interactive,
  standalone pass and never runs inside the concurrent waves.

## Prepare the shared inputs (before dispatching)

Do this once, before any subagent goes out:

1. **Derive the partner `SLUG` and the output directory** using Stage 13's filename convention —
   `SLUG` = the partner name lowercased and hyphenated (e.g. "Alvee Health" → `alvee-health`); every
   artifact lands in one output directory with relative links.
2. **Persist the approved POV to disk** at `{output-dir}/{SLUG}-pov.md` (the path Stage 13 expects).
   The fan-out subagents read the POV from this file, not from your conversation — so it must exist
   on disk before you dispatch.
2a. **Fix the package date once, and pass it to every subagent.** Resolve a single `{PACKAGE_DATE}`
   (today, `YYYY-MM-DD`) before dispatching. Subagents filling an HTML template have no reliable date
   of their own — left to themselves they copy the template's seeded date or scrape one from the POV
   body, so a multi-wave run ships **mixed dates** across artifacts (observed in production). The
   orchestrator owns the one true date; every brief carries it (see the payload below).
3. **Tell each subagent to name its artifact per Stage 13's convention** (`{SLUG}-<artifact>.md` /
   `.html`, e.g. `{SLUG}-investor-presentation.html`) so Stage 13 links every output without renaming.
   State the **exact** filename in the brief — do not leave the subagent to abbreviate. The names Stage 13
   expects are fixed; the two that subagents most often shorten are:
   - Stage 16 → `{SLUG}-technical-architecture-assessment.{md,html}` (NOT `{SLUG}-architecture-assessment`)
   - Stage 8 → `{SLUG}-mvp-build-plan.{md,html}`
   - Stage 12 → `{SLUG}-readiness-scorecard.{md,html}` (NOT `{SLUG}-partner-readiness-scorecard`, even though the menu/README call it the "Partner Readiness Scorecard")
   A name mismatch does not error — it silently drops the artifact's card from the home page. Pin every name.
4. **Capture-preservation check (before regenerating discovery).** If `{output-dir}/{SLUG}-discovery-document.md` already exists **with at least one filled** (non-`[pending]`) Discussion-capture slot, do not let the discovery subagent overwrite it silently. Surface a single `AskUserQuestion` offering: **(a) Archive original, then regenerate** (default/recommended — copy the existing `.md` and `.html` to `{SLUG}-discovery-document.archived-{YYYY-MM-DD}.{md,html}`, suffix `-2`/`-3` if that name exists, then regenerate fresh); **(b) Apply captures first** — run the discovery readback (`refs/discovery-framework.md` → Capture Readback) to fold insights into the POV before regenerating; **(c) Skip discovery regeneration** — keep the captured doc, regenerate the rest of the package around it (omit Stage 15 from Wave 1 this run); **(d) Overwrite anyway**. Resolve this **before** dispatching Wave 1, because the discovery subagent runs non-interactively and cannot prompt. A doc that does not exist, or whose slots are all `[pending]`, regenerates silently — no prompt.

## Compact shared payload (caps the token cost)

Each subagent gets a **compact** brief — never the conversation history. Hand each subagent exactly:
1. the **path to the approved POV file** (`{output-dir}/{SLUG}-pov.md` from the prepare step),
2. the **path to its one** `refs/stages/stage-NN-*.md` instruction file,
3. the **output directory** + the partner `SLUG`,
4. the **`{PACKAGE_DATE}`** (from prepare step 2a) — the subagent must use this as the artifact's
   date (the HTML date token, any "Prepared/Generated" line), never invent its own or copy the
   template's. State it verbatim in the brief.
5. the **home-page back-link instruction** — state verbatim: **"This artifact is part of a package.
   A home page WILL be built. Fill `{{HOME_HREF}}` with `{SLUG}-index.html` and KEEP the
   '← All artifacts' back-link — do NOT treat this as a standalone artifact and do NOT remove the
   pill."** Without this, a subagent sees no home page on disk yet, classifies itself as standalone
   per `html-output-method.md`, and strips the pill — observed on ~half the artifacts in production.
   This is belt; the Stage 13 `ensure-home-link.py` sweep is suspenders — keep both.

The subagent reads those two files, generates its artifact to the output directory following the
stage instructions (including its own validation checklist), and returns the **output file path(s)**.
This bounds input duplication to the small compact POV instead of re-deriving full context N times.

**State non-interactive mode explicitly in every brief.** Several per-stage files (notably Stage 8 MVP
Build Plan and Stage 12 Readiness Scorecard) describe an interactive "draft Markdown → present → wait for
Approve → then generate HTML" review loop. That loop is for inline, conversational generation. A fanned-out
subagent has no user to approve and must not pause. Tell each subagent verbatim: **"Run non-interactively:
skip any draft→Approve review loop in your stage file; produce the final Markdown and HTML in one pass and
return the paths. Do not wait for approval."** Without this line, subagents either stall waiting for an
Approve that never comes, or each improvises its own workaround — both observed in production. The orchestrator
already holds the user's Stage 7 approval of the POV; that approval covers the downstream artifacts.

**Upstream-dependency inputs.** When a stage consumes an artifact produced by an earlier wave, add
that artifact's path to its brief as an extra item. The only such case today: Stage 8 (MVP Build
Plan) consumes the Stage 16 (Architectural Assessment) output, so Stage 8's brief must include the
path to the Stage 16 artifact returned from Wave 0.

**Confidence anchoring (analytical artifacts).** Stages that state their own confidence score (MVP
Build Plan, Red Team, Architectural Assessment) each re-derive it and tend to recalibrate downward for
the open gaps — so a package can ship the POV at 0.82 while three artifacts read 0.74/0.72 with no
explanation, and the package speaks with several voices (observed in production). Tell each such
subagent verbatim: **"Anchor to the POV's confidence score. State your own artifact-level confidence,
but if it differs from the POV's, explain the delta in one sentence (e.g. 'lower than the POV's 0.82
because the DMS access posture is unverified')."** Divergence is fine — *silent* divergence is the defect.

**Discovery (Stage 15) brief.** When Stage 15 is dispatched in a package, its brief must state **auto-capture mode** verbatim: "Run in auto-capture mode: pre-fill all dimensions and both canvases from the POV, ask no questions, emit each Discussion-capture slot as `[pending]`, and do not run the POV handshake." Without this, the discovery subagent could fall into workshop mode and stall on questions.

**Consumption (Stage 18) brief.** Stage 18 is independent (needs only the approved POV) and runs in Wave 1. Its brief states: "Produce the Consumption Opportunities artifact (.md + .html) in one pass, non-interactively. Consumption-growth-scoped only — do not restate the core architecture (Stage 16) or the license pull-through (POV Commercial Model); give qualitative consumption signals, not dollar sizing."

**Competitive (Stage 19) brief.** Stage 19 is independent (needs only the approved POV) and runs in Wave 1. Its brief states: "Produce the Competitive Assessment artifact (.md + .html) in one pass, non-interactively. Compare Salesforce vs. app platforms, hyperscalers, and AI providers across the four dimensions and both layers; load `refs/competitive-landscape.md` for durable facts and top up fast-movers live. Each dimension MUST name at least one area where a competitor is genuinely stronger, and each objection must concede before countering. Do not restate Red Team threats (Stage 9), the pull-through economics (POV Commercial Model), or dollar sizing (sf-flex-estimator)."

## Dependency-aware waves

Stage 16 (Architectural Assessment) feeds Stage 8 (MVP Build Plan), so they cannot share a wave.

- **Wave 0 — Stage 16**, if selected. Wait for it to finish; its output is an input to Stage 8.
- **Wave 1 — all other selected artifacts** (Stages 8, 9, 10, 11, 12, 14, 15, 17, 18, 19), dispatched **concurrently**,
  one subagent each, each with its own compact payload. Wait for all to return. Include Stage 14
  (Marketecture) only if the POV Architecture Summary is populated — if it is empty, drop Stage 14
  from the wave (same gate SKILL.md applies).
- **The three heavy artifacts run a critic pipeline, not a single pass.** Stages 8, 9, and 16 are
  each generated as a **generate → critic → repair** pipeline (inside their existing wave — Stage 16
  in Wave 0, Stages 8/9 in Wave 1), per the **Per-artifact critic** section below. The other
  artifacts generate once, as above.
- **Wave 2 — package completeness-critic**, run by the orchestrator after Wave 1 and the mechanical
  cleanups, **before** Stage 13. See the **Package completeness-critic (Wave 2)** section below.
- **Final — Stage 13** (home page), run by the **orchestrator** (not a subagent) once every artifact
  file exists **and Wave 2 has run**, since it needs all the (repaired) output paths. Run it whenever
  2 or more artifacts were produced.

## When a subagent fails

A subagent may crash, time out, or return without a valid artifact path. Do not let one failure sink the run.

- **Wave 0 (Stage 16) fails:** Stage 8 depends on it. Do not dispatch Stage 8 with a missing input.
  Either re-dispatch Stage 16 once, or — if it fails again — drop **both** Stage 16 and Stage 8 from
  the run, proceed with the rest of Wave 1, and tell the user which two artifacts were skipped and why.
- **A Wave 1 subagent fails:** the others are independent — let them complete. Re-dispatch the failed
  one once; if it fails again, omit just that artifact and note it. Never block sibling artifacts on it.
- **Always report.** Stage 13 links only artifacts that actually exist, so a skipped artifact silently
  drops from the home page. Name every skipped artifact explicitly when you deliver, so the gap is visible.

## After the waves

Collect every returned artifact path and confirm each file exists. Then, in this order: run the
three cleanups below, run the **Wave-2 package completeness-critic** (see its section below), and
**only then** run Stage 13 to build the home page that links them. Stage 13 is the **last** step —
it must see the repaired artifacts, so it never runs before Wave 2. Deliver the `SLUG-index.html`
path as the primary entry point and list the artifact files beneath it, exactly as Stage 13 specifies.

**Before the package critic and the home page, the orchestrator does three cleanups** — all fix
failures observed in production where a subagent's instruction did not reliably take:
1. **Sweep stray fill scripts.** Subagents are told to delete their HTML fill script, but compliance is
   not guaranteed (one leaked `_fill_*.py` per ~9 artifacts in practice). Run `rm -f {output-dir}/_fill*.py`
   so no scaffolding ships in the package directory. Belt-and-suspenders — do not rely on self-cleanup.
2. **Re-render Markdown-native HTML from the current `.md`.** The Markdown-native artifacts (POV, Red Team)
   have their HTML built by Stage 13, not by the wave subagent — a Red-Team subagent that regenerates only
   its `.md` leaves a **stale `.html`** on disk from a prior run. Stage 13 must therefore *always* re-render
   these from their current `.md` via `scripts/md-to-html.py` — never assume an existing HTML view is current.
3. **Guarantee the home-link pill on every artifact.** Run this **after** the home page exists (it links to
   it) — see Stage 13's final step. Subagents misjudge "standalone" and strip the `← All artifacts` pill
   (~half the artifacts in production), so enforce it mechanically rather than trusting the brief:
   `python3 scripts/ensure-home-link.py --dir {output-dir} --slug {SLUG}`. Idempotent; injects the pill
   where missing and repairs a wrong/leftover `{{HOME_HREF}}` href. The brief instruction (payload item 5)
   is the belt; this sweep is the suspenders.

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

**Disclosed-gap exclusion (both critics).** Do **not** flag — and never auto-repair — a gap the
POV or the artifact itself **already discloses** as a known unknown (a `[TBD]`, an explicit
"not yet committed / no committed pilot", an unpapered term, a stated open risk). An
honestly-disclosed gap is correct reporting, not a defect: e.g. "post-MVP phases have no
commitment anchor" when the POV states no pilot is committed is the artifact telling the truth.
The fix for a real disclosed gap is to **surface** it, **never to fabricate a value** to close it
(never invent a pilot name, date, SKU, or metric the POV does not support). If a finding's only
remedy would be to manufacture a fact, it is out of scope — drop it. A repair subagent that
receives such a finding must leave the gap and report it, not fill it.

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
4. **Anti-overlap violation (advisory)** — an artifact restates content its scope guard forbids
   (Competitive restating Red Team threats; Consumption doing dollar sizing; an artifact restating
   the core Stage 16 architecture). **This class is advisory: reported, not auto-repaired** — see
   the repair paragraph. "Is this a forbidden restatement or legitimate cross-reference?" is a
   judgment that proved run-to-run unstable in testing, and an over-eager trim can delete
   legitimate content the structural re-validation gate would not catch. Surface class-4 findings
   for the orchestrator/human to weigh; do not let a repair subagent act on them.

**Detect → auto-repair, one round — classes 1–3 only.** Auto-repair applies to the deterministic
classes: **Contradiction with the POV (1)**, **Contradiction between artifacts (2)**, and
**Unexplained confidence drift (3)** — these were stable and verifiable in testing. **Class 4
(anti-overlap) is advisory and is NOT auto-repaired** — collect those findings and surface them in
the delivery summary for a human to weigh; never dispatch a repair for a class-4 finding. For each
class-1–3 defect, dispatch a **fresh repair subagent** scoped to that one artifact (artifact path +
POV path + the specific defect), with the same scoped-edit instruction as the per-artifact repair:
**"Edit the `.md` in place to fix only this defect. Do not regenerate; preserve all other content;
then re-render the `.html`."** It also carries the **disclosed-gap exclusion** above — if the
defect is an honestly-disclosed gap, leave it and report, never fabricate a value. Repairs run
**concurrently** (the artifacts are independent). After each repair, re-apply the mechanical
cleanups to the touched artifact **and** run the **post-repair re-validation gate** — re-run that
artifact's `validation/*-checklist.md`; if it now fails a **previously-passing** check, **discard
the repair** and keep the pre-repair version, and note it. Then proceed to Stage 13. **One round
only** — there is no second critic pass.

**Failure handling.** If the completeness-critic subagent itself fails, log one status line and
proceed to Stage 13 with the unrepaired package — the critic is an enhancement, **never a gate**
that can sink a package. If a repair subagent fails, keep the original artifact, note it, and
continue; never block sibling repairs or Stage 13 on one failure.

**Gating (both loops).** Both critic loops run **only on this fan-out path** (the ≥3-artifact
threshold / "All outputs + home page"). The inline 1–2-artifact path is unchanged — the user is
watching those generate, and the patches these loops generalize were all written for the
non-interactive, unwatched fan-out.
