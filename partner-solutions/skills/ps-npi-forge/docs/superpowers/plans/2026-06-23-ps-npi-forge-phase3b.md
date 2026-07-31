# PS-NPI-FORGE Phase 3b — Generate→Refine→Validate cycle + 4 quality loops (+ live Org62 intake)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Standard-mode draft→refine→validate for all 11 artifacts — the mechanical engine (render, section-diff edit-preservation, uncertainty scan, Org62 entitlement parse, manifest loop-verdict state) in tested Python plus the judgment (the four quality loops, the cycle narration, the Org62 query spine) as lazy-loaded refs — and prove it end-to-end on the pasted Agentforce-for-Healthcare brief.

**Architecture:** Mechanical → code, judgment → agent. Five Python units in `scripts/` (each behaviorally tested against fixtures), two new instruction refs in `refs/`, and a grown manifest schema (`loops` verdicts + `last_generated` baseline pointer). The validation suite grows from 20 → 29 checks; the live-org and full-narrative steps are capability-gated/manual, never CI-blocking.

**Tech Stack:** Python 3 stdlib only (no deps); the existing `tests/validate_skill.py` harness (`@check`, `_load_script`, fixtures under `tests/fixtures/`); markdown templates from Phase 3a.

## Global Constraints

- **Skill location:** `~/.claude/skills/ps-npi-forge/` (own git repo; remote `origin` → private `github.com/bstaubersalesforce/ps-npi-forge`).
- **Python:** stdlib only. Suite runs `python3 tests/validate_skill.py`; must stay green and grow. Scripts must be side-effect-free libraries (no `sf`/network/Slack calls in `scripts/`; parsers consume already-fetched data).
- **ARTIFACT_REGISTRY (verbatim, already in `scripts/manifest.py` + `tests/validate_skill.py`):** `00-executive-summary`, `01-brief`, `02-slide-summary`, `03-internal-enablement`, `04-internal-faq`, `05-external-faq`, `06-license-entitlements`, `07-addon-tiering`, `08-setup-guide`, `09-org-provisioning-validation`, `10-partner-profile-pov`.
- **New manifest constants (single source of truth, must match between `scripts/manifest.py` and `tests/validate_skill.py`):** `LOOP_REGISTRY = ["claim_verification", "completeness", "uncertainty", "partner_lens"]`; `VERDICT_VOCAB = ["pass", "flag", "fail"]`. A freshly seeded loop verdict is `""` (not-yet-run); `set_loop_verdict` only accepts a value from `VERDICT_VOCAB`.
- **Token convention:** every `{{TOKEN}}` is `UPPER_SNAKE_CASE` (`[A-Z0-9_]+`); `render` only substitutes tokens matching that shape and leaves any unmatched/unknown token literal.
- **Edit-preservation unit:** one section = one `## H2` block of an artifact. The H1 + gap-banner blockquote (before the first `## `) and the footer (from the standalone `---` rule onward) are tool-owned and always regenerate.
- **Refusal rules unchanged (SKILL.md):** official Salesforce docs only; never assert entitlements without flagging for human confirmation; pricing out of scope (placeholders only); Org62 read-only; never publish to Slack without confirmation; never silently drop an uncertainty.
- **Effort data lives outside the repo** at `/Users/bstauber/claude-projects/ps-npi-efforts/<release>/<product-slug>/`; baselines under `artifacts/.baseline/`. Nothing under there is committed to the skill repo.
- **Each script gets a behavioral test (skill-forge R-TEST-04 discipline):** the suite loads it via `_load_script` and exercises it against a golden fixture under `tests/fixtures/`.

## File Structure

- `scripts/manifest.py` — **modify**: add `LOOP_REGISTRY`, `VERDICT_VOCAB`, grow `new_effort`, `dumps`, `load`; add `set_loop_verdict`, `set_last_generated`.
- `scripts/render.py` — **create**: `render(template_text, fills) -> (artifact_md, unfilled)`.
- `scripts/sections.py` — **create**: `split(md) -> dict`, `locked_sections(live_md, baseline_md) -> set`.
- `scripts/scan.py` — **create**: `scan(md) -> list[dict]` (uncertainty/gap markers).
- `scripts/org62.py` — **create**: `parse_entitlements(sf_json) -> dict` (pure parser).
- `refs/quality-loops.md` — **create**: the cycle + four loops (judgment prose).
- `refs/org62-entitlements.md` — **create**: pinned `sf`/SOQL query spine + parent-SKU modeling (closes B1).
- `tests/fixtures/org62/parent-entitlements.json` — **create**: sanitized captured pull (parser contract).
- `tests/validate_skill.py` — **modify**: +9 checks; tighten R-TPL-02 (B7); simplify R-TPL-01 (B8); extend R-MANIFEST-06.
- `SKILL.md` — **modify**: wire both new refs; expand the cycle section.
- `BACKLOG.md` — **modify**: mark Phase 3b done; close B1/B6/B7/B8.
- `docs/superpowers/acceptance/2026-06-23-healthcare-dogfood.md` — **create**: dogfood acceptance record.

---

### Task 1: Grow the manifest — loop verdicts + last_generated

**Files:**
- Modify: `scripts/manifest.py`
- Modify: `tests/validate_skill.py` (add constants, R-MANIFEST-07, R-MANIFEST-08; extend R-MANIFEST-06)
- Modify: `templates/manifest.yaml` (regenerate to carry the new schema)

**Interfaces:**
- Consumes: existing `manifest.py` (`new_effort`, `set_status`, `dumps`, `load`, `overall_confidence`, `_scalar`, `_parse_scalar`, `_inline_list`, `_parse_inline_list`).
- Produces: `LOOP_REGISTRY`, `VERDICT_VOCAB`; `set_loop_verdict(manifest, artifact, loop, verdict, note="")`, `set_last_generated(manifest, artifact, pointer)`; each artifact record now has `loops: {loop: {verdict, note}}` and `last_generated: str`. Round-trip preserves both.

- [ ] **Step 1: Write the failing tests** — append to `tests/validate_skill.py` before `# ---- runner`, and add the two constants next to `STATUS_VOCAB` (top of file).

Add beside `STATUS_VOCAB` (after line 36):

```python
LOOP_REGISTRY = ["claim_verification", "completeness", "uncertainty", "partner_lens"]
VERDICT_VOCAB = ["pass", "flag", "fail"]
```

Append before the runner:

