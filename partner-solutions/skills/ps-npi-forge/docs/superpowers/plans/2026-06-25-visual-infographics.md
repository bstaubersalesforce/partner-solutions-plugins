# Visual Infographic Views (#11 + #14) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an SLDS-light visual "poster" HTML view for the solution infographic (#11) and exec infographic (#14), projected from each artifact's markdown source, with the Key Resources canvas linking both the document and poster views.

**Architecture:** A second render path. The markdown templates stay the source of truth (untouched). Two new self-contained styled `templates/*-poster.html` files carry `{{PANEL_*}}` token slots in the skill's SLDS-light palette. A new `scripts/poster.py` splits an effort artifact's markdown by H2 (`sections.split`), maps each section to its panel via a per-artifact map, converts each section body to HTML (`md_to_html.md_to_html`), fills the poster, and reports unfilled tokens. `canvas.py` is extended so #11/#14 cards link both views.

**Tech Stack:** Python 3 stdlib only. HTML/CSS (SLDS-light palette). Reuses `scripts/sections.py` and `scripts/md_to_html.py`. No new dependencies.

## Global Constraints

- **Stdlib-only.** No third-party imports in `scripts/` or `tests/`.
- **MD is the source of truth.** Do NOT edit `templates/11-solution-infographic.md` or `templates/14-exec-infographic.md`, the registry, the manifest, or the other 13 artifacts. Family stays 15.
- **SLDS-light palette only** (match the skill's `document-shell.html` / canvas tokens): brand blue `#0176d3`, navy `#032d60`, slate `#444`, rule `#e5e5e5`, panel/bg `#f8fafc`/`#eef4ff`, white `#fff`, font `"Salesforce Sans","Helvetica Neue",Helvetica,Arial,sans-serif`. NOT pov-builder's dark 1920px poster.
- **Reuse the sanctioned converters** — `from sections import split` and `from md_to_html import md_to_html`. Do NOT re-implement markdown. `poster.py` converts each section *body* with `md_to_html(body)` (full block conversion: paragraphs, lists, inline), NOT `_inline` alone.
- **Poster tokens are UPPER_SNAKE** (`{{PANEL_*}}`, `{{TITLE}}` etc.) — same hygiene rule as templates.
- **Poster file naming:** `<slug>-poster.html` (companion, like `02-slide-summary-slides.html`).
- **No new registry artifact** — posters are *views*, not artifacts. Do NOT touch `ARTIFACT_REGISTRY`.
- **Run the suite:** `python3 tests/validate_skill.py` (exit 0). Baseline is 46/46.
- **Branch:** `npi-visual-infographics` (already created off `main`; spec already committed at `76f08dd`).

## Section → panel maps (the content contract — used verbatim by Tasks 1–3)

**#14 exec-infographic** (`templates/14-exec-infographic.md` H2 headings → panel token):
- "Vision" → `PANEL_VISION`
- "Value proposition" → `PANEL_VALUE_PROP`
- "Key use cases" → `PANEL_USE_CASES`
- "Ideal partners" → `PANEL_IDEAL_PARTNERS`
- "Market opportunity (TAM)" → `PANEL_TAM`
- ("Executive overview (diagram)" → NOT a panel — omitted from the poster)

**#11 solution-infographic** (`templates/11-solution-infographic.md` H2 headings → panel token):
- "The one-line story" → `PANEL_HEADLINE` (header-band tagline)
- "The problem (why this matters)" → `PANEL_PROBLEM`
- "The solution (what we built on Salesforce)" → `PANEL_SOLUTION`
- "Outcomes (the proof)" → `PANEL_OUTCOMES`
- "Market & who it's for" → `PANEL_MARKET`
- "Built on Salesforce (the OEM/Embedded stack)" → `PANEL_BUILT_ON`
- ("Solution overview (diagram)" → NOT a panel — omitted)

> These exact H2 strings are the contract. `sections.split` keys sections by the H2 text with the
> leading `## ` stripped (verified). The map lives in ONE place — `poster.py` `SECTION_MAP` — keyed by
> artifact slug.

---

### Task 1: `poster.py` core — split, map, fill, report (with #14 map)

Build the render engine and prove it on #14. (#11's map is added in Task 3 once #11's template exists.)

**Files:**
- Create: `scripts/poster.py`
- Create: `templates/exec-infographic-poster.html` (minimal valid poster for the test; styled fully in Task 2)
- Test: extend `tests/validate_skill.py` (new R-POSTER-02 check)

**Interfaces:**
- Produces: `poster.SECTION_MAP` (dict: slug → {H2-title: PANEL_TOKEN}); `poster.render_poster(md_text, template_text, meta)` → `(filled_html, unfilled_tokens)`; `poster.PANELS_FOR(slug)` → set of panel tokens. Later tasks (canvas, #11) consume `SECTION_MAP`.

- [ ] **Step 1: Create a minimal `templates/exec-infographic-poster.html`** (full styling comes in Task 2; this is enough to test the fill engine). It must carry every #14 panel token + the metadata tokens:

```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}} — Executive Overview</title></head>
<body>
<header><h1>{{TITLE}}</h1><p>{{LABEL}} · {{RELEASE}} · {{GENERATED_DATE}}</p>
<a href="{{HOME_HREF}}">← All artifacts</a></header>
<section class="panel panel-vision"><h2>Vision</h2>{{PANEL_VISION}}</section>
<section class="panel panel-value"><h2>Value proposition</h2>{{PANEL_VALUE_PROP}}</section>
<section class="panel panel-usecases"><h2>Key use cases</h2>{{PANEL_USE_CASES}}</section>
<section class="panel panel-partners"><h2>Ideal partners</h2>{{PANEL_IDEAL_PARTNERS}}</section>
<section class="panel panel-tam"><h2>Market opportunity (TAM)</h2>{{PANEL_TAM}}</section>
</body></html>
```

- [ ] **Step 2: Create `scripts/poster.py`** with the engine + the #14 map:

```python
#!/usr/bin/env python3
"""
Poster renderer for ps-npi-forge. Stdlib-only.

Projects an artifact's markdown (the source of truth) into a styled SLDS-light "poster" HTML
template by mapping each H2 section's body into the matching {{PANEL_*}} slot. Reuses the sanctioned
splitter (sections.split) and block converter (md_to_html.md_to_html); does NOT re-implement markdown.
"""
import os, re, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from sections import split            # split(md) -> {H2-title: section-text}
from md_to_html import md_to_html     # block converter (paragraphs, lists, inline)

TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

# the section->panel contract, keyed by artifact slug. H2 title (without "## ") -> panel token.
SECTION_MAP = {
    "14-exec-infographic": {
        "Vision": "PANEL_VISION",
        "Value proposition": "PANEL_VALUE_PROP",
        "Key use cases": "PANEL_USE_CASES",
        "Ideal partners": "PANEL_IDEAL_PARTNERS",
        "Market opportunity (TAM)": "PANEL_TAM",
    },
}

def PANELS_FOR(slug):
    return set(SECTION_MAP.get(slug, {}).values())

def _body_after_h2(section_text):
    # sections.split returns the section text; strip a leading "## Heading" line if present
    lines = section_text.splitlines()
    if lines and lines[0].lstrip().startswith("## "):
        lines = lines[1:]
    return "\n".join(lines).strip()

def render_poster(slug, md_text, template_text, meta):
    """Return (filled_html, unfilled_tokens). meta supplies TITLE/LABEL/RELEASE/GENERATED_DATE/HOME_HREF."""
    secs = split(md_text)                      # {H2-title: section-text}
    fills = dict(meta)                          # metadata tokens
    smap = SECTION_MAP.get(slug, {})
    for h2, panel in smap.items():
        if h2 not in secs:
            raise ValueError(f"{slug}: poster section '{h2}' not found in artifact markdown")
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

- [ ] **Step 3: Write the failing test** — add to `tests/validate_skill.py` after the R-RENDER checks:

```python
# ---- R-POSTER-02: poster.render_poster fills every panel from MD sections; missing section raises -
@check("R-POSTER-02: render_poster maps #14 MD sections into panel slots, leaving no unfilled token; a missing mapped section raises")
def t_poster_render():
    p = _load_script("scripts/poster.py", "poster_mod")
    tmpl = read("templates/exec-infographic-poster.html")
    md = read("templates/14-exec-infographic.md")  # the template itself has every mapped H2
    meta = {"TITLE":"X","LABEL":"Executive Overview","RELEASE":"r","GENERATED_DATE":"d","HOME_HREF":"index.html"}
    out, unfilled = p.render_poster("14-exec-infographic", md, tmpl, meta)
    assert unfilled == [], f"unfilled poster tokens: {unfilled}"
    assert "{{" not in out, "no raw token may survive a complete poster fill"
    # each panel slot received converted HTML (the {{PANEL_*}} tokens are gone)
    for tok in p.PANELS_FOR("14-exec-infographic"):
        assert "{{"+tok+"}}" not in out, f"{tok} not filled"
    # a missing mapped section raises (contract guard)
    broken = md.replace("## Vision", "## Visionnn")
    try:
        p.render_poster("14-exec-infographic", broken, tmpl, meta)
        assert False, "missing mapped section must raise"
    except ValueError:
        pass
```

- [ ] **Step 4: Run it; verify PASS**

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-POSTER-02"`
Expected: PASS. (#14's MD template has all five mapped H2 headings, so every panel fills.)

- [ ] **Step 5: Commit**

```bash
git add scripts/poster.py templates/exec-infographic-poster.html tests/validate_skill.py
git commit -m "feat(poster): poster.py render engine + #14 poster template scaffold + R-POSTER-02"
```

---

### Task 2: Style the #14 poster (SLDS-light visual)

Turn the minimal #14 template into the actual SLDS-light "poster" — the visual deliverable.

**Files:**
- Modify: `templates/exec-infographic-poster.html` (full styling; keep every token from Task 1)

**Interfaces:**
- Consumes: the panel/metadata tokens defined in Task 1 (must remain present, same names).

- [ ] **Step 1: Replace the file with the styled poster.** Keep all the same tokens; add the SLDS-light CSS, an accent bar, a header band, and a responsive panel grid:

```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}} — Executive Overview</title>
<style>
 *,*::before,*::after{box-sizing:border-box;} 
 body{margin:0;font-family:"Salesforce Sans","Helvetica Neue",Helvetica,Arial,sans-serif;color:#181818;background:#f8fafc;}
 .accent{height:6px;background:linear-gradient(90deg,#032d60,#0176d3,#6bb7ff);}
 .poster{max-width:1100px;margin:0 auto;padding:0 0 3rem;}
 header.band{background:#032d60;color:#fff;padding:1.6rem 2rem;}
 header.band .eyebrow{text-transform:uppercase;letter-spacing:0.1em;font-size:0.7rem;color:#9ec7f0;}
 header.band h1{margin:0.2rem 0;font-size:1.7rem;}
 header.band .tagline{font-size:1rem;color:#cfe2f7;margin:0.4rem 0 0;}
 header.band .meta{font-size:0.78rem;color:#9ec7f0;margin-top:0.6rem;}
 header.band a{color:#9ec7f0;font-size:0.78rem;}
 .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;padding:1.5rem 2rem;}
 .panel{background:#fff;border:1px solid #e5e5e5;border-top:3px solid #0176d3;border-radius:8px;padding:1.1rem 1.25rem;}
 .panel h2{margin:0 0 0.5rem;color:#032d60;font-size:1.05rem;}
 .panel.span2{grid-column:span 2;}
 .panel :is(p,li){font-size:0.92rem;color:#181818;line-height:1.5;}
 @media print{body{background:#fff;} header.band{print-color-adjust:exact;-webkit-print-color-adjust:exact;}}
</style></head>
<body>
<div class="accent"></div>
<div class="poster">
 <header class="band">
   <div class="eyebrow">{{LABEL}} · {{RELEASE}}</div>
   <h1>{{TITLE}}</h1>
   <div class="meta">Generated {{GENERATED_DATE}} · <a href="{{HOME_HREF}}">← All artifacts</a></div>
 </header>
 <div class="grid">
   <section class="panel"><h2>Vision</h2>{{PANEL_VISION}}</section>
   <section class="panel"><h2>Value proposition</h2>{{PANEL_VALUE_PROP}}</section>
   <section class="panel span2"><h2>Key use cases</h2>{{PANEL_USE_CASES}}</section>
   <section class="panel"><h2>Ideal partners</h2>{{PANEL_IDEAL_PARTNERS}}</section>
   <section class="panel"><h2>Market opportunity (TAM)</h2>{{PANEL_TAM}}</section>
 </div>
</div>
</body></html>
```

- [ ] **Step 2: Verify R-POSTER-02 still passes** (tokens unchanged, only styling added):

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-POSTER-02"`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add templates/exec-infographic-poster.html
git commit -m "feat(poster): style #14 exec poster in SLDS-light palette"
```

---

### Task 3: #11 solution poster (template + map entry)

**Files:**
- Create: `templates/solution-infographic-poster.html` (styled, SLDS-light)
- Modify: `scripts/poster.py` (add the #11 entry to `SECTION_MAP`)
- Test: extend `tests/validate_skill.py` (R-POSTER-02 to also exercise #11)

**Interfaces:**
- Consumes: `poster.render_poster`, `SECTION_MAP` from Task 1.
- Produces: `SECTION_MAP["11-solution-infographic"]` and the #11 poster template.

- [ ] **Step 1: Add the #11 map entry** to `SECTION_MAP` in `scripts/poster.py` (after the #14 entry):

```python
    "11-solution-infographic": {
        "The one-line story": "PANEL_HEADLINE",
        "The problem (why this matters)": "PANEL_PROBLEM",
        "The solution (what we built on Salesforce)": "PANEL_SOLUTION",
        "Outcomes (the proof)": "PANEL_OUTCOMES",
        "Market & who it's for": "PANEL_MARKET",
        "Built on Salesforce (the OEM/Embedded stack)": "PANEL_BUILT_ON",
    },
```

- [ ] **Step 2: Create `templates/solution-infographic-poster.html`** (SLDS-light, headline in the band):

```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}} — Solution Overview</title>
<style>
 *,*::before,*::after{box-sizing:border-box;}
 body{margin:0;font-family:"Salesforce Sans","Helvetica Neue",Helvetica,Arial,sans-serif;color:#181818;background:#f8fafc;}
 .accent{height:6px;background:linear-gradient(90deg,#032d60,#0176d3,#6bb7ff);}
 .poster{max-width:1100px;margin:0 auto;padding:0 0 3rem;}
 header.band{background:#032d60;color:#fff;padding:1.6rem 2rem;}
 header.band .eyebrow{text-transform:uppercase;letter-spacing:0.1em;font-size:0.7rem;color:#9ec7f0;}
 header.band h1{margin:0.2rem 0;font-size:1.7rem;}
 header.band .tagline{font-size:1.05rem;color:#eaf2fd;margin:0.5rem 0 0;}
 header.band .meta{font-size:0.78rem;color:#9ec7f0;margin-top:0.6rem;}
 header.band a{color:#9ec7f0;font-size:0.78rem;}
 .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;padding:1.5rem 2rem;}
 .panel{background:#fff;border:1px solid #e5e5e5;border-top:3px solid #0176d3;border-radius:8px;padding:1.1rem 1.25rem;}
 .panel h2{margin:0 0 0.5rem;color:#032d60;font-size:1.05rem;}
 .panel.span2{grid-column:span 2;}
 .panel :is(p,li){font-size:0.92rem;color:#181818;line-height:1.5;}
 @media print{body{background:#fff;} header.band{print-color-adjust:exact;-webkit-print-color-adjust:exact;}}
</style></head>
<body>
<div class="accent"></div>
<div class="poster">
 <header class="band">
   <div class="eyebrow">{{LABEL}} · {{RELEASE}}</div>
   <h1>{{TITLE}}</h1>
   <div class="tagline">{{PANEL_HEADLINE}}</div>
   <div class="meta">Generated {{GENERATED_DATE}} · <a href="{{HOME_HREF}}">← All artifacts</a></div>
 </header>
 <div class="grid">
   <section class="panel span2"><h2>The problem</h2>{{PANEL_PROBLEM}}</section>
   <section class="panel span2"><h2>The solution</h2>{{PANEL_SOLUTION}}</section>
   <section class="panel"><h2>Outcomes</h2>{{PANEL_OUTCOMES}}</section>
   <section class="panel"><h2>Market &amp; who it's for</h2>{{PANEL_MARKET}}</section>
   <section class="panel span2"><h2>Built on Salesforce</h2>{{PANEL_BUILT_ON}}</section>
 </div>
</div>
</body></html>
```

- [ ] **Step 3: Extend R-POSTER-02 to also cover #11.** In `t_poster_render`, after the #14 assertions, add:

```python
    # #11 solution poster fills identically
    tmpl11 = read("templates/solution-infographic-poster.html")
    md11 = read("templates/11-solution-infographic.md")
    out11, unf11 = p.render_poster("11-solution-infographic", md11, tmpl11, meta)
    assert unf11 == [], f"unfilled #11 poster tokens: {unf11}"
    assert "{{" not in out11, "no raw token may survive a complete #11 poster fill"
```

- [ ] **Step 4: Run it; verify PASS**

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-POSTER-02"`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add templates/solution-infographic-poster.html scripts/poster.py tests/validate_skill.py
git commit -m "feat(poster): #11 solution poster template + SECTION_MAP entry"
```

---

### Task 4: Template/map parity guard (R-POSTER-01 + R-POSTER-03)

Guard the new parallel structure: every poster template's `{{PANEL_*}}` slots must equal the map's panel tokens for that slug (no orphan slot, no map token without a slot).

**Files:**
- Modify: `tests/validate_skill.py` (add R-POSTER-01 + R-POSTER-03)

- [ ] **Step 1: Add the checks** after `t_poster_render`:

```python
_POSTER_FILES = {
    "14-exec-infographic": "templates/exec-infographic-poster.html",
    "11-solution-infographic": "templates/solution-infographic-poster.html",
}

@check("R-POSTER-01: poster templates exist and every {{TOKEN}} is UPPER_SNAKE")
def t_poster_templates():
    for slug, path in _POSTER_FILES.items():
        assert exists(path), f"missing poster template: {path}"
        for tok in re.findall(r"\{\{([^{}]*)\}\}", read(path)):
            assert re.fullmatch(r"[A-Z0-9_]+", tok), f"{path}: malformed token {{{{{tok}}}}}"

@check("R-POSTER-03: each poster template's PANEL_* slots exactly match poster.SECTION_MAP for that slug")
def t_poster_map_parity():
    p = _load_script("scripts/poster.py", "poster_parity_mod")
    for slug, path in _POSTER_FILES.items():
        body = read(path)
        slots = {t for t in re.findall(r"\{\{([A-Z0-9_]+)\}\}", body) if t.startswith("PANEL_")}
        mapped = p.PANELS_FOR(slug)
        assert slots == mapped, f"{slug}: poster PANEL_ slots {slots} != SECTION_MAP panels {mapped}"
```

- [ ] **Step 2: Run; verify PASS**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-POSTER-01|R-POSTER-03"`
Expected: both PASS. (The #14 template's PANEL_ slots = {VISION,VALUE_PROP,USE_CASES,IDEAL_PARTNERS,TAM}; #11's = {HEADLINE,PROBLEM,SOLUTION,OUTCOMES,MARKET,BUILT_ON} — each must equal its map.)

- [ ] **Step 3: Sanity-gate R-POSTER-03.** Temporarily delete one `{{PANEL_TAM}}` from the #14 template, run, confirm R-POSTER-03 FAILS, then restore.

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-POSTER-03"`
Expected (during sanity check): FAIL. After restore: PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/validate_skill.py
git commit -m "test(R-POSTER-01,03): poster template token hygiene + slot/map parity guard"
```

---

### Task 5: Canvas dual-link for poster-bearing artifacts

Extend `canvas.py` so #11/#14 cards link both the document and poster views.

**Files:**
- Modify: `scripts/canvas.py` (`_card` signature + `build_index` signature, ~lines 64-122)
- Test: extend `tests/validate_skill.py` R-CANVAS-01 (the existing canvas check)

**Interfaces:**
- Consumes: nothing new.
- Produces: `build_index(manifest, html_present, poster_present=None)` — the new optional third arg `poster_present` is a `{slug: bool}` map (default `{}`); `_card(slug, rec, has_html, has_poster=False)`.

- [ ] **Step 1: Update `_card`** to take `has_poster` and emit a Poster link when present. Replace the `_card` function (lines 64-87) so the `has_html` branch becomes:

```python
def _card(slug, rec, has_html, has_poster=False):
    status = rec.get("status", "pending")
    conf = rec.get("confidence", 0.0)
    color = _STATUS_COLOR.get(status, "#444444")
    label = _LABEL.get(slug, slug)
    kind = _html.escape(_KIND.get(slug, "Artifact"))
    summary = _html.escape(_SUMMARY.get(slug, ""))
    badge = (f'<span class="badge" style="background:{color}">{_html.escape(status)}</span>'
             f'<span class="conf">conf {conf:.2f}</span>')
    if has_html or has_poster:
        links = []
        if has_html:
            links.append(f'<a href="{slug}.html">{_html.escape(label)}</a>')
        if has_poster:
            links.append(f'<a href="{slug}-poster.html">Poster</a>')
        title = " · ".join(links)
        if has_html and status != "verified":
            title += f' <span class="tag-pending">— {_html.escape(status)}, not yet final</span>'
        cls = "card"
    else:
        title = f'{_html.escape(label)} <span class="gap">— not yet rendered</span>'
        cls = "card gap-card"
    return (f'<div class="{cls}">'
            f'<span class="card-kind">{kind}</span>'
            f'<h3 class="card-title">{title}</h3>'
            f'<p class="card-desc">{summary}</p>'
            f'<div class="card-meta">{badge}</div></div>')
```

(Note: when `has_html` is False but `has_poster` is True, the document label isn't shown as a link; to keep the card readable, prepend the label as plain text in that edge case. Add this just before `title = " · ".join(links)`:)

```python
        if not has_html and has_poster:
            links.insert(0, _html.escape(label))
```

- [ ] **Step 2: Update `build_index`** (lines 117-122) to accept and thread `poster_present`:

```python
def build_index(manifest, html_present, poster_present=None):
    poster_present = poster_present or {}
    release = _html.escape(str(manifest.get("release", "")))
    slug = _html.escape(str(manifest.get("product_slug", "")))
    overall = _overall(manifest)
    cards = "\n".join(_card(s, manifest["artifacts"][s], html_present.get(s, False),
                            poster_present.get(s, False))
                      for s in manifest["artifacts"])
```

(Leave the rest of `build_index` unchanged.)

- [ ] **Step 3: Extend R-CANVAS-01.** In `t_canvas_index`, after the existing assertions, add a dual-link case:

```python
    # dual-link: a poster-bearing artifact links both its document and its -poster.html
    page_poster = c.build_index(eff, {a: (a == "11-solution-infographic") for a in mani.ARTIFACT_REGISTRY},
                                {"11-solution-infographic": True})
    assert "11-solution-infographic.html" in page_poster, "document link missing for poster-bearing artifact"
    assert "11-solution-infographic-poster.html" in page_poster, "poster link missing"
    assert ">Poster</a>" in page_poster, "poster link must be labeled 'Poster'"
    # a non-poster artifact still single-links (no spurious -poster.html)
    assert "01-brief-poster.html" not in page_poster, "non-poster artifact must not get a poster link"
    # poster present but document absent → poster link still renders, no dead document link
    page_only = c.build_index(eff, {a: False for a in mani.ARTIFACT_REGISTRY},
                              {"14-exec-infographic": True})
    assert "14-exec-infographic-poster.html" in page_only, "poster-only link must render"
    assert "14-exec-infographic.html\"" not in page_only, "no dead document link when document absent"
```

- [ ] **Step 4: Run; verify PASS**

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-CANVAS-01"`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/canvas.py tests/validate_skill.py
git commit -m "feat(canvas): dual-link document + poster views for #11/#14"
```

---

### Task 6: Render-and-canvas ref + full suite

**Files:**
- Modify: `refs/render-and-canvas.md` (add a poster-view subsection)

- [ ] **Step 1: Add a poster subsection** to `refs/render-and-canvas.md` after the format-rule section (section 1). Insert:

```markdown
## 1b. Poster views (#11, #14)

The solution infographic (`11-solution-infographic`) and exec infographic (`14-exec-infographic`) ALSO
render a visual **poster** view — `<slug>-poster.html` — via `scripts/poster.py`, in addition to their
document HTML. The poster is an SLDS-light styled projection: `poster.py` splits the artifact markdown
by H2 (`sections.split`), maps each section to a `{{PANEL_*}}` slot via `poster.SECTION_MAP` (keyed by
slug), converts each section body with `md_to_html`, and fills the poster template
(`templates/<solution|exec>-infographic-poster.html`). The markdown stays the source of truth; the
poster is a derived view. The canvas links **both** views for these two artifacts (document + poster).
The section→panel contract keys on the artifact's exact H2 headings — if an H2 is reworded, update
`SECTION_MAP` (guarded by R-POSTER-02/03).
```

- [ ] **Step 2: Run the full suite**

Run: `python3 tests/validate_skill.py`
Expected: `N/N checks passed` (N = 46 + R-POSTER-01/02/03 = 49). If a doc states a "N checks" count, R-DOC-01 flags it — grep and update if present.

- [ ] **Step 3: Confirm no stale check-count claim.**

Run: `grep -rnE "[0-9]+ checks?" SKILL.md README.md refs/`
Expected: any match equals the suite size; fix and re-run if not.

- [ ] **Step 4: Commit**

```bash
git add refs/render-and-canvas.md
git commit -m "docs: document the poster view + dual-link in render-and-canvas ref"
```

---

### Task 7: Dogfood — render both posters for the HC effort + dual-link canvas

**Files:**
- None modified (verification). Effort at `/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem`.

- [ ] **Step 1: Render both posters** via a short driver (poster.py is a library; drive it like canvas.py). Run:

```bash
cd /Users/bstauber/.claude/skills/ps-npi-forge
EFF=/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem
python3 - "$EFF" <<'PY'
import os,sys; sys.path.insert(0,"scripts"); import poster
eff=sys.argv[1]
for slug,tmpl in [("14-exec-infographic","templates/exec-infographic-poster.html"),
                  ("11-solution-infographic","templates/solution-infographic-poster.html")]:
    md=open(os.path.join(eff,"artifacts",slug+".md")).read()
    t=open(tmpl).read()
    meta={"TITLE":"Agentforce for Healthcare","LABEL":slug,"RELEASE":"summer-26","GENERATED_DATE":"2026-06-25","HOME_HREF":"index.html"}
    out,unf=poster.render_poster(slug,md,t,meta)
    assert unf==[], f"{slug} unfilled: {unf}"
    open(os.path.join(eff,"canvas",slug+"-poster.html"),"w").write(out)
    print(f"{slug}: poster rendered, no unfilled tokens")
PY
```
Expected: both render, "no unfilled tokens".

- [ ] **Step 2: Rebuild the canvas with poster presence.** Run:

```bash
cd /Users/bstauber/.claude/skills/ps-npi-forge
EFF=/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem
python3 - "$EFF" <<'PY'
import os,sys; sys.path.insert(0,"scripts"); import manifest,canvas
eff=sys.argv[1]; m=manifest.load(os.path.join(eff,"manifest.yaml"))
present={a:os.path.exists(os.path.join(eff,"canvas",a+".html")) for a in manifest.ARTIFACT_REGISTRY}
posters={s:os.path.exists(os.path.join(eff,"canvas",s+"-poster.html")) for s in ["11-solution-infographic","14-exec-infographic"]}
open(os.path.join(eff,"canvas","index.html"),"w").write(canvas.build_index(m,present,posters))
print("canvas rebuilt; posters:",posters)
PY
```
Expected: `posters: {'11-…': True, '14-…': True}`.

- [ ] **Step 3: Verify the dogfood output.** Run:

```bash
EFF=/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem
echo "posters exist:" && ls "$EFF"/canvas/*-poster.html
echo "no raw tokens:" && grep -L "{{" "$EFF"/canvas/14-exec-infographic-poster.html "$EFF"/canvas/11-solution-infographic-poster.html
echo "SLDS-light (navy band present):" && grep -c "#032d60" "$EFF"/canvas/14-exec-infographic-poster.html
echo "canvas dual-links:" && grep -c -E "(11-solution-infographic|14-exec-infographic)-poster.html" "$EFF"/canvas/index.html
```
Expected: both poster files exist; no `{{` in either; navy band present; canvas shows 2 poster links.

- [ ] **Step 4: No commit needed** (effort assets are outside the skill repo). If anything failed, fix the skill code in the relevant task and re-run.

---

## Notes for the implementer

- **Order:** Task 1 (engine + #14 map/template) → 2 (style #14) → 3 (#11) → 4 (parity guards) → 5 (canvas) → 6 (ref + suite) → 7 (dogfood).
- **Do NOT** edit the markdown templates (`11-…md`, `14-…md`), the registry, or the manifest. Posters are views.
- **Reuse, don't reinvent:** `from sections import split`, `from md_to_html import md_to_html`. No second markdown parser.
- **The suite is your gate** after each task: `python3 tests/validate_skill.py`.
- **Section→panel map lives in ONE place** (`poster.py SECTION_MAP`); R-POSTER-03 enforces it matches the templates.
