# PS-NPI-FORGE Phase 2 — Voice/Style & Intake Source-Map Refs

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the two lazy-loaded instruction refs that govern *how* every artifact is written and *where its inputs come from* — `refs/voice-and-style.md` and `refs/intake-source-map.md` — wire them into SKILL.md, and extend the validation suite to gate ref presence, no-orphans, and the binding content invariants from the spec.

**Architecture:** Markdown instruction refs (no executable code this phase — no live fetch yet; that is Phases 4/6). The refs are content the skill loads on demand. The validation suite grows two structural checks (expected-refs-exist, refs no-orphans) and content-invariant checks per ref, following the `pie-poc-forge` pattern. Phase 2 builds on Phase 1's SKILL.md + `tests/validate_skill.py` (currently 13/13).

**Tech Stack:** Markdown; Python 3 stdlib validation harness (extend `tests/validate_skill.py`).

## Global Constraints

- **Skill location:** `~/.claude/skills/ps-npi-forge/` (its own git repo, `main`, remote `origin` → private `github.com/bstaubersalesforce/ps-npi-forge`).
- **Python:** stdlib only. Suite runs `python3 tests/validate_skill.py`; full suite must stay green and grow.
- **Refs are lazy:** SKILL.md stays lean and *references* each ref by path; domain detail lives in the ref. R-ARCH-02 (already present) asserts every path referenced in SKILL.md exists.
- **Authorial voice (verbatim from spec §1):** first-person **Brandon-as-Salesforce-exec/architect**, **McKinsey register** (pyramid principle, MECE, action titles, "so what" up front). Narrative artifacts use this voice; **reference artifacts stay appropriately factual**.
- **Audience calibration (spec §1):** author assuming Salesforce-product fluency, but write outputs to serve **partner account managers (PAMs), the NPI team, and less-technical personas** — plain-language framing over jargon.
- **Six intake channels (spec §4):** Paste (baseline), Link/source-fetch, Org62, Slack channel, SF price-list catalog, Web research. Each **degrades gracefully** — absent ⇒ artifacts proceed with a flagged gap, never blocked.
- **Minimum viable input (spec §4):** the only required input is a **parent direct SKU reference**.
- **Official-docs allowlist (spec §4):** `help.salesforce.com`, `developer.salesforce.com`, `architect.salesforce.com`, Trailhead, Partner Community, Org62-internal tools. Non-official ⇒ flagged, excluded from technical guidance, never silently dropped.
- **Parent-SKU modeling spine (spec §4):** derive the Embedded/OEM entitlement set from the parent `Product2`, flag naming differences + deltas, apply partner-motion rules, derive minimalist add-on tiers; skill drafts and flags, human confirms.
- **Out of scope (unchanged from Phase 1):** pricing/discount determination; live Org62 writes; non-official doc sources; auto-publish to Slack without confirmation; silently dropping uncertainty.
- **No live fetch this phase:** the intake ref *documents* the channels and the access pattern; it does NOT implement WebFetch/`sf`/Slack calls (Phases 4/6). Do not add network or `sf` code.

---

### Task 1: `refs/voice-and-style.md` + content gate + SKILL.md wiring

**Files:**
- Create: `~/.claude/skills/ps-npi-forge/refs/voice-and-style.md`
- Modify: `~/.claude/skills/ps-npi-forge/SKILL.md` (add a "Voice & style" line referencing the ref)
- Modify: `~/.claude/skills/ps-npi-forge/tests/validate_skill.py` (append the R-VOICE check)

**Interfaces:**
- Consumes: `check()`, `read()`, `exists()` from `tests/validate_skill.py` (Phase 1).
- Produces: `refs/voice-and-style.md` referenced from SKILL.md; check `R-VOICE-01` asserting the ref exists and carries the voice/audience invariants. (The shared `EXPECTED_REFS` list + no-orphans check are added in Task 3, after both refs exist.)

- [ ] **Step 1: Write the failing test** (append to `tests/validate_skill.py`, immediately before the `# ---- runner` block)

```python
# ---- R-VOICE: authorial voice ref carries the spec's voice invariants ----
@check("R-VOICE-01: voice-and-style ref exists, is referenced by SKILL.md, and states the McKinsey/exec voice + audience + reference-factual rule")
def t_voice_ref():
    path = "refs/voice-and-style.md"
    assert exists(path), f"missing {path}"
    body = read(path).lower()
    for needle in ["mckinsey", "first-person", "exec", "architect",
                   "pyramid", "action title", "so what"]:
        assert needle in body, f"voice ref missing voice marker: {needle}"
    # audience calibration: PAM / NPI / less-technical
    assert "account manager" in body or "pam" in body, "voice ref missing PAM audience"
    assert "less-technical" in body or "non-technical" in body, "voice ref missing non-technical audience"
    # the narrative-vs-reference split must be explicit
    assert "reference artifact" in body and "factual" in body, \
        "voice ref must state that reference artifacts stay factual"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"
```

