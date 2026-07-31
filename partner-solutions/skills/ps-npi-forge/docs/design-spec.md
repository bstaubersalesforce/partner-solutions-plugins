# PS-NPI-FORGE — Design Specification

**Date:** 2026-06-23
**Author:** Brandon Stauber (with Claude Code)
**Status:** Approved for planning
**Related skills:** `skill-forge` (authoring meta-skill), `pie-poc-forge` (sibling Tier-3 forge, design-pattern source), `pov-builder` (voice/confidence pattern)

---

## 1. Purpose & strategic frame

PS-NPI-FORGE is a Claude skill that helps the **Partner Solutions (PS) team build scale and
consistency** in its contributions to the Salesforce **NPI (New Product Introduction)** process.

For a single new NPI product (typically an **Embedded / OEM** SKU modeled on a directly-sold
parent product), the skill turns source material into a consistent **family of PS-owned
artifacts** plus a synced **Key Resources canvas**.

**Consumption model:** Outputs are PS-owned. Parts are shared upward with the larger NPI team and
are later synthesized into official NPI deliverables. Therefore artifacts are **authoritative-feeder
quality** — consistent, source-grounded, uncertainty-flagged — not final published collateral. The
quality loops exist to make PS output trustworthy enough to flow upward without rework.

**Lens (constant):** Partner Solutions / ISV-OEM program. Every artifact is written from this
partnership-program lens.

**Authorial voice:** First-person **Brandon-as-Salesforce-exec/architect**, in the **McKinsey
register** (pyramid principle, MECE, action titles, "so what" up front). Narrative artifacts speak
in this voice; reference artifacts stay appropriately factual.

**Audience calibration:** Author *assuming Salesforce-product fluency*, but write outputs to serve
**partner account managers (PAMs), the NPI team, and less-technical personas** — plain-language
framing over jargon.

---

## 2. Architecture

**Approach:** Modular artifact pipeline (B) with an optional adversarial multi-agent **Deep Build**
mode (C). B is the everyday spine; C is an explicit escalation for high-confidence full builds.

**Foundation:** Tier-3 skill following the `skill-forge` structure and the `pov-builder` /
`pie-poc-forge` design pattern — SLDS palette, Mermaid pipeline, lazy-loaded refs, validation suite,
CI, refusal conditions.

### 2.1 The "effort" — unit of work & persistence

One effort = **one product for one release** (e.g., `agentforce-healthcare-oem` under `summer-26`).

Effort root (the user's data, kept out of the skill repo's git history):

```
/Users/bstauber/claude-projects/ps-npi-efforts/<release>/<product-slug>/
  manifest.yaml      # the spine: per-artifact status + confidence + placeholders + sources + slack channel
  sources/           # pasted/fetched inputs, Org62 pulls, parent-SKU reference
  artifacts/         # the 11 deliverables — .md and/or .html, Mermaid embedded where it fits
  canvas/            # index.html (SLDS hub) + slack-canvas.md (Slack payload)
```

Skill code lives separately at `~/.claude/skills/ps-npi-forge/`.

### 2.2 The manifest — state that makes the tool interactive & resumable

The manifest tracks, per artifact and per key field:

- **status:** `pending` / `in_progress` / `drafted` / `verified` / `pulled`
  (`pulled` = removed from the effort, the strikethrough case, e.g. Life Sciences Cloud in April)
- **confidence:** 0.0–1.0 + one-line rationale (consistent with pov-builder/pie-poc-forge)
- **placeholders:** open unknowns, each with a suggested **owner + next step**
- **sources:** which inputs grounded the artifact (powers claim verification + confidence)
- **last_verified:** which quality loops ran and their verdicts (implemented as the per-artifact
  `loops{}` map holding verdicts, plus a separate `last_generated` baseline pointer)

On return to an effort: skill reads the manifest → shows a status/confidence/blockers table → user
targets one artifact to refine → only that artifact regenerates (respecting human edits) → canvas +
manifest update. Edit-preservation follows the pie-poc-forge model (manifest flags human-touched
sections).

### 2.3 Run modes

- **Standard (B):** interactive, per-artifact generate→refine→validate; quality loops run as
  single-pass checks. The default; cheap to run and re-run.
