#!/usr/bin/env bash
# Preflight: verify tooling + org connectivity before the workshop build.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
. "$ROOT/scripts/lib/common.sh"
ORG="$(resolve_org "$@")"
FAILED=0
command -v sf >/dev/null 2>&1 && pass "sf CLI present" || { fail "sf CLI not found — https://developer.salesforce.com/tools/salesforcecli"; FAILED=1; }
[ -n "$ORG" ] || { fail "no org (pass --org <alias> or set ORG_ALIAS in .env)"; FAILED=1; }
if [ -n "$ORG" ]; then
  sf org display --target-org "$ORG" >/dev/null 2>&1 && pass "org connectivity: $ORG" || { fail "cannot connect to org $ORG"; FAILED=1; }
fi
exit $FAILED