```python
# ---- R-MANIFEST-07/08: loop verdicts + last_generated -------------------
@check("R-MANIFEST-07: loops + last_generated survive round-trip and re-dump is stable")
def t_manifest_loops_roundtrip():
    m = _load_script("scripts/manifest.py", "manifest_mod7")
    eff = m.new_effort("summer-26", "x-oem", "Parent EE")
    # every artifact seeded with all four loops at the not-yet-run verdict
    for a in ARTIFACT_REGISTRY:
        assert set(eff["artifacts"][a]["loops"].keys()) == set(LOOP_REGISTRY), f"{a} loops not seeded"
        for lp in LOOP_REGISTRY:
            assert eff["artifacts"][a]["loops"][lp]["verdict"] == "", "seed verdict should be '' (not run)"
        assert eff["artifacts"][a]["last_generated"] == ""
    eff = m.set_loop_verdict(eff, "06-license-entitlements", "claim_verification", "flag",
                             "PSL naming delta unconfirmed")
    eff = m.set_last_generated(eff, "06-license-entitlements", "artifacts/.baseline/06-license-entitlements.md")
    import tempfile, os as _os
    p = _os.path.join(tempfile.mkdtemp(), "manifest.yaml")
    open(p, "w").write(m.dumps(eff))
    back = m.load(p)
    lp = back["artifacts"]["06-license-entitlements"]["loops"]["claim_verification"]
    assert lp["verdict"] == "flag" and lp["note"] == "PSL naming delta unconfirmed", "loop verdict lost"
    assert back["artifacts"]["06-license-entitlements"]["last_generated"] == \
        "artifacts/.baseline/06-license-entitlements.md", "last_generated lost"
    # re-dump is byte-stable
    assert m.dumps(back) == m.dumps(eff), "round-trip is not stable"

@check("R-MANIFEST-08: set_loop_verdict rejects unknown loop or verdict")
def t_manifest_loop_guard():
    m = _load_script("scripts/manifest.py", "manifest_mod8")
    eff = m.new_effort("r", "p", "parent")
    try:
        m.set_loop_verdict(eff, "01-brief", "nope_loop", "pass"); assert False, "unknown loop should raise"
    except ValueError: pass
    try:
        m.set_loop_verdict(eff, "01-brief", "completeness", "banana"); assert False, "bad verdict should raise"
    except ValueError: pass
    try:
        m.set_loop_verdict(eff, "99-nope", "completeness", "pass"); assert False, "unknown artifact should raise"
    except ValueError: pass
```

Extend `t_manifest_constant_parity` (R-MANIFEST-06) — add after the existing two asserts:

```python
    assert m.LOOP_REGISTRY == LOOP_REGISTRY, "LOOP_REGISTRY drift between manifest.py and validate_skill.py"
    assert m.VERDICT_VOCAB == VERDICT_VOCAB, "VERDICT_VOCAB drift between manifest.py and validate_skill.py"
```

- [ ] **Step 2: Run the suite to verify the new checks FAIL**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on R-MANIFEST-06 (`AttributeError`/missing `LOOP_REGISTRY`), R-MANIFEST-07, R-MANIFEST-08 (missing `set_loop_verdict`/`loops`).

- [ ] **Step 3: Grow `scripts/manifest.py`** — add the constants, the two setters, and replace `new_effort`, `dumps`, `load`.

Add after the existing `STATUS_VOCAB`/`ARTIFACT_REGISTRY` block (after line 16):

```python
LOOP_REGISTRY = ["claim_verification", "completeness", "uncertainty", "partner_lens"]
VERDICT_VOCAB = ["pass", "flag", "fail"]
```

Replace `new_effort` (lines 18-29) with:

```python
def new_effort(release, product_slug, parent_sku):
    return {
        "release": release,
        "product_slug": product_slug,
        "parent_sku": parent_sku,
        "slack_channel": "",
        "artifacts": {
            a: {"status": "pending", "confidence": 0.0, "rationale": "",
                "sources": [], "placeholders": [],
                "loops": {lp: {"verdict": "", "note": ""} for lp in LOOP_REGISTRY},
                "last_generated": ""}
            for a in ARTIFACT_REGISTRY
        },
    }
```

Add the two setters after `set_status` (after line 37):

```python
def set_loop_verdict(manifest, artifact, loop, verdict, note=""):
    if artifact not in manifest["artifacts"]:
        raise ValueError(f"unknown artifact: {artifact}")
    if loop not in LOOP_REGISTRY:
        raise ValueError(f"unknown loop: {loop} (allowed: {LOOP_REGISTRY})")
    if verdict not in VERDICT_VOCAB:
        raise ValueError(f"unknown verdict: {verdict} (allowed: {VERDICT_VOCAB})")
    manifest["artifacts"][artifact].setdefault("loops", {})[loop] = {"verdict": verdict, "note": note}
    return manifest

def set_last_generated(manifest, artifact, pointer):
    if artifact not in manifest["artifacts"]:
        raise ValueError(f"unknown artifact: {artifact}")
    manifest["artifacts"][artifact]["last_generated"] = pointer
    return manifest
```

In `dumps`, after the placeholders loop (after current line 61, inside the `for a in ARTIFACT_REGISTRY` loop), add:

```python
        lines.append("    loops:")
        loops = rec.get("loops") or {}
        for lp in LOOP_REGISTRY:
            v = loops.get(lp) or {"verdict": "", "note": ""}
            lines.append(f"      {lp}:")
            lines.append(f"        verdict: {_scalar(v.get('verdict',''))}")
            lines.append(f"        note: {_scalar(v.get('note',''))}")
        lines.append(f"    last_generated: {_scalar(rec.get('last_generated',''))}")
```

Replace `load` (lines 75-112) with the section-aware parser:

