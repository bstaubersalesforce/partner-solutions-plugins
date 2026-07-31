# PIE-POC-FORGE — Design Spec

**Date:** 2026-06-10
**Author:** Brandon Stauber, Partner Innovation Engineering (PIE) — ISV Partner Solutions Program, Salesforce
**Status:** Approved for planning

---

## 1. Purpose & Identity

**Name:** `pie-poc-forge`

A **Partner Innovation Engineering (PIE)** skill — part of the ISV Partner Solutions Program at Salesforce — that turns a POV MVP build plan, an Agentforce Labs agent output, or pasted requirements into an **installable proof-of-concept distribution package** (deployable SFDX scaffolding + manifest), plus a **canvas** of execution, config, security, and gaps artifacts. The skill is **re-entrant**: it updates the package and canvas as requirements evolve rather than regenerating from scratch.

**Overall goal:** Produce a proof-of-concept distribution package that can be installed into a partner's org or a demo instance — IDE-compatible, with a manifest.

This skill supports the PIE team's function: converting upstream POV/strategy artifacts into hands-on, buildable proof-of-concept assets for partner engagements.

---

## 2. Scope & Boundaries

### Build types supported
The PoC build may target any of:
- **Agents** (Agentforce)
- **Data 360** (Data Cloud)
- **Platform** (custom objects, Apex, LWC, Flow)

…or any combination.

### Owns (generated directly by this skill)
- Requirements normalization into a source-of-truth state file
- An **opinion on the MVP/PoC scope** — what to build first to prove the concept, what to cut, and why
- **Packaging analysis** — 1GP vs 2GP recommendation + per-component metadata-coverage / unsupported-types check
- **SFDX scaffold** — custom object/field XML + Apex/LWC/Flow **stubs** (signatures, headers, TODO bodies — no business logic)
- **Manifests** — `package.xml` + `sfdx-project.json` (IDE-compatible)
- **Pre-instance config** docs
- **Post-config steps** docs
- **Security-review callouts**
- **Gaps document** — key open questions, technical gaps, unresolved architectural items
- The **HTML + Markdown canvas** (output index + per-artifact docs)

### Delegates
- `.agent` / `aiAuthoringBundle` authoring → `agentforce-adlc:developing-agentforce`
- Deep metadata scaffolding / deploy → `agentforce-adlc:adlc-engineer`

### Does NOT
- Write business logic into stubs (honest, deployable scaffold only — humans fill in logic)
- Deploy to production (generates the package only)
- Paper commercials / contracts

---

## 3. Inputs

Accept any of the following; **ask for what is missing** rather than fabricating:

| Input | Role | If absent |
|---|---|---|
| POV **MVP Build Plan** (`.md`) | Primary — features, objects, components, integrations, phases | Ask; or accept pasted requirements |
| POV **Technical & Architectural Assessment** (`.md`) | Feeds the gaps document (Part 1 Well-Architected gaps, Part 3 build-ready spec, Part 4 roadmap) | Ask for it; if still unavailable, build the gaps doc from the build plan alone and **flag lower confidence** |
| **Agentforce Labs** agent output | Agent definition/spec (file or pasted text) | N/A — optional |
| **Free-text / pasted requirements** | Loosely-structured requirements to normalize | N/A |

Reference material for packaging analysis (consulted by the skill, not inputs):
- Metadata Coverage Report
- Unsupported Metadata Types
- 1GP vs 2GP (`dev2gp`) comparison

---

## 4. Outputs

All outputs land in a per-engagement working directory. Two faces: a **distribution package** (IDE-ready SFDX project) and a **canvas** (HTML + MD docs, styled like the POV output index).

### 4.1 Working directory layout
```
<partner>-poc/
├── requirements.json              ← normalized source-of-truth (state for re-runs); listed in .forceignore so it never deploys
├── force-app/main/default/        ← SFDX source (objects, classes, lwc, flows, agents, …)
├── manifest/package.xml           ← deploy manifest
├── sfdx-project.json              ← IDE/project manifest
├── .forceignore                   ← excludes requirements.json and docs/ from deploy
└── docs/                          ← the canvas
    ├── index.html                 ← output index (links every artifact, .md + .html)
    ├── 01-execution-plan
    ├── 02-mvp-pov-opinion
    ├── 03-pre-instance-config
    ├── 04-package-analysis
    ├── 05-post-config-steps
    ├── 06-security-review
    ├── 07-gaps-document
    ├── 08-component-manifest
    └── 09-agentscript             ← conditional (agent builds only)
```

### 4.2 Canvas artifacts (each rendered as `.md` + `.html`)

