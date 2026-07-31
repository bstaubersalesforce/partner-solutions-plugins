# pie-poc-forge

A Tier-3 Claude skill for the **Partner Innovation Engineering (PIE)** team within the Salesforce ISV Partner Solutions Program. It turns an upstream POV artifact into a hands-on, installable proof of concept.

## What it does

Takes a **POV MVP build plan**, an **Agentforce Labs agent output**, or **pasted requirements** and produces two things:

1. An installable proof-of-concept **SFDX distribution package** — deployable scaffolding (custom objects/fields as real metadata; Apex/LWC/Flow as honest stubs), a least-privilege permission set, a scratch org definition (`config/project-scratch-def.json`), and IDE-ready manifests (`package.xml` + `sfdx-project.json`).
2. A **canvas** of HTML + Markdown artifacts (styled like the POV-builder output), linked from a single `index.html`:

| # | Artifact | Always? |
|---|----------|---------|
| 01 | Execution Plan (narrative install/deploy + task backlog) | ✓ |
| 02 | MVP / PoC Opinion (opinionated hero-slice recommendation) | ✓ |
| 03 | Pre-Instance Config (what must exist before deploy) | ✓ |
| 04 | Packaging Analysis (1GP vs 2GP + metadata coverage) | ✓ |
| 05 | Post-Config Steps (activation tasks after deploy) | ✓ |
| 06 | Security Assessment (findings + verdict) | ✓ |
| 07 | Gaps Document (open questions, technical gaps, architectural items) | ✓ |
| 08 | Component Manifest (human-readable inventory) | ✓ |
| 09 | Agentscript (review copy) — incl. a **Mermaid subagent routing diagram** | agent builds only |
| 10 | Dev Environment (scratch org def + org-template/snapshot decision + dev quickstart) | ✓ |
| 11 | PIE Engagement Kickoff Deck (slide outline; source-or-pending) | ✓ |
| 12 | PIE Engagement Review / Demo Deck (slide outline; source-or-pending) | ✓ |
| 13 | Finalize Report (Phase-D org lifecycle results + per-failure mitigation) | after a finalize run |

The goal: a package that installs into a partner's org or a demo instance, compatible with typical IDEs, with a manifest.

### Diagrams (Mermaid)

For agent builds, the **Agentscript** artifact (09) embeds a **subagent routing diagram** — user → router → subagent → action — authored in Mermaid and built from the real authored `.agent` (never invented; a subagent pending authoring renders as `[pending authoring]`). The theme, recipe, and export rules live in `refs/mermaid-diagrams.md`, anchored to the SLDS design tokens (also captured in `~/.claude/style-conventions.md`). The fenced ` ```mermaid ` block renders natively on GitHub **and live in the artifact's HTML** — `document-shell.html` carries the Mermaid CDN, and `md-to-html.py` emits a ` ```mermaid ` fence as a `<pre class="mermaid">` block (other fenced languages become an escaped `<pre><code>` source block). When `@mermaid-js/mermaid-cli` (`mmdc`) is installed, the diagram also exports to PNG/SVG for the Kickoff (11) / Engagement-Review (12) decks — capability-gated, so a missing `mmdc` skips the export with an install hint rather than blocking the run.

## How it works

A stateful project skill driven by `SKILL.md` in four phases (A–C are org-free; D is opt-in):

- **Phase A — Ingest & Normalize** (interactive): collect inputs, normalize into a `requirements.json` source-of-truth, prompt for build decisions (1GP vs 2GP, target org vs demo instance, agent-in-scope, how to resolve managed-package object references), and present an MVP/PoC opinion for confirmation.
- **Phase B — Generate**: run the artifact generators (packaging analysis, security assessment, gaps doc, SFDX scaffold + perm set), delegate `.agent` authoring and metadata scaffolding, then a barrier synthesis assembles the execution plan + component manifest, populates per-file content hashes, and renders the canvas. Fans out to parallel subagents when the component count exceeds 6.
- **Phase C — Review & Update** (re-entrant): on re-run with new requirements, diff against the stored state, regenerate only affected artifacts, and **preserve hand-edited files** — any file whose on-disk hash diverges from the recorded hash is left untouched and the proposed regeneration is written to a `<name>.regen` sibling for human merge.
- **Phase D — Finalize** (org-connected, opt-in, re-entrant): runs only when explicitly invoked against an authenticated org alias. Two gates — **Gate 1 (validate, non-mutating)** runs by default (deploy dry-run, agent validate, MCP env/reachability); **Gate 2 (deploy, mutating)** is offered only after Gate 1 is green (real deploy, perm-set assign, agent publish, MCP deploy-and-configure + validate-end-to-end). A **production** org requires explicit typed confirmation before any mutating step. Stop-on-first-failure, with a detailed per-failure mitigation block (Symptom / Likely cause / Fix / Resume) written to the `13-finalize-report` artifact.

## How to invoke

> "Use pie-poc-forge to turn <partner>-mvp-build-plan.md into a PoC package."

The skill prompts for the build decisions and presents its MVP/PoC opinion before generating anything.

## Optional: Org62 engagement pre-fill

pie-poc-forge can optionally pre-fill `requirements.json` from an Org62
`Partner_Engagement__c` (partner, pilot customer, opportunity use-case) instead of
relying only on pasted inputs. Pick from your active engagements or paste a
PE/Account/Opportunity ID. Read-only and optional; declining changes nothing.
The org alias comes from `ORG62_ALIAS` (default `org62`); identity is the logged-in
session user.