```python
def load(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    manifest = {"artifacts": {}}
    cur_art = None
    cur_section = None   # None | "placeholders" | "loops"
    cur_ph = None
    cur_loop = None
    for raw in lines:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0:
            if line == "artifacts:":
                cur_art = None; cur_section = None; continue
            k, _, v = line.partition(":")
            manifest[k.strip()] = _parse_scalar(v.strip())
        elif indent == 2 and line.endswith(":"):
            cur_art = line[:-1].strip()
            manifest["artifacts"][cur_art] = {
                "sources": [], "placeholders": [], "loops": {}, "last_generated": ""}
            cur_section = None; cur_ph = None; cur_loop = None
        elif indent == 4 and cur_art:
            k, _, v = line.partition(":")
            k = k.strip()
            if k == "placeholders":
                cur_section = "placeholders"; cur_ph = None; continue
            if k == "loops":
                cur_section = "loops"; cur_loop = None; continue
            cur_section = None
            if k == "sources":
                manifest["artifacts"][cur_art]["sources"] = _parse_inline_list(v.strip())
            elif k == "confidence":
                manifest["artifacts"][cur_art]["confidence"] = float(v.strip())
            else:
                manifest["artifacts"][cur_art][k] = _parse_scalar(v.strip())
        elif indent == 6 and cur_section == "placeholders" and line.startswith("- item:"):
            cur_ph = {"item": _parse_scalar(line.split(":", 1)[1].strip())}
            manifest["artifacts"][cur_art]["placeholders"].append(cur_ph)
        elif indent == 6 and cur_section == "loops" and line.endswith(":"):
            cur_loop = line[:-1].strip()
            manifest["artifacts"][cur_art]["loops"][cur_loop] = {"verdict": "", "note": ""}
        elif indent == 8 and cur_section == "placeholders" and cur_ph is not None:
            k, _, v = line.partition(":")
            cur_ph[k.strip()] = _parse_scalar(v.strip())
        elif indent == 8 and cur_section == "loops" and cur_loop is not None:
            k, _, v = line.partition(":")
            manifest["artifacts"][cur_art]["loops"][cur_loop][k.strip()] = _parse_scalar(v.strip())
    return manifest
```

- [ ] **Step 4: Regenerate `templates/manifest.yaml`** so the seed template carries the new schema.

Run (from the repo root, writes the canonical seed):

```bash
cd ~/.claude/skills/ps-npi-forge
python3 -c "import sys; sys.path.insert(0,'scripts'); import manifest as m; open('templates/manifest.yaml','w').write(m.dumps(m.new_effort('<release>','<product-slug>','<parent-sku>')))"
```

- [ ] **Step 5: Run the suite to verify all PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `22/22 checks passed`, exit 0 (20 prior + R-MANIFEST-07 + R-MANIFEST-08; R-MANIFEST-05 still parses the old sample fixture — `load` tolerates absent loops).

- [ ] **Step 6: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add scripts/manifest.py tests/validate_skill.py templates/manifest.yaml
git commit -m "feat(manifest): add loop verdicts + last_generated, section-aware YAML round-trip"
```

---

### Task 2: render.py — token fill + unfilled reporting (subsumes B6)

**Files:**
- Create: `scripts/render.py`
- Modify: `tests/validate_skill.py` (add R-RENDER-01)

**Interfaces:**
- Consumes: nothing (pure stdlib).
- Produces: `render(template_text: str, fills: dict) -> (artifact_md: str, unfilled: list[str])`. Substitutes only `{{UPPER_SNAKE}}` tokens present in `fills`; unknown/omitted tokens are left literal and reported once each (order-preserving, de-duplicated). `render` is the authoritative fill-set for a template.

- [ ] **Step 1: Write the failing test** — append before `# ---- runner`:

```python
# ---- R-RENDER-01: token fill + unfilled reporting -----------------------
@check("R-RENDER-01: render fills known tokens, reports unfilled, and a complete fill leaves no surviving {{TOKEN}}")
def t_render():
    r = _load_script("scripts/render.py", "render_mod")
    tmpl = "# {{PRODUCT_NAME}}\n{{VISION}} and {{VISION}}\n{{SOURCES}}\n"
    out, unfilled = r.render(tmpl, {"PRODUCT_NAME": "Agentforce for Healthcare", "VISION": "win healthcare"})
    assert "Agentforce for Healthcare" in out and "win healthcare" in out
    assert unfilled == ["SOURCES"], f"expected ['SOURCES'], got {unfilled}"
    assert "{{SOURCES}}" in out, "unfilled token must stay literal"
    # complete fill across every token in every shipped template leaves nothing behind
    import re as _re, os as _os
    tdir = _os.path.join(SKILL, "templates")
    survivor = []
    for f in _os.listdir(tdir):
        if not f.endswith(".md"):
            continue
        body = read(f"templates/{f}")
        toks = set(_re.findall(r"\{\{([A-Z0-9_]+)\}\}", body))
        rendered, left = r.render(body, {t: "X" for t in toks})
        if "{{" in rendered or left:
            survivor.append((f, left))
    assert not survivor, f"complete fill left tokens behind: {survivor}"
```

- [ ] **Step 2: Run to verify it FAILS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on R-RENDER-01 (`scripts/render.py` not found).

- [ ] **Step 3: Create `scripts/render.py`**

```python
#!/usr/bin/env python3
"""
Template renderer for ps-npi-forge. Stdlib-only, side-effect-free.

Fills {{UPPER_SNAKE}} tokens in a Phase-3a artifact template from a `fills` dict and reports any
token left unfilled. This module is the authoritative fill-set for a template: the validation suite
asserts that a complete fill leaves no surviving {{TOKEN}}.
"""
import re

TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

def render(template_text, fills):
    unfilled = []
    def repl(m):
        key = m.group(1)
        if key in fills:
            return str(fills[key])
        if key not in unfilled:
            unfilled.append(key)
        return m.group(0)  # leave the token literal so the gap is visible + scannable
    out = TOKEN_RE.sub(repl, template_text)
    return out, unfilled
```

- [ ] **Step 4: Run to verify PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `23/23 checks passed`, exit 0.

- [ ] **Step 5: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add scripts/render.py tests/validate_skill.py
git commit -m "feat(render): token-fill renderer with unfilled reporting (subsumes B6)"
```

---

### Task 3: sections.py — H2 split + per-section lock diff

**Files:**
- Create: `scripts/sections.py`
- Modify: `tests/validate_skill.py` (add R-SECT-01)

**Interfaces:**
- Consumes: nothing.
- Produces: `split(md: str) -> dict[str, str]` (H2 heading text → body string, excluding the pre-first-H2 preamble and the post-`---` footer); `locked_sections(live_md: str, baseline_md: str) -> set[str]` (headings whose live body diverged from baseline, plus headings only in live).

- [ ] **Step 1: Write the failing test** — append before `# ---- runner`:

```python
# ---- R-SECT-01: H2 split + per-section lock diff ------------------------
@check("R-SECT-01: split keys by H2; locked_sections flags exactly the human-edited section")
def t_sections():
    s = _load_script("scripts/sections.py", "sections_mod")
    base = ("<!-- VOICE -->\n# Title\n> banner\n\n"
            "## Licenses\nbase licenses\n\n## Features\nbase features\n\n"
            "---\n**Sources:** x\n")
    secs = s.split(base)
    assert set(secs.keys()) == {"Licenses", "Features"}, f"unexpected sections: {set(secs.keys())}"
    assert "base licenses" in secs["Licenses"]
    # human edits the Features body only
    live = base.replace("base features", "HUMAN-EDITED features")
    assert s.locked_sections(live, base) == {"Features"}, "only the edited section should lock"
    # identical files lock nothing
    assert s.locked_sections(base, base) == set(), "no edits -> no locks"
    # a human-added section locks too
    live2 = base.replace("## Features", "## Storage\nadded\n\n## Features")
    assert "Storage" in s.locked_sections(live2, base), "human-added section should lock"
```

- [ ] **Step 2: Run to verify it FAILS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on R-SECT-01 (`scripts/sections.py` not found).

- [ ] **Step 3: Create `scripts/sections.py`**

```python
#!/usr/bin/env python3
"""
Section addressing + edit-preservation diff for ps-npi-forge. Stdlib-only, side-effect-free.

One section = one '## H2' block of an artifact (the Phase-3a templates make this exact). The H1 +
gap-banner before the first '## ' and the footer from the standalone '---' rule onward are
tool-owned and excluded from section addressing. `locked_sections` is the heart of per-section
edit-preservation: any H2 body that diverged from its last-generated baseline is human-locked and
must be carried over verbatim on regeneration.
"""
import re

H2_RE = re.compile(r"^## (.+?)\s*$")

def split(md):
    sections = {}
    cur = None
    buf = []
    for line in md.splitlines():
        if line.strip() == "---":          # footer rule: tool-owned, stop here
            break
        m = H2_RE.match(line)
        if m:
            if cur is not None:
                sections[cur] = "\n".join(buf)
            cur = m.group(1).strip()
            buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        sections[cur] = "\n".join(buf)
    return sections

def locked_sections(live_md, baseline_md):
    live = split(live_md)
    base = split(baseline_md)
    locked = set()
    for heading, body in live.items():
        if heading not in base or body.strip() != base[heading].strip():
            locked.add(heading)
    return locked
```

- [ ] **Step 4: Run to verify PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `24/24 checks passed`, exit 0.

- [ ] **Step 5: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add scripts/sections.py tests/validate_skill.py
git commit -m "feat(sections): H2 split + per-section lock diff for edit-preservation"
```

---

### Task 4: scan.py — uncertainty / gap scan

**Files:**
- Create: `scripts/scan.py`
- Modify: `tests/validate_skill.py` (add R-SCAN-01)

**Interfaces:**
- Consumes: nothing.
- Produces: `scan(md: str) -> list[dict]` where each dict is `{"item": "<label>: <match>"}`. Detects the canonical gap types: PENDING / TBD markers, `$xx`-style price stubs, surviving literal `{{TOKEN}}`, and a missing Template ID (a "Template ID" line carrying PENDING/TBD/missing/not provided). Owner + next_step are filled by the agent and written to the manifest — `scan` reports items only. A clean artifact returns `[]`.

- [ ] **Step 1: Write the failing test** — append before `# ---- runner`:

```python
# ---- R-SCAN-01: uncertainty / gap scan ----------------------------------
@check("R-SCAN-01: scan catches each canonical gap type and a clean artifact scans empty")
def t_scan():
    sc = _load_script("scripts/scan.py", "scan_mod")
    md = ("## Template ID\nPENDING -- not yet provided\n"
          "## Pricing\nlist price $xx; discount TBD\n"
          "## Composition\n{{ENTITLEMENT_COMPOSITION}}\n")
    items = [g["item"] for g in sc.scan(md)]
    joined = " | ".join(items)
    assert "Template ID" in joined, "missing-Template-ID gap not caught"
    assert any("PENDING" in i for i in items), "PENDING marker not caught"
    assert any("TBD" in i for i in items), "TBD marker not caught"
    assert any("price" in i.lower() for i in items), "price stub not caught"
    assert any("token" in i.lower() for i in items), "surviving token not caught"
    assert sc.scan("## All set\nfully grounded prose with no gaps.\n") == [], "clean artifact must scan empty"
```

- [ ] **Step 2: Run to verify it FAILS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on R-SCAN-01 (`scripts/scan.py` not found).

- [ ] **Step 3: Create `scripts/scan.py`**

```python
#!/usr/bin/env python3
"""
Uncertainty / gap scanner for ps-npi-forge. Stdlib-only, side-effect-free.

Implements the mechanical half of the uncertainty-surfacing loop: find every place a rendered
artifact admits an unknown so the agent can attach an owner + next step and the manifest can carry
it. Never silently drops an uncertainty -- the scanner's whole job is to make gaps loud.
"""
import re

_PATTERNS = [
    (re.compile(r"Template ID[^\n]*\b(?:PENDING|TBD|missing|not provided)\b", re.I), "missing Template ID"),
    (re.compile(r"\bPENDING\b", re.I), "PENDING marker"),
    (re.compile(r"\bTBD\b", re.I), "TBD marker"),
    (re.compile(r"\$[xX]{2,}\b"), "price stub"),
    (re.compile(r"\{\{[A-Z0-9_]+\}\}"), "unfilled token"),
]

def scan(md):
    gaps = []
    seen = set()
    for rx, label in _PATTERNS:
        for m in rx.finditer(md):
            key = (label, m.group(0))
            if key in seen:
                continue
            seen.add(key)
            gaps.append({"item": f"{label}: {m.group(0).strip()}"})
    return gaps
```

- [ ] **Step 4: Run to verify PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `25/25 checks passed`, exit 0. (The "missing Template ID" line also matches the PENDING pattern; both are distinct `(label, match)` keys, so the scan reports the specific gap and the generic marker — acceptable and the test only asserts presence.)

