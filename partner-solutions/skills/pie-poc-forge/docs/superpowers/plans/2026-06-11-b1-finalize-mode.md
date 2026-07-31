# B1 — Org-Connected "Finalize" Mode (Phase D) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in, re-entrant **Phase D — Finalize** to pie-poc-forge that runs the org-dependent lifecycle (validate → deploy) against an authenticated org and records results + detailed mitigations in a new `13-finalize-report` artifact.

**Architecture:** Phase D is a new, explicitly-invoked phase layered on the existing A–C flow; generation stays org-free. It runs in two gates (non-mutating validate, then offered mutating deploy), guards production behind typed confirmation, and writes a CONDITIONAL canvas artifact `13-finalize-report` (mirroring how `09-agentscript` is agent-only). The procedure + a known-failure taxonomy live in a new `refs/finalize.md`.

**Tech Stack:** Markdown (SKILL.md, refs, artifact template), HTML (`output-index.html` card), Python 3 stdlib (`tests/validate_skill.py`), Salesforce CLI (`sf`) commands documented in the ref, delegating to `agentforce-adlc` + `sf-mcp-partner-toolkit`.

**Spec:** `docs/superpowers/specs/2026-06-11-b1-finalize-mode-design.md`

**Working discipline:** This skill's validation suite is the test harness. The RED→GREEN loop runs against `tests/validate_skill.py`. After every task, run `python3 tests/validate_skill.py` and keep it green. Final task runs a `skill-forge` audit (spec hygiene gate). Commit after each task.

---

## File structure

| File | Action | Responsibility |
|------|--------|----------------|
| `tests/validate_skill.py` | Modify | Register `13-finalize-report` in the CONDITIONAL artifact set (drives R-TEST-03 / R-ARCH-03). |
| `templates/13-finalize-report.md` | Create | The finalize-report artifact body (tokens for org, gate results, mitigations). |
| `templates/output-index.html` | Modify | Add a Phase-4 "Review" card linking the finalize report; bump the agentInScope-style removal note. |
| `refs/finalize.md` | Create | Phase D procedure: two gates, prod guardrail, delegation sequence, stop-on-failure, report contract, **known-failure taxonomy**. |
| `SKILL.md` | Modify | Add "Phase D — Finalize" section; reword the production refusal; add `refs/finalize.md` to the lazy-ref list. |
| `refs/requirements-schema.md` | Modify | Document the new `finalize` block (last-run org, gate results, IDs, timestamp). |
| `BACKLOG.md` | Modify | Move B1 to Done. |

---

### Task 1: Register `13-finalize-report` as a CONDITIONAL artifact

**Files:**
- Modify: `tests/validate_skill.py:35`
- Create: `templates/13-finalize-report.md`

- [ ] **Step 1: Add the slug to CONDITIONAL to create the failing state (RED)**

In `tests/validate_skill.py`, change line 35 from:

```python
CONDITIONAL = ["09-agentscript"]
```

to:

```python
CONDITIONAL = ["09-agentscript", "13-finalize-report"]
```

- [ ] **Step 2: Run the suite to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL on `R-TEST-03` with `artifact .md source templates missing: ['templates/13-finalize-report.md']` (because `ALL_ARTIFACTS` now includes the slug but the template does not exist yet).

- [ ] **Step 3: Create the finalize-report template (GREEN)**

Create `templates/13-finalize-report.md` with this exact content:

```markdown
# {{PARTNER}} — Finalize Report

**Generated:** {{DATE}} · **Target org:** {{TARGET_ORG}} · **Phase:** D (Finalize)

Point-in-time record of the org-dependent lifecycle run against the target org. Generation
artifacts (01–12) describe the package; this artifact records what actually happened when it
met a live org.

## Gate 1 — Validate (non-mutating)
{{GATE1_RESULTS}}

## Gate 2 — Deploy (mutating)
{{GATE2_RESULTS}}

## Mitigations
{{MITIGATIONS}}
```

- [ ] **Step 4: Run the suite to verify it passes**

