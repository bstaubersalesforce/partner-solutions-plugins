# Rename `pov-builder` → Tech Strat POV Forge — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the POV skill from `pov-builder` to **Tech Strat POV Forge** across every live layer — slug, directory, GitHub repo, Slack config, sibling/workspace/memory references — while preserving dated historical records.

**Architecture:** A mechanical, ordered rename. The physical skill directory is `~/.claude/skills/pov-builder` (the marketplace path is a symlink to `~/.claude/skills`, so one `mv` updates both views). The Slack-config migration lands before the validator gate because the validator asserts the config filename. History (dated `docs/specs/*`, `docs/plans/*`, historical memory blocks) is left as record; only live files change.

**Tech Stack:** git, `gh` CLI, Python 3 stdlib validator (`tests/validate_skill.py`), plain filesystem moves. No code logic changes.

## Global Constraints

- **New canonical names** (verbatim): slug/dir `tech-strat-pov-forge`; title `Tech Strat POV Forge`; repo `bstaubersalesforce/tech-strat-pov-forge`; config `~/.claude/tech-strat-pov-forge-slack.json`; memory file `tech-strat-pov-forge-skill.md`; memory slug `tech-strat-pov-forge-skill`.
- **Live-files-only history policy.** Do NOT rewrite dated `docs/specs/*`, `docs/plans/*`, or historical dated blocks in memory. Add a one-line rename head-note where a doc set is affected; leave bodies.
- **`refs/org62-prefill.md` parity is byte-exact.** The validator asserts `pov-builder/refs/org62-prefill.md` == `pie-poc-forge/refs/org62-prefill.md` byte-for-byte. Line 84 (`**pov-builder:**` label) is the only skill-name reference. It must be edited **identically in both copies or in neither** — never one alone. Recommended: edit both to `**tech-strat-pov-forge:**` in the same task.
- **Validator must end at 77/77** in the renamed repo. Run `python3 tests/validate_skill.py` after edits.
- **Marketplace manifests are OUT of scope** (they name only the `brandon-skills` plugin, not the skill).
- Work happens on a branch off `main` (baseline `fdcebf3`; spec commit `1f7dca1` already on `main`). Do not implement on a detached HEAD.
- The validator root `SKILL` is derived from `__file__` and the parity sibling from `../pie-poc-forge` — both are path-relative and rename-safe; do not "fix" them.

---

### Task 1: Slack config migration (must precede the directory/validator work)

**Files:**
- Create: `~/.claude/tech-strat-pov-forge-slack.json`
- Delete: `~/.claude/pov-builder-slack.json`
- Inspect: `~/.claude/settings.json`

**Interfaces:**
- Consumes: existing `~/.claude/pov-builder-slack.json` contents (keys `tool_name`, `workspace`, `channel_conventions`, `read_window_days`).
- Produces: `~/.claude/tech-strat-pov-forge-slack.json` with byte-identical contents. Later tasks' validator assertions will reference this new filename.

- [ ] **Step 1: Confirm the old config exists and capture its contents**

Run:
```bash
ls -l ~/.claude/pov-builder-slack.json && cat ~/.claude/pov-builder-slack.json
```
Expected: the file exists and prints valid JSON. If it does NOT exist, record that and skip the copy (Steps 2 & 4) — but still verify no live file references it; note the absence in the report.

- [ ] **Step 2: Copy to the new name**

Run:
```bash
cp ~/.claude/pov-builder-slack.json ~/.claude/tech-strat-pov-forge-slack.json
```

- [ ] **Step 3: Verify the new file is valid JSON and identical**

Run:
```bash
python3 -c "import json,sys; json.load(open('/Users/bstauber/.claude/tech-strat-pov-forge-slack.json')); print('valid json')"
diff ~/.claude/pov-builder-slack.json ~/.claude/tech-strat-pov-forge-slack.json && echo "identical"
```
Expected: `valid json` then `identical` (no diff output).

- [ ] **Step 4: Check for other references to the old config name and remove the old file**

Run:
```bash
grep -rn "pov-builder-slack" ~/.claude/settings.json ~/.claude/settings.local.json 2>/dev/null || echo "no settings references"
rm ~/.claude/pov-builder-slack.json
ls ~/.claude/pov-builder-slack.json 2>&1 || echo "old config removed"
```
Expected: no settings reference the old config (if any do, note them for a later task — settings.json is edited in Task 6); old file removed.

- [ ] **Step 5: No commit** (this touches only `~/.claude/`, outside the repo). Record in the report that the config is migrated. Commit happens with repo work in later tasks.

