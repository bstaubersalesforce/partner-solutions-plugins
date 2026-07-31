# workshop-forge Schema-Richness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add additive overlay-schema richness to workshop-forge (optional/mode-gated modules, `sample_data_path`, surfaces + model-enum cleanup), update docs incl. a README output-anatomy section, and validate via an nCino scaffold dogfood.

**Architecture:** All scaffolder changes are guarded on the presence of new overlay keys, so any kit.json lacking them renders byte-identically to today. The two existing golden fixtures (`educate`, `full`) are the back-compat gate; a new `rich` fixture exercises the new fields. Docs reconcile the `provisioning.model` enum to a single owner.

**Tech Stack:** Python 3 stdlib only (`scripts/scaffold_kit.py`), `{{TOKEN}}` string-substitution templates under `templates/`, bash `check.sh` self-validation, plain-`assert` tests run directly with `python3`.

## Global Constraints

- Python **stdlib only** — no third-party imports in `scaffold_kit.py`.
- Scaffolder is **deterministic, idempotent, no deletes** — repeat runs produce byte-identical output.
- All changes **additive + backward-compatible** — `tests/fixtures/educate/expected/` and `tests/fixtures/full/expected/` trees MUST stay byte-identical. Any drift there is a plan violation; stop and fix the code, never the golden.
- Valid workshop modes: **`"lab"`, `"engagement"`** (used for module `modes` validation).
- Values reaching bash/`check.sh` must pass existing `_slug()` / `_safe_path()` scrubbing.
- After every task: `python3 tests/validate_skill.py` (13/13) **and** `python3 tests/test_scaffold.py` (all pass) stay green. Pre-commit hook + CI enforce both.
- Author-mode content in stamped files uses the stub marker string `_(author mode fills this)_`.

---

### Task 1: Optional + mode-gated modules

**Files:**
- Modify: `scripts/scaffold_kit.py` — `_validate` (lines 38-45), module-section loop in `_tokens` (lines 105-113)
- Test: `tests/test_scaffold.py`

**Interfaces:**
- Consumes: existing `_validate(cfg)`, `_tokens(cfg)`, `render_kit(kit_json_path, out_dir)`, module dict shape `{n, title, checkpoint?}`.
- Produces: module dicts may now carry `optional: bool` and `modes: [str]`. `MODULE_LIST` token renders `(Optional)` suffix for optional modules and **omits** modules whose `modes` list excludes the kit's top-level `mode`. `config/kit.json` still records ALL modules (unfiltered — it's the as-authored overlay). Adds a module-level constant `VALID_MODES = {"lab", "engagement"}` at module scope.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_scaffold.py` (before the `if __name__` block):

```python
def test_optional_module_renders_marker():
    """A module with optional:true renders an (Optional) marker in GUIDE.md."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()
        cfg["modules"] = [{"n": 0, "title": "Comprehend"},
                          {"n": 6, "title": "Agent Grounding", "optional": True}]
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        out = os.path.join(d, "out")
        sk.render_kit(kj, out)
        guide = open(os.path.join(out, "GUIDE.md"), encoding="utf-8").read()
        assert "## Module 6: Agent Grounding (Optional)" in guide, guide
        assert "## Module 0: Comprehend\n" in guide, guide  # non-optional: no marker

def test_mode_gated_module_included_when_mode_matches():
    """A module gated to the kit's mode is rendered."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()  # mode == "lab"
        cfg["modules"] = [{"n": 0, "title": "Comprehend"},
                          {"n": 5, "title": "BYO Data", "modes": ["lab"]}]
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        out = os.path.join(d, "out")
        sk.render_kit(kj, out)
        guide = open(os.path.join(out, "GUIDE.md"), encoding="utf-8").read()
        assert "## Module 5: BYO Data" in guide, guide

