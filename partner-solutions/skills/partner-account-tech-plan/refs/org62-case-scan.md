# Built-in Org62 case scan

Grounds the Blocker Assessment (Stage 3) in the partner's **real** support history before any
narrative. Reuses `partner-blocker-forge`'s investigate-snippets. Read-only against Org62
(production) — scrub before any external use.

## Scope

Scope to the partner's Org62 Account. Two record-type families carry the technical signal:
- **Platform / Application Support** — product/packaging/platform cases.
- **Partner Program Support** — program, enablement, Security Review, enforcement cases.

## Queries

Resolve the alias from `ORG62_ALIAS` (default `org62`). Use `--json`; CSV drops GROUP BY
aggregates.

**Volume + open count (18-month window), grouped:**
```bash
sf data query --target-org "$ORG62_ALIAS" --json -q \
"SELECT RecordType.Name, Status, COUNT(Id) ct FROM Case \
 WHERE AccountId = '<ACCOUNT_ID>' AND CreatedDate = LAST_N_DAYS:540 \
 AND RecordType.Name IN ('Platform / Application Support','Partner Program Support') \
 GROUP BY RecordType.Name, Status"
```

**Candidate cases to deep-dive (recent, high-signal):**
```bash
sf data query --target-org "$ORG62_ALIAS" --json -q \
"SELECT CaseNumber, Subject, Status, Priority, CreatedDate FROM Case \
 WHERE AccountId = '<ACCOUNT_ID>' \
 AND RecordType.Name IN ('Platform / Application Support','Partner Program Support') \
 ORDER BY CreatedDate DESC LIMIT 50"
```

## Deep-dive routing

From the candidate list, pick 3–5 that look like **real technical debt or enforcement
patterns** (packaging limits, Security Review bounces, MFA/enforcement lockouts, upgrade
failures) — not routine how-to tickets. For each, hand the case number to
`partner-blocker-forge` as a subagent for the claimed-vs-real diagnosis and root-cause read of
the comment thread. Separate REAL issues from routine volume in the plan.

## Data-safety gate (mandatory)

Case comment threads frequently contain **live credentials, internal URLs, and cross-customer
PII**. Before anything is written to a shareable location:
- Raw case captures + any credential-bearing threads → gitignored **`.notes/`** only
  (`.notes/<partner>-cases.md`, `.notes/<partner>-case-comments.json`). **Never** paste a
  credential into the plan, a canvas, a commit, or a chat message.
- The plan cites cases by **number + one-line root cause**, never by raw thread content.
- Partner-facing versions are scrubbed of all internal identifiers first.

This gate is inherited from `partner-blocker-forge`'s scrub discipline — do not relax it.