- [ ] **Step 5: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add scripts/scan.py tests/validate_skill.py
git commit -m "feat(scan): uncertainty/gap scanner for the surfacing loop"
```

---

### Task 5: org62.py + sanitized fixture + entitlements ref (closes B1)

**Files:**
- Create: `scripts/org62.py`
- Create: `tests/fixtures/org62/parent-entitlements.json`
- Create: `refs/org62-entitlements.md`
- Modify: `tests/validate_skill.py` (add R-ENT-01, R-ORG62-01; add ref to `EXPECTED_REFS`)
- Modify: `SKILL.md` (reference the new ref)

**Interfaces:**
- Consumes: nothing (pure parser; never invokes `sf`).
- Produces: `parse_entitlements(sf_json: dict) -> dict` with keys `product`, `product_code`, `licenses` (list), `psls` (list), `features` (list), `storage`. Missing child collections degrade to empty lists; an empty result set returns a `_warning`.

- [ ] **Step 1: Create the sanitized fixture** `tests/fixtures/org62/parent-entitlements.json`

This is the captured-and-scrubbed shape of a parent-SKU pull — the parser's contract. IDs and counts are redacted/zeroed; relationship names mirror the `sf data query --json` envelope.

```json
{
  "status": 0,
  "result": {
    "totalSize": 1,
    "done": true,
    "records": [
      {
        "attributes": {"type": "Product2"},
        "Id": "01tXXXXXXXXXXXXXXX",
        "Name": "Health Cloud",
        "ProductCode": "HEALTH_CLOUD_EE_UE",
        "Licenses__r": {
          "records": [
            {"Name": "Health Cloud"},
            {"Name": "Health Cloud for Provider"}
          ]
        },
        "PermissionSetLicenses__r": {
          "records": [
            {"Name": "HealthCloudPsl"},
            {"Name": "CareePlanPsl"}
          ]
        },
        "Features__r": {
          "records": [
            {"Name": "HealthCloudGA"},
            {"Name": "HealthCloudIndustriesAddOn"}
          ]
        },
        "Storage__c": "Standard data + file allocation (parent-derived; confirm per OEM packaging)"
      }
    ]
  }
}
```

- [ ] **Step 2: Write the failing tests** — append before `# ---- runner`. Add `refs/org62-entitlements.md` to `EXPECTED_REFS` (the list near R-ARCH-03).

In `EXPECTED_REFS`, add the entry:

```python
    "refs/org62-entitlements.md",
```

Append the checks:

```python
# ---- R-ENT-01: Org62 entitlement parser ---------------------------------
@check("R-ENT-01: parse_entitlements maps the sanitized fixture to licenses/PSLs/features/storage")
def t_org62_parse():
    o = _load_script("scripts/org62.py", "org62_mod")
    import json
    with open(os.path.join(SKILL, "tests/fixtures/org62/parent-entitlements.json"), encoding="utf-8") as f:
        payload = o.parse_entitlements(json.load(f))
    assert payload["product"] == "Health Cloud", payload
    assert "Health Cloud" in payload["licenses"]
    assert "HealthCloudPsl" in payload["psls"]
    assert "HealthCloudGA" in payload["features"]
    assert payload["storage"], "storage should be carried through"
    # empty result set degrades gracefully, never raises
    empty = o.parse_entitlements({"result": {"records": []}})
    assert empty["licenses"] == [] and empty["psls"] == [] and empty.get("_warning"), empty

# ---- R-ORG62-01: entitlements ref pins the query spine ------------------
@check("R-ORG62-01: org62-entitlements ref exists, is referenced by SKILL.md, and pins the read-only query spine + human-confirm")
def t_org62_ref():
    path = "refs/org62-entitlements.md"
    assert exists(path), f"missing {path}"
    body = read(path).lower()
    for needle in ["product2", "productentitlements", "sf data query", "--json",
                   "org62", "read-only", "naming difference", "delta", "human"]:
        assert needle in body, f"org62 ref missing: {needle}"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"
```

- [ ] **Step 3: Run to verify it FAILS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on R-ENT-01 (`scripts/org62.py` not found), R-ORG62-01 (ref missing), R-ARCH-03 (expected ref missing).

- [ ] **Step 4: Create `scripts/org62.py`**

```python
#!/usr/bin/env python3
"""
Org62 entitlement parser for ps-npi-forge. Stdlib-only, side-effect-free.

Parses the JSON produced by `sf data query ... --json` against the parent Product2 + its entitlement
composition into the #06 payload (licenses, PSLs, features, storage). This module NEVER invokes `sf`
or the network -- the live pull is a capability-gated manual step documented in
refs/org62-entitlements.md; this parser consumes its already-captured output so it stays testable.
The skill drafts and flags entitlements; a human always confirms (refusal rule).
"""

def parse_entitlements(sf_json):
    res = sf_json.get("result", sf_json) if isinstance(sf_json, dict) else {}
    records = (res or {}).get("records") or []
    if not records:
        return {"product": None, "product_code": None, "licenses": [], "psls": [],
                "features": [], "storage": None,
                "_warning": "no Product2 record in query result -- fall back to paste/knowledge, flag the gap"}
    rec = records[0]
    def names(child):
        node = rec.get(child) or {}
        return [r.get("Name") for r in (node.get("records") or []) if r.get("Name")]
    return {
        "product": rec.get("Name"),
        "product_code": rec.get("ProductCode"),
        "licenses": names("Licenses__r"),
        "psls": names("PermissionSetLicenses__r"),
        "features": names("Features__r"),
        "storage": rec.get("Storage__c"),
    }
```

- [ ] **Step 5: Create `refs/org62-entitlements.md`**

```markdown
# Org62 entitlement intake (parent-SKU modeling)

Feeds artifact **#06 license & entitlement details** (and, via #06, **#07 add-on tiering**). The
skill reads Org62 **read-only** through the `sf` CLI against the `org62` alias (env `ORG62_ALIAS`,
default `org62`) using the logged-in session identity -- the same pattern as the `team-projects`
skill. It **never writes** to Org62.

## The query spine

Given the parent direct SKU, resolve its `Product2` and pull its entitlement composition. The
extraction runs as a `sf data query ... --json` call; `scripts/org62.py` parses the captured JSON
into the #06 payload (licenses, PSLs, features, storage). Example shape (confirm field/relationship
names against live Org62 -- the committed fixture `tests/fixtures/org62/parent-entitlements.json`
is the current captured contract):

```bash
sf data query --target-org "$ORG62_ALIAS" --json --query "
  SELECT Id, Name, ProductCode,
         (SELECT Name FROM Licenses__r),
         (SELECT Name FROM PermissionSetLicenses__r),
         (SELECT Name FROM Features__r),
         Storage__c
  FROM Product2 WHERE Id = '<parent pId>'"