def test_mode_gated_module_omitted_when_mode_differs():
    """A module gated to a different mode is omitted from GUIDE.md but kept in config."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()  # mode == "lab"
        cfg["modules"] = [{"n": 0, "title": "Comprehend"},
                          {"n": 5, "title": "Engagement Deep Dive", "modes": ["engagement"]}]
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        out = os.path.join(d, "out")
        sk.render_kit(kj, out)
        guide = open(os.path.join(out, "GUIDE.md"), encoding="utf-8").read()
        assert "Engagement Deep Dive" not in guide, guide
        cfgout = json.loads(open(os.path.join(out, "config/kit.json"), encoding="utf-8").read())
        titles = [m["title"] for m in cfgout["modules"]]
        assert "Engagement Deep Dive" in titles, "config/kit.json must retain all authored modules"

def test_module_optional_must_be_bool():
    """optional not a bool → clear ValueError mentioning 'optional'."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()
        cfg["modules"] = [{"n": 0, "title": "C", "optional": "yes"}]
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        try:
            sk.render_kit(kj, os.path.join(d, "out"))
            assert False, "should raise for non-bool optional"
        except ValueError as e:
            assert "optional" in str(e).lower(), e

def test_module_modes_must_be_nonempty_valid_list():
    """modes empty or containing an unknown mode → clear ValueError mentioning 'modes'."""
    with tempfile.TemporaryDirectory() as d:
        for bad in ([], ["bogus"], "lab"):
            cfg = MINIMAL.copy()
            cfg["modules"] = [{"n": 0, "title": "C", "modes": bad}]
            kj = os.path.join(d, "kit.json")
            open(kj, "w").write(json.dumps(cfg))
            try:
                sk.render_kit(kj, os.path.join(d, "out_" + str(bad)))
                assert False, f"should raise for modes={bad!r}"
            except ValueError as e:
                assert "modes" in str(e).lower(), e
```

Also register them in the `if __name__ == "__main__":` block (mirror the existing `func(); print("name: PASS")` pattern) for all five new tests.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 tests/test_scaffold.py`
Expected: FAIL — first new test raises `AssertionError` (marker not present) or the validation tests fail to raise.

- [ ] **Step 3: Add `VALID_MODES` and extend `_validate`**

At module scope near the top of `scripts/scaffold_kit.py` (after the imports/`TPL` line), add:

```python
VALID_MODES = {"lab", "engagement"}
```

In `_validate`, inside the existing `for i, m in enumerate(cfg.get("modules", [])):` loop, after the existing `title` checks, add:

```python
        if "optional" in m and not isinstance(m["optional"], bool):
            raise ValueError(f"Error: module {i} (n={m.get('n', '?')}) field 'optional' must be true/false")
        if "modes" in m:
            modes = m["modes"]
            if not isinstance(modes, list) or not modes:
                raise ValueError(f"Error: module {i} (n={m.get('n', '?')}) field 'modes' must be a non-empty list")
            bad = [x for x in modes if x not in VALID_MODES]
            if bad:
                raise ValueError(f"Error: module {i} (n={m.get('n', '?')}) field 'modes' has unknown mode(s) {bad}; valid: {sorted(VALID_MODES)}")
```

- [ ] **Step 4: Extend the module-section loop in `_tokens`**

Replace the existing loop (lines ~106-113) that builds `module_sections`:

```python
    module_sections = []
    for m in modules:
        section = f"## Module {m['n']}: {m['title']}\n\n<!-- body stub: author mode fills this -->"
        if m.get("checkpoint"):
            section += "\n\n🔴 **Checkpoint:** _(reason to be filled by author)_"
        module_sections.append(section)
    module_list = "\n\n".join(module_sections)
```

with:

```python
    kit_mode = cfg.get("mode")
    module_sections = []
    for m in modules:
        gate = m.get("modes")
        if gate and kit_mode not in gate:
            continue  # mode-gated out for this kit's mode
        title = m["title"] + (" (Optional)" if m.get("optional") else "")
        section = f"## Module {m['n']}: {title}\n\n<!-- body stub: author mode fills this -->"
        if m.get("checkpoint"):
            section += "\n\n🔴 **Checkpoint:** _(reason to be filled by author)_"
        module_sections.append(section)
    module_list = "\n\n".join(module_sections)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 tests/test_scaffold.py`
Expected: PASS (all tests, including the 5 new ones and the 2 existing golden tests — goldens unaffected because their modules carry neither key).

- [ ] **Step 6: Run the skill validation suite**

Run: `python3 tests/validate_skill.py`
Expected: `13/13 passed`.

- [ ] **Step 7: Commit**

