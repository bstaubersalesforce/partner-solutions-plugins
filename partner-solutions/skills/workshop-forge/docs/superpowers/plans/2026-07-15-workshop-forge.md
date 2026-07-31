# workshop-forge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `workshop-forge`, a Tier-3 Claude skill that scaffolds and authors Salesforce partner workshop kits, then dogfood it against the hand-built headless360-workshop.

**Architecture:** Approach 2 — a deterministic Python generator (`scripts/scaffold_kit.py`) renders the kit *skeleton* from a `config/kit.json` overlay + `templates/`; prompt-driven `refs/*-flow.md` flows author the *content*. Two modes (scaffold / author-enrich). Built per skill-forge conventions (rubric-selected `tests/validate_skill.py`, pre-commit hook, CI, spec+plan archive).

**Tech Stack:** Python 3 (stdlib only), Bash (generated kit scripts + `check.sh`), Markdown (SKILL/refs/templates), git + `gh`.

## Global Constraints

- **Skill dir:** `~/.claude/skills/workshop-forge/` (already `git init`'d; spec committed at `4765f97`). Never overwrite an existing target when scaffolding a kit — refuse and ask for a new name.
- **Tier 3 rubric IDs (all required):** R-FM-01, R-REF-01, R-ARCH-01, R-ARCH-02, R-ARCH-03, R-TEST-01, R-TEST-02, R-TEST-03, R-TEST-04, R-CI-01, R-CI-02, R-PROC-01, R-DOC-01. Snippets come verbatim from `~/.claude/skills/skill-forge/refs/check-library.md` (`chk_frontmatter`, `chk_refusal_present`, `chk_refs_dir`, `chk_refs_exist`, `chk_no_orphans`, `chk_test_suite_exists`, `chk_token_hygiene`, `chk_router_parity`, `chk_behavioral_tests`, `chk_precommit_hook`, `chk_ci_workflow`, `chk_spec_plan_archive`, `chk_readme`).
- **`tests/validate_skill.py` is stdlib-only.** Assembled via `~/.claude/skills/skill-forge/templates/validate_skill.py.tmpl` (`{{INJECTED_CHECKS}}` + `{{CHECK_REGISTRY}}`).
- **Template tokens:** `{{UPPER_SNAKE_CASE}}`, balanced braces (R-TEST-02).
- **`scaffold_kit.py`:** deterministic, idempotent, **no deletes**; output must be byte-stable for golden-file testing (sort keys, fixed ordering, trailing newline discipline).
- **No orphans (R-ARCH-03):** every file under `refs/`/`templates/`/`validation/` must be referenced by the instructions; every referenced path must exist (R-ARCH-02).
- **Delivery voice** (SKILL.md + authored content): senior Salesforce advisor — lead with the conclusion, no hedging, uncertainty-flagged. Matches the `*-forge` family.
- **Wrap, don't invent, the reference build.** Never generate agent/SFDX metadata (pie-poc-forge's job).
- **Commit after every task.** Activate `git config core.hooksPath .githooks` once the hook exists (Task 12).

---

## File Structure

- `SKILL.md` — router: overview, delivery voice, refusal/scope, mode detection. (Task 2)
- `refs/kit-anatomy.md` — common skeleton vs overlay. (Task 3)
- `refs/guide-conventions.md` — Module 0→N arc, 🔴 checkpoints, Educate-First. (Task 3)
- `refs/provisioning-models.md` — picker + decision guide, "no org" first-class. (Task 4)
- `refs/input-contract.md` — author-mode input detection. (Task 5)
- `refs/scaffold-flow.md` — mode 1 flow. (Task 6)
- `refs/author-flow.md` — mode 2 flow. (Task 6)
- `refs/kit-check-spec.md` — what the generated `check.sh` validates. (Task 7)
- `templates/*.tmpl` + `templates/docs/` + `templates/scripts/` — the kit skeleton. (Task 7)
- `scripts/scaffold_kit.py` — the deterministic generator. (Tasks 8–10)
- `tests/validate_skill.py` — Tier-3 structural suite. (Task 11)
- `tests/test_scaffold.py` + `tests/fixtures/` — golden-file generator tests. (Tasks 9–10)
- `README.md`, `.githooks/pre-commit`, `.github/workflows/validate.yml`. (Task 12)

---

## Task 1: Directory skeleton + README

