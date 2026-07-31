# partner-blocker-forge

Turns a partner technical blocker (packaging, platform, connectivity, Agentforce / Data Cloud) into an
**adversarial, evidence-based diagnosis** and a **structured deliverable** — separating what the partner *claims*
from what is *real*, verified against their actual support cases and primary Salesforce documentation.

The premise: a partner's account of a blocker is a set of *claims*, not facts. Claims are often overstated
("packaging is too gappy to use"), miscategorized (a config error read as a product defect), or padded (a
question and three permission tickets counted as "numerous blockers"). This skill interrogates each claim,
classifies what's actually going on, and names the *underlying* issue — which is frequently not the one the
partner named (a capability complaint is often really a confidence problem).

It generalizes a family of real case deep-dives across different domains: 1GP→2GP managed-package migration,
Agentforce / Data Kit packaging, and Data Cloud private-connectivity troubleshooting.

## Inputs
The ask, the partner name, **≥1 support case** (number or record ID), and a **Slack thread**. Missing pieces are
flagged, not blocking — the skill proceeds with what's available and marks the gaps.

## How it works — one path, two depths

1. **Intake + access preflight** — parse the inputs; check org / Slack / web access. If a source is unreachable,
   the run enters **degraded mode**: unverifiable claims are tagged `UNVERIFIED`, and the partner-facing doc is
   blocked until the core sources are covered. Fail loud, not silent.
2. **Triage (always runs)** — pull the case(s), quick-verify each claim, classify, and **always write a short
   internal doc** — visibly stamped *provisional* (single-source, capped at Medium confidence). Ends with a
   recommend-and-ask escalation gate.
3. **Deep-dive (on approval)** — full verification across **four source classes** (primary docs, Known Issues +
   precedent, case **comment threads read in full**, release notes), a per-case root-cause read, and the
   recommended path — **expanding the same doc in place**, reclassifying (not just appending) where the fuller
   evidence overturns a triage call.

### The adversarial method (mandatory every run)
Each claim is classified as one of: **confirmed product bug · config/permission · knowledge-gap/overstated ·
question (not an issue) · accurate + by-design (workaround exists) · accurate + hard constraint (no path) ·
roadmap/unreleased (unverifiable)**. The skill then names the underlying issue — **capability / operational /
confidence** — and produces a required *"Is there a real issue to resolve?"* verdict. Every claim is confidence-
tagged; anything unconfirmable from primary sources is flagged as a PM/support open item, never asserted.

## What it produces
- **Always:** an internal, evidence-based `.md` — TL;DR (with verification depth) → claims verified → the cases
  (what they actually say) → recommended path *or an honest "no supported path today"* → phased action plan →
  risks & open items → routing → dated, confidence-tagged sources.
- **On request:** a scrubbed, partner-facing version (internal routing, case-comment specifics, and cross-customer
  references removed).

The templates deliberately include a **"no supported path"** branch so a genuinely bad answer is stated plainly
rather than dressed up as optimism.

## Bundled scripts
- **`scripts/pull_cases.sh`** — pulls case records **and comment tails** from a support org (Org62) to a
  gitignored `.notes/` file. Reads the comments, not just the record; resolves record IDs → case numbers.
- **`scripts/scrub_check.py`** — mechanical pre-share leak detector (org/case IDs, `gus`/`splunk`/internal URLs,
  internal Slack-archive links, phone numbers, GUS work-items). This is the *enforcement* behind the data-safety
  gate — not just a checklist. Deterministic and covered by a mutation-verified behavioral test.

## Data safety
Raw case comments and Slack threads carry cross-customer data. The skill keeps all raw capture in a gitignored
`.notes/`, writes the internal draft there first, and runs `scrub_check.py` before anything is shared or
committed. The partner-facing doc gets an additional scrub pass.

## Dogfood-tested
Validated end-to-end against **real partner support cases in Org62** across two domains (a package-migration
blocker and an Agentforce packaging engagement) — closed cases and a live Sev1 alike. The real run exercised the
bundled scripts against actual case data (records + full comment threads), confirmed record-ID→case-number
resolution, and confirmed the scrub gate blocks a raw capture from being shared. (Partner-specific captures stay
in gitignored `.notes/` and are never committed.)

## Invoke
`/partner-blocker-forge`

## Tier
Built as a Tier 3 skill (routing + two output artifacts) via the skill-forge tier model; authored and audited
through skill-forge (built==complexity, no tier-gap), and hardened against its own adversarial self-review.

## Roadmap
Open improvements are tracked in [BACKLOG.md](BACKLOG.md).

## Validating
```bash
python3 tests/validate_skill.py
```
14 checks (structural + a behavioral scrub-check test). A pre-commit hook runs this automatically; activate it
once with `git config core.hooksPath .githooks`.