Run: `python3 tests/validate_skill.py`
Expected: PASS — 16/16 (R-TEST-03 now finds `templates/13-finalize-report.md`; R-TEST-02 token hygiene passes because every token is UPPER_SNAKE_CASE; R-ARCH-03 blesses the new `.md` via the registry).

- [ ] **Step 5: Commit**

```bash
git add tests/validate_skill.py templates/13-finalize-report.md
git commit -m "feat(b1): register 13-finalize-report as a CONDITIONAL artifact + template"
```

---

### Task 2: Add the finalize-report card to the index

**Files:**
- Modify: `templates/output-index.html` (the Phase-4 "Review" `card-grid`, after the Engagement Review Deck card)

- [ ] **Step 1: Add the card**

In `templates/output-index.html`, inside the `<div class="phase-title"><span class="phase-step">4</span>Review</div>` group's `card-grid`, immediately AFTER the Engagement Review Deck card's closing `</div>` (the card whose `href="12-engagement-review-deck.html"`), insert:

```html
      <div class="card"><span class="card-kind">Finalize</span>
        <h3 class="card-title">Finalize Report</h3>
        <p class="card-desc">Point-in-time record of the Phase-D org lifecycle (validate → deploy) against the target org — per-step results, returned IDs, and detailed mitigation for any failure. Present only after a finalize run.</p>
        <div class="card-actions"><a class="btn btn-view" href="13-finalize-report.html">View ↗</a><a class="btn btn-md" href="13-finalize-report.md">Markdown ↓</a></div></div>
```

- [ ] **Step 2: Update the generation-time removal comment**

In `templates/output-index.html`, find the comment near line 77 that reads:

```html
         The 09 Agentscript card is removed at generation time when agentInScope is false. -->
```

Replace it with:

```html
         The 09 Agentscript card is removed at generation time when agentInScope is false.
         The 13 Finalize Report card is removed unless a Phase-D finalize run produced it. -->
```

- [ ] **Step 3: Run the suite**

Run: `python3 tests/validate_skill.py`
Expected: PASS — 16/16. R-TEST-03's unknown-slug check (`linked - set(ALL_ARTIFACTS)`) stays green because `13-finalize-report` is now in `ALL_ARTIFACTS`; the ALWAYS-linked check is unaffected (13 is CONDITIONAL, not ALWAYS).

- [ ] **Step 4: Commit**

```bash
git add templates/output-index.html
git commit -m "feat(b1): add Finalize Report card to the index (Review group)"
```

---

### Task 3: Write `refs/finalize.md` — Phase D procedure + failure taxonomy

**Files:**
- Create: `refs/finalize.md`

- [ ] **Step 1: Create the ref**

Create `refs/finalize.md` with this exact content:

