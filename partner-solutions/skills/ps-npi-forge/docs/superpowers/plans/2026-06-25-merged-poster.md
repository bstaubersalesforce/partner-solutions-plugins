# Merged Exec Poster Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate the two near-identical poster views into ONE merged 7-panel exec poster (keyed to #14) that draws its panels from BOTH the #14 and #11 markdown artifacts; remove #11's poster so its canvas card reverts to a plain document link.

**Architecture:** Poster-layer-only change. `poster.py`'s `SECTION_MAP` becomes a structured `{panel: (source_slug, h2)}` map and `render_poster` takes a `sources` dict (`{slug: md_text}`) so a poster can pull panels from multiple artifacts. The merged `exec-infographic-poster.html` carries the 7 locked panels; `solution-infographic-poster.html` is deleted along with #11's map entry. Both markdown artifacts and both *document* views stay; family stays 15; registry untouched.

**Tech Stack:** Python 3 stdlib only. Reuses `sections.split` + `md_to_html.md_to_html`. No new dependencies.

## Global Constraints

- **Stdlib-only.** No third-party imports in `scripts/` or `tests/`.
- **Poster-layer-only.** Do NOT touch `ARTIFACT_REGISTRY`, `templates/manifest.yaml`, the fixture, the markdown templates (`11-…md`, `14-…md`), or any "15 artifacts" count. Family stays 15. Both #11 and #14 keep their *document* views.
- **Locked panel set + order** (the merged poster, all 7): `PANEL_VISION` (from #14 "Vision") → `PANEL_PROBLEM` (#11 "The problem (why this matters)") → `PANEL_SOLUTION` (#11 "The solution (what we built on Salesforce)") → `PANEL_OUTCOMES` (#11 "Outcomes (the proof)") → `PANEL_TAM` (#14 "Market opportunity (TAM)") → `PANEL_IDEAL_PARTNERS` (#14 "Ideal partners") → `PANEL_BUILT_ON` (#11 "Built on Salesforce (the OEM/Embedded stack)"). These H2 strings are exact (verified against both templates).
- **Reuse converters** — `from sections import split`, `from md_to_html import md_to_html`. No second parser. Metadata stays HTML-escaped (prior increment's fix); panel fills are NOT re-escaped (already-converted HTML).
- **Keep the dark poster treatment** — do not re-theme; only the panel set/markup changes.
- **`solution-infographic-poster.html` must be DELETED** (not left as a stale copy).
- **Run the suite:** `python3 tests/validate_skill.py` (exit 0). Baseline is 49/49.
- **Branch:** `npi-merged-poster` (already created off `main`; spec committed at `cff34aa`).

---

### Task 1: Multi-source `poster.py` (structured map + sources signature)

**Files:**
- Modify: `scripts/poster.py` (`SECTION_MAP` shape, `render_poster` signature, add `SOURCES_FOR`, keep `PANELS_FOR`)
- Test: `tests/validate_skill.py` R-POSTER-02 (rewrite for the new signature)

**Interfaces:**
- Produces: `SECTION_MAP[slug]` = `{PANEL_TOKEN: (source_slug, "H2 heading")}`; `render_poster(slug, sources, template_text, meta)` where `sources` is `{source_slug: md_text}` → `(filled_html, unfilled_tokens)`; `PANELS_FOR(slug)` → set of panel tokens; `SOURCES_FOR(slug)` → set of distinct source slugs. Later tasks (template, canvas, dogfood) consume these.

- [ ] **Step 1: Replace `SECTION_MAP`, `render_poster`, and add `SOURCES_FOR` in `scripts/poster.py`.** Replace the existing `SECTION_MAP = {...}`, `PANELS_FOR`, and `render_poster` definitions with:

```python
# the section->panel contract. Each panel names its SOURCE artifact slug and the exact H2 heading
# in that source. The merged exec poster draws from BOTH #14 and #11. Keep this the single source of truth.
SECTION_MAP = {
    "14-exec-infographic": {
        "PANEL_VISION":         ("14-exec-infographic", "Vision"),
        "PANEL_PROBLEM":        ("11-solution-infographic", "The problem (why this matters)"),
        "PANEL_SOLUTION":       ("11-solution-infographic", "The solution (what we built on Salesforce)"),
        "PANEL_OUTCOMES":       ("11-solution-infographic", "Outcomes (the proof)"),
        "PANEL_TAM":            ("14-exec-infographic", "Market opportunity (TAM)"),
        "PANEL_IDEAL_PARTNERS": ("14-exec-infographic", "Ideal partners"),
        "PANEL_BUILT_ON":       ("11-solution-infographic", "Built on Salesforce (the OEM/Embedded stack)"),
    },
}

def PANELS_FOR(slug):
    return set(SECTION_MAP.get(slug, {}).keys())

def SOURCES_FOR(slug):
    return {src for (src, _h2) in SECTION_MAP.get(slug, {}).values()}

def render_poster(slug, sources, template_text, meta):
    """Return (filled_html, unfilled_tokens). `sources` is {source_slug: md_text} — every artifact this
    poster draws from. meta supplies TITLE/LABEL/RELEASE/GENERATED_DATE/HOME_HREF."""
    # metadata are plain scalars -> HTML-escape (matches md_to_html.py / canvas.py). Panel fills are NOT
    # re-escaped: md_to_html already produced escaped HTML.
    fills = {k: _html.escape(str(v)) for k, v in meta.items()}
    split_cache = {}
    for panel, (src, h2) in SECTION_MAP.get(slug, {}).items():
        if src not in sources:
            raise ValueError(f"{slug}: panel {panel} needs source '{src}' but it was not provided")
        if src not in split_cache:
            split_cache[src] = split(sources[src])
        secs = split_cache[src]
        if h2 not in secs:
            raise ValueError(f"{slug}: poster section '{h2}' not found in source '{src}'")
        fills[panel] = md_to_html(_body_after_h2(secs[h2]))
    unfilled = []
    def repl(m):
        k = m.group(1)
        if k in fills:
            return str(fills[k])
        if k not in unfilled:
            unfilled.append(k)
        return m.group(0)
    out = TOKEN_RE.sub(repl, template_text)
    return out, unfilled
```

Keep the existing `import html as _html`, `TOKEN_RE`, `_body_after_h2`, and the `from sections import split` / `from md_to_html import md_to_html` imports. Remove the old `"11-solution-infographic"` entry entirely (it's gone from the merged map above).

- [ ] **Step 2: Rewrite R-POSTER-02** in `tests/validate_skill.py` (the `t_poster_render` function, ~lines 808-876) for the new multi-source signature:

```python
# ---- R-POSTER-02: render_poster fills every panel from its source artifact; missing source/section raises -
@check("R-POSTER-02: merged poster fills all 7 panels from #14+#11 sources, no unfilled token; missing source/section raises; metadata escaped")
def t_poster_render():
    p = _load_script("scripts/poster.py", "poster_mod")
    tmpl = read("templates/exec-infographic-poster.html")
    md14 = """# Product — Executive Overview

## Vision
The vision is to transform the industry.

## Value proposition
We deliver value through innovation.

## Key use cases
- Use case one

## Ideal partners
Regional system integrators in healthcare.

## Market opportunity (TAM)
$50B market growing at 15% CAGR.
"""
    md11 = """# Product — Solution Infographic

## The one-line story
Revolutionizing healthcare data access.

## The problem (why this matters)
Fragmented patient data creates inefficiencies.

## The solution (what we built on Salesforce)
A unified Health Cloud platform.

## Outcomes (the proof)
- 40% reduction in coordination time

## Market & who it's for
Providers and payers in North America.

## Built on Salesforce (the OEM/Embedded stack)
Health Cloud + Agentforce + Data 360.
"""
    sources = {"14-exec-infographic": md14, "11-solution-infographic": md11}
    meta = {"TITLE":"X","LABEL":"Executive & Solution Overview","RELEASE":"r","GENERATED_DATE":"d","HOME_HREF":"index.html"}
    out, unfilled = p.render_poster("14-exec-infographic", sources, tmpl, meta)
    assert unfilled == [], f"unfilled poster tokens: {unfilled}"
    assert "{{" not in out, "no raw token may survive a complete poster fill"
    for tok in p.PANELS_FOR("14-exec-infographic"):
        assert "{{"+tok+"}}" not in out, f"{tok} not filled"
    # SOURCES_FOR reports both source artifacts
    assert p.SOURCES_FOR("14-exec-infographic") == {"14-exec-infographic", "11-solution-infographic"}, \
        "merged poster must declare both sources"
    # a missing section in a source raises (contract guard)
    broken = {**sources, "11-solution-infographic": md11.replace("## Outcomes (the proof)", "## Outcomesss")}
    try:
        p.render_poster("14-exec-infographic", broken, tmpl, meta)
        assert False, "missing mapped section must raise"
    except ValueError:
        pass
    # a missing SOURCE entirely raises
    try:
        p.render_poster("14-exec-infographic", {"14-exec-infographic": md14}, tmpl, meta)
        assert False, "missing source artifact must raise"
    except ValueError:
        pass
    # metadata HTML-escaped (matches md_to_html / canvas)
    out_esc, _ = p.render_poster("14-exec-infographic", sources, tmpl, {**meta, "TITLE": "Acme <Health> & Co"})
    assert "Acme &lt;Health&gt; &amp; Co" in out_esc, "metadata TITLE must be HTML-escaped"
    assert "Acme <Health>" not in out_esc, "raw HTML-special TITLE must not reach the markup"
```

- [ ] **Step 3: Run R-POSTER-02 — expect FAIL.** It will fail because the merged template (Task 2) doesn't exist yet with the 7 panels.

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-POSTER-02"`
Expected: FAIL (template still has the old 5 exec-only panels / `PANEL_VALUE_PROP` etc.; `PANEL_PROBLEM` won't be in it). This drives Task 2.

- [ ] **Step 4: Commit** (engine first; template follows in Task 2 — suite not yet green, so use `--no-verify` to bypass the pre-commit hook for this intermediate commit):

```bash
git add scripts/poster.py tests/validate_skill.py
git commit --no-verify -m "feat(poster): multi-source render_poster + structured SECTION_MAP (engine)"
```

---

### Task 2: The merged 7-panel template

**Files:**
- Modify: `templates/exec-infographic-poster.html` (replace the 5 exec panels with the 7 merged panels, locked order; keep the dark treatment)

**Interfaces:**
- Consumes: the 7 panel tokens from Task 1's `SECTION_MAP["14-exec-infographic"]`.

- [ ] **Step 1: Replace the `.grid` panel block** in `templates/exec-infographic-poster.html`. Keep the entire `<style>` (dark treatment) and header band as-is; replace only the `<div class="grid">…</div>` section with the 7 merged panels in locked order:

```html
 <div class="grid">
   <section class="panel c3"><div class="label">Vision</div><div class="body">{{PANEL_VISION}}</div></section>
   <section class="panel c3 accent-red"><div class="label">The Problem</div><div class="body">{{PANEL_PROBLEM}}</div></section>
   <section class="panel c6 accent-sky"><div class="label">The Solution</div><div class="body">{{PANEL_SOLUTION}}</div></section>
   <section class="panel c3 accent-green"><div class="label">Outcomes</div><div class="body">{{PANEL_OUTCOMES}}</div></section>
   <section class="panel c3 accent-amber"><div class="label">Market Opportunity · TAM</div><div class="body">{{PANEL_TAM}}</div></section>
   <section class="panel c3"><div class="label">Ideal Partners</div><div class="body">{{PANEL_IDEAL_PARTNERS}}</div></section>
   <section class="panel c3 accent-teal"><div class="label">Built on Salesforce</div><div class="body">{{PANEL_BUILT_ON}}</div></section>
 </div>
```

(If the template's `<style>` lacks an `.accent-red` or `.accent-green` rule, add them alongside the existing accent classes — the prior #14 template had `accent-sky/teal/amber`; #11's had `accent-red/green`. Add any missing ones using the same pattern, e.g. `.panel.accent-red .label{color:#f87171;} .panel.accent-red .label::before{background:#dc2626;}` and `.panel.accent-green .label{color:#4ade80;} .panel.accent-green .label::before{background:#16a34a;}`.)

- [ ] **Step 2: Update the header sub-label** — change the `<div class="sub">Executive Overview</div>` line to `<div class="sub">Executive &amp; Solution Overview</div>` (reflects the merged scope).

- [ ] **Step 3: Run R-POSTER-02 — expect PASS now.**

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-POSTER-02"`
Expected: PASS (all 7 panels fill from the two sources; no surviving tokens).

- [ ] **Step 4: Commit**

```bash
git add templates/exec-infographic-poster.html
git commit --no-verify -m "feat(poster): merged 7-panel exec template (vision/problem/solution/outcomes/TAM/partners/built-on)"
```

---

### Task 3: Remove #11's poster (template + map + test references)

**Files:**
- Delete: `templates/solution-infographic-poster.html`
- Modify: `tests/validate_skill.py` (`_POSTER_FILES`, R-POSTER-01 to assert #11 poster absent, R-POSTER-03 to assert no #11 map entry)

**Interfaces:**
- Consumes: `SOURCES_FOR`/`PANELS_FOR`/`SECTION_MAP` from Task 1 (no `11-solution-infographic` key).

- [ ] **Step 1: Delete the #11 poster template.**

```bash
git rm templates/solution-infographic-poster.html
```

- [ ] **Step 2: Update `_POSTER_FILES`** in `tests/validate_skill.py` to only the merged poster:

```python
_POSTER_FILES = {
    "14-exec-infographic": "templates/exec-infographic-poster.html",
}
```

- [ ] **Step 3: Strengthen R-POSTER-01 + R-POSTER-03** to guard the consolidation. Replace `t_poster_templates` and `t_poster_map_parity` with:

```python
@check("R-POSTER-01: the one merged poster template exists w/ UPPER_SNAKE tokens; the #11 poster is gone")
def t_poster_templates():
    for slug, path in _POSTER_FILES.items():
        assert exists(path), f"missing poster template: {path}"
        for tok in re.findall(r"\{\{([^{}]*)\}\}", read(path)):
            assert re.fullmatch(r"[A-Z0-9_]+", tok), f"{path}: malformed token {{{{{tok}}}}}"
    # consolidation guard: the #11 poster template must NOT exist (no stale duplicate)
    assert not exists("templates/solution-infographic-poster.html"), \
        "solution-infographic-poster.html must be removed (posters consolidated into the merged exec poster)"

@check("R-POSTER-03: merged poster PANEL_ slots exactly match SECTION_MAP; #11 has no poster map entry")
def t_poster_map_parity():
    p = _load_script("scripts/poster.py", "poster_parity_mod")
    for slug, path in _POSTER_FILES.items():
        body = read(path)
        slots = {t for t in re.findall(r"\{\{([A-Z0-9_]+)\}\}", body) if t.startswith("PANEL_")}
        mapped = p.PANELS_FOR(slug)
        assert slots == mapped, f"{slug}: poster PANEL_ slots {slots} != SECTION_MAP panels {mapped}"
    # consolidation guard: #11 must not carry a poster map entry
    assert "11-solution-infographic" not in p.SECTION_MAP, \
        "11-solution-infographic must have no SECTION_MAP entry (poster consolidated)"
```

- [ ] **Step 4: Run R-POSTER-01 + R-POSTER-03 — expect PASS.**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-POSTER-01|R-POSTER-03"`
Expected: both PASS (merged template's 7 `PANEL_` slots == map keys; #11 poster file and map entry both gone).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit --no-verify -m "feat(poster): remove #11 solution poster (consolidated into merged exec poster)"
```

---

### Task 4: Canvas — #11 reverts to a document-only card

`_card`/`build_index` need no code change (they already render a plain document card when `has_poster` is False). This task updates the R-CANVAS test so #11 is asserted as document-only and #14 as the (sole) poster-bearing card.

**Files:**
- Modify: `tests/validate_skill.py` (the R-CANVAS-01 poster assertions, ~lines 680-692)

**Interfaces:**
- Consumes: `build_index(manifest, html_present, poster_present)` (unchanged from the prior increment).

- [ ] **Step 1: Update the R-CANVAS-01 poster block.** Replace the dual-link assertions (the block added in the visual-infographics increment) with the merged shape — #14 is the only poster-bearing card; #11 is document-only:

```python
    # consolidation: #14 is the only poster-bearing card (title links the poster, document is secondary)
    page_poster = c.build_index(eff, {a: (a in ("14-exec-infographic","11-solution-infographic")) for a in mani.ARTIFACT_REGISTRY},
                                {"14-exec-infographic": True})
    assert "14-exec-infographic-poster.html" in page_poster, "merged poster (primary) link missing on #14"
    assert 'class="secondary-link" href="14-exec-infographic.html"' in page_poster, "#14 document must be the secondary link"
    assert ">(document)</a>" in page_poster, "secondary link must be labeled '(document)'"
    # #11 reverts to a plain document card — NO poster link anywhere for #11
    assert "11-solution-infographic.html" in page_poster, "#11 document link missing"
    assert "11-solution-infographic-poster.html" not in page_poster, "#11 must NOT have a poster link (consolidated)"
    # a non-poster artifact still single-links
    assert "01-brief-poster.html" not in page_poster, "non-poster artifact must not get a poster link"
```

- [ ] **Step 2: Run R-CANVAS-01 — expect PASS.**

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-CANVAS-01"`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/validate_skill.py
git commit --no-verify -m "test(R-CANVAS-01): #14 sole poster card; #11 reverts to document-only"
```

---

### Task 5: Ref update + full suite green

**Files:**
- Modify: `refs/render-and-canvas.md` (section 1b — one merged multi-source poster)

- [ ] **Step 1: Replace the section 1b poster paragraph** in `refs/render-and-canvas.md` with the merged/multi-source description:

```markdown
## 1b. The merged poster view (#14)

`14-exec-infographic` renders a single visual **poster** view — `14-exec-infographic-poster.html` — via
`scripts/poster.py`, in addition to its document HTML. It is a **merged, multi-source** poster: it draws
its 7 panels from BOTH the exec (#14) and solution (#11) markdown — Vision (#14) · The Problem (#11) ·
The Solution (#11) · Outcomes (#11) · Market·TAM (#14) · Ideal Partners (#14) · Built on Salesforce (#11).
`poster.SECTION_MAP["14-exec-infographic"]` maps each `{{PANEL_*}}` slot to a `(source_slug, H2)` pair;
`render_poster(slug, sources, template, meta)` takes `sources={slug: md_text}` for every artifact the
poster needs (use `SOURCES_FOR(slug)` to know which). Each source's markdown stays the source of truth;
the poster is a derived projection. The canvas links the poster as the **primary** title on the #14 card
with the document as a secondary "(document)" link. **#11 has a document view only** (its poster was
consolidated into this merged one). The section→panel contract keys on the exact H2 headings of *each*
source — if an H2 is reworded in #11 or #14, update `SECTION_MAP` (guarded by R-POSTER-02/03).
```

- [ ] **Step 2: Run the full suite — expect all green.**

Run: `python3 tests/validate_skill.py`
Expected: `49/49 checks passed` (check count unchanged — we rewrote checks, didn't add/remove). If a doc states a check-count, R-DOC-01 flags it; grep and reconcile.

- [ ] **Step 3: Confirm no stale check-count claim.**

Run: `grep -rnE "[0-9]+ checks?" SKILL.md README.md refs/`
Expected: any match equals the suite size; fix and re-run if not.

- [ ] **Step 4: Commit (this one runs the hook — suite is green now).**

```bash
git add refs/render-and-canvas.md
git commit -m "docs: render-and-canvas ref — one merged multi-source poster; #11 document-only"
```

---

### Task 6: Dogfood — render the merged poster for the HC effort

**Files:**
- None modified (verification). Effort at `/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem`.

- [ ] **Step 1: Remove the stale #11 effort poster + render the merged one.** Run:

```bash
cd /Users/bstauber/.claude/skills/ps-npi-forge
EFF=/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem
rm -f "$EFF/canvas/11-solution-infographic-poster.html"   # consolidated away
python3 - "$EFF" <<'PY'
import os,sys; sys.path.insert(0,"scripts"); import poster
eff=sys.argv[1]
srcs = {s: open(os.path.join(eff,"artifacts",s+".md")).read()
        for s in poster.SOURCES_FOR("14-exec-infographic")}
tmpl = open("templates/exec-infographic-poster.html").read()
meta = {"TITLE":"Agentforce for Healthcare","LABEL":"Executive & Solution Overview",
        "RELEASE":"summer-26","GENERATED_DATE":"2026-06-25","HOME_HREF":"index.html"}
out,unf = poster.render_poster("14-exec-infographic", srcs, tmpl, meta)
assert unf==[], f"unfilled: {unf}"
open(os.path.join(eff,"canvas","14-exec-infographic-poster.html"),"w").write(out)
print("merged poster rendered; sources:", set(srcs), "unfilled:", unf)
PY
```
Expected: "merged poster rendered; sources: {'14-exec-infographic', '11-solution-infographic'} unfilled: []".

- [ ] **Step 2: Rebuild the canvas (only #14 poster-bearing now).** Run:

```bash
cd /Users/bstauber/.claude/skills/ps-npi-forge
EFF=/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem
python3 - "$EFF" <<'PY'
import os,sys; sys.path.insert(0,"scripts"); import manifest,canvas
eff=sys.argv[1]; m=manifest.load(os.path.join(eff,"manifest.yaml"))
present={a:os.path.exists(os.path.join(eff,"canvas",a+".html")) for a in manifest.ARTIFACT_REGISTRY}
posters={"14-exec-infographic": os.path.exists(os.path.join(eff,"canvas","14-exec-infographic-poster.html"))}
open(os.path.join(eff,"canvas","index.html"),"w").write(canvas.build_index(m,present,posters))
print("canvas rebuilt; poster-bearing:", {k:v for k,v in posters.items() if v})
PY
```
Expected: "poster-bearing: {'14-exec-infographic': True}".

- [ ] **Step 3: Verify the dogfood.** Run:

```bash
EFF=/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem
echo "stale #11 poster gone:" && ([ ! -f "$EFF/canvas/11-solution-infographic-poster.html" ] && echo OK || echo "STILL PRESENT")
echo "merged poster panels (expect 7 labels):" && grep -oE 'class="label">[^<]+' "$EFF/canvas/14-exec-infographic-poster.html" | wc -l
echo "no raw tokens:" && grep -L "{{" "$EFF/canvas/14-exec-infographic-poster.html"
echo "canvas: #14 poster-primary, #11 document-only:" 
grep -oE '14-exec-infographic-poster.html|11-solution-infographic-poster.html' "$EFF/canvas/index.html" | sort -u
```
Expected: stale gone = OK; 7 labels; no raw tokens (file path printed = clean); canvas shows `14-exec-infographic-poster.html` but NOT `11-solution-infographic-poster.html`.

- [ ] **Step 4: No commit** (effort assets are outside the repo). If any check failed, fix the relevant task's skill code and re-run.

---

## Notes for the implementer

- **Order:** Task 1 (engine, suite goes red) → 2 (merged template, R-POSTER-02 green) → 3 (delete #11 poster + guards) → 4 (canvas test) → 5 (ref + full green) → 6 (dogfood).
- Tasks 1-4 use `git commit --no-verify` because the suite is intentionally red mid-sequence (the pre-commit hook runs it). Task 5's commit runs the hook (suite green by then).
- **Do NOT** touch the registry, manifest, the markdown artifacts, or the family count. Both #11 and #14 keep their *document* views.
- **The H2 strings in `SECTION_MAP` are exact** (verified against both templates) — copy them verbatim.
- **Keep the dark poster treatment** — only the panel set/order/labels change.
- The merged map lives in ONE place (`poster.py SECTION_MAP`); R-POSTER-03 enforces slot↔map parity + no #11 entry.
