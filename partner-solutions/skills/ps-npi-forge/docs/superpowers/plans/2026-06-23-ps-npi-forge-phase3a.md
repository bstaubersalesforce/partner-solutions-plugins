# PS-NPI-FORGE Phase 3a — The 11 Artifact Templates

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the 11 artifact templates (`templates/NN-*.md`) that define the section grammar, `{{TOKEN}}` slots, shared gap-banner header, and confidence/sources footer for every PS-NPI-FORGE deliverable — and gate them with token-hygiene + template-registry-parity checks. This phase delivers the *skeletons the generator fills*; the generate→refine→validate cycle that fills them is **Phase 3b** (separate plan).

**Architecture:** Markdown templates with `{{UPPER_SNAKE}}` tokens (matching the Phase-1 `templates/manifest.yaml` convention and the pie-poc-forge token style). One template per artifact slug in `ARTIFACT_REGISTRY`. Each template carries a shared **gap-banner header** (status · confidence · gaps) and a **footer** (sources · confidence rationale), so gaps and confidence are first-class in every artifact (spec §3, §3.1, §3.2). The validation suite (currently 17/17) grows: token hygiene, template-registry parity (every registry slug has a template), and the shared header/footer convention check. No executable generation code this phase.

**Tech Stack:** Markdown templates; Python 3 stdlib validation harness (extend `tests/validate_skill.py`).

## Global Constraints

- **Skill location:** `~/.claude/skills/ps-npi-forge/` (own git repo; remote `origin` → private `github.com/bstaubersalesforce/ps-npi-forge`).
- **Python:** stdlib only. Suite runs `python3 tests/validate_skill.py`; must stay green and grow.
- **Token convention:** every `{{TOKEN}}` is `UPPER_SNAKE_CASE` (`[A-Z0-9_]+`), balanced braces. (This is enforced by the new R-TEST-02 check; it mirrors pie-poc-forge.)
- **ARTIFACT_REGISTRY (the 11 slugs, verbatim — already in `scripts/manifest.py` + `tests/validate_skill.py`):** `00-executive-summary`, `01-brief`, `02-slide-summary`, `03-internal-enablement`, `04-internal-faq`, `05-external-faq`, `06-license-entitlements`, `07-addon-tiering`, `08-setup-guide`, `09-org-provisioning-validation`, `10-partner-profile-pov`.
- **One template per slug:** `templates/<slug>.md` (e.g., `templates/00-executive-summary.md`).
- **Shared gap-banner header (every template, verbatim — top of file, after the H1):**
  ```
  > **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
  >
  > {{GAP_BANNER}}
  ```
  `{{GAP_BANNER}}` renders either "No open gaps." or a bulleted list of gaps, each `⚠ Gap: <item> — <next step>; owner: <owner>` (spec §3.1). The generator (Phase 3b) fills it from the manifest placeholders.
- **Shared footer (every template, verbatim — bottom of file):**
  ```
  ---
  **Sources:** {{SOURCES}}
  **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
  ```
- **Two registers (spec §1, from `refs/voice-and-style.md`):** NARRATIVE artifacts (00, 01, 02, 03, 05, 10) carry a voice reminder comment; REFERENCE artifacts (04, 06, 07, 08, 09) carry a factual reminder comment. The reminder is an HTML comment at the top: `<!-- VOICE: narrative — first-person exec/architect McKinsey register; see refs/voice-and-style.md -->` or `<!-- VOICE: reference — factual/precise; do not editorialize; see refs/voice-and-style.md -->`.
- **Pricing out of scope:** SKU/add-on tables surface *which* SKUs exist; price & discount cells are literal placeholder text `{{PRICE_PENDING}}` / `{{DISCOUNT_PENDING}}` — never a computed number.
- **Official docs only** for technical-guidance templates (08, 09): any resource/link slot is labeled to accept official Salesforce docs only.
- **No generation/fetch code this phase:** templates are static markdown. Do not add WebFetch/`sf`/Slack/generation logic (Phases 3b/4/6).
- **ASCII note:** the gap-banner uses `·` (middle dot, U+00B7) and `—` (em dash) and `⚠` deliberately as *rendered* punctuation — these are allowed in template BODIES (they are display content, not code). Do NOT force templates to ASCII. (The Phase-2 ASCII gate was for refs/, not templates/.)

