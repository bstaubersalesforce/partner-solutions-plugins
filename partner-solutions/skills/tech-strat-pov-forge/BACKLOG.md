# tech-strat-pov-forge — Backlog

Ideas and improvements not yet actioned, kept here so they stay visible. Each
item records where it came from, why it matters, and what "done" looks like.
This is a working list, not a commitment — items graduate to a spec → plan →
implementation cycle (see `docs/superpowers/`) when picked up.

Origin: the maturity & design assessment of 2026-06-03 (a hand-read, later
re-run objectively via the `skill-forge` audit).

---

## Done

- **R9 — Dogfood fixes from the nCino full-regen (2026-06-11).** Three defects surfaced by
  regenerating the full nCino package through the updated skill, all fixed same-day:
  1. **`{{TOKEN}}` glossary false-positive.** The trailing token-reference comment in
     `technical-architecture-assessment.html`, `discovery-document.html`,
     `consumption-opportunities.html`, and `competitive-assessment.html` contained a literal
     `{{TOKEN}}` (with braces) — which tripped the html-output-method zero-unfilled-token scan
     on every clean run (4 subagents independently reported it + hand-patched around it).
     Reworded to "each literal token name appears" (brace-free). The comment now obeys its own
     "names WITHOUT braces" rule.
  2. **SLDS migration missed three deck templates.** The first migration pass targeted only
     `#0070d2`; `investor-presentation.html`, `solution-infographic.html`, and
     `pov-presentation.html` carry the legacy Salesforce cloud cyan **`#00A1E0`** as their
     `--sf-blue` `:root` accent. Result: those decks rendered in old cyan while the home-pill
     used the new `#0176d3` — a visible within-deck brand-blue inconsistency. Migrated
     `#00A1E0 → #0176d3` in all three.
  3. **Stage 13 filename drift.** The doc's filename convention listed
     `SLUG-red-team-assessment.*`, but the artifact (and the `ensure-home-link.py` test fixture)
     use `SLUG-red-team.*`. Corrected the convention line to match the real slug.

- **R1 — Behavioral tests for `scripts/`.** ✅ Shipped 2026-06-03 (commit
  `d1fcda7`). Golden-file test for `md-to-html.py` + inject/repair/idempotency
  checks for `ensure-home-link.py`; fixtures in `tests/fixtures/`. Surfaced and
  fixed a latent `t_no_orphans` bug (`__pycache__` false-flag). Suite 56 → 59.

## Withdrawn

- **R2 — Golden-file test of a generated POV.** ❌ Mis-framed and dropped. POV
  prose is LLM-generated and non-deterministic — it cannot be golden-filed. R1
  is the sound version of the instinct: test the *deterministic* code (the
  scripts), not the prose. POV quality stays a human judgment at the Stage 7
  approve gate.

---

## Open

### R3 — The test suite is a second source of truth that must be hand-maintained
**Priority:** Medium · **Effort:** Medium · **Type:** maintainability

`tests/validate_skill.py` hardcodes constants that mirror the content —
`DISCOVERY_DIMENSIONS` (10), `WA_QUALITIES` (8), `WA_PILLARS` (3), `CANON_STAGES`,
`VERTICAL_HEADINGS`, `VERTICAL_LITERALS`. Adding a vertical or a Well-Architected
quality means editing **both** the content **and** the test's constant. The tests
guard the content; nothing guards the tests. Sustainable at ~59 checks; becomes a
drag past ~100.

**Done looks like:** the most-churned constants are derived from the content
itself (single source of truth) rather than duplicated — e.g. read the discovery
dimensions from the framework ref and assert the template/checklist match *that*,
instead of all three against a hardcoded list. Watch-item until a content family
actually changes; revisit then.

### R4 — Single-maintainer legibility ceiling
**Priority:** Low · **Effort:** ongoing · **Type:** complexity hygiene

18 stages, 11 stage files, 11 validation checklists, 10 templates, 9 verticals,
parallel dispatch. Well-organized, but the cognitive surface is large; the docs
(README + spec/plan archive) are what keep it legible. Risk is silent drift as
features accrete.

**Done looks like:** no single action — keep the README "How it works" + the
`docs/superpowers/` spec/plan archive current with every feature; if a single
file grows unwieldy, split by responsibility. Treat any new stage as a doc change
too, not just a code change.