- [ ] **Step 2: Run the test to verify it FAILS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on `R-VOICE-01` with `missing refs/voice-and-style.md`.

- [ ] **Step 3: Create `refs/voice-and-style.md`** (verbatim)

```markdown
# Voice & style

The authorial register for ps-npi-forge artifacts. Load this before writing any narrative
artifact (00-executive-summary, 01-brief, 02-slide-summary, 03-internal-enablement,
05-external-faq, 10-partner-profile-pov). Reference artifacts (06, 07, 08, 09, and the
04-internal-faq) stay factual — see "Two registers" below.

## Who is speaking

Write in the **first-person voice of Brandon — a Salesforce exec/architect** in the Partner
Solutions / ISV program. The artifacts are his point of view and carry his authority and
judgment, not a neutral corporate-marketing voice. "I recommend," "my read is," "where I'd
push" are in-voice; "Salesforce is pleased to announce" is not.

## The McKinsey register

Structure every narrative artifact on the **pyramid principle**:

- **Answer first.** Lead with the "so what" — the single governing message — then support it.
  Never bury the conclusion under buildup.
- **MECE** groupings. Supporting points are mutually exclusive and collectively exhaustive — no
  overlap, no gaps.
- **Action titles.** Section headings and bullets state the *insight*, not the topic. Prefer
  "Free ingestion removes the #1 data-tax objection" over "Ingestion pricing."
- **Rule of three.** Group支持 points in threes where natural; cut the fourth-best point.
- **Top-down.** Each section opens with its governing sentence; detail follows.

## Audience calibration

**Author assuming Salesforce-product fluency** — you may use Data 360, PSL, 2GP, OEM/VAR, Flex
Credits without defining them in working notes. **But write the artifacts to serve partner
account managers (PAMs), the larger NPI team, and less-technical personas.** That means:

- Plain-language framing over jargon in the prose a PAM reads; expand an acronym on first use in
  any partner-facing artifact (02-slide-summary, 05-external-faq, 10-partner-profile-pov).
- Lead with the partner/commercial "so what," then the technical mechanism — not the reverse.
- Every claim should survive the question "would a PAM understand *why this matters to a
  partner*?"

## Two registers

- **Narrative artifacts** (00, 01, 02, 03, 05, 10): full McKinsey voice above — opinionated,
  action-titled, partner-lens.
- **Reference artifacts** (04-internal-faq, 06-license-entitlements, 07-addon-tiering,
  08-setup-guide, 09-org-provisioning-validation): stay **factual and precise**. State licenses,
  PSLs, features, storage, steps, and rules plainly. Do not editorialize entitlement or setup
  facts; the value here is accuracy, not persuasion. Opinion belongs in 02/03/10, not in a
  setup step.

## Always

- Mark every uncertainty in-voice with an owner and a next step (never silently smooth over a
  gap — see [intake-source-map.md](intake-source-map.md) and the manifest placeholders).
- Keep the partner-program lens constant: every artifact is written for the ISV/OEM partner
  motion, not for a direct-sales reader.
```

> Note: if the snippet above shows a stray non-ASCII character, normalize it — the body must be plain ASCII English (e.g., "Group supporting points in threes"). Verify with Step 4's grep.

- [ ] **Step 4: Wire the ref into SKILL.md and verify ASCII**

Add a line under the run-modes / lifecycle area of SKILL.md that references the ref. Edit SKILL.md to insert this line after the "## The effort lifecycle" section's final paragraph (before "## Run modes"):

```markdown
**Voice & style:** narrative artifacts use the first-person exec/architect McKinsey voice;
reference artifacts stay factual. See [refs/voice-and-style.md](refs/voice-and-style.md).
```

Then verify the ref is clean ASCII:

Run: `cd ~/.claude/skills/ps-npi-forge && LC_ALL=C grep -nP '[^\x00-\x7F]' refs/voice-and-style.md || echo "ASCII-CLEAN"`
Expected: `ASCII-CLEAN` (no non-ASCII bytes). If any line prints, fix that character and re-run.

- [ ] **Step 5: Run the suite to verify all PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `14/14 checks passed`, exit 0.

