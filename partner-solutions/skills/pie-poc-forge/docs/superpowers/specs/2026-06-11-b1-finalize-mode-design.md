# B1 — Org-Connected "Finalize" Mode (Phase D) — Design

**Date:** 2026-06-11
**Status:** Approved (brainstorming) — pending implementation plan
**Backlog item:** B1 (`BACKLOG.md`)
**Origin:** the live nCino run + the standing known limitation — everything org-dependent currently defers to the build session because no org is authenticated at generate time.

---

## Problem

pie-poc-forge produces an org-independent package: SFDX scaffold, authored `.agent`, MCP
registration metadata, manifests, and the canvas. Six lifecycle steps are org-dependent and
today defer to the build session with a "skipped — no org authenticated" note:

1. deploy dry-run validation (`sf project deploy start --dry-run`)
2. real deploy (`sf project deploy start`)
3. agent `validate`
4. agent `preview` / `publish` (→ `agentforce-adlc`)
5. MCP `deploy-and-configure` (→ `sf-mcp-partner-toolkit`)
6. MCP `validate-end-to-end` (→ `sf-mcp-partner-toolkit`)

The skill therefore stops at "authored package," never "deployed + validated package." B1
closes that gap with an opt-in finalize mode.

## Goals

- When an authenticated org alias is available, run the org-dependent lifecycle end-to-end and
  report results.
- Keep generation (Phases A–C) org-free and deterministic — finalize is opt-in and never fires
  by accident.
- Clearly state what was skipped when no org is set.

## Non-goals (YAGNI)

- **No scratch-org creation** in Phase D — standing up a dev org is the `10-dev-environment`
  artifact's job; Phase D takes an *existing* package to an *existing* org.
- **No rollback / undeploy.**
- **No scheduled or CI-driven runs** — finalize is an interactive, explicitly-invoked phase.

---

## Design

### 1. Invocation — a separate Phase D (Finalize)

A new **Phase D — Finalize**: re-entrant, opt-in, runs only when explicitly invoked against an
existing package plus an authenticated org alias. Phases A–C are unchanged and stay org-free.

Trigger phrasing: *"finalize the &lt;partner&gt; PoC against org &lt;alias&gt;"* (or equivalent).
Phase D never runs automatically as a tail of Phase B/C.

### 2. Lifecycle — validate-first, then offer deploy

Phase D runs in two gates:

**Gate 1 — Validate (non-mutating; runs by default):**
- `sf org display` — identify the target org (feeds the guardrail in §3).
- `sf project deploy start --manifest manifest/package.xml --dry-run --target-org <alias>`.
- Agent `validate` (delegated to `agentforce-adlc` when an agent is in the package).
- MCP **environment + endpoint reachability** check when MCP metadata is present, via
  `sf-mcp-partner-toolkit:setup-workspace` (env/CLI/org readiness). The MCP registration is
  not deployed yet at Gate 1, so there is nothing in the org to connect to — the live
  connectivity test (`diagnose-connection` / `validate-end-to-end`) belongs to Gate 2, after
  the metadata is deployed.
- Produces a per-step PASS/FAIL scorecard.

**Gate 2 — Deploy (mutating; offered ONLY after Gate 1 is fully green):**
- `sf project deploy start --manifest manifest/package.xml --target-org <alias>` (real deploy).
- Permission-set assignment.
- Agent `publish` → `agentforce-adlc`.
- MCP `deploy-and-configure` → `sf-mcp-partner-toolkit`, then `validate-end-to-end`.

If **any** Gate 1 step FAILs, Phase D stops and does NOT offer Gate 2. The user fixes the
package (re-run Phase C) and re-finalizes.

### 3. Org guardrail — confirmation-gated production

Phase D inspects the alias first via `sf org display` (edition / instance / scratch-or-sandbox
signals). It **accepts any authenticated org**, but if it detects **production** (production
edition, or not a scratch/sandbox/demo org) it **requires explicit typed confirmation** before
any mutating Gate-2 step. Gate 1 (non-mutating) needs no confirmation.

This **reverses** the skill's current absolute refusal condition. Today SKILL.md states the
skill *"never deploys to production."* That is reworded to: *"never deploys to production
without explicit, per-run typed confirmation; Phase D is the only sanctioned path, and only
after Gate-1 validation is green."* The Org62/data guardrails (no destructive ops without
confirmation) are satisfied by the typed-confirmation gate.

Delegations are unchanged: agent `publish` → `agentforce-adlc`, MCP config → toolkit. The bare
`sf project deploy` runs directly (consistent with the existing dry-run step in
`refs/sfdx-scaffold.md`).