**Files:**
- Create: `~/.claude/skills/workshop-forge/{refs,templates,templates/docs,templates/scripts,templates/scripts/lib,scripts,tests,tests/fixtures,.githooks,.github/workflows}/.gitkeep`
- Create: `README.md`

**Interfaces:**
- Produces: the on-disk tree every later task writes into.

- [ ] **Step 1: Create the directory tree**

```bash
cd ~/.claude/skills/workshop-forge
mkdir -p refs templates/docs templates/scripts/lib scripts tests/fixtures .githooks .github/workflows
```

- [ ] **Step 2: Write `README.md`** (from `~/.claude/skills/skill-forge/templates/README.md.tmpl` shape)

```markdown
# workshop-forge

Tier-3 skill that **scaffolds and authors Salesforce partner workshop kits** — the enablement/activation
member of the `*-forge` family (pov-builder → pie-poc-forge → ps-npi-forge → workshop-forge).

## Two modes
- **Scaffold** — stamp the kit skeleton from a `config/kit.json` overlay (`scripts/scaffold_kit.py`).
- **Author / enrich** — author module content, the provisioning doc, and commercial track onto a scaffolded tree.

## Invoke
"Scaffold a workshop kit for <topic>" → scaffold mode. "Author the modules for <kit>" → author mode.

## Validate
`python3 tests/validate_skill.py` (also run by `.githooks/pre-commit` and CI).

See `docs/superpowers/specs/2026-07-15-workshop-forge-design.md` for the full design.
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "chore: workshop-forge dir skeleton + README"
```

---

## Task 2: SKILL.md router

**Files:**
- Create: `SKILL.md`

**Interfaces:**
- Produces: mode-detection contract ("scaffold" vs "author"); names every `refs/` file (satisfies R-ARCH-02/03 once refs exist).

- [ ] **Step 1: Write `SKILL.md`** with YAML frontmatter (R-FM-01) and explicit refusal conditions (R-REF-01)

```markdown
---
name: workshop-forge
description: Use when scaffolding or authoring a Salesforce partner workshop/lab kit — stamps the shared kit skeleton (GUIDE/FACILITATOR/scripts/check.sh) from an overlay, then authors modules, provisioning, and commercial content. Joins the pov-builder / pie-poc-forge / ps-npi-forge family.
---

# workshop-forge

## Overview
Scaffolds and authors Salesforce partner workshop kits from the pattern proven across data360 / headless360 /
ncino kits. Two modes share one overlay (`config/kit.json`) and one anatomy (`refs/kit-anatomy.md`).

## Delivery Voice
Write authored content as a senior Salesforce industry advisor briefing a partner team. Lead with the
conclusion; no hedging; flag uncertainty explicitly.

## Refusal / scope conditions
- Not a workshop-kit request (neither scaffold nor author) → clarify before acting.
- Scaffold: the target kit directory already exists → **refuse**, ask for a new name (never overwrite).
- Author: no scaffolded tree present → direct the user to scaffold mode first.
- Asked to generate the reference-build **agent/SFDX metadata** → redirect to pie-poc-forge; workshop-forge
  **wraps**, does not invent, the reference build.
- Do not fabricate provisioning specifics that can't be verified — flag residual confirmations.

## Mode detection
- "scaffold / new kit / stamp …" → **Scaffold**: load `refs/scaffold-flow.md`.
- "author / enrich / fill / write the modules …" → **Author**: load `refs/author-flow.md`.
- Ambiguous → ask which mode.

## Shared spine
Both flows read `refs/kit-anatomy.md` (skeleton vs overlay), `refs/guide-conventions.md` (Module 0→N +
🔴 checkpoints), and `refs/provisioning-models.md` (the picker + decision guide). Author also reads
`refs/input-contract.md`. The generated kit's self-check is specified in `refs/kit-check-spec.md`.

## Self-validation
workshop-forge satisfies its own rubric at Tier 3. After editing it, run `python3 tests/validate_skill.py`
(also enforced by `.githooks/pre-commit` and CI).
```

- [ ] **Step 2: Commit**

```bash
git add SKILL.md && git commit -m "feat: SKILL.md router + refusal conditions"
```

---

## Task 3: Anatomy + GUIDE-conventions refs

**Files:**
- Create: `refs/kit-anatomy.md`, `refs/guide-conventions.md`