```

The internal **productEntitlements** view is the authority for the parent's composition; where its
exact object/relationship names differ from the example above, capture a fresh `--json` pull, scrub
it, and refresh the fixture -- the parser keys off `result.records[0]` and the `*__r.records[].Name`
child collections, degrading to empty lists when a collection is absent.

## Graceful degradation

If no org is reachable (no auth, headless CI, offline), **#06 is not blocked**: it falls back to
paste + model knowledge at lower confidence and the missing pull is surfaced as a flagged gap
(owner + next step) in the manifest. A live pull is a **capability-gated manual step**, never a
hard dependency.

## Parent-SKU modeling (draft + flag; human confirms)

From the parent composition the skill:

1. Pulls the parent's entitlement composition (licenses, PSLs, features, storage).
2. Proposes the Embedded/OEM equivalent, **flagging naming differences** (e.g. "Health Cloud" ->
   "Agentforce for Healthcare") and **deltas** (OEM vs. direct).
3. Applies partner-motion rules (OEM-only, shared-org restrictions) as a validation pass.
4. Derives the minimalist Required/Recommended/Optional add-on tiers for #07.

The skill **drafts and flags** every entitlement; it never silently asserts one. A human always
confirms before #06 reaches `verified`. **Pricing is out of scope** -- #07 surfaces which SKUs/add-ons
exist and tiers them; price/discount cells stay as marked placeholders.
```

- [ ] **Step 6: Wire the ref into SKILL.md** — add after the "Artifacts:" line (currently line 33-34):

```markdown
**Entitlements:** #06/#07 model the parent SKU's composition from Org62 (read-only) per
[refs/org62-entitlements.md](refs/org62-entitlements.md); the skill drafts and flags, a human confirms.
```

- [ ] **Step 7: Run to verify PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `27/27 checks passed`, exit 0 (R-ENT-01, R-ORG62-01 added; R-ARCH-03/04 satisfied).

- [ ] **Step 8: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add scripts/org62.py tests/fixtures/org62/parent-entitlements.json refs/org62-entitlements.md SKILL.md tests/validate_skill.py
git commit -m "feat(org62): entitlement parser + sanitized fixture + query-spine ref (closes B1)"
```

---

### Task 6: refs/quality-loops.md — the cycle + four loops + SKILL.md cycle section

**Files:**
- Create: `refs/quality-loops.md`
- Modify: `tests/validate_skill.py` (add R-LOOPS-01; add ref to `EXPECTED_REFS`)
- Modify: `SKILL.md` (expand the generate→refine→validate section; reference the ref)

**Interfaces:**
- Consumes: the scripts from Tasks 2–5 (named in the prose so the agent knows what to call).
- Produces: `refs/quality-loops.md` (judgment prose) wired into SKILL.md and `EXPECTED_REFS`.

- [ ] **Step 1: Write the failing test** — append before `# ---- runner`; add `refs/quality-loops.md` to `EXPECTED_REFS`.

In `EXPECTED_REFS`, add:

```python
    "refs/quality-loops.md",
```

Append the check:

```python
# ---- R-LOOPS-01: quality-loops ref documents the cycle + four loops -----
@check("R-LOOPS-01: quality-loops ref exists, is referenced by SKILL.md, and documents the 3-pass cycle, 4 loops, POV exception, and the scripts it drives")
def t_loops_ref():
    path = "refs/quality-loops.md"
    assert exists(path), f"missing {path}"
    body = read(path).lower()
    for phase in ["draft", "refine", "validate"]:
        assert phase in body, f"cycle phase missing: {phase}"
    for loop in ["claim verification", "completeness", "uncertainty", "partner-lens"]:
        assert loop in body, f"loop missing: {loop}"
    # POV/opinion exception: strict on fact, lenient on POV
    assert "pov" in body and ("lenient" in body or "internal logic" in body), \
        "loops ref must state the POV/opinion exception"
    # names the mechanical scripts it drives
    for script in ["render.py", "sections.py", "scan.py", "org62.py", "manifest.py"]:
        assert script in body, f"loops ref should name the script it drives: {script}"
    # writes verdicts back to the manifest
    assert "verdict" in body and "manifest" in body, "loops ref must say verdicts are written to the manifest"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"
```

- [ ] **Step 2: Run to verify it FAILS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on R-LOOPS-01 and R-ARCH-03 (expected ref missing).

- [ ] **Step 3: Create `refs/quality-loops.md`**

```markdown
# The generate -> refine -> validate cycle & four quality loops

Every artifact is produced by three passes: **start with what you know, refine against sources,
validate**. The mechanical work runs through the `scripts/` library; the judgment is yours, written
in the first-person exec/architect McKinsey voice (see [voice-and-style.md](voice-and-style.md)).
Confidence and gap state live in the effort `manifest.yaml` (via `scripts/manifest.py`).

## The three passes

1. **Draft.** Produce a substantive v1 from model knowledge. Build the `{{TOKEN}}` fills dict and
   call `scripts/render.py` `render(template_text, fills)` to fill the artifact template. Set the
   artifact's status to `drafted` and a modest confidence with a one-line rationale. Never block on
   missing inputs -- a drafted artifact with flagged gaps beats a blank one.
2. **Refine.** Fold provided sources into the fills: pasted FCD/Quip text (#01-05), the Org62
   entitlement payload from `scripts/org62.py` (#06/#07; see
   [org62-entitlements.md](org62-entitlements.md)), fetched **official** docs (#08/#10), Slack
   context. Tie each claim to a source recorded in the artifact's `sources`. Re-render **only the
   sections you own**: call `scripts/sections.py` `locked_sections(live_md, baseline_md)` against the
   `last_generated` baseline; any human-edited `## H2` section is carried over **verbatim**, only
   model-owned sections regenerate. Write a fresh baseline after every (re)generation. Confidence
   rises as sources land.
3. **Validate.** Run the four loops below, then `scripts/scan.py` `scan(rendered_md)` to catch every
   surviving uncertainty. Each unresolved item becomes a manifest placeholder with an **owner + next
   step** and lowers confidence. Record each loop's outcome with `manifest.set_loop_verdict(...)`
   (verdict `pass` / `flag` / `fail` + note). An artifact reaches `verified` only when the loops pass
   and a human confirms.

## The four loops (one per failure mode)