---

### Task 1: Shared conventions doc + token-hygiene gate + the two anchor templates (00, 01)

**Files:**
- Create: `~/.claude/skills/ps-npi-forge/refs/artifact-templates.md` (the grammar/convention reference, lazy-loaded)
- Create: `~/.claude/skills/ps-npi-forge/templates/00-executive-summary.md`
- Create: `~/.claude/skills/ps-npi-forge/templates/01-brief.md`
- Modify: `~/.claude/skills/ps-npi-forge/SKILL.md` (reference `refs/artifact-templates.md`)
- Modify: `~/.claude/skills/ps-npi-forge/tests/validate_skill.py` (add `TOKEN_RE` + R-TEST-02 token hygiene)

**Interfaces:**
- Consumes: `check()`, `read()`, `exists()`, `os`, `re`, `SKILL` from Phase 1; `EXPECTED_REFS` from Phase 2.
- Produces: `refs/artifact-templates.md` (referenced by SKILL.md, added to `EXPECTED_REFS`); two templates; `TOKEN_RE` + `R-TEST-02` (token hygiene over `templates/*.md`). The template-registry parity check arrives in Task 4 once all 11 exist.

- [ ] **Step 1: Write the failing test** (append to `tests/validate_skill.py` before `# ---- runner`)

```python
# ---- R-TEST-02: token hygiene over templates/ ---------------------------
TOKEN_RE = re.compile(r"\{\{([^{}]*)\}\}")

@check("R-TEST-02: every {{TOKEN}} in templates/*.md is UPPER_SNAKE_CASE with balanced braces")
def t_token_hygiene():
    tdir = os.path.join(SKILL, "templates")
    assert os.path.isdir(tdir), "templates/ directory missing"
    bad = []
    for f in os.listdir(tdir):
        if not f.endswith(".md"):
            continue
        for tok in TOKEN_RE.findall(read(f"templates/{f}")):
            if not re.fullmatch(r"[A-Z0-9_]+", tok):
                bad.append(f"templates/{f}: {{{{{tok}}}}}")
    assert not bad, f"malformed tokens: {bad}"
```

- [ ] **Step 2: Add `refs/artifact-templates.md` to `EXPECTED_REFS`**

In `tests/validate_skill.py`, change the `EXPECTED_REFS` list to include the new ref:

```python
EXPECTED_REFS = [
    "refs/voice-and-style.md",
    "refs/intake-source-map.md",
    "refs/artifact-templates.md",
]
```

- [ ] **Step 3: Run the suite to verify it FAILS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on `R-ARCH-03` (`expected refs missing: ['refs/artifact-templates.md']`). R-TEST-02 itself passes vacuously now (no malformed tokens yet) — that's fine; it becomes meaningful as templates land.

- [ ] **Step 4: Create `refs/artifact-templates.md`** (verbatim)

