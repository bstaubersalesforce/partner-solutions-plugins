#!/usr/bin/env bash
# Validation harness for the rich_schema_kit workshop kit (bash-only, no external deps).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
. "$ROOT/scripts/lib/common.sh"
FAILED=0
req() { [ -f "$ROOT/$1" ] && pass "file: $1" || { fail "missing: $1"; FAILED=1; }; }

echo "== required files =="
for f in README.md GUIDE.md FACILITATOR.md LESSONS-LEARNED.md KNOWN-GAPS.md .env.example .gitignore docs/framework.md docs/buildability-matrix.md scripts/lib/common.sh scripts/00-preflight.sh config/kit.json data/README.md; do
  if [[ "$f" == scripts/* ]]; then
    # Scripts: validate bash syntax
    if [ -f "$ROOT/$f" ]; then
      bash -n "$ROOT/$f" 2>/dev/null && pass "script ok: $f" || { fail "bash syntax error: $f"; FAILED=1; }
    else
      fail "missing script: $f"; FAILED=1
    fi
  else
    # Non-scripts: just check existence
    req "$f"
  fi
done

echo "== content dirs =="
[ -d "$ROOT/slides" ] && pass "content dir: slides/" || { fail "missing content dir: slides/"; FAILED=1; }

# internal markdown link resolution (relative links only)
echo "== links =="
while IFS= read -r f; do
  # extract (target) from ](target) where target is a relative path (no http, no #-only)
  grep -oE '\]\(([^)#]+)' "$f" 2>/dev/null | sed 's/](//' | while IFS= read -r tgt; do
    case "$tgt" in
      http*|mailto:*|"") continue;;
    esac
    # resolve relative to the file's dir
    d="$(cd "$(dirname "$f")" && pwd)"
    [ -e "$d/$tgt" ] || [ -e "$ROOT/$tgt" ] || echo "BROKEN_LINK $f -> $tgt"
  done
done < <(find "$ROOT" -name '*.md' -not -path '*/.notes/*' -not -path '*/.git/*' -not -path '*/node_modules/*') > /tmp/rich_schema_kit_links.txt 2>/dev/null
if [ -s /tmp/rich_schema_kit_links.txt ]; then cat /tmp/rich_schema_kit_links.txt; fail "broken internal links"; FAILED=1; else pass "internal links resolve"; fi

[ $FAILED -eq 0 ] && echo "check.sh: ALL GREEN" || echo "check.sh: FAILURES ABOVE"
exit $FAILED
