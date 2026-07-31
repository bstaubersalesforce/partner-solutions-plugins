# ps-npi-forge Artifact Consolidation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make derived artifacts single-sourced — generated FROM a source-of-record, grounded not re-researched — via a machine-readable derivation graph, a derivation contract in the generate cycle, source-naming template headers, and three new validator guards. No artifact created, merged, or deleted.

**Architecture:** A `refs + manifest + validator` change. `manifest.py` gains a `DERIVES_FROM` map + `generation_order()` topological sort (the machine-readable graph). `refs/quality-loops.md` gains the derivation contract + dependency-ordered batching. Six derived templates get a source-naming header comment; `refs/artifact-templates.md` documents the map. Three checks (R-DERIVE-01/02/03) gate it. Dogfood against the existing healthcare effort proves no-drift.

**Tech Stack:** Python 3 stdlib (`scripts/manifest.py`, `tests/validate_skill.py` — the `@check`-decorated suite run via `python3 tests/validate_skill.py`), Markdown refs/templates. No third-party deps.

## Global Constraints

- **Stdlib only**; `manifest.py` stays dependency-free (hand-rolled YAML).
- **No artifact created, merged, or deleted.** `ARTIFACT_REGISTRY` stays exactly the 15 slugs 00–14. Verification asserts the count is unchanged.
- **Derivation graph (the one true map):** `01-brief → {00-executive-summary, 02-slide-summary, 11-solution-infographic, 14-exec-infographic}`; `04-internal-faq → {05-external-faq}`; `06-license-entitlements → {07-addon-tiering}`. Sources 01/04/06 are never themselves derived → acyclic.
- **`DERIVES_FROM` lives ONLY in `manifest.py`** (single source of truth). The validator LOADS manifest.py to read it (like R-MANIFEST-06 does via `_load_script`) — never duplicate the map in the validator.
- **Suite must stay green** — run `python3 tests/validate_skill.py` after every task; it is currently 58/58 and grows by 3 (→61). Trust the live run over any number written here. Pre-commit hook + CI enforce it.
- **07 is partially derived** — only its Required tier is grounded in 06; Recommended/Optional stay 07-authored. The `DERIVES_FROM` edge is for ordering/validation; the refs carry the partial-scope nuance.
- **00 is a special derivation** — `rollup(01) + manifest state` (Next Steps & Blockers register + confidence rollup, both unique to 00 and unchanged).

---

### Task 1: Machine-readable derivation graph in `manifest.py` + R-DERIVE-01

**Files:**
- Modify: `scripts/manifest.py` (add `DERIVES_FROM` after `LOOP_REGISTRY`/`VERDICT_VOCAB` ~line 19; add `generation_order()` after `overall_confidence` ~line 63)
- Modify: `tests/validate_skill.py` (add `@check` R-DERIVE-01 near the other R-MANIFEST checks)

**Interfaces:**
- Consumes: existing `ARTIFACT_REGISTRY`, the `_load_script` helper in the validator.
- Produces: `manifest.DERIVES_FROM` (dict slug→source-slug), `manifest.generation_order()` (list of all 15 slugs, every source before its derivatives, raises `ValueError` on cycle/missing-source). Later tasks (quality-loops) reference this order.

- [ ] **Step 1: Write the failing check**

Add to `tests/validate_skill.py` (place after the R-MANIFEST-08 check, before the R-CI section):

```python
@check("R-DERIVE-01: DERIVES_FROM keys+values are registry slugs; graph is acyclic; generation_order topological")
def t_derivation_graph():
    m = _load_script("scripts/manifest.py", "manifest_derive")
    reg = set(m.ARTIFACT_REGISTRY)
    df = m.DERIVES_FROM
    # keys and values must all be real registry slugs
    for k, v in df.items():
        assert k in reg, f"DERIVES_FROM key not in registry: {k}"
        assert v in reg, f"DERIVES_FROM source not in registry: {v}"
        assert k != v, f"artifact derives from itself: {k}"
    # a source must not itself be derived (2-level, acyclic by construction)
    for k, v in df.items():
        assert v not in df, f"source {v} is itself derived — graph not shallow/acyclic"
    # generation_order returns all 15, every source before its derivatives, no dup
    order = m.generation_order()
    assert sorted(order) == sorted(m.ARTIFACT_REGISTRY), "generation_order must return every artifact exactly once"
    pos = {slug: i for i, slug in enumerate(order)}
    for derived, src in df.items():
        assert pos[src] < pos[derived], f"generation_order places source {src} after its derivative {derived}"
```