## Prerequisites (companion skills)

pie-poc-forge orchestrates and delegates by **exact skill name**. For full function, install these alongside it. If one is missing or renamed, the skill **degrades gracefully** — it never hand-authors what the delegate would have produced and never dead-stops the run; it keeps the `DELEGATION PENDING` brief, marks the affected component pending (artifacts `01`/`07`/`08`), generates everything not blocked, and tells you which delegate is missing and to install it and re-run:

| Companion skill | Source | Used for |
|---|---|---|
| `agentforce-adlc` (`developing-agentforce`, `testing-agentforce`, `adlc-engineer`) | `github.com/SalesforceAIResearch/agentforce-adlc` | All agentic work — `.agent` authoring, agent tests, Flow/Apex metadata + deploy |
| `sf-mcp-partner-toolkit` (`setup-workspace`, `scaffold-mcp-integration`, `deploy-and-configure`, `diagnose-connection`, `validate-end-to-end`) | `github.com/mvogelgesang/sf-mcp-partner-toolkit` | All MCP integration work |
| `isv-validate-agentforce` | `github.com/dmckeeSF/isv-validate-agentforce` | The bundle validation gate (packaging/2GP/MCP readiness of the generated agent/MCP/Apex) |

Also requires: Python 3 (stdlib only) for the render/validation scripts, and the Salesforce CLI (`sf`) for any org-connected step. pie-poc-forge runs without these for the planning/canvas artifacts, but agent/MCP generation and the validation gate need the companions present.

## Boundaries

- Delegates **all agentic work** to the **Agentforce ADLC** toolkit (`github.com/SalesforceAIResearch/agentforce-adlc`): `.agent`/aiAuthoringBundle authoring → `developing-agentforce`, agent tests → `testing-agentforce`, deep Flow/Apex metadata + deploy → `adlc-engineer`. Never hand-authors Bot/GenAiPlanner metadata.
- Delegates **all MCP integration work** to the **SF MCP Partner Toolkit** (`github.com/mvogelgesang/sf-mcp-partner-toolkit`): `setup-workspace` → `scaffold-mcp-integration` → `deploy-and-configure` → `diagnose-connection` → `validate-end-to-end`. Never hand-authors MCP registration metadata.
- Writes **honest scaffolding only** — signatures and TODO stubs, never fabricated business logic.
- Phases A–C never deploy. **Phase D (Finalize) is the only deploy path**, and only against an authenticated org — never to production without explicit per-run typed confirmation, and only after Gate-1 validation is green.
- Flags lowered confidence when the Technical & Architectural Assessment is not provided.

## Repository layout

```
SKILL.md                     orchestration: phases, decision prompts, refusal conditions
refs/                        lazy-loaded domain logic (13 files, incl. mermaid-diagrams.md)
templates/                   13 canvas artifact .md sources, shared shell (document-shell.html), output index
scripts/                     md-to-html.py, ensure-home-link.py (flat-layout canvas)
tests/validate_skill.py      stdlib-only validation: structural (skill-forge Tier-3 rubric) + behavioral (render scripts)
tests/fixtures/              golden fixtures for the behavioral script tests
.githooks/pre-commit         runs the validation suite locally
.github/workflows/           runs the validation suite on push/PR
docs/superpowers/            archived spec + plan
```

## Validation

```bash
python3 tests/validate_skill.py
```

Enforces every applicable skill-forge Tier-3 rubric ID (frontmatter, refusal conditions, lazy refs, no dangling/orphan references, token hygiene, registry/index parity, CI hooks, spec/plan archive) **plus behavioral tests** that exercise the render scripts (`md-to-html.py` golden-file render + escaping; `ensure-home-link.py` inject/repair/idempotency) against golden fixtures. Runs automatically via `.githooks/pre-commit` and `.github/workflows/validate.yml`. To activate the hook in a fresh clone:

```bash
git config core.hooksPath .githooks
```

## Status

Built, dogfooded, and validated by a **live interactive run** end-to-end against a representative MVP build plan (agents + Data 360 + Platform, MCP integration, 1GP/2GP packaging). The live run exercised the full interactive flow — input ingestion (build plan + Technical & Architectural Assessment), decision prompts, an opinionated MVP/PoC scope confirmation, and **both mandated delegations against real tooling**: MCP registration metadata generated via `sf-mcp-partner-toolkit` against a live MCP server (introspected, OAuth-secured), and an agent authored via `agentforce-adlc:developing-agentforce` (Agent Spec approval gate + 7-category safety review). Phase-C edit-preservation verified. Gaps surfaced by the live run (plan-vs-built reconciliation, state re-sync, MCP realism) are patched.

**Known remaining limitation:** the agent/MCP CLI lifecycle (`sf agent validate/preview/publish`, `deploy-and-configure`, `validate-end-to-end`) requires an authenticated org, so those steps run live at the build session — the skill produces the org-independent package (scaffold, spec, authored bundle, metadata) up to that point. See [BACKLOG.md](BACKLOG.md) for the feature backlog.

## Related skills

Modeled on `tech-strat-pov-forge`; audited against the `skill-forge` maturity rubric. Both are part of the same PIE / ISV Partner Solutions toolset.