**Interfaces:**
- Consumes: the spec's overlay schema + common-skeleton evidence.
- Produces: the canonical skeleton/overlay description both flows cite; the Module-arc + 🔴 rules the generator and author flow enforce.

- [ ] **Step 1: Write `refs/kit-anatomy.md`** — the common skeleton (always-present files), the conditional parts (org-provisioning, content_dirs, sfdx), and the `config/kit.json` overlay schema (copy the schema block verbatim from the spec).

- [ ] **Step 2: Write `refs/guide-conventions.md`** — Module 0 "Comprehend" → Module N "Extend" arc; the 🔴 checkpoint semantics (order-sensitive/silent-failure steps); Educate-First framing; that module bodies are authored (not scaffolded).

- [ ] **Step 3: Commit**

```bash
git add refs/kit-anatomy.md refs/guide-conventions.md && git commit -m "docs: kit-anatomy + guide-conventions refs"
```

---

## Task 4: Provisioning decision guide (the reusable IP)

**Files:**
- Create: `refs/provisioning-models.md`

**Interfaces:**
- Produces: the Step-1 "needs_org?" gate, the Step-2 feature→org-type table, the Step-3 universal rules; consumed by author flow to write `docs/org-provisioning.md` and set `kit.json.provisioning`.

- [ ] **Step 1: Write `refs/provisioning-models.md`** with the three-step guide from the spec: (1) gating branch (`needs_org:false` is first-class — educate-only / facilitator-demo / shared-hosted-backend); (2) feature-dependency→org-type table (DE-per-team / SDO-per-team / assigned-preconfigured / scratch-pool, each with the "why"); (3) universal rules (pre-provision T-minus-days never morning-of; safety-net org; per-org ECA/PKCE/JWT never auto-provisioned → generate a setup helper; smoke-test the real flow). End with "reason to a recommendation + flag residual confirmations."

- [ ] **Step 2: Commit**

```bash
git add refs/provisioning-models.md && git commit -m "docs: provisioning-models decision guide"
```

---

## Task 5: Input contract ref

**Files:**
- Create: `refs/input-contract.md`

**Interfaces:**
- Produces: author-mode input-detection order — upstream pie-poc-forge/pov-builder artifact | freeform sources | interview.

- [ ] **Step 1: Write `refs/input-contract.md`** — how author mode detects and prefers an upstream family artifact (a pie-poc-forge PoC package path or pov-builder POV), the freeform fallback (brief/research/pasted reqs), and the interview last-resort; plus the "wrap the reference build into `sfdx/`, never regenerate metadata" rule.

- [ ] **Step 2: Commit**

```bash
git add refs/input-contract.md && git commit -m "docs: author-mode input-contract ref"
```

---

## Task 6: The two mode-flow refs

**Files:**
- Create: `refs/scaffold-flow.md`, `refs/author-flow.md`

**Interfaces:**
- Consumes: kit-anatomy, provisioning-models, input-contract, guide-conventions.
- Produces: the step sequences SKILL.md routes to.

- [ ] **Step 1: Write `refs/scaffold-flow.md`** — S1 intake overlay (one question only where not inferable) → S2 **refuse if target dir exists** → S3 write `config/kit.json` + run `scripts/scaffold_kit.py` → S4 run the generated `check.sh` (must be green) → S5 handoff ("run author mode to fill content").

- [ ] **Step 2: Write `refs/author-flow.md`** — A1 detect input (`input-contract.md`) → A2 wrap the reference build into `sfdx/` → A3 author onto the scaffolded tree (GUIDE bodies per `guide-conventions.md`; provisioning doc per `provisioning-models.md`; framework + buildability + commercial + slides) → A4 re-run `check.sh` → A5 handoff (authored/stubbed/residual gaps). Note re-entrancy: updates, never regenerates.

- [ ] **Step 3: Commit**

```bash
git add refs/scaffold-flow.md refs/author-flow.md && git commit -m "docs: scaffold + author mode flows"
```

---

## Task 7: Kit templates + check-spec

**Files:**
- Create: `refs/kit-check-spec.md`
- Create: `templates/README.md.tmpl`, `templates/GUIDE.md.tmpl`, `templates/FACILITATOR.md.tmpl`, `templates/LESSONS-LEARNED.md.tmpl`, `templates/kit.json.tmpl`, `templates/env.example.tmpl`, `templates/gitignore.tmpl`
- Create: `templates/docs/org-provisioning.md.tmpl`, `templates/docs/framework.md.tmpl`, `templates/docs/buildability-matrix.md.tmpl`
- Create: `templates/scripts/lib/common.sh.tmpl`, `templates/scripts/00-preflight.sh.tmpl`, `templates/scripts/deploy.sh.tmpl`, `templates/scripts/assign-perms.sh.tmpl`, `templates/scripts/check.sh.tmpl`

