#!/usr/bin/env bash
# Re-vendor the 5 forge skills from their canonical repos in ~/.claude/skills into
# this marketplace monorepo. The standalone repos remain where you DEVELOP; this
# monorepo is the travelable distribution artifact the PS team installs.
#
# Uses `git archive HEAD` per skill → only the committed, tracked tree (honors each
# skill's .gitignore, so .git/.notes/.superpowers never come along; docs/superpowers
# specs ARE tracked and kept). Run after committing changes in any source skill.
#
# Usage: scripts/sync-skills.sh            (re-vendor all)
#        SKILLS_SRC=/path scripts/sync-skills.sh   (override source root)
set -euo pipefail

SRC="${SKILLS_SRC:-$HOME/.claude/skills}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$HERE/partner-solutions/skills"
SKILLS=(tech-strat-pov-forge pie-poc-forge ps-npi-forge workshop-forge partner-blocker-forge)

for s in "${SKILLS[@]}"; do
  [ -d "$SRC/$s/.git" ] || { echo "ERROR: $SRC/$s is not a git repo"; exit 1; }
  rm -rf "${DEST:?}/$s"
  mkdir -p "$DEST/$s"
  git -C "$SRC/$s" archive HEAD | tar -x -C "$DEST/$s"
  rev="$(git -C "$SRC/$s" rev-parse --short HEAD)"
  echo "vendored $s @ $rev"
done

# Guard: no dev-only dirs should ever land in the vendored tree.
if find "$DEST" -maxdepth 2 \( -name .git -o -name .notes -o -name .superpowers \) | grep -q .; then
  echo "ERROR: dev-only dir leaked into vendored tree"; exit 1
fi
echo "sync complete → $DEST"
