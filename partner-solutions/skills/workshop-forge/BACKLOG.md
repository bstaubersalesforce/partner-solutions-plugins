# workshop-forge — Backlog

Consolidated from two dogfoods (`docs/superpowers/dogfood-headless360.md`, `docs/superpowers/dogfood-data360.md`)
and the adversarial review (2026-07-15). Ordered by value. Nothing here blocks use of the shipped skill; these are the
known limits and the next improvements.

## What's proven vs. what's next

- **Proven (tested + dogfooded):** the deterministic scaffolder (determinism, token coverage, conditional rendering,
  self-validating `check.sh`), the provisioning decision guide (correctly discriminates DE-for-Agentforce vs SDO-for-Data-Cloud
  across both dogfoods), input validation + value scrubbing.
- **Real but human-review-gated:** author/enrich mode — mock-run against data360 produced coherent Module 2/3 drafts at
  ~80% quality (judgment estimate from one mock, not a measured figure); plateaus on domain-specific teaching depth. Assistive
  drafter, not a final generator. Never yet run interactively for real.

## High — the overlay under-models real kits (schema richness)

The current `config/kit.json` schema was extracted from headless360; data360 exposed load-bearing concepts it can't express.

- [ ] **3-tier provisioning fallback** — deferred — vocabulary reserved as `tiered-fallback`, rendering not built. Real kits define a sequence (partner PBO org → facilitator-provisioned pool → shared reference org, degraded). Current schema has a single `provisioning.model`. Add an optional tiered/fallback shape.
- [x] **`sample_data_path` / BYO dataset** — **landed 2026-07-16**
- [x] **Optional modules** — **landed 2026-07-16**
- [x] **Interleaved / mode-gated modules** — **landed 2026-07-16 (via `modes`)**
- [x] **`surfaces: {}` semantics** — **landed 2026-07-16 (documented convention)**
- [x] **Document `provisioning.model` enum** — **landed 2026-07-16 (enum table in provisioning-models.md)**

## Medium — content the scaffolder should stub

- [x] **`data/` directory** — **landed 2026-07-16**: `reference_build.sample_data_path` set ⇒ scaffolder stamps a `data/`
      dir + `data/README.md` stub, and the generated `check.sh` requires it. (Populating the 53 actual data files remains
      author-mode's / the reference build's job.)
- [ ] **Surface-driven stubs** — `surfaces.web:true` currently creates nothing (surfaces are descriptive-only by design).
      Consider: when a surface implies a directory (e.g. `web/` for the React Agent-API surface), emit a minimal stub
      (`web/.env.example`, `web/README.md`) instead of leaving it to author mode. Design tension: helpful stub vs. noise.
- [ ] **Engagement-specific setup scripts** — the real headless360 kit has a ~180-line `04-mcp-connect-setup.sh`; the
      scaffolder emits nothing of that class. Currently deferred to author mode. Consider a generic `NN-<name>-setup.sh.tmpl`
      stub the overlay can request.

## Medium — de-bias the templates (Agentforce/MCP assumptions)

- [ ] The scaffolder over-generates MCP/Agentforce-flavored files (`framework.md`, `buildability-matrix.md`, numbered
      deploy/assign scripts) that are noise for a Data-Cloud kit (harmless — `check.sh` stays green, but reveals the design
      grew out of headless360). Make framework/buildability docs opt-in via the overlay, or topic-neutral.
- [ ] **Doc-name convention** — real kits use descriptive provisioning doc names (`org-provisioning-and-session-journey.md`)
      vs the scaffolder's fixed `org-provisioning.md`. Minor; either accept or make the name overlay-driven.

## Validate — close the confidence gaps

- [ ] **Run author mode for real, interactively** — both dogfood author passes were *mocked* (simulated by a subagent),
      never run as a live interactive flow. Do one real run against an actual pie-poc-forge PoC and measure output quality.
- [x] **Third dogfood: nCino (scaffold)** — **done 2026-07-16** (`docs/superpowers/dogfood-ncino.md`). Confirmed the skill
      handles nCino's flatter/older shape (assigned-preconfigured org, engagement mode); all 4 new schema fields expressed it;
      no new gaps. Remaining nCino coverage = a *live author-mode* run (folded into the "Run author mode for real" item above).

## From the headless360 workshop maturation (evaluated 2026-07-31)

The headless360 kit accreted several maturity artifacts *by hand, after* scaffolding — a signal that the skill
scaffolds the skeleton but not the artifacts a kit grows in real use. Evaluated all five; shipped 3, documented 1,
declined 1.

- [x] **L1 — `KNOWN-GAPS.md` as standard anatomy.** ✅ **shipped 2026-07-31.** New `templates/KNOWN-GAPS.md.tmpl`
      added to `ALWAYS` (auto-flows into check.sh REQUIRED_FILES); a single open/unverified/watch-before-the-event
      list every mature kit needs. All 3 goldens regenerated; +2 behavioral assertions.
- [x] **L2 — capability-first vs. build-live sequencing principle.** ✅ **shipped 2026-07-31.** Added to
      `refs/guide-conventions.md`: default to touring a pre-staged fragile core + spending hands-on on
      surface-wiring; front-load the one hard ordering gate; when build-live is still right. Pedagogy guidance, no
      scaffolder change.
- [x] **L3 — credential-setup cookbook as an org-gated artifact.** ✅ **shipped 2026-07-31.** New
      `templates/docs/credential-setup-cookbook.md.tmpl`, emitted iff `needs_org:true` (mirrors org-provisioning
      conditional); topic-neutral (what-to-create / the-gotcha / the-verify-step). Isolates the #1 silent-failure
      time-sink out of the GUIDE. `full` golden regenerated + check.sh updated.
- [ ] **L4 — naming + module-number drift.** Origin: headless360 was built as "Summit," renamed "Workshop," and
      the capability-first reorder left stale module numbers — both needed reconciliation sweeps. Why: kits carry a
      program name + module numbers that drift when edited by hand. Done when: `guide-conventions.md` notes that the
      event name + module numbers are overlay-derived single-source values (don't hardcode in prose), reducing
      future drift. **Low effort; documented here, not yet in the ref.**
- **L5 — multi-track *event* orchestration (program/commercial/bridge/PAM-invite layer).** ❌ **DECLINED — out of
      scope by design.** headless360 grew a dual-track program, commercial track, summit→DF bridge, and PAM outreach.
      workshop-forge produces workshop **content**; event orchestration + logistics belong to the program layer /
      the PIE Lab Slack logistics companion (`refs/lab-logistics-companion.md`). Recorded so this is a deliberate
      "no," not an oversight — do not absorb.

## Acknowledged-by-design (limits, not bugs — documented, won't "fix")

- `check.sh` validates file **presence + link resolution, not content** — a kit can have an empty README and pass. Matches
  the sibling kits' convention.
- **Golden tests are regression guards, not correctness oracles** — generated by the code they test; regenerating goldens can
  mask drift. Mitigated by manual mutation-verification discipline, not enforced automatically.
- **Provisioning residual confirmations** (free-DE `mcp_api` pre-enablement; the Data-Cloud-connector datapoint) are flagged
  ⚠️ in `provisioning-models.md` but remain unverified until confirmed on-network before a real workshop.