- **Deep Build (C):** opt-in Workflow escalation for a full high-confidence package — adversarial
  multi-agent verification + live target-partner research. Writes back to the **same** effort
  folder/manifest; never a separate output. Triggered explicitly (e.g., "deep build the August
  Healthcare effort").

---

## 3. Artifact family (11 artifacts + canvas)

> **SUPERSEDED (2026-06-25):** this is the frozen 0.x planning reference. The family is now **15
> artifacts** (added 11-solution-infographic, 12-marketecture, 13-demand-plan, 14-exec-infographic to
> the original 11) — the authoritative, current list is `ARTIFACT_REGISTRY` in `scripts/manifest.py`
> and the registry table in `refs/artifact-templates.md`. The "11 artifacts" counts below are
> historical; do not rely on them. (R-DOC-01 deliberately excludes this frozen doc from its count guard.)

Every artifact: McKinsey voice + SLDS/Mermaid pattern, written for the PAM/NPI/non-technical reader,
carries a **confidence score + rationale**, records **sources + placeholders** in the manifest, and
**opens with a gap banner** (status + confidence + any blocking gaps).

| # | Artifact | Purpose (PS lens) | Primary source | Format | Mermaid |
|---|----------|-------------------|----------------|--------|---------|
| 00 | **Executive Summary** | Front door: vision & purpose; **top 3–6 use cases**; **Ideal Partner Profile summary**; **Key Next Steps & Blockers register**; effort confidence + status rollup | All artifacts (rollup) | MD + HTML | status/blocker rollup |
| 01 | **Use-case & details brief** | Canonical 8-section product narrative (What is / Value to partners / Why different / Who for / What ISVs build / Opportunities) | Paste (FCD) + parent product + Slack | MD + HTML | — |
| 02 | **Slide-version summary** | One-screen exec/PAM summary | Derived from #01 | MD + HTML | optional |
| 03 | **Internal enablement doc** | Deeper internal teach: positioning, motion rules, entitlement implications | #01 + #06 + motion rules | MD + HTML | — |
| 04 | **Internal FAQ** | PS/NPI Q&A incl. OEM/VAR/shared-org rules, packageability timing | Release-FAQ grammar | MD | — |
| 05 | **External FAQ** | Partner-facing Q&A, scrubbed of internal-only detail; a **safe subset derived from #04** | Filtered from #04 | MD + HTML | — |
| 06 | **License & entitlement details** | Technical payload: licenses, PSLs, features, storage — **derived from parent product**, deltas + naming differences flagged | Org62 (`Product2` + `productEntitlements`) | MD + HTML | entitlement composition |
| 07 | **Add-on tiering** | Minimalist **Required / Recommended / Optional** SKU & add-on recommendation — only what's truly required | SF price-list catalog + #06 | MD + HTML | tier decision view |
| 08 | **Setup guide** | Build/provisioning guidance: Basic Info / TrialForce (+approval) / 2GP scratch orgs / managed-pkg prep. **Official Salesforce docs only** | Official admin/dev/setup docs | MD | optional |
| 09 | **Org-provisioning validation** | Static Template-ID/entitlement check (always) **+** optional live `sf` org diff (when org exists) | #06 + #08 + (live org) | MD | — |
| 10 | **Ideal-partner-profile POV + target partners** | Whitespace POV: great *embedded/OEM* fit *because* poor *direct-SF* target. **Tier B** (archetypes + illustrative companies, marked "verify") always; **Tier C** (live-researched candidates + citations) opt-in | #01 + reasoning + (web research) | MD + HTML | partner-fit logic |
| — | **Key Resources canvas** | Assembler: SLDS HTML index linking all present artifacts **+** synced Slack canvas | All of the above | HTML + Slack payload | — |

### 3.1 Key judgment calls (approved)

- **#05 derives from #04** — guarantees the external FAQ never contradicts the internal one and is a
  safe subset.
- **#07 is separate from #06** — "what entitlements compose the product" (technical truth) ≠ "what we
  recommend a partner attach" (minimalist commercial judgment); different audiences.
- **Pricing is out of scope.** The skill surfaces *which* SKUs/add-ons exist and tiers them; price &
  discount cells remain marked placeholders owned elsewhere.
- **Gaps are first-class** via two views over one source (the manifest): a per-artifact gap banner
  **and** the aggregated Next Steps & Blockers register in the Exec Summary. A gap is never silent —
  always owner + next step. (e.g., Org-Provisioning Validation with no Template ID renders
  "⚠ Gap: live org test cannot run — Template ID pending; owner: …", not an empty or complete-looking
  section.)

### 3.2 Confidence model

Each artifact scores 0.0–1.0 + rationale. Drivers that **lower** it: unresolved placeholders
(PENDING/TBD/`$xx`/missing Template ID), claims not grounded in a provided source, official-docs-only
violations in #08, unverified live research in #10 Tier C. The effort's overall confidence is the
**weighted floor** across artifacts (a single shaky artifact stays visible, not averaged away). The
loops drive the score; Deep Build's adversarial votes produce a tighter, better-justified score.

---

## 4. Intake & source map

**Minimum viable start:** the only required input is a **parent direct SKU reference** ("model a
partner/OEM product on *this*"). From that alone the skill derives a first-pass entitlement set (#06)
and skeletal brief; everything else firms up as more is fed. Every other source is an enricher.

**Six channels, each degrades gracefully** (absent = artifacts proceed with flagged gaps, never
blocked):

| Channel | Feeds | Access | If absent |
|---------|-------|--------|-----------|
| **Paste** (baseline) | #01–05 | User drops FCD text, draft Quip content, notes | Artifacts stay skeletal, low confidence |
| **Link / source-fetch** | #08, #10, #01 | WebFetch on **official Salesforce docs only**; non-official links flagged, not fetched | Resource links left as `pending` |
| **Org62** | #06, parent-SKU modeling | `sf` CLI vs. `org62` alias (read-only, session identity): `Product2` + `productEntitlements` for the parent `pId` | #06 from paste/knowledge, low confidence, gap flagged |
| **Slack channel** | Coordination context (read); canvas publish (write) | Slack MCP — register effort's `#help-sell-…` channel | No coordination context; canvas exported locally only |
| **SF price-list catalog** | #07 (which SKUs/add-ons exist) | Reference catalog (Heroku pricelist tool) | Tiering from knowledge + Org62, flagged for catalog check |
| **Web research** | #10 Tier C | Opt-in deep-research fan-out, citations + verify loop | POV stays at Tier B |

**Official-docs allowlist** (operational expression of "official Salesforce only"):
`help.salesforce.com`, `developer.salesforce.com`, `architect.salesforce.com`, Trailhead, the Partner
Community, and Org62-internal tools. Anything else → flagged non-official, excluded from
technical-guidance artifacts, never silently dropped.

**Parent-SKU modeling (spine of the technical artifacts).** Given the parent `Product2` (e.g., Health
Cloud EE/UE), the skill:
1. Pulls the parent's entitlement composition (licenses, PSLs, features, storage) from Org62.
2. Proposes the Embedded/OEM equivalent, **flagging naming differences** ("Health Cloud" →
   "Agentforce for Healthcare") and **deltas** (OEM vs. direct).
3. Applies partner-motion rules (OEM-only, shared-org restrictions) as a validation pass.
4. Derives the minimalist Required/Recommended/Optional add-on tiers (#07).

The skill **drafts and flags**; a human always confirms entitlements — it never silently asserts them.

---

## 5. Generate→refine→validate cycle & quality loops

**Every artifact follows three passes** ("start with what you know, refine, validate"):

1. **Draft** — substantive v1 from model knowledge in the first-person exec/architect McKinsey voice.
   Never blocked on inputs; confidence starts modest.
2. **Refine** — fold in provided sources (paste, Org62, fetched official docs, Slack); tie each claim
   to a source in the manifest; confidence rises.
3. **Validate** — run the four loops; unresolved items become flagged gaps + lower confidence; human
   confirms.

**Four quality loops** (one per failure mode), per-artifact:

| Loop | Checks | Standard (B) | Deep Build (C) |
|------|--------|--------------|----------------|
| **Claim verification** | Every factual/positioning claim traceable to a source? Contradicts the FCD? | 1 pass, flags ungrounded claims | 3 independent skeptic agents/claim, refute-by-default, majority kills |
| **Completeness audit** | All canonical sections present? Empty personas/rows? Audience-appropriate? | template diff | critic agent loops "what's missing?" until dry |
| **Uncertainty surfacing** | Every PENDING/TBD/`$xx`/missing Template-ID flagged with owner + next step? | placeholder scan → manifest | agent cross-checks manifest vs. rendered output |
| **Partner-lens rules** | OEM/VAR correct? Shared-org restrictions? Packageability timing? Official-docs-only honored? | rule checklist | rule-specialist agent per artifact |

**POV/opinion exception (approved):** Claim verification is **strict for technical/positioning
claims** but **lenient for POV/vision** (#10, parts of #00). A POV is Brandon's reasoned argument,
not a sourced fact — the loop checks **internal logic + clearly-marked assumptions**, not citations,
so it never strips the judgment the skill is meant to express.

**Deep Build (C)** is a Workflow: parallel artifact drafting → 3-vote adversarial claim verification →
completeness-critic loop-until-dry → Tier-C target-partner research sub-pipeline (search → fetch →
verify → cite). Writes back to the same effort folder/manifest.

---

## 6. Outputs, canvas assembly & Slack sync

**Local output is the source of truth; the Slack canvas is a projection.**

- **Format rule:** narrative/shareable artifacts → **MD + HTML**; internal-only reference artifacts
  (#04 internal FAQ, #08 setup guide, #09 validation) → **MD-only** unless they carry a diagram.
- **Mermaid** embedded wherever it earns its place (entitlement composition #06, add-on tiers #07,
  partner-fit logic #10, status/blocker rollup #00), themed to the SLDS `%%{init}%%` directive from
  `style-conventions.md`.

**Key Resources canvas (assembler):**
- `canvas/index.html` — SLDS-themed hub: effort title, release, overall confidence + status rollup,
  the Next Steps & Blockers register, then a linked card per artifact with status + confidence badge.
  `pending` artifacts render as a labeled gap card, not a dead link.
- **Slack sync (write):** publishes/updates a canvas in the registered `#help-sell-…` channel via
  Slack MCP, mirroring the index. Re-running **updates in place**, no duplicates.

**Publish gate (approved):** The skill **confirms before creating a Slack canvas**, and **external-FAQ
content always requires an explicit OK** before going up. Subsequent syncs update in place. Consistent
with the "confirm outward-facing actions" guardrail.

---

## 7. Skill structure, guardrails & validation

**Repository:** The skill will ultimately live in its **own git repo** (like pie-poc-forge /
skill-forge). For the 0.x build it is scaffolded at `~/.claude/skills/ps-npi-forge/` and initialized
as its own repo. The design spec (this file) currently lives in
`/Users/bstauber/claude-projects/docs/superpowers/specs/` and is **copied into the repo as
`docs/design-spec.md`** to serve as the 0.x reference, **linked from `README.md`**. A `BACKLOG.md`
seeds visibility on next additions (see §9 + the dogfood gaps).

```
~/.claude/skills/ps-npi-forge/
  SKILL.md                     # entry: triggers, effort lifecycle, run modes, refusal/guardrail rules
  docs/
    design-spec.md             # 0.x reference (copy of this spec), linked from README
  refs/
    artifact-templates.md      # the 11 artifact structures + section grammar
    voice-and-style.md         # first-person exec/architect McKinsey register
    org62-entitlements.md      # sf/org62 queries: Product2 + productEntitlements, parent-SKU modeling
    intake-source-map.md       # 6 channels, official-docs allowlist, graceful degradation
    quality-loops.md           # 4 loops, confidence model, draft→refine→validate cycle
    mermaid-diagrams.md        # SLDS-themed directive + diagram types (synced from style-conventions)
    canvas-assembly.md         # index.html + Slack-canvas sync + publish gate (folded into SKILL.md Outputs + scripts/canvas.py in Phase 5)
    deep-build-workflow.md     # C-mode Workflow script + escalation triggers (Phase 7 — not yet created)
  templates/                   # manifest.yaml + per-artifact MD/HTML skeletons
  scripts/                     # manifest read/update, status+confidence rollup, org-validation diff
  tests/                       # validation suite
  .github/ + .githooks/        # CI (parity checks, lint) — same as pie-poc-forge
  README.md                    # links to docs/design-spec.md (0.x reference) + BACKLOG.md
  BACKLOG.md                   # next additions / open items (seeded from §9)
```

**Refusal / guardrail rules (in SKILL.md):**
- Official Salesforce docs only for technical guidance; non-official sources flagged + excluded.
- Never assert entitlements without flagging for human confirmation.
- Never auto-publish to Slack without confirmation; external-FAQ content always requires explicit OK.
- Pricing is out of scope — placeholders left as-marked.
- Never silently drop an uncertainty — flag with owner + next step.

**Validation suite (skill-forge style):**
- Template-parity checks (artifact skeletons match the grammar).
- Manifest-schema check.
- Confidence-rollup unit test.
- Mermaid-theme parity check vs. `style-conventions.md`.
- **Dogfood fixture:** the pasted **Agentforce for Healthcare** material is the golden end-to-end test
  — run the effort, assert the 11 artifacts generate with correct gap-flagging for the missing
  Template ID.

**Build approach:** `skill-forge` scaffolds the structure and scores it against the maturity rubric;
implement via `writing-plans` → `executing-plans`, with the Healthcare fixture as the running
acceptance test.

---

## 8. Out of scope (explicit)

- Determining or filling **pricing / discounts** (owned elsewhere; left as marked placeholders).
- Publishing **final official NPI collateral** (PS output feeds upward; official synthesis is downstream).
- Non-official documentation sources for technical guidance.
- Live Org62 *writes* (read-only access only).

---

## 9. Open items / expected additions

The user noted additional pieces will surface during build. Known soft spots to revisit:
- Exact Org62 objects/SOQL behind `productEntitlements` (pin during implementation).
- Slack MCP canvas create/update specifics and the `#help-sell-…` channel registration UX.
- Whether the SF price-list Heroku tool is fetchable or must be treated as a manual-reference catalog.