```bash
cd ~/.claude/skills/workshop-forge
git add scripts/scaffold_kit.py tests/test_scaffold.py
git commit -m "feat(schema): optional + mode-gated modules"
```

---

### Task 2: `sample_data_path` / BYO data directory

**Files:**
- Create: `templates/data/README.md.tmpl`
- Modify: `scripts/scaffold_kit.py` — `render_kit` (after the content-dirs block, ~line 272) and `_render_check` (lines 283-297)
- Test: `tests/test_scaffold.py`

**Interfaces:**
- Consumes: `render_kit`, `_render_check`, `_safe_path`, the `tok` dict from `_tokens`, `_render(tpl_rel, tokens)`.
- Produces: when `cfg["reference_build"]["sample_data_path"]` is set + non-empty, `render_kit` emits `data/.gitkeep` and `data/README.md` (from the new template), and `_render_check` adds `data/README.md` to `REQUIRED_FILES`. Absent/empty → nothing emitted (back-compat).

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_scaffold.py` (and register in `__main__`):

```python
def test_sample_data_path_emits_data_dir():
    """reference_build.sample_data_path set → data/.gitkeep + data/README.md emitted and required."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()
        cfg["reference_build"] = {"source": "freeform", "path": "sfdx/", "sample_data_path": "data/"}
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        out = os.path.join(d, "out")
        written = sk.render_kit(kj, out)
        assert "data/.gitkeep" in written, written
        assert "data/README.md" in written, written
        assert os.path.exists(os.path.join(out, "data/README.md"))
        check = open(os.path.join(out, "scripts/check.sh"), encoding="utf-8").read()
        assert "data/README.md" in check, "check.sh must require data/README.md"
        # meta-check: generated check.sh passes
        r = subprocess.run(["bash", "scripts/check.sh"], cwd=out, capture_output=True, text=True)
        assert r.returncode == 0, f"{r.stdout}{r.stderr}"

def test_no_sample_data_path_emits_no_data_dir():
    """No sample_data_path → no data/ artifacts (back-compat)."""
    with tempfile.TemporaryDirectory() as d:
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(MINIMAL))  # no sample_data_path
        out = os.path.join(d, "out")
        written = sk.render_kit(kj, out)
        assert "data/.gitkeep" not in written
        assert "data/README.md" not in written
        assert not os.path.exists(os.path.join(out, "data"))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 tests/test_scaffold.py`
Expected: FAIL — `data/README.md` not in `written`.

- [ ] **Step 3: Create the data README template**

Create `templates/data/README.md.tmpl`:

```markdown
# Sample Data — {{KIT_TITLE}}

This directory holds the sample datasets the workshop references (CSV/JSON seed
files, load scripts, and any generators).

_(author mode fills this)_
```

- [ ] **Step 4: Emit the data dir in `render_kit`**

In `render_kit`, immediately **after** the "Conditional rendering: sfdx placeholder" block (after line ~276, before `written += _render_check(...)`), add:

```python
    # Conditional rendering: sample-data directory
    sample_data = cfg.get("reference_build", {}).get("sample_data_path")
    if sample_data and str(sample_data).strip():
        _write(out_dir, "data/.gitkeep", "")
        written.append("data/.gitkeep")
        _write(out_dir, "data/README.md", _render("data/README.md.tmpl", tok))
        written.append("data/README.md")
```

- [ ] **Step 5: Require data/README.md in `_render_check`**

In `_render_check`, after the `needs_org` append block and before `tok["REQUIRED_FILES"] = ...`, add exactly this:

```python
    _sdp = cfg.get("reference_build", {}).get("sample_data_path")
    if _sdp and str(_sdp).strip():
        req.append("data/README.md")
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python3 tests/test_scaffold.py`
Expected: PASS (new tests pass; `educate`/`full` goldens unaffected — neither sets `sample_data_path`).

- [ ] **Step 7: Run the skill validation suite**

Run: `python3 tests/validate_skill.py`
Expected: `13/13 passed`.

- [ ] **Step 8: Commit**

```bash
cd ~/.claude/skills/workshop-forge
git add scripts/scaffold_kit.py templates/data/README.md.tmpl tests/test_scaffold.py
git commit -m "feat(schema): sample_data_path emits data/ dir + README stub"
```

---

### Task 3: `rich` golden fixture (all new fields, byte-equal + meta-check)

**Files:**
- Create: `tests/fixtures/rich/kit.json`
- Create: `tests/fixtures/rich/expected/**` (generated, then committed as the golden)
- Test: `tests/test_scaffold.py`

**Interfaces:**
- Consumes: `sk.render_kit`, the Task 1 + Task 2 behavior.
- Produces: a third committed golden tree proving the combined new-field output is stable and self-validates.

- [ ] **Step 1: Write the fixture overlay**

Create `tests/fixtures/rich/kit.json`:

```json
{
  "name": "rich-schema-kit",
  "title": "Rich Schema Workshop",
  "mode": "lab",
  "duration": "1-day",
  "partner_overlay": "reference",
  "surfaces": {},
  "provisioning": {
    "needs_org": false,
    "model": "none",
    "required_features": []
  },
  "modules": [
    { "n": 0, "title": "Comprehend" },
    { "n": 1, "title": "Model the Data", "checkpoint": true },
    { "n": 5, "title": "BYO Dataset", "modes": ["lab"] },
    { "n": 6, "title": "Agent Grounding", "optional": true },
    { "n": 7, "title": "Engagement Deep Dive", "modes": ["engagement"] }
  ],
  "content_dirs": { "slides": true },
  "reference_build": { "source": "freeform", "path": "sfdx/", "sample_data_path": "data/" }
}
```

(Note: `needs_org:false` keeps the fixture small — org files stay out — so the golden focuses on the new module/data behavior. Module 7 is gated to `engagement` and MUST be absent from the rendered GUIDE; Module 5 is gated to `lab` and MUST be present.)

- [ ] **Step 2: Write the failing test**

Add to `tests/test_scaffold.py` (and register in `__main__`):

```python
def test_rich_kit_matches_golden_and_check_passes():
    """Rich fixture (optional + mode-gated modules + sample_data_path) is byte-equal and self-validates."""
    fx = SKILL / "tests/fixtures/rich"
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out")
        written = sk.render_kit(str(fx / "kit.json"), out)
        # new-field expectations
        assert "data/README.md" in written, written
        guide = open(os.path.join(out, "GUIDE.md"), encoding="utf-8").read()
        assert "## Module 6: Agent Grounding (Optional)" in guide
        assert "## Module 5: BYO Dataset" in guide
        assert "Engagement Deep Dive" not in guide  # gated to engagement
        # byte-equal against committed golden
        for rel in written:
            got = open(os.path.join(out, rel), encoding="utf-8").read()
            exp = open(fx / "expected" / rel, encoding="utf-8").read()
            assert got == exp, f"drift in {rel}"
        # meta-check
        r = subprocess.run(["bash", "scripts/check.sh"], cwd=out, capture_output=True, text=True)
        assert r.returncode == 0, f"{r.stdout}{r.stderr}"
```

- [ ] **Step 3: Run to verify it fails**

Run: `python3 tests/test_scaffold.py`
Expected: FAIL — `tests/fixtures/rich/expected/...` does not exist yet (FileNotFoundError).

- [ ] **Step 4: Generate the golden tree**

Run:
```bash
cd ~/.claude/skills/workshop-forge
python3 scripts/scaffold_kit.py tests/fixtures/rich/kit.json tests/fixtures/rich/expected
```

- [ ] **Step 5: Manually verify the golden before trusting it**

Run and eyeball:
```bash
cd ~/.claude/skills/workshop-forge
grep -n "Module" tests/fixtures/rich/expected/GUIDE.md
ls tests/fixtures/rich/expected/data/
cat tests/fixtures/rich/expected/scripts/check.sh | grep -n "REQUIRED_FILES\|data/README"
bash -c 'cd tests/fixtures/rich/expected && bash scripts/check.sh'
```
Expected: GUIDE shows Modules 0,1,5,6 (with `6 ... (Optional)`), **no** Module 7; `data/` contains `.gitkeep` + `README.md`; `check.sh` requires `data/README.md` and prints ALL GREEN. If any of these is wrong, the golden is wrong — fix Task 1/2 code, regenerate, do not commit a bad golden.

- [ ] **Step 6: Run tests to verify they pass**

Run: `python3 tests/test_scaffold.py`
Expected: PASS.

- [ ] **Step 7: Run the skill validation suite**

Run: `python3 tests/validate_skill.py`
Expected: `13/13 passed`.

- [ ] **Step 8: Commit**

```bash
cd ~/.claude/skills/workshop-forge
git add tests/fixtures/rich tests/test_scaffold.py
git commit -m "test(schema): rich golden fixture — optional/mode-gated modules + sample_data_path"
```

---

### Task 4: Docs — anatomy, guide conventions, provisioning enum, surfaces convention, README output-anatomy, BACKLOG

**Files:**
- Modify: `refs/kit-anatomy.md` (schema block lines 51-68, key-behaviors 71-81)
- Modify: `refs/guide-conventions.md`
- Modify: `refs/provisioning-models.md`
- Modify: `README.md` (overlay example 60-81, output tree 94-105)
- Modify: `BACKLOG.md`
- Test: `python3 tests/validate_skill.py` (R-DOC-01, R-ARCH-02/03 exercise refs/README)

**Interfaces:**
- Consumes: nothing (pure docs). Must stay consistent with the code shipped in Tasks 1-2 and the enum owned here.
- Produces: single-source `provisioning.model` enum in `refs/provisioning-models.md`; the README output-anatomy section.

- [ ] **Step 1: Update `refs/kit-anatomy.md` schema block**

In the ```jsonc schema (lines 51-68), change the `surfaces`, `modules`, and `reference_build` lines to:

```jsonc
  "surfaces": { "slack": true, "react_agent_api": true, "clt_lex": true, "mobile": false },
                                      // {} = no surfaces by design; key omitted = not yet decided
  ...
  "modules": [ /* ordered {n, title, checkpoint?, optional?, modes?:["lab"|"engagement"]};
                  Module 0 Comprehend … Module N Extend */ ],
  ...
  "reference_build": { "source": "pie-poc-forge|freeform|none", "path": "sfdx/",
                       "sample_data_path": "data/"  /* optional: set ⇒ emit data/ dir + README stub */ }
```

In "Key overlay behaviors" (lines 71-81), add three bullets:

```markdown
- `modules[].optional: true` → the GUIDE header is stamped `## Module N: Title (Optional)`.
- `modules[].modes: ["lab"|"engagement"]` → the module is rendered in GUIDE.md **only** when the
  kit's top-level `mode` is in the list; otherwise it is omitted from GUIDE.md (but retained in
  `config/kit.json`, which records the overlay as authored).
- `reference_build.sample_data_path` (optional) → when set, the scaffolder emits a `data/`
  directory with a `data/README.md` stub and the kit validator requires it. Absent ⇒ no `data/`.
- `surfaces: {}` means **no surfaces, by design** (e.g. a Data-Cloud pipeline kit); omitting the
  `surfaces` key entirely means **not yet decided**. `surfaces` remains descriptive-only.
```

In "Per-engagement overlay differences" replace the standalone model list reference so the enum is **not** re-listed here; add: `The full \`provisioning.model\` enum is owned by \`refs/provisioning-models.md\`.`

- [ ] **Step 2: Update `refs/guide-conventions.md`**

Append a subsection documenting optional + mode-gated module rendering:

```markdown
## Optional & mode-gated modules

- **Optional modules** (`optional: true` in the overlay) render with an `(Optional)` suffix in the
  module header, e.g. `## Module 6: Agent Grounding (Optional)`. Use for modules a team can skip
  without breaking the arc (e.g. data360's "(Optional) Agent Grounding").
- **Mode-gated modules** (`modes: ["lab"]` or `["engagement"]`) appear in GUIDE.md only when the
  kit's top-level `mode` matches. A `lab`-only "BYO Dataset" module is omitted from an
  `engagement` kit's GUIDE, and vice-versa. The module still lives in `config/kit.json` (the
  authored overlay); only the participant-facing GUIDE is filtered.
```

- [ ] **Step 3: Update `refs/provisioning-models.md` — own the enum + elevate the conceptual path**

Add, near the top (after the intro paragraph, before "The three-step method"), an explicit enum block:

```markdown
## `provisioning.model` enum (single source of truth)

Valid values for `kit.json.provisioning.model`:

| Value | Meaning |
|-------|---------|
| `none` | No participant orgs (`needs_org:false`) — conceptual / educate-only / shared-backend. |
| `de-per-team` | One free Developer Edition per team (Agentforce-centric). |
| `sdo-per-team` | One SDO (Enterprise) per team (Data-Cloud-connector-centric). |
| `assigned-preconfigured` | Pre-baked orgs handed out as aliases (managed-package / multi-cloud). |
| `scratch-pool` | Scratch-org pool + snapshot (facilitator/CI; not for participants). |
| `tiered-fallback` | ⚠️ Recognized vocabulary, **not yet scaffolded** — a sequenced fallback (partner org → facilitator pool → shared reference). Deferred; documented so the enum is complete. |

Other refs (`kit-anatomy.md`, `README.md`) reference this table rather than re-listing it.
```

In Step 1's table area, reinforce the conceptual framing — add a sentence under the `needs_org:false` heading:

```markdown
**Conceptual / educate-only workshops are the canonical `needs_org:false` case.** When org shape is
lower-priority (the workshop teaches concepts, patterns, or architecture rather than hands-on
build), set `needs_org:false` and `model:"none"`; note in `docs/org-provisioning.md`'s absence that
this is deliberate, not a gap.
```

- [ ] **Step 4: Update `README.md` overlay example**

In the ```jsonc overlay (lines 60-81), update the `surfaces`, `modules`, `content_dirs`, and `reference_build` lines to show the new fields:

```jsonc
  "surfaces": { "slack": false, "react_agent_api": false },   // descriptive; {} = none by design, omit = TBD
  ...
  "modules": [                            // Module 0 "Comprehend" … Module N "Extend"
    { "n": 0, "title": "Comprehend" },
    { "n": 2, "title": "Model (DMO)", "checkpoint": true },       // 🔴 order-sensitive step
    { "n": 5, "title": "BYO Dataset", "modes": ["lab"] },         // lab-only; omitted in engagement kits
    { "n": 6, "title": "Agent Grounding", "optional": true },     // renders "(Optional)"
    { "n": 7, "title": "Extend" }
  ],
  "content_dirs": { "slides": true, "commercial": true },
  "reference_build": { "source": "pie-poc-forge", "path": "sfdx/", "sample_data_path": "data/" }
```

Update the "Key behaviors" list to add:

```markdown
- **Modules can be `optional`** (renders an `(Optional)` marker) or **mode-gated** (`modes:["lab"]`)
  so a module appears only in the matching workshop mode; the overlay still records every module.
- **`reference_build.sample_data_path`** — set it for kits that ship sample datasets; the scaffolder
  stamps a `data/` dir + README stub (data360-style kits ship dozens of data files).
```

- [ ] **Step 5: Add the README "Anatomy of the output" section**

Insert a new section in `README.md` immediately after "What a generated kit contains" (after line 108):

```markdown
## Anatomy of the output — what each piece is for

A generated kit is one coherent deliverable read by four audiences across the workshop lifecycle:

| Artifact | Audience | When it's used |
|----------|----------|----------------|
| `README.md` | everyone | first contact — what this is, who it's for, how to run |
| `docs/org-provisioning.md` | ops / facilitator | **T-minus 5+ days** — provision + preflight orgs (only for `needs_org` kits) |
| `scripts/` (`00-preflight` … `check.sh`) | ops / facilitator | T-minus prep + morning-of alias checks; `check.sh` validates kit shape |
| `FACILITATOR.md` | facilitator | prep + in-room — run-of-show, timing, fallbacks, demo reminders |
| `docs/framework.md`, `docs/buildability-matrix.md` | facilitator / partner-exec | prep + debrief — the teaching model and the paid-extension scoping story |
| `GUIDE.md` | participant | **in-room** — the hands-on Module 0→N arc with 🔴 checkpoints |
| `data/`, `sfdx/` | participant / facilitator | in-room — the sample data and reference build the modules operate on |
| `slides/`, `commercial/`, `showcase/` (per `content_dirs`) | facilitator / partner-exec | prep + delivery — decks and commercial framing |
| `LESSONS-LEARNED.md` | facilitator | **after** — retro: what to fix before the next run |

**How they compose:** provisioning + scripts stand up the environment before the room opens;
FACILITATOR + framework prime the facilitator; GUIDE (against `data/`/`sfdx/`) is what participants
actually do; slides/commercial wrap the business narrative; LESSONS-LEARNED closes the loop. For a
**conceptual / educate-only** kit (`needs_org:false`), the provisioning + scripts + `sfdx/` rows
drop out and the kit is GUIDE + slides + framework — a fully valid, non-degraded shape.
```

- [ ] **Step 6: Update `BACKLOG.md`**

In the "High — the overlay under-models real kits" section, mark landed items done and leave tiered-fallback open. Change the checkboxes:
- `[x]` `sample_data_path / BYO dataset` — **landed 2026-07-16**
- `[x]` `Optional modules` — **landed 2026-07-16**
- `[x]` `Interleaved / mode-gated modules` — **landed 2026-07-16 (via `modes`)**
- `[x]` `surfaces: {}` semantics — **landed 2026-07-16 (documented convention)**
- `[x]` `Document provisioning.model enum` — **landed 2026-07-16 (enum table in provisioning-models.md)**
- leave `[ ]` **3-tier provisioning fallback** open, annotated: `deferred — vocabulary reserved as \`tiered-fallback\`, rendering not built`.

Add a line under "Validate": `[ ] nCino scaffold dogfood — see docs/superpowers/dogfood-ncino.md (run 2026-07-16).` (Task 5 writes that file.)

- [ ] **Step 7: Run the skill validation suite**

Run: `python3 tests/validate_skill.py`
Expected: `13/13 passed` (R-DOC-01 README present; R-ARCH-02 referenced paths exist; R-ARCH-03 no orphan refs — the new `templates/data/README.md.tmpl` from Task 2 is referenced by anatomy/scaffolder, verify no dangling ref).

- [ ] **Step 8: Commit**

```bash
cd ~/.claude/skills/workshop-forge
git add refs/kit-anatomy.md refs/guide-conventions.md refs/provisioning-models.md README.md BACKLOG.md
git commit -m "docs(schema): anatomy/guide/provisioning enum + README output-anatomy + BACKLOG"
```

---

### Task 5: nCino scaffold dogfood

**Files:**
- Create: `docs/superpowers/dogfood-ncino.md` (findings)
- Create (throwaway, gitignored): `./dogfood-ncino/` scaffold output — do NOT commit
- Modify: `.gitignore` (add `dogfood-ncino/` if not already ignored)
- Reference (read-only): `~/claude-projects/ncino-pov/ncino-workshop`

**Interfaces:**
- Consumes: the shipped scaffolder (Tasks 1-4), the real nCino kit as ground truth.
- Produces: a findings doc categorizing deltas (expected vs. genuine gaps) and confirming new-field coverage.

- [ ] **Step 1: Confirm the reference kit shape**

Run:
```bash
find ~/claude-projects/ncino-pov/ncino-workshop -maxdepth 2 -not -path '*/.git/*' | sort
```
Expected: `.env.example`, `config/`, `data/covenant-monitors.apex`, `force-app/`, `GUIDE.md`, `LESSONS-LEARNED.md`, `README.md`, `scripts/{01-check-env,02-deploy,03-assign-perms,05-seed-data,06-smoke-test}.sh`, `sfdx-project.json`. (Note: flatter — no `FACILITATOR.md`, no `docs/`.)

- [ ] **Step 2: Author the nCino overlay**

Create `docs/superpowers/dogfood-ncino-kit.json` (the input overlay, kept with the findings for reproducibility):

```json
{
  "name": "ncino-workshop",
  "title": "nCino Banking Advisor Partner Workshop",
  "mode": "engagement",
  "partner_overlay": "nCino",
  "duration": "1-day",
  "surfaces": { "slack": true },
  "provisioning": {
    "needs_org": true,
    "model": "assigned-preconfigured",
    "required_features": ["nCino Managed Package", "Agentforce", "Hosted MCP (shared Worker)"]
  },
  "modules": [
    { "n": 0, "title": "Comprehend the Banking Advisor Pattern" },
    { "n": 1, "title": "Connect to the Shared MCP Backend", "checkpoint": true },
    { "n": 2, "title": "Ground the Agent in nCino Data", "checkpoint": true },
    { "n": 3, "title": "Extend the Agent" },
    { "n": 4, "title": "Self-Service Org Rebuild", "optional": true }
  ],
  "content_dirs": {},
  "reference_build": { "source": "freeform", "path": "sfdx/", "sample_data_path": "data/" }
}
```

- [ ] **Step 3: Scaffold it (throwaway output)**

Run:
```bash
cd ~/.claude/skills/workshop-forge
python3 scripts/scaffold_kit.py docs/superpowers/dogfood-ncino-kit.json ./dogfood-ncino
cd dogfood-ncino && bash scripts/check.sh; cd ..
```
Expected: scaffold completes; `check.sh` prints ALL GREEN. Capture any failure verbatim for the findings.

- [ ] **Step 4: Structural diff vs. the real kit**

Run:
```bash
cd ~/.claude/skills/workshop-forge
diff <(cd dogfood-ncino && find . -type f -not -path './.git/*' | sort) \
     <(cd ~/claude-projects/ncino-pov/ncino-workshop && find . -type f -not -path './.git/*' | sort)
grep -n "Module" dogfood-ncino/GUIDE.md
ls dogfood-ncino/data/
```
Expected observations to record: `data/` dir emitted (new field works); Module 4 shows `(Optional)`; engagement mode; deltas include real kit's `FACILITATOR.md` absence, `05-seed-data.sh`/`06-smoke-test.sh` (engagement-specific, author-mode's job), `force-app/`+`sfdx-project.json` (reference-build payload).

- [ ] **Step 5: Write the findings doc**

Create `docs/superpowers/dogfood-ncino.md` capturing:
- **New-field coverage** — confirm each shipped field (`optional` module, `sample_data_path`→`data/`, engagement mode, `assigned-preconfigured` model) expressed nCino's shape.
- **Delta table** — each structural diff line categorized **Expected** (authored content, engagement-specific scripts, reference-build payload, flatter hand-built layout) vs. **Genuine gap** (schema still can't express X).
- **Conceptual-framing note** — explicitly assess where org shape mattered less for this engagement kit and confirm the `needs_org`/conceptual-path framing reads correctly.
- **Genuine gaps → BACKLOG** — list any true gaps as new BACKLOG candidates (do not silently drop).

- [ ] **Step 6: Ensure the throwaway output is ignored**

Run:
```bash
cd ~/.claude/skills/workshop-forge
grep -qxF 'dogfood-ncino/' .gitignore || echo 'dogfood-ncino/' >> .gitignore
git status --short
```
Expected: `dogfood-ncino/` does NOT appear as an untracked dir in `git status` (it's ignored). Only `docs/superpowers/dogfood-ncino.md`, `docs/superpowers/dogfood-ncino-kit.json`, and possibly `.gitignore` are staged-worthy.

- [ ] **Step 7: Run the full validation suite (regression guard)**

Run:
```bash
cd ~/.claude/skills/workshop-forge
python3 tests/validate_skill.py && python3 tests/test_scaffold.py
```
Expected: `13/13 passed` and `All tests passed!`.

- [ ] **Step 8: Commit**

```bash
cd ~/.claude/skills/workshop-forge
git add docs/superpowers/dogfood-ncino.md docs/superpowers/dogfood-ncino-kit.json .gitignore
git commit -m "test(dogfood): nCino scaffold dogfood — new-field coverage + delta findings"
```

---

## Notes for the executor

- **Never edit a golden to make a test pass.** If `educate`/`full` drift, the additive-code contract is broken — fix `scaffold_kit.py`. The `rich` golden (Task 3) is generated once from correct code, then frozen.
- Run tests with `python3 tests/test_scaffold.py` (they use plain `assert` + a `__main__` runner, not pytest).
- Every task ends green on **both** suites and a commit. The pre-commit hook runs them anyway.
- Final state target: 3 goldens (educate/full byte-unchanged + new rich), all schema-richness backlog items except tiered-fallback checked off, README carries the output-anatomy section, nCino dogfood findings committed.
