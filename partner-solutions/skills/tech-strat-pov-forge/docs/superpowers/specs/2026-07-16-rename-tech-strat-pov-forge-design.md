# Rename `pov-builder` → Tech Strat POV Forge (Design)

**Date:** 2026-07-16
**Status:** Approved (brainstorming) → ready for implementation plan
**Baseline:** repo `main` @ `fdcebf3` (ahead of origin by 1), validator **77/77**, tree otherwise clean.

## Goal

Rename the POV skill from `pov-builder` / "POV Builder" / repo `salesforce-isv-pov-builder`
to the `*-forge`-family-consistent **Tech Strat POV Forge** across every layer that carries
the name — locally, on GitHub, in the live Slack config, and in cross-skill / memory references —
while preserving dated historical records as point-in-time documents.

## Canonical new names

| Layer | Old | New |
|-------|-----|-----|
| Invocation slug (`SKILL.md` `name:`) | `pov-builder` | `tech-strat-pov-forge` |
| Physical directory | `~/.claude/skills/pov-builder/` | `~/.claude/skills/tech-strat-pov-forge/` |
| GitHub repo | `bstaubersalesforce/salesforce-isv-pov-builder` | `bstaubersalesforce/tech-strat-pov-forge` |
| Human title (H1) | `POV Builder` | `Tech Strat POV Forge` |
| Slack config file | `~/.claude/pov-builder-slack.json` | `~/.claude/tech-strat-pov-forge-slack.json` |
| Memory file | `memory/pov-builder-skill.md` | `memory/tech-strat-pov-forge-skill.md` |

## Key facts established during brainstorming (ground truth)

1. **Single physical directory.** `~/.claude/local-marketplace/brandon-skills/skills` is a
   **symlink** to `~/.claude/skills`. Therefore `pov-builder` is ONE directory reached via two
   paths; a single `mv ~/.claude/skills/pov-builder ~/.claude/skills/tech-strat-pov-forge`
   updates both views. No dual-path handling needed.
2. **Marketplace manifest does not enumerate skills by name.** `marketplace.json` +
   `brandon-skills/.claude-plugin/plugin.json` name only the *plugin* (`brandon-skills`), not
   individual skills. The rename does NOT touch either manifest.
3. **org62-prefill parity check is content-based.** `tests/validate_skill.py` compares
   `refs/org62-prefill.md` between this skill and `pie-poc-forge` by **content** (`here == there`),
   not by path/name — unaffected by the rename, but re-verify green after.
4. **Config file is named in the validator.** `validate_skill.py` asserts
   `"pov-builder-slack.json" in txt` at two points (lines ~893, ~917) — these MUST move to the new
   config name in lockstep with the file rename, or the validator fails.
5. **Repo is a normal git repo** on `main`, ahead of origin by 1 (the earlier local commit). The
   rename commits stack on top; push includes the backlog commit already present.
6. **Clone URL** appears in `README.md:266` (`git clone …/salesforce-isv-pov-builder.git`).
7. **GitHub auto-redirects** the old repo URL after `gh repo rename`, so external clones/links
   don't hard-break; still update the documented URL.

## Scope

**In scope (confirmed):** slug, directory, title, GitHub repo, Slack config file, sibling-skill
live refs, workspace `CLAUDE.md`, memory (index + current head + file rename + sibling backlinks).

**History policy (confirmed):** *live files only.* Do NOT rewrite dated `docs/specs/*`,
`docs/plans/*`, or historical dated blocks in memory — they are accurate records of when the skill
was named `pov-builder`. Where a doc *set* is affected, add a single dated rename note at its head
rather than editing bodies.

