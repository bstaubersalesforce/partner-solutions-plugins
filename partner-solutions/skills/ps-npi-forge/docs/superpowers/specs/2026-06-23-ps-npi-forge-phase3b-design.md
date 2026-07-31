# PS-NPI-FORGE Phase 3b — Generate→Refine→Validate cycle + 4 quality loops (+ live Org62 intake)

**Date:** 2026-06-23
**Author:** Brandon Stauber (with Claude Code)
**Status:** Approved for planning
**Builds on:** Phase 1 (scaffold + manifest model), Phase 2 (voice/intake refs), Phase 3a (the 11 artifact templates). Implements design-spec.md §5 (the cycle + four loops) and folds in §4/Phase-4 live Org62 entitlement intake.

---

## 1. Scope & boundary

Phase 3b builds **Standard (B) run mode end-to-end** for all 11 artifacts: the three-pass
draft→refine→validate cycle, the four quality loops, per-section edit-preservation, and **live
Org62 entitlement intake** (Phase 4 is folded in here because "refine" and the claim-verification
loop both depend on the parent-SKU entitlement pull — they are too coupled to split).

**Live sources this phase:** paste + model knowledge + Org62 (`sf` vs. the `org62` alias,
read-only). The web-research and Slack channels stay **documented-but-gap-flagged** (a missing
channel yields a flagged gap, never a block) — their live wiring is Phase 6.

**Explicitly out of this phase (unchanged):**
- Web-research / Tier-C target-partner research and live Slack sync — **Phase 6**.
- Deep Build (C-mode) adversarial Workflow — **Phase 7**.
- Canvas `index.html` assembly + Mermaid render — **Phase 5**. (3b produces artifact markdown with
  filled tokens; HTML/Mermaid rendering is downstream.)

This is the largest phase to date; it is presented as one spec because the cycle, the loops, the
manifest growth, and the Org62 refine step are mutually dependent.

---

## 2. Architecture — code ↔ agent split

A skill has two materials: deterministic Python in `scripts/` (testable, CI-gated) and
agent-followed prose in `refs/` (lazy-loaded, judgment). The split follows the
`pie-poc-forge` / `skill-forge` pattern: **mechanical → code, judgment → agent.**

### 2.1 Python (`scripts/`) — mechanical, behaviorally tested (R-TEST-04)

| Script | Responsibility | Interface |
|--------|---------------|-----------|
| `render.py` | Fill a template's `{{TOKEN}}` slots from a fills dict → artifact markdown; report any token left unfilled. | `render(template_text, fills) -> (artifact_md, unfilled: list[str])` |
| `sections.py` | Split an artifact into H2 sections using the Phase-3a headings as anchors; diff a live file against its baseline; return which sections are human-locked. | `split(md) -> dict[heading, body]`; `locked_sections(live_md, baseline_md) -> set[heading]` |
| `scan.py` | Scan rendered markdown for uncertainty markers (PENDING/TBD, `$xx`-style price stubs, missing Template ID, surviving literal `{{TOKEN}}`) → gap list. | `scan(md) -> list[Gap]` where each `Gap` has `item` (owner/next_step are filled by the agent + written to the manifest) |
| `org62.py` | Parse `sf ... --json` output for the parent `Product2` + `productEntitlements` into the #06 entitlement payload (licenses, PSLs, features, storage). Parser only — never invokes `sf`. | `parse_entitlements(sf_json: dict) -> EntitlementPayload` |
| `manifest.py` (extend) | Add per-artifact `loops` verdicts and `last_generated` baseline ref; keep existing status/confidence/rollup/round-trip. | `set_loop_verdict(manifest, artifact, loop, verdict, note)`, `set_last_generated(...)` |

Each script gets a behavioral test exercising it against a fixture (the skill-forge R-TEST-04
discipline: a skill that ships `scripts/` must exercise them, with golden fixtures under
`tests/fixtures/`).

### 2.2 Agent prose (`refs/`) — judgment, lazy-loaded

- **`refs/quality-loops.md`** (new) — narrates the draft→refine→validate cycle and the four loops'
  *reasoning*: how to draft in the McKinsey voice, how claim-verification is **strict for
  technical/positioning claims but lenient for POV/vision** (#10, parts of #00 — checks internal
  logic + marked assumptions, not citations), the completeness judgment, the uncertainty-surfacing
  pass (every gap gets an owner + next step), and the partner-lens rules
  (OEM/VAR/shared-org/packageability/official-docs-only). Instructs the agent **how to call the
  scripts and write verdicts back** to the manifest.