### 4. Results & failure handling

Phase D writes a new **conditional canvas artifact `13-finalize-report`** capturing, per step:
the command run, its PASS/FAIL/SKIP result, any returned IDs (deploy id, agent/bot id, MCP
registration id), the target-org identity, and a timestamp. It is linked from the index.

**Stop-on-first-failure:** a failing step halts the run, records what passed and what failed in
`13-finalize-report`, and prints how to resume — Phase D never plows ahead deploying on a
failed validate.

**Detailed mitigation on failure (REQUIRED).** A failed step is never recorded as a bare
"FAIL". For every failure, `13-finalize-report` writes a **Mitigation** block with:
- **Symptom** — the exact error/CLI output (captured, not paraphrased), and which gate/step.
- **Likely cause** — mapped from a known-failure taxonomy in `refs/finalize.md` keyed by step
  + error signature (e.g. dry-run "INVALID_FIELD" → unresolved managed-package reference such
  as `Loan__c`; agent `validate` schema error → `mcpTool://` target not yet rewired; MCP
  `deploy-and-configure` 401 → External Credential principal/secret not entered post-deploy;
  deploy "insufficient access" → Platform Integration User perm-set / postInstall not run).
- **Fix** — the concrete next action, routed to the owning artifact/delegate: re-run Phase C
  to regenerate, fix a Pre-Instance Config (`03`) / Post-Config (`05`) step, enter a credential
  in Setup, or re-invoke the delegate (`agentforce-adlc` / `sf-mcp-partner-toolkit`).
- **Resume** — the exact command/phase to re-run once fixed, so the PIE can pick up where the
  lifecycle stopped without restarting from scratch.

`refs/finalize.md` carries the failure taxonomy (step × error-signature → cause + fix). For an
unrecognized error, Phase D still writes Symptom + Resume and labels the cause "unclassified —
inspect output," never inventing a cause. This mapping is the same discipline the
`isv-validate-agentforce` gate uses for packaging FAILs, applied to the org lifecycle.

`13-finalize-report` is **CONDITIONAL** (Phase-D-only), exactly mirroring how `09-agentscript`
is agent-only: it joins the `CONDITIONAL` set in the artifact registry, so the index /
`R-TEST-03` / orphan checks treat its absence as legitimate.

### 5. Surfaces touched

- **New ref `refs/finalize.md`** — the Phase D procedure (gates, guardrail, delegation
  sequence, failure handling, report contract) **plus the known-failure taxonomy**
  (step × error-signature → likely cause + concrete fix) that drives the Mitigation blocks.
- **SKILL.md** — new "Phase D — Finalize" section under Operating Procedure; reworded
  production refusal condition (§3); add `refs/finalize.md` to the lazy-loaded refs list.
- **New template `templates/13-finalize-report.md`** + a card in `templates/output-index.html`,
  added to the `CONDITIONAL` registry in `tests/validate_skill.py` and wired through
  `R-TEST-03` / orphan parity.
- **`requirements.json`** — gains a `finalize` block recording the last run (target org, gate
  results, returned IDs, timestamp).
- **Degraded mode** — invoked with no org alias: Phase D explains it cannot run and points to
  the Gate-1 commands for manual execution (consistent with the existing "skipped — no org"
  behavior, now centralized in Phase D).

---

## Acceptance (Done when)

- With an authenticated **non-prod** org alias, Phase D runs Gate 1, and on green offers and
  runs Gate 2 (agent + MCP CLI lifecycle end-to-end), writing `13-finalize-report` with
  per-step results and IDs.
- Against a **production** org, Phase D refuses every mutating step until explicit typed
  confirmation; Gate 1 still runs.
- A **Gate-1 failure** stops the run, records pass/fail in `13-finalize-report`, and does not
  deploy.
- Every recorded failure carries a **Mitigation block** (Symptom / Likely cause / Fix /
  Resume); a recognized error maps to its taxonomy entry in `refs/finalize.md`, and an
  unrecognized error is labelled "unclassified — inspect output" with Symptom + Resume still
  written (never a fabricated cause).
- **Skill hygiene:** after implementation, a `skill-forge` audit of pie-poc-forge reports no
  new rubric regressions (no tier gap, no new orphans), and `13-finalize-report` is registered
  CONDITIONAL so it passes whether present or absent.
- Invoked with **no org alias**, Phase D states it cannot run and surfaces the manual Gate-1
  commands.
- The skill's validation suite stays green: `13-finalize-report` is registered CONDITIONAL and
  passes R-TEST-03 / R-ARCH-03 whether present or absent.
