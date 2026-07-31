# ps-npi-forge Content & Render Upgrades Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two new content sections (Key Use Cases table in #01, Messaging Hierarchy in #00), surface them on the canvas, and fix the rendering issues (rich HTML for #11/#12, Mermaid diagram clipping, and inconsistent tables) — all in the light SFDC scheme.

**Architecture:** ps-npi-forge is a stdlib-only Python skill. Artifact *content* is driven by Markdown templates in `templates/` with `{{UPPER_SNAKE}}` tokens; *rendering* runs through `scripts/md_to_html.py` (generic doc shell), `scripts/poster.py` (section→panel projection into a bespoke HTML template), `scripts/slide_deck.py`, and `scripts/canvas.py` (the Key Resources hub). Structural invariants are enforced by `tests/validate_skill.py` (50 checks at baseline). This plan adds template sections + tokens (Part 1), and extends the `poster.py` projection into a general `RICH_VIEWS` registry plus render-surface fixes (Part 2).

**Tech Stack:** Python 3 (stdlib only — no third-party imports), HTML/CSS, Mermaid 11 (browser CDN), the skill's own `validate_skill.py` harness.

## Global Constraints

- **Stdlib only.** No third-party Python imports in any `scripts/*.py`. (Copied verbatim from every script header.)
- **Tokens are UPPER_SNAKE.** Every `{{TOKEN}}` in `templates/*.md` must match `[A-Z0-9_]+` (enforced by R-TEST-02).
- **Shared template convention.** Every artifact template MUST keep the literal gap-banner header line, the `> {{GAP_BANNER}}` line, the `---\n**Sources:** {{SOURCES}}\n**Confidence:** ...` footer, and a `VOICE:` comment (enforced by R-TPL-02). New sections go BETWEEN the banner and the footer.
- **Complete-fill invariant.** Filling every `{{TOKEN}}` in a template with a value must leave no surviving `{{...}}` (enforced by R-RENDER-01). Any new token must therefore be a real fillable slot.
- **SLDS light palette** (from `~/.claude/style-conventions.md`): brand `#0176d3`, brand-dark `#014486`, navy `#032d60`, tint `#f0f5fc`/`#eef4ff`, panel `#f8fafc`, rule/border `#e5e5e5`, body `#181818`, white `#ffffff`. Font stack `'Salesforce Sans','Helvetica Neue',Arial,sans-serif`.
- **Mermaid theme directive** (verbatim, from `refs/mermaid-diagrams.md`): `%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f0f5fc","primaryTextColor":"#032d60","primaryBorderColor":"#0176d3","lineColor":"#444444","secondaryColor":"#f8fafc","tertiaryColor":"#ffffff","fontFamily":"Salesforce Sans, Helvetica Neue, Arial, sans-serif"}} }%%`
- **Every task ends green.** Run `python3 tests/validate_skill.py` from the skill root; expect `N/N checks passed` (N grows as tasks add checks). Commit only on green.
- **Skill root** for all paths below: `/Users/bstauber/.claude/skills/ps-npi-forge/`. Run commands from there.

---

## File Structure

**Part 1 (content):**
- Modify `templates/01-brief.md` — add Key Use Cases table section + enrich Additional resources grammar.
- Modify `templates/00-executive-summary.md` — add Messaging Hierarchy section.
- Modify `refs/artifact-templates.md` — document the new sections in the registry grammar.
- Modify `scripts/canvas.py` — `_SUMMARY["00"]` and `_SUMMARY["01"]` mention the new component.
- Modify `tests/validate_skill.py` — new checks R-TPL-05 (use-case table), R-TPL-06 (messaging hierarchy), R-CANVAS-04 (highlight mentions).

