# Partner Solutions Forge — Claude plugin + marketplace

A travelable Claude Code **marketplace** carrying the five Tier-3 *-forge skills the Partner Solutions team uses to
turn partner engagements into structured deliverables. Install once, get all five; update by re-pulling the repo.

## The skills

| Skill | Turns… | …into |
|-------|--------|-------|
| **tech-strat-pov-forge** | a partner solution narrative | a Point-of-View doc / OG Tech Strategy worksheet |
| **pie-poc-forge** | a POV build plan or pasted requirements | an installable PoC SFDX package + execution/config/security/gaps canvas |
| **ps-npi-forge** | sources for a new Embedded/OEM product | the PS-owned NPI artifact family (15 artifacts + canvas + deck) |
| **workshop-forge** | proven kit pattern + sources | a Salesforce partner workshop/lab kit (scaffold + author) |
| **partner-blocker-forge** | a partner-reported technical blocker | a claimed-vs-real, evidence-based diagnosis + deliverable |

## Install (team members)

```
/plugin marketplace add <this-repo-url-or-path>
/plugin install partner-solutions
```

Then invoke any skill by name (`/tech-strat-pov-forge`, `/pie-poc-forge`, …) — installing the plugin makes all
five available; it does not change how you invoke them.

## Layout

```
.claude-plugin/marketplace.json     # the marketplace (one plugin: partner-solutions)
partner-solutions/
  .claude-plugin/plugin.json        # the plugin (suite version + changelog live here)
  skills/                           # the five skills, vendored as real content
    tech-strat-pov-forge/  pie-poc-forge/  ps-npi-forge/  workshop-forge/  partner-blocker-forge/
scripts/sync-skills.sh              # re-vendor from the canonical skill repos
```

## How this is maintained (important)

- **The canonical skill repos live in `~/.claude/skills/<skill>` (each its own git repo).** That is where you
  **develop, test, and commit** — each skill keeps its own `tests/validate_skill.py`, pre-commit hook, and CI.
- **This monorepo is a distribution artifact.** The `skills/` trees are **vendored copies** produced by
  `scripts/sync-skills.sh` (`git archive HEAD` per source repo → tracked files only; `.git`/`.notes`/`.superpowers`
  never travel). After committing a change in any source skill, run the sync script and commit the refresh here.
- **Do not hand-edit `partner-solutions/skills/**`** — edits there are overwritten on the next sync. Change the
  source skill, then sync.

## Versioning

One **suite version** in `partner-solutions/.claude-plugin/plugin.json` (starts `0.1.0`) + a changelog, rather than
five independent semvers. Bump on any material skill change that ships to the team.

## Not included (by design)

Scope is the **five partner-deliverable forge tools**. Out of scope: post-install runners
(`partner-package-post-install`, `sf-package-post-install`), `sf-flex-estimator`, `skill-forge`, and personal
skills — different audiences; a separate plugin can carry those if the team wants them.

## Deferred (v2)

- **Shared-ref dedup.** `org62-prefill.md` (pov+poc) and `mermaid-diagrams.md` (pov+poc+npi) are still per-skill
  copies (each referenced by relative path inside its skill). Hoisting to a plugin-level `shared-refs/` would
  retire the parity checks but requires rewriting those references — deferred so v1 vendors skills verbatim and
  every skill keeps passing its own validator unchanged.
