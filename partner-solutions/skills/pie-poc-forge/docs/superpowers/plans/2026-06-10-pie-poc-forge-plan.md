# PIE-POC-FORGE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `pie-poc-forge` skill — a Tier-3 Salesforce skill that turns a POV MVP build plan, an Agentforce Labs output, or pasted requirements into an installable proof-of-concept SFDX distribution package plus an HTML+Markdown canvas of execution/config/security/gaps artifacts, re-entrant across requirement changes.

**Architecture:** A stateful project skill modeled on `pov-builder`. `SKILL.md` drives a three-phase flow (Ingest→Normalize, parallel Generate fan-out, re-entrant Update). Domain logic lives in lazy-loaded `refs/`; outputs use `templates/` rendered by reused `pov-builder` scripts. A stdlib-only `tests/validate_skill.py` enforces every skill-forge Tier-3 rubric ID and is the test harness for this build — each content file is created to make a previously-failing validator check pass.

**Tech Stack:** Markdown (SKILL.md, refs, templates), Python 3 stdlib (validation + render scripts), HTML/CSS (canvas templates), git + GitHub Actions (CI), Salesforce DX metadata conventions. Delegates `.agent` authoring to `agentforce-adlc:developing-agentforce` and metadata scaffolding to `agentforce-adlc:adlc-engineer`.

**Spec:** `docs/superpowers/specs/2026-06-10-pie-poc-forge-design.md`

**Reference skill (copy patterns from):** `/Users/bstauber/.claude/skills/pov-builder/`

**Build location:** `/Users/bstauber/.claude/skills/pie-poc-forge/` (its own git repo)

---

## File Structure

The skill repo `pie-poc-forge/` contains:

| Path | Responsibility |
|---|---|
| `SKILL.md` | Frontmatter + orchestration: 3-phase flow, decision prompts, delegation, refusal conditions |
| `README.md` | What the skill does + how to invoke it |
| `refs/requirements-schema.md` | `requirements.json` shape (incl. per-file content-hash map) + normalization rules |
| `refs/packaging-analysis.md` | 1GP vs 2GP rules + metadata-coverage / unsupported-types logic |
| `refs/security-review.md` | Security checklist (sharing, CRUD/FLS, secrets, OAuth, PII, Shield) |
| `refs/gaps-document.md` | How to ingest the Tech & Arch Assessment + extend it |
| `refs/sfdx-scaffold.md` | SFDX project layout, manifest generation, stub conventions |
| `refs/agentscript-handoff.md` | When/how to delegate to agentforce-adlc |
| `refs/mvp-opinion.md` | How the skill forms its PoC-scope recommendation |
| `refs/workflow-dispatch.md` | Phase-B fan-out workflow script + inline-vs-fanout heuristic |
| `templates/01-execution-plan.md` / `.html` | Execution plan artifact (always) |
| `templates/02-mvp-pov-opinion.md` / `.html` | MVP/PoC opinion artifact (always) |
| `templates/03-pre-instance-config.md` / `.html` | Pre-instance config artifact (always) |
| `templates/04-package-analysis.md` / `.html` | Packaging analysis artifact (always) |
| `templates/05-post-config-steps.md` / `.html` | Post-config steps artifact (always) |
| `templates/06-security-review.md` / `.html` | Security review artifact (always) |
| `templates/07-gaps-document.md` / `.html` | Gaps document artifact (always) |
| `templates/08-component-manifest.md` / `.html` | Component manifest artifact (always) |
| `templates/09-agentscript.md` / `.html` | Agentscript artifact (conditional — agent builds) |
| `templates/document-shell.html` | Shared HTML shell (copied from pov-builder) |
| `templates/output-index.html` | Canvas index/router (copied + adapted from pov-builder) |
| `scripts/md-to-html.py` | MD→styled-HTML renderer (copied from pov-builder) |
| `scripts/ensure-home-link.py` | Home-link enforcer (copied from pov-builder) |
| `tests/validate_skill.py` | Stdlib-only structural validation suite (the test harness) |
| `.githooks/pre-commit` | Runs the validation suite locally |
| `.github/workflows/validate.yml` | Runs the validation suite on push/PR |
| `docs/superpowers/specs/2026-06-10-pie-poc-forge-design.md` | The spec (copied in) |
| `docs/superpowers/plans/2026-06-10-pie-poc-forge-plan.md` | This plan (copied in) |