**Part 2 (render):**
- Modify `scripts/poster.py` — generalize `SECTION_MAP` into a `RICH_VIEWS` registry; add `render_rich_view(slug, sources, template, meta)` (or extend `render_poster`).
- Create `templates/solution-infographic.html` — light 3-column infographic (#11 primary view).
- Create `templates/marketecture.html` — light layered marketecture (#12 primary view).
- Modify `templates/document-shell.html` — Mermaid `flowchart` config + `.mermaid svg` CSS + shared light table style.
- Modify `scripts/slide_deck.py` — same Mermaid config in the deck's `mermaid.initialize`.
- Modify `refs/mermaid-diagrams.md` — authoring note on short labels + the useMaxWidth config.
- Modify `refs/render-and-canvas.md` — document the rich-view render path for #11/#12.
- Modify `tests/validate_skill.py` — new checks R-RICH-01/02 (rich-view registry + render), R-MERMAID-02 (config), R-TABLE-01 (shared light table).

---

## Task 1: Key Use Cases table in #01 brief (Req 1A)

**Files:**
- Modify: `templates/01-brief.md`
- Modify: `refs/artifact-templates.md`
- Test: `tests/validate_skill.py`

**Interfaces:**
- Produces: token `{{KEY_USE_CASES_TABLE}}` in `templates/01-brief.md`; a new `## Key use cases` H2 section.

- [ ] **Step 1: Write the failing test**

Add near the other R-TPL checks in `tests/validate_skill.py`:

```python
# ---- R-TPL-05: #01 carries the Key Use Cases table section + its 5 columns ----
@check("R-TPL-05: 01-brief carries a Key use cases section with the five required column headers and a fill token")
def t_use_case_table():
    body = read("templates/01-brief.md")
    assert "## Key use cases" in body, "#01 must carry a '## Key use cases' section"
    assert "{{KEY_USE_CASES_TABLE}}" in body, "#01 must carry the {{KEY_USE_CASES_TABLE}} fill token"
    for col in ["Category", "Opportunity", "Example Use Case", "Key Features", "What Partners Package"]:
        assert col in body, f"#01 use-case grammar missing column: {col}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-TPL-05`
Expected: `FAIL  R-TPL-05...` with "must carry a '## Key use cases' section"

- [ ] **Step 3: Add the section to `templates/01-brief.md`**

Insert this block immediately AFTER the `## What is {{PRODUCT_NAME}}?` / `{{WHAT_IS}}` pair is not required — put it right after the `## What are the opportunities for {{PRODUCT_NAME}}?` / `{{OPPORTUNITIES}}` pair (line 24) and BEFORE `## Market & TAM`:

```markdown
## Key use cases
<!-- One row per priority use case. Category → Opportunity (market size + why now) → a concrete Example Use Case → the Key Features used → What Partners Package (the shippable components). Required: if sources are thin, emit ONE row reading "PENDING — <what's missing>" and raise a gap in the banner (owner + next step); never omit the table. -->
| Category | Opportunity | Example Use Case | Key Features | What Partners Package |
|----------|-------------|------------------|--------------|-----------------------|
{{KEY_USE_CASES_TABLE}}
```

Note: `{{KEY_USE_CASES_TABLE}}` fills with one-or-more `| ... | ... | ... | ... | ... |` table-body rows (the generator emits the row markdown).

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-TPL-05`
Expected: `PASS  R-TPL-05...`

- [ ] **Step 5: Verify the complete-fill + token-hygiene invariants still hold**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-RENDER-01|R-TEST-02|R-TPL-02"`
Expected: all three `PASS` (the new token is UPPER_SNAKE, fills cleanly, and the shared convention is intact).

- [ ] **Step 6: Document the section in `refs/artifact-templates.md`**

In the registry table row for `01-brief`, change the Notes cell to mention the use-case grid. Find the line:

```markdown
| 01-brief | narrative | the 8-section product narrative |
```

Replace with:

```markdown
| 01-brief | narrative | the product narrative + the Key Use Cases grid (Category/Opportunity/Example/Key Features/What Partners Package) |
```

- [ ] **Step 7: Run full suite + commit**

```bash
python3 tests/validate_skill.py
git add templates/01-brief.md refs/artifact-templates.md tests/validate_skill.py
git commit -m "feat(01-brief): add Key Use Cases table section (Category/Opportunity/Example/Key Features/What Partners Package)"
```
Expected: `51/51 checks passed` (50 baseline + R-TPL-05).

---

## Task 2: Enrich #01 Additional resources grammar (Req 1D)

**Files:**
- Modify: `templates/01-brief.md`
- Test: `tests/validate_skill.py` (extend R-TPL-05's file — no new check needed; fold into a light assertion)

**Interfaces:**
- Consumes: the existing `{{RESOURCES}}` token and `## Additional resources` section (already present at line 29-30).
- Produces: an authoring comment guiding the resource categories. No new token (keeps `{{RESOURCES}}`).

- [ ] **Step 1: Write the failing test**

Extend the R-TPL-05 check (add these asserts at the end of `t_use_case_table`), so the resources grammar is pinned:

```python
    # Req 1D: the Additional resources section prompts for the FCD / COA / trial-org categories
    assert "## Additional resources" in body, "#01 must keep the Additional resources section"
    flat = " ".join(body.split()).lower()
    for needle in ["fcd", "coa", "trial"]:
        assert needle in flat, f"#01 Additional resources grammar missing prompt for: {needle}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-TPL-05`
Expected: `FAIL  R-TPL-05...` with "Additional resources grammar missing prompt for: fcd"

- [ ] **Step 3: Add the authoring comment to `templates/01-brief.md`**

Replace the existing Additional resources block (lines 29-30):

```markdown
## Additional resources
{{RESOURCES}}
```

with:

```markdown
## Additional resources
<!-- Group real links (from intake) under: (1) GTM assets — product FCDs (e.g. Agentforce 360 / Provider / Payer / Public Health FCDs); (2) Technical assets — COA ordering process (COA guide, Product SKUs guide, COA demo) and Administer/Developer guides; (3) Trial & Scratch orgs — Partner Org Setup Guide. Only include links the intake actually supplied; a missing category is a flagged gap, never invented. -->
{{RESOURCES}}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-TPL-05`
Expected: `PASS  R-TPL-05...`

- [ ] **Step 5: Confirm comment-stripping still works (R-MD2H-04)**

The `<!-- ... -->` comment must be stripped at render, not rendered as visible text.
Run: `python3 tests/validate_skill.py 2>&1 | grep R-MD2H-04`
Expected: `PASS` (the check renders every template and asserts no comment leaks).

- [ ] **Step 6: Commit**

```bash
python3 tests/validate_skill.py
git add templates/01-brief.md tests/validate_skill.py
git commit -m "feat(01-brief): enrich Additional resources grammar (FCDs, COA ordering, trial/scratch orgs)"
```
Expected: `51/51 checks passed`.

---

## Task 3: Messaging Hierarchy in #00 executive summary (Req 1B)

**Files:**
- Modify: `templates/00-executive-summary.md`
- Modify: `refs/artifact-templates.md`
- Test: `tests/validate_skill.py`

**Interfaces:**
- Produces: token `{{MESSAGING_HIERARCHY}}` and a `## Messaging hierarchy` H2 in `templates/00-executive-summary.md`.

- [ ] **Step 1: Write the failing test**

```python
# ---- R-TPL-06: #00 carries the Messaging Hierarchy section + its four content tiers ----
@check("R-TPL-06: 00-executive-summary carries a Messaging hierarchy section naming key message, product, pillars, features, plus a fill token")
def t_messaging_hierarchy():
    body = read("templates/00-executive-summary.md")
    assert "## Messaging hierarchy" in body, "#00 must carry a '## Messaging hierarchy' section"
    assert "{{MESSAGING_HIERARCHY}}" in body, "#00 must carry the {{MESSAGING_HIERARCHY}} fill token"
    flat = " ".join(body.split()).lower()
    for tier in ["key message", "product", "pillar", "feature"]:
        assert tier in flat, f"#00 messaging hierarchy grammar missing tier: {tier}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-TPL-06`
Expected: `FAIL  R-TPL-06...` with "must carry a '## Messaging hierarchy' section"

- [ ] **Step 3: Add the section to `templates/00-executive-summary.md`**

Insert immediately AFTER the `## Why this matters to our partners` / `{{PURPOSE}}` pair (line 14) and BEFORE `## Top use cases`:

```markdown
## Messaging hierarchy
<!-- The message stack (we author the content, not a slide graphic). Structure the fill as: **Key message** (one grounding sentence); **Product** (the positioning statement — what it is + the core promise); **Pillars** (exactly four, each a bold title + one line); **Features** (supporting bullets grouped under each pillar). Required: if a tier is unsupported, write "PENDING — <what's missing>" and raise a banner gap; never omit a tier. -->
{{MESSAGING_HIERARCHY}}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-TPL-06`
Expected: `PASS  R-TPL-06...`

- [ ] **Step 5: Verify invariants (complete-fill, token hygiene, shared convention)**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-RENDER-01|R-TEST-02|R-TPL-02"`
Expected: all `PASS`.

- [ ] **Step 6: Document in `refs/artifact-templates.md`**

Find:

```markdown
| 00-executive-summary | narrative | front door: vision, top 3-6 use cases, IPP summary, Next Steps & Blockers, rollup |
```

Replace with:

```markdown
| 00-executive-summary | narrative | front door: vision, messaging hierarchy (key message → product → 4 pillars → features), top 3-6 use cases, IPP summary, Next Steps & Blockers, rollup |
```

- [ ] **Step 7: Commit**

```bash
python3 tests/validate_skill.py
git add templates/00-executive-summary.md refs/artifact-templates.md tests/validate_skill.py
git commit -m "feat(00-exec-summary): add Messaging Hierarchy section (key message → product → 4 pillars → features)"
```
Expected: `52/52 checks passed` (50 + R-TPL-05 + R-TPL-06).

---

## Task 4: Canvas highlight-card mentions (Req 1C)

**Files:**
- Modify: `scripts/canvas.py`
- Test: `tests/validate_skill.py`

**Interfaces:**
- Consumes: `canvas._SUMMARY` dict (existing).
- Produces: updated `_SUMMARY["00-executive-summary"]` and `_SUMMARY["01-brief"]` strings that name the new components.

- [ ] **Step 1: Write the failing test**

```python
# ---- R-CANVAS-04: highlight-card blurbs mention the new #00/#01 components ----
@check("R-CANVAS-04: canvas _SUMMARY blurbs for #00 and #01 name the messaging hierarchy and the key use-case grid")
def t_canvas_highlight_mentions():
    c = _load_script("scripts/canvas.py", "canvas_hl_mod")
    s00 = c._SUMMARY["00-executive-summary"].lower()
    s01 = c._SUMMARY["01-brief"].lower()
    assert "messaging hierarchy" in s00, "#00 blurb must mention the messaging hierarchy"
    assert "use case" in s01 or "use-case" in s01, "#01 blurb must mention the key use-case grid"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-CANVAS-04`
Expected: `FAIL  R-CANVAS-04...` with "#00 blurb must mention the messaging hierarchy"
(The #01 blurb already says "use-case", so only the #00 assert fails first — that still fails the check.)

- [ ] **Step 3: Update `_SUMMARY` in `scripts/canvas.py`**

Replace the `00-executive-summary` line (line 43):

```python
    "00-executive-summary": "The front door: vision, top use cases, ideal-partner summary, and the rolled-up Next Steps & Blockers register.",
```

with:

```python
    "00-executive-summary": "The front door: vision, the messaging hierarchy (key message → product → four pillars → features), top use cases, ideal-partner summary, and the rolled-up Next Steps & Blockers register.",
```

Replace the `01-brief` line (line 44):

```python
    "01-brief": "The eight-section product narrative — the canonical use-case and details story for the new OEM/Embedded SKU.",
```

with:

```python
    "01-brief": "The product narrative plus the Key Use Cases grid (category, opportunity, example, key features, what partners package) — the canonical use-case and details story for the new OEM/Embedded SKU.",
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-CANVAS-04`
Expected: `PASS  R-CANVAS-04...`

- [ ] **Step 5: Confirm the existing canvas check still passes (R-CANVAS-01)**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-CANVAS-01`
Expected: `PASS` (blurb text change does not affect card structure).

- [ ] **Step 6: Commit**

```bash
python3 tests/validate_skill.py
git add scripts/canvas.py tests/validate_skill.py
git commit -m "feat(canvas): highlight-card blurbs mention messaging hierarchy (#00) and key use-case grid (#01)"
```
Expected: `53/53 checks passed`.

---

## Task 5: Generalize poster.py into a rich-view registry (Part 2A, foundation)

**Files:**
- Modify: `scripts/poster.py`
- Test: `tests/validate_skill.py`

**Interfaces:**
- Consumes: existing `SECTION_MAP`, `render_poster`, `PANELS_FOR`, `SOURCES_FOR`.
- Produces: `RICH_VIEWS` dict `{slug: {"template": <path-rel>, "map": {PANEL: (src, H2)}}}`; helper `panels_for_view(slug)` and `sources_for_view(slug)`. `render_poster` is retained unchanged for #14 (back-compat); new `#11`/`#12` entries live in `RICH_VIEWS` and are rendered by the same `render_poster` internals via a thin wrapper `render_view(slug, sources, template_text, meta)`.

Design note: `render_poster` already contains the generic projection (walk a `{PANEL: (src,H2)}` map, split each source, fill panels). We refactor so the map is looked up from a registry keyed by slug, and `#14` continues to work by keeping its entry in that registry. This keeps ONE projection implementation.

- [ ] **Step 1: Write the failing test**

```python
# ---- R-RICH-01: rich-view registry maps #11 and #12 to their own templates + section maps ----
@check("R-RICH-01: RICH_VIEWS registers #11 and #12 with a template path and a PANEL→(source,H2) map matching each template's slots; #14 poster still registered")
def t_rich_view_registry():
    p = _load_script("scripts/poster.py", "rich_reg_mod")
    assert hasattr(p, "RICH_VIEWS"), "poster.py must expose RICH_VIEWS"
    for slug in ("11-solution-infographic", "12-marketecture"):
        assert slug in p.RICH_VIEWS, f"{slug} must be a rich view"
        entry = p.RICH_VIEWS[slug]
        assert exists(entry["template"]), f"{slug} rich template missing: {entry['template']}"
        # PANEL_ slots in the template must equal the map's keys
        body = read(entry["template"])
        slots = {t for t in re.findall(r"\{\{([A-Z0-9_]+)\}\}", body) if t.startswith("PANEL_")}
        assert slots == set(entry["map"].keys()), f"{slug}: template slots {slots} != map {set(entry['map'].keys())}"
    # #14 still projects (either via RICH_VIEWS or the retained SECTION_MAP)
    assert p.PANELS_FOR("14-exec-infographic"), "#14 merged poster must still project"
```

Note: this test references `entry["template"]` paths that do not exist yet — Task 6/7 create them. So this test will FAIL now and stay failing until Task 7. To keep tasks independently green, split: **Task 5 adds the registry keyed to the templates but the templates are created FIRST as empty-but-valid stubs in this task's Step 3.** (See Step 3.)

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-RICH-01`
Expected: `FAIL  R-RICH-01...` with "poster.py must expose RICH_VIEWS"

- [ ] **Step 3: Create minimal valid rich templates (stubs) so the registry resolves**

Create `templates/solution-infographic.html` with the required PANEL slots (full styling comes in Task 6; this stub is valid HTML with the slots and the metadata tokens):

```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{{TITLE}} — Solution Infographic</title></head>
<body>
<section>{{PANEL_PROBLEM}}</section>
<section>{{PANEL_SOLUTION}}</section>
<section>{{PANEL_OUTCOMES}}</section>
<section>{{PANEL_MARKET}}</section>
<section>{{PANEL_BUILT_ON}}</section>
</body></html>
```

Create `templates/marketecture.html` (stub):

```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{{TITLE}} — Marketecture</title></head>
<body>
<section>{{PANEL_STORY}}</section>
<section>{{PANEL_PARTNER}}</section>
<section>{{PANEL_AGENT}}</section>
<section>{{PANEL_PLATFORM}}</section>
<section>{{PANEL_DATA}}</section>
<section>{{PANEL_TRUST}}</section>
</body></html>
```

- [ ] **Step 4: Add `RICH_VIEWS` + `render_view` to `scripts/poster.py`**

After the existing `SECTION_MAP` block, add:

```python
# Rich single-source views: an artifact whose PRIMARY <slug>.html is a bespoke projected layout
# (not the generic doc shell). Each maps PANEL_* slots -> (source_slug, exact H2 heading in that source).
# Keys must equal the {{PANEL_*}} tokens in the referenced template (guarded by R-RICH-01/R-POSTER-03).
RICH_VIEWS = {
    "11-solution-infographic": {
        "template": "templates/solution-infographic.html",
        "map": {
            "PANEL_PROBLEM":  ("11-solution-infographic", "The problem (why this matters)"),
            "PANEL_SOLUTION": ("11-solution-infographic", "The solution (what we built on Salesforce)"),
            "PANEL_OUTCOMES": ("11-solution-infographic", "Outcomes (the proof)"),
            "PANEL_MARKET":   ("11-solution-infographic", "Market & who it's for"),
            "PANEL_BUILT_ON": ("11-solution-infographic", "Built on Salesforce (the OEM/Embedded stack)"),
        },
    },
    "12-marketecture": {
        "template": "templates/marketecture.html",
        "map": {
            "PANEL_STORY":    ("12-marketecture", "The architecture story (top to bottom)"),
            "PANEL_PARTNER":  ("12-marketecture", "Partner solution layer (what the ISV builds & sells)"),
            "PANEL_AGENT":    ("12-marketecture", "Agent & experience layer (Agentforce, portals, channels)"),
            "PANEL_PLATFORM": ("12-marketecture", "Platform layer (the parent SKU + Salesforce clouds)"),
            "PANEL_DATA":     ("12-marketecture", "Data & integration layer (Data 360, MuleSoft, Zero-Copy, source systems)"),
            "PANEL_TRUST":    ("12-marketecture", "Trust & compliance (Einstein Trust Layer, data protection, regulatory posture)"),
        },
    },
}

def render_view(slug, sources, template_text, meta):
    """Project a rich single-source view. Mirrors render_poster but reads its PANEL->(src,H2) map
    from RICH_VIEWS[slug]. Returns (filled_html, unfilled_tokens)."""
    if slug not in RICH_VIEWS:
        raise ValueError(f"{slug} is not a registered rich view")
    section_map = RICH_VIEWS[slug]["map"]
    fills = {k: _html.escape(str(v)) for k, v in meta.items()}
    split_cache = {}
    for panel, (src, h2) in section_map.items():
        if src not in sources:
            raise ValueError(f"{slug}: panel {panel} needs source '{src}' but it was not provided")
        if src not in split_cache:
            split_cache[src] = split(sources[src])
        secs = split_cache[src]
        if h2 not in secs:
            raise ValueError(f"{slug}: section '{h2}' not found in source '{src}'")
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

def panels_for_view(slug):
    return set(RICH_VIEWS.get(slug, {}).get("map", {}).keys())

def sources_for_view(slug):
    return {src for (src, _h2) in RICH_VIEWS.get(slug, {}).get("map", {}).values()}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-RICH-01`
Expected: `PASS  R-RICH-01...`

- [ ] **Step 6: Confirm the #14 poster checks still pass**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-POSTER-0"`
Expected: R-POSTER-01/02/03 all `PASS` (SECTION_MAP and `render_poster` untouched).

- [ ] **Step 7: Commit**

```bash
python3 tests/validate_skill.py
git add scripts/poster.py templates/solution-infographic.html templates/marketecture.html tests/validate_skill.py
git commit -m "feat(poster): add RICH_VIEWS registry + render_view for #11/#12 (stub templates)"
```
Expected: `54/54 checks passed` (53 + R-RICH-01).

---

## Task 6: Light 3-column infographic template for #11 (Part 2A + 2C)

**Files:**
- Modify: `templates/solution-infographic.html` (replace stub with full light layout)
- Test: `tests/validate_skill.py`

**Interfaces:**
- Consumes: PANEL slots `PANEL_PROBLEM/SOLUTION/OUTCOMES/MARKET/BUILT_ON` (from Task 5 map) + metadata tokens `TITLE/LABEL/RELEASE/GENERATED_DATE/HOME_HREF`.

- [ ] **Step 1: Write the failing test**

```python
# ---- R-RICH-02: rich templates are light-scheme, carry metadata tokens + the shared table style ----
@check("R-RICH-02: #11/#12 rich templates use the SLDS light scheme (no dark body bg), carry all metadata tokens, and render cleanly from fixture sources")
def t_rich_render():
    p = _load_script("scripts/poster.py", "rich_render_mod")
    # fixture sources: reuse the effort's real markdown headings so the section map resolves
    md11 = ("# X — Solution Infographic\n> banner\n\n"
            "## The one-line story\nstory\n\n"
            "## The problem (why this matters)\nproblem body\n\n"
            "## The solution (what we built on Salesforce)\nsolution body\n\n"
            "## Outcomes (the proof)\noutcome body\n\n"
            "## Market & who it's for\nmarket body\n\n"
            "## Built on Salesforce (the OEM/Embedded stack)\nbuilt body\n\n"
            "---\n**Sources:** x\n**Confidence:** 0.6 — ok\n")
    tmpl = read(p.RICH_VIEWS["11-solution-infographic"]["template"])
    meta = {"TITLE":"X","LABEL":"Solution Infographic","RELEASE":"summer-26","GENERATED_DATE":"2026-07-01","HOME_HREF":"index.html"}
    out, unfilled = p.render_view("11-solution-infographic", {"11-solution-infographic": md11}, tmpl, meta)
    assert unfilled == [], f"unfilled tokens in #11 rich render: {unfilled}"
    assert "{{" not in out, "no raw token may survive the #11 rich render"
    assert "problem body" in out and "solution body" in out and "built body" in out, "panels not projected"
    # light scheme: body background must be light (not the #0f1117 dark ground)
    assert "#0f1117" not in out, "#11 must use the light scheme (no dark ground background)"
    assert "Salesforce Sans" in out, "#11 must carry the Salesforce Sans font stack"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-RICH-02`
Expected: `FAIL  R-RICH-02...` (the stub has no `Salesforce Sans` / may still pass token asserts but fails the font/scheme assert).

- [ ] **Step 3: Replace `templates/solution-infographic.html` with the full light layout**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}} — Solution Infographic</title>
<style>
  :root { --brand:#0176d3; --brand-dark:#014486; --navy:#032d60; --tint:#eef4ff;
          --panel:#f8fafc; --rule:#e5e5e5; --body:#181818; --white:#fff; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:'Salesforce Sans','Helvetica Neue',Arial,sans-serif; background:#f4f6f9; color:var(--body); line-height:1.5; }
  .info { max-width:1180px; margin:0 auto; background:var(--white); }
  .top-bar { height:6px; background:linear-gradient(90deg,var(--navy),var(--brand),#6bb7ff,#0b827c); }
  .header { padding:30px 44px; background:var(--navy); color:#fff; display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:16px; }
  .header .eyebrow { font-size:11px; font-weight:800; letter-spacing:0.18em; text-transform:uppercase; color:#9ec7f0; }
  .header h1 { font-size:30px; font-weight:800; margin-top:8px; }
  .header .meta { font-size:12px; color:#9ec7f0; }
  .header .meta a { color:#9ec7f0; text-decoration:none; }
  .cols { display:grid; grid-template-columns:1fr 1.25fr 1fr; }
  .col { padding:34px 36px; border-right:1px solid var(--rule); }
  .col:last-child { border-right:none; }
  .col-label { font-size:11px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase; margin-bottom:14px; display:flex; align-items:center; gap:8px; }
  .col-label::before { content:''; width:26px; height:3px; border-radius:2px; display:block; }
  .col-problem .col-label { color:#c62828; } .col-problem .col-label::before { background:#c62828; }
  .col-solution .col-label { color:var(--brand); } .col-solution .col-label::before { background:var(--brand); }
  .col-outcomes .col-label { color:#2e7d32; } .col-outcomes .col-label::before { background:#2e7d32; }
  .col-problem { background:#fdf5f5; } .col-solution { background:var(--tint); } .col-outcomes { background:#f2faf3; }
  .body { font-size:14px; line-height:1.6; color:#181818; }
  .body p { margin:0 0 12px; } .body ul { margin:0 0 12px; padding-left:20px; } .body li { margin-bottom:6px; }
  .body strong { color:var(--navy); } .body a { color:var(--brand); }
  .footer { display:grid; grid-template-columns:auto 1fr; gap:36px; padding:26px 44px; background:var(--panel); border-top:1px solid var(--rule); }
  .footer .flabel { font-size:11px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase; color:#444; }
  .footer .body { font-size:13px; }
  .built { padding:26px 44px; border-top:1px solid var(--rule); }
  .built .col-label { color:#0b827c; } .built .col-label::before { background:#0b827c; }
  /* shared light styled-table (mirror of document-shell / canvas) */
  table { width:100%; border-collapse:separate; border-spacing:0; border:1px solid var(--rule); border-radius:6px; overflow:hidden; font-size:0.85rem; margin:1rem 0; }
  th { background:var(--tint); color:var(--navy); text-align:left; padding:9px 12px; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid var(--rule); }
  td { padding:9px 12px; border-top:1px solid #eef2f7; vertical-align:top; }
  tr:nth-child(even) td { background:var(--panel); }
  @media print { *{ -webkit-print-color-adjust:exact; print-color-adjust:exact; } }
  @media (max-width:1000px) { .cols { grid-template-columns:1fr; } .col { border-right:none; border-bottom:1px solid var(--rule); } }
</style>
</head>
<body>
<div class="info">
  <div class="top-bar"></div>
  <header class="header">
    <div>
      <div class="eyebrow">{{LABEL}} · {{RELEASE}}</div>
      <h1>{{TITLE}}</h1>
    </div>
    <div class="meta">Generated {{GENERATED_DATE}} · <a href="{{HOME_HREF}}">← All artifacts</a></div>
  </header>
  <div class="cols">
    <section class="col col-problem"><div class="col-label">The Problem</div><div class="body">{{PANEL_PROBLEM}}</div></section>
    <section class="col col-solution"><div class="col-label">The Solution</div><div class="body">{{PANEL_SOLUTION}}</div></section>
    <section class="col col-outcomes"><div class="col-label">Outcomes</div><div class="body">{{PANEL_OUTCOMES}}</div></section>
  </div>
  <section class="built"><div class="col-label">Built on Salesforce</div><div class="body">{{PANEL_BUILT_ON}}</div></section>
  <footer class="footer">
    <div class="flabel">Market &amp; who it's for</div>
    <div class="body">{{PANEL_MARKET}}</div>
  </footer>
</div>
</body>
</html>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-RICH-02`
Expected: `PASS  R-RICH-02...`

- [ ] **Step 5: Manual visual check (browser)**

Render the real effort's #11 and open it:
```bash
python3 - <<'PY'
import sys; sys.path.insert(0,'scripts')
import poster
eff='/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/artifacts'
md=open(f'{eff}/11-solution-infographic.md').read()
tmpl=open('templates/solution-infographic.html').read()
meta={"TITLE":"Agentforce for Healthcare","LABEL":"Solution Infographic","RELEASE":"summer-26","GENERATED_DATE":"2026-07-01","HOME_HREF":"index.html"}
out,unf=poster.render_view("11-solution-infographic",{"11-solution-infographic":md},tmpl,meta)
open('/tmp/npi-11-preview.html','w').write(out); print("unfilled:",unf)
PY
open /tmp/npi-11-preview.html
```
Expected: unfilled `[]`; a light 3-column infographic (problem/solution/outcomes) with a built-on-Salesforce band and market footer. Confirm visually.

- [ ] **Step 6: Commit**

```bash
python3 tests/validate_skill.py
git add templates/solution-infographic.html tests/validate_skill.py
git commit -m "feat(#11): light SFDC 3-column solution infographic template"
```
Expected: `55/55 checks passed`.

---

## Task 7: Light layered marketecture template for #12 (Part 2A + 2C)

**Files:**
- Modify: `templates/marketecture.html` (replace stub with full light layered layout)
- Test: `tests/validate_skill.py` (extend R-RICH-02 to also render #12)

**Interfaces:**
- Consumes: PANEL slots `PANEL_STORY/PARTNER/AGENT/PLATFORM/DATA/TRUST` + metadata tokens.

- [ ] **Step 1: Extend R-RICH-02 to cover #12 (failing)**

Append to `t_rich_render`:

```python
    # #12 marketecture rich render
    md12 = ("# X — Solution Marketecture\n> banner\n\n"
            "## The architecture story (top to bottom)\nstory body\n\n"
            "## Partner solution layer (what the ISV builds & sells)\npartner body\n\n"
            "## Agent & experience layer (Agentforce, portals, channels)\nagent body\n\n"
            "## Platform layer (the parent SKU + Salesforce clouds)\nplatform body\n\n"
            "## Data & integration layer (Data 360, MuleSoft, Zero-Copy, source systems)\ndata body\n\n"
            "## Trust & compliance (Einstein Trust Layer, data protection, regulatory posture)\ntrust body\n\n"
            "---\n**Sources:** x\n**Confidence:** 0.6 — ok\n")
    tmpl12 = read(p.RICH_VIEWS["12-marketecture"]["template"])
    out12, unf12 = p.render_view("12-marketecture", {"12-marketecture": md12}, tmpl12, meta)
    assert unf12 == [], f"unfilled tokens in #12 rich render: {unf12}"
    assert "{{" not in out12, "no raw token may survive the #12 rich render"
    assert "partner body" in out12 and "trust body" in out12, "#12 layers not projected"
    assert "#0f1117" not in out12, "#12 must use the light scheme"
    assert "Salesforce Sans" in out12, "#12 must carry the Salesforce Sans font stack"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-RICH-02`
Expected: `FAIL  R-RICH-02...` with "#12 must use the light scheme" or a missing-panel assert.

- [ ] **Step 3: Replace `templates/marketecture.html` with the full light layered layout**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}} — Solution Marketecture</title>
<style>
  :root { --brand:#0176d3; --navy:#032d60; --tint:#eef4ff; --panel:#f8fafc; --rule:#e5e5e5; --body:#181818; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:'Salesforce Sans','Helvetica Neue',Arial,sans-serif; background:#f4f6f9; color:var(--body); line-height:1.5; }
  .page { max-width:1000px; margin:0 auto; padding:32px 24px; }
  .header { background:var(--navy); color:#fff; padding:26px 32px; border-radius:8px; margin-bottom:22px; }
  .header .eyebrow { font-size:11px; font-weight:800; letter-spacing:0.18em; text-transform:uppercase; color:#9ec7f0; }
  .header h1 { font-size:26px; font-weight:800; margin-top:6px; }
  .header .meta { font-size:12px; color:#9ec7f0; margin-top:10px; }
  .header .meta a { color:#9ec7f0; text-decoration:none; }
  .story { background:#fff; border:1px solid var(--rule); border-radius:8px; padding:20px 24px; margin-bottom:22px; }
  .story .lbl { font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#444; margin-bottom:10px; }
  .story .body { font-size:14px; line-height:1.6; }
  .stack { display:flex; flex-direction:column; border:1px solid var(--rule); border-radius:8px; overflow:hidden; }
  .layer { padding:18px 22px; border-bottom:1px solid rgba(255,255,255,0.25); }
  .layer:last-child { border-bottom:none; }
  .layer .llabel { font-size:0.66rem; font-weight:800; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px; }
  .layer .body { font-size:13.5px; line-height:1.55; }
  .layer .body p { margin:0 0 8px; } .layer .body p:last-child { margin:0; }
  .layer .body strong { font-weight:700; } .layer .body a { color:inherit; text-decoration:underline; }
  /* Partner (top) = brand; then descending shades to trust (bottom) = teal */
  .l-partner  { background:var(--tint);   color:var(--navy); } .l-partner .llabel { color:var(--brand); }
  .l-agent    { background:#0176d3; color:#fff; } .l-agent .llabel { color:#cfe6fb; }
  .l-platform { background:var(--navy);  color:#fff; } .l-platform .llabel { color:#9ec7f0; }
  .l-data     { background:#0b5cab; color:#fff; } .l-data .llabel { color:#cfe6fb; }
  .l-trust    { background:#0b827c; color:#fff; } .l-trust .llabel { color:#bdeae6; }
  .diagram { background:#fff; border:1px solid var(--rule); border-radius:8px; padding:20px 24px; margin-top:22px; text-align:center; }
  .diagram .lbl { font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#444; margin-bottom:12px; text-align:left; }
  .mermaid svg { max-width:100%; height:auto; }
  /* shared light styled-table */
  table { width:100%; border-collapse:separate; border-spacing:0; border:1px solid var(--rule); border-radius:6px; overflow:hidden; font-size:0.85rem; margin:1rem 0; }
  th { background:var(--tint); color:var(--navy); text-align:left; padding:9px 12px; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid var(--rule); }
  td { padding:9px 12px; border-top:1px solid #eef2f7; vertical-align:top; }
  tr:nth-child(even) td { background:var(--panel); }
  @media print { *{ -webkit-print-color-adjust:exact; print-color-adjust:exact; } }
</style>
</head>
<body>
<div class="page">
  <header class="header">
    <div class="eyebrow">{{LABEL}} · {{RELEASE}}</div>
    <h1>{{TITLE}} — Solution Marketecture</h1>
    <div class="meta">Generated {{GENERATED_DATE}} · <a href="{{HOME_HREF}}">← All artifacts</a></div>
  </header>
  <div class="story"><div class="lbl">The architecture story</div><div class="body">{{PANEL_STORY}}</div></div>
  <div class="stack">
    <div class="layer l-partner"><div class="llabel">Partner Solution Layer</div><div class="body">{{PANEL_PARTNER}}</div></div>
    <div class="layer l-agent"><div class="llabel">Agent &amp; Experience Layer</div><div class="body">{{PANEL_AGENT}}</div></div>
    <div class="layer l-platform"><div class="llabel">Platform Layer</div><div class="body">{{PANEL_PLATFORM}}</div></div>
    <div class="layer l-data"><div class="llabel">Data &amp; Integration Layer</div><div class="body">{{PANEL_DATA}}</div></div>
    <div class="layer l-trust"><div class="llabel">Trust &amp; Compliance</div><div class="body">{{PANEL_TRUST}}</div></div>
  </div>
</div>
</body>
</html>
```

Note: #12's rich view shows the layered CSS stack. The live Mermaid diagram (the `{{MARKETECTURE_DIAGRAM}}` in the markdown) is intentionally NOT in this projected view — the CSS stack IS the visual. (If the diagram is wanted too, that is a BACKLOG follow-up; keeping it out avoids a second Mermaid-in-projection code path here.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-RICH-02`
Expected: `PASS  R-RICH-02...`

- [ ] **Step 5: Manual visual check (browser)**

```bash
python3 - <<'PY'
import sys; sys.path.insert(0,'scripts')
import poster
eff='/Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/artifacts'
md=open(f'{eff}/12-marketecture.md').read()
tmpl=open('templates/marketecture.html').read()
meta={"TITLE":"Agentforce for Healthcare","LABEL":"Marketecture","RELEASE":"summer-26","GENERATED_DATE":"2026-07-01","HOME_HREF":"index.html"}
out,unf=poster.render_view("12-marketecture",{"12-marketecture":md},tmpl,meta)
open('/tmp/npi-12-preview.html','w').write(out); print("unfilled:",unf)
PY
open /tmp/npi-12-preview.html
```
Expected: unfilled `[]`; a light layered stack (Partner → Agent → Platform → Data → Trust). Confirm visually.

- [ ] **Step 6: Commit**

```bash
python3 tests/validate_skill.py
git add templates/marketecture.html tests/validate_skill.py
git commit -m "feat(#12): light layered marketecture template"
```
Expected: `55/55 checks passed` (R-RICH-02 extended, not a new check).

---

## Task 8: Mermaid diagram overflow/clipping fix (Part 2B)

**Files:**
- Modify: `templates/document-shell.html`
- Modify: `scripts/slide_deck.py`
- Modify: `refs/mermaid-diagrams.md`
- Test: `tests/validate_skill.py`

**Interfaces:**
- Consumes: the existing `mermaid.initialize({ startOnLoad: true, ... })` calls.
- Produces: `flowchart: { useMaxWidth: true, htmlLabels: true }` config + `.mermaid svg { max-width:100%; height:auto; }` CSS in the shell; matching config in the deck.

- [ ] **Step 1: Write the failing test**

```python
# ---- R-MERMAID-02: render surfaces size the injected SVG to the container (no clipping) ----
@check("R-MERMAID-02: document-shell + slide_deck set flowchart useMaxWidth and constrain .mermaid svg width so long-label diagrams don't clip")
def t_mermaid_no_clip():
    shell = read("templates/document-shell.html")
    assert "useMaxWidth" in shell, "shell mermaid.initialize must set flowchart useMaxWidth"
    assert ".mermaid svg" in shell and "max-width" in shell.split(".mermaid svg")[1][:80], \
        "shell must constrain .mermaid svg to max-width:100%"
    sd = read("scripts/slide_deck.py")
    assert "useMaxWidth" in sd, "slide_deck mermaid.initialize must set flowchart useMaxWidth"
    ref = read("refs/mermaid-diagrams.md").lower()
    assert "usemaxwidth" in ref or "max-width" in ref, "mermaid ref must document the useMaxWidth/scaling fix"
    assert "short" in ref and "label" in ref, "mermaid ref must advise short node labels"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-MERMAID-02`
Expected: `FAIL  R-MERMAID-02...` with "shell mermaid.initialize must set flowchart useMaxWidth"

- [ ] **Step 3: Update `templates/document-shell.html`**

Replace the mermaid init script (lines 61-64):

```html
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({ startOnLoad: true, securityLevel: "loose" });
</script>
```

with:

```html
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({ startOnLoad: true, securityLevel: "loose",
                       flowchart: { useMaxWidth: true, htmlLabels: true, wrappingWidth: 220 } });
</script>
```

And add to the `<style>` block, right after the existing `.content pre.mermaid` rule (line 37):

```css
    .content pre.mermaid { background: #fff; border: none; text-align: center; }
    .content .mermaid svg { max-width: 100%; height: auto; }
```

(The first line already exists — add only the second `.mermaid svg` line after it.)

- [ ] **Step 4: Update `scripts/slide_deck.py`**

Find the `mermaid.initialize(` call in the deck's HTML template string and apply the same flowchart config. Locate it:

```bash
grep -n "mermaid.initialize" scripts/slide_deck.py
```

Replace `mermaid.initialize({ startOnLoad: true, securityLevel: "loose" });` (or whatever the current args are) with:

```javascript
mermaid.initialize({ startOnLoad: true, securityLevel: "loose", flowchart: { useMaxWidth: true, htmlLabels: true, wrappingWidth: 220 } });
```

Also ensure the deck CSS constrains `.mermaid svg` — add `.mermaid svg{max-width:100%;height:auto;}` to the deck's style block (find the `<style>` in `build_deck`).

- [ ] **Step 5: Update `refs/mermaid-diagrams.md`**

Add a new subsection before "## SVG / PNG for decks":

```markdown
## Rendering wide diagrams (no clipping)

Long node labels can overflow their container and clip in the browser view. Two guards:

1. **Render-surface config.** `document-shell.html` and `slide_deck.py` initialise Mermaid with
   `flowchart: { useMaxWidth: true, htmlLabels: true, wrappingWidth: 220 }` and constrain the
   injected SVG with `.mermaid svg { max-width: 100%; height: auto; }` so a diagram scales to its
   card instead of clipping.
2. **Authoring.** Keep node labels short. Break a long `·`-joined list across `<br/>` lines rather
   than one wide line (e.g. `Data 360 · MuleSoft<br/>Zero-Copy · EHR/FHIR`), so no single label is
   wider than the container.
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-MERMAID-02`
Expected: `PASS  R-MERMAID-02...`

- [ ] **Step 7: Confirm the existing shell + deck + mermaid-ref checks still pass**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-HTML-01|R-SLIDE-01|R-MERMAID-01"`
Expected: all `PASS`.

- [ ] **Step 8: Manual visual check (browser) — the actual bug**

Re-render the effort's #00 (longest-label diagram) through the doc shell and confirm the diagram no longer clips:
```bash
python3 scripts/md_to_html.py \
  --md /Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/artifacts/00-executive-summary.md \
  --shell templates/document-shell.html --out /tmp/npi-00-preview.html \
  --title "Agentforce for Healthcare" --label "Executive Summary" --release "summer-26" --date "2026-07-01" --home "index.html"
open /tmp/npi-00-preview.html
```
Expected: the status-rollup diagram fits the content column, no text cut off at node edges.

- [ ] **Step 9: Commit**

```bash
python3 tests/validate_skill.py
git add templates/document-shell.html scripts/slide_deck.py refs/mermaid-diagrams.md tests/validate_skill.py
git commit -m "fix(render): constrain Mermaid SVG width + flowchart useMaxWidth so long-label diagrams don't clip"
```
Expected: `56/56 checks passed`.

---

## Task 9: Consistent light styled-table across surfaces (Part 2C)

**Files:**
- Modify: `templates/document-shell.html` (table CSS → light scheme)
- Modify: `scripts/canvas.py` (blockers table → same light scheme)
- Test: `tests/validate_skill.py`

**Interfaces:**
- Produces: identical table treatment (light tint header, navy text, rounded 1px border, zebra rows) in the doc shell, both rich templates (Tasks 6/7 already use it), and the canvas.

Decision: use the **light tint header** (`--tint` bg, `--navy` text) as the single standard — matches the rich templates built in Tasks 6/7 and the SLDS light scheme the user asked for. This changes the doc shell's current navy-header tables and the canvas's navy-header blockers table to the light standard.

- [ ] **Step 1: Write the failing test**

```python
# ---- R-TABLE-01: one consistent light styled-table treatment across shell + rich templates + canvas ----
@check("R-TABLE-01: doc shell, both rich templates, and the canvas use the SAME light styled-table (tint header, navy text) — no navy-background table headers remain")
def t_table_consistency():
    shell = read("templates/document-shell.html")
    canvas = read("scripts/canvas.py")
    info = read("templates/solution-infographic.html")
    mkt = read("templates/marketecture.html")
    # the light standard: th uses the tint background + navy text, NOT a navy fill
    for name, body in [("document-shell", shell), ("solution-infographic", info), ("marketecture", mkt)]:
        assert "#eef4ff" in body or "var(--tint)" in body, f"{name}: table header must use the tint background"
    # the doc shell's content-table header must no longer be a navy fill
    # (find the '.content th' rule and confirm it is not 'background: var(--navy)' / '#032d60')
    m = re.search(r"\.content th\s*\{[^}]*\}", shell)
    assert m, "shell must define a .content th rule"
    th_rule = m.group(0)
    assert "#032d60" not in th_rule and "var(--navy)" not in th_rule.split("color")[0], \
        "shell .content th must not use a navy BACKGROUND (light scheme: tint bg, navy text)"
    # canvas blockers table also moves to the light header
    mb = re.search(r"table\.blockers th\s*\{[^}]*\}", canvas)
    assert mb, "canvas must define a table.blockers th rule"
    assert "#032d60" not in mb.group(0).split("color")[0], \
        "canvas blockers th must not use a navy BACKGROUND (light scheme)"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-TABLE-01`
Expected: `FAIL  R-TABLE-01...` (shell + canvas currently use navy `#032d60` header backgrounds).

- [ ] **Step 3: Update `templates/document-shell.html` table CSS**

Replace the current table rules (lines 29-31):

```css
    .content table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.9rem; }
    .content th { background: var(--navy); color: #fff; text-align: left; padding: 7px 10px; }
    .content td { border: 1px solid var(--rule); padding: 6px 10px; }
```

with:

```css
    .content table { border-collapse: separate; border-spacing: 0; width: 100%; margin: 1rem 0; font-size: 0.9rem; border: 1px solid var(--rule); border-radius: 6px; overflow: hidden; }
    .content th { background: var(--tint); color: var(--navy); text-align: left; padding: 9px 11px; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid var(--rule); }
    .content td { border-top: 1px solid #eef2f7; padding: 8px 11px; vertical-align: top; }
    .content tr:nth-child(even) td { background: var(--panel); }
```

Note: `--tint` (`#f0f5fc`) and `--panel` (`#f8fafc`) are already declared in the shell's `:root` (lines 8-11). Confirm `--tint` value; if the shell's `--tint` is `#f0f5fc`, that is fine (still light). The test accepts `var(--tint)`.

- [ ] **Step 4: Update `scripts/canvas.py` blockers table CSS**

Replace (lines 190-191):

```python
 table.blockers th {{ background:#032d60; color:#fff; text-align:left; padding:7px 10px; }}
 table.blockers td {{ border:1px solid #e5e5e5; padding:6px 10px; }}
```

with:

```python
 table.blockers {{ border:1px solid #e5e5e5; border-radius:6px; overflow:hidden; border-spacing:0; }}
 table.blockers th {{ background:#eef4ff; color:#032d60; text-align:left; padding:9px 11px; font-size:0.76rem; text-transform:uppercase; letter-spacing:0.04em; border-bottom:1px solid #e5e5e5; }}
 table.blockers td {{ border-top:1px solid #eef2f7; padding:8px 11px; }}
 table.blockers tr:nth-child(even) td {{ background:#f8fafc; }}
```

(Keep the existing `table.blockers {{ border-collapse... }}` line replaced by the new border-spacing rule above; ensure no duplicate `border-collapse:collapse` remains — the new rule uses `border-spacing:0` with `border-collapse` defaulting to separate.)

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-TABLE-01`
Expected: `PASS  R-TABLE-01...`

- [ ] **Step 6: Confirm canvas + shell structural checks still pass**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-CANVAS-01|R-HTML-01"`
Expected: both `PASS`.

- [ ] **Step 7: Manual visual check**

Re-render any table-bearing artifact (e.g. #07 add-on tiering) and the canvas; confirm tables match the light scheme.
```bash
python3 scripts/md_to_html.py \
  --md /Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/artifacts/07-addon-tiering.md \
  --shell templates/document-shell.html --out /tmp/npi-07-preview.html \
  --title "Agentforce for Healthcare" --label "Add-On Tiering" --release "summer-26" --date "2026-07-01" --home "index.html"
open /tmp/npi-07-preview.html
```
Expected: light tint header, zebra rows, rounded border — matching #11/#12.

- [ ] **Step 8: Commit**

```bash
python3 tests/validate_skill.py
git add templates/document-shell.html scripts/canvas.py tests/validate_skill.py
git commit -m "style(tables): unify on the light SFDC styled-table (tint header, zebra rows) across shell + canvas"
```
Expected: `57/57 checks passed`.

---

## Task 10: Wire the rich views into the render path + document it

**Files:**
- Modify: `refs/render-and-canvas.md`
- Test: `tests/validate_skill.py` (extend R-RENDER-REF-01)

**Interfaces:**
- Consumes: `poster.RICH_VIEWS`, `poster.render_view` (Task 5).
- Produces: documentation of how #11/#12 get their PRIMARY `<slug>.html` from the rich view (not the doc shell), so a future render run does the right thing.

- [ ] **Step 1: Extend the ref check (failing)**

Append to `t_render_canvas_ref`:

```python
    assert "rich view" in body or "rich_views" in body or "render_view" in body, \
        "render-canvas ref must document the #11/#12 rich-view render path"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-RENDER-REF-01`
Expected: `FAIL  R-RENDER-REF-01...` with "must document the #11/#12 rich-view render path"

- [ ] **Step 3: Document the rich-view path in `refs/render-and-canvas.md`**

Add a new section after "## 1b. The merged poster view (#14)":

```markdown
## 1c. Rich single-source views (#11, #12)

`11-solution-infographic` and `12-marketecture` render their PRIMARY `<slug>.html` from a bespoke
light-scheme layout, NOT the generic document shell. `poster.RICH_VIEWS[slug]` maps each
`{{PANEL_*}}` slot to a `(source_slug, H2)` pair in the artifact's own markdown;
`poster.render_view(slug, sources, template_text, meta)` projects the markdown sections into the
template (`templates/solution-infographic.html` / `templates/marketecture.html`). The markdown stays
the source of truth; the rich HTML is a derived projection (same pattern as the #14 merged poster).
The section→panel contract keys on the exact H2 headings — if an H2 is reworded in #11/#12, update
`RICH_VIEWS` (guarded by R-RICH-01). #11 is a light 3-column problem/solution/outcomes infographic;
#12 is a light layered Partner→Agent→Platform→Data→Trust stack. Neither gets a `-poster.html` (the
`-poster.html` suffix remains #14-only).
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-RENDER-REF-01`
Expected: `PASS  R-RENDER-REF-01...`

- [ ] **Step 5: Full suite green + commit**

```bash
python3 tests/validate_skill.py
git add refs/render-and-canvas.md tests/validate_skill.py
git commit -m "docs(render): document the #11/#12 rich single-source view render path"
```
Expected: `57/57 checks passed`.

---

## Task 11: Final validation, skill-forge self-audit, and hook check

**Files:**
- Run-only (no edits unless a check surfaces a gap).

- [ ] **Step 1: Run the full suite**

Run: `python3 tests/validate_skill.py`
Expected: `57/57 checks passed` (50 baseline + R-TPL-05, R-TPL-06, R-CANVAS-04, R-RICH-01, R-MERMAID-02, R-TABLE-01; R-RICH-02 and the ref/canvas extensions fold into existing checks).

- [ ] **Step 2: Confirm the pre-commit hook runs clean**

Run: `.githooks/pre-commit` (or make a trivial commit and let husky/the hook run).
Expected: the hook invokes `validate_skill.py` and passes.

- [ ] **Step 3: Count-drift guard**

Run: `python3 tests/validate_skill.py 2>&1 | grep R-DOC-01`
Expected: `PASS` (the "15 deliverables" claims are unchanged — no new artifact slugs; no doc hardcodes a check count).

- [ ] **Step 4: Regenerate the real effort end-to-end (manual, optional but recommended)**

Regenerate #11/#12 via the rich views and re-render the rest through the (now light-table) shell, then reassemble the canvas, and open it:
```bash
# (render #11/#12 rich views to the effort canvas dir, render the doc-shell set, reassemble canvas)
# then:
open /Users/bstauber/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/canvas/index.html
```
Expected: #11 and #12 cards open the new light rich layouts; tables consistent; diagrams no longer clip; #00 shows the Messaging Hierarchy and #01 shows the Key Use Cases table.

- [ ] **Step 5: Final commit (if Step 4 produced regenerated effort output)**

The effort output lives OUTSIDE the skill repo (`ps-npi-efforts/`), so it is not committed to the skill. No skill commit needed here unless a doc gap was fixed.

---

## Self-Review

**Spec coverage:**
- 1A Key Use Cases table → Task 1 ✓
- 1B Messaging Hierarchy → Task 3 ✓
- 1C highlight-card mentions → Task 4 ✓
- 1D Additional-resources grammar → Task 2 ✓
- 2A rich HTML #11/#12 → Tasks 5, 6, 7, 10 ✓
- 2B diagram clipping → Task 8 ✓
- 2C consistent light tables → Task 9 (and Tasks 6/7 build the same table style into the rich templates) ✓

**Type/name consistency:**
- `render_view(slug, sources, template_text, meta)` defined in Task 5, used in Tasks 6, 7 tests, and Task 10 docs — consistent signature.
- `RICH_VIEWS[slug]["template"]` / `["map"]` shape defined in Task 5, read in Tasks 6/7 tests and R-RICH-01.
- PANEL slot names: #11 = `PANEL_PROBLEM/SOLUTION/OUTCOMES/MARKET/BUILT_ON`; #12 = `PANEL_STORY/PARTNER/AGENT/PLATFORM/DATA/TRUST` — identical in the stub (Task 5), the full template (Tasks 6/7), and the map (Task 5). ✓
- New tokens: `{{KEY_USE_CASES_TABLE}}` (Task 1), `{{MESSAGING_HIERARCHY}}` (Task 3) — both UPPER_SNAKE, both real fill slots.

**Check-count arithmetic:** baseline 50 → +6 new named checks (R-TPL-05, R-TPL-06, R-CANVAS-04, R-RICH-01, R-MERMAID-02, R-TABLE-01) = 56; R-RICH-02 is a new check too → 57. R-RENDER-REF-01 and t_use_case_table/t_rich_render extensions are additions to existing checks, not new checks. Final expected: **57/57**.