**Interfaces:**
- Produces: the token-parameterized skeleton `scaffold_kit.py` renders. Tokens are `{{UPPER_SNAKE_CASE}}` (R-TEST-02): e.g. `{{KIT_NAME}}`, `{{KIT_TITLE}}`, `{{MODE}}`, `{{DURATION}}`, `{{MODULE_LIST}}`, `{{PROVISIONING_MODEL}}`.
- `check.sh.tmpl` mirrors headless360's `scripts/check.sh` (file-presence `req`/`opt` + internal-link resolution), but its required-file list is rendered from the overlay so it matches the conditional shape.

- [ ] **Step 1: Write `refs/kit-check-spec.md`** — what the generated `check.sh` asserts: required top-level docs; `config/kit.json` present; scripts present + bash-syntax-valid; conditional assertions (org-provisioning doc present **iff** `needs_org`; content dirs per `content_dirs`); internal markdown links resolve. This is the contract Task 10's meta-check verifies.

- [ ] **Step 2: Write the always-present templates** (README/GUIDE/FACILITATOR/LESSONS-LEARNED/kit.json/env.example/gitignore) with `{{TOKENS}}`. GUIDE.md.tmpl encodes the Module-0→N arc with a `{{MODULE_LIST}}` insertion point and the 🔴 convention.

- [ ] **Step 3: Write the conditional templates** (`docs/*.tmpl`) and the script templates (`lib/common.sh` = the headless360 `pass/warn/fail/resolve_org` helpers; preflight/deploy/assign; `check.sh.tmpl`).

- [ ] **Step 4: Commit**

```bash
git add refs/kit-check-spec.md templates && git commit -m "feat: kit skeleton templates + check-spec"
```

---

## Task 8: scaffold_kit.py — overlay load + always-present render

**Files:**
- Create: `scripts/scaffold_kit.py`
- Test: `tests/test_scaffold.py`

**Interfaces:**
- Produces: `render_kit(kit_json_path, out_dir)` — reads overlay JSON, renders the always-present skeleton to `out_dir`, returns the sorted list of relative paths written. Deterministic: sorted iteration, `\n` line endings, files end with a trailing newline.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scaffold.py
import json, os, tempfile, importlib.util, pathlib
SKILL = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sk", SKILL/"scripts/scaffold_kit.py")
sk = importlib.util.module_from_spec(spec); spec.loader.exec_module(sk)

MINIMAL = {"name":"t","title":"T","mode":"lab","duration":"2-day","partner_overlay":"reference",
           "surfaces":{}, "provisioning":{"needs_org":False,"model":"none","required_features":[]},
           "modules":[{"n":0,"title":"Comprehend"}], "content_dirs":{}, "reference_build":{"source":"none","path":"sfdx/"}}