```markdown
# Artifact templates

The 11 artifact skeletons live in `templates/<slug>.md`, one per `ARTIFACT_REGISTRY` slug. Each is
a markdown file with `{{UPPER_SNAKE}}` tokens the generator (Phase 3b) fills from the effort
manifest and sources. This ref documents the shared conventions; the per-artifact grammar is in
each template file.

## Shared conventions (every template)

- **Voice comment** (top, HTML comment): narrative artifacts (00, 01, 02, 03, 05, 10) declare the
  first-person exec/architect McKinsey register; reference artifacts (04, 06, 07, 08, 09) declare
  the factual register. See [voice-and-style.md](voice-and-style.md).
- **Gap-banner header** (after the H1): a blockquote carrying `{{STATUS}}`, `{{CONFIDENCE}}`,
  `{{CONFIDENCE_RATIONALE}}`, and `{{GAP_BANNER}}`. `{{GAP_BANNER}}` renders "No open gaps." or a
  bulleted list, each `Gap: <item> -- <next step>; owner: <owner>`. Gaps are first-class: a missing
  Template ID, a PENDING price, an ungrounded claim each surface here and roll up into 00's Next
  Steps & Blockers register.
- **Footer**: a horizontal rule, then `{{SOURCES}}` and the confidence line again. Sources are what
  the claim-verification loop checks against (Phase 3b).
- **Tokens are UPPER_SNAKE.** Price/discount cells are literal `{{PRICE_PENDING}}` /
  `{{DISCOUNT_PENDING}}` -- pricing is out of scope, never a computed number.

## The registry

| Slug | Register | Notes |
|------|----------|-------|
| 00-executive-summary | narrative | front door: vision, top 3-6 use cases, IPP summary, Next Steps & Blockers, rollup |
| 01-brief | narrative | the 8-section product narrative |
| 02-slide-summary | narrative | one-screen summary derived from 01 |
| 03-internal-enablement | narrative | positioning, motion rules, entitlement implications |
| 04-internal-faq | reference | PS/NPI Q&A incl. OEM/VAR/shared-org/packageability |
| 05-external-faq | narrative | partner-facing, safe subset derived from 04 |
| 06-license-entitlements | reference | licenses/PSLs/features/storage from parent, deltas flagged |
| 07-addon-tiering | reference | Required/Recommended/Optional, minimalist |
| 08-setup-guide | reference | Basic Info/TrialForce/2GP scratch/managed-pkg; official docs only |
| 09-org-provisioning-validation | reference | static Template-ID check + optional live org diff |
| 10-partner-profile-pov | narrative | whitespace POV; Tier B always, Tier C opt-in |

## How the generator uses these (Phase 3b, for context)

Phase 3b's cycle draft -> refine -> validate fills the tokens: draft from knowledge, refine against
sources (recording them in `{{SOURCES}}`), then the quality loops set `{{CONFIDENCE}}` +
`{{CONFIDENCE_RATIONALE}}` and populate `{{GAP_BANNER}}`. Until Phase 3b lands, the templates are
inert skeletons.
```

- [ ] **Step 5: Wire the ref into SKILL.md**

Add this line in SKILL.md, immediately after the "Voice & style:" line added in Phase 2:

```markdown
**Artifacts:** the 11 deliverables are generated from skeletons in `templates/` per the grammar in
[refs/artifact-templates.md](refs/artifact-templates.md).
```

- [ ] **Step 6: Create `templates/00-executive-summary.md`** (verbatim)

```markdown
<!-- VOICE: narrative — first-person exec/architect McKinsey register; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — Executive Summary

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

**Release:** {{RELEASE}} · **Parent SKU:** {{PARENT_SKU}} · **Partner motion:** {{PARTNER_MOTION}}

## The vision
{{VISION}}

## Why this matters to our partners
{{PURPOSE}}

## Top use cases
{{TOP_USE_CASES}}

## Ideal partner profile (summary)
{{IPP_SUMMARY}}

## Key next steps & blockers
{{NEXT_STEPS_AND_BLOCKERS}}

## Effort status & confidence rollup
{{STATUS_ROLLUP}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 7: Create `templates/01-brief.md`** (verbatim — the canonical 8-section grammar from the sample Quip docs)

```markdown
<!-- VOICE: narrative — first-person exec/architect McKinsey register; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — Use-Case & Details Brief

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

## What is {{PRODUCT_NAME}}?
{{WHAT_IS}}

## What value does {{PRODUCT_NAME}} offer partners?
{{VALUE_TO_PARTNERS}}

## Why is {{PRODUCT_NAME}} different?
{{WHY_DIFFERENT}}

## Who is {{PRODUCT_NAME}} for?
{{WHO_FOR}}

## What can ISVs build with {{PRODUCT_NAME}}?
{{WHAT_ISVS_BUILD}}

## What are the opportunities for {{PRODUCT_NAME}}?
{{OPPORTUNITIES}}