- [ ] **Step 2: Run the suite to verify the new check fails**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on R-DERIVE-01 with `AttributeError`/`module 'manifest_derive' has no attribute 'DERIVES_FROM'` (or `generation_order`).

- [ ] **Step 3: Add `DERIVES_FROM` to `manifest.py`**

Insert after line 19 (`VERDICT_VOCAB = [...]`):

```python
# Derivation graph: derived-artifact-slug -> source-of-record slug.
# Derived artifacts are GENERATED FROM their source (grounded transform, not re-research).
# 00 is a special derivation: rollup(01-brief) PLUS manifest state (blockers/confidence).
# 07 is PARTIALLY derived: its Required tier is grounded in 06; Recommended/Optional stay 07-authored.
DERIVES_FROM = {
    "00-executive-summary":    "01-brief",
    "02-slide-summary":        "01-brief",
    "11-solution-infographic": "01-brief",
    "14-exec-infographic":     "01-brief",
    "05-external-faq":         "04-internal-faq",
    "07-addon-tiering":        "06-license-entitlements",
}
```

- [ ] **Step 4: Add `generation_order()` to `manifest.py`**

Insert after `overall_confidence` (after line 63):

```python
def generation_order():
    """Artifact slugs ordered so every source precedes its derivatives.
    Stable: within a readiness wave, ARTIFACT_REGISTRY order is preserved.
    Raises ValueError on a cycle or a source that never becomes available."""
    order, emitted, remaining = [], set(), list(ARTIFACT_REGISTRY)
    progress = True
    while remaining and progress:
        progress = False
        for a in list(remaining):
            src = DERIVES_FROM.get(a)
            if src is None or src in emitted:
                order.append(a); emitted.add(a); remaining.remove(a); progress = True
    if remaining:
        raise ValueError(f"derivation cycle or missing source among: {remaining}")
    return order
```

- [ ] **Step 5: Run the suite to verify it passes**

