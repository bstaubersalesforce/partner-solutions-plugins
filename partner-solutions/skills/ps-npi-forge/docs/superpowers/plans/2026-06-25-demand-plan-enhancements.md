# Demand Plan & GTM Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add four NPI-tool enhancements to ps-npi-forge — a required-licensing summary (#06), a standard ISV add-on catalog (#07), a new demand-plan grid (#13), and a new exec infographic (#14) — growing the artifact family 13 → 15.

**Architecture:** ps-npi-forge is a stdlib-only, registry-driven skill. The artifact family is defined by `ARTIFACT_REGISTRY` (duplicated in `scripts/manifest.py` and `tests/validate_skill.py`, kept in parity by R-MANIFEST-06). Each artifact is a `templates/<slug>.md` skeleton of `{{UPPER_SNAKE}}` tokens; `scripts/render.py` substitutes tokens; `scripts/md_to_html.py` renders to HTML with diagram/price tokens treated as render-safe "pending" markers via `INTENTIONAL_PLACEHOLDERS`. The validation suite `tests/validate_skill.py` is registry-derived: adding a registry slug + its template + its diagram placeholder + updating the hardcoded doc counts keeps every rule green. This plan moves all those touchpoints in lockstep.

**Tech Stack:** Python 3 stdlib only. Markdown templates. Mermaid (SLDS-themed) diagrams. No new dependencies.

## Global Constraints

- **Stdlib-only.** No third-party imports in any `scripts/` or `tests/` change. (`scripts/render.py` docstring + repo convention.)
- **Registry parity.** `ARTIFACT_REGISTRY` MUST be byte-identical between `scripts/manifest.py` and `tests/validate_skill.py` (enforced by R-MANIFEST-06).
- **Pricing out of scope.** Price/discount cells are ALWAYS the literal tokens `{{PRICE_PENDING}}` / `{{DISCOUNT_PENDING}}` — never a number.
- **Template shared convention (R-TPL-02).** Every `templates/<slug>.md` MUST contain, verbatim: the VOICE comment, the line `> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}`, the line `> {{GAP_BANNER}}`, and the footer block `---\n**Sources:** {{SOURCES}}\n**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}`. Note: the `·` and `—` characters are literal.
- **Token hygiene (R-TEST-02).** Every `{{TOKEN}}` is `[A-Z0-9_]+`.
- **Diagram tokens** end in `_DIAGRAM` and MUST be added to `INTENTIONAL_PLACEHOLDERS` in `scripts/md_to_html.py` or a render-safe pass will hard-fail.
- **Count claims (R-DOC-01).** Any "the/all N artifacts|deliverables" string in SKILL.md/README/refs MUST equal `len(ARTIFACT_REGISTRY)`. After this change that is **15**.
- **Run the suite** with `python3 tests/validate_skill.py` (exit 0 = all pass). The pre-commit hook runs it too.
- **Branch:** `npi-demand-plan-enhancements` (already created off `main`).

---

### Task 1: Register the two new artifacts (registry parity)

This is the keystone: it makes R-TPL-01 (template-per-slug), R-MANIFEST-01/05, and R-DOC-01 demand the rest of the work. Do this first so the suite goes red and guides the remaining tasks.

**Files:**
- Modify: `scripts/manifest.py:12-17` (`ARTIFACT_REGISTRY`)
- Modify: `tests/validate_skill.py:31-36` (`ARTIFACT_REGISTRY`)

**Interfaces:**
- Produces: `ARTIFACT_REGISTRY` now ends with `"13-demand-plan", "14-exec-infographic"` in both files. Later tasks rely on these exact slugs.

- [ ] **Step 1: Add the two slugs in `scripts/manifest.py`.** Replace the registry list (lines 12-17) so it ends with the two new entries:

```python
ARTIFACT_REGISTRY = [
    "00-executive-summary", "01-brief", "02-slide-summary", "03-internal-enablement",
    "04-internal-faq", "05-external-faq", "06-license-entitlements", "07-addon-tiering",
    "08-setup-guide", "09-org-provisioning-validation", "10-partner-profile-pov",
    "11-solution-infographic", "12-marketecture", "13-demand-plan", "14-exec-infographic",
]
```

- [ ] **Step 2: Mirror the identical list in `tests/validate_skill.py`** (lines 31-36) — same 15 entries, same order. (R-MANIFEST-06 asserts byte-parity.)

- [ ] **Step 3: Run the suite to confirm it now fails for the expected reasons**

Run: `python3 tests/validate_skill.py`
Expected: FAIL — R-TPL-01 ("artifact templates missing: templates/13-demand-plan.md, templates/14-exec-infographic.md"), R-MANIFEST-05 (fixture missing the new slugs), R-DOC-01 (docs say 13, registry has 15). These red checks are the worklist for Tasks 2-8.

- [ ] **Step 4: Commit**

```bash
git add scripts/manifest.py tests/validate_skill.py
git commit -m "feat(registry): add 13-demand-plan and 14-exec-infographic slugs"
```

---

### Task 2: Item 3 — required-licensing summary in #06

**Files:**
- Modify: `templates/06-license-entitlements.md` (insert a section after the parent/product line, before `## Entitlement composition`)

**Interfaces:**
- Produces: new token `{{REQUIRED_LICENSING_TABLE}}` in #06. Task 7 adds it to the render fill-set test; Task 6 references the required SKUs in the demand grid.

- [ ] **Step 1: Add the summary section.** In `templates/06-license-entitlements.md`, immediately after the line `**Pinned Org62 Product2:** {{PINNED_PRODUCT}} ({{PINNED_PRODUCT_CODE}})` and before `## Entitlement composition (from Org62 ...)`, insert:

```markdown

## Required licensing summary

The required licensing for {{PRODUCT_NAME}}, as captured from the source NPI table. This is the
human-authored "what a partner must license" summary; the Org62-derived composition below substantiates it.

{{REQUIRED_LICENSING_TABLE}}
```

- [ ] **Step 2: Verify the template still satisfies R-TPL-02 + token hygiene**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-TPL-02|R-TEST-02"`
Expected: both PASS (the new token is UPPER_SNAKE; the header/footer blocks are untouched).

- [ ] **Step 3: Commit**

```bash
git add templates/06-license-entitlements.md
git commit -m "feat(#06): add required-licensing summary table section"
```

---

### Task 3: Item 1 — standard ISV add-on catalog in #07

**Files:**
- Modify: `templates/07-addon-tiering.md` (append a section after the existing `## SKU reference ...` table, before the `## Tier decision (diagram)` section)

**Interfaces:**
- Produces: new token `{{STANDARD_ISV_ADDONS}}` in #07. Task 6 references this catalog in the demand grid's "Standard add-ons" column. Task 7 adds it to the render fill-set test.

- [ ] **Step 1: Add the catalog section.** In `templates/07-addon-tiering.md`, after the SKU-reference table block (the table that ends the `## SKU reference (which SKUs/add-ons exist)` section) and before `## Tier decision (diagram)`, insert:

```markdown

## Standard ISV add-ons partners may attach

Distinct from the Required/Recommended/Optional tiers above (which are *this product's own* add-on
dependencies), this is the **cross-sell menu** — standard ISV add-on SKUs partners commonly attach on
top of {{PRODUCT_NAME}}. Pricing is out of scope.

| Standard add-on | Why relevant to this partner motion | Typical attach trigger | Price |
|-----------------|--------------------------------------|------------------------|-------|
| {{STANDARD_ISV_ADDONS}} | | | {{PRICE_PENDING}} |
```

- [ ] **Step 2: Verify R-TPL-02 + token hygiene still pass**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-TPL-02|R-TEST-02"`
Expected: both PASS.

- [ ] **Step 3: Commit**