---

### Task 2: Rename the skill directory

**Files:**
- Move: `~/.claude/skills/pov-builder/` → `~/.claude/skills/tech-strat-pov-forge/`

**Interfaces:**
- Consumes: the symlink `~/.claude/local-marketplace/brandon-skills/skills → ~/.claude/skills`.
- Produces: the skill repo at its new path; all later tasks `cd` into the new path.

- [ ] **Step 1: Re-confirm the symlink structure immediately before moving (guard against drift)**

Run:
```bash
readlink ~/.claude/local-marketplace/brandon-skills/skills
```
Expected: `/Users/bstauber/.claude/skills`. If it is NOT a symlink to that path, STOP and report BLOCKED — the single-`mv` assumption is invalid and the plan needs revision.

- [ ] **Step 2: Confirm the repo tree is clean before the move**

Run:
```bash
cd ~/.claude/skills/pov-builder && git status -sb
```
Expected: on `main`, ahead of origin by 1 (the spec commit `1f7dca1` + backlog `fdcebf3`), no uncommitted changes. If there are uncommitted changes, stop and surface them.

- [ ] **Step 3: Rename the directory**

Run:
```bash
mv ~/.claude/skills/pov-builder ~/.claude/skills/tech-strat-pov-forge
```

- [ ] **Step 4: Verify both path views resolve to the renamed dir**

Run:
```bash
ls -d ~/.claude/skills/tech-strat-pov-forge
ls -d ~/.claude/local-marketplace/brandon-skills/skills/tech-strat-pov-forge
cd ~/.claude/skills/tech-strat-pov-forge && git rev-parse --show-toplevel
```
Expected: both `ls` succeed; git toplevel is the new path. The old `~/.claude/skills/pov-builder` no longer exists.

- [ ] **Step 5: No commit yet** (directory rename is not a git-tracked change from inside the repo — git tracks contents, not its own location). Proceed to Task 3.

---

### Task 3: Create the working branch

**Files:** none (git branch only).

**Interfaces:**
- Produces: branch `rename/tech-strat-pov-forge` off `main`, on which Tasks 4-5 commit.

- [ ] **Step 1: Create and switch to the branch**

Run:
```bash
cd ~/.claude/skills/tech-strat-pov-forge && git checkout -b rename/tech-strat-pov-forge && git branch --show-current
```
Expected: `rename/tech-strat-pov-forge`.

---

### Task 4: In-repo content edits (slug, title, config refs, validator, hook, backlog, org62 parity)

**Files:**
- Modify: `SKILL.md` (lines 2, 6, 100)
- Modify: `README.md` (lines 1, 13, 53, 69, 73, 158, 266, 267, 279, 284, 294)
- Modify: `tests/validate_skill.py` (lines 3, 893, 917, 1004)
- Modify: `.githooks/pre-commit` (line 2, comment only)
- Modify: `BACKLOG.md` (line 1 title; line 143 live ref)
- Modify: `refs/org62-prefill.md` line 84 (**and** the pie-poc-forge copy — see Task 4b)

**Interfaces:**
- Consumes: the migrated config name from Task 1.
- Produces: a repo whose live files all say `tech-strat-pov-forge` / `Tech Strat POV Forge`; validator asserts the new config filename.

- [ ] **Step 1: Edit `SKILL.md`**

- Line 2: `name: pov-builder` → `name: tech-strat-pov-forge`
- Line 6: `# POV Builder` → `# Tech Strat POV Forge`
- Line 100: `~/.claude/pov-builder-slack.json` → `~/.claude/tech-strat-pov-forge-slack.json`

- [ ] **Step 2: Edit `README.md`** (all live references)

- Line 1: `# POV Builder` → `# Tech Strat POV Forge`
- Line 13: `` `/pov-builder` `` → `` `/tech-strat-pov-forge` ``
- Line 53: `` `~/.claude/pov-builder-slack.json` `` → `` `~/.claude/tech-strat-pov-forge-slack.json` ``
- Line 69: `pov-builder-slack.json` → `tech-strat-pov-forge-slack.json`
- Line 73: `pov-builder can hydrate` → `Tech Strat POV Forge can hydrate`
- Line 158: repo-tree `pov-builder/` → `tech-strat-pov-forge/`
- Line 266: clone URL `…/salesforce-isv-pov-builder.git` → `…/tech-strat-pov-forge.git`
- Line 267: clone target `~/.claude/skills/pov-builder` → `~/.claude/skills/tech-strat-pov-forge`
- Line 279: `/pov-builder` → `/tech-strat-pov-forge`
- Line 284: `~/.claude/skills/pov-builder` → `~/.claude/skills/tech-strat-pov-forge`
- Line 294: `Read(~/.claude/skills/pov-builder/**)` → `Read(~/.claude/skills/tech-strat-pov-forge/**)`