```markdown
# Phase D — Finalize (org-connected lifecycle)

Opt-in, re-entrant. Runs ONLY when explicitly invoked against an existing package plus an
authenticated org alias (e.g. "finalize the <partner> PoC against org <alias>"). Phases A–C
stay org-free; Phase D never runs as an automatic tail of B or C.

This phase exists because six lifecycle steps are org-dependent and otherwise defer to the
build session: deploy dry-run, real deploy, agent validate, agent publish, MCP
deploy-and-configure, MCP validate-end-to-end.

## Preconditions
- A package exists (force-app/ + manifest/ + requirements.json).
- An org alias is provided AND authenticated (`sf org display --target-org <alias>` succeeds).
- If no org alias is provided: do NOT run. State that Phase D cannot run without an org, and
  surface the Gate 1 commands below for manual use. (Consistent with the prior "skipped — no
  org" behavior, now centralized here.)

## Step 0 — Identify the org (guardrail)
Run `sf org display --target-org <alias>` and read the edition / instance / org type.
- **Scratch, sandbox, or demo org** → proceed normally.
- **Production** (production edition, or not a scratch/sandbox/demo org) → require an explicit
  **typed confirmation** from the user before ANY mutating Gate-2 step (e.g. the user types the
  org alias or "DEPLOY TO PRODUCTION"). Gate 1 (non-mutating) still runs without confirmation.
  Record the confirmation in the report.

## Gate 1 — Validate (non-mutating; runs by default)
Run each applicable step, capture PASS/FAIL + output:
1. `sf project deploy start --manifest manifest/package.xml --dry-run --target-org <alias>`
2. Agent **validate** — when an agent is in the package, delegate to `agentforce-adlc`
   (`developing-agentforce` validate path). Never hand-run agent metadata validation here.
3. MCP **environment + endpoint reachability** — when MCP metadata is present, delegate to
   `sf-mcp-partner-toolkit:setup-workspace` (env/CLI/org readiness). NOTE: the MCP registration
   is not deployed yet at Gate 1, so there is nothing in the org to connect to — the live
   connectivity test belongs to Gate 2.

If ANY Gate-1 step FAILs → STOP. Write the report (Gate 1 results + Mitigation), do NOT offer
Gate 2. The user fixes the package (usually re-run Phase C) and re-finalizes.

## Gate 2 — Deploy (mutating; offered ONLY after Gate 1 is fully green)
Offer to proceed. On confirmation (and the §0 prod gate, if applicable), run in order:
1. `sf project deploy start --manifest manifest/package.xml --target-org <alias>` (real deploy).
2. Assign the generated permission set(s): `sf org assign permset --name <PermSet> --target-org <alias>`.
3. Agent **publish** → delegate to `agentforce-adlc`.
4. MCP **deploy-and-configure** → delegate to `sf-mcp-partner-toolkit:deploy-and-configure`,
   then **validate-end-to-end** → `sf-mcp-partner-toolkit:validate-end-to-end`.

Stop-on-first-failure applies in Gate 2 too: a failed step halts the run and writes its
Mitigation; later steps are recorded SKIP.

## Report contract (`13-finalize-report`)
Fill the `templates/13-finalize-report.md` tokens:
- `{{PARTNER}}`, `{{DATE}}`, `{{TARGET_ORG}}` — partner, run date, and the org identity from §0
  (alias + edition/instance; mark "PRODUCTION (confirmed)" when the prod gate was used).
- `{{GATE1_RESULTS}}` / `{{GATE2_RESULTS}}` — one table row per step: `step | command | result
  (PASS/FAIL/SKIP) | returned id/notes`. Gate 2 reads "Not run — Gate 1 not green" when stopped
  at Gate 1.
- `{{MITIGATIONS}}` — one block per FAILed step (see below); "None — all steps passed" if clean.

Then render via the standard recipe (`refs/workflow-dispatch.md` rendering recipe) and add a
`13-finalize-report` card to the index (it is CONDITIONAL — present only after a finalize run).
Record the run in `requirements.json.finalize` (see `refs/requirements-schema.md`).

## Detailed mitigation on failure (REQUIRED)
A failed step is NEVER recorded as a bare "FAIL". For each failure, write a Mitigation block:
- **Symptom** — the captured error / CLI output (verbatim, not paraphrased) + which gate/step.
- **Likely cause** — from the taxonomy below, keyed by step + error signature. If no entry
  matches, label it "unclassified — inspect output" (never invent a cause).
- **Fix** — the concrete next action, routed to the owning artifact/delegate.
- **Resume** — the exact command/phase to re-run once fixed, so the lifecycle resumes without
  restarting.

### Known-failure taxonomy (step × error signature → cause + fix)
| Step | Error signature | Likely cause | Fix | Resume |
|------|-----------------|--------------|-----|--------|
| dry-run / deploy | `INVALID_FIELD` / `INVALID_TYPE` on a managed-package object (e.g. `Loan__c`) | Unresolved managed-package reference — placeholder not resolved in the target org | Install the nCino managed package (or use a snapshot that carries it); or resolve the reference per `refs/sfdx-scaffold.md`. See Pre-Instance Config (`03`). | re-run Gate 1 |
| dry-run / deploy | `INSUFFICIENT_ACCESS` / perm-set or Platform Integration User errors | Perm set not assignable, or MCP postInstall (re-grant `UserExternalCredential`) not run | Confirm perm sets deploy; ensure the MCP postInstall InstallHandler is present (see `refs/mcp-integration.md`). | re-run Gate 1 |
| agent validate | Agent Script schema error / `mcpTool://` target unresolved | Agent references an MCP tool whose registration isn't deployed/wired yet | Deploy MCP registration first (Gate 2 ordering scaffolds MCP before agent); re-wire the tool action via Agent Builder canvas post-install. See Post-Config (`05`) + `refs/mcp-integration.md`. | re-run Gate 1 agent validate |
| MCP setup-workspace | CLI / Dev Hub / org not ready | Environment precondition missing (CLI version, Dev Hub auth, org connection) | Resolve per `sf-mcp-partner-toolkit:setup-workspace` output (install/auth steps). | re-run Gate 1 |
| MCP deploy-and-configure | `401` / `invalid_client` on the MCP callout | External Credential principal / client secret not entered post-deploy | Enter the secret at Setup → Named Credentials → External Credentials → <ESR> → Principals (out-of-band secret; never in source). See Security Assessment (`06`) + Post-Config (`05`). | re-run Gate 2 from deploy-and-configure |
| MCP validate-end-to-end | tool not discoverable / agent can't invoke | `mcpTool://` target is name-based and rewritten to an org-specific Record ID on install | Re-wire the MCP tool via the Agent Builder canvas "+" button post-install; verify with a sample utterance. See `refs/mcp-integration.md` (validator 7.10). | re-run Gate 2 validate-end-to-end |
| agent publish | publish blocked / activation error | Agent not validated, or required licenses/features absent in the target org | Clear agent validate first; confirm Agentforce licenses/features (Pre-Instance Config `03`). | re-run Gate 2 from agent publish |