- [ ] **Step 6: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add refs/voice-and-style.md SKILL.md tests/validate_skill.py
git commit -m "feat: add voice-and-style ref (McKinsey exec voice, audience, two registers)"
```

---

### Task 2: `refs/intake-source-map.md` + content gate + SKILL.md wiring

**Files:**
- Create: `~/.claude/skills/ps-npi-forge/refs/intake-source-map.md`
- Modify: `~/.claude/skills/ps-npi-forge/SKILL.md` (add an "Intake" line referencing the ref)
- Modify: `~/.claude/skills/ps-npi-forge/tests/validate_skill.py` (append the R-INTAKE check)

**Interfaces:**
- Consumes: `check()`, `read()`, `exists()`.
- Produces: `refs/intake-source-map.md` referenced from SKILL.md; check `R-INTAKE-01` asserting the six channels, the official-docs allowlist, graceful degradation, the minimum-viable parent-SKU input, and the parent-SKU modeling spine are all documented.

- [ ] **Step 1: Write the failing test** (append before the `# ---- runner` block)

```python
# ---- R-INTAKE: intake source-map ref documents all six channels + rules ----
@check("R-INTAKE-01: intake-source-map ref exists, is referenced by SKILL.md, and documents the 6 channels, allowlist, graceful degradation, min-viable input, and parent-SKU spine")
def t_intake_ref():
    path = "refs/intake-source-map.md"
    assert exists(path), f"missing {path}"
    body = read(path).lower()
    # the six channels
    for needle in ["paste", "source-fetch", "org62", "slack", "price-list", "web research"]:
        assert needle in body, f"intake ref missing channel: {needle}"
    # official-docs allowlist domains
    for dom in ["help.salesforce.com", "developer.salesforce.com",
                "architect.salesforce.com", "trailhead", "partner community"]:
        assert dom in body, f"intake ref missing allowlist entry: {dom}"
    # graceful degradation + never-blocked
    assert ("graceful" in body or "degrade" in body), "intake ref missing graceful-degradation concept"
    assert ("never blocked" in body or "flagged gap" in body or "flag a gap" in body), \
        "intake ref must state that a missing source flags a gap, not blocks"
    # minimum viable input = a parent direct SKU
    assert "minimum" in body and "parent" in body and "sku" in body, \
        "intake ref must state the minimum-viable input is a parent direct SKU"
    # parent-SKU modeling spine + human-confirm
    assert "naming difference" in body and "delta" in body, "intake ref missing parent-SKU delta/naming-difference modeling"
    assert "human" in body and "confirm" in body, "intake ref must state the skill drafts and flags; a human confirms"
    # pricing out of scope reminder
    assert "pricing" in body and ("out of scope" in body or "not" in body), \
        "intake ref must note pricing is out of scope"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"
```

- [ ] **Step 2: Run the test to verify it FAILS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: FAIL on `R-INTAKE-01` with `missing refs/intake-source-map.md`.

- [ ] **Step 3: Create `refs/intake-source-map.md`** (verbatim)

```markdown
# Intake & source map

How an effort gets its inputs, and what each source feeds. This phase *documents* the channels
and the access pattern — it does not yet make live calls (Org62 entitlement pulls land in
Phase 4; Slack and web research in Phases 4/6). For now, treat every non-paste channel as
"paste what you have from it, and record the source."

## Minimum viable input

The **only required input to open an effort is a parent direct SKU reference** — "model a
partner/OEM product on *this*" (e.g., Health Cloud EE/UE for an Agentforce-for-Healthcare-OEM
effort). From that alone the skill derives a first-pass entitlement set (06) and a skeletal
brief (01). Everything else is an enricher that raises confidence and fills placeholders.

## The six channels (each degrades gracefully)

A source being absent **never blocks** an artifact — the artifact proceeds and the missing input
becomes a flagged gap (manifest placeholder with an owner + next step), recorded so the
00-executive-summary's Next Steps & Blockers register can roll it up.

| Channel | Feeds | Access | If absent |
|---------|-------|--------|-----------|
| **Paste** (baseline) | 01-05 | User drops FCD text, draft Quip content, notes | Artifacts stay skeletal, low confidence |
| **Link / source-fetch** | 08, 10, 01 | Official Salesforce docs only (allowlist below); non-official links flagged, not fetched | Resource links left as `pending` |
| **Org62** | 06, parent-SKU modeling | Read-only `sf` CLI vs. the `org62` alias (session identity): `Product2` + `productEntitlements` for the parent `pId` | 06 from paste/knowledge, low confidence, gap flagged |
| **Slack channel** | Coordination context (read); canvas publish (write) | Slack MCP — register the effort's `#help-sell-...` channel | No coordination context; canvas exported locally only |
| **SF price-list catalog** | 07 (which SKUs/add-ons exist) | Reference catalog (the SF price-list tool) | Tiering from knowledge + Org62, flagged for catalog check |
| **Web research** | 10 Tier C | Opt-in deep-research fan-out, citations + verify loop | POV stays at Tier B (archetypes + illustrative companies) |

