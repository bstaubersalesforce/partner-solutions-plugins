# Changelog — Partner Solutions Forge

One **suite version** across all five skills (in `partner-solutions/.claude-plugin/plugin.json`), not five
independent semvers. Bump on any material skill change that ships to the team; record the source commits in
`VENDOR.md`.

## 0.2.1 — 2026-10-08

Refreshes **partner-account-tech-plan** to @51013ac — adds `refs/external-sources.md`, a catalog of external
research sources (LinkedIn execs → stakeholder power map, SEC 10-K risk factors, press/newsroom, events,
analyst/review, funding/ownership) wired into the profile and red-team/commercial stages. Vendored copy
re-validates 13/13.

## 0.2.0 — 2026-10-08

Adds the **partner-account-tech-plan** orchestrator (@eb36eb6) — a Tier-3 skill that runs the other five forge
skills as subagents, adds a built-in Org62 case scan and a trust/relationship-posture overlay, and binds them into
one living, V2MOM-framed Partner Account Tech Plan (Measures nested under Methods; Go-Forward gap-closure matrix;
governance as influence-not-own). Dogfood-proven against Riskonnect. Bundling it with its five subagent skills
means one install gives a teammate the orchestrator and everything it calls. Vendored copy re-validates 13/13.

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
