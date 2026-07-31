# Commercial Business-Case Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the ps-npi-forge artifact family from a demand/GTM set into one carrying a real commercial business case — internal ASP/penetration/attrition (#13), cross-cloud halo ACV (#07+#13), partner-forecast proof points (#14/#11/#00), an anchor-partner archetype (#10), and AE channel-conflict guidance (#03/#04) — with a precise pricing-guardrail carve-out.

**Architecture:** All six target artifacts already exist in the registry (family stays 15 — no registry/manifest change). Changes are new sections/tokens/columns in existing `templates/<slug>.md` files plus a refined refusal rule in SKILL.md. The validation suite (`tests/validate_skill.py`) is registry-derived; new tokens are auto-covered by R-RENDER-01's full-fill loop, and new structural guards are added explicitly (a refined R-REF-02 and a new R-TPL-04).

**Tech Stack:** Python 3 stdlib only. Markdown templates. No new dependencies. No new diagram tokens (reuse existing slots), so `INTENTIONAL_PLACEHOLDERS` is unchanged.

## Global Constraints

- **Stdlib-only.** No third-party imports in `scripts/` or `tests/`.
- **Pricing guardrail (refined this increment).** Partner-facing **list / quote / discount** pricing stays out of scope and renders as literal `{{PRICE_PENDING}}` / `{{DISCOUNT_PENDING}}` — never a number. **Internal business-case inputs** (ASP, penetration rate, attrition, halo ACV) ARE allowed, but ONLY as flagged estimates in the demand-plan artifact (#13), sourced from internal Salesforce insights, each carrying an `estimate` framing. They are planning inputs, never a partner quote.
- **Template shared convention (R-TPL-02).** Every edited `templates/<slug>.md` MUST still contain verbatim: the VOICE comment, `> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}`, `> {{GAP_BANNER}}`, and the footer block `---` / `**Sources:** {{SOURCES}}` / `**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}`. (`·` and `—` are literal.)
- **Token hygiene (R-TEST-02).** Every new `{{TOKEN}}` is `[A-Z0-9_]+`.
- **No registry / manifest / count change.** Family stays 15; do NOT touch `ARTIFACT_REGISTRY`, `templates/manifest.yaml`, the fixture, or the "15 artifacts" doc counts.
- **R-REF-02 keeps its four needles.** The refusal section MUST still contain the literal strings `pricing`, `non-official`, `read-only`, `without confirmation` (the test lowercases). The carve-out is ADDED, nothing removed.
- **Voice unchanged.** #13/#14/#11/#00/#10 narrative; #03 narrative; #04 reference (per existing VOICE comments — do not change them).
- **Run the suite:** `python3 tests/validate_skill.py` (exit 0 = pass). Baseline is 45/45.
- **Branch:** create `npi-commercial-business-case` off `main`.

---

### Task 1: Pricing-guardrail carve-out (SKILL.md + refined R-REF-02)

Do this first: it sets the rule the rest of the increment depends on, and the refined test makes the carve-out non-revertible.

**Files:**
- Modify: `SKILL.md:72-73` (the pricing bullet in the Refusal & scope section)
- Modify: `tests/validate_skill.py` (R-REF-02 check `t_out_of_scope`, ~line 67-71)

**Interfaces:**
- Produces: SKILL.md states both (a) list/quote/discount pricing out of scope, and (b) internal business-case inputs allowed as flagged estimates in #13. Task 2/3 rely on (b) being the sanctioned rule.

- [ ] **Step 1: Edit the SKILL.md pricing bullet.** Replace lines 72-73:

```markdown
- Determine or fill **partner-facing pricing or discounts** — out of scope; list/quote/discount
  cells are left as marked placeholders owned elsewhere. (Carve-out: **internal business-case
  inputs** — ASP, penetration, attrition, and cross-cloud halo ACV — are in scope as *flagged
  estimates* in the demand-plan artifact (#13) only, sourced from internal Salesforce insights;
  they are planning inputs, never a partner quote.)
```

- [ ] **Step 2: Run R-REF-02 to confirm it still passes** (the four needles `pricing`/`non-official`/`read-only`/`without confirmation` are all still present elsewhere in the section):

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-REF-02"`
Expected: PASS.

- [ ] **Step 3: Refine R-REF-02 to assert the carve-out.** In `tests/validate_skill.py`, after the existing four-needle loop in `t_out_of_scope`, add:

```python
    # the pricing carve-out must be stated: internal business-case inputs allowed as flagged estimates
    assert "business-case" in s or "business case" in s, \
        "refusal section must state the internal-business-case carve-out"
    assert "asp" in s and "halo" in s and "estimate" in s, \
        "carve-out must name ASP + halo ACV as flagged estimates"
```

- [ ] **Step 4: Run it; verify PASS**

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-REF-02"`
Expected: PASS.

- [ ] **Step 5: Sanity-gate.** Temporarily delete the `(Carve-out: ...)` text from SKILL.md, run the suite, confirm R-REF-02 now FAILS, then restore.

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-REF-02"`
Expected (during sanity check): FAIL. After restore: PASS.

- [ ] **Step 6: Commit**

```bash
git add SKILL.md tests/validate_skill.py
git commit -m "feat(guardrail): carve out internal business-case inputs from the pricing rule"
```

---

### Task 2: Internal business case in #13 (B22 — ASP / penetration / attrition)

**Files:**
- Modify: `templates/13-demand-plan.md` (insert a section after `## Segment & TAM basis`, before `## Conditional (NPI-dependent) add-ons — inclusion rule`)

**Interfaces:**
- Produces: token `{{BUSINESS_CASE_TABLE}}` in #13. Task 7 pins it; Task 8 (R-TPL-04) asserts the business-case columns + framing.

- [ ] **Step 1: Insert the business-case section.** In `templates/13-demand-plan.md`, after line 22 (`{{SEGMENT_TAM_BASIS}}`) and before line 24 (`## Conditional ...`), insert:

```markdown

## Internal business case (estimates)

Internal planning inputs — **flagged estimates** from internal Salesforce insights, **not
partner-facing pricing**. Each is an estimate pending commercial-team confirmation.

| Segment | TAM (est.) | ASP (est.) | Penetration % (est.) | Attrition % (est.) | Modeled ACV (est.) |
|---------|-----------|-----------|----------------------|--------------------|--------------------|
| {{BUSINESS_CASE_TABLE}} | | | | | |
```

- [ ] **Step 2: Verify R-TPL-02 + token hygiene still pass**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-TPL-02|R-TEST-02"`
Expected: both PASS.

- [ ] **Step 3: Commit**

```bash
git add templates/13-demand-plan.md
git commit -m "feat(#13): add internal business-case section (ASP/penetration/attrition estimates)"
```

---

### Task 3: Cross-cloud halo revenue (B23 — #07 framing + #13 + #07 halo column)

**Files:**
- Modify: `templates/13-demand-plan.md` (add a Halo ACV column to the demand-grid header + intro)
- Modify: `templates/07-addon-tiering.md` (add a halo-ACV framing line + column to the standard-ISV-add-on catalog section)

**Interfaces:**
- Consumes: the existing `{{DEMAND_GRID}}` token (#13) and `{{STANDARD_ISV_ADDONS}}` token (#07) — both stay single-token rows; only header columns + framing prose are added. No new token required.

- [ ] **Step 1: Add the halo column to the #13 demand grid.** In `templates/13-demand-plan.md`, update the grid intro (lines 13-15) and the table header (lines 17-19) to add a Halo ACV column. Replace:

```markdown
Rows are identified segments (each with a TAM estimate and an Ideal-Partner-Profile fit indicator from
#10). The SKU-bundle columns are **Core / Required SKUs**, **Standard add-ons**, and **Conditional
(NPI-dependent) add-ons**.

| Segment | TAM (est.) | IPP-fit | Core / Required SKUs | Standard add-ons | Conditional (NPI-dependent) add-ons |
|---------|-----------|---------|----------------------|------------------|-------------------------------------|
| {{DEMAND_GRID}} | | | | | |
```

with:

```markdown
Rows are identified segments (each with a TAM estimate and an Ideal-Partner-Profile fit indicator from
#10). The SKU-bundle columns are **Core / Required SKUs**, **Standard add-ons**, and **Conditional
(NPI-dependent) add-ons**. The **Halo ACV (est.)** column captures cross-cloud pull-through (Data
Cloud / MuleSoft / Tableau Next) the PAM is credited for alongside the OEM licenses — a flagged
estimate, not partner-facing pricing.

| Segment | TAM (est.) | IPP-fit | Core / Required SKUs | Standard add-ons | Conditional (NPI-dependent) add-ons | Halo ACV (est.) |
|---------|-----------|---------|----------------------|------------------|-------------------------------------|-----------------|
| {{DEMAND_GRID}} | | | | | | |
```

- [ ] **Step 2: Add the halo framing + column to the #07 catalog.** In `templates/07-addon-tiering.md`, replace the standard-ISV-add-on section (lines 26-34) with:

```markdown
## Standard ISV add-ons partners may attach

Distinct from the Required/Recommended/Optional tiers above (which are *this product's own* add-on
dependencies), this is the **cross-sell menu** — standard ISV add-on SKUs partners commonly attach on
top of {{PRODUCT_NAME}}, and the **halo ACV** they pull through for the PAM. (For example, the FSC OEM
motion at AgFirst generated a halo of MuleSoft + Tableau ACV alongside the OEM licenses.) List pricing
is out of scope; Halo ACV is an internal flagged estimate, not a partner quote.

| Standard add-on | Why relevant to this partner motion | Typical attach trigger | Halo ACV (est.) | Price |
|-----------------|--------------------------------------|------------------------|-----------------|-------|
| {{STANDARD_ISV_ADDONS}} | | | | {{PRICE_PENDING}} |
```

- [ ] **Step 3: Verify R-TPL-02, token hygiene, and the full-fill render pass**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-TPL-02|R-TEST-02|R-RENDER-01"`
Expected: all PASS (no new tokens; `{{PRICE_PENDING}}` preserved; header columns are plain text).

- [ ] **Step 4: Commit**

```bash
git add templates/13-demand-plan.md templates/07-addon-tiering.md
git commit -m "feat(#07,#13): frame standard add-ons as PAM halo ACV; add Halo ACV est. column"
```

---

### Task 4: Anchor-partner archetype (B25 — #10)

**Files:**
- Modify: `templates/10-partner-profile-pov.md` (add an anchor-partner section after `## Ideal partner archetypes (Tier B)` / `{{ARCHETYPES}}`)

**Interfaces:**
- Produces: token `{{ANCHOR_PARTNER}}` in #10. Task 7 pins it.

- [ ] **Step 1: Insert the anchor-partner section.** In `templates/10-partner-profile-pov.md`, insert after line 15 (`{{ARCHETYPES}}`, which closes the `## Ideal partner archetypes (Tier B)` section) and before line 17 (`## Illustrative example companies (Tier B — verify)`):

```markdown

## Anchor partner (the model to replicate)
{{ANCHOR_PARTNER}}
```

- [ ] **Step 3: Verify R-TPL-02 + token hygiene + full-fill**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-TPL-02|R-TEST-02|R-RENDER-01"`
Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add templates/10-partner-profile-pov.md
git commit -m "feat(#10): add anchor-partner archetype section (gold-standard model to replicate)"
```

---

### Task 5: AE channel-conflict guidance (B26 — #03 + #04)

**Files:**
- Modify: `templates/03-internal-enablement.md` (add a channel-conflict section)
- Modify: `templates/04-internal-faq.md` (add a channel-conflict Q&A section)

**Interfaces:**
- Produces: token `{{CHANNEL_CONFLICT}}` in #03 and `{{CHANNEL_CONFLICT_FAQ}}` in #04 (both templates use per-section tokens, so a new section = a new token). Task 7 pins both.

- [ ] **Step 1: Add the #03 section.** In `templates/03-internal-enablement.md`, insert after `## The partner motion & rules` / `{{MOTION_RULES}}` (lines 11-12) and before `## Entitlement implications`:

```markdown

## AE channel conflict (get ahead of it)
{{CHANNEL_CONFLICT}}
```

- [ ] **Step 2: Add the #04 Q&A section.** In `templates/04-internal-faq.md`, insert after `## Licensing & entitlements` / `{{FAQ_LICENSING}}` (lines 17-18) and before `## Open questions`:

```markdown

## AE channel conflict & non-compliant resale
{{CHANNEL_CONFLICT_FAQ}}
```

- [ ] **Step 3: Verify R-TPL-02 + token hygiene + full-fill**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-TPL-02|R-TEST-02|R-RENDER-01"`
Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add templates/03-internal-enablement.md templates/04-internal-faq.md
git commit -m "feat(#03,#04): add AE channel-conflict / non-compliant-resale guidance"
```

---

### Task 6: Partner-forecast proof-point framing (B24 — #14 / #11 / #00)

This is framing/guidance in template prose — no new tokens, no structural change. It directs the generator to frame proof/outcomes as forecasted partner deals, not existing direct-SF customer logos.

**Files:**
- Modify: `templates/14-exec-infographic.md` (framing line under `## Key use cases`)
- Modify: `templates/11-solution-infographic.md` (framing line under the outcomes section)
- Modify: `templates/00-executive-summary.md` (framing line under `## Top use cases`)

**Interfaces:**
- No new tokens. Pure prose guidance lines that sit above the existing tokens.

- [ ] **Step 1: #14 — add a framing line.** In `templates/14-exec-infographic.md`, change the `## Key use cases` block (lines 14-15) to:

```markdown
## Key use cases
<!-- Proof points are partner-driven forecasted deals, not existing direct-Salesforce customer logos. -->
{{USE_CASES_PANEL}}
```

- [ ] **Step 2: #11 — add a framing line.** In `templates/11-solution-infographic.md`, the outcomes section is `## Outcomes (the proof)` (line 17) with token `{{OUTCOMES_PANEL}}` (line 18). Insert an HTML-comment framing line between them, so line 17-18 becomes:

```markdown
## Outcomes (the proof)
<!-- Frame outcomes as forecasted partner-sourced deals, not existing direct-Salesforce customers. -->
{{OUTCOMES_PANEL}}
```

- [ ] **Step 3: #00 — add a framing line.** In `templates/00-executive-summary.md`, change the `## Top use cases` block (lines 16-17) to:

```markdown
## Top use cases
<!-- Proof points should be partner-driven forecasted deals, not existing direct-Salesforce customers. -->
{{TOP_USE_CASES}}
```

- [ ] **Step 4: Verify the comments are stripped on render (R-MD2H-04) and nothing else broke**

Run: `python3 tests/validate_skill.py 2>&1 | grep -E "R-MD2H-04|R-TPL-02|R-RENDER-01"`
Expected: all PASS. (R-MD2H-04 already loops every template through `md_to_html` and asserts HTML comments are stripped, so these new comments are covered — they will NOT leak into rendered output.)

- [ ] **Step 5: Commit**

```bash
git add templates/14-exec-infographic.md templates/11-solution-infographic.md templates/00-executive-summary.md
git commit -m "feat(#14,#11,#00): frame proof points as partner-forecasted deals"
```

---

### Task 7: Render fill-set presence pins for the new tokens (R-RENDER-01)

R-RENDER-01's generic full-fill loop already covers the new tokens for surviving-token detection. This task adds explicit presence pins (matching the prior increment's pattern) so a future rename surfaces.

**Files:**
- Modify: `tests/validate_skill.py` (extend the presence-pin block inside `t_render`, the `expect` dict added in the prior increment)

**Interfaces:**
- Consumes: `{{BUSINESS_CASE_TABLE}}` (Task 2), `{{ANCHOR_PARTNER}}` (Task 4), `{{CHANNEL_CONFLICT}}` / `{{CHANNEL_CONFLICT_FAQ}}` (Task 5).

- [ ] **Step 1: Read the current `expect` dict** in `t_render` (added by the prior increment, ~line 394) to match its exact structure.

- [ ] **Step 2: Add the new entries** to that `expect` dict:

```python
        "templates/13-demand-plan.md": ["{{DEMAND_GRID}}", "{{DEMAND_DIAGRAM}}", "{{BUSINESS_CASE_TABLE}}"],
        "templates/10-partner-profile-pov.md": ["{{ANCHOR_PARTNER}}"],
        "templates/03-internal-enablement.md": ["{{CHANNEL_CONFLICT}}"],
        "templates/04-internal-faq.md": ["{{CHANNEL_CONFLICT_FAQ}}"],
```

(Note: the #13 entry already exists from the prior increment with `DEMAND_GRID`+`DEMAND_DIAGRAM` — extend it to add `BUSINESS_CASE_TABLE`; do not create a duplicate key.)

- [ ] **Step 3: Run R-RENDER-01; verify PASS**

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-RENDER-01"`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/validate_skill.py
git commit -m "test(R-RENDER-01): pin new business-case/anchor/channel-conflict tokens"
```

---

### Task 8: Business-case discipline assert (new R-TPL-04)

A targeted guard so #13's business-case columns and the "estimates / not partner-facing pricing" framing can't be silently dropped — mirroring how R-TPL-03 guards the conditional-add-on discipline.

**Files:**
- Modify: `tests/validate_skill.py` (add a `@check` function after `t_demand_grid_structure`, the R-TPL-03 function)

- [ ] **Step 1: Write the check.** Add after the R-TPL-03 function:

```python
# ---- R-TPL-04: #13 carries the internal business-case columns + the estimate/not-pricing framing ----
@check("R-TPL-04: 13-demand-plan carries the business-case columns (ASP/penetration/attrition) and the estimate-not-pricing framing")
def t_business_case_structure():
    body = read("templates/13-demand-plan.md")
    for col in ["ASP (est.)", "Penetration % (est.)", "Attrition % (est.)", "Halo ACV (est.)"]:
        assert col in body, f"#13 business case missing column: {col}"
    assert "not\n  partner-facing pricing" in body or "not partner-facing pricing" in body or "not\npartner-facing pricing" in body, \
        "#13 must frame the business-case inputs as estimates, not partner-facing pricing"
    assert "flagged estimate" in body.lower(), "#13 business case must call the inputs flagged estimates"
```

- [ ] **Step 2: Run it; verify PASS**

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-TPL-04"`
Expected: PASS. (If the "not partner-facing pricing" assertion fails due to line-wrapping in the template, normalize by checking `" ".join(body.split())` — see Step 3.)

- [ ] **Step 3: If the framing assertion is brittle to whitespace, make it whitespace-robust.** Replace the middle assertion with:

```python
    flat = " ".join(body.split())
    assert "not partner-facing pricing" in flat, \
        "#13 must frame the business-case inputs as estimates, not partner-facing pricing"
```

Re-run: `python3 tests/validate_skill.py 2>&1 | grep "R-TPL-04"` → Expected: PASS.

- [ ] **Step 4: Sanity-gate.** Temporarily change `ASP (est.)` in the template to `ASP`, run, confirm R-TPL-04 FAILS, then restore.

Run: `python3 tests/validate_skill.py 2>&1 | grep "R-TPL-04"`
Expected (during sanity check): FAIL. After restore: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/validate_skill.py
git commit -m "test(R-TPL-04): assert #13 business-case columns + estimate-not-pricing framing"
```

---

### Task 9: Refs alignment + full suite + dogfood

**Files:**
- Modify: `refs/artifact-templates.md` (update the #07/#13 notes to mention halo ACV + business case; update #03/#04/#10 notes if they enumerate sections — light)
- Modify: `refs/intake-source-map.md` (note ASP/penetration/attrition/halo as research-derived business-case estimates, alongside the TAM/segments note added in the prior increment)

**Interfaces:**
- No code. Doc alignment so the refs describe the new sections; R-DOC-01 is unaffected (no count change).

- [ ] **Step 1: Update `refs/artifact-templates.md` registry-table notes.** For the #07 row, append "+ standard ISV add-on / halo-ACV catalog"; for #13, append "+ internal business case (ASP/penetration/attrition est.)"; for #10, append "+ anchor partner"; for #03/#04, append "+ AE channel-conflict". Keep each note one line.

- [ ] **Step 2: Update `refs/intake-source-map.md`.** In the research-channel paragraph that the prior increment added for TAM/segments, add a sentence: business-case inputs (ASP, penetration, attrition, cross-cloud halo ACV) are likewise **research-derived flagged estimates** from internal Salesforce insights, confined to #13, never partner-facing pricing. (Keep all strings R-INTAKE-01/02 assert — additive only.)

- [ ] **Step 3: Run the full suite**

Run: `python3 tests/validate_skill.py`
Expected: `N/N checks passed`, exit 0 (N = 45 + R-TPL-04 = 46; if any doc states a "N checks" count, R-DOC-01 will flag it — grep and update if present).

- [ ] **Step 4: Confirm no stale check-count claim.**

Run: `grep -rnE "[0-9]+ checks?" SKILL.md README.md refs/`
Expected: any match equals the suite size; fix and re-run if not.

- [ ] **Step 5: Dogfood render (manual, against the existing effort).** Fill the new tokens for the Healthcare effort (business case, halo ACV, anchor partner = FSC/nCino, channel-conflict guidance) and render #03/#04/#07/#10/#13 to HTML + canvas. Verify zero surviving `{{TOKEN}}`, the proof-point framing comments are stripped (not visible), and the #13 business-case + halo columns render. This is judgment work (the agent fills tokens); if the effort data or numbers are unavailable, run the full validation suite as the mechanical completion bar and flag that the live render needs Brandon's numbers — do NOT fabricate ASP/penetration/halo figures.

- [ ] **Step 6: Commit any doc edits**

```bash
git add refs/artifact-templates.md refs/intake-source-map.md
git commit -m "docs: align refs with business-case/halo/anchor/channel-conflict sections"
```

---

## Notes for the implementer

- **Order:** Task 1 first (the carve-out rule everything else relies on). Tasks 2-6 edit templates. Tasks 7-8 add test guards. Task 9 aligns refs + verifies end-to-end.
- **No registry/manifest/count change** — this increment stays at 15 artifacts. If you find yourself editing `ARTIFACT_REGISTRY`, `manifest.yaml`, the fixture, or a "15 artifacts" count, stop — that's out of scope.
- **No new diagram tokens** — do not add to `INTENTIONAL_PLACEHOLDERS`.
- **The suite is your guide:** `python3 tests/validate_skill.py` after each task.
- **Do not** introduce price/discount numbers; halo ACV / ASP are internal estimates framed as such, confined to #13 (and the #07 halo column as an estimate), never a partner quote.
- **Point 6 (FSC/AutoCloud NPI precedent) is OUT of scope** — it's backlog B21, a separate cross-effort design. Do not add a precedent/lessons section here.