**Explicitly out of scope:** marketplace manifests (don't name the skill); rewriting historical
spec/plan bodies; any behavioral change to the skill itself.

## Design

Ordered so each step is independently verifiable and the risky/irreversible-ish moves are gated by
investigation and a green validator.

### Step group A — Local repo rename (directory + in-repo content)
1. **Re-confirm symlink structure** immediately before moving (guard against drift):
   `readlink ~/.claude/local-marketplace/brandon-skills/skills` must resolve to `~/.claude/skills`.
2. **Rename the directory:** `mv ~/.claude/skills/pov-builder ~/.claude/skills/tech-strat-pov-forge`.
   Verify the marketplace symlink path now lists `tech-strat-pov-forge`.
3. **In-repo content edits** (all within the renamed dir):
   - `SKILL.md`: `name: pov-builder` → `name: tech-strat-pov-forge`; H1 `# POV Builder` →
     `# Tech Strat POV Forge`; any self-referential prose.
   - `README.md`: H1; clone URL (`salesforce-isv-pov-builder` → `tech-strat-pov-forge`); config-file
     references (`pov-builder-slack.json` → `tech-strat-pov-forge-slack.json`); "POV Builder" /
     "pov-builder" prose in live sections. Leave any dated changelog-style lines as record.
   - `tests/validate_skill.py`: both `pov-builder-slack.json` assertions → new config name; the
     module docstring/label + the final print label (`pov-builder skill validation`) → new name.
     Do NOT alter the org62-prefill content-parity assertion logic.
   - `.githooks/pre-commit`: update the name string if it is cosmetic only (verify it doesn't
     hard-code a path that breaks; it runs `python3 tests/validate_skill.py` relatively, so a
     name-in-comment is cosmetic).
   - `BACKLOG.md`: update the title/live references; leave dated R-item history intact.
4. **Validator gate:** `python3 tests/validate_skill.py` → expect **77/77** (after config-file
   migration in Step group B, since the config assertions reference the new file — sequence B before
   the final A-gate, or make the assertion name-only and verify the file separately; see Step group B).

### Step group B — Slack config migration
The config file lives OUTSIDE the repo (`~/.claude/`), so `git mv` doesn't apply.
1. Copy `~/.claude/pov-builder-slack.json` → `~/.claude/tech-strat-pov-forge-slack.json`
   (preserve contents exactly; it holds `tool_name: "slack"` etc.).
2. Verify the new file exists and is valid JSON.
3. Grep `~/.claude/settings.json` + any skill for other references to the old config name; update
   live ones.
4. Remove the old `~/.claude/pov-builder-slack.json` only after the copy is confirmed.
5. This step must land **before** the Step-group-A validator gate, because the validator asserts
   the new config filename appears in README/validator text — the physical file and the asserted
   name must agree.

### Step group C — GitHub repo rename
1. `gh repo rename tech-strat-pov-forge --repo bstaubersalesforce/salesforce-isv-pov-builder`
   (or run from within the repo). Confirm success.
2. Update the local remote: `git remote set-url origin
   https://github.com/bstaubersalesforce/tech-strat-pov-forge.git`.
3. Verify `git remote -v` and that `README.md:266` clone URL now matches (edited in Step A3).
4. Push: `git push` (includes the rename commits + the pre-existing backlog commit).

### Step group D — Cross-skill + workspace + memory
Each sibling skill is its own repo → its own commit; commit/push per repo.
1. **Sibling live refs** — update prose `pov-builder` → `tech-strat-pov-forge` (and "POV Builder"
   → "Tech Strat POV Forge" where it's the human title) in the LIVE files of `pie-poc-forge`,
   `ps-npi-forge`, `workshop-forge` (READMEs, BACKLOGs). Leave each sibling's dated specs/plans as
   record. Do NOT touch `refs/org62-prefill.md` content in a way that breaks the parity check
   (that file is about Org62, unlikely to name the skill; verify).
2. **Workspace `CLAUDE.md`** (`~/claude-projects/CLAUDE.md`) — update the skill's name where it's
   referenced (e.g. skill inventory / pov-builder mentions).
3. **`~/.claude/style-conventions.md`** — update if it names the skill.
4. **Memory:**
   - `git mv`-equivalent rename `memory/pov-builder-skill.md` → `memory/tech-strat-pov-forge-skill.md`
     (plain `mv`; memory isn't a git repo).
   - Update the file's frontmatter `name:` slug and add a one-line **rename note** at the head
     ("Renamed from pov-builder → Tech Strat POV Forge on 2026-07-16"); leave dated state blocks intact.
   - Update `MEMORY.md` index line (link target + hook text).
   - Fix `[[pov-builder-skill]]` backlinks in sibling memory files → `[[tech-strat-pov-forge-skill]]`.

### Verification (Step group E)
1. Renamed repo validator green (**77/77**).
2. Skill resolves under the new slug (frontmatter `name:` = `tech-strat-pov-forge`; directory
   matches).
3. Grep sweep: no **live** file (excluding dated `docs/specs/*`, `docs/plans/*`, historical memory
   blocks) contains `pov-builder`, `POV Builder`, or `salesforce-isv-pov-builder`.
4. Each touched sibling repo's validator still green.
5. `~/.claude/tech-strat-pov-forge-slack.json` exists; old config removed; `settings.json` has no
   dangling reference.
6. GitHub: new repo name live, old URL redirects, `origin` updated, pushed.

## Success criteria

- All six canonical-name layers renamed; validator 77/77 in the renamed repo.
- Live grep sweep clean; historical records preserved with head-notes.
- GitHub repo renamed + pushed; local remote updated; clone URL matches.
- Slack config migrated; no dangling references.
- Sibling skills, `CLAUDE.md`, and memory (incl. backlinks) reference the new name; each sibling
  repo committed + still green.

## Risks / mitigations

- **Directory rename breaks the marketplace view** → mitigated: single symlinked parent, re-confirmed
  immediately before `mv`; verify the symlinked path post-move.
- **Validator/config-name desync** → mitigated: Step group B lands before the Step-group-A gate;
  file name and asserted name change together.
- **GitHub rename external breakage** → mitigated: GitHub auto-redirects; documented URL updated.
- **Over-rewriting history** → mitigated: explicit live-files-only policy + head-notes, enforced by
  the grep-sweep exclusion list in verification.
- **Sibling parity check** (org62-prefill) → mitigated: content-based; re-run each sibling validator.
