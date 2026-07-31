# workshop-forge — Schema-Richness Pass (Design)

**Date:** 2026-07-16
**Status:** Approved (brainstorming) → ready for implementation plan
**Baseline:** `main` @ `ba993d3` (published private, 13/13 validate + scaffold green, 2× dogfooded)

## Problem

The `config/kit.json` overlay schema was extracted from the headless360 kit. Both dogfoods
(headless360, data360) confirmed the deterministic scaffolder works, but data360 exposed
load-bearing concepts the schema **cannot express**, and the nCino kit shape (flatter, older,
ships sample data) further stresses it. This is the top **High** item in `BACKLOG.md`:
the overlay under-models real kits.

This pass adds the schema richness that unblocks a faithful representation of real kits,
strictly **additively** — no existing overlay or golden fixture changes behavior.

## Scope

Four schema/doc changes plus a README overview section and a defined-but-deferred nCino dogfood.
All additive and backward-compatible.

**Explicitly out of scope (deferred):**
- **Tiered-fallback provisioning** (`provisioning.tiers[]`) — the structurally riskiest backlog
  item; touches the org-provisioning template + doc. Deferred to a later pass. Its vocabulary is
  still reconciled in docs (see §3) so the enum is consistent, but no tiered *rendering* is built.
- **Surface-driven directory stubs** (Medium) — surfaces stay descriptive-only (honors the
  2026-07-15 adversarial-review decision #5).
- **Template de-biasing** (Medium) — framework/buildability opt-in is a separate concern.
- **Running the nCino dogfood** — defined here, executed after the schema lands.

## Design

### 1. Schema & scaffolder changes (`scripts/scaffold_kit.py`)

All changes are additive; a kit.json without the new fields renders byte-identically to today.

#### 1a. Optional + mode-gated modules
`modules[]` entries gain two optional keys:
- `optional: true` (bool) — stamps the GUIDE header as `## Module N: Title (Optional)`.
- `modes: ["lab"]` or `["engagement"]` (non-empty list of valid mode strings) — the module is
  **emitted only when the kit's top-level `mode` is in the list**. A module whose `modes` excludes
  the kit mode is omitted from GUIDE.md entirely.

Behavior notes:
- Modules emit no files (headers only in GUIDE.md), so mode-gating a module changes only the
  `MODULE_LIST` token — no impact on `check.sh` REQUIRED_FILES.
- `optional` and `modes` are independent; a module can be both.
- Ordering is preserved (existing behavior); gated-out modules simply drop from the list.

Validation additions in `_validate`:
- If `optional` present and not a bool → `ValueError` (clear message, module index + n).
- If `modes` present: must be a non-empty list; every element must be a known mode string
  (`"lab"`, `"engagement"`). Otherwise → `ValueError`.

#### 1b. `sample_data_path` / BYO dataset
New optional field under `reference_build`:
```jsonc
"reference_build": { "source": "...", "path": "sfdx/", "sample_data_path": "data/" }
```
- When `sample_data_path` is set + non-empty: scaffolder emits `data/.gitkeep` and a
  `data/README.md` stub (explains the dir holds sample datasets the kit references; author mode
  fills specifics). `check.sh` asserts the `data/` dir is present.
- Path value is run through the existing `_safe_path()` before reaching any bash/`check.sh`.
- When absent: nothing emitted (back-compat). The stamped `data/README.md` body uses an
  author-mode stub marker, consistent with other authored content.

#### 1c. surfaces convention (docs + no code behavior change)
`surfaces` stays descriptive-only. Add an explicit documented convention:
- `surfaces: {}` (present, empty) → **"no surfaces, by design"** (e.g. a Data-Cloud pipeline kit).
- `surfaces` key omitted entirely → **"not yet decided."**
No scaffolder behavior change; this removes the documented ambiguity flagged in BACKLOG.

#### 1d. model enum reconciliation (docs)
Single source of truth for the `provisioning.model` enum lives in `refs/provisioning-models.md`.
`refs/kit-anatomy.md` references it rather than re-listing. `tiered-fallback` is documented as a
**recognized-but-not-yet-scaffolded** value (⚠️ flagged) so the vocabulary is consistent even
though tiered rendering is out of scope.

### 2. Tests (`tests/test_scaffold.py`, fixtures)

The skill golden-file-tests its own generator (byte-equal + meta-check that runs the generated
`check.sh` + mutation discipline).

- **Existing fixtures unchanged:** `tests/fixtures/educate/` and `tests/fixtures/full/` stay
  **byte-identical** — this is the back-compat proof. If any expected file changes, the design is
  violated and we stop.
- **New third fixture** `tests/fixtures/rich/` exercising all new fields in one overlay:
  an `optional: true` module, a `modes`-gated module (gated in and one gated out), and
  `reference_build.sample_data_path`. Includes its own `expected/` tree and passes the meta-check
  (generated `check.sh` returns ALL GREEN).
- **Targeted behavioral cases** in `test_scaffold.py`:
  - mode-gated module included when mode matches; omitted when it doesn't
  - optional module renders the `(Optional)` marker
  - `data/` dir + `data/README.md` emitted iff `sample_data_path` set
  - new `_validate` error paths: non-bool `optional`, empty `modes`, unknown mode string
  - determinism: the rich fixture renders byte-identically on repeat runs

Run `python3 tests/validate_skill.py` and `python3 tests/test_scaffold.py`; both must stay green
(13/13 + all scaffold cases). Pre-commit + CI enforce.

### 3. Docs

- `refs/kit-anatomy.md` — schema block gains `optional`/`modes` on modules, `sample_data_path`
  under reference_build, the `surfaces` `{}`-vs-omitted convention; model enum points to the ref.
- `refs/guide-conventions.md` — how optional + mode-gated modules render in GUIDE.md.
- `refs/provisioning-models.md` — owns the `provisioning.model` enum (incl. `tiered-fallback` as
  recognized-but-not-scaffolded ⚠️); elevate `needs_org: false` as the documented **conceptual /
  educate-only** path (first-class, restated where the model picker lives).
- `README.md` — updated overlay example + the new "anatomy of the output" section (§4 of ask).
- `BACKLOG.md` — check off landed items (optional/mode-gated modules, sample_data_path, surfaces
  + enum cleanup); note tiered-fallback + surface stubs + de-biasing still deferred; note the
  nCino dogfood is defined and pending execution.

#### README "anatomy of the output" section
One combined section giving, per generated artifact: **purpose · audience · when-used**, plus a
short "how they compose into one kit" paragraph. Covers the full output set (GUIDE, FACILITATOR,
README, LESSONS-LEARNED, framework/buildability docs, org-provisioning, scripts, check.sh, content
dirs, data/, sfdx/). Audiences: participant / facilitator / partner-exec / ops. Timing:
pre-provision (T-minus) → facilitator prep → in-room delivery → retro.

### 4. nCino dogfood (defined now, executed after schema lands)

Validation vehicle for the schema work. The real kit lives at
`~/claude-projects/ncino-pov/ncino-workshop` (flatter/older: no FACILITATOR.md, no docs/, but has
`data/` and engagement-specific scripts `05-seed-data.sh` / `06-smoke-test.sh`).

Procedure:
1. Hand-write a `kit.json` for the nCino kit: `mode: "engagement"`, `partner_overlay: "nCino"`,
   `provisioning.model: "assigned-preconfigured"` + shared-MCP-backend framing,
   `reference_build.sample_data_path` set, and an `optional: true` self-service-rebuild module.
2. `python3 scripts/scaffold_kit.py <that>.json ./dogfood-ncino` (a throwaway/gitignored dir).
3. Structurally diff `./dogfood-ncino` against the real `ncino-workshop`.
4. Record findings in `docs/superpowers/dogfood-ncino.md`.

Success criteria:
- The **new fields express nCino's shape** — `sample_data_path` produces the `data/` dir; the
  optional module renders; engagement mode gates correctly.
- Residual deltas are **categorized**: expected (authored content, engagement-specific scripts that
  are author-mode's job, the flatter hand-built layout) vs. **genuine gaps** (schema still can't
  express something real). Genuine gaps become new BACKLOG items, not silent.
- Because some nCino-family workshops are more **conceptual** (org shape lower-priority), the
  dogfood explicitly notes where org-shape mattered less and confirms the `needs_org` /
  conceptual-path framing reads correctly for an engagement-mode kit.

## Success criteria (whole pass)

- All four schema/doc changes land; `educate` + `full` goldens byte-identical (back-compat proven).
- New `rich` fixture + behavioral tests green; `validate_skill.py` stays 13/13.
- README carries the "anatomy of the output" section; docs reconciled (enum single-source).
- nCino dogfood defined as an executable task with inputs, diff target, and success criteria.
- BACKLOG updated to reflect what landed vs. what's still deferred.

## Risks / mitigations

- **Golden drift** — new behavior accidentally perturbs existing fixtures. *Mitigation:* additive
  code paths guarded on presence of new keys; byte-equality of existing goldens is an explicit
  gate.
- **Enum divergence recurs** — two docs list the enum again. *Mitigation:* one owner
  (`provisioning-models.md`), the other references it.
- **`data/README.md` stub vs. noise** — emitting a data dir the kit doesn't use. *Mitigation:*
  gated strictly on `sample_data_path` being set.