```bash
git add templates/07-addon-tiering.md
git commit -m "feat(#07): add standard ISV add-on cross-sell catalog section"
```

---

### Task 4: Item 4 — new exec infographic template (#14)

Done before #13 because #13's "diagram" verification reuses the same pattern and #14 is the simpler new template.

**Files:**
- Create: `templates/14-exec-infographic.md`

**Interfaces:**
- Consumes: registry slug `14-exec-infographic` (Task 1).
- Produces: tokens `{{VISION_PANEL}}`, `{{VALUE_PROP_PANEL}}`, `{{USE_CASES_PANEL}}`, `{{IDEAL_PARTNERS_PANEL}}`, `{{TAM_PANEL}}`, `{{EXEC_DIAGRAM}}` (plus the shared `{{PRODUCT_NAME}}/{{STATUS}}/{{CONFIDENCE}}/{{CONFIDENCE_RATIONALE}}/{{GAP_BANNER}}/{{SOURCES}}`). Task 7 fills them; Task 8 adds `EXEC_DIAGRAM` to `INTENTIONAL_PLACEHOLDERS`.

- [ ] **Step 1: Create the template file** with the exact shared-convention structure (R-TPL-02 requires the header/gap/footer lines verbatim):

```markdown
<!-- VOICE: narrative — first-person exec/architect McKinsey register; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — Executive Overview

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

## Vision
{{VISION_PANEL}}

## Value proposition
{{VALUE_PROP_PANEL}}

## Key use cases
{{USE_CASES_PANEL}}

## Ideal partners
{{IDEAL_PARTNERS_PANEL}}

## Market opportunity (TAM)
{{TAM_PANEL}}

## Executive overview (diagram)
{{EXEC_DIAGRAM}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 2: Run R-TPL-01 + R-TPL-02 for #14**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-TPL-01|R-TPL-02"`
Expected: R-TPL-01 no longer lists `templates/14-exec-infographic.md` as missing; R-TPL-02 passes for #14. (R-TPL-01 will still list #13 as missing — that's Task 5.)

- [ ] **Step 3: Commit**

```bash
git add templates/14-exec-infographic.md
git commit -m "feat(#14): add exec-infographic template (vision/value/use-cases/partners/TAM)"
```

---

### Task 5: Item 2 — new demand-plan grid template (#13)

**Files:**
- Create: `templates/13-demand-plan.md`

**Interfaces:**
- Consumes: registry slug `13-demand-plan` (Task 1).
- Produces: tokens `{{FRAMEWORK_INTRO}}`, `{{DEMAND_GRID}}`, `{{SEGMENT_TAM_BASIS}}`, `{{CONDITIONAL_ADDONS_NOTE}}`, `{{DEMAND_DIAGRAM}}`. Task 7 fills them; Task 8 adds `DEMAND_DIAGRAM` to `INTENTIONAL_PLACEHOLDERS`; Task 9 adds a targeted structure assert.

- [ ] **Step 1: Create the template file.** The grid carries the three required SKU-bundle column labels literally (Task 9 asserts they survive future edits):

```markdown
<!-- VOICE: narrative — first-person exec/architect McKinsey register; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — Demand Plan Framework

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

## How to use this framework
{{FRAMEWORK_INTRO}}

## The demand grid

Rows are identified segments (each with a TAM estimate and an Ideal-Partner-Profile fit indicator from
#10). The SKU-bundle columns are **Core / Required SKUs**, **Standard add-ons**, and **Conditional
(NPI-dependent) add-ons**.

| Segment | TAM (est.) | IPP-fit | Core / Required SKUs | Standard add-ons | Conditional (NPI-dependent) add-ons |
|---------|-----------|---------|----------------------|------------------|-------------------------------------|
| {{DEMAND_GRID}} | | | | | |

## Segment & TAM basis
{{SEGMENT_TAM_BASIS}}

## Conditional (NPI-dependent) add-ons — inclusion rule

A cell in the **Conditional (NPI-dependent) add-ons** column is filled **only when the NPI process has
identified that add-on as required** for that segment (for example, the CC / CC+ elements for
Agentforce for Healthcare). Otherwise the cell stays empty — do not populate it speculatively.

{{CONDITIONAL_ADDONS_NOTE}}

## Demand logic (diagram)
{{DEMAND_DIAGRAM}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 2: Run R-TPL-01 + R-TPL-02**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-TPL-01|R-TPL-02"`
Expected: both PASS now (every registry slug has a template; both new templates carry the shared convention).