## Market & TAM
{{MARKET_TAM}}

## Additional resources
{{RESOURCES}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 8: Run the suite to verify all PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `18/18 checks passed` (17 prior + R-TEST-02), exit 0. (R-ARCH-03 now passes — the ref exists; R-ARCH-04 still passes — the ref is referenced.)

- [ ] **Step 9: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add refs/artifact-templates.md templates/00-executive-summary.md templates/01-brief.md SKILL.md tests/validate_skill.py
git commit -m "feat: add artifact-templates ref, token-hygiene gate, and 00/01 templates"
```

---

### Task 2: Remaining narrative templates (02, 03, 05, 10)

**Files:**
- Create: `templates/02-slide-summary.md`, `templates/03-internal-enablement.md`, `templates/05-external-faq.md`, `templates/10-partner-profile-pov.md`

**Interfaces:**
- Consumes: the shared conventions from Task 1.
- Produces: four narrative templates. No new check (Task 1's R-TEST-02 now covers them; Task 4's parity check will require them).

- [ ] **Step 1: Create `templates/02-slide-summary.md`** (verbatim)

```markdown
<!-- VOICE: narrative — first-person exec/architect McKinsey register; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — One-Screen Summary

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

## The one-liner
{{ONE_LINER}}

## Three things to know
{{THREE_THINGS}}

## Who it's for
{{WHO_FOR_SHORT}}

## The partner play
{{PARTNER_PLAY}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 2: Create `templates/03-internal-enablement.md`** (verbatim)

```markdown
<!-- VOICE: narrative — first-person exec/architect McKinsey register; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — Internal Enablement

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

## Positioning (how we talk about it)
{{POSITIONING}}

## The partner motion & rules
{{MOTION_RULES}}

## Entitlement implications
{{ENTITLEMENT_IMPLICATIONS}}

## Objection handling
{{OBJECTION_HANDLING}}

## Where I'd push (my take)
{{MY_TAKE}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 3: Create `templates/05-external-faq.md`** (verbatim — note the derived-from-04 reminder)

```markdown
<!-- VOICE: narrative — first-person exec/architect McKinsey register; see refs/voice-and-style.md -->
<!-- DERIVED: this is a safe subset of 04-internal-faq; never include internal-only detail -->
# {{PRODUCT_NAME}} — Partner FAQ

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

## What is {{PRODUCT_NAME}}?
{{FAQ_WHAT_IS}}

## What can I build and sell with it?
{{FAQ_BUILD_SELL}}

## How do I get started?
{{FAQ_GET_STARTED}}

## Where do I find more?
{{FAQ_RESOURCES}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 4: Create `templates/10-partner-profile-pov.md`** (verbatim — Tier B always, Tier C opt-in)

```markdown
<!-- VOICE: narrative — first-person exec/architect McKinsey register; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — Ideal Partner Profile & Target Partners (POV)

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

## My thesis: where this wins
{{THESIS}}

## The whitespace (great embedded/OEM fit *because* poor direct-SF target)
{{WHITESPACE_LOGIC}}

## Ideal partner archetypes (Tier B)
{{ARCHETYPES}}

## Illustrative example companies (Tier B — verify)
{{ILLUSTRATIVE_COMPANIES}}

## Researched candidate partners (Tier C — opt-in, cited)
{{RESEARCHED_CANDIDATES}}

## How to qualify a candidate
{{QUALIFY_CRITERIA}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 5: Run the suite**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `18/18 checks passed` (R-TEST-02 now also scans these four; no new check number).

- [ ] **Step 6: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add templates/02-slide-summary.md templates/03-internal-enablement.md templates/05-external-faq.md templates/10-partner-profile-pov.md
git commit -m "feat: add narrative artifact templates (02 slide, 03 enablement, 05 external-faq, 10 partner-pov)"
```

---

### Task 3: Reference templates (04, 06, 07, 08, 09)

**Files:**
- Create: `templates/04-internal-faq.md`, `templates/06-license-entitlements.md`, `templates/07-addon-tiering.md`, `templates/08-setup-guide.md`, `templates/09-org-provisioning-validation.md`

**Interfaces:**
- Consumes: shared conventions from Task 1.
- Produces: five reference templates (factual register).

- [ ] **Step 1: Create `templates/04-internal-faq.md`** (verbatim)

```markdown
<!-- VOICE: reference — factual/precise; do not editorialize; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — Internal FAQ

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

## Partner motion (OEM / VAR / ISVforce)
{{FAQ_MOTION}}

## Shared-org restrictions
{{FAQ_SHARED_ORG}}

## Packageability & timing
{{FAQ_PACKAGEABILITY}}

## Licensing & entitlements
{{FAQ_LICENSING}}

## Open questions
{{FAQ_OPEN_QUESTIONS}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 2: Create `templates/06-license-entitlements.md`** (verbatim — the parent-derived technical payload)

```markdown
<!-- VOICE: reference — factual/precise; do not editorialize; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — License & Entitlement Details

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

**Parent product:** {{PARENT_SKU}} · **Embedded/OEM product:** {{PRODUCT_NAME}}

## Entitlement composition (derived from parent)
{{ENTITLEMENT_COMPOSITION}}

## Licenses
{{LICENSES}}

## Permission Set Licenses (PSLs)
{{PSLS}}

## Features
{{FEATURES}}

## Storage
{{STORAGE}}

## Naming differences & deltas vs. parent
{{DELTAS_AND_NAMING}}

## Human-confirmation checklist
{{CONFIRMATION_CHECKLIST}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 3: Create `templates/07-addon-tiering.md`** (verbatim — minimalist Required/Recommended/Optional; pricing pending)

```markdown
<!-- VOICE: reference — factual/precise; do not editorialize; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — Add-On Tiering

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

**Principle:** recommend only what is *truly required*. Pricing is out of scope — price and
discount columns stay as pending placeholders.

## Required
{{TIER_REQUIRED}}

## Recommended
{{TIER_RECOMMENDED}}

## Optional
{{TIER_OPTIONAL}}

## SKU reference (which SKUs/add-ons exist)

| SKU / Add-on | Tier | Why | Price | Discount |
|--------------|------|-----|-------|----------|
| {{SKU_ROW_EXAMPLE}} | {{TIER_EXAMPLE}} | {{WHY_EXAMPLE}} | {{PRICE_PENDING}} | {{DISCOUNT_PENDING}} |

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 4: Create `templates/08-setup-guide.md`** (verbatim — official docs only)

```markdown
<!-- VOICE: reference — factual/precise; do not editorialize; see refs/voice-and-style.md -->
<!-- OFFICIAL DOCS ONLY: every link here must be an official Salesforce source -->
# {{PRODUCT_NAME}} — Setup Guide

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

## Basic information
{{BASIC_INFO}}

## Template ID
{{TEMPLATE_ID}}

## TrialForce orgs (TSO)
{{TRIALFORCE}}

## Scratch orgs for 2GP
{{SCRATCH_ORGS_2GP}}

## Features to add to the scratch org definition
{{SCRATCH_DEF_FEATURES}}

## Get the org ready for the managed package
{{MANAGED_PACKAGE_PREP}}

## Official documentation
{{OFFICIAL_DOCS}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 5: Create `templates/09-org-provisioning-validation.md`** (verbatim — static always, live optional)

```markdown
<!-- VOICE: reference — factual/precise; do not editorialize; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — Org-Provisioning Validation

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

## Static check (always)
{{STATIC_CHECK}}

## Template ID status
{{TEMPLATE_ID_STATUS}}

## Expected entitlement set (from 06)
{{EXPECTED_ENTITLEMENTS}}

## Live org diff (optional — when an org exists)
{{LIVE_ORG_DIFF}}

## Result & next step
{{VALIDATION_RESULT}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
```

- [ ] **Step 6: Run the suite**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `18/18 checks passed`.

- [ ] **Step 7: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add templates/04-internal-faq.md templates/06-license-entitlements.md templates/07-addon-tiering.md templates/08-setup-guide.md templates/09-org-provisioning-validation.md
git commit -m "feat: add reference artifact templates (04 internal-faq, 06 license, 07 add-on, 08 setup, 09 org-validation)"
```

---

### Task 4: Template-registry parity + shared header/footer convention checks

**Files:**
- Modify: `~/.claude/skills/ps-npi-forge/tests/validate_skill.py` (add R-TPL-01 + R-TPL-02)

**Interfaces:**
- Consumes: `ARTIFACT_REGISTRY`, `check()`, `read()`, `exists()`, `os`.
- Produces: `R-TPL-01` (every registry slug has `templates/<slug>.md`) + `R-TPL-02` (every artifact template carries the gap-banner tokens + footer). These gate all 11 templates as a set. Also closes BACKLOG **B5** spirit at the template level: every template filename is a known registry slug (no orphan templates).

- [ ] **Step 1: Write the failing tests** (append before `# ---- runner`)

```python
# ---- R-TPL-01/02: artifact-template registry parity + shared convention -
@check("R-TPL-01: every ARTIFACT_REGISTRY slug has a templates/<slug>.md, and no template is an unknown slug")
def t_template_registry_parity():
    missing = [f"templates/{s}.md" for s in ARTIFACT_REGISTRY if not exists(f"templates/{s}.md")]
    assert not missing, f"artifact templates missing: {missing}"
    tdir = os.path.join(SKILL, "templates")
    known = set(ARTIFACT_REGISTRY) | {"manifest"}  # manifest.yaml is infra, not an artifact
    unknown = []
    for f in os.listdir(tdir):
        if not f.endswith(".md"):
            continue
        slug = f[:-3]
        if slug not in known:
            unknown.append(f"templates/{f}")
    assert not unknown, f"template files that are not a known artifact slug: {sorted(unknown)}"

@check("R-TPL-02: every artifact template carries the shared gap-banner header and sources/confidence footer")
def t_template_shared_convention():
    bad = []
    for s in ARTIFACT_REGISTRY:
        body = read(f"templates/{s}.md")
        for tok in ("{{STATUS}}", "{{CONFIDENCE}}", "{{CONFIDENCE_RATIONALE}}",
                    "{{GAP_BANNER}}", "{{SOURCES}}"):
            if tok not in body:
                bad.append(f"templates/{s}.md missing {tok}")
        if "VOICE:" not in body:
            bad.append(f"templates/{s}.md missing VOICE register comment")
    assert not bad, f"shared-convention violations: {bad}"
```

- [ ] **Step 2: Run the suite — expect PASS** (Tasks 1–3 created all 11 templates with the convention)

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `20/20 checks passed`, exit 0.

- [ ] **Step 3: Prove R-TPL-01 + R-TPL-02 can fail (sanity-gate)**

Run:
```bash
cd ~/.claude/skills/ps-npi-forge
# (a) orphan template slug -> R-TPL-01 fails
touch templates/99-bogus.md
python3 tests/validate_skill.py | grep -E "R-TPL-01|checks passed" ; echo "exit-a=${PIPESTATUS[0]}"
rm templates/99-bogus.md
# (b) a template missing a shared token -> R-TPL-02 fails
cp templates/01-brief.md /tmp/01-brief.bak
python3 - <<'PY'
p="templates/01-brief.md"; s=open(p).read().replace("{{GAP_BANNER}}","REMOVED")
open(p,"w").write(s)
PY
python3 tests/validate_skill.py | grep -E "R-TPL-02|checks passed"
cp /tmp/01-brief.bak templates/01-brief.md
python3 tests/validate_skill.py | tail -1
```
Expected: (a) prints a FAIL line for R-TPL-01 naming `templates/99-bogus.md`; (b) prints a FAIL line for R-TPL-02 naming `01-brief.md missing {{GAP_BANNER}}`; the final line reads `20/20 checks passed` after both files are restored.

- [ ] **Step 4: Confirm clean tree, then commit**

Run: `cd ~/.claude/skills/ps-npi-forge && git status --porcelain` — expect only `tests/validate_skill.py` modified (no stray `99-bogus.md`, `01-brief.md` restored).

```bash
cd ~/.claude/skills/ps-npi-forge
git add tests/validate_skill.py
git commit -m "test: gate the 11 artifact templates with registry-parity and shared-convention checks"
```

---

### Task 5: BACKLOG roadmap + close B5 note

**Files:**
- Modify: `~/.claude/skills/ps-npi-forge/BACKLOG.md`

**Interfaces:**
- Produces: BACKLOG with Phase 3a tracked and B5 resolved-at-template-level noted.

- [ ] **Step 1: Update the roadmap and B5**

In `BACKLOG.md`:
- Under "## Phase roadmap", replace the `- [ ] Phase 3 — ...` line with two lines:
  ```
  - [x] Phase 3a — the 11 artifact templates
  - [ ] Phase 3b — generate→refine→validate cycle + quality loops
  ```
- Append to the B5 line: ` (Partially addressed in Phase 3a: R-TPL-01 rejects template files whose slug is not in ARTIFACT_REGISTRY. The ref↔registry slug check for refs/ text remains for Phase 3b.)`

- [ ] **Step 2: Run the suite (no regression)**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `20/20 checks passed`.

- [ ] **Step 3: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add BACKLOG.md
git commit -m "docs: track Phase 3a complete; note B5 partial resolution at template level"
```

---

## Self-Review

**Spec coverage (Phase 3a scope):**
- 11 artifact templates, one per registry slug (spec §3) → Tasks 1–3 + R-TPL-01. ✅
- Each opens with a gap banner (status + confidence + gaps) (spec §3, §3.1) → shared header + R-TPL-02. ✅
- Confidence + rationale + sources first-class (spec §3.2) → header + footer tokens + R-TPL-02. ✅
- The 8-section brief grammar from the sample docs (spec §3 / pasted Quip docs) → `01-brief.md` Task 1 Step 7. ✅
- 05 derived from 04; 07 separate from 06; pricing-out-of-scope placeholders (spec §3.1) → DERIVED comment in 05, separate 06/07 templates, `{{PRICE_PENDING}}`/`{{DISCOUNT_PENDING}}` in 07. ✅
- Two registers (narrative vs reference) (spec §1) → VOICE comments + R-TPL-02 VOICE check. ✅
- Official docs only for 08/09 (spec §4) → OFFICIAL DOCS comment in 08. ✅
- Token hygiene (consistency w/ Phase 1 + pie-poc-forge) → R-TEST-02. ✅
- **Deferred (correctly out of Phase 3a):** the generate→refine→validate cycle + the four quality loops (Phase 3b); HTML render + Mermaid (Phase 5); canvas assembly (Phase 5); Slack (Phase 6); Org62/web fetch (Phases 4/6). Templates are inert skeletons — no generation/fetch code added.

**Placeholder scan:** All 11 templates + the ref are written in full in the plan. Checks assert specific tokens/slugs, not vague "has content." The `{{...}}` inside templates are intentional generator tokens, not plan placeholders. ✅

**Type consistency:** New check IDs are unique and continue the series (R-TEST-02, R-TPL-01, R-TPL-02). `EXPECTED_REFS` gains exactly the one new ref Task 1 creates. R-TPL-01's `known` set = `ARTIFACT_REGISTRY ∪ {manifest}`, so Phase-1's `templates/manifest.yaml` is not falsely flagged as an orphan template (it's `.yaml`, excluded by the `.md` filter anyway — double-safe). Shared header/footer tokens (`{{STATUS}}`, `{{CONFIDENCE}}`, `{{CONFIDENCE_RATIONALE}}`, `{{GAP_BANNER}}`, `{{SOURCES}}`) are identical across all 11 templates and exactly match R-TPL-02's assertion list. Final suite count: 17 (Phase 2) + R-TEST-02 + R-TPL-01 + R-TPL-02 = 20. ✅
```