def test_always_present_files_rendered():
    with tempfile.TemporaryDirectory() as d:
        kj = os.path.join(d,"kit.json"); open(kj,"w").write(json.dumps(MINIMAL))
        written = sk.render_kit(kj, os.path.join(d,"out"))
        for f in ["README.md","GUIDE.md","FACILITATOR.md","LESSONS-LEARNED.md",
                  "config/kit.json",".env.example",".gitignore",
                  "scripts/lib/common.sh","scripts/check.sh"]:
            assert f in written, f"{f} not rendered"
            assert os.path.exists(os.path.join(d,"out",f))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/.claude/skills/workshop-forge && python3 -m pytest tests/test_scaffold.py -q` (or `python3 tests/test_scaffold.py` with a `__main__` runner if pytest is absent)
Expected: FAIL — `scaffold_kit.py` / `render_kit` not defined.

- [ ] **Step 3: Implement `render_kit` (always-present branch)**

```python
#!/usr/bin/env python3
"""Deterministic workshop-kit scaffolder. Stdlib only. Idempotent, no deletes."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TPL  = os.path.join(os.path.dirname(HERE), "templates")

def _render(tpl_rel, tokens):
    with open(os.path.join(TPL, tpl_rel), encoding="utf-8") as f: s = f.read()
    for k, v in tokens.items(): s = s.replace("{{"+k+"}}", str(v))
    if not s.endswith("\n"): s += "\n"
    return s

def _write(out_dir, rel, content):
    p = os.path.join(out_dir, rel); os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(content)

def _tokens(cfg):
    modules = "\n".join(f"- Module {m['n']}: {m['title']}" + (" 🔴" if m.get("checkpoint") else "")
                        for m in cfg.get("modules", []))
    return {"KIT_NAME":cfg["name"],"KIT_TITLE":cfg["title"],"MODE":cfg["mode"],
            "DURATION":cfg["duration"],"MODULE_LIST":modules,
            "PROVISIONING_MODEL":cfg.get("provisioning",{}).get("model","none")}

ALWAYS = [("README.md.tmpl","README.md"),("GUIDE.md.tmpl","GUIDE.md"),
          ("FACILITATOR.md.tmpl","FACILITATOR.md"),("LESSONS-LEARNED.md.tmpl","LESSONS-LEARNED.md"),
          ("env.example.tmpl",".env.example"),("gitignore.tmpl",".gitignore"),
          ("scripts/lib/common.sh.tmpl","scripts/lib/common.sh"),
          ("scripts/00-preflight.sh.tmpl","scripts/00-preflight.sh")]

def render_kit(kit_json_path, out_dir):
    with open(kit_json_path, encoding="utf-8") as f: cfg = json.load(f)
    tok = _tokens(cfg); written = []
    for tpl, rel in ALWAYS:
        _write(out_dir, rel, _render(tpl, tok)); written.append(rel)
    # config/kit.json: canonical, sorted for byte-stability
    _write(out_dir, "config/kit.json", json.dumps(cfg, indent=2, sort_keys=True) + "\n")
    written.append("config/kit.json")
    # check.sh is generated last (Task 10) — placeholder call kept here:
    written += _render_check(out_dir, cfg)
    return sorted(written)

def _render_check(out_dir, cfg):
    # Task 10 fills this; minimal for now so tests can grow incrementally.
    _write(out_dir, "scripts/check.sh", _render("scripts/check.sh.tmpl", _tokens(cfg)))
    return ["scripts/check.sh"]

if __name__ == "__main__":
    out = render_kit(sys.argv[1], sys.argv[2]); print("\n".join(out))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_scaffold.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/scaffold_kit.py tests/test_scaffold.py && git commit -m "feat: scaffold_kit.py always-present render + test"
```

---

## Task 9: Conditional rendering + needs_org:false golden fixture

**Files:**
- Modify: `scripts/scaffold_kit.py`
- Create: `tests/fixtures/educate/kit.json`, `tests/fixtures/educate/expected/` (golden tree)
- Modify: `tests/test_scaffold.py`

**Interfaces:**
- Consumes: `render_kit` from Task 8.
- Produces: conditional emission — `docs/org-provisioning.md` + `scripts/{deploy,assign-perms}.sh` only when `needs_org`; content dirs per `content_dirs`; `sfdx/` placeholder per `reference_build`. Byte-equal golden fixture for the no-org case.

- [ ] **Step 1: Write the failing test — no-org kit OMITS org artifacts + is byte-equal to golden**

```python
def test_educate_kit_omits_org_and_matches_golden():
    fx = SKILL/"tests/fixtures/educate"
    with tempfile.TemporaryDirectory() as d:
        written = sk.render_kit(str(fx/"kit.json"), os.path.join(d,"out"))
        assert "docs/org-provisioning.md" not in written
        assert "scripts/deploy.sh" not in written
        # byte-equal against the committed golden tree
        for rel in written:
            got = open(os.path.join(d,"out",rel),encoding="utf-8").read()
            exp = open(fx/"expected"/rel,encoding="utf-8").read()
            assert got == exp, f"drift in {rel}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_scaffold.py::test_educate_kit_omits_org_and_matches_golden -q`
Expected: FAIL — conditionals not implemented / fixtures absent.

- [ ] **Step 3: Implement conditional rendering** (add to `render_kit` before the check.sh call)

```python
    prov = cfg.get("provisioning", {})
    if prov.get("needs_org"):
        _write(out_dir, "docs/org-provisioning.md", _render("docs/org-provisioning.md.tmpl", tok))
        written.append("docs/org-provisioning.md")
        for tpl, rel in [("scripts/deploy.sh.tmpl","scripts/deploy.sh"),
                         ("scripts/assign-perms.sh.tmpl","scripts/assign-perms.sh")]:
            _write(out_dir, rel, _render(tpl, tok)); written.append(rel)
    for dirname, on in cfg.get("content_dirs", {}).items():
        if on:
            _write(out_dir, f"{dirname}/.gitkeep", ""); written.append(f"{dirname}/.gitkeep")
    if cfg.get("reference_build", {}).get("source") != "none":
        _write(out_dir, "sfdx/.gitkeep", ""); written.append("sfdx/.gitkeep")
```

- [ ] **Step 4: Generate the golden fixture, then lock it**

```bash
cd ~/.claude/skills/workshop-forge
mkdir -p tests/fixtures/educate
# author kit.json: needs_org:false, no content_dirs, reference_build source "none"
$EDITOR tests/fixtures/educate/kit.json
python3 scripts/scaffold_kit.py tests/fixtures/educate/kit.json tests/fixtures/educate/expected
# eyeball the tree, confirm NO docs/org-provisioning.md and NO scripts/deploy.sh
find tests/fixtures/educate/expected -type f | sort
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_scaffold.py -q`
Expected: PASS (both tests).

- [ ] **Step 6: Mutation-verify (manual discipline — R-TEST-04)**

Temporarily change the `if prov.get("needs_org"):` guard to `if True:`, re-run the test, confirm `test_educate_kit_omits_org_and_matches_golden` FAILS (org doc now wrongly present), then restore and confirm PASS. Record that you watched it fail in the commit body.

- [ ] **Step 7: Commit**

```bash
git add scripts/scaffold_kit.py tests/test_scaffold.py tests/fixtures/educate && \
git commit -m "feat: conditional render + educate golden fixture (mutation-verified)"
```

---

## Task 10: check.sh generation + needs_org:true golden fixture + meta-check

**Files:**
- Modify: `scripts/scaffold_kit.py` (`_render_check` → real, overlay-driven required-file list)
- Create: `tests/fixtures/full/kit.json`, `tests/fixtures/full/expected/` (golden tree)
- Modify: `tests/test_scaffold.py`

**Interfaces:**
- Consumes: `render_kit`, `refs/kit-check-spec.md`.
- Produces: a generated `scripts/check.sh` whose required-file list matches exactly what was emitted (org assertions present only when `needs_org`); a full multi-surface golden fixture; a meta-check that runs the generated `check.sh` and asserts green.

- [ ] **Step 1: Write the failing tests — full kit renders org artifacts, is byte-equal, and its check.sh passes**

```python
import subprocess, shutil
def test_full_kit_matches_golden_and_check_passes():
    fx = SKILL/"tests/fixtures/full"
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d,"out"); written = sk.render_kit(str(fx/"kit.json"), out)
        assert "docs/org-provisioning.md" in written and "scripts/deploy.sh" in written
        for rel in written:
            assert open(os.path.join(out,rel),encoding="utf-8").read() == open(fx/"expected"/rel,encoding="utf-8").read(), f"drift in {rel}"
        # meta-check: the generated kit's own check.sh must be green
        r = subprocess.run(["bash","scripts/check.sh"], cwd=out, capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_scaffold.py::test_full_kit_matches_golden_and_check_passes -q`
Expected: FAIL — check.sh required-list not overlay-driven / fixtures absent.

- [ ] **Step 3: Implement overlay-driven `_render_check`**

```python
def _render_check(out_dir, cfg):
    req = ["README.md","GUIDE.md","FACILITATOR.md","LESSONS-LEARNED.md","config/kit.json",
           "scripts/lib/common.sh","scripts/00-preflight.sh"]
    if cfg.get("provisioning",{}).get("needs_org"):
        req += ["docs/org-provisioning.md","scripts/deploy.sh","scripts/assign-perms.sh"]
    req_lines = " ".join(req)
    tok = _tokens(cfg); tok["REQUIRED_FILES"] = req_lines
    _write(out_dir, "scripts/check.sh", _render("scripts/check.sh.tmpl", tok))
    return ["scripts/check.sh"]
```

Ensure `templates/scripts/check.sh.tmpl` iterates `{{REQUIRED_FILES}}` with a `req` helper + does internal-link resolution (mirror headless360 `check.sh`).

- [ ] **Step 4: Generate the full golden fixture**

```bash
$EDITOR tests/fixtures/full/kit.json   # needs_org:true, surfaces+content_dirs on, reference_build source "pie-poc-forge"
python3 scripts/scaffold_kit.py tests/fixtures/full/kit.json tests/fixtures/full/expected
( cd tests/fixtures/full/expected && bash scripts/check.sh )   # confirm ALL GREEN before locking
```

- [ ] **Step 5: Run tests to verify pass**

Run: `python3 -m pytest tests/test_scaffold.py -q`
Expected: PASS (all three tests).

- [ ] **Step 6: Mutation-verify**

Drop `docs/org-provisioning.md` from `_render_check`'s `req` list, re-run — confirm the generated check.sh still passes but note the required-list no longer matches emission; better mutation: make `render_kit` skip emitting `docs/org-provisioning.md` while check.sh still requires it → the meta-check FAILS. Restore, confirm PASS. Note in commit.

- [ ] **Step 7: Commit**

```bash
git add scripts/scaffold_kit.py tests/test_scaffold.py tests/fixtures/full && \
git commit -m "feat: overlay-driven check.sh + full golden fixture + meta-check (mutation-verified)"
```

---

## Task 11: Tier-3 validate_skill.py (assembled from skill-forge check-library)

**Files:**
- Create: `tests/validate_skill.py`

**Interfaces:**
- Consumes: snippet bodies from `~/.claude/skills/skill-forge/refs/check-library.md`; template `~/.claude/skills/skill-forge/templates/validate_skill.py.tmpl`.
- Produces: the green Tier-3 self-validation suite.

- [ ] **Step 1: Assemble the suite** — stamp from `validate_skill.py.tmpl`; inject the 13 Tier-3 snippet bodies verbatim into `{{INJECTED_CHECKS}}`; build `{{CHECK_REGISTRY}}` wrappers:

```python
@check("R-FM-01: frontmatter")            def _fm(): chk_frontmatter()
@check("R-REF-01: refusal conditions")    def _ref(): chk_refusal_present()
@check("R-ARCH-01: refs lazy-loaded")     def _a1(): chk_refs_dir()
@check("R-ARCH-02: referenced paths exist") def _a2(): chk_refs_exist()
@check("R-ARCH-03: no orphan refs")       def _a3(): chk_no_orphans()
@check("R-TEST-01: suite exists")         def _t1(): chk_test_suite_exists()
@check("R-TEST-02: token hygiene")        def _t2(): chk_token_hygiene()
@check("R-TEST-03: router parity")        def _t3(): chk_router_parity()
@check("R-TEST-04: behavioral tests")     def _t4(): chk_behavioral_tests()
@check("R-CI-01: pre-commit hook")        def _c1(): chk_precommit_hook()
@check("R-CI-02: CI workflow")            def _c2(): chk_ci_workflow()
@check("R-PROC-01: spec+plan archive")    def _p1(): chk_spec_plan_archive()
@check("R-DOC-01: README")                def _d1(): chk_readme()
```

- [ ] **Step 2: Run it**

Run: `python3 tests/validate_skill.py`
Expected: some FAIL initially — R-TEST-03 (router parity) needs SKILL.md ↔ refs to match (Task 2 named them; confirm every ref exists and every ref is referenced); R-CI-01/02 fail until Task 12. Fix R-ARCH/router failures now (rename/reference mismatches).

- [ ] **Step 3: Confirm R-TEST-04 sees the golden apparatus**

`chk_behavioral_tests` should pass because `tests/test_scaffold.py` + `tests/fixtures/` exist and exercise `scripts/scaffold_kit.py`.

- [ ] **Step 4: Commit**

```bash
git add tests/validate_skill.py && git commit -m "test: Tier-3 validate_skill.py (13 rubric checks)"
```

---

## Task 12: CI + hook + green gate + publish

**Files:**
- Create: `.githooks/pre-commit`, `.github/workflows/validate.yml`

**Interfaces:**
- Produces: R-CI-01 + R-CI-02 green; the full suite green; the published repo.

- [ ] **Step 1: Write `.githooks/pre-commit`** (from `skill-forge/templates/pre-commit.tmpl`) running `python3 tests/validate_skill.py` and the golden tests.

- [ ] **Step 2: Write `.github/workflows/validate.yml`** (from `skill-forge/templates/validate.yml.tmpl`) running `python3 tests/validate_skill.py` + `python3 -m pytest tests/test_scaffold.py` on push/PR.

- [ ] **Step 3: Activate the hook + run the full suite**

```bash
git config core.hooksPath .githooks
python3 tests/validate_skill.py            # expect 13/13 PASS
python3 -m pytest tests/test_scaffold.py -q # expect all PASS
```
Expected: both green. Repair and re-run if red — never proceed red.

- [ ] **Step 4: Commit**

```bash
git add .githooks/pre-commit .github/workflows/validate.yml && \
git commit -m "ci: pre-commit hook + GitHub Actions validation"
```

- [ ] **Step 5: Publish [GATE: confirm repo name/visibility with user]**

```bash
gh repo create workshop-forge --private --source . --remote origin --push
```
If `gh` is unauthenticated, stop and hand the user the exact command; never block the local build on remote auth.

---

## Task 13: DOGFOOD against the hand-built headless360-workshop

**Files:**
- Create: `docs/superpowers/dogfood-headless360.md` (findings), updates to `refs/`/`templates/` as gaps surface.

**Interfaces:**
- Consumes: the finished skill; ground truth at `/Users/bstauber/claude-projects/headless360-workshop`.
- Produces: a gap report + fixes; confidence the skill reproduces a real kit.

- [ ] **Step 1: Derive the headless360 overlay** — hand-write `kit.json` matching the real kit (mode=lab, duration=2-day, surfaces slack/react_agent_api/clt_lex, provisioning needs_org:true model=de-per-team required_features Agentforce+HostedMCP, modules 0–7 with 🔴 on M2/M4/M6, content_dirs slides+commercial+web, reference_build source=pie-poc-forge).

- [ ] **Step 2: Scaffold into a scratch dir**

```bash
python3 ~/.claude/skills/workshop-forge/scripts/scaffold_kit.py /tmp/h360-kit.json /tmp/h360-scaffold
( cd /tmp/h360-scaffold && bash scripts/check.sh )   # expect ALL GREEN
```

- [ ] **Step 3: Diff scaffold vs ground truth (structure)**

```bash
diff <(cd /tmp/h360-scaffold && find . -type f | sort) \
     <(cd /Users/bstauber/claude-projects/headless360-workshop && git ls-files | sort) \
  > /tmp/h360-structural.diff || true
```
Classify each delta: (a) expected (authored content / reference-build payload not scaffolded), (b) a template gap workshop-forge should fill, (c) noise.

- [ ] **Step 4: Author-mode pass (dry, on the scaffold)** — run the author flow against the scaffold using the real kit's source `.notes/` as freeform input; spot-check that GUIDE module bodies, `docs/org-provisioning.md`, and `commercial/` come out coherent and in-voice.

- [ ] **Step 5: Write the findings** to `docs/superpowers/dogfood-headless360.md` — what reproduced cleanly, category-(b) template gaps found, and fixes applied. Apply small template/ref fixes inline; log larger ones as backlog.

- [ ] **Step 6: Re-run the skill suite + commit**

```bash
python3 ~/.claude/skills/workshop-forge/tests/validate_skill.py   # still 13/13
cd ~/.claude/skills/workshop-forge && git add -A && \
git commit -m "test: dogfood workshop-forge against headless360 + gap fixes"
```

---

## Self-Review

- **Spec coverage:** two modes → Tasks 6/8-10 (scaffold) + 6/13 (author); overlay schema → Tasks 3,7,8; wrap-not-invent reference build → Tasks 2 (refusal),5; provisioning picker + "no org" first-class → Task 4 + conditional render Task 9; generated self-validating check.sh → Tasks 7,10; golden-file + mutation-verified generator → Tasks 9,10; Tier-3 suite → Task 11; CI/hook/spec-plan archive → Task 12 + this plan; family seam → Tasks 5,7; dogfood → Task 13. All covered.
- **Placeholder scan:** no "TBD/TODO/handle edge cases"; every code step shows code; commands show expected output. `$EDITOR` steps (fixture authoring) are genuine human-authoring actions, not placeholders — the surrounding steps pin exactly what the file must contain.
- **Type consistency:** `render_kit(kit_json_path, out_dir) -> sorted[str]`, `_render`, `_write`, `_tokens`, `_render_check` used consistently across Tasks 8/9/10; check names match check-library snippet names verbatim.