## Companion-skill degradation
If `agentforce-adlc` or `sf-mcp-partner-toolkit` is not installed, the matching Gate step is
recorded SKIP with a Mitigation pointing to install the companion (mirror the degraded-mode
contract in SKILL.md). Phase D never hand-runs a delegated lifecycle step.
```

- [ ] **Step 2: Run the suite to verify no dangling/orphan references**

Run: `python3 tests/validate_skill.py`
Expected: PASS — but note `refs/finalize.md` is not yet referenced by SKILL.md, so R-ARCH-03 (orphans) would flag it. **Therefore this step is expected to FAIL R-ARCH-03** with `present but never referenced: ['refs/finalize.md']` until Task 4 wires it into SKILL.md.

- [ ] **Step 3: Commit (the ref; SKILL.md wiring lands in Task 4)**

```bash
git add refs/finalize.md
git commit -m "feat(b1): add refs/finalize.md — Phase D procedure + failure taxonomy"
```

Note: the pre-commit hook runs the suite and will report the R-ARCH-03 orphan. Use
`git commit --no-verify` for THIS commit only (the orphan is resolved in Task 4, which
re-enables verification). Record in the commit body: "orphan resolved in Task 4 (SKILL.md wiring)".

---

### Task 4: Wire Phase D into SKILL.md + reword the production refusal

**Files:**
- Modify: `SKILL.md:29` (refusal condition), after `:64` (Phase C section → add Phase D), `:67` (the "never deploys to production itself" line), and the lazy-ref list at `:83`.

- [ ] **Step 1: Reword the production refusal condition**

In `SKILL.md`, replace line 29:

```markdown
- **Production deploy requested** — this skill generates the package only; it never deploys to production.
```

with:

```markdown
- **Production deploy** — Phases A–C never deploy. Phase D (Finalize) is the ONLY sanctioned deploy path, and only against an authenticated org. It never deploys to production WITHOUT explicit, per-run typed confirmation, and only after Gate-1 validation is green (see `refs/finalize.md`).
```

- [ ] **Step 2: Add the Phase D section**

In `SKILL.md`, immediately AFTER the Phase C section (the paragraph ending `…and bump the index changelog.`) and BEFORE the `## Delegation` heading, insert:

