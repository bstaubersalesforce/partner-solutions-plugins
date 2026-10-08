# Stage 3 — Blocker scan

Ground the plan in the partner's **real** support history, then diagnose the high-signal cases
adversarially (claimed vs. real).

## Case scan first
Run the built-in Org62 case scan per `../org62-case-scan.md`: scope to the partner Account,
pull the 18-month grouped volume/open counts, and list recent high-signal candidates. Report
the shape (total Platform/App vs. Partner-Program, # open) so routine volume is separated from
real issues.

## Deep-dive via partner-blocker-forge
Pick 3–5 candidates that look like genuine technical debt or enforcement patterns (packaging
limits, Security Review bounces, MFA/enforcement lockouts, upgrade failures) and hand each to
`partner-blocker-forge` as a subagent for the claimed-vs-real diagnosis + root-cause read.

## Data-safety gate (mandatory)
Case comment threads often carry live credentials / internal URLs / cross-customer PII. Raw
captures and credential-bearing threads go to gitignored **`.notes/`** only; the plan cites
cases by **number + one-line root cause**. See the gate in `../org62-case-scan.md`.

## Hand-off
Each confirmed REAL blocker becomes an **Obstacle** and a gap-closure row (Stage 7). Do not
inflate the count or accept the partner's crisis framing as fact.