### R5 — Pre-commit hook activation is manual per clone
**Priority:** Low · **Effort:** Low · **Type:** distribution friction

The tracked hook needs `git config core.hooksPath .githooks` run once per clone;
it is documented but opt-in and silently skippable. Fine for a single maintainer;
matters if the skill goes multi-user (an un-activated hook means the local guard
is off and only CI catches breakage).

**Done looks like:** either accept-and-document (current state, CI is the real
net) or add a one-time bootstrap step (e.g. a `make setup` / setup script) that
activates the hook, if/when more than one person edits the repo.

### R6 — Output-quality signal for the LLM prose (the real frontier)
**Priority:** Aspirational · **Effort:** High · **Type:** quality
**Origin:** the standing limitation noted in every assessment pass.

The one thing no structural or behavioral test can see: whether a *generated POV
is good*. Today this is caught only by human review at the Stage 7 approve gate
and the Stage 5/6 self-contradiction + validation checks (which test the contract,
not the prose quality).

**Done looks like:** an explored — not necessarily built — approach to a
repeatable quality signal (e.g. an LLM-as-judge rubric scoring a sample POV
against the delivery-voice contract, run ad hoc rather than in the structural
suite). Explicitly *not* a structural-suite check; it would be non-deterministic.
Capture findings before building anything.

### R8 — Mermaid diagrams in more artifacts
**Priority:** Medium · **Effort:** Low–Medium · **Type:** quality
**Origin:** the 2026-06-11 Mermaid-diagrams add (Stage 16 shipped first as the
highest-impact area). Spec/plan: `docs/superpowers/{specs,plans}/2026-06-11-mermaid-diagrams*`.

Stage 16 now embeds a target-state architecture flowchart (live HTML render via CDN +
capability-gated `mmdc` PNG/SVG export), all driven by the single-source theme in
`refs/mermaid-diagrams.md`. The same method extends cleanly to:
- **Gantt timeline** for the MVP Build Plan (Stage 8) — phases/milestones.
- **Marketecture solution-layer flowchart** (Stage 14).
- **Consumption data/agent interaction flow** (Stage 18).

**Done looks like:** each chosen stage builds its `.mmd` from the same theme directive,
injects a `{{..._MERMAID}}` token (brace-safe), and reuses the `mmdc` export path —
no second theme definition.

### R10 — Google Drive ingestion as a research source
**Priority:** Medium · **Effort:** Medium · **Type:** capability
**Origin:** 2026-06-16 session — "we often have additional artifacts in Google
Drive that may also inform the POV; does it make sense to wire up [an MCP] to
ingest as well?"

Engagement-relevant source material (discovery decks, call notes, partner
one-pagers, BVS business cases, architecture docs) frequently lives in a shared
Google Drive. Today it informs the POV only by hand — the author reads it and
re-types the relevant facts into Stage 2. This is the same *shape* of input the
skill already fuses from Org62 engagement pre-fill, Slack enrichment, and web
research; Drive is one more source feeding an existing fusion engine, not a new
mechanism. Ingestion is read-only (no write surface, no clobber/sync risk) and
inherits the existing provenance discipline — Drive-sourced facts get tagged
`[from Drive: <doc> — confirm]`, exactly parallel to the `[from internal Slack —
confirm]` pattern, and never harden to confirmed without partner confirmation.

**Open questions to resolve first:**
- **Reuse vs. new server.** A read-only `google-drive-reader` skill already
  exists ("browse, list, explore by URL/ID"). Determine whether it can *extract
  content* or only list — if it extracts, wire tech-strat-pov-forge to call it directly
  and skip standing up a new MCP. Build no infrastructure that already exists.
- **Extraction fidelity by format.** Listing is trivial; clean text extraction
  differs per type (Google Docs/Sheets generally clean; binary PDFs and
  image-heavy decks are lossy). Scope expectations accordingly.
- **Scope = targeted, not the whole drive.** Opt-in per engagement: the author
  names specific files/folder IDs (naming = consent, mirroring the Slack-channel
  pattern), never a blanket shared-drive crawl.
- **Sensitivity.** Drive folders often hold rawer material than curated Slack
  channels; the scrub-before-external rule applies *more* carefully since
  ingested content can surface in a later externally-shared artifact.