| Loop | Question it answers | How to run it (Standard mode) |
|------|--------------------|-------------------------------|
| **Claim verification** | Is every factual/positioning claim traceable to a source? Does anything contradict the FCD? | One pass: walk the claims, confirm each maps to a `sources` entry; flag the ungrounded. |
| **Completeness** | Are all canonical sections present and non-empty? Audience-appropriate (PAM / NPI / less-technical)? | Diff the rendered artifact against its template grammar; flag empty personas/rows/sections. |
| **Uncertainty surfacing** | Is every PENDING / TBD / `$xx` / missing Template ID / unfilled token flagged with an owner + next step? | Run `scan.py`; for each gap, attach owner + next step and write it to the manifest placeholders. |
| **Partner-lens rules** | OEM/VAR correct? Shared-org restrictions honored? Packageability timing right? Official-docs-only respected (#08)? | Walk the partner-motion checklist; flag any violation. |

## The POV / opinion exception (important)

Claim verification is **strict for technical and positioning claims** but **lenient for POV / vision**
content (#10 partner-profile POV, and the vision parts of #00). A POV is Brandon's reasoned argument,
not a sourced fact: the loop checks **internal logic and clearly-marked assumptions**, not citations,
so it never strips the judgment the skill exists to express. Do not flag a well-reasoned, clearly
labeled POV as "ungrounded."

## Confidence & the gap banner

Drivers that **lower** confidence: unresolved placeholders, claims not grounded in a provided source,
official-docs-only violations in #08, unverified Tier-C research in #10. The effort's overall
confidence is the **weighted floor** across artifacts (`manifest.overall_confidence`) -- a single
shaky artifact stays visible, never averaged away. Every artifact opens with its gap banner; #00
aggregates all open gaps into the Next Steps & Blockers register. **A gap is never silent** -- always
owner + next step.
```

- [ ] **Step 4: Expand the cycle section in SKILL.md** — replace the Phase-1 note blockquote (currently lines 28-29) and tie in the ref. Replace:

```markdown
> Phase 1 implements the scaffold, the manifest model, and the validation harness only. Artifact
> generation, intake, canvas, and Slack sync arrive in later phases (see BACKLOG.md).
```

with:

```markdown
Each artifact runs the three-pass **generate → refine → validate** cycle with four quality loops
(claim verification, completeness, uncertainty surfacing, partner-lens rules); per-section
edit-preservation carries human edits over verbatim on regeneration. See
[refs/quality-loops.md](refs/quality-loops.md). The mechanical steps run through `scripts/`
(render, section-diff, scan, Org62 parse, manifest); the judgment is the agent's.

> Canvas HTML/Mermaid render (Phase 5), live web/Slack sync (Phase 6), and Deep Build C-mode
> (Phase 7) are not yet implemented (see BACKLOG.md).
```

- [ ] **Step 5: Run to verify PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `28/28 checks passed`, exit 0.

- [ ] **Step 6: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add refs/quality-loops.md SKILL.md tests/validate_skill.py
git commit -m "feat(loops): quality-loops ref (cycle + 4 loops + POV exception); SKILL.md cycle section"
```

---

### Task 7: Validation hardening — fold in B7 (R-TPL-02 structure) + B8 (R-TPL-01 scope)

**Files:**
- Modify: `tests/validate_skill.py`

**Interfaces:**
- Consumes: `ARTIFACT_REGISTRY`, `read`, `exists`.
- Produces: a structurally stricter R-TPL-02 (asserts the literal gap-banner blockquote + footer block, not just token presence) and a tightened R-TPL-01 (drops the dead `manifest` whitelist entry; `.md` filter already excludes `manifest.yaml`).

- [ ] **Step 1: Tighten R-TPL-02 (B7)** — replace the body of `t_template_shared_convention` (currently lines 285-295) with a structure check:

```python
@check("R-TPL-02: every artifact template carries the literal gap-banner header block and sources/confidence footer block")
def t_template_shared_convention():
    header_line = "> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}"
    gap_line = "> {{GAP_BANNER}}"
    footer = "---\n**Sources:** {{SOURCES}}\n**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}"
    bad = []
    for s in ARTIFACT_REGISTRY:
        body = read(f"templates/{s}.md")
        if header_line not in body:
            bad.append(f"templates/{s}.md missing the literal gap-banner status line")
        if gap_line not in body:
            bad.append(f"templates/{s}.md missing the '> {{{{GAP_BANNER}}}}' blockquote line")
        if footer not in body:
            bad.append(f"templates/{s}.md missing the literal sources/confidence footer block")
        if "VOICE:" not in body:
            bad.append(f"templates/{s}.md missing VOICE register comment")
    assert not bad, f"shared-convention violations: {bad}"
```

- [ ] **Step 2: Tighten R-TPL-01 (B8)** — in `t_template_registry_parity` (line 274), replace:

```python
    known = set(ARTIFACT_REGISTRY) | {"manifest"}  # manifest.yaml is infra, not an artifact
```

with:

```python
    known = set(ARTIFACT_REGISTRY)  # manifest.yaml is .yaml, excluded by the .md filter below
```

- [ ] **Step 3: Run to verify PASS** (the Phase-3a templates already conform to the literal blockquote/footer shape)

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `28/28 checks passed`, exit 0.

- [ ] **Step 4: Prove the tightened checks can fail (sanity-gate)**

```bash
cd ~/.claude/skills/ps-npi-forge
# (a) break the footer in one template -> R-TPL-02 fails
cp templates/01-brief.md /tmp/01-brief.bak
python3 - <<'PY'
p="templates/01-brief.md"; open(p,"w").write(open(p).read().replace("**Sources:** {{SOURCES}}","**Srcs:** {{SOURCES}}"))
PY
python3 tests/validate_skill.py | grep -E "R-TPL-02|checks passed"
cp /tmp/01-brief.bak templates/01-brief.md
# (b) an orphan .md slug -> R-TPL-01 still fails (regression guard for B8)
touch templates/99-bogus.md
python3 tests/validate_skill.py | grep -E "R-TPL-01|checks passed"
rm templates/99-bogus.md
python3 tests/validate_skill.py | tail -1
```
Expected: (a) a FAIL line for R-TPL-02 naming `01-brief.md`; (b) a FAIL line for R-TPL-01 naming `99-bogus.md`; final line `28/28 checks passed` after both restores.

- [ ] **Step 5: Confirm clean tree, then commit**

Run: `cd ~/.claude/skills/ps-npi-forge && git status --porcelain` — expect only `tests/validate_skill.py` modified (no `99-bogus.md`, `01-brief.md` restored).

```bash
cd ~/.claude/skills/ps-npi-forge
git add tests/validate_skill.py
git commit -m "test: tighten R-TPL-02 to structure (B7) and scope R-TPL-01 to .md slugs (B8)"
```

---

### Task 8: Dogfood acceptance — paste-driven end-to-end run on the Healthcare brief

This task is **manual + agent-driven**, not a unit test. The controller (not a subagent) drives it with Brandon's pasted brief; its mechanical sub-steps are already CI-covered by Tasks 1–7. The deliverable is a committed acceptance record.

**Files:**
- Create: `docs/superpowers/acceptance/2026-06-23-healthcare-dogfood.md`
- Modify: `BACKLOG.md` (mark Phase 3b complete; close B1/B6/B7/B8)

- [ ] **Step 1: Set up the effort folder** (outside the repo)

```bash
mkdir -p /Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/{sources,artifacts/.baseline,canvas}
cd ~/.claude/skills/ps-npi-forge
python3 -c "import sys; sys.path.insert(0,'scripts'); import manifest as m; open('/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/manifest.yaml','w').write(m.dumps(m.new_effort('summer-26','agentforce-healthcare-oem','Health Cloud EE/UE')))"
```

- [ ] **Step 2: Run the cycle for the 11 artifacts** using the pasted Agentforce-for-Healthcare brief as the paste source and (if an org is reachable) a live Org62 pull for #06/#07, else the flagged-gap fallback. For each artifact: draft via `render.py`, refine folding the paste/Org62, run the four loops + `scan.py`, write verdicts + placeholders + confidence to the manifest, and write a baseline. Save artifacts under the effort's `artifacts/`.

- [ ] **Step 3: Assert the golden signals** (the brief's natural gap is the missing Template ID):
  - #09 org-provisioning-validation shows a flagged gap: "live org test cannot run — Template ID pending; owner: …".
  - #00 executive-summary's Next Steps & Blockers register aggregates that gap.
  - `manifest.overall_confidence` is the weighted floor (the Template-ID gap holds #09 — and the rollup — visibly below the verified artifacts).
  - Each artifact carries four loop verdicts in the manifest; no uncertainty is silent.

- [ ] **Step 4: Write the acceptance record** `docs/superpowers/acceptance/2026-06-23-healthcare-dogfood.md` capturing: which channels were live (paste; Org62 live vs. fallback), the per-artifact status/confidence table, the Template-ID gap trace through #09 → #00, and any rough edges found (feed into BACKLOG).

- [ ] **Step 5: Update BACKLOG.md** — under the roadmap mark `- [x] Phase 3b — generate→refine→validate cycle + quality loops`; append resolution notes to **B1** (query spine pinned + fixture contract; live re-confirm is the gated manual step), **B6** (closed by R-RENDER-01), **B7** (closed — R-TPL-02 now structural), **B8** (closed — R-TPL-01 scoped to `.md` slugs).

- [ ] **Step 6: Run the suite once more and commit**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `28/28 checks passed`, exit 0.

```bash
cd ~/.claude/skills/ps-npi-forge
git add docs/superpowers/acceptance/2026-06-23-healthcare-dogfood.md BACKLOG.md
git commit -m "docs: Phase 3b dogfood acceptance record; close B1/B6/B7/B8"
```

---

## Self-Review

**Spec coverage (Phase 3b scope):**
- Three-pass cycle (spec §5) → `refs/quality-loops.md` (Task 6) + `render.py`/`sections.py`/`scan.py` (Tasks 2–4). ✅
- Four quality loops + POV exception (spec §5) → quality-loops ref + R-LOOPS-01 (Task 6). ✅
- Per-section edit-preservation (spec §2.2, §4) → `sections.py.locked_sections` + R-SECT-01 (Task 3); baseline written each (re)gen (Task 6 prose, Task 8 run). ✅
- Manifest growth: `loops` verdicts + `last_generated` (spec §3) → Task 1 + R-MANIFEST-07/08. ✅
- Live Org62 entitlement intake, pinned queries + sanitized fixture, capability-gated (spec §5 decision + §2.1) → `org62.py` + fixture + ref + R-ENT-01/R-ORG62-01 (Task 5); closes B1. ✅
- Validation additions (spec §6) → R-RENDER-01, R-SECT-01, R-SCAN-01, R-ENT-01, R-MANIFEST-07/08, R-LOOPS-01, R-ORG62-01 (9 new). ✅
- B6/B7/B8 folded in (spec §6) → render parity = B6 (Task 2); R-TPL-02 structure = B7, R-TPL-01 scope = B8 (Task 7). ✅
- Dogfood acceptance, Template-ID gap as golden signal (spec §6) → Task 8. ✅
- **Deferred (correctly out of 3b):** canvas HTML/Mermaid (Phase 5), live web/Slack (Phase 6), Deep Build C-mode (Phase 7), pricing. No fetch/Slack/render code added; `org62.py` is a pure parser.

**Placeholder scan:** All scripts, refs, fixture, and checks are written in full. No TBD/TODO. The `{{TOKEN}}`s in template/ref bodies and the `<release>`/`<parent pId>` in shell/ref examples are intentional fill slots/example placeholders, not plan gaps. Task 8 is explicitly manual/agent-driven (no fabricated unit-test code for a non-deterministic step). The exact Org62 relationship names are honestly framed as "confirm live; fixture is the captured contract" — the parser keys off documented structure, not invented SOQL. ✅

**Type consistency:** `render(template_text, fills) -> (md, unfilled:list)`, `split(md)->dict`, `locked_sections(live,base)->set`, `scan(md)->list[{item}]`, `parse_entitlements(sf_json)->dict`, `set_loop_verdict(manifest,artifact,loop,verdict,note="")`, `set_last_generated(manifest,artifact,pointer)` — names/signatures identical across the tasks that define and consume them. `LOOP_REGISTRY`/`VERDICT_VOCAB` defined once per file and parity-checked (R-MANIFEST-06). Check-count arithmetic: 20 (Phase 3a) +2 (T1) +1 (T2) +1 (T3) +1 (T4) +2 (T5) +1 (T6) +0 (T7 tightens existing) = **28** at the end; the spec's "~26" was a hedge — 28 is the real number, noted here so reviewers expect it. ✅
