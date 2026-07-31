# Assessment Run — skill-forge audit of ps-npi-forge

**Date:** 2026-06-24
**Auditor:** skill-forge (Audit mode, inspect-only)
**Target:** `ps-npi-forge` @ v0.2.0 (commit `e58b40d`)
**Trigger:** Brandon — run skill-forge against the new NPI skill to see the result.

> Inspect-only: skill-forge read the target's files and ran its own rubric
> snippets against them; it never executed ps-npi-forge's code or its suite.

## Verdict

**Complexity tier:** 3 (Platform)   **Build tier:** 3 (Platform)

**No tier gap. Complexity demands Tier 3; built like Tier 3.** The discipline
matches the ambition. Every Tier-3-required rubric ID passes mechanically except
one, and that one is a false-positive in skill-forge's own audit snippet — not a
defect in ps-npi-forge.

Complexity is unambiguously Tier 3: multi-output (13 artifacts + Key Resources
canvas + slide deck), deterministic `scripts/` with golden fixtures across three
domains, and a manifest-driven multi-stage generate→refine→validate flow.

## Rubric scorecard

| ID | Min Tier | Practice | Result | Evidence |
|----|----------|----------|--------|----------|
| R-FM-01 | 1 | Frontmatter w/ name+description | PASS | `SKILL.md` opens with valid YAML frontmatter |
| R-REF-01 | 1 | Refusal/scope conditions stated | PASS | SKILL.md names the hard out-of-scope rules |
| R-ARCH-01 | 2 | Lazy-loaded `refs/` | PASS | 7 ref modules, none inlined |
| R-ARCH-02 | 2 | No dangling path references | PASS | every referenced path resolves |
| R-ARCH-03 | 2 | No orphan files | FAIL\* | *false-positive — see note* |
| R-TEST-01 | 2 | `tests/validate_skill.py` exists, stdlib-only | PASS | present |
| R-TEST-02 | 2 | Token hygiene in templates | PASS | all `{{TOKEN}}` UPPER_SNAKE, balanced |
| R-TEST-03 | 3 | Router/index bidirectional sync | PASS | n-a (no `refs/stages/`); no-op passes |
| R-TEST-04 | 2 | Scripts exercised behaviorally + fixtures | PASS | `spec_from_file_location` loads scripts; fixtures under `tests/fixtures/{manifest,org62,render}` |
| R-CI-01 | 2 | Tracked pre-commit runs suite | PASS | `.githooks/pre-commit` runs `validate_skill.py` |
| R-CI-02 | 3 | CI workflow runs suite | PASS | `.github/workflows/validate.yml` |
| R-PROC-01 | 3 | spec→plan archive | PASS | 4 specs + 6 phase plans under `docs/superpowers/` |
| R-DOC-01 | 2 | README documents + invocation | PASS | substantial README, v0.2.0 |
| R-GIT-01 | 2 | Git repo, ≥1 commit | PASS | 81 commits, tagged v0.2.0 (audit-only, manual) |

**12/13 mechanical PASS + R-GIT-01 PASS.** The lone FAIL is a tooling artifact.

### \* R-ARCH-03 is a skill-forge snippet false-positive, not a ps-npi-forge defect

`chk_no_orphans` flagged all 13 `templates/<slug>.md` files + `templates/manifest.yaml`
as orphans. They are **not** orphans — they are referenced by *pattern*:

- `SKILL.md:53` — "the 13 deliverables are generated from skeletons in `templates/`"
- `refs/artifact-templates.md:3` — "live in `templates/<slug>.md`, one per `ARTIFACT_REGISTRY` slug"
- `templates/manifest.yaml` — referenced from `SKILL.md:17` and `refs/quality-loops.md`

And ps-npi-forge's *own* suite binds every one of them mechanically:
**R-TPL-01** asserts each registry slug has a `templates/<slug>.md` (and rejects
unknown slugs), **R-MANIFEST-05** covers `manifest.yaml`, and **R-TEST-02** scans
all of them for token hygiene. There is zero real orphan risk.

The snippet only matches *literal* paths, so a pattern-referenced family of files
reads as orphaned. This is the same glob-blindness the rubric already patched in
`chk_refs_exist` (which skips `*` / `{` / `NN` placeholders) but did **not** apply
in `chk_no_orphans`. **Fix belongs in skill-forge**, not here.

## Maturity & design read

ps-npi-forge is a textbook Tier-3 build and the most rigorous of the three sibling
skills (pov-builder, pie-poc-forge, ps-npi-forge). Signals:

- **Behavioral test depth beyond the rubric floor.** R-TEST-04 only asks that
  scripts be exercised with fixtures. The target has 44 checks, golden fixtures
  across three domains, mutation-verified sanity gates, and *systemic* guards like
  R-DOC-01 (count-drift) that catch a whole class of future bug rather than one
  instance. That is Tier-3+ behavior.
- **The spec→plan archive is substantive, not ceremonial** — six phase plans + four
  specs tracing the real build.
- **CI + pre-commit both run the suite** — discipline enforced, not aspirational.

The honest structural critique is not about the build tier: ps-npi-forge carries
the **same shared-ref duplication** as its siblings (`mermaid-diagrams.md` and the
SLDS theme are copied in, kept in sync by hand). The rubric audits one skill in
isolation, so it cannot see cross-skill DRY — but this is the debt that ties
directly to the open "package as a plugin?" question.

## The one decision worth a real conversation

Three independently-audited Tier-3 skills, each passing its own rubric, each
carrying a hand-synced copy of the same shared refs. The audit cannot fault any
one of them — but the *duplication across them* is exactly the debt a plugin
retires. This audit is evidence **for** packaging the family: not because the
skills are immature (they are not), but because they have matured into a family
that the single-skill view structurally cannot optimize.

## Remediation

**Nothing to remediate in ps-npi-forge** — clean Tier-3 pass. The one actionable
item is in **skill-forge itself**: give `chk_no_orphans` (R-ARCH-03) the same
glob/pattern-skip that `chk_refs_exist` already has, and credit pattern references
like `templates/<slug>.md`. That turns this audit to a clean 13/13 and hardens the
checker against the same false-positive on pov-builder and pie-poc-forge.