**Done looks like:** an optional, read-only Drive enrichment step in Stage 2,
parallel to Slack enrichment — author passes engagement folder/file IDs, the
skill extracts + summarizes + trust-tags facts. Pairs naturally with the Org62
engagement pre-fill ([[org62-engagement-prefill]]): the `Partner_Engagement__c`
record could carry the Drive folder link so the POV pulls Org62 + Drive + Slack
from one engagement pointer. Strictly additive — declining or any blank falls
through to existing research/ask, like every other pre-fill source.

### R11 — Publish/export artifacts to a shared Google Drive
**Priority:** Low · **Effort:** Medium · **Type:** distribution
**Origin:** 2026-06-16 session — "is it possible to have [the POV/PoC tools]
place artifacts into a shared Google Drive?" (companion to R10's ingestion side).

The skills produce excellent *local* artifacts; stakeholders increasingly want
them in a shared Drive. No write-capable Drive tool is currently connected (the
only Drive capability is the read-only `google-drive-reader` skill), so this is
net-new. Three candidate mechanisms, differing mainly on sync behavior:
- **Drive for Desktop (synced output folder)** — zero code; OS file-watcher
  auto-publishes edits. Cleanest "edit locally → current in Drive" experience.
- **`rclone`/CLI post-build sync** — skill runs it as a post-build step; push
  on demand (re-syncs only when re-run), good for a deliberate "publish now."
- **Drive MCP with write scope** — I upload artifacts directly, same as the
  Slack `create_canvas` flow; re-upload required per edit.

**Hard caveats (name these in any design):**
- **HTML doesn't render in Drive.** Styled SLDS decks upload as `.html` files
  that download rather than display; Docs/Slides don't import custom-CSS HTML
  cleanly. Drive works as a shared *file store*, not a viewing surface for the
  visual deliverables (same limitation hit with Slack canvas — text artifacts
  travel cleanly, visuals don't).
- **Sync ≠ collaboration.** These are file-sync mechanisms, not merge-aware
  co-editing. Artifacts are *generated*, so the sound model is **local (skill
  output) = source of truth, Drive = published mirror, view/comment only**; a
  regenerate run will overwrite Drive-side edits (last-writer-wins, generator
  wins). True in-Drive collaborative editing is a different, bigger lift
  (convert to native Docs/Slides on upload, lose SLDS styling, abandon
  regenerate-from-source) — out of scope unless explicitly wanted.

**Done looks like:** an optional post-build publish step (likely Drive-for-Desktop
folder or `rclone` sync — decide during design) that mirrors the artifact folder
to a designated shared Drive folder, documented as a one-way publish with the
HTML-rendering and source-of-truth caveats stated up front. Lower priority than
R10 — ingestion automates a step done by hand today; export is a convenience over
the existing local output.

### R7 — Fan-out critic loops (spec + plan + built branch ready to merge)
**Priority:** Medium · **Effort:** Low (already built; just merge) · **Type:** quality
**Origin:** the 2026-06-08 "would looping help?" design session.

Two bounded QA loops on the package fan-out, to catch the **semantic** defects the
mechanical patches and one-pass self-grading miss: **(1)** a per-artifact
`generate → critic → repair` pipeline on the three heavy artifacts (Stages 8/9/16),
with a widened (generator-parity) critic payload + a mandated-build-detail exclusion;
**(2)** a Wave-2 package completeness-critic over the whole package (contradiction vs.
POV, contradiction between artifacts, unexplained confidence drift, anti-overlap). Both
detect→auto-repair (1 round), independent subagents, scoped-edit repair + post-repair
re-validation gate, gated to the fan-out path.

Unlike the other backlog items, this one is **fully built and reviewed** — spec at
`docs/superpowers/specs/2026-06-08-critic-loops-design.md` (revised after an empirical
lean-vs-wide critic test on the citnow + particle-health packages showed a 36–53%
false-positive rate on the lean payload — that test is why the payload is widened),
plan at `docs/superpowers/plans/2026-06-08-critic-loops.md`, and the implementation on
branch **`feature/critic-loops`** (4 commits, validator 62→67, suite green). Deliberately
**parked unmerged** at Brandon's direction — roadmap it; merge when there's time to dogfood
it on a live package run first. The spec/plan/backlog live on `main`; only the
implementation commits sit on the branch.

**Done looks like:** dogfood the loops on a real package regeneration (the skill's best
bug-source per the dogfooding history), then fast-forward `feature/critic-loops` → `main`
and delete the branch. The merge is clean (main hasn't moved since the branch point).