Run: `python3 tests/validate_skill.py`
Expected: `61/61 checks passed` (58 prior + R-DERIVE-01; R-DERIVE-02/03 land in Tasks 2/3 — if running before those, expect 59). Confirm R-DERIVE-01 PASS and no prior check regressed (R-MANIFEST-06 still green — we added a constant, didn't change the four it mirrors).

- [ ] **Step 6: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add scripts/manifest.py tests/validate_skill.py
git commit -m "feat(consolidation): DERIVES_FROM graph + generation_order + R-DERIVE-01"
```

---

### Task 2: Derivation contract + dependency-ordered batching in `refs/quality-loops.md` + R-DERIVE-02

**Files:**
- Modify: `refs/quality-loops.md` (add a "Derivation contract" subsection; rewrite the batching grouping ~lines 63–86 to be dependency-ordered AND cover all 15)
- Modify: `tests/validate_skill.py` (add R-DERIVE-02)

**Interfaces:**
- Consumes: `manifest.generation_order()`, `manifest.DERIVES_FROM` from Task 1.
- Produces: the generate-cycle rule that derived artifacts transform their source; the corrected batching grouping.

- [ ] **Step 1: Write the failing check**

R-DERIVE-02 enforces the *code-level* order guarantee plus the *documented* contract (parsing the free-prose batch groups reliably is brittle — instead assert the ref states the rule and references the mechanism, and that the mechanism is valid). Add to `tests/validate_skill.py` after R-DERIVE-01:

```python
@check("R-DERIVE-02: quality-loops states the derivation contract + sources-before-derivatives, and generation_order backs it")
def t_derivation_contract():
    txt = read("refs/quality-loops.md")
    low = txt.lower()
    # the contract: derived artifacts transform their source, not re-research
    assert "derivation contract" in low, "quality-loops.md must carry a 'Derivation contract' subsection"
    assert "generation_order" in txt, "quality-loops.md must reference manifest.generation_order() as the ordering authority"
    assert ("source" in low and "before" in low and ("derivativ" in low or "derived" in low)), \
        "quality-loops.md must state that sources are generated before their derivatives"
    assert ("transform" in low or "do not re-research" in low or "not re-research" in low), \
        "quality-loops.md must state derived artifacts transform the source (not re-research)"
    # every derived slug is named in the ref so a builder knows its source
    m = _load_script("scripts/manifest.py", "manifest_der2")
    for derived, src in m.DERIVES_FROM.items():
        assert derived in txt, f"quality-loops.md must name derived artifact {derived}"
    # the mechanism is valid (topological — reuses Task 1 guarantee, fails loudly if it regressed)
    m.generation_order()
```

- [ ] **Step 2: Run the suite to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL on R-DERIVE-02 (`quality-loops.md must carry a 'Derivation contract' subsection`).

- [ ] **Step 3: Add the Derivation contract subsection**

In `refs/quality-loops.md`, add this subsection immediately BEFORE the "## Generation batching" section (before line 63):

```markdown
## Derivation contract (single-source-of-record)

Some artifacts are **derived**: they are generated FROM another artifact (their *source of record*),
not independently researched. The map lives in `scripts/manifest.py` as `DERIVES_FROM`, and
`manifest.generation_order()` returns the artifacts in an order where **every source is generated
before its derivatives**. Batching (below) and any full-build MUST follow that order.

| Source of record | Derived from it | Transform |
|------------------|-----------------|-----------|
| `01-brief` (narrative of record) | `00-executive-summary` | rollup of 01's narrative **plus** the manifest Next Steps & Blockers register + confidence rollup (00-only) |
| `01-brief` | `02-slide-summary` | condense 01 to a one-screen slide deck |
| `01-brief` | `11-solution-infographic` | render 01's problem/solution/outcomes/built-on as the solution infographic |
| `01-brief` | `14-exec-infographic` | render 01's exec narrative as the leadership poster |
| `04-internal-faq` | `05-external-faq` | partner-safe subset: emit only content 04 does not mark internal-only |
| `06-license-entitlements` | `07-addon-tiering` (Required tier) | ground 07's **Required** tier in 06's entitlement table; Recommended/Optional stay 07-authored |

**Contract for generating a derived artifact:** take its already-generated source as explicit input;
**transform it, do not re-research.** Introduce no claim absent from the source. Where the source is
silent, **flag a gap — never invent.** The claim-verification loop still applies (fact drift is caught
regardless). `12-marketecture`, `13-demand-plan`, `03`, `08`, `09`, `10` are NOT derived — they are
authored from effort sources.
```

- [ ] **Step 4: Rewrite the batching grouping to be dependency-ordered AND cover all 15**

Replace the existing grouping bullet (currently lines ~72–77, groups (a)–(e) covering only 13 slugs — it omits 13-demand-plan and 14-exec-infographic) with:

```markdown
- A dependency-ordered grouping (sources before derivatives; see the Derivation contract above and
  `manifest.generation_order()`):
  **(a) sources first** -- 01-brief, 04-internal-faq, 06-license-entitlements;
  **(b) independents** -- 03-internal-enablement, 08-setup-guide, 09-org-provisioning-validation,
  10-partner-profile-pov, 12-marketecture, 13-demand-plan;
  **(c) derivatives** -- 02-slide-summary, 05-external-faq (subset of 04), 07-addon-tiering
  (Required tier from 06), 11-solution-infographic, 14-exec-infographic;
  **(d) 00-executive-summary LAST** -- its rollup reflects the others' real status/confidence/blockers.
```

(Batch (a) MUST precede (c) and (d); (b) may run any time after (a). This replaces the old arbitrary A/B/C/D grouping and closes the stale-13 gap.)

- [ ] **Step 5: Run the suite to verify it passes**

Run: `python3 tests/validate_skill.py`
Expected: R-DERIVE-02 PASS; no regression. (R-DOC-01 greps for family-size claims — the new table names artifacts but adds no "N artifacts" count string, so it stays green; if R-DOC-01 flags a count, reword to avoid a bare "N artifacts/deliverables" literal.)

- [ ] **Step 6: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add refs/quality-loops.md tests/validate_skill.py
git commit -m "feat(consolidation): derivation contract + dependency-ordered batching + R-DERIVE-02"
```

---

### Task 3: Source-naming template headers + `refs/artifact-templates.md` map + R-DERIVE-03

**Files:**
- Modify: the six derived templates — `templates/00-executive-summary.md`, `templates/02-slide-summary.md`, `templates/05-external-faq.md`, `templates/07-addon-tiering.md`, `templates/11-solution-infographic.md`, `templates/14-exec-infographic.md`
- Modify: `refs/artifact-templates.md` (add/normalize the derivation map)
- Modify: `tests/validate_skill.py` (add R-DERIVE-03)

**Interfaces:**
- Consumes: `manifest.DERIVES_FROM`.
- Produces: each derived template carries a `<!-- DERIVED: from <source-slug> ... -->` comment naming its actual source; artifact-templates.md documents the graph.

- [ ] **Step 1: Write the failing check**

Add to `tests/validate_skill.py` after R-DERIVE-02:

```python
@check("R-DERIVE-03: every derived template carries a DERIVED header naming its actual source slug")
def t_derived_headers():
    m = _load_script("scripts/manifest.py", "manifest_der3")
    for derived, src in m.DERIVES_FROM.items():
        body = read(f"templates/{derived}.md")
        head = body[:600]  # top-of-file region (comment block + H1 + gap banner)
        assert "DERIVED" in head.upper(), f"{derived}.md missing a DERIVED header comment"
        assert src in head, f"{derived}.md DERIVED header must name its source slug {src}"
    # artifact-templates.md documents the map
    ref = read("refs/artifact-templates.md")
    assert "DERIVES_FROM" in ref or "derivation" in ref.lower(), \
        "artifact-templates.md must document the derivation map"
    for derived, src in m.DERIVES_FROM.items():
        assert derived in ref and src in ref, f"artifact-templates.md must name {derived} and its source {src}"
```

- [ ] **Step 2: Run the suite to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL on R-DERIVE-03 (some derived template lacks a DERIVED header naming its source — 05 and 02 may already have derivation comments; 00/07/11/14 likely do not).

- [ ] **Step 3: Add/normalize the DERIVED header comment on each of the six templates**

Placement follows the existing convention: the comment sits in the **top comment block ABOVE the H1**, alongside the `<!-- VOICE: ... -->` comment (see `templates/05-external-faq.md`, which already has both). Do NOT place it after the H1 or inside the gap-banner. The R-DERIVE-03 check reads the first 600 chars, which covers this region. Use the exact source slug. Examples (adapt the transform phrase per the Derivation contract table):

- `templates/00-executive-summary.md`: `<!-- DERIVED: rollup of 01-brief's narrative PLUS manifest Next Steps & Blockers + confidence rollup. Transform 01, do not re-research. -->`
- `templates/02-slide-summary.md`: `<!-- DERIVED: from 01-brief -- condense to a one-screen slide deck. Do not re-research. -->`
- `templates/05-external-faq.md`: `<!-- DERIVED: from 04-internal-faq -- partner-safe subset; never include content 04 marks internal-only. -->`
- `templates/07-addon-tiering.md`: `<!-- DERIVED: Required tier grounded in 06-license-entitlements; Recommended/Optional are 07-authored. -->`
- `templates/11-solution-infographic.md`: `<!-- DERIVED: from 01-brief -- render problem/solution/outcomes/built-on. Do not re-research. -->`
- `templates/14-exec-infographic.md`: `<!-- DERIVED: from 01-brief -- render the exec narrative as the leadership poster. Do not re-research. -->`

If a template already has a derivation comment (05, 02), REPLACE it with the normalized form above (keep it a single HTML comment; must contain "DERIVED" and the source slug). Do NOT touch the gap-banner header, tokens, or body — comment only. Verify no `{{TOKEN}}` was disturbed: R-TEST-02 must stay green.

- [ ] **Step 4: Document the map in `refs/artifact-templates.md`**

Add a "Derivation map" subsection that names each derived artifact and its source (mirroring the Derivation contract table) and points to `DERIVES_FROM` in `manifest.py` as the machine-readable source of truth. This satisfies the R-DERIVE-03 assertions that the ref names every `derived`+`src` and references `DERIVES_FROM`/"derivation".

- [ ] **Step 5: Run the suite to verify it passes**

Run: `python3 tests/validate_skill.py`
Expected: R-DERIVE-03 PASS; R-TEST-02 (token hygiene), R-TPL-02 (gap-banner header present) still green — the comment sits between H1 and the banner and disturbs neither. Full suite green (→ 61/61).

- [ ] **Step 6: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add templates/00-executive-summary.md templates/02-slide-summary.md templates/05-external-faq.md templates/07-addon-tiering.md templates/11-solution-infographic.md templates/14-exec-infographic.md refs/artifact-templates.md tests/validate_skill.py
git commit -m "feat(consolidation): source-naming template headers + derivation map + R-DERIVE-03"
```

---

### Task 4: Dogfood verification against the healthcare effort

**Files:**
- Read-only: `~/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/` (existing effort artifacts)
- Create: `docs/superpowers/acceptance/2026-07-16-consolidation-dogfood.md` (findings)

**Interfaces:**
- Consumes: the shipped Tasks 1–3 behavior; the existing effort as ground truth.
- Produces: a findings doc confirming the derivation model holds on real artifacts (or flagging where it doesn't).

- [ ] **Step 1: Confirm the effort exists and inventory its artifacts**

Run:
```bash
ls ~/claude-projects/ps-npi-efforts/summer-26/agentforce-healthcare-oem/*.md 2>/dev/null | sed 's|.*/||'
```
Expected: the effort's artifact `.md` files (00–14 or a subset). If the effort is absent, record that and treat this task as a **static** verification (assert the graph/contract/headers only); do not fabricate an effort.

- [ ] **Step 2: Verify each derivation relationship holds in the real bytes**

For the effort's artifacts, check consistency (read + compare; this is judgment, capture findings):
- **05 vs 04:** does `05-external-faq` contain any content that `04-internal-faq` marks internal-only (channel-conflict specifics, open questions)? It must NOT. Record pass/leak.
- **07 vs 06:** does `07-addon-tiering`'s Required tier match `06-license-entitlements`' required entitlements (no diverging/restated SKU list)? Record.
- **02 / 11 / 14 vs 01:** do the slide/infographic/poster narratives assert anything ABSENT from `01-brief`? They should be condensations/renders, not new claims. Record any drift.
- **00 vs 01 + manifest:** does `00-executive-summary` carry the Next Steps & Blockers register + confidence rollup (its unique manifest-fed content) AND stay consistent with 01's narrative? Record.

- [ ] **Step 3: Run the full suite as a regression gate**

Run: `python3 tests/validate_skill.py`
Expected: full suite green (61/61), R-DERIVE-01/02/03 included.

- [ ] **Step 4: Write the findings doc**

Create `docs/superpowers/acceptance/2026-07-16-consolidation-dogfood.md` capturing: the effort inventoried, each derivation relationship's pass/flag with the evidence (quoted lines where a leak/drift was found), and any genuine gaps → new BACKLOG candidates. Be honest: if a real artifact violates the contract, that's a finding, not a failure of the plan — record it.

- [ ] **Step 5: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add docs/superpowers/acceptance/2026-07-16-consolidation-dogfood.md
git commit -m "test(consolidation): dogfood the derivation model vs the healthcare effort"
```

---

## Notes for the executor

- **`DERIVES_FROM` has ONE home** (`manifest.py`); the validator reads it via `_load_script`, never re-declares it. This avoids a second source of truth (the mistake R-MANIFEST-06 exists to prevent).
- **Order of tasks matters:** Task 1 (the map + `generation_order`) is the foundation Tasks 2 & 3 assert against. Run them in order.
- **No template body/token changes** — Task 3 adds only HTML comments between H1 and the gap-banner. If R-TEST-02 or R-TPL-02 goes red, you touched more than the comment; revert and redo.
- **No artifact count change** — `ARTIFACT_REGISTRY` stays 15. If any registry-derived check (R-TPL-01, R-MANIFEST-01) moves, something structural was altered by accident; stop and diagnose.
- **The suite is the contract** — every task ends on a green `python3 tests/validate_skill.py` and a commit. Pre-commit hook runs it anyway.
- **Memory is stale** (says 13 artifacts / 44 checks; real = 15 / 58→61). Fix memory at close-out, not mid-plan.