| # | Artifact | Core content | Condition |
|---|---|---|---|
| 1 | **Execution Plan** | Exec summary + sequenced narrative install/execution plan: install order, deploy steps, owners, task backlog | Always |
| 2 | **MVP / PoC Opinion** | Skill's recommended PoC slice — what to build first to prove the concept, what to cut, and why | Always |
| 3 | **Pre-Instance Config** | Licenses/features/perm sets/remote sites that must exist *before* deploy | Always |
| 4 | **Packaging Analysis** | 1GP vs 2GP recommendation + per-component metadata-coverage / unsupported-types check | Always |
| 5 | **Post-Config Steps** | Activation tasks after deploy (Named Creds, Data 360 streams, agent activation, etc.) | Always |
| 6 | **Security Review** | Flagged issues: sharing, CRUD/FLS, secrets, OAuth scopes, PII-in-transit, Shield needs | Always |
| 7 | **Gaps Document** | Key open questions, technical gaps, unresolved architectural items (ingests Tech & Arch Assessment) | Always |
| 8 | **Component Manifest** | Human-readable inventory: every object/class/LWC/flow, purpose, MVP vs deferred | Always |
| 9 | **Agentscript** | The actual `.agent` document rendered for review (the deployable file lives in `force-app/`) | Agent builds only |

### 4.3 Canvas styling
Reuses the `pov-builder` HTML output method (`document-shell.html` + `md-to-html.py` + `output-index.html` pattern) so PIE outputs match the look of the POV deliverables.

---

## 5. Workflow Architecture (the engine)

Approach-2 stateful project model, executed with workflow/subagent fan-out where parallelism pays off. `SKILL.md` drives a three-phase control flow.

### Phase A — Ingest & Normalize (single pass, interactive)
1. Detect/collect inputs (build plan, arch assessment, Labs output, pasted text). Ask for what's missing.
2. Parse into `requirements.json` — normalized source-of-truth (features, objects, components, integrations, dependencies, security signals, build type: agent / data360 / platform).
3. **Prompt for build decisions:** 1GP vs 2GP; target (partner org vs demo instance); agent-in-scope (yes/no).
4. Present the **MVP/PoC opinion** and confirm scope with the user **before** generating.

### Phase B — Generate (parallel fan-out via Workflow)
Once scope is locked, dispatch independent generators concurrently (read-only on `requirements.json`):
- Packaging analysis (metadata-coverage + 1GP/2GP)
- Security review
- Gaps document (ingests arch assessment)
- SFDX scaffold + manifests → delegates metadata scaffolding to `adlc-engineer`
- Agentscript (if agent in scope) → delegates to `developing-agentforce`

Then a **synthesis step (barrier)** assembles the **execution plan** + **component manifest** from the others' outputs, and renders the full canvas (HTML + MD + index).

**Inline-vs-fanout heuristic:** for a small build plan, Phase B may run inline; the workflow fan-out is used when there are many components/use cases. The skill decides based on component count.

### Phase C — Review & Update (re-entrant)
On re-run with new requirements:
1. Diff new requirements against stored `requirements.json`.
2. Regenerate only affected artifacts + manifest.
3. **Preserve human edits to stubs (explicit mechanism):** `requirements.json` stores a content hash for each generated file. Before overwriting any file, compare its current on-disk content to the stored hash. If they differ, the file has been hand-edited — do NOT overwrite it; instead flag it in the changelog as "preserved — manual edits detected; review needed" and emit the proposed regeneration to a sibling `<name>.regen` file for human merge. Only files matching their stored hash are regenerated in place.
4. Bump a changelog entry in the index (artifacts changed, preserved, added).

---

## 6. Skill Structure, Tiering & Validation

**Tier:** Tier 3 (multi-phase, stateful, delegates to other skills, generates deployable artifacts, validation suite + CI) — same tier as `pov-builder` and `skill-forge`. The skill must satisfy **every** skill-forge rubric ID with min-tier ≤ 3: R-FM-01, R-REF-01, R-ARCH-01..03, R-TEST-01..03, R-CI-01, R-CI-02, R-PROC-01, R-DOC-01, R-GIT-01 (see Validation suite below for the ID→check mapping).

