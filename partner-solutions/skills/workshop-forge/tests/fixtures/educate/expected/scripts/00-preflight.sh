#!/usr/bin/env bash
# Preflight: verify tooling before the workshop build.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
. "$ROOT/scripts/lib/common.sh"
# No org needed for this educate-only kit
FAILED=0
# Educate-only: no tooling checks needed
pass "educate-only kit (no org required)"

exit $FAILED
