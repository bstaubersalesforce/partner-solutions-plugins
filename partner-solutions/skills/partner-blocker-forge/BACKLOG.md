# partner-blocker-forge — Backlog

Ideas and improvements not yet actioned, kept here so they stay visible. Each item records where it came from,
why it matters, and what "done" looks like. This is a working list, not a commitment — items graduate to a
spec → plan → implementation cycle (see `docs/superpowers/`) when picked up.

## How to add an item

```
- **<short-id> — <title>.** Origin: <where it came from>. Why: <why it matters>.
  Done when: <observable definition of done>.
```

---

## Done

- **B1 — case-pull helper.** ✅ shipped `scripts/pull_cases.sh` (records + comment tails → .notes/).
- **B4 — scrub-check linter.** ✅ shipped `scripts/scrub_check.py` + golden-fixture behavioral test (R-TEST-04 now real, mutation-verified).

- **B3 — capability/operational/confidence decision aid.** ✅ added Step 2.5 table + tell in refs/adversarial.md.
- **B5 — access preflight + graceful degradation.** ✅ added preflight + degraded-mode to refs/intake.md.
- **B6 — living / multi-session engagement mode.** ✅ Origin: Bullhorn dogfood (8+ sessions, claims A1→A12, one triage doc + a live Slack canvas). Shipped `refs/living-engagement.md` (stable claim IDs, new-evidence routing, doc↔canvas sync, session hygiene, scope check) + wired into SKILL.md.
- **B7 — resolve-a-partner-cited-number recipe.** ✅ Origin: Bullhorn dogfood (repeated `473…` legacy numbers + a `0D5…` FeedItem VoC needed manual resolution). Shipped the resolution ladder + prefix cheat-sheet in refs/investigate-snippets.md.
- **B8 — name the recurring cross-claim pattern.** ✅ Origin: Bullhorn dogfood (A11/A12 = "mandatory platform change breaks a long-working setup," 3 instances — stronger than any single claim). Shipped Step 2.7 in refs/adversarial.md + a verdict-block line.

## Open

- **B2 — Precedent-resolution search as a first-class step.** Origin: a migration-blocker dogfood (leaned on a
  Jidoka/Compliatric precedent case); **RE-VALIDATED by the Bullhorn dogfood 2026-07-31** — the Maxval-identical
  1GP-email case + nCino/Revenova throughlines were the fastest "this is a known shape" route (second vote → raise
  priority). Why: a prior partner who cleared the same blocker is often the fastest route to fix + routing;
  currently folded into the Known-Issues step. Done when: `refs/deep-dive.md` has an explicit "search for a
  precedent resolution" step with a query pattern, and it's exercised in a dogfood.


