# Changelog — Partner Solutions Forge

One **suite version** across all five skills (in `partner-solutions/.claude-plugin/plugin.json`), not five
independent semvers. Bump on any material skill change that ships to the team; record the source commits in
`VENDOR.md`.

## 0.1.0 — 2026-07-31

Initial release. Marketplace + `partner-solutions` plugin carrying five Tier-3 *-forge deliverable skills,
vendored from their canonical repos (see `VENDOR.md` for source commits):

- **tech-strat-pov-forge** — POV docs / OG Tech Strategy worksheet (@7263e2b)
- **pie-poc-forge** — installable PoC SFDX package + execution canvas (@75847ba)
- **ps-npi-forge** — PS NPI artifact family (15 artifacts + canvas + deck) (@5e5ced3)
- **workshop-forge** — partner workshop/lab kit scaffolder + author (@02f7435)
- **partner-blocker-forge** — claimed-vs-real blocker diagnosis + deliverable (@88a4417)

All five vendored copies re-validate identical to their standalone baselines (77 / 18 / 61 / 13 / 14 checks).
Shared-ref dedup (org62-prefill, mermaid-diagrams) deferred to a future release — v1 vendors verbatim so each
skill keeps passing its own validator unchanged.