- **`refs/org62-entitlements.md`** (new) — pins the exact SOQL / `sf` commands behind
  `productEntitlements` for the parent `pId` (closes BACKLOG **B1**), the read-only `org62`-alias
  pattern (same as `team-projects`), graceful degradation when no org is reachable, and the
  parent-SKU modeling spine (propose OEM equivalent, flag naming differences + deltas, human
  confirms — never silently asserted).

Both refs are wired into `SKILL.md` and gated by the existing `EXPECTED_REFS` / no-orphans checks.

---

## 3. The cycle & manifest growth

**Per artifact, three passes** (design-spec §5):

1. **Draft** — substantive v1 from model knowledge in the first-person exec/architect McKinsey
   voice. `render.py` fills the template from a knowledge-derived fills dict. Status → `drafted`,
   confidence modest. Never blocked on inputs.
2. **Refine** — fold provided sources (paste, Org62 entitlement payload, fetched official docs)
   into the fills; tie each claim to a source recorded in the manifest `sources`; re-render **only
   non-locked sections** (see §4). Confidence rises.
3. **Validate** — run the four loops; `scan.py` + agent judgment produce verdicts and a gap list;
   unresolved items become flagged gaps (lowering confidence) and the artifact reaches `verified`
   only when the loops pass and the human confirms.

**Manifest growth (minimal — keep the hand-rolled stdlib YAML round-trip tractable).** Per
artifact, add:

```yaml
loops:
  claim_verification: {verdict: pass|flag|fail, note: "..."}
  completeness:       {verdict: pass|flag|fail, note: "..."}
  uncertainty:        {verdict: pass|flag|fail, note: "..."}
  partner_lens:       {verdict: pass|flag|fail, note: "..."}
last_generated: "<baseline pointer>"   # path/hash of the baseline used for the section-diff
```

`placeholders` (item/owner/next_step) already exist from Phase 1 and carry the surfaced gaps.
`dumps`/`load` round-trip must preserve `loops` and `last_generated`; the registry/vocab parity
check (R-MANIFEST-06) and round-trip test (R-MANIFEST-02) extend to cover them. A `LOOP_REGISTRY`
constant names the four loops and a `VERDICT_VOCAB` (`pass`/`flag`/`fail`) gates them, mirroring
the existing `STATUS_VOCAB` discipline.

---

## 4. Edit-preservation (per-section)

The spec (§2.2) mandates the pie-poc-forge model: the manifest flags human-touched sections and
regeneration respects them. The Phase-3a templates make "section" cheap to address — each artifact
is a fixed gap-banner header + a body of `## Heading` blocks (one per token group) + a fixed
footer, so **one section = one H2 block**.

Mechanism:
- On every (re)generation, `render.py`'s output is written to the artifact **and** copied to a
  baseline at `artifacts/.baseline/<slug>.md`; `last_generated` records the pointer.
- On the next **refine**, `sections.py.locked_sections(live, baseline)` diffs the live artifact
  against its baseline. Any H2 section whose body diverged from the baseline is **human-locked**.
- Regeneration rewrites only model-owned (unchanged-since-baseline) sections; locked sections are
  carried over **verbatim**. The gap-banner header and footer are tool-owned and always regenerate
  (they reflect current status/confidence/gaps).
- First generation (no baseline) locks nothing.

`artifacts/.baseline/` lives under the effort folder (outside the skill repo), so it never enters
the skill's git history.

---

## 5. Org62 entitlement path

- **`refs/org62-entitlements.md`** pins the queries (B1): the `Product2` lookup for the parent
  `pId` and the `productEntitlements` composition (licenses, PSLs, features, storage), via `sf ...
  --json` against the read-only `org62` alias (env `ORG62_ALIAS`, default `org62`; session
  identity — the `team-projects` pattern).
- **`org62.py` is a pure parser:** it takes already-fetched `sf --json` output and produces the
  #06 payload. It never shells out to `sf` (keeps it testable and side-effect-free).