Use `grep -n "pov-builder\|POV Builder\|salesforce-isv" README.md` after editing to confirm zero live remainders.

- [ ] **Step 3: Edit `tests/validate_skill.py`**

- Line 3 (docstring): `pov-builder skill` → `tech-strat-pov-forge skill`
- Line 893: both the assertion string `"pov-builder-slack.json"` → `"tech-strat-pov-forge-slack.json"` **and** the message `~/.claude/pov-builder-slack.json` → `~/.claude/tech-strat-pov-forge-slack.json`
- Line 917: assertion string `"pov-builder-slack.json"` → `"tech-strat-pov-forge-slack.json"`
- Line 1004: print label `pov-builder skill validation` → `tech-strat-pov-forge skill validation`
- Line 941: the parity-failure MESSAGE mentions "pov-builder" — update the human text to `tech-strat-pov-forge` for clarity, but this does not affect logic. (Do NOT change the `here == there` comparison.)

- [ ] **Step 4: Edit `.githooks/pre-commit`**

- Line 2 comment: `# pov-builder pre-commit hook` → `# tech-strat-pov-forge pre-commit hook` (cosmetic; the hook body is path-relative via `git rev-parse --show-toplevel`, so no functional change).

- [ ] **Step 5: Edit `BACKLOG.md`**

- Line 1: `# pov-builder — Backlog` → `# tech-strat-pov-forge — Backlog`
- Line 143: live ref `wire pov-builder to call it directly` → `wire tech-strat-pov-forge to call it directly`
- Leave all dated historical R-item text untouched (record). Add nothing else.

- [ ] **Step 6 (Task 4b): Edit `refs/org62-prefill.md` line 84 in BOTH copies identically**

In `~/.claude/skills/tech-strat-pov-forge/refs/org62-prefill.md` line 84:
`- **pov-builder:** fold populated fields…` → `- **tech-strat-pov-forge:** fold populated fields…`

Then make the byte-identical edit in the sibling:
`~/.claude/skills/pie-poc-forge/refs/org62-prefill.md` line 84 — same change.

