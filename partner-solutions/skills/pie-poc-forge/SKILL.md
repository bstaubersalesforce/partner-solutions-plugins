---
name: pie-poc-forge
description: Use when turning a POV MVP build plan, an Agentforce Labs agent output, or pasted requirements into an installable proof-of-concept SFDX distribution package plus an execution/config/security/gaps canvas — for Partner Innovation Engineering (PIE) partner engagements.
---

# PIE-POC-FORGE

## Overview
A Partner Innovation Engineering (PIE) skill — part of the ISV Partner Solutions Program at Salesforce. It converts upstream POV/strategy artifacts into a hands-on, installable proof-of-concept: a deployable SFDX package (scaffolding + manifest) and a canvas of execution, config, security, and gaps artifacts. Re-entrant: it updates the package as requirements evolve rather than regenerating from scratch.

## Delivery Voice
Write the **human-facing canvas and deck prose** (execution plan, MVP/PoC opinion, security assessment, gaps, dev-env, kickoff/review decks) as a senior Salesforce industry advisor briefing an ISV partner's executive team — a strategic briefing, not a coaching session or a vendor pitch.

- **Lead with the conclusion.** Every section opens with the finding; evidence follows. Never bury the recommendation.
- **Be direct. No hedging.** "It may be worth considering…" → "Do this." "There could be some risk…" → "This is a risk."
- **Short sentences. Active voice.** Split any sentence past 25 words. Name who does what.
- **Quantify or qualify.** Every claim is a number, a named source, or explicit uncertainty ("not yet validated"). Vague adjectives — "significant," "major," "substantial" — need a number or they are cut.
- **"So what?" framing.** Every section answers the partner's implicit "What does this mean for my business, and what should I do?" Observations without implications are not permitted.

**Scope of this voice — read carefully:**
- It governs **human-facing prose only**. The deterministic artifacts — SFDX metadata, `package.xml`/`sfdx-project.json`, the scratch-org def, permission set, and the authored `.agent`/agentscript — stay literal and conventional. Do not "advisor-ify" them.
- It does **not** override the strict source-or-pending / no-fabrication rules (see Refusal / Scope Conditions). Lead with the conclusion only where a sourced conclusion exists; everywhere else mark `[Pending — … — owner]`. Never invent a metric, name, date, or result to satisfy "quantify or qualify."

## Refusal / Scope Conditions
This skill does NOT do whatever it is asked. Stop and clarify or refuse when:
- **No usable input** — no build plan, Labs output, or pasted requirements. Ask; do not fabricate requirements.
- **Business logic requested in stubs** — generated Apex/LWC/Flow are signatures + TODO scaffolding only. Refuse to invent business-logic bodies.
- **Fabricating deck/artifact content** — for the Kickoff and Engagement Review decks (and all artifacts), never invent metrics, names, dates, demo results, or measured outcomes. Populate only from provided inputs; mark anything uncovered `[Pending — … — owner]`. Never present a POV target as a proven result.
- **Production deploy** — Phases A–C never deploy. Phase D (Finalize) is the ONLY sanctioned deploy path, and only against an authenticated org. It never deploys to production WITHOUT explicit, per-run typed confirmation, and only after Gate-1 validation is green (see `refs/finalize.md`).
- **Missing Technical & Architectural Assessment** — proceed using the build plan alone but flag lowered confidence in the gaps document.
- **Org62 / data guardrails** (inherited from CLAUDE.md) — scrub partner data before external use; no destructive org commands without confirmation.

## Operating Procedure

### Phase A — Ingest & Normalize (interactive)
1. Collect inputs: POV MVP Build Plan (`.md`), Technical & Architectural Assessment (`.md`), Agentforce Labs output, and/or pasted requirements. Ask for any that are missing; if the Tech & Arch Assessment is unavailable, proceed and flag lowered confidence.

   **Optional Org62 pre-fill.** Before/alongside collecting pasted inputs, offer to hydrate from an Org62 engagement: "Want to pull partner + use-case context from an Org62 engagement, or work only from the inputs you provide?" If accepted (or the user names/pastes a `Partner_Engagement__c`/Account/Opportunity ID), load `refs/org62-prefill.md`, follow it, and map the emitted engagement-context block into `requirements.json` (partner account, pilot customer, opportunity use-case). Alias = `ORG62_ALIAS` env (default `org62`); identity = logged-in session user. Declining changes nothing; any field it cannot supply is filled by the normal intake. Read-only.