## Official-docs allowlist

Technical guidance (08-setup-guide, 09, the technical parts of 01/03) cites **official Salesforce
sources only**. The operational allowlist:

- `help.salesforce.com`
- `developer.salesforce.com`
- `architect.salesforce.com`
- Trailhead
- the Partner Community
- Org62-internal tools

Anything else is **flagged as non-official and excluded** from technical-guidance artifacts —
never silently included, never silently dropped. A non-official link the user pastes is recorded
as a flagged source, not used as a citation.

## Parent-SKU modeling (the spine of the technical artifacts)

Given the parent `Product2` (e.g., Health Cloud EE/UE), the skill:

1. Reads the parent's entitlement composition — licenses, PSLs, features, storage (Phase 4 pulls
   this from Org62; until then, from paste/knowledge, flagged low-confidence).
2. Proposes the Embedded/OEM equivalent, **flagging naming differences** ("Health Cloud" ->
   "Agentforce for Healthcare") and **deltas** (what changes for OEM vs. the direct SKU).
3. Applies partner-motion rules (OEM-only, shared-org restrictions, packageability timing) as a
   validation pass.
4. Derives the minimalist Required / Recommended / Optional add-on tiers (07).

The skill **drafts and flags; a human confirms.** It never silently asserts an entitlement — a
proposed license/PSL/feature/storage set is always presented for human confirmation.

## Out of scope

**Pricing and discounts are out of scope** — not the skill's to determine. SKU/add-on tables
surface *which* SKUs exist and tier them; price and discount cells stay as marked placeholders
owned elsewhere. Do not invent or infer a price.

## Recording sources

Every input is recorded against the artifact it grounded (the manifest `sources` list). This is
what later lets the claim-verification loop ask "is this sentence traceable to a provided
source?" and what drives the confidence score down when a claim is ungrounded.
```

- [ ] **Step 4: Wire the ref into SKILL.md and verify ASCII**

Edit SKILL.md to add this line inside the "## The effort lifecycle" section, right after the existing sentence about the manifest being the state:

```markdown
**Intake:** the only required input is a parent direct SKU; five more channels (paste, source-fetch,
Org62, Slack, price-list, web research) enrich it and each degrades gracefully. See
[refs/intake-source-map.md](refs/intake-source-map.md).
```

Run: `cd ~/.claude/skills/ps-npi-forge && LC_ALL=C grep -nP '[^\x00-\x7F]' refs/intake-source-map.md || echo "ASCII-CLEAN"`
Expected: `ASCII-CLEAN`. If any line prints, fix that character (e.g., replace a smart-arrow with `->`) and re-run.

- [ ] **Step 5: Run the suite to verify all PASS**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `15/15 checks passed`, exit 0.

- [ ] **Step 6: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add refs/intake-source-map.md SKILL.md tests/validate_skill.py
git commit -m "feat: add intake source-map ref (6 channels, allowlist, parent-SKU spine, graceful degradation)"
```

---

### Task 3: Structural ref invariants — expected-refs-exist + no-orphans

**Files:**
- Modify: `~/.claude/skills/ps-npi-forge/tests/validate_skill.py` (append `EXPECTED_REFS` + two checks)

**Interfaces:**
- Consumes: `check()`, `read()`, `exists()`, `instructions()`-style access to SKILL.md, `SKILL` root, `os`.
- Produces: `EXPECTED_REFS` list (the growing manifest of required refs) + `R-ARCH-03` (every expected ref exists) + `R-ARCH-04` (every file under `refs/` is referenced by SKILL.md — no orphans). These gate all future ref work.

- [ ] **Step 1: Write the failing tests** (append before the `# ---- runner` block)