- [ ] **Step 3: Commit**

```bash
git add templates/13-demand-plan.md
git commit -m "feat(#13): add demand-plan grid template (segments x SKU-bundle, IPP+TAM)"
```

---

### Task 6: Manifest template + fixture seed the 15 artifacts

R-MANIFEST-05 requires both `templates/manifest.yaml` and `tests/fixtures/manifest/sample-manifest.yaml` to list exactly the registry set. `new_effort()` already seeds from `ARTIFACT_REGISTRY` programmatically (so R-MANIFEST-01 passes once Task 1 lands), but the two on-disk YAML files are static and must be extended.

**Files:**
- Modify: `templates/manifest.yaml` (append two artifact blocks)
- Modify: `tests/fixtures/manifest/sample-manifest.yaml` (append two artifact blocks)

**Interfaces:**
- Consumes: the manifest block shape (status/confidence/rationale/sources/placeholders/loops×4/last_generated) — copy an existing block verbatim, changing only the slug key.

- [ ] **Step 1: Append the #13 and #14 blocks to `templates/manifest.yaml`.** After the `12-marketecture:` block (the file currently ends there), add — matching the existing block indentation exactly:

```yaml
  13-demand-plan:
    status: pending
    confidence: 0.0
    rationale: ""
    sources: []
    placeholders:
    loops:
      claim_verification:
        verdict: ""
        note: ""
      completeness:
        verdict: ""
        note: ""
      uncertainty:
        verdict: ""
        note: ""
      partner_lens:
        verdict: ""
        note: ""
    last_generated: ""
  14-exec-infographic:
    status: pending
    confidence: 0.0
    rationale: ""
    sources: []
    placeholders:
    loops:
      claim_verification:
        verdict: ""
        note: ""
      completeness:
        verdict: ""
        note: ""
      uncertainty:
        verdict: ""
        note: ""
      partner_lens:
        verdict: ""
        note: ""
    last_generated: ""
```

- [ ] **Step 2: Append the same two blocks to `tests/fixtures/manifest/sample-manifest.yaml`.** Open the file first to match its exact field values/indentation (it may carry non-default status/confidence for other artifacts — the two NEW blocks should use the `pending`/`0.0` shape above, appended after its last artifact block).

- [ ] **Step 3: Run the manifest checks**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-MANIFEST-05|R-MANIFEST-01"`
Expected: both PASS (fixture + new_effort both cover all 15 slugs; `load()` round-trips the new blocks).

- [ ] **Step 4: Commit**

```bash
git add templates/manifest.yaml tests/fixtures/manifest/sample-manifest.yaml
git commit -m "feat(manifest): seed 13-demand-plan and 14-exec-infographic blocks"
```

---

### Task 7: Render fill-set coverage (R-RENDER-01)