**Canvas-artifact registry** (single source of truth used by the validator's parity check):

```
ALWAYS = ["01-execution-plan", "02-mvp-pov-opinion", "03-pre-instance-config",
          "04-package-analysis", "05-post-config-steps", "06-security-review",
          "07-gaps-document", "08-component-manifest"]
CONDITIONAL = ["09-agentscript"]
```

---

## Task 1: Initialize the skill repo with SKILL.md skeleton, README, and git

**Files:**
- Create: `/Users/bstauber/.claude/skills/pie-poc-forge/SKILL.md`
- Create: `/Users/bstauber/.claude/skills/pie-poc-forge/README.md`

- [ ] **Step 1: Create the repo directory and SKILL.md skeleton**

Create `SKILL.md` with valid frontmatter and a refusal section (these satisfy R-FM-01 and R-REF-01; full orchestration is added in Task 8):

```markdown
---
name: pie-poc-forge
description: Use when turning a POV MVP build plan, an Agentforce Labs agent output, or pasted requirements into an installable proof-of-concept SFDX distribution package plus an execution/config/security/gaps canvas — for Partner Innovation Engineering (PIE) partner engagements.
---

# PIE-POC-FORGE

## Overview
A Partner Innovation Engineering (PIE) skill — part of the ISV Partner Solutions Program at Salesforce. It converts upstream POV/strategy artifacts into a hands-on, installable proof-of-concept: a deployable SFDX package (scaffolding + manifest) and a canvas of execution, config, security, and gaps artifacts. Re-entrant: it updates the package as requirements evolve rather than regenerating from scratch.

## Refusal / Scope Conditions
This skill does NOT do whatever it is asked. Stop and clarify or refuse when:
- **No usable input** — no build plan, Labs output, or pasted requirements. Ask; do not fabricate requirements.
- **Business logic requested in stubs** — generated Apex/LWC/Flow are signatures + TODO scaffolding only. Refuse to invent business-logic bodies.
- **Production deploy requested** — this skill generates the package only; it never deploys to production.
- **Missing Technical & Architectural Assessment** — proceed using the build plan alone but flag lowered confidence in the gaps document.
- **Org62 / data guardrails** (inherited from CLAUDE.md) — scrub partner data before external use; no destructive org commands without confirmation.

<!-- Full orchestration (Phases A/B/C) added in Task 8. -->
```

- [ ] **Step 2: Create README.md**

```markdown
# pie-poc-forge

A Partner Innovation Engineering (PIE) skill for the ISV Partner Solutions Program at Salesforce.

## What it does
Turns a POV MVP build plan, an Agentforce Labs agent output, or pasted requirements into:
- an installable proof-of-concept **SFDX distribution package** (deployable scaffolding + `package.xml` + `sfdx-project.json`), and
- a **canvas** of HTML+Markdown artifacts: execution plan, MVP/PoC opinion, pre-instance config, packaging analysis (1GP vs 2GP), post-config steps, security review, gaps document, component manifest, and — for agent builds — the agentscript.

It is re-entrant: re-run it with new requirements and it updates only what changed, preserving hand-edited files.

## How to invoke
Ask Claude to build a PoC package from a build plan, e.g.:
> "Use pie-poc-forge to turn <partner>-mvp-build-plan.md into a PoC package."

The skill prompts for build decisions (1GP vs 2GP, target org vs demo instance, agent-in-scope) and presents an MVP/PoC opinion before generating.

## Boundaries
Delegates `.agent` authoring to `agentforce-adlc:developing-agentforce` and deep metadata scaffolding to `agentforce-adlc:adlc-engineer`. Does not deploy to production or write business logic into stubs.

## Validation
`python3 tests/validate_skill.py` enforces the structural invariants (skill-forge Tier-3 rubric). Run automatically via `.githooks/pre-commit` and `.github/workflows/validate.yml`.
```

- [ ] **Step 3: Initialize git and make the first commit**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
git init
git add SKILL.md README.md
git commit -m "feat: scaffold pie-poc-forge skill (frontmatter, refusal conditions, README)"
```

Expected: a git repo with one commit (satisfies R-GIT-01 baseline).

---

## Task 2: Build the validation harness with frontmatter + refusal checks (TDD)

**Files:**
- Create: `/Users/bstauber/.claude/skills/pie-poc-forge/tests/validate_skill.py`

- [ ] **Step 1: Write the validation harness with the first two checks**

Create `tests/validate_skill.py`. This is the skill's test suite; checks added here cover R-FM-01 and R-REF-01:

```python
#!/usr/bin/env python3
"""
Validation suite for the pie-poc-forge skill. Stdlib-only.

Asserts the structural invariants that must hold for the skill to run correctly
and to satisfy the skill-forge Tier-3 rubric. It validates files, references,
tokens, and router parity — it does NOT judge LLM output quality.

Run:   python3 tests/validate_skill.py
Exit:  0 = all pass, 1 = one or more failures.
"""
import os, re, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- tiny test harness --------------------------------------------------
RESULTS = []
def check(name):
    def deco(fn):
        RESULTS.append((name, fn)); return fn
    return deco

def read(rel):
    with open(os.path.join(SKILL, rel), encoding="utf-8") as f:
        return f.read()

def exists(rel):
    return os.path.exists(os.path.join(SKILL, rel))

# ---- canvas-artifact registry (single source of truth) ------------------
ALWAYS = ["01-execution-plan", "02-mvp-pov-opinion", "03-pre-instance-config",
          "04-package-analysis", "05-post-config-steps", "06-security-review",
          "07-gaps-document", "08-component-manifest"]
CONDITIONAL = ["09-agentscript"]
ALL_ARTIFACTS = ALWAYS + CONDITIONAL

# SKILL.md is the only instruction file for this skill (no refs/stages router).
INSTRUCTION_FILES = ["SKILL.md"]
def instructions():
    return "\n".join(read(f) for f in INSTRUCTION_FILES if exists(f))

TOKEN_RE = re.compile(r"\{\{([^{}]*)\}\}")

# ---- R-FM-01: frontmatter ----------------------------------------------
@check("R-FM-01: SKILL.md opens with frontmatter carrying non-empty name + description")
def t_frontmatter():
    s = read("SKILL.md")
    m = re.match(r"^---\n(.*?)\n---\n", s, re.S)
    assert m, "SKILL.md must open with a YAML frontmatter block"
    fm = m.group(1)
    name = re.search(r"^name:\s*(\S.*)$", fm, re.M)
    desc = re.search(r"^description:\s*(\S.*)$", fm, re.M)
    assert name and name.group(1).strip(), "frontmatter missing non-empty name:"
    assert desc and desc.group(1).strip(), "frontmatter missing non-empty description:"

# ---- R-REF-01: refusal conditions present ------------------------------
@check("R-REF-01: SKILL.md states refusal/scope conditions")
def t_refusal_present():
    s = read("SKILL.md").lower()
    assert "refusal" in s or "scope conditions" in s, \
        "SKILL.md must have a refusal/scope-conditions section"
    assert "does not" in s or "do not" in s or "refuse" in s, \
        "refusal section must state what the skill will not do"

# ---- runner -------------------------------------------------------------
def main():
    failed = 0
    for name, fn in RESULTS:
        try:
            fn(); print(f"PASS  {name}")
        except AssertionError as e:
            failed += 1; print(f"FAIL  {name}\n      {e}")
    print(f"\n{len(RESULTS)-failed}/{len(RESULTS)} checks passed")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the suite to verify the two checks pass**

Run: `cd /Users/bstauber/.claude/skills/pie-poc-forge && python3 tests/validate_skill.py`
Expected: `PASS R-FM-01...`, `PASS R-REF-01...`, `2/2 checks passed`, exit 0.

- [ ] **Step 3: Commit**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
git add tests/validate_skill.py
git commit -m "test: add validation harness with R-FM-01 + R-REF-01 checks"
```

---

## Task 3: Add the refs/ checks, then create the refs files (TDD)

**Files:**
- Modify: `/Users/bstauber/.claude/skills/pie-poc-forge/tests/validate_skill.py`
- Create: 8 files under `/Users/bstauber/.claude/skills/pie-poc-forge/refs/`
- Modify: `/Users/bstauber/.claude/skills/pie-poc-forge/SKILL.md` (reference the refs so they aren't orphans)

- [ ] **Step 1: Add R-ARCH-01/02/03 checks to validate_skill.py**

Insert these checks before the `# ---- runner` section:

```python
# ---- R-ARCH-01: refs/ directory exists and holds the domain logic -------
EXPECTED_REFS = [
    "refs/requirements-schema.md", "refs/packaging-analysis.md",
    "refs/security-review.md", "refs/gaps-document.md",
    "refs/sfdx-scaffold.md", "refs/agentscript-handoff.md",
    "refs/mvp-opinion.md", "refs/workflow-dispatch.md",
]

@check("R-ARCH-01: refs/ exists and SKILL.md stays lean (domain logic externalized)")
def t_refs_dir():
    assert os.path.isdir(os.path.join(SKILL, "refs")), "refs/ directory missing"
    assert len(read("SKILL.md")) < 20000, \
        "SKILL.md too large — domain logic belongs in refs/"

# ---- R-ARCH-02: every referenced path exists ----------------------------
@check("R-ARCH-02: every file path referenced in the instructions exists")
def t_refs_exist():
    skill = instructions()
    paths = set(re.findall(r"(?:templates|refs|validation|scripts)/[A-Za-z0-9._/-]+", skill))
    missing = [p.rstrip(".") for p in paths if not exists(p.rstrip("."))]
    assert not missing, f"referenced but missing: {sorted(missing)}"

# ---- R-ARCH-03: no orphans under refs/ templates/ scripts/ --------------
@check("R-ARCH-03: every file under refs/ templates/ scripts/ is referenced (no orphans)")
def t_no_orphans():
    skill = instructions()
    orphans = []
    for d in ("refs", "templates", "scripts"):
        dpath = os.path.join(SKILL, d)
        if not os.path.isdir(dpath): continue
        for f in os.listdir(dpath):
            if f.startswith(".") or f == "__pycache__": continue
            if not os.path.isfile(os.path.join(dpath, f)): continue
            if f"{d}/{f}" not in skill: orphans.append(f"{d}/{f}")
    assert not orphans, f"present but never referenced: {sorted(orphans)}"

@check("All 8 expected refs/ files exist")
def t_expected_refs_exist():
    missing = [r for r in EXPECTED_REFS if not exists(r)]
    assert not missing, f"expected refs missing: {missing}"
```

- [ ] **Step 2: Run the suite to verify the new checks FAIL**

Run: `cd /Users/bstauber/.claude/skills/pie-poc-forge && python3 tests/validate_skill.py`
Expected: FAIL on `t_expected_refs_exist` (refs not created yet) and `t_no_orphans`/`t_refs_exist` are still green (nothing references missing files yet). This confirms the checks are wired.

- [ ] **Step 3: Create the 8 refs/ files**

Each file is a focused domain-logic doc. Create them with these exact contents (headings are the contract; prose may be expanded but the named sections must remain):

`refs/requirements-schema.md`:
```markdown
# requirements.json — schema & normalization

The normalized source-of-truth for a PoC engagement. Lives at the package root and is listed in `.forceignore` so it never deploys.

## Top-level shape
- `partner` — string (slug-able partner name)
- `buildTypes` — array subset of `["agent","data360","platform"]`
- `decisions` — `{ packaging: "1GP"|"2GP", target: "partnerOrg"|"demoInstance", agentInScope: bool }`
- `mvpOpinion` — the confirmed PoC scope (set after Phase A step 4)
- `features` — array of `{ id, title, persona, userStory, acceptanceCriteria[] }`
- `objects` — array of `{ apiName, fields[], relationships[] }`
- `components` — array of `{ name, type, responsibility, phase }`
- `integrations` — array of `{ system, type, direction, auth }`
- `dependencies` — array of `{ name, type, mustHave, status }`
- `securitySignals` — array of free-text risks for the security-review generator
- `confidence` — float 0.0–1.0 (lowered if Tech & Arch Assessment absent)
- `fileHashes` — map of `generated/file/path -> sha256` (edit-preservation; see below)

## Normalization rules
- Map POV MVP Build Plan sections → fields above (Feature Breakdown → features, Technical Requirements → objects/components/integrations, Dependencies & Blockers → dependencies).
- Agentforce Labs output → one agent component + agentInScope=true.
- Pasted free-text → best-effort parse; flag every inferred field as `"inferred": true`.

## Edit-preservation (fileHashes)
On generation, store `sha256` of each written file. On re-run, before overwriting, recompute and compare; if it differs, the file was hand-edited — do not overwrite (see refs/workflow-dispatch.md Phase C).
```

`refs/packaging-analysis.md`:
```markdown
# Packaging analysis — 1GP vs 2GP + metadata coverage

## Decision inputs
Read `decisions.packaging` and the component inventory. Produce the `04-package-analysis` artifact.

## 1GP vs 2GP rules
- **2GP (recommend by default for PoC):** source-driven, IDE-friendly, supports `sfdx-project.json` package directories, easier versioning, no Dev Hub namespace lock-in for unlocked packages. Reference: dev2gp comparison.
- **1GP:** choose only when the partner's existing managed package is 1GP and the PoC must extend it in place.
- Always state the recommendation, the reason, and the one fact that would flip it.

## Metadata coverage check
For every component in the inventory, classify:
- **Packageable** — supported in the chosen packaging model per the Metadata Coverage Report.
- **Unsupported / manual** — appears in the Unsupported Metadata Types list → moves to pre/post-config as a manual step, NOT into the package.
Emit a per-component table: component | type | packageable? | coverage note | action.

## Reference sources (consult, cite by name)
- Metadata Coverage Report
- Unsupported Metadata Types
- 1GP vs 2GP (dev2gp) comparison
```

`refs/security-review.md`:
```markdown
# Security review checklist

Produce the `06-security-review` artifact from `securitySignals` + the component/integration inventory. Flag issues; do not silently pass.

## Checklist (one finding row per applicable item)
- **Sharing model** — every custom object has an explicit sharing decision (private/public/controlled-by-parent).
- **CRUD/FLS** — Apex marked `with sharing`; stubs note `Security.stripInaccessible` / `WITH SECURITY_ENFORCED` obligations.
- **Secrets** — no hardcoded keys; external auth via Named Credential, never inline.
- **OAuth scopes** — least-privilege scopes named for each integration.
- **PII in transit** — flag any payload crossing an org boundary (esp. external AI stacks); recommend minimization.
- **Shield** — flag regulated data (KYC/AML, lending, health) needing Platform Encryption + Event Monitoring.

## Output format
Table: finding | severity (Critical/High/Medium/Low) | component | recommendation | owner.
End with a "Security review verdict: Go / Conditional-Go / Not-ready" line.
```

`refs/gaps-document.md`:
```markdown
# Gaps document — ingest & extend the Tech & Arch Assessment

Produce the `07-gaps-document` artifact.

## If the Technical & Architectural Assessment is provided
Ingest its Part 1 (Well-Architected gaps), Part 3 (build-ready spec gaps), and Part 4 (gap-closing roadmap). Carry forward each open `[TBD]` and Top-3 technical risk as a gap row.

## If it is absent
Build the gaps doc from the build plan alone and set `confidence` lower; add a banner: "Tech & Arch Assessment not provided — gaps derived from build plan only; confidence reduced."

## Gap categories (each gets a section)
- **Open questions** — unresolved decisions blocking build.
- **Technical gaps** — missing architecture detail, unproven integrations, undefined data model.
- **Architectural items** — scale, security topology, residency, packaging decisions still open.

## Output format
Per gap: id | category | description | blocks (what it blocks) | owner | target. Lead each section with the single highest-severity gap.
```

`refs/sfdx-scaffold.md`:
```markdown
# SFDX scaffold — project layout, manifests, stub conventions

## Project layout
```
<partner>-poc/
  force-app/main/default/{objects,classes,lwc,flows,...}
  manifest/package.xml
  sfdx-project.json
  .forceignore   (excludes requirements.json and docs/)
```

## Manifests
- `sfdx-project.json` — `sourceApiVersion` 66.0; one packageDirectory (`force-app`); namespace empty for PoC unless partner specifies.
- `package.xml` — one `<types>` block per metadata type present, members enumerated from the component inventory; `<version>66.0</version>`.

## Stub conventions (honest scaffold — NO business logic)
- Apex: `public with sharing class X { /* Serves: <use case>. TODO (build): <intent> */ }` — signatures only.
- LWC: component skeleton with `@api` props + TODO; template with structural comment only.
- Objects/fields: full `*-meta.xml` (these are real, deployable config, not stubs).
- Every stub header cites the source feature/use case for traceability.

## Delegation
Real metadata scaffolding is delegated to `agentforce-adlc:adlc-engineer`; this ref defines the layout/manifest contract that delegation must satisfy.
```

`refs/agentscript-handoff.md`:
```markdown
# Agentscript handoff to agentforce-adlc

## When
Only when `decisions.agentInScope` is true (build involves an Agentforce agent).

## Handoff
- Authoring the `.agent` / aiAuthoringBundle is delegated to `agentforce-adlc:developing-agentforce`.
- Pass it: the agent's purpose, the subagent/topic breakdown from the build plan, the actions/tools it must call, and any MCP integration contracts from `integrations`.
- The returned `.agent` file lands in `force-app/main/default/`; render a review copy into the `09-agentscript` canvas artifact.

## If agentInScope is false
Skip entirely; the `09-agentscript` artifact is omitted (the validator's router parity allows its absence).
```

`refs/mvp-opinion.md`:
```markdown
# MVP / PoC opinion — how to form the recommendation

Produce the `02-mvp-pov-opinion` artifact AND confirm it with the user in Phase A step 4 before generating.

## Method
1. Identify the single "hero" use case — the one that proves the concept end-to-end and exercises the most architectural layers.
2. Recommend building that hero slice first; explicitly name what to CUT from the MVP and why (defer to Horizon 1+).
3. State the proof the PoC must demonstrate (the riskiest assumption it pressure-tests).
4. Be opinionated: give one recommended scope, not a menu. Name the one trade-off a reviewer might push back on.

## Output format
- **Recommended PoC scope:** <hero use case, one sentence>
- **Build first / cut for now** table.
- **What this proves:** <the riskiest assumption>
- **The trade-off worth a conversation:** <one line>
```

`refs/workflow-dispatch.md`:
```markdown
# Workflow dispatch — Phase B fan-out + Phase C update

## Inline-vs-fanout heuristic
- Component count (objects + components + integrations) ≤ 6 → run generators inline, sequentially.
- > 6 → dispatch the Phase-B generators as parallel subagents (Workflow), then a barrier synthesis step.

## Phase B generators (independent, read-only on requirements.json)
1. Packaging analysis (refs/packaging-analysis.md)
2. Security review (refs/security-review.md)
3. Gaps document (refs/gaps-document.md)
4. SFDX scaffold + manifests (refs/sfdx-scaffold.md → delegate to adlc-engineer)
5. Agentscript (refs/agentscript-handoff.md → delegate to developing-agentforce) — only if agentInScope

## Barrier synthesis (needs all of the above)
Assemble `01-execution-plan` and `08-component-manifest` from the generators' outputs, then render the full canvas (md→html via scripts/md-to-html.py, then scripts/ensure-home-link.py over the docs dir).

## Phase C — re-entrant update
1. Diff new requirements vs stored requirements.json.
2. Regenerate only affected artifacts + manifest.
3. Edit-preservation: for each file, compare on-disk sha256 to `fileHashes`. If different, do NOT overwrite — write `<name>.regen` beside it and flag "preserved — manual edits detected; review needed" in the changelog.
4. Bump a changelog entry in the index (changed / preserved / added).
```

- [ ] **Step 4: Reference all 8 refs in SKILL.md so they aren't orphans**

Add this block to `SKILL.md` (replace the `<!-- Full orchestration ... -->` comment from Task 1):

```markdown
## Domain references (lazy-loaded)
Load the relevant ref only when its phase runs:
- `refs/requirements-schema.md` — normalize inputs into `requirements.json` (Phase A).
- `refs/mvp-opinion.md` — form the MVP/PoC recommendation (Phase A step 4).
- `refs/packaging-analysis.md` — 1GP vs 2GP + metadata coverage (Phase B).
- `refs/security-review.md` — security findings (Phase B).
- `refs/gaps-document.md` — gaps from the Tech & Arch Assessment (Phase B).
- `refs/sfdx-scaffold.md` — project layout, manifests, stub conventions (Phase B).
- `refs/agentscript-handoff.md` — delegate `.agent` authoring (Phase B, conditional).
- `refs/workflow-dispatch.md` — fan-out heuristic + Phase C update logic.
```

- [ ] **Step 5: Run the suite to verify all refs checks pass**

Run: `cd /Users/bstauber/.claude/skills/pie-poc-forge && python3 tests/validate_skill.py`
Expected: all checks PASS (frontmatter, refusal, refs_dir, refs_exist, no_orphans, expected_refs_exist), exit 0.

- [ ] **Step 6: Commit**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
git add tests/validate_skill.py SKILL.md refs/
git commit -m "feat: add 8 domain refs + R-ARCH-01/02/03 checks"
```

---

## Task 4: Add template checks (token hygiene + router parity), then create templates (TDD)

**Files:**
- Modify: `/Users/bstauber/.claude/skills/pie-poc-forge/tests/validate_skill.py`
- Create: 18 artifact templates + shell + index under `templates/`
- Modify: `/Users/bstauber/.claude/skills/pie-poc-forge/SKILL.md` (reference templates)

- [ ] **Step 1: Add R-TEST-02 (token hygiene) and R-TEST-03 (router parity) checks**

Insert before the `# ---- runner` section:

```python
# ---- R-TEST-02: token hygiene -------------------------------------------
@check("R-TEST-02: every {{TOKEN}} in templates is UPPER_SNAKE_CASE with balanced braces")
def t_token_hygiene():
    tdir = os.path.join(SKILL, "templates")
    bad = []
    for f in os.listdir(tdir):
        if not (f.endswith(".html") or f.endswith(".md")): continue
        text = read(f"templates/{f}")
        # balanced braces: no stray single { } around tokens
        for tok in TOKEN_RE.findall(text):
            if not re.fullmatch(r"[A-Z0-9_]+", tok):
                bad.append(f"templates/{f}: {{{{{tok}}}}}")
    assert not bad, f"malformed tokens: {bad}"

# ---- R-TEST-03: canvas router parity ------------------------------------
@check("R-TEST-03: output-index template and artifact templates are in bidirectional sync")
def t_router_parity():
    index = read("templates/output-index.html")
    # Every ALWAYS artifact must have md+html templates AND be named in the index.
    missing_files, not_in_index = [], []
    for a in ALWAYS:
        if not exists(f"templates/{a}.md"): missing_files.append(f"templates/{a}.md")
        if not exists(f"templates/{a}.html"): missing_files.append(f"templates/{a}.html")
        if a not in index: not_in_index.append(a)
    # CONDITIONAL artifact: templates must exist, index reference is optional (may be absent at runtime).
    for a in CONDITIONAL:
        if not exists(f"templates/{a}.md"): missing_files.append(f"templates/{a}.md")
        if not exists(f"templates/{a}.html"): missing_files.append(f"templates/{a}.html")
    assert not missing_files, f"artifact templates missing: {missing_files}"
    assert not not_in_index, f"ALWAYS artifacts absent from output-index.html: {not_in_index}"

@check("Shared shell + index templates exist")
def t_shell_index_exist():
    for rel in ("templates/document-shell.html", "templates/output-index.html"):
        assert exists(rel), f"{rel} missing"
```

- [ ] **Step 2: Run the suite to verify the new checks FAIL**

Run: `cd /Users/bstauber/.claude/skills/pie-poc-forge && python3 tests/validate_skill.py`
Expected: FAIL on `t_shell_index_exist` and `t_router_parity` (templates not created yet). Confirms wiring.

- [ ] **Step 3: Copy the shared shell from pov-builder**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
mkdir -p templates
cp /Users/bstauber/.claude/skills/pov-builder/templates/document-shell.html templates/document-shell.html
```

- [ ] **Step 4: Create the output-index.html template**

Create `templates/output-index.html` adapting pov-builder's index. It must name every ALWAYS artifact slug (the parity check greps for them). Use the same `<head>`/styling as `document-shell.html`. Body must contain the 8 ALWAYS slugs as link cards plus a changelog slot:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{PARTNER}} — PoC Package</title>
<link rel="stylesheet" href="poc-shell.css">
</head>
<body>
<header><h1>{{PARTNER}} — Proof-of-Concept Package</h1>
<p>Generated {{DATE}} · Build types: {{BUILD_TYPES}}</p></header>
<main>
<section class="cards">
  <a class="card" href="01-execution-plan.html"><h3>01 · Execution Plan</h3></a>
  <a class="card" href="02-mvp-pov-opinion.html"><h3>02 · MVP / PoC Opinion</h3></a>
  <a class="card" href="03-pre-instance-config.html"><h3>03 · Pre-Instance Config</h3></a>
  <a class="card" href="04-package-analysis.html"><h3>04 · Packaging Analysis</h3></a>
  <a class="card" href="05-post-config-steps.html"><h3>05 · Post-Config Steps</h3></a>
  <a class="card" href="06-security-review.html"><h3>06 · Security Review</h3></a>
  <a class="card" href="07-gaps-document.html"><h3>07 · Gaps Document</h3></a>
  <a class="card" href="08-component-manifest.html"><h3>08 · Component Manifest</h3></a>
  <!-- 09-agentscript card injected at runtime only when agentInScope -->
</section>
<section class="changelog"><h2>Changelog</h2>{{CHANGELOG}}</section>
</main>
</body>
</html>
```

- [ ] **Step 5: Create the 9 markdown artifact templates**

Create each `templates/NN-*.md` with the section structure from its ref. Tokens UPPER_SNAKE_CASE. Example for `templates/01-execution-plan.md`:

```markdown
# {{PARTNER}} — Execution Plan

**Generated:** {{DATE}} · **Build types:** {{BUILD_TYPES}} · **Packaging:** {{PACKAGING}} · **Target:** {{TARGET}}

## Executive Summary
{{EXEC_SUMMARY}}

## Install Order
{{INSTALL_ORDER}}

## Deploy Steps
{{DEPLOY_STEPS}}

## Task Backlog
{{TASK_BACKLOG}}
```

Create the remaining eight following their refs' "Output format" sections, each with a `# {{PARTNER}} — <Title>` H1 and tokenized body sections:
- `templates/02-mvp-pov-opinion.md` — Recommended PoC scope, Build first/cut table, What this proves, The trade-off ({{RECOMMENDED_SCOPE}}, {{BUILD_FIRST_TABLE}}, {{WHAT_THIS_PROVES}}, {{TRADE_OFF}}).
- `templates/03-pre-instance-config.md` — Required licenses/features/perm sets/remote sites ({{PRECONFIG_TABLE}}).
- `templates/04-package-analysis.md` — 1GP/2GP recommendation + coverage table ({{PACKAGING_RECOMMENDATION}}, {{COVERAGE_TABLE}}).
- `templates/05-post-config-steps.md` — Post-deploy activation tasks ({{POSTCONFIG_TABLE}}).
- `templates/06-security-review.md` — Findings table + verdict ({{SECURITY_FINDINGS}}, {{SECURITY_VERDICT}}).
- `templates/07-gaps-document.md` — Open questions / technical gaps / architectural items ({{OPEN_QUESTIONS}}, {{TECH_GAPS}}, {{ARCH_ITEMS}}, {{CONFIDENCE_BANNER}}).
- `templates/08-component-manifest.md` — Component inventory table ({{COMPONENT_INVENTORY}}).
- `templates/09-agentscript.md` — Rendered agentscript review ({{AGENTSCRIPT_BODY}}).

- [ ] **Step 6: Create the 9 HTML artifact templates**

For each artifact create `templates/NN-*.html`. These are thin — each is rendered by `md-to-html.py` from the `.md`, so each HTML file is a copy of `document-shell.html` (which already carries the `{{TOKEN}}` slots `md-to-html.py` fills). Simplest correct approach:

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
for n in 01-execution-plan 02-mvp-pov-opinion 03-pre-instance-config 04-package-analysis \
         05-post-config-steps 06-security-review 07-gaps-document 08-component-manifest 09-agentscript; do
  cp templates/document-shell.html "templates/$n.html"
done
```

(The render step overwrites these per-run with filled content; they exist in the repo so the parity check passes and the IDE has a static preview.)

- [ ] **Step 7: Reference templates + scripts in SKILL.md**

Add to `SKILL.md`:

```markdown
## Output templates & rendering
Canvas artifacts render from `templates/` into the engagement `docs/` dir:
- Artifact bodies: `templates/01-execution-plan.md` … `templates/09-agentscript.md` (09 only when agentInScope).
- Shared shell: `templates/document-shell.html`; index: `templates/output-index.html`.
- Render Markdown → HTML with `scripts/md-to-html.py`, then run `scripts/ensure-home-link.py` over the docs dir to guarantee the back-link on every artifact.
```

- [ ] **Step 8: Run the suite to verify template checks pass**

Run: `cd /Users/bstauber/.claude/skills/pie-poc-forge && python3 tests/validate_skill.py`
Expected: all PASS including token hygiene, router parity, shell/index exist. (`t_no_orphans` now also covers the new templates — all are referenced via SKILL.md or are shell/index named in the render section and parity check.)

Note: `t_no_orphans` greps SKILL.md for `templates/<file>`. The per-artifact templates are named by range in SKILL.md ("01-execution-plan.md … 09-agentscript.md"), which is NOT a literal match for each file. To keep them from being flagged as orphans, ensure SKILL.md lists each artifact slug explicitly OR adjust `t_no_orphans` to treat `templates/NN-*.md/.html` as referenced when the slug appears in `output-index.html`. Implement the latter: in `t_no_orphans`, before flagging, also check membership in `read("templates/output-index.html")` and the registry `ALL_ARTIFACTS`.

- [ ] **Step 9: Apply the orphan-exemption refinement**

Update `t_no_orphans` to treat registry artifacts as referenced:

```python
    index_txt = read("templates/output-index.html") if exists("templates/output-index.html") else ""
    registry_slugs = {f"{a}.md" for a in ALL_ARTIFACTS} | {f"{a}.html" for a in ALL_ARTIFACTS}
    ...
            rel = f"{d}/{f}"
            if rel in skill: continue
            if d == "templates" and (f in registry_slugs or f in index_txt): continue
            if rel not in skill: orphans.append(rel)
```

Re-run: `python3 tests/validate_skill.py` → expected all PASS.

- [ ] **Step 10: Commit**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
git add tests/validate_skill.py SKILL.md templates/
git commit -m "feat: add 9 canvas artifact templates + shell/index + token/parity checks"
```

---

## Task 5: Copy the render scripts and add a presence check (TDD)

**Files:**
- Modify: `/Users/bstauber/.claude/skills/pie-poc-forge/tests/validate_skill.py`
- Create: `scripts/md-to-html.py`, `scripts/ensure-home-link.py`

- [ ] **Step 1: Add a scripts-present check**

Insert before the runner:

```python
@check("Render scripts present")
def t_scripts_exist():
    for rel in ("scripts/md-to-html.py", "scripts/ensure-home-link.py"):
        assert exists(rel), f"{rel} missing"
```

- [ ] **Step 2: Run to verify it FAILS**

Run: `python3 tests/validate_skill.py` → expected FAIL on `t_scripts_exist`.

- [ ] **Step 3: Copy the scripts from pov-builder**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
mkdir -p scripts
cp /Users/bstauber/.claude/skills/pov-builder/scripts/md-to-html.py scripts/md-to-html.py
cp /Users/bstauber/.claude/skills/pov-builder/scripts/ensure-home-link.py scripts/ensure-home-link.py
```

- [ ] **Step 4: Run to verify all checks pass**

Run: `python3 tests/validate_skill.py` → expected all PASS (scripts are already referenced in SKILL.md from Task 4 step 7, so no orphans).

- [ ] **Step 5: Commit**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
git add tests/validate_skill.py scripts/
git commit -m "feat: reuse pov-builder render scripts (md-to-html, ensure-home-link)"
```

---

## Task 6: Add the pre-commit hook and CI workflow (R-CI-01, R-CI-02)

**Files:**
- Create: `.githooks/pre-commit`
- Create: `.github/workflows/validate.yml`
- Modify: `/Users/bstauber/.claude/skills/pie-poc-forge/tests/validate_skill.py`

- [ ] **Step 1: Add R-CI-01 / R-CI-02 presence checks**

Insert before the runner:

```python
@check("R-CI-01: tracked .githooks/pre-commit runs the validation suite")
def t_precommit_hook():
    assert exists(".githooks/pre-commit"), ".githooks/pre-commit missing"
    assert "validate_skill.py" in read(".githooks/pre-commit"), \
        "pre-commit hook does not run validate_skill.py"

@check("R-CI-02: CI workflow runs the validation suite")
def t_ci_workflow():
    wdir = os.path.join(SKILL, ".github/workflows")
    assert os.path.isdir(wdir), ".github/workflows missing"
    yml = "\n".join(read(f".github/workflows/{f}") for f in os.listdir(wdir) if f.endswith(".yml"))
    assert "validate_skill.py" in yml, "no workflow runs validate_skill.py"
```

- [ ] **Step 2: Run to verify both FAIL**

Run: `python3 tests/validate_skill.py` → expected FAIL on `t_precommit_hook`, `t_ci_workflow`.

- [ ] **Step 3: Create the pre-commit hook**

Create `.githooks/pre-commit` (adapted from pov-builder):

```sh
#!/bin/sh
# pie-poc-forge pre-commit hook — runs the skill validation suite.
# Activate once per clone with: git config core.hooksPath .githooks
root="$(git rev-parse --show-toplevel)"
if ! command -v python3 >/dev/null 2>&1; then
  echo "pre-commit: python3 not found — cannot run skill validation." >&2
  exit 1
fi
python3 "$root/tests/validate_skill.py"
status=$?
if [ "$status" -ne 0 ]; then
  echo "" >&2
  echo "pre-commit: skill validation FAILED — commit aborted." >&2
  echo "Fix the checks above, or bypass with: git commit --no-verify" >&2
fi
exit "$status"
```

Make it executable and activate the hooks path:

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
```

- [ ] **Step 4: Create the CI workflow**

Create `.github/workflows/validate.yml`:

```yaml
name: Validate skill
on:
  push:
    branches: [main]
  pull_request:
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - name: Run validation suite
        run: python3 tests/validate_skill.py
```

- [ ] **Step 5: Run to verify all checks pass**

Run: `python3 tests/validate_skill.py` → expected all PASS.

- [ ] **Step 6: Commit (exercises the hook)**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
git add tests/validate_skill.py .githooks/pre-commit .github/workflows/validate.yml
git commit -m "ci: add pre-commit hook + GitHub Actions validation (R-CI-01, R-CI-02)"
```

Expected: the pre-commit hook runs `validate_skill.py`, prints all PASS, and the commit succeeds.

---

## Task 7: Archive the spec and plan in the skill repo (R-PROC-01)

**Files:**
- Create: `docs/superpowers/specs/2026-06-10-pie-poc-forge-design.md` (copy)
- Create: `docs/superpowers/plans/2026-06-10-pie-poc-forge-plan.md` (copy)
- Modify: `/Users/bstauber/.claude/skills/pie-poc-forge/tests/validate_skill.py`

- [ ] **Step 1: Add R-PROC-01 check**

Insert before the runner:

```python
@check("R-PROC-01: spec→plan archive exists under docs/superpowers/")
def t_spec_plan_archive():
    specs = os.path.join(SKILL, "docs/superpowers/specs")
    plans = os.path.join(SKILL, "docs/superpowers/plans")
    assert os.path.isdir(specs) and any(f.endswith(".md") for f in os.listdir(specs)), \
        "no spec under docs/superpowers/specs/"
    assert os.path.isdir(plans) and any(f.endswith(".md") for f in os.listdir(plans)), \
        "no plan under docs/superpowers/plans/"
```

- [ ] **Step 2: Run to verify it FAILS**

Run: `python3 tests/validate_skill.py` → expected FAIL on `t_spec_plan_archive`.

- [ ] **Step 3: Copy the spec and plan into the skill repo**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
mkdir -p docs/superpowers/specs docs/superpowers/plans
cp /Users/bstauber/claude-projects/docs/superpowers/specs/2026-06-10-pie-poc-forge-design.md docs/superpowers/specs/
cp /Users/bstauber/claude-projects/docs/superpowers/plans/2026-06-10-pie-poc-forge-plan.md docs/superpowers/plans/
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 tests/validate_skill.py` → expected all PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
git add tests/validate_skill.py docs/
git commit -m "docs: archive spec + plan in skill repo (R-PROC-01)"
```

---

## Task 8: Write the full SKILL.md orchestration (Phases A/B/C)

**Files:**
- Modify: `/Users/bstauber/.claude/skills/pie-poc-forge/SKILL.md`

- [ ] **Step 1: Add the three-phase orchestration to SKILL.md**

Append the operating procedure between the refusal section and the domain-references section:

```markdown
## Operating Procedure

### Phase A — Ingest & Normalize (interactive)
1. Collect inputs: POV MVP Build Plan (`.md`), Technical & Architectural Assessment (`.md`), Agentforce Labs output, and/or pasted requirements. Ask for any that are missing; if the Tech & Arch Assessment is unavailable, proceed and flag lowered confidence.
2. Normalize into `requirements.json` per `refs/requirements-schema.md`.
3. Prompt for build decisions: **1GP vs 2GP** (see `refs/packaging-analysis.md` for the default), **target** (partner org vs demo instance), **agent-in-scope** (yes/no).
4. Form and present the **MVP/PoC opinion** (`refs/mvp-opinion.md`). Get explicit user confirmation of scope before generating.

### Phase B — Generate
Follow `refs/workflow-dispatch.md`: run generators inline if the component count ≤ 6, else fan them out as parallel subagents. Generators: packaging analysis, security review, gaps document, SFDX scaffold + manifests (delegate metadata to `agentforce-adlc:adlc-engineer`), and — only if agentInScope — agentscript (delegate to `agentforce-adlc:developing-agentforce`). Then run the barrier synthesis: assemble the execution plan + component manifest, render every artifact (`scripts/md-to-html.py`), build the index, and run `scripts/ensure-home-link.py` over the docs dir.

### Phase C — Review & Update (re-entrant)
On re-run with new requirements, follow `refs/workflow-dispatch.md` Phase C: diff against stored `requirements.json`, regenerate only affected artifacts, preserve hand-edited files via the `fileHashes` comparison (emit `<name>.regen` on divergence), and bump the index changelog.

## Delegation
- `.agent` / aiAuthoringBundle authoring → `agentforce-adlc:developing-agentforce`.
- Deep metadata scaffolding / deploy prep → `agentforce-adlc:adlc-engineer`.
This skill owns planning, packaging analysis, security review, gaps, and canvas rendering; it never authors agent internals or deploys to production itself.
```

- [ ] **Step 2: Run the suite to confirm nothing regressed**

Run: `cd /Users/bstauber/.claude/skills/pie-poc-forge && python3 tests/validate_skill.py`
Expected: all PASS. (SKILL.md still references every ref/template/script; size still < 20000.)

- [ ] **Step 3: Commit**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
git add SKILL.md
git commit -m "feat: add full Phase A/B/C orchestration to SKILL.md"
```

---

## Task 9: End-to-end dry run against a representative build plan

**Files:**
- None modified (validation + manual smoke test)

- [ ] **Step 1: Confirm the full validation suite passes**

Run: `cd /Users/bstauber/.claude/skills/pie-poc-forge && python3 tests/validate_skill.py`
Expected: every check PASS, exit 0. Capture the output.

- [ ] **Step 2: Smoke-test the render pipeline on one artifact**

Render the execution-plan template through the real script to prove the pipeline works end-to-end:

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
mkdir -p /tmp/pie-smoke
python3 scripts/md-to-html.py \
  --md templates/01-execution-plan.md \
  --shell templates/document-shell.html \
  --out /tmp/pie-smoke/01-execution-plan.html \
  --partner "<Partner>" --label "Execution Plan" --stage "02-Assess" --date "<YYYY-MM-DD>"
```

Expected: exits 0 and writes the HTML. If it exits non-zero on unfilled `{{TOKEN}}`s, that is expected for a raw template (tokens are filled at generation time, not render time) — instead confirm the script runs and reports which tokens are unfilled. Note this in the run log; it confirms the converter is wired.

- [ ] **Step 3: Invoke the skill against the real input (manual acceptance)**

In a Claude session, invoke `pie-poc-forge` with a representative MVP build plan (`.md`). Verify the skill:
- asks for the Tech & Arch Assessment (absent → flags lowered confidence),
- prompts for 1GP/2GP (recommends 2GP), target, agent-in-scope,
- presents an MVP/PoC opinion centered on the hero use case,
- generates the always-on artifacts + agentscript (when agent in scope), an SFDX scaffold (custom objects/fields, Apex/LWC stubs, permission set), `package.xml`, `sfdx-project.json`, and a populated `docs/index.html`.

Record results in the run log; file any gaps as follow-up tasks.

- [ ] **Step 4: Final commit / tag**

```bash
cd /Users/bstauber/.claude/skills/pie-poc-forge
git add -A
git commit -m "chore: pie-poc-forge v1 — validated end-to-end against a representative build plan" --allow-empty
```

---

## Self-Review

**Spec coverage:**
- Purpose/identity → Task 1 (SKILL.md + README). ✓
- Build types (agent/data360/platform) → encoded in `refs/requirements-schema.md` `buildTypes` + Phase A decisions. ✓
- Owns list (MVP opinion, packaging, scaffold, manifests, pre/post config, security, gaps, canvas) → refs in Task 3 + templates in Task 4. ✓
- Delegates → `refs/agentscript-handoff.md`, `refs/sfdx-scaffold.md`, SKILL.md Delegation section (Tasks 3, 8). ✓
- Inputs incl. "ask for what's missing" + lowered confidence → SKILL.md Phase A + `refs/gaps-document.md` (Tasks 8, 3). ✓
- Outputs / directory layout / 9 artifacts incl. conditional #9 → templates + registry + parity check (Task 4). ✓
- Canvas styling reuse → shell + scripts copied (Tasks 4, 5). ✓
- Workflow Phases A/B/C incl. fan-out heuristic + edit preservation → `refs/workflow-dispatch.md` + SKILL.md (Tasks 3, 8). ✓
- All 13 rubric IDs → R-FM-01/R-REF-01 (Task 2), R-ARCH-01/02/03 (Task 3), R-TEST-02/03 (Task 4), R-TEST-01 (suite exists, Task 2), R-CI-01/02 (Task 6), R-PROC-01 (Task 7), R-DOC-01 (Task 1), R-GIT-01 (Task 1). ✓
- Test case (representative build plan) → Task 9. ✓

**Placeholder scan:** No "TBD/implement later" left in steps; every code/content step shows concrete content. The deliberate `{{TOKEN}}` placeholders are template tokens (the artifact's runtime fill points), not plan placeholders — and the validator enforces their hygiene.

**Type consistency:** Registry names `ALWAYS`/`CONDITIONAL`/`ALL_ARTIFACTS`, helpers `read`/`exists`/`instructions`, and check names are consistent across Tasks 2–8. `t_no_orphans` is defined in Task 3 and refined once in Task 4 step 9 (explicitly called out). Artifact slugs (`01-execution-plan` … `09-agentscript`) match between the registry, templates, index, and parity check.