```markdown
### Phase D — Finalize (org-connected, opt-in, re-entrant)
Runs ONLY when explicitly invoked against an existing package + an authenticated org alias (e.g. "finalize the <partner> PoC against org <alias>"). Follow `refs/finalize.md`. Two gates: **Gate 1 — Validate** (non-mutating: deploy `--dry-run`, agent validate via `agentforce-adlc`, MCP env/reachability via `sf-mcp-partner-toolkit:setup-workspace`) runs by default; **Gate 2 — Deploy** (mutating: real deploy, perm-set assign, agent publish, MCP deploy-and-configure + validate-end-to-end) is offered ONLY after Gate 1 is fully green. Inspect the org first (`sf org display`); a **production** org requires explicit typed confirmation before any mutating step. Stop-on-first-failure. Write the `13-finalize-report` artifact (per-step results + returned IDs + a detailed Mitigation block per failure, from the taxonomy in `refs/finalize.md`), record the run in `requirements.json.finalize`, and re-render the canvas. With no org alias, state Phase D cannot run and surface the Gate-1 commands.
```

- [ ] **Step 3: Update the closing delegation line**

In `SKILL.md`, replace line 67:

```markdown
This skill never deploys to production itself.
```

with:

```markdown
This skill deploys only via Phase D (Finalize), and only to a confirmed org — never to production without explicit per-run typed confirmation (see `refs/finalize.md`).
```

- [ ] **Step 4: Add `refs/finalize.md` to the lazy-ref list**

In `SKILL.md`, after the `refs/workflow-dispatch.md` bullet (line 83), add:

```markdown
- `refs/finalize.md` — Phase D org-connected lifecycle: gates, prod guardrail, delegation sequence, failure taxonomy, `13-finalize-report` contract (Phase D, opt-in).
```

- [ ] **Step 5: Run the suite**

Run: `python3 tests/validate_skill.py`
Expected: PASS — 16/16. R-ARCH-03 orphan from Task 3 is resolved (SKILL.md now references `refs/finalize.md`); R-ARCH-02 confirms the path exists.

- [ ] **Step 6: Commit**

```bash
git add SKILL.md
git commit -m "feat(b1): wire Phase D into SKILL.md + reword production refusal (confirmation-gated)"
```

---

### Task 5: Document the `finalize` block in the requirements schema

**Files:**
- Modify: `refs/requirements-schema.md`

- [ ] **Step 1: Locate the schema's top-level field list**

Run: `grep -n "fileHashes\|changelog\|appType\|^##\|^- " refs/requirements-schema.md | head -40`
Expected: shows where top-level keys (e.g. `fileHashes`, `changelog`) are documented. Add the new block in the same style as the existing `changelog` documentation.

- [ ] **Step 2: Add the `finalize` block documentation**

In `refs/requirements-schema.md`, in the section that documents top-level keys (alongside `changelog` / `fileHashes`), add:

```markdown
### `finalize` (Phase D, optional)
Records the last Phase-D finalize run; absent until a finalize run occurs. Shape:
- `date` — run date (YYYY-MM-DD).
- `targetOrg` — `{ "alias": "<alias>", "type": "scratch|sandbox|demo|production", "confirmed": <bool> }`. `confirmed` is true only when a production run was typed-confirmed.
- `gate1` — array of `{ "step", "result": "PASS|FAIL|SKIP", "notes" }`.
- `gate2` — array of the same shape, or `"not-run"` when Gate 1 was not green.
- `ids` — returned identifiers worth keeping (`{ "deployId", "agentId", "mcpRegistrationId" }`), keys present only when produced.
- `stoppedAt` — the step name where the run halted, or `null` if it completed.
This block is informational state for the next finalize run; it is NOT part of `fileHashes`
edit-preservation (it records a run, it is not a generated artifact).
```

- [ ] **Step 3: Run the suite**

Run: `python3 tests/validate_skill.py`
Expected: PASS — 16/16 (documentation-only change; no new file paths or tokens introduced).

