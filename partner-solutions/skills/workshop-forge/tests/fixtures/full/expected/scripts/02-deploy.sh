#!/usr/bin/env bash
# Deploy the reference-build metadata to the assigned org.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
. "$ROOT/scripts/lib/common.sh"
ORG="$(resolve_org "$@")"
[ -n "$ORG" ] || { fail "no org (pass --org <alias> or set ORG_ALIAS)"; exit 1; }
[ -d "$ROOT/sfdx/" ] || { fail "sfdx/ not found"; exit 1; }
( cd "$ROOT/sfdx" && sf project deploy start --source-dir force-app --target-org "$ORG" )