2. Normalize into `requirements.json` per `refs/requirements-schema.md`.
3. Prompt for build decisions: **1GP vs 2GP** (see `refs/packaging-analysis.md` for the default), **target** (partner org vs demo instance), **agent-in-scope** (yes/no), **org template / scratch-org snapshot ID** (always offered; emphasized when `appType` is OEM/Embedded — see `refs/dev-environment.md`), and — for any field referencing a managed-package or non-generated object — **how to resolve it** (package dependency vs local placeholder; see `refs/sfdx-scaffold.md`). Never silent-default an external object reference or an org template.
4. Form and present the **MVP/PoC opinion** (`refs/mvp-opinion.md`). Get explicit user confirmation of scope before generating.

### Phase B — Generate
Follow `refs/workflow-dispatch.md`. Component count = objects + components + integrations; run generators inline if ≤ 6, else fan out as parallel subagents (fan-out is an optimization — the inline path is always correct). Generators: packaging analysis, security assessment, gaps document, SFDX scaffold + manifests (delegate metadata to `agentforce-adlc:adlc-engineer`). For SFDX scaffolding, generate a least-privilege **permission set** granting CRUD/FLS on every generated object/field/Apex (see `refs/sfdx-scaffold.md`) and a **scratch org definition** at `config/project-scratch-def.json` plus the `10-dev-environment` canvas artifact (see `refs/dev-environment.md`). Also generate the `11-kickoff-deck` and `12-engagement-review-deck` outlines (see `refs/engagement-decks.md`) — populate strictly from the POV/build/gaps inputs; mark anything uncovered `[Pending — … — owner]` and never fabricate metrics, names, or results. If any integration uses **MCP** (detected per `refs/mcp-integration.md`), follow that ref's sequenced handoff to the `sf-mcp-partner-toolkit` skills to scaffold the MCP registration metadata — never hand-author it. If `agentInScope`, follow the explicit sequenced agent handoff in `refs/agentscript-handoff.md` (write brief → pause → invoke `agentforce-adlc:developing-agentforce` → drop `.agent` into force-app → re-render). When the build is both agentic and MCP-based, scaffold MCP first, then author the agent to use the tool. Then run the barrier synthesis (`refs/workflow-dispatch.md`): re-sync `requirements.json` to as-built, run the plan-vs-built reconciliation check, then — when the package contains an agent, MCP, or invocable Apex — run the **`isv-validate-agentforce` bundle validation gate** and fold its FAILs/material WARNs back into the package (generator-side, not one-off). Then assemble the execution plan + component manifest, populate `requirements.json.fileHashes` (sha256 per generated file — see `refs/requirements-schema.md`), and render the full canvas per the rendering recipe. Finally, if an org is authenticated, run a deploy dry-run validation (see `refs/sfdx-scaffold.md`); otherwise state it was skipped.

### Phase C — Review & Update (re-entrant)
On re-run with new requirements, follow `refs/workflow-dispatch.md` Phase C: diff against stored `requirements.json`, regenerate only affected artifacts, preserve hand-edited files via the `fileHashes` comparison (emit `<name>.regen` on divergence), and bump the index changelog.

### Phase D — Finalize (org-connected, opt-in, re-entrant)
Runs ONLY when explicitly invoked against an existing package + an authenticated org alias (e.g. "finalize the <partner> PoC against org <alias>"). Follow `refs/finalize.md`. Two gates: **Gate 1 — Validate** (non-mutating: deploy `--dry-run`, agent validate via `agentforce-adlc`, MCP env/reachability via `sf-mcp-partner-toolkit:setup-workspace`) runs by default; **Gate 2 — Deploy** (mutating: real deploy, perm-set assign, agent publish, MCP deploy-and-configure + validate-end-to-end) is offered ONLY after Gate 1 is fully green. Inspect the org first (`sf org display`); a **production** org requires explicit typed confirmation before any mutating step. Stop-on-first-failure. Write the `13-finalize-report` artifact (per-step results + returned IDs + a detailed Mitigation block per failure, from the taxonomy in `refs/finalize.md`), record the run in `requirements.json.finalize`, and re-render the canvas. With no org alias, state Phase D cannot run and surface the Gate-1 commands.

## Delegation (mandatory — do not re-implement these)
This skill owns planning, packaging analysis, security assessment, gaps, dev-env, decks, and canvas rendering. It MUST delegate the following rather than hand-authoring them:

**Agentic work → Agentforce ADLC** (`github.com/SalesforceAIResearch/agentforce-adlc`, installed as the `agentforce-adlc` plugin). Whenever the build involves an agent (`agentInScope`, `buildTypes` includes `agent`, or the input describes an Agentforce agent/topics/actions/Agent Spec):
- `.agent` / aiAuthoringBundle authoring, actions, subagents, flow control → `agentforce-adlc:developing-agentforce`
- agent test suites (AiEvaluationDefinition) → `agentforce-adlc:testing-agentforce`
- production session-trace / monitoring path (post-deploy) → `agentforce-adlc:observing-agentforce`
- deep Flow/Apex metadata scaffolding + deploy → `agentforce-adlc:adlc-engineer` (subagent)
See `refs/agentscript-handoff.md` for the sequenced handoff. Never hand-author Bot/GenAiPlanner/aiAuthoringBundle metadata inside this skill.

**MCP integrations → SF MCP Partner Toolkit** (`github.com/mvogelgesang/sf-mcp-partner-toolkit`, installed as the `sf-mcp-partner-toolkit` plugin). Whenever an integration uses MCP (any `integrations[].type` containing "MCP", or the input describes an MCP server/bridge):
- environment check → `sf-mcp-partner-toolkit:setup-workspace`
- generate the four MCP registration metadata files → `sf-mcp-partner-toolkit:scaffold-mcp-integration`
- deploy + OAuth credential config → `sf-mcp-partner-toolkit:deploy-and-configure`
- connectivity troubleshooting → `sf-mcp-partner-toolkit:diagnose-connection`
- end-to-end agent-invokes-MCP validation → `sf-mcp-partner-toolkit:validate-end-to-end`
See `refs/mcp-integration.md` for the sequenced handoff. Never hand-author MCP client/registration metadata inside this skill.

**Bundle validation → ISV Validate Agentforce** (`github.com/dmckeeSF/isv-validate-agentforce`, installed as the `isv-validate-agentforce` skill). When the generated package contains an agent, MCP metadata, or invocable Apex, run it as the synthesis validation gate (see `refs/workflow-dispatch.md` step 3) and fix what it flags. It validates packaging/2GP/MCP readiness of exactly the artifacts this skill produces.

This skill deploys only via Phase D (Finalize), and only to a confirmed org — never to production without explicit per-run typed confirmation (see `refs/finalize.md`).

**If a companion skill is not installed:** degrade gracefully — never hand-author what it would have produced, and never dead-stop the whole run. Keep the `DELEGATION PENDING` brief/contract, mark the affected component "pending" in `01`/`08` with a gap row in `07`, generate everything not blocked, and tell the user exactly which delegate is missing, what was skipped, and to install it and re-run. Per-delegate detail: agent → `refs/agentscript-handoff.md`; MCP → `refs/mcp-integration.md`; validator → `refs/workflow-dispatch.md`.

## Domain references (lazy-loaded)
Load the relevant ref only when its phase runs:
- `refs/requirements-schema.md` — normalize inputs into `requirements.json` (Phase A).
- `refs/mvp-opinion.md` — form the MVP/PoC recommendation (Phase A step 4).
- `refs/packaging-analysis.md` — 1GP vs 2GP + metadata coverage (Phase B).
- `refs/security-review.md` — Security Assessment findings (Phase B).
- `refs/gaps-document.md` — gaps from the Tech & Arch Assessment (Phase B).
- `refs/sfdx-scaffold.md` — project layout, manifests, stub conventions (Phase B).
- `refs/agentscript-handoff.md` — delegate `.agent` authoring to agentforce-adlc (Phase B, conditional).
- `refs/mermaid-diagrams.md` — single-source Mermaid theme + recipes + capability-gated PNG/SVG export; the `09-agentscript` routing diagram uses it (Phase B, conditional).
- `refs/mcp-integration.md` — delegate MCP registration/config to sf-mcp-partner-toolkit (Phase B, when MCP present).
- `refs/dev-environment.md` — scratch org definition + org-template/snapshot decision (Phase A prompt + Phase B artifact `10` + `config/project-scratch-def.json`).
- `refs/engagement-decks.md` — PIE Kickoff (`11`) + Engagement Review (`12`) deck outlines; strict source-or-pending, no fabrication.
- `refs/workflow-dispatch.md` — fan-out heuristic + Phase C update logic.
- `refs/finalize.md` — Phase D org-connected lifecycle: gates, prod guardrail, delegation sequence, failure taxonomy, `13-finalize-report` contract (Phase D, opt-in).

## Output templates & rendering
Canvas artifacts render from `templates/` into the engagement `docs/` dir:
- Artifact bodies: `templates/01-execution-plan.md` … `templates/09-agentscript.md` (09 only when agentInScope).
- Shared shell: `templates/document-shell.html`; index: `templates/output-index.html`.
- Render Markdown → HTML with `scripts/md-to-html.py`, then run `scripts/ensure-home-link.py` over the docs dir to guarantee the back-link on every artifact.