R-RENDER-01 already iterates every `templates/*.md`, extracts its tokens, fills them all with `"X"`, and asserts zero survivors. So the new tokens are auto-covered by the existing test the moment the templates exist — **but** the diagram tokens would survive a *real* render-safe pass unless added to `INTENTIONAL_PLACEHOLDERS` (Task 8). This task confirms R-RENDER-01 is green and adds an explicit assertion that the four new content tokens are present in the templates (so a future token rename can't silently drop them).

**Files:**
- Modify: `tests/validate_skill.py` (extend the R-RENDER-01 check function `t_render`, near line 370-390)

**Interfaces:**
- Consumes: tokens from Tasks 2-5 (`REQUIRED_LICENSING_TABLE`, `STANDARD_ISV_ADDONS`, `DEMAND_GRID`, `EXEC_DIAGRAM`, etc.).

- [ ] **Step 1: Run R-RENDER-01 as-is to confirm it already passes** (the generic full-fill loop covers the new templates):

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-RENDER-01"`
Expected: PASS (complete fill leaves no surviving tokens across all 15 templates).

- [ ] **Step 2: Add a presence assertion** at the end of `t_render` (after the `survivor` loop, before the function ends), pinning the new tokens to their templates so a rename surfaces:

```python
    # new-token presence guard (Tasks 2-5): these must exist in their templates
    expect = {
        "templates/06-license-entitlements.md": ["{{REQUIRED_LICENSING_TABLE}}"],
        "templates/07-addon-tiering.md": ["{{STANDARD_ISV_ADDONS}}"],
        "templates/13-demand-plan.md": ["{{DEMAND_GRID}}", "{{DEMAND_DIAGRAM}}"],
        "templates/14-exec-infographic.md": ["{{TAM_PANEL}}", "{{EXEC_DIAGRAM}}"],
    }
    missing_tok = []
    for path, toks in expect.items():
        body = read(path)
        for t in toks:
            if t not in body:
                missing_tok.append(f"{path}: {t}")
    assert not missing_tok, f"expected token(s) missing from template: {missing_tok}"
```

- [ ] **Step 3: Run it to verify it passes**

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-RENDER-01"`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/validate_skill.py
git commit -m "test(R-RENDER-01): pin new #06/#07/#13/#14 tokens to their templates"
```

---

### Task 8: Register the new diagram tokens as intentional placeholders

The two new `*_DIAGRAM` tokens must be render-safe (visible "pending" marker, exit 0) or a real HTML render hard-fails. R-MD2H-02 enumerates the expected set and must be extended in lockstep.

**Files:**
- Modify: `scripts/md_to_html.py:27-31` (`INTENTIONAL_PLACEHOLDERS`)
- Modify: `tests/validate_skill.py` (R-MD2H-02 token list, ~line 674-677)

**Interfaces:**
- Consumes: `DEMAND_DIAGRAM` (Task 5), `EXEC_DIAGRAM` (Task 4).

- [ ] **Step 1: Add the two tokens to `INTENTIONAL_PLACEHOLDERS`** in `scripts/md_to_html.py`:

```python
INTENTIONAL_PLACEHOLDERS = {
    "STATUS_ROLLUP_DIAGRAM", "COMPOSITION_DIAGRAM", "TIER_DIAGRAM", "PARTNER_FIT_DIAGRAM",
    "INFOGRAPHIC_DIAGRAM", "MARKETECTURE_DIAGRAM", "DEMAND_DIAGRAM", "EXEC_DIAGRAM",
    "PRICE_PENDING", "DISCOUNT_PENDING",
}
```

- [ ] **Step 2: Add the two tokens to the R-MD2H-02 assertion list** in `tests/validate_skill.py` (the `for tok in (...)` tuple at ~line 674) — append `"DEMAND_DIAGRAM", "EXEC_DIAGRAM"`.

- [ ] **Step 3: Run R-MD2H-02 and the render-safe e2e check**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-MD2H-02|R-RENDER-SAFE-01"`
Expected: both PASS.

- [ ] **Step 4: Commit**

```bash
git add scripts/md_to_html.py tests/validate_skill.py
git commit -m "feat(render): make DEMAND_DIAGRAM + EXEC_DIAGRAM render-safe placeholders"
```

---

### Task 9: Targeted structure assert for the demand-grid discipline

A dedicated check so the demand grid's three SKU-bundle column labels and the conditional-add-on inclusion rule cannot be silently dropped by a future edit (the spec calls this out explicitly).

**Files:**
- Modify: `tests/validate_skill.py` (add a new `@check` function near the other R-TPL checks)

- [ ] **Step 1: Write the failing test.** Add this check function after `t_template_shared_convention` (~line 328):

```python
# ---- R-TPL-03: demand-grid carries its required columns + the inclusion rule ----
@check("R-TPL-03: 13-demand-plan carries the three SKU-bundle columns and the NPI-dependent inclusion rule")
def t_demand_grid_structure():
    body = read("templates/13-demand-plan.md")
    for col in ["Core / Required SKUs", "Standard add-ons", "Conditional (NPI-dependent) add-ons"]:
        assert col in body, f"demand grid missing required column label: {col}"
    assert "only when the NPI process has identified that add-on as required" in body, \
        "demand grid missing the conditional-add-on inclusion rule"
    assert "CC / CC+" in body, "demand grid should name the CC/CC+ worked example"
```

- [ ] **Step 2: Run it to verify it passes** (the #13 template from Task 5 already contains these strings):

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-TPL-03"`
Expected: PASS.

- [ ] **Step 3: Sanity-gate the check** — temporarily change one expected column string in the assertion to a wrong value, run, confirm it FAILS, then revert. (Proves the check can fail.)

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-TPL-03"`
Expected (during sanity check): FAIL. After revert: PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/validate_skill.py
git commit -m "test(R-TPL-03): assert demand-grid columns + NPI-dependent inclusion rule"
```

---

### Task 10: Update the hardcoded count claims (R-DOC-01) + voice classification + intake/registry refs

R-DOC-01 is currently RED (docs say "13", registry has 15). Fix every family-size string and the supporting refs in one task so the suite goes fully green.

**Files:**
- Modify: `SKILL.md:53` ("the 13 deliverables" → "the 15 deliverables"); also the "(8 narrative)" voice line if present (see Step 2)
- Modify: `README.md:3,34,49` (three "13 artifacts/deliverables" claims → "15"); line 13 is an acceptance-doc *filename* link — leave it (historical artifact name)
- Modify: `refs/artifact-templates.md:3` ("The 13 artifact skeletons" → "15") and the registry table (add two rows)
- Modify: `refs/voice-and-style.md` (the narrative-artifact slug list, if it enumerates slugs — add 13, 14 as narrative)
- Modify: `refs/quality-loops.md` (the "all 11"/"all 13" batching warning string that R-LOOPS-01 checks, line ~507 of the test references "all 11"/"all-in-one"/"single subagent" — ensure the ref's phrasing still satisfies it; if it says "all 13", update to "all 15")
- Modify: `refs/intake-source-map.md` (add TAM + segments as a research-channel output)

**Interfaces:**
- Consumes: `len(ARTIFACT_REGISTRY) == 15`.

- [ ] **Step 1: Update SKILL.md line 53.** Change `**Artifacts:** the 13 deliverables are generated` → `**Artifacts:** the 15 deliverables are generated`. Then add the two new artifacts to the registry/notes table in `refs/artifact-templates.md`:

```markdown
| 13-demand-plan | narrative | segments × SKU-bundle grid; IPP+TAM-keyed; conditional add-ons only-if-required |
| 14-exec-infographic | narrative | exec single-screen: vision → value prop → use cases → ideal partners → TAM |
```
and change its line 3 `The 13 artifact skeletons` → `The 15 artifact skeletons`.

- [ ] **Step 2: Update README.md** lines 3, 34, 49 — replace `13-artifact`/`the 13 artifacts` with `15-artifact`/`the 15 artifacts`. (Leave line 13's acceptance-doc filename link unchanged — it's a historical file name, not a count claim; R-DOC-01's regex requires "the/all N artifact(s)" so a filename like `...-13-artifacts.md` is not matched. Verify by reading the regex at test line ~790.)

- [ ] **Step 3: Update the voice ref + loops ref (exact edits).**
  - `refs/voice-and-style.md` enumerates the narrative slugs in two places — **line 4-5** (the "Load this before writing any narrative artifact (00-…, …, 12-marketecture)" list) and **line 42** (the "Narrative artifacts (00, 01, 02, 03, 05, 10, 11, 12)" list). Add `13-demand-plan` and `14-exec-infographic` to the line 4-5 list, and `13, 14` to the line 42 parenthetical. Both #13 and #14 are narrative.
  - `refs/quality-loops.md` **line 65** reads "never generate all 13 artifacts in a single subagent" — change `13` → `15`. (R-LOOPS-01 is satisfied either way because line 63 "all-in-one" and line 66 phrasing remain; this edit is for R-DOC-01 count accuracy.)

- [ ] **Step 4: Add TAM/segments to the intake ref.** In `refs/intake-source-map.md`, under the web-research / research channel, add a short paragraph: TAM and target segments are **estimated during research using internal Salesforce insights**, captured once as effort data (value + basis + confidence + `estimate` flag), reused by #13/#14/#00/#11, and degrade to a flagged `pending` gap when not provided. (Keep all the strings R-INTAKE-01/02 assert — do not remove existing channel/allowlist/question text.)

- [ ] **Step 5: Run the full suite**

Run: `python3 tests/validate_skill.py`
Expected: ALL PASS, including R-DOC-01, R-INTAKE-01, R-INTAKE-02, R-LOOPS-01, R-VOICE-01.

- [ ] **Step 6: Commit**

```bash
git add SKILL.md README.md refs/artifact-templates.md refs/voice-and-style.md refs/quality-loops.md refs/intake-source-map.md
git commit -m "docs: bump family size 13->15; classify #13/#14 narrative; add TAM/segments to intake ref"
```

---

### Task 11: Full-suite green + dogfood render on the Healthcare effort

**Files:**
- None modified (verification task). Effort data lives outside the repo at
  `/Users/bstauber/claude-projects/ps-npi-efforts/<release>/agentforce-healthcare-oem/`.

- [ ] **Step 1: Run the entire validation suite**

Run: `python3 tests/validate_skill.py`
Expected: `N/N checks passed`, exit 0 (N is now the original count + 1 for R-TPL-03; R-DOC-01's check-count claim, if any doc states one, must match — grep `\d+ checks` in docs and update if present).

- [ ] **Step 2: Confirm no doc states a stale check-count.** If R-DOC-01 fails on a "N checks" claim, update that doc string to the new suite size, then re-run Step 1.

Run: `grep -rnE "[0-9]+ checks?" SKILL.md README.md refs/`
Expected: any match equals the suite size; fix and re-run if not.

- [ ] **Step 3: Dogfood render (manual, against the existing effort).** Generate #06, #07, #13, #14 for the Healthcare effort by filling tokens (per the normal generate cycle) and rendering to HTML + canvas. Verify: zero surviving `{{TOKEN}}` in the rendered HTML, #13/#14 appear as canvas cards (or labeled gap cards if pending), and the two new diagrams render as live `<pre class="mermaid">` fences with a `graph`/`%%{init` body (per B18 — check fence CONTENT, not just presence). This step is judgment work (the agent fills tokens); it is not a unit test.

- [ ] **Step 4: Final commit if any doc count was touched in Step 2**

```bash
git add -A
git commit -m "docs: reconcile check-count claim after R-TPL-03"
```

---

## Notes for the implementer

- **Order matters:** Task 1 first (turns the suite red as a worklist). Tasks 2-6 satisfy the structural rules. Tasks 7-9 extend tests. Task 10 turns R-DOC-01 green. Task 11 verifies end-to-end.
- **The suite is your guide:** after each task, `python3 tests/validate_skill.py` tells you exactly what's still red.
- **Do not** add price numbers, fetch live TAM, or touch #11 (explicitly out of scope per the spec).
- **Pre-commit hook** runs the suite on every commit — a red suite blocks the commit, which is intended; finish the task that greens it.