- **Tests run against a committed sanitized fixture** — `tests/fixtures/org62/parent-entitlements.json`,
  a real parent-SKU pull scrubbed of sensitive values. CI tests the parser, never the live org.
- **A live pull is a manual, capability-gated step** (like `mmdc` in the diagram pipeline): when no
  org is reachable, #06 falls back to paste/knowledge at lower confidence with a flagged gap; the
  effort is never blocked.
- **Human always confirms entitlements** — the skill drafts and flags naming differences ("Health
  Cloud" → "Agentforce for Healthcare") and OEM-vs-direct deltas; it never silently asserts them
  (refusal rule, already in SKILL.md).

---

## 6. Validation additions & dogfood

**New checks** (extend `tests/validate_skill.py`, stdlib-only; targets ~20 → ~26):
- **Render token-fill parity** — a complete fills dict leaves no surviving `{{TOKEN}}`; an
  incomplete one is reported, not silently emitted. (Subsumes Phase-3a **B6** body-token↔fill-set
  parity — render is the fill-set authority.)
- **Section-diff round-trip** — a hand-edited H2 section survives regeneration verbatim; an
  untouched section regenerates. (Behavioral test for `sections.py`.)
- **Placeholder/uncertainty scan** — `scan.py` catches each canonical gap type (PENDING/TBD,
  price stub, missing Template ID, surviving literal `{{…}}`), and a clean artifact scans empty.
- **Org62 parser** — `parse_entitlements` against the sanitized fixture yields the expected
  licenses/PSLs/features/storage shape.
- **Manifest round-trip** — `loops` + `last_generated` survive `load(dumps(x))`; `LOOP_REGISTRY` /
  `VERDICT_VOCAB` parity with the suite (extends R-MANIFEST-06).
- **Refs gates** — `refs/quality-loops.md` and `refs/org62-entitlements.md` added to
  `EXPECTED_REFS`; SKILL.md references them (no orphans).

**Phase-3a hardening folded in:** **B6** (above), **B7** (tighten R-TPL-02 from token-presence to
gap-banner/footer *structure* now that templates are being filled), **B8** (scope R-TPL-01's
`manifest` exception to `manifest.yaml`).

**Dogfood acceptance (manual, agent-driven — not a unit test):** Brandon pastes the real
**Agentforce for Healthcare** brief into the session. The phase's acceptance is a full Standard-mode
run of the 11 artifacts against it, asserting:
- the cycle drafts all 11, refines #01–#05 from the paste and #06/#07 from Org62 (or flagged
  fallback),
- the **missing Template ID** surfaces as a flagged gap in **#09 org-provisioning-validation** and
  rolls up into **#00**'s Next Steps & Blockers register (the brief's natural gap — the golden
  signal),
- the four loops write verdicts to the manifest and the overall confidence is the weighted floor.

The mechanical sub-steps (render, scan, section-diff, Org62 parse, rollup) are CI-tested via
fixtures; the end-to-end narrative run is the manual acceptance gate.

---

## 7. Out of scope (explicit, this phase)

- Web research / Tier-C target-partner research and live Slack sync (Phase 6).
- Deep Build C-mode Workflow (Phase 7).
- Canvas `index.html` + Mermaid render (Phase 5).
- Pricing/discount determination (out of scope entirely — placeholders only).
- Live Org62 *writes* (read-only always).
- Auto-publishing anything outward.

---

## 8. Anticipated task decomposition (for the plan)

1. **Manifest growth** — `LOOP_REGISTRY` + `VERDICT_VOCAB`, `loops`/`last_generated` schema,
   round-trip, parity check.
2. **`render.py` + token-fill parity check** (folds B6).
3. **`sections.py` + section-diff round-trip** (edit-preservation core).
4. **`scan.py` + uncertainty-scan check.**
5. **`org62.py` + sanitized fixture + parser check; `refs/org62-entitlements.md`** (closes B1).
6. **`refs/quality-loops.md`** — the cycle + four loops prose; wire both refs into SKILL.md;
   SKILL.md cycle section.
7. **Validation hardening** — fold B7 (R-TPL-02 structure) + B8 (R-TPL-01 manifest scope);
   whole-suite green.
8. **Dogfood acceptance** — paste-driven manual end-to-end run; record the Template-ID gap signal.

(Exact task count/ordering finalized in the plan; ~7–8 tasks.)