Verify parity:
```bash
diff ~/.claude/skills/tech-strat-pov-forge/refs/org62-prefill.md ~/.claude/skills/pie-poc-forge/refs/org62-prefill.md && echo "parity OK"
```
Expected: `parity OK` (no diff). (The pie-poc-forge edit is committed in Task 7 with the other sibling edits; here we only need the files byte-equal so this repo's validator passes.)

- [ ] **Step 7: Run the validator**

Run:
```bash
cd ~/.claude/skills/tech-strat-pov-forge && python3 tests/validate_skill.py
```
Expected: `77/77 passed`. If the org62-parity check fails, the two copies diverged — re-check Step 6. If a config check fails, confirm Task 1 created the new config and the README/validator strings match.

- [ ] **Step 8: Confirm no live `pov-builder` remains (excluding history)**

Run:
```bash
cd ~/.claude/skills/tech-strat-pov-forge && grep -rn "pov-builder\|POV Builder\|salesforce-isv-pov-builder" \
  --include="*.md" --include="*.py" --include="pre-commit" . \
  | grep -v "docs/specs/" | grep -v "docs/plans/" | grep -v "docs/superpowers/"
```
Expected: no output (all remaining hits are under the excluded history dirs). If a live file shows up, edit it and re-run.

- [ ] **Step 9: Commit**

```bash
cd ~/.claude/skills/tech-strat-pov-forge
git add SKILL.md README.md tests/validate_skill.py .githooks/pre-commit BACKLOG.md refs/org62-prefill.md
git commit -m "rename: pov-builder -> tech-strat-pov-forge (slug/title/config/validator/live refs)"
```
(The pre-commit hook re-runs the validator; expect 77/77.)

---

### Task 5: GitHub repo rename + push

**Files:** none in-repo (remote + git config).

**Interfaces:**
- Consumes: the committed rename from Task 4; the README clone URL already updated.
- Produces: renamed GitHub repo, updated `origin`, pushed branch/commits.

- [ ] **Step 1: Rename the GitHub repo**

Run:
```bash
gh repo rename tech-strat-pov-forge --repo bstaubersalesforce/salesforce-isv-pov-builder --yes
```
Expected: success message with the new repo URL. If `gh` reports the name is taken or auth fails, STOP and report — do not force anything.

- [ ] **Step 2: Update the local remote URL**

Run:
```bash
cd ~/.claude/skills/tech-strat-pov-forge
git remote set-url origin https://github.com/bstaubersalesforce/tech-strat-pov-forge.git
git remote -v
```
Expected: `origin` fetch/push both show `tech-strat-pov-forge.git`.

- [ ] **Step 3: Push main + the rename branch**

Decision: merge the branch to `main` locally first (this is a mechanical rename, already validator-gated), then push `main`.
```bash
cd ~/.claude/skills/tech-strat-pov-forge
git checkout main
git merge --no-ff rename/tech-strat-pov-forge -m "Merge rename/tech-strat-pov-forge: rename to Tech Strat POV Forge"
python3 tests/validate_skill.py            # expect 77/77 on merged main
git push origin main
git branch -d rename/tech-strat-pov-forge
```
Expected: validator 77/77; push succeeds to the renamed remote; branch deleted.

- [ ] **Step 4: Verify the remote**

Run:
```bash
gh repo view bstaubersalesforce/tech-strat-pov-forge --json name,url -q '.name + " " + .url'
git -C ~/.claude/skills/tech-strat-pov-forge status -sb | head -1
```
Expected: repo name `tech-strat-pov-forge`; local `main` in sync with `origin/main`.

---

### Task 6: Sibling skills, workspace CLAUDE.md, style-conventions

**Files:**
- Modify: `~/.claude/skills/pie-poc-forge/README.md:112`, `~/.claude/skills/pie-poc-forge/refs/org62-prefill.md:84` (already edited in Task 4b — commit here), `~/.claude/skills/pie-poc-forge/BACKLOG.md:128,137`
- Modify: `~/.claude/skills/ps-npi-forge/BACKLOG.md:11`
- Modify: `~/.claude/skills/workshop-forge/README.md:4,16,20`
- Modify: `~/claude-projects/CLAUDE.md:25`
- Modify: `~/.claude/style-conventions.md:68`

**Interfaces:**
- Consumes: the new canonical names.
- Produces: siblings + workspace referencing `tech-strat-pov-forge`; each sibling repo committed separately.

**Editorial rule:** where the reference is the human title or a family label, use `Tech Strat POV Forge`; where it is the slug/dir/command, use `tech-strat-pov-forge`. For BACKLOG *dated closed items* that name pov-builder as historical context (pie-poc-forge BACKLOG:128,137 "Closed 2026-06-11"), treat as history → leave as-is. Only update forward-looking/live references. (This means pie-poc-forge BACKLOG lines 128/137 are LEFT unchanged; the pie-poc README:112 family reference IS updated.)

- [ ] **Step 1: pie-poc-forge**

- `README.md:112`: `Modeled on \`pov-builder\`;` → `Modeled on \`tech-strat-pov-forge\`;`
- `refs/org62-prefill.md:84`: already changed in Task 4b (verify still byte-equal to this repo's copy).
- `BACKLOG.md:128,137`: LEAVE (dated closed-item history).

Commit:
```bash
cd ~/.claude/skills/pie-poc-forge
git add README.md refs/org62-prefill.md
git commit -m "docs: rename pov-builder -> tech-strat-pov-forge in live refs + org62 parity"
python3 tests/validate_skill.py    # expect green; org62 parity now matches renamed sibling
```
Note: pie-poc-forge's own validator has the mirror parity check pointing at `../pov-builder`. After THIS skill's directory rename (Task 2), that path is stale. **Check pie-poc-forge's validator** for a hardcoded `pov-builder` sibling path:
```bash
grep -n "pov-builder" ~/.claude/skills/pie-poc-forge/tests/validate_skill.py
```
If found, update the sibling path to `tech-strat-pov-forge` in the same commit, else pie-poc-forge's parity check breaks. (If the check resolves the sibling by a name-agnostic means, no change needed — verify.)

- [ ] **Step 2: ps-npi-forge**

- `BACKLOG.md:11`: `the dark pov-builder treatment` → `the dark tech-strat-pov-forge treatment` (live descriptive ref).

Commit:
```bash
cd ~/.claude/skills/ps-npi-forge
git add BACKLOG.md
git commit -m "docs: rename pov-builder -> tech-strat-pov-forge reference"
python3 tests/validate_skill.py    # expect green (docs-only)
```

- [ ] **Step 3: workshop-forge**

- `README.md:4`: `(\`pov-builder\` → \`pie-poc-forge\`…` → `(\`tech-strat-pov-forge\` → \`pie-poc-forge\`…`
- `README.md:16`: `\`pov-builder\` POV` → `\`tech-strat-pov-forge\` POV`
- `README.md:20`: `a strategy POV (\`pov-builder\`)` → `a strategy POV (\`tech-strat-pov-forge\`)`

Commit:
```bash
cd ~/.claude/skills/workshop-forge
git add README.md
git commit -m "docs: rename pov-builder -> tech-strat-pov-forge in family refs"
python3 tests/validate_skill.py    # expect green (docs-only)
```

- [ ] **Step 4: workspace CLAUDE.md** (not a git repo path we manage per-commit here; edit in place)

`~/claude-projects/CLAUDE.md:25`: update the two `pov-builder` mentions →`tech-strat-pov-forge` and the parity-note sentence ("edit pov-builder's copy, then re-copy to pie-poc-forge") → "edit tech-strat-pov-forge's copy…".

- [ ] **Step 5: style-conventions.md**

`~/.claude/style-conventions.md:68`: `\`pov-builder\` and \`pie-poc-forge\`` → `\`tech-strat-pov-forge\` and \`pie-poc-forge\``.
(Also scan the rest of that file: `grep -n "pov-builder\|POV Builder" ~/.claude/style-conventions.md` and update any other live hit, e.g. the pov-builder/pie-poc-forge `refs/mermaid-diagrams.md` sync sentence if present.)

- [ ] **Step 6: settings.json** (if Task 1 Step 4 found references, or line 294's README allow-list has a settings analog)

Run:
```bash
grep -n "pov-builder" ~/.claude/settings.json ~/.claude/settings.local.json 2>/dev/null || echo "no settings references"
```
If any live path like `Read(~/.claude/skills/pov-builder/**)` exists, update it to `tech-strat-pov-forge`. Expected common case: none (the README documents allow-lists but settings may use the marketplace path). Record the outcome.

---

### Task 7: Memory rename + backlinks

**Files:**
- Move: `memory/pov-builder-skill.md` → `memory/tech-strat-pov-forge-skill.md`
- Modify: `memory/MEMORY.md` (index line)
- Modify: backlinks in `memory/{ncino-pov,particle-health-pov,ps-npi-forge,bwell-pov,style-conventions,workshop-forge-skill,skills-plugin-packaging,org62-engagement-prefill,skill-forge,pie-poc-forge,slack-mcp,ncino-treasury-pov}.md`

Memory dir: `/Users/bstauber/.claude/projects/-Users-bstauber-claude-projects/memory/`. Not a git repo — plain `mv` + edits.

**Interfaces:**
- Produces: the memory file renamed; all `[[pov-builder-skill]]` backlinks resolve to `[[tech-strat-pov-forge-skill]]`; the index updated.

- [ ] **Step 1: Rename the memory file**

```bash
cd /Users/bstauber/.claude/projects/-Users-bstauber-claude-projects/memory
mv pov-builder-skill.md tech-strat-pov-forge-skill.md
```

- [ ] **Step 2: Update the renamed file's frontmatter + add a head-note**

In `tech-strat-pov-forge-skill.md`:
- Frontmatter `name: pov-builder-skill` → `name: tech-strat-pov-forge-skill`.
- Update the `description:` to name the new title.
- Add a single line at the very top of the body (before the first dated state block):
  `**Renamed 2026-07-16:** skill renamed \`pov-builder\` → **Tech Strat POV Forge** (slug \`tech-strat-pov-forge\`, repo \`bstaubersalesforce/tech-strat-pov-forge\`, config \`tech-strat-pov-forge-slack.json\`). Dated blocks below predate the rename and are preserved as record.`
- Update the first sentence (the live "lives at" line) to the new path/repo. Leave dated blocks intact.

- [ ] **Step 3: Update `MEMORY.md` index line**

Change the POV Builder index entry link target `pov-builder-skill.md` → `tech-strat-pov-forge-skill.md` and the label/hook to "Tech Strat POV Forge".

- [ ] **Step 4: Fix backlinks in sibling memory files**

For each file that contains `[[pov-builder-skill]]`, replace with `[[tech-strat-pov-forge-skill]]`:
```bash
cd /Users/bstauber/.claude/projects/-Users-bstauber-claude-projects/memory
grep -rl "\[\[pov-builder-skill\]\]" . | while read -r f; do
  # inspect each; apply the replacement
  echo "backlink in: $f"
done
```
Then edit each (or, if confident, `sed -i '' 's/\[\[pov-builder-skill\]\]/[[tech-strat-pov-forge-skill]]/g' <file>` per file). Also update prose mentions of "pov-builder" that are LIVE (not dated-historical) in those memory files where they refer to the skill by its current identity — use judgment per the live-files-only policy; dated observations stay.

- [ ] **Step 5: Verify no dangling backlink**

```bash
cd /Users/bstauber/.claude/projects/-Users-bstauber-claude-projects/memory
grep -rn "\[\[pov-builder-skill\]\]" . || echo "no dangling backlinks"
grep -rn "pov-builder-skill.md" . || echo "no stale index/link targets"
```
Expected: both print the "no …" line.

---

### Task 8: Whole-rename verification

**Files:** none (verification only).

- [ ] **Step 1: Renamed repo validator green**

```bash
cd ~/.claude/skills/tech-strat-pov-forge && python3 tests/validate_skill.py | tail -1
```
Expected: `77/77 passed`.

- [ ] **Step 2: Slug resolves; directory matches**

```bash
head -2 ~/.claude/skills/tech-strat-pov-forge/SKILL.md   # name: tech-strat-pov-forge
```

- [ ] **Step 3: Live grep sweep across all touched locations**

```bash
echo "--- skill repo (live only) ---"
grep -rn "pov-builder\|POV Builder\|salesforce-isv-pov-builder" ~/.claude/skills/tech-strat-pov-forge \
  --include="*.md" --include="*.py" --include="pre-commit" \
  | grep -vE "docs/(specs|plans|superpowers)/" || echo "clean"
echo "--- siblings (README+BACKLOG live) ---"
grep -rn "pov-builder\|POV Builder" ~/.claude/skills/pie-poc-forge/README.md ~/.claude/skills/ps-npi-forge/BACKLOG.md ~/.claude/skills/workshop-forge/README.md | grep -vi "closed 2026" || echo "clean"
echo "--- workspace + style ---"
grep -n "pov-builder\|POV Builder" ~/claude-projects/CLAUDE.md ~/.claude/style-conventions.md || echo "clean"
echo "--- config ---"
ls ~/.claude/tech-strat-pov-forge-slack.json && (ls ~/.claude/pov-builder-slack.json 2>&1 || echo "old config gone")
```
Expected: each section prints `clean`/the-expected-artifact; only dated-history hits remain (which the excludes drop). Note any residual and judge whether it's history (leave) or a miss (fix + re-run).

- [ ] **Step 4: Sibling validators still green**

```bash
for s in pie-poc-forge ps-npi-forge workshop-forge; do
  echo "== $s =="; (cd ~/.claude/skills/$s && python3 tests/validate_skill.py | tail -1)
done
```
Expected: each `passed` (counts as-is per skill).

- [ ] **Step 5: GitHub remote confirmed**

```bash
gh repo view bstaubersalesforce/tech-strat-pov-forge --json name -q .name
git -C ~/.claude/skills/tech-strat-pov-forge status -sb | head -1
```
Expected: `tech-strat-pov-forge`; `main` in sync with `origin/main`.

- [ ] **Step 6: Report the final state** — renamed layers, validator counts, any residual history hits deliberately left, and the config/GitHub confirmations.

---

## Notes for the executor

- **Order matters:** Task 1 (config) → Task 2 (dir) → Task 3 (branch) → Task 4 (content, incl. org62 parity in BOTH copies) → Task 5 (GitHub + push) → Task 6 (siblings/workspace) → Task 7 (memory) → Task 8 (verify). Task 4's validator gate depends on Task 1's config file existing under the new name.
- **org62 parity is the sharp edge:** edit line 84 in both `tech-strat-pov-forge` and `pie-poc-forge` copies identically, or the validator's byte-compare fails. Commit the pie-poc side in Task 6 Step 1, but make the files equal during Task 4b.
- **Check pie-poc-forge's OWN validator** for a hardcoded `../pov-builder` sibling path (Task 6 Step 1) — the directory rename may have broken its mirror parity check.
- **History is sacred:** never edit dated `docs/specs/*`, `docs/plans/*`, or dated memory blocks. The grep sweeps exclude them; if one shows up, that's expected — leave it.
- No behavioral change to the skill. If any validator count moves off 77, something structural was altered by accident — stop and diagnose, don't adjust the expected number.