- [ ] **Step 4: Commit**

```bash
git add refs/requirements-schema.md
git commit -m "feat(b1): document the requirements.json finalize block (Phase D run state)"
```

---

### Task 6: Hygiene gate — skill-forge audit + backlog move

**Files:**
- Modify: `BACKLOG.md`

- [ ] **Step 1: Run the full validation suite (regression check)**

Run: `python3 tests/validate_skill.py`
Expected: PASS — 16/16. If anything is red, fix before proceeding.

- [ ] **Step 2: Run a skill-forge audit against pie-poc-forge (spec hygiene gate)**

Invoke the `skill-forge` skill in **Audit** mode against `~/.claude/skills/pie-poc-forge`. Run its mechanical scorer (the `chk_*` snippets) and read the tier-gap headline.
Expected: no tier gap (complexity Tier 3 / build Tier 3), no NEW R-ARCH-03 orphans, no new FAILs introduced by B1. The pre-existing 10 `.md` false-positives in the canonical scorer (referenced via the `NN-*.md` glob) are acceptable and already documented; `refs/finalize.md` must NOT be among any new orphans (it is referenced by SKILL.md as of Task 4). Record the audit verdict in the commit body.

- [ ] **Step 3: If the audit flags anything new, fix it, then re-run Steps 1–2**

Expected: a clean audit before moving B1 to Done. Do not move B1 to Done on a red audit.

- [ ] **Step 4: Move B1 to Done in the backlog**

In `BACKLOG.md`, remove the entire `- **B1 — Org-connected "finalize" mode.** …` block from `## Open`, and add to `## Done` (top of the list):

```markdown
- **B1 — Org-connected "finalize" mode (Phase D).** Closed 2026-06-11. Added an opt-in,
  re-entrant Phase D that runs the org-dependent lifecycle against an authenticated org in two
  gates — Gate 1 validate (non-mutating: dry-run, agent validate, MCP env/reachability) runs by
  default; Gate 2 deploy (real deploy, perm-set assign, agent publish, MCP deploy-and-configure
  + validate-end-to-end) is offered only after Gate 1 is green. Production requires explicit
  typed confirmation (reworked the old absolute "never deploys to production" refusal). Writes a
  new CONDITIONAL `13-finalize-report` artifact with per-step results, returned IDs, and a
  detailed Mitigation block per failure (Symptom / Likely cause / Fix / Resume) from a
  known-failure taxonomy in `refs/finalize.md`. Stop-on-first-failure. Procedure in
  `refs/finalize.md`; wired into SKILL.md (Phase D section + reworded refusal); `finalize` run
  block documented in `refs/requirements-schema.md`. Suite 16/16; skill-forge audit clean (no
  tier gap, no new orphans).
```

- [ ] **Step 5: Commit and push**

```bash
git add BACKLOG.md
git commit -m "docs(backlog): move B1 (Phase D finalize mode) to Done — suite green, skill-forge audit clean"
git push
```

---

## Notes for the implementer

- **No new scripts** — Phase D is documented procedure + a template, not Python code. R-TEST-04
  (behavioral tests for `scripts/`) is unaffected; no new `scripts/*.py` is added.
- **Run the `sf` lifecycle by hand?** No. Phase D is the *skill's documented behavior*; this plan
  builds the documentation/template/wiring that makes the skill DO Phase D at runtime. Do not
  attempt to deploy to a live org while implementing the plan.
- **Token hygiene (R-TEST-02):** every `{{TOKEN}}` you add to `templates/13-finalize-report.md`
  must be UPPER_SNAKE_CASE. The six tokens used (`PARTNER`, `DATE`, `TARGET_ORG`,
  `GATE1_RESULTS`, `GATE2_RESULTS`, `MITIGATIONS`) already satisfy this.
- **Commit order matters:** Task 3 intentionally leaves a transient R-ARCH-03 orphan that Task 4
  resolves. Only Task 3's commit uses `--no-verify`; every other commit runs the hook clean.
```