### File structure
```
pie-poc-forge/                     ← OWN git repo (R-GIT-01): git init + initial commit
├── SKILL.md                       ← frontmatter (name + description); lazy-loaded orchestration: 3-phase flow, decision prompts, refusal conditions
├── README.md                      ← what it does + how to invoke (R-DOC-01)
├── refs/                          ← lazy-loaded domain logic (loaded only when that phase runs)
│   ├── requirements-schema.md     ← requirements.json shape (incl. per-file content hashes) + normalization rules
│   ├── packaging-analysis.md      ← 1GP vs 2GP rules + metadata-coverage / unsupported-types logic
│   ├── security-review.md         ← security checklist (sharing, CRUD/FLS, secrets, OAuth, PII, Shield)
│   ├── gaps-document.md           ← how to ingest the Tech & Arch Assessment + extend it
│   ├── sfdx-scaffold.md           ← project layout, manifest generation, stub conventions
│   ├── agentscript-handoff.md     ← when/how to delegate to agentforce-adlc
│   ├── mvp-opinion.md             ← how the skill forms its PoC-scope recommendation
│   └── workflow-dispatch.md       ← Phase-B fan-out script + inline-vs-fanout heuristic
├── templates/                     ← one per canvas artifact (.md + .html), + document-shell/index; {{TOKEN}} placeholders UPPER_SNAKE_CASE
├── scripts/
│   ├── md-to-html.py              ← reused from pov-builder
│   └── ensure-home-link.py        ← reused from pov-builder
├── tests/
│   └── validate_skill.py          ← structural validation (stdlib-only)
├── .githooks/
│   └── pre-commit                 ← runs validate_skill.py (R-CI-01)
├── .github/workflows/
│   └── validate.yml               ← runs validate_skill.py on push/PR (R-CI-02)
└── docs/superpowers/              ← spec→plan archive lives IN THE SKILL REPO (R-PROC-01)
    ├── specs/2026-06-10-pie-poc-forge-design.md   ← this spec, copied in at scaffold time
    └── plans/2026-06-10-pie-poc-forge-plan.md     ← the implementation plan
```

### Validation suite + CI (Tier-3 rubric coverage)
`validate_skill.py` (stdlib-only) asserts every rubric ID applicable at Tier 3:
- **R-FM-01** — `SKILL.md` frontmatter has non-empty `name:` + `description:`.
- **R-REF-01** — refusal/scope conditions present in `SKILL.md`.
- **R-ARCH-01** — domain logic in `refs/`, not inlined.
- **R-ARCH-02** — every referenced path exists (no dangling references).
- **R-ARCH-03** — every file under `refs/`/`templates/`/`scripts/` is referenced (no orphans). `SKILL.md` references `scripts/md-to-html.py` and `scripts/ensure-home-link.py` in the canvas-render step, so the orphan scan covers `scripts/` too.
- **R-TEST-01** — the suite exists and is stdlib-only.
- **R-TEST-02** — token hygiene: every `{{TOKEN}}` is UPPER_SNAKE_CASE with balanced braces.
- **R-TEST-03** — router parity: `output-index.html` (and `output-index` template) ↔ the 9 artifact docs are in bidirectional sync; the conditional agentscript artifact (#9) is allowed to be absent without failing parity.
- **R-DOC-01** — `README.md` present.

**CI:** `.github/workflows/validate.yml` runs the suite on push/PR (R-CI-02). **Pre-commit:** `.githooks/pre-commit` runs the suite (R-CI-01), mirroring `pov-builder`. **Git:** `pie-poc-forge` is initialized as its own git repo with an initial commit (R-GIT-01).

### Refusal / guardrail conditions (in SKILL.md)
- No usable input → ask, don't fabricate.
- Won't write business logic into stubs (honest scaffold).
- Won't deploy to production; generates the package only.
- Flags low confidence when the Tech & Arch Assessment is absent.
- Org62 / data-scrubbing guardrails inherited from CLAUDE.md.

### Reuse
HTML output method from `pov-builder` (`document-shell.html`, `md-to-html.py`, `ensure-home-link.py`, `output-index.html` pattern).

---

## 7. Test Case

A representative MVP Build Plan is the primary real-world validation input — one that exercises agents, Data 360, and Platform (custom objects, an Apex integration service, LWC), a bidirectional MCP integration, and explicit 1GP/2GP packaging notes — covering every build type and the packaging-analysis path.

---

## 8. skill-forge Rubric Compliance (audited 2026-06-10)

Audited against `skill-forge/refs/rubric.md`. Complexity tier **3**; the design now commits to build tier **3** (all gaps closed):

| Gap found | Resolution |
|---|---|
| R-CI-02 — no CI workflow | Added `.github/workflows/validate.yml` (§6) |
| R-PROC-01 — spec/plan archive in wrong location | Archive lives in the skill's own repo at `pie-poc-forge/docs/superpowers/{specs,plans}/` (§6) |
| R-GIT-01 — skill not a git repo | `pie-poc-forge` initialized as its own git repo with initial commit (§6) |
| R-TEST-03 — router parity unspecified | `validate_skill.py` asserts `output-index` ↔ artifact bidirectional sync, with conditional #9 handled (§6) |
| R-ARCH-03 — no-orphans check missing | Added to validation scope (§6) |
| R-TEST-02 — token hygiene missing | Added to validation scope; templates use UPPER_SNAKE_CASE `{{TOKEN}}` (§6) |
| Design — stub-edit preservation under-specified | Content-hash mechanism defined in Phase C (§5) |
| Design — state file deploy risk | `requirements.json` listed in `.forceignore` (§4.1) |

## 9. Open Items

- None blocking. Stub conventions and the exact `requirements.json` schema (including the per-file content-hash map used for edit preservation) are detailed during the planning phase (`refs/requirements-schema.md`, `refs/sfdx-scaffold.md`).
