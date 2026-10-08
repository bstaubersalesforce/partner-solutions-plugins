# Vendor provenance

Each skill under `partner-solutions/skills/` is vendored from its canonical repo in `~/.claude/skills/` via `scripts/sync-skills.sh` (`git archive HEAD`). Source commit at vendor time:

| Skill | Source repo | Vendored @ commit | Date |
|-------|-------------|-------------------|------|
| `tech-strat-pov-forge` | https://github.com/bstaubersalesforce/tech-strat-pov-forge | `7263e2b` | 2026-07-31 |
| `pie-poc-forge` | https://github.com/bstaubersalesforce/pie-poc-forge | `75847ba` | 2026-07-31 |
| `ps-npi-forge` | https://github.com/bstaubersalesforce/ps-npi-forge | `5e5ced3` | 2026-07-31 |
| `workshop-forge` | https://github.com/bstaubersalesforce/workshop-forge | `02f7435` | 2026-07-31 |
| `partner-blocker-forge` | https://github.com/bstaubersalesforce/partner-blocker-forge | `88a4417` | 2026-07-31 |
| `partner-account-tech-plan` | https://github.com/bstaubersalesforce/partner-account-tech-plan | `51013ac` | 2026-10-08 |

Re-run `scripts/sync-skills.sh` after committing changes in any source repo, then update this table + CHANGELOG and bump the suite version in `partner-solutions/.claude-plugin/plugin.json`.