```python
# ---- R-ARCH-03/04: refs manifest + no-orphans -------------------------
# refs/ holds SKILL.md-referenced instruction modules. scripts/ and templates/
# are infrastructure wired via tests/scripts (not the instruction router), so the
# no-orphans check is scoped to refs/ only.
EXPECTED_REFS = [
    "refs/voice-and-style.md",
    "refs/intake-source-map.md",
]

@check("R-ARCH-03: every expected ref exists")
def t_expected_refs_exist():
    missing = [r for r in EXPECTED_REFS if not exists(r)]
    assert not missing, f"expected refs missing: {missing}"

@check("R-ARCH-04: every file under refs/ is referenced by SKILL.md (no orphans)")
def t_refs_no_orphans():
    refs_dir = os.path.join(SKILL, "refs")
    if not os.path.isdir(refs_dir):
        raise AssertionError("refs/ directory missing")
    skill = read("SKILL.md")
    orphans = []
    for f in os.listdir(refs_dir):
        if f.startswith(".") or not os.path.isfile(os.path.join(refs_dir, f)):
            continue
        if f"refs/{f}" not in skill:
            orphans.append(f"refs/{f}")
    assert not orphans, f"refs present but never referenced by SKILL.md: {sorted(orphans)}"
```

- [ ] **Step 2: Run the suite — expect PASS** (Tasks 1–2 already created + referenced both refs)

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `17/17 checks passed`, exit 0.

- [ ] **Step 3: Prove the no-orphans check can fail (sanity-gate the guard)**

Run:
```bash
cd ~/.claude/skills/ps-npi-forge
touch refs/__orphan_probe.md
python3 tests/validate_skill.py; echo "exit=$?"
rm refs/__orphan_probe.md
python3 tests/validate_skill.py | tail -1
```
Expected: first run FAILS `R-ARCH-04` naming `refs/__orphan_probe.md` and `exit=1`; after removing the probe, the final line reads `17/17 checks passed`.

- [ ] **Step 4: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add tests/validate_skill.py
git commit -m "test: gate refs with expected-refs manifest and no-orphans check"
```

---

### Task 4: Update BACKLOG roadmap

**Files:**
- Modify: `~/.claude/skills/ps-npi-forge/BACKLOG.md`

**Interfaces:**
- Consumes: nothing.
- Produces: BACKLOG roadmap with Phase 2 marked complete.

- [ ] **Step 1: Mark Phase 2 complete in the roadmap**

In `BACKLOG.md`, under "## Phase roadmap", change the Phase 2 line from `- [ ] Phase 2 — ...` to `- [x] Phase 2 — voice/style + intake source-map refs (no live fetch yet)`.

- [ ] **Step 2: Run the suite (no regression)**

Run: `cd ~/.claude/skills/ps-npi-forge && python3 tests/validate_skill.py`
Expected: `17/17 checks passed`.

- [ ] **Step 3: Commit**

```bash
cd ~/.claude/skills/ps-npi-forge
git add BACKLOG.md
git commit -m "docs: mark Phase 2 complete in backlog roadmap"
```

---

## Self-Review

**Spec coverage (Phase 2 scope):**
- Authorial voice — McKinsey/exec/first-person, two registers (spec §1) → Task 1 ref + R-VOICE-01. ✅
- Audience calibration — PAM/NPI/less-technical (spec §1) → Task 1 ref + R-VOICE-01. ✅
- Six intake channels + graceful degradation (spec §4) → Task 2 ref + R-INTAKE-01. ✅
- Minimum-viable parent-SKU input (spec §4) → Task 2 ref + R-INTAKE-01. ✅
- Official-docs allowlist (spec §4) → Task 2 ref + R-INTAKE-01. ✅
- Parent-SKU modeling spine + human-confirm + pricing-out-of-scope (spec §4) → Task 2 ref + R-INTAKE-01. ✅
- Lazy refs + no-orphans discipline (spec §7) → Task 3 (R-ARCH-03/04). ✅
- **Deferred (correctly out of Phase 2):** live WebFetch/`sf`/Slack calls (Phases 4/6); Mermaid/visual pipeline ref (Phase 5); artifact templates + generate→refine→validate cycle (Phase 3). The intake ref explicitly states it documents, not implements, the channels.

**Placeholder scan:** No TBD/TODO. Both refs are written in full in the plan. Content checks assert specific substrings, not vague "has content." ✅

**Type consistency:** Check names are unique and sequential with Phase 1 (R-VOICE-01, R-INTAKE-01, R-ARCH-03, R-ARCH-04 — note Phase 1 used R-ARCH-02; 03/04 continue the series). `EXPECTED_REFS` paths exactly match the files Tasks 1–2 create. The no-orphans check is scoped to `refs/` only, so Phase 1's `scripts/manifest.py` and `templates/manifest.yaml` (referenced via tests, not SKILL.md) are not falsely flagged. Final suite count: 13 (Phase 1) + R-VOICE-01 + R-INTAKE-01 + R-ARCH-03 + R-ARCH-04 = 17. ✅
