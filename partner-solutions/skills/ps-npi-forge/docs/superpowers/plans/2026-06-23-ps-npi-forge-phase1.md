# PS-NPI-FORGE Phase 1 — Skeleton, Validation Harness & Effort Model

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the PS-NPI-FORGE skill repo with a Tier-3 skill-forge skeleton, a stdlib-only validation suite that enforces the structural invariants, and a working effort/manifest model — the foundation every later phase builds on.

**Architecture:** Markdown-instruction-driven skill (`SKILL.md` + lazy `refs/` + `templates/`) with a stdlib-only Python validation harness, mirroring `pie-poc-forge`. Phase 1 delivers the scaffold, the `manifest.yaml` schema + read/update/rollup script, and the validation tests that gate everything. No artifact generation yet — that is Phase 3.

**Tech Stack:** Python 3 (stdlib only — no npm, no pip deps), Markdown, YAML (parsed with a stdlib-only minimal parser, see Task 5), git + `.githooks` + GitHub Actions CI.

## Global Constraints

- **Skill location:** `~/.claude/skills/ps-npi-forge/` — its own git repo (git-init'd in Task 1).
- **Effort data location (NOT in skill repo):** `/Users/bstauber/claude-projects/ps-npi-efforts/<release>/<product-slug>/`.
- **Python:** stdlib only. No third-party packages. `python3`, runnable as `python3 tests/validate_skill.py`.
- **Voice (for any prose authored later):** first-person Brandon-as-Salesforce-exec/architect, McKinsey register.
- **Design pattern:** SLDS palette + Mermaid `%%{init}%%` directive from `~/.claude/style-conventions.md`; lazy-loaded refs; refusal conditions in SKILL.md.
- **Artifact registry (single source of truth, used Phase 3+ but declared now):**
  `00-executive-summary`, `01-brief`, `02-slide-summary`, `03-internal-enablement`,
  `04-internal-faq`, `05-external-faq`, `06-license-entitlements`, `07-addon-tiering`,
  `08-setup-guide`, `09-org-provisioning-validation`, `10-partner-profile-pov`.
- **Status vocabulary:** `pending` / `in_progress` / `drafted` / `verified` / `pulled`.
- **Confidence:** float 0.0–1.0 + one-line rationale, per artifact; effort overall = weighted floor.
- **Out of scope (never implement):** pricing/discount determination; live Org62 writes; non-official doc sources for technical guidance; auto-publish to Slack without confirmation.

---

### Task 1: Repo scaffold + git init

**Files:**
- Create: `~/.claude/skills/ps-npi-forge/.gitignore`
- Create: `~/.claude/skills/ps-npi-forge/README.md`
- Create: `~/.claude/skills/ps-npi-forge/BACKLOG.md`

**Interfaces:**
- Produces: the repo root at `~/.claude/skills/ps-npi-forge/` as a git repo; `README.md` linking `docs/design-spec.md` + `BACKLOG.md`.

- [ ] **Step 1: Create the directory and init git**

```bash
mkdir -p ~/.claude/skills/ps-npi-forge
cd ~/.claude/skills/ps-npi-forge
git init
```

- [ ] **Step 2: Write `.gitignore`**

```
__pycache__/
*.pyc
.DS_Store
```

- [ ] **Step 3: Write `README.md`**

```markdown
# ps-npi-forge

Builds a consistent family of Partner-Solutions-owned NPI artifacts (executive summary, brief,
FAQs, license/entitlement details, setup guide, add-on tiering, ideal-partner POV) plus a synced
Key Resources canvas, for a single new NPI product (typically an Embedded/OEM SKU modeled on a
directly-sold parent). Built on the skill-forge Tier-3 pattern; sibling to pie-poc-forge.

- **Design spec (0.x reference):** [docs/design-spec.md](docs/design-spec.md)
- **Backlog / next additions:** [BACKLOG.md](BACKLOG.md)

## Status

0.x — under construction. See the design spec for the full architecture and the backlog for
what is implemented vs. pending.

## Validation

```bash
python3 tests/validate_skill.py
```

Activate the pre-commit hook once per clone:

```bash
git config core.hooksPath .githooks
```
```

- [ ] **Step 4: Write `BACKLOG.md`** (seeded from spec §9)

```markdown
# ps-npi-forge — Backlog

Visibility on next additions for the 0.x build. Phase numbers refer to the implementation plans
under `docs/superpowers/plans/`.

## Open items (from design spec §9)

- [ ] **B1 — Org62 entitlement query:** pin the exact objects/SOQL behind the `productEntitlements`
  Apex page (licenses, PSLs, features, storage) for the parent `pId`. (Phase 4)
- [ ] **B2 — Slack canvas API:** confirm Slack MCP canvas create/update calls and the
  `#help-sell-…` channel registration UX + publish-confirmation gate. (Phase 6)
- [ ] **B3 — SF price-list tool:** determine whether the Heroku pricelist tool is fetchable or must
  be treated as a manual-reference catalog for add-on tiering. (Phase 5)

## Phase roadmap

- [x] Phase 1 — skeleton, validation harness, effort/manifest model
- [ ] Phase 2 — voice/style + intake source-map refs (no live fetch yet)
- [ ] Phase 3 — artifact templates + the generate→refine→validate cycle
- [ ] Phase 4 — Org62 entitlement intake + license/add-on artifacts
- [ ] Phase 5 — canvas assembly + HTML render + Mermaid
- [ ] Phase 6 — Slack sync + publish gate
- [ ] Phase 7 — Deep Build (C-mode) Workflow
```

- [ ] **Step 5: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add .gitignore README.md BACKLOG.md
git commit -m "chore: scaffold ps-npi-forge repo with README and backlog"
```

---

### Task 2: Copy the design spec into the repo + seed the spec/plan archive

**Files:**
- Create: `~/.claude/skills/ps-npi-forge/docs/design-spec.md` (copy of the approved spec)
- Create: `~/.claude/skills/ps-npi-forge/docs/superpowers/specs/2026-06-23-ps-npi-forge-design.md` (same content; satisfies R-PROC-01)
- Create: `~/.claude/skills/ps-npi-forge/docs/superpowers/plans/2026-06-23-ps-npi-forge-phase1.md` (this plan)

**Interfaces:**
- Produces: `docs/design-spec.md` (README target); a spec under `docs/superpowers/specs/` and a plan under `docs/superpowers/plans/` (the R-PROC-01 archive invariant tested in Task 4).

- [ ] **Step 1: Copy the spec and this plan into the repo**

```bash
cd ~/.claude/skills/ps-npi-forge
mkdir -p docs/superpowers/specs docs/superpowers/plans
cp /Users/bstauber/claude-projects/docs/superpowers/specs/2026-06-23-ps-npi-forge-design.md docs/design-spec.md
cp /Users/bstauber/claude-projects/docs/superpowers/specs/2026-06-23-ps-npi-forge-design.md docs/superpowers/specs/
cp /Users/bstauber/claude-projects/docs/superpowers/plans/2026-06-23-ps-npi-forge-phase1.md docs/superpowers/plans/
```

- [ ] **Step 2: Verify the three files exist**

Run: `cd ~/.claude/skills/ps-npi-forge && ls docs/design-spec.md docs/superpowers/specs/*.md docs/superpowers/plans/*.md`
Expected: all three paths listed, no "No such file".

- [ ] **Step 3: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add docs
git commit -m "docs: add 0.x design spec and phase 1 plan to repo archive"
```

---

### Task 3: SKILL.md with frontmatter + refusal conditions

**Files:**
- Create: `~/.claude/skills/ps-npi-forge/SKILL.md`

**Interfaces:**
- Produces: `SKILL.md` opening with YAML frontmatter (`name`, `description`) and containing a refusal/scope-conditions section — the contract Task 4's R-FM-01 and R-REF-01 checks assert.

- [ ] **Step 1: Write `SKILL.md`** (lean entry point; domain logic deferred to refs/ in later phases)

````markdown
---
name: ps-npi-forge
description: Use when the Partner Solutions team is contributing to a Salesforce NPI (New Product Introduction) effort for a new Embedded/OEM product — turns a parent direct SKU plus pasted/fetched/Org62 sources into a consistent family of PS-owned artifacts (executive summary, use-case brief, internal/external FAQs, license & entitlement details, add-on tiering, setup guide, org-provisioning validation, ideal-partner POV) plus a synced Key Resources canvas, with confidence scoring and gap tracking.
---

# ps-npi-forge

Builds PS-owned NPI artifacts for one new product (one release), modeled on a directly-sold parent
SKU. Outputs feed upward into the larger NPI team's official deliverables, so they are
**authoritative-feeder quality**: consistent, source-grounded, and uncertainty-flagged.

See [docs/design-spec.md](docs/design-spec.md) for the full architecture.

## The effort lifecycle

An **effort** = one product for one release. Effort data lives **outside this repo** at
`/Users/bstauber/claude-projects/ps-npi-efforts/<release>/<product-slug>/`. The `manifest.yaml`
there is the state: per-artifact status, confidence, placeholders, sources, and the Slack channel.

1. **Open / resume** an effort (minimum input: a parent direct SKU reference).
2. **Generate → refine → validate** each artifact (start from knowledge, fold in sources, run loops).
3. **Assemble** the Key Resources canvas (local HTML + optional Slack canvas).

> Phase 1 implements the scaffold, the manifest model, and the validation harness only. Artifact
> generation, intake, canvas, and Slack sync arrive in later phases (see BACKLOG.md).

## Run modes

- **Standard** — interactive, per-artifact generate→refine→validate; quality loops single-pass.
- **Deep Build** — opt-in Workflow escalation (adversarial multi-agent verification + live
  target-partner research) writing back to the same effort. Triggered explicitly.

## Refusal & scope conditions

This skill **does not**:

- Determine or fill **pricing or discounts** — out of scope; price/discount cells are left as
  marked placeholders owned elsewhere.
- Cite **non-official documentation** for technical guidance — only official Salesforce sources
  (help/developer/architect.salesforce.com, Trailhead, Partner Community, Org62-internal tools).
  Non-official links are flagged and excluded, never silently included.
- **Assert entitlements** (licenses/PSLs/features/storage) without flagging them for human
  confirmation — it drafts and flags; a human confirms.
- **Write to Org62** — Org62 access is read-only.
- **Publish to Slack without confirmation** — it confirms before creating a Slack canvas, and
  external-FAQ content always requires an explicit OK.
- **Silently drop an uncertainty** — every PENDING/TBD/missing value is surfaced with an owner and
  a next step.
````

- [ ] **Step 2: Verify frontmatter parses**

Run: `cd ~/.claude/skills/ps-npi-forge && head -4 SKILL.md`
Expected: first line `---`, then `name: ps-npi-forge`, then a `description:` line, then `---`.

- [ ] **Step 3: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add SKILL.md
git commit -m "feat: add SKILL.md entry point with frontmatter and refusal conditions"
```

---

### Task 4: Validation harness — structural invariants

**Files:**
- Create: `~/.claude/skills/ps-npi-forge/tests/validate_skill.py`

**Interfaces:**
- Consumes: `SKILL.md`, `docs/superpowers/specs|plans/` from Tasks 2–3.
- Produces: `python3 tests/validate_skill.py` exit 0/1; the `check()` decorator + `read()`/`exists()` helpers + `ARTIFACT_REGISTRY` constant that Task 5's tests and later phases extend.

- [ ] **Step 1: Write the failing test harness** (Phase 1 checks only; later phases add to it)

```python
#!/usr/bin/env python3
"""
Validation suite for the ps-npi-forge skill. Stdlib-only.

Asserts the structural invariants that must hold for the skill to run correctly and to satisfy the
skill-forge Tier-3 rubric. Validates files, references, and the manifest model — it does NOT judge
LLM output quality.

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

# ---- artifact registry (single source of truth) ------------------------
ARTIFACT_REGISTRY = [
    "00-executive-summary", "01-brief", "02-slide-summary", "03-internal-enablement",
    "04-internal-faq", "05-external-faq", "06-license-entitlements", "07-addon-tiering",
    "08-setup-guide", "09-org-provisioning-validation", "10-partner-profile-pov",
]
STATUS_VOCAB = ["pending", "in_progress", "drafted", "verified", "pulled"]

INSTRUCTION_FILES = ["SKILL.md"]
def instructions():
    return "\n".join(read(f) for f in INSTRUCTION_FILES if exists(f))

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

# ---- R-REF-02: out-of-scope rules named -------------------------------
@check("R-REF-02: SKILL.md names the four hard out-of-scope rules")
def t_out_of_scope():
    s = read("SKILL.md").lower()
    for needle in ["pricing", "non-official", "read-only", "without confirmation"]:
        assert needle in s, f"refusal section missing rule about: {needle}"

# ---- R-ARCH-02: every referenced path exists ----------------------------
@check("R-ARCH-02: every file path referenced in SKILL.md exists")
def t_refs_exist():
    skill = instructions()
    paths = set(re.findall(r"(?:templates|refs|scripts|tests|docs)/[A-Za-z0-9._/-]+", skill))
    missing = [p.rstrip(".") for p in paths if not exists(p.rstrip("."))]
    assert not missing, f"referenced but missing: {sorted(missing)}"

# ---- R-PROC-01: spec->plan archive exists -------------------------------
@check("R-PROC-01: spec->plan archive exists under docs/superpowers/")
def t_spec_plan_archive():
    specs = os.path.join(SKILL, "docs/superpowers/specs")
    plans = os.path.join(SKILL, "docs/superpowers/plans")
    assert os.path.isdir(specs) and any(f.endswith(".md") for f in os.listdir(specs)), \
        "no spec under docs/superpowers/specs/"
    assert os.path.isdir(plans) and any(f.endswith(".md") for f in os.listdir(plans)), \
        "no plan under docs/superpowers/plans/"

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

- [ ] **Step 2: Run the suite — expect all current checks to PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `5/5 checks passed`, exit 0. (Tasks 1–3 already satisfy every invariant.)

- [ ] **Step 3: Prove the harness can fail (sanity check the gate)**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 -c "import re,sys; s=open('SKILL.md').read(); sys.exit(0 if re.match(r'^---',s) else 1)" && echo FRONTMATTER_OK`
Expected: `FRONTMATTER_OK` (confirms the file the harness reads is well-formed).

- [ ] **Step 4: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add tests/validate_skill.py
git commit -m "test: add stdlib validation harness with structural invariants"
```

---

### Task 5: Manifest model — schema, read, update & confidence rollup

**Files:**
- Create: `~/.claude/skills/ps-npi-forge/scripts/manifest.py`
- Create: `~/.claude/skills/ps-npi-forge/templates/manifest.yaml`
- Create: `~/.claude/skills/ps-npi-forge/tests/fixtures/manifest/sample-manifest.yaml`
- Modify: `~/.claude/skills/ps-npi-forge/tests/validate_skill.py` (append behavioral tests)

**Interfaces:**
- Consumes: `check()`, `read()`, `exists()`, `ARTIFACT_REGISTRY`, `STATUS_VOCAB` from Task 4.
- Produces (in `scripts/manifest.py`):
  - `STATUS_VOCAB: list[str]` and `ARTIFACT_REGISTRY: list[str]` (re-declared here so the script is self-contained).
  - `load(path: str) -> dict` — parse a manifest YAML file into a dict.
  - `dumps(manifest: dict) -> str` — serialize a manifest dict back to YAML text.
  - `new_effort(release: str, product_slug: str, parent_sku: str) -> dict` — build a fresh manifest with all 11 artifacts at status `pending`, confidence `0.0`.
  - `set_status(manifest: dict, artifact: str, status: str) -> dict` — mutate+return; raises `ValueError` on unknown artifact or status outside `STATUS_VOCAB`.
  - `overall_confidence(manifest: dict) -> float` — the **weighted floor**: `min` of per-artifact confidence across all non-`pulled` artifacts (0.0 if none).

**Manifest YAML shape** (the contract):

```yaml
release: summer-26
product_slug: agentforce-healthcare-oem
parent_sku: "Health Cloud EE/UE"
slack_channel: ""
artifacts:
  00-executive-summary:
    status: pending
    confidence: 0.0
    rationale: ""
    sources: []
    placeholders: []   # each: {item, owner, next_step}
  # ... all 11 ...
```

- [ ] **Step 1: Write the failing tests** (append to `tests/validate_skill.py`, before the `# ---- runner` block)

```python
# ---- R-MANIFEST: behavioral tests for scripts/manifest.py ---------------
def _load_script(rel, name):
    import importlib.util
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, os.path.join(SKILL, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

@check("R-MANIFEST-01: new_effort seeds all 11 artifacts at pending/0.0")
def t_manifest_new():
    m = _load_script("scripts/manifest.py", "manifest_mod1")
    eff = m.new_effort("summer-26", "agentforce-healthcare-oem", "Health Cloud EE/UE")
    assert eff["release"] == "summer-26"
    assert eff["parent_sku"] == "Health Cloud EE/UE"
    assert set(eff["artifacts"].keys()) == set(ARTIFACT_REGISTRY), "all 11 artifacts must be seeded"
    for a, rec in eff["artifacts"].items():
        assert rec["status"] == "pending", f"{a} should start pending"
        assert rec["confidence"] == 0.0, f"{a} should start at 0.0"

@check("R-MANIFEST-02: round-trip load(dumps(x)) preserves the manifest")
def t_manifest_roundtrip():
    m = _load_script("scripts/manifest.py", "manifest_mod2")
    eff = m.new_effort("summer-26", "x-oem", "Parent EE")
    eff = m.set_status(eff, "01-brief", "drafted")
    eff["artifacts"]["01-brief"]["confidence"] = 0.6
    import tempfile, os as _os
    d = tempfile.mkdtemp()
    p = _os.path.join(d, "manifest.yaml")
    open(p, "w").write(m.dumps(eff))
    back = m.load(p)
    assert back["artifacts"]["01-brief"]["status"] == "drafted"
    assert abs(back["artifacts"]["01-brief"]["confidence"] - 0.6) < 1e-9
    assert back["release"] == "summer-26"

@check("R-MANIFEST-03: set_status rejects unknown artifact or status")
def t_manifest_set_status_guard():
    m = _load_script("scripts/manifest.py", "manifest_mod3")
    eff = m.new_effort("r", "p", "parent")
    try:
        m.set_status(eff, "99-nope", "drafted"); assert False, "unknown artifact should raise"
    except ValueError: pass
    try:
        m.set_status(eff, "01-brief", "banana"); assert False, "bad status should raise"
    except ValueError: pass

@check("R-MANIFEST-04: overall_confidence is the weighted floor, ignoring pulled artifacts")
def t_manifest_floor():
    m = _load_script("scripts/manifest.py", "manifest_mod4")
    eff = m.new_effort("r", "p", "parent")
    for a in ARTIFACT_REGISTRY:
        eff["artifacts"][a]["confidence"] = 0.8
        eff["artifacts"][a]["status"] = "verified"
    eff["artifacts"]["06-license-entitlements"]["confidence"] = 0.3   # the floor
    eff = m.set_status(eff, "10-partner-profile-pov", "pulled")        # excluded
    eff["artifacts"]["10-partner-profile-pov"]["confidence"] = 0.0
    assert abs(m.overall_confidence(eff) - 0.3) < 1e-9, "floor should be 0.3, ignoring the pulled artifact"

@check("R-MANIFEST-05: manifest template + fixture exist and parse")
def t_manifest_files():
    m = _load_script("scripts/manifest.py", "manifest_mod5")
    assert exists("templates/manifest.yaml"), "templates/manifest.yaml missing"
    assert exists("tests/fixtures/manifest/sample-manifest.yaml"), "sample fixture missing"
    parsed = m.load(os.path.join(SKILL, "tests/fixtures/manifest/sample-manifest.yaml"))
    assert set(parsed["artifacts"].keys()) == set(ARTIFACT_REGISTRY), "fixture must list all 11 artifacts"
```

- [ ] **Step 2: Run the tests to verify they FAIL**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on the R-MANIFEST checks with `No such file or directory: '.../scripts/manifest.py'`.

- [ ] **Step 3: Write `scripts/manifest.py`** (stdlib-only; minimal YAML for the known flat shape)

```python
#!/usr/bin/env python3
"""
Effort manifest model for ps-npi-forge. Stdlib-only.

The manifest is the per-effort state: status, confidence, placeholders, and sources for each of the
11 artifacts. This module is the single place that reads/writes it. The YAML handled here is the
*known, flat* manifest shape only (not general YAML) — kept dependency-free on purpose.
"""
import re

STATUS_VOCAB = ["pending", "in_progress", "drafted", "verified", "pulled"]
ARTIFACT_REGISTRY = [
    "00-executive-summary", "01-brief", "02-slide-summary", "03-internal-enablement",
    "04-internal-faq", "05-external-faq", "06-license-entitlements", "07-addon-tiering",
    "08-setup-guide", "09-org-provisioning-validation", "10-partner-profile-pov",
]

def new_effort(release, product_slug, parent_sku):
    return {
        "release": release,
        "product_slug": product_slug,
        "parent_sku": parent_sku,
        "slack_channel": "",
        "artifacts": {
            a: {"status": "pending", "confidence": 0.0, "rationale": "",
                "sources": [], "placeholders": []}
            for a in ARTIFACT_REGISTRY
        },
    }

def set_status(manifest, artifact, status):
    if artifact not in manifest["artifacts"]:
        raise ValueError(f"unknown artifact: {artifact}")
    if status not in STATUS_VOCAB:
        raise ValueError(f"unknown status: {status} (allowed: {STATUS_VOCAB})")
    manifest["artifacts"][artifact]["status"] = status
    return manifest

def overall_confidence(manifest):
    vals = [rec["confidence"] for rec in manifest["artifacts"].values()
            if rec["status"] != "pulled"]
    return min(vals) if vals else 0.0

# ---- minimal YAML for the known flat manifest shape ---------------------
def dumps(manifest):
    lines = []
    for key in ("release", "product_slug", "parent_sku", "slack_channel"):
        lines.append(f"{key}: {_scalar(manifest.get(key, ''))}")
    lines.append("artifacts:")
    for a in ARTIFACT_REGISTRY:
        rec = manifest["artifacts"][a]
        lines.append(f"  {a}:")
        lines.append(f"    status: {rec['status']}")
        lines.append(f"    confidence: {rec['confidence']}")
        lines.append(f"    rationale: {_scalar(rec.get('rationale',''))}")
        lines.append(f"    sources: {_inline_list(rec.get('sources', []))}")
        lines.append("    placeholders:")
        for ph in rec.get("placeholders", []):
            lines.append(f"      - item: {_scalar(ph.get('item',''))}")
            lines.append(f"        owner: {_scalar(ph.get('owner',''))}")
            lines.append(f"        next_step: {_scalar(ph.get('next_step',''))}")
    return "\n".join(lines) + "\n"

def _scalar(v):
    s = str(v)
    if s == "" or re.search(r'[:#]', s) or s != s.strip():
        return '"' + s.replace('"', '\\"') + '"'
    return s

def _inline_list(items):
    if not items:
        return "[]"
    return "[" + ", ".join(_scalar(i) for i in items) + "]"

def load(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    manifest = {"artifacts": {}}
    cur_art = None
    cur_ph = None
    for raw in lines:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0:
            if line == "artifacts:":
                cur_art = None; continue
            k, _, v = line.partition(":")
            manifest[k.strip()] = _parse_scalar(v.strip())
        elif indent == 2 and line.endswith(":"):
            cur_art = line[:-1].strip()
            manifest["artifacts"][cur_art] = {"sources": [], "placeholders": []}
            cur_ph = None
        elif indent == 4 and cur_art:
            k, _, v = line.partition(":")
            k = k.strip()
            if k == "placeholders":
                continue
            if k == "sources":
                manifest["artifacts"][cur_art]["sources"] = _parse_inline_list(v.strip())
            elif k == "confidence":
                manifest["artifacts"][cur_art]["confidence"] = float(v.strip())
            else:
                manifest["artifacts"][cur_art][k] = _parse_scalar(v.strip())
        elif indent == 6 and line.startswith("- item:"):
            cur_ph = {"item": _parse_scalar(line.split(":",1)[1].strip())}
            manifest["artifacts"][cur_art]["placeholders"].append(cur_ph)
        elif indent == 8 and cur_ph is not None:
            k, _, v = line.partition(":")
            cur_ph[k.strip()] = _parse_scalar(v.strip())
    return manifest

def _parse_scalar(v):
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        return v[1:-1].replace('\\"', '"')
    return v

def _parse_inline_list(v):
    v = v.strip()
    if v in ("", "[]"):
        return []
    inner = v[1:-1] if v[0] == "[" and v[-1] == "]" else v
    return [_parse_scalar(x.strip()) for x in inner.split(",") if x.strip()]
```

- [ ] **Step 4: Write `templates/manifest.yaml`** (the seed template, generated to match `dumps`)

```bash
cd ~/.claude/skills/ps-npi-forge
mkdir -p templates tests/fixtures/manifest
python3 -c "import sys; sys.path.insert(0,'scripts'); import manifest as m; open('templates/manifest.yaml','w').write(m.dumps(m.new_effort('RELEASE_SLUG','PRODUCT_SLUG','PARENT_SKU')))"
```

- [ ] **Step 5: Write the fixture** (a partially-filled sample for the load test)

```bash
cd ~/.claude/skills/ps-npi-forge
python3 -c "
import sys; sys.path.insert(0,'scripts'); import manifest as m
e = m.new_effort('summer-26','agentforce-healthcare-oem','Health Cloud EE/UE')
e['slack_channel'] = '#help-sell-health-cloud'
m.set_status(e,'01-brief','drafted'); e['artifacts']['01-brief']['confidence']=0.6
e['artifacts']['09-org-provisioning-validation']['placeholders']=[{'item':'Template ID','owner':'Manish/John','next_step':'request template ID'}]
open('tests/fixtures/manifest/sample-manifest.yaml','w').write(m.dumps(e))
"
```

- [ ] **Step 6: Run the suite to verify all checks PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `10/10 checks passed`, exit 0.

- [ ] **Step 7: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add scripts/manifest.py templates/manifest.yaml tests/fixtures/manifest/sample-manifest.yaml tests/validate_skill.py
git commit -m "feat: add effort manifest model with status, confidence floor, and round-trip YAML"
```

---

### Task 6: Pre-commit hook + CI workflow

**Files:**
- Create: `~/.claude/skills/ps-npi-forge/.githooks/pre-commit`
- Create: `~/.claude/skills/ps-npi-forge/.github/workflows/validate.yml`
- Modify: `~/.claude/skills/ps-npi-forge/tests/validate_skill.py` (append CI invariant checks)

**Interfaces:**
- Consumes: `check()`, `exists()`, `read()` from Task 4.
- Produces: a tracked pre-commit hook and CI workflow, both running `validate_skill.py`; the R-CI-01/02 checks that assert they exist.

- [ ] **Step 1: Write the failing CI invariant tests** (append before `# ---- runner`)

```python
# ---- R-CI: hook + workflow run the validation suite --------------------
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

- [ ] **Step 2: Run to verify they FAIL**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on R-CI-01 (`.githooks/pre-commit missing`).

- [ ] **Step 3: Write `.githooks/pre-commit`**

```sh
#!/bin/sh
# ps-npi-forge pre-commit hook — runs the skill validation suite.
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

- [ ] **Step 4: Make the hook executable and activate it**

```bash
cd ~/.claude/skills/ps-npi-forge
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
```

- [ ] **Step 5: Write `.github/workflows/validate.yml`**

```yaml
name: validate
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - name: Run skill validation suite
        run: python3 tests/validate_skill.py
```

- [ ] **Step 6: Run the full suite to verify all PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `12/12 checks passed`, exit 0.

- [ ] **Step 7: Commit (exercises the hook)**

```bash
cd ~/.claude/skills/ps-npi-forge
git add .githooks/pre-commit .github/workflows/validate.yml tests/validate_skill.py
git commit -m "ci: add pre-commit hook and GitHub Actions workflow running the validation suite"
```
Expected: the pre-commit hook prints `12/12 checks passed` before the commit completes.

---

## Self-Review

**Spec coverage (Phase 1 scope):**
- Repo + own-git-repo (spec §7, "own repo") → Task 1. ✅
- design-spec.md in repo + README link + BACKLOG (user request) → Tasks 1–2. ✅
- SKILL.md + frontmatter + refusal conditions (spec §7) → Task 3. ✅
- Tier-3 validation harness, stdlib-only (spec §7) → Tasks 4, 6. ✅
- Artifact registry, status vocab, confidence weighted-floor (spec §2.2, §3.2) → Tasks 4–5. ✅
- Effort/manifest model, resumability state (spec §2.1–2.2) → Task 5. ✅
- CI + pre-commit (spec §7) → Task 6. ✅
- **Deferred to later phases (correctly out of Phase 1):** artifact templates/generation (Phase 3), voice/intake refs (Phase 2), Org62 (Phase 4), canvas/render/Mermaid (Phase 5), Slack (Phase 6), Deep Build workflow (Phase 7). Tracked in BACKLOG.md.

**Placeholder scan:** No TBD/TODO in steps; every code/script step shows complete content; `templates/manifest.yaml` and the fixture are generated by shown commands, not hand-waved. ✅

**Type consistency:** `ARTIFACT_REGISTRY` (11 slugs) and `STATUS_VOCAB` (5 values) are identical in `tests/validate_skill.py` (Task 4) and `scripts/manifest.py` (Task 5). Function names `new_effort`/`set_status`/`overall_confidence`/`load`/`dumps` match between the Interfaces block, the tests (Task 5 Step 1), and the implementation (Task 5 Step 3). ✅
