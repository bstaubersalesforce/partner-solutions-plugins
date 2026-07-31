#!/usr/bin/env bash
# pull_cases — fetch Org62 case records + comment threads to a .notes/ file (raw sensitive capture).
# Enforces the practice in refs/investigate-snippets.md: read the COMMENTS, not just the record.
#
# Usage:
#   scripts/pull_cases.sh --org org62 --out .notes/cases.md 66996591 66716628 500ed00000tXs6oAAC ...
# Accepts CaseNumbers and/or record IDs (500…). Output goes UNDER .notes/ only (gitignored).
#
# Notes baked in from practice:
#  - Do NOT select Product_Area__c (doesn't exist on Case).
#  - Query record IDs by Id, everything else by CaseNumber.
#  - Output is RAW SENSITIVE CAPTURE — .notes/ only; run scrub_check.py before any doc is shared.
set -uo pipefail
ORG="org62"; OUT=".notes/cases.md"; IDS=()
while [ $# -gt 0 ]; do case "$1" in
  --org) ORG="$2"; shift 2;;
  --out) OUT="$2"; shift 2;;
  *) IDS+=("$1"); shift;;
esac; done
[ ${#IDS[@]} -eq 0 ] && { echo "usage: pull_cases.sh [--org A] [--out .notes/f.md] <caseNo|recordId> ..." >&2; exit 2; }
case "$OUT" in .notes/*) ;; *) echo "refusing: --out must be under .notes/ (raw sensitive capture)" >&2; exit 2;; esac
command -v sf >/dev/null 2>&1 || { echo "sf CLI not found" >&2; exit 1; }
mkdir -p "$(dirname "$OUT")"

# split into record IDs (500…/15-18 char) vs case numbers
byid=(); bynum=()
for x in "${IDS[@]}"; do
  if printf '%s' "$x" | grep -qE '^500[A-Za-z0-9]{12,15}$'; then byid+=("$x"); else bynum+=("$x"); fi
done
q_in(){ local IFS=,; printf "'%s'" "${*}" | sed "s/,/','/g"; }

: > "$OUT"
echo "# RAW case capture ($ORG) — $(printf '%s ' "${IDS[@]}")" >> "$OUT"
echo "> gitignored (.notes/). Read the comment tails. Scrub before sharing (scripts/scrub_check.py)." >> "$OUT"

# fetch to a temp file (heredoc python reads the FILE via argv[2], never stdin — piping data
# into a `python3 - <<HEREDOC` swallows the data because the heredoc IS stdin).
TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
fetch_to_tmp(){ # $1 = SOQL where-clause
  sf data query -o "$ORG" --json -q "SELECT CaseNumber, Subject, Status, IsClosed, CreatedDate, ClosedDate, Account.Name, Description FROM Case WHERE $1" 2>/dev/null > "$TMP"
}
append_cases(){ python3 - "$OUT" "$TMP" <<'PY'
import json,sys
out,src=sys.argv[1],sys.argv[2]
try: d=json.load(open(src,encoding="utf-8"))
except Exception as e: sys.stderr.write(f"append_cases: bad JSON ({e})\n"); sys.exit(0)
with open(out,"a",encoding="utf-8") as f:
    for r in d.get("result",{}).get("records",[]):
        acct=(r.get("Account") or {}).get("Name") if r.get("Account") else None
        f.write(f"\n## Case {r.get('CaseNumber')} — {r.get('Status')} (closed={r.get('IsClosed')})\n")
        f.write(f"- Account: {acct}\n- Subject: {r.get('Subject')}\n")
        f.write(f"- Created: {(r.get('CreatedDate') or '')[:10]}  Closed: {(r.get('ClosedDate') or '')[:10]}\n")
        desc=(r.get("Description") or "").strip().replace("\n"," ")
        f.write(f"- Description: {desc[:600]}\n")
PY
}
[ ${#bynum[@]} -gt 0 ] && { fetch_to_tmp "CaseNumber IN ($(q_in "${bynum[@]}"))"; append_cases; }
[ ${#byid[@]}  -gt 0 ] && { fetch_to_tmp "Id IN ($(q_in "${byid[@]}"))";        append_cases; }

# comment threads (the load-bearing part) — by CaseNumber (resolve record IDs to numbers first)
echo "" >> "$OUT"; echo "# Comment threads (resolution tails)" >> "$OUT"
allnums=("${bynum[@]}")
if [ ${#byid[@]} -gt 0 ]; then
  more=$(sf data query -o "$ORG" --json -q "SELECT CaseNumber FROM Case WHERE Id IN ($(q_in "${byid[@]}"))" 2>/dev/null \
        | python3 -c "import json,sys;print('\n'.join(r['CaseNumber'] for r in json.load(sys.stdin).get('result',{}).get('records',[])))")
  while IFS= read -r n; do [ -n "$n" ] && allnums+=("$n"); done <<< "$more"
fi
if [ ${#allnums[@]} -gt 0 ]; then
  sf data query -o "$ORG" --json -q "SELECT Parent.CaseNumber, CreatedDate, CommentBody FROM CaseComment WHERE Parent.CaseNumber IN ($(q_in "${allnums[@]}")) ORDER BY Parent.CaseNumber, CreatedDate" 2>/dev/null > "$TMP"
  python3 - "$OUT" "$TMP" <<'PY'
import json,sys
out,src=sys.argv[1],sys.argv[2]
try: d=json.load(open(src,encoding="utf-8"))
except Exception as e: sys.stderr.write(f"comments: bad JSON ({e})\n"); sys.exit(0)
from collections import defaultdict
g=defaultdict(list)
for r in d.get("result",{}).get("records",[]):
    g[(r.get("Parent") or {}).get("CaseNumber")].append(r)
with open(out,"a",encoding="utf-8") as f:
    for cn,rows in g.items():
        f.write(f"\n## {cn} — {len(rows)} comments (tail):\n")
        for r in rows[-5:]:
            b=(r.get("CommentBody") or "").replace("\n"," ").strip()
            f.write(f"- [{(r.get('CreatedDate') or '')[:10]}] {b[:400]}\n")
PY
fi
echo "wrote $OUT (raw — scrub before sharing)"
