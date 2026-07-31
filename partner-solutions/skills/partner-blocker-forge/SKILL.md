---
name: partner-blocker-forge
description: Use when a partner reports a technical blocker (packaging, platform, connectivity, Agentforce/Data Cloud) and you need to verify what is REAL vs. CLAIMED against their actual support cases and primary Salesforce docs, then produce an evidence-based diagnosis and deliverable. Triage fast, escalate to a full deep-dive on approval. Generalizes real partner case deep-dives (package migration, Agentforce packaging, Data Cloud connectivity).
---

# partner-blocker-forge

Turns a partner technical blocker into an **adversarial, evidence-based diagnosis** and a **structured
deliverable** — separating what the partner *claims* from what is *real*, verified against their actual support
cases and primary documentation. Two depths on one continuous path: a fast **triage** that always writes a short
internal doc, escalating (on your approval) into a full **deep-dive** that expands the same doc in place.

## Refusal conditions

Stop and clarify, or decline, when:
- There is **no partner blocker to diagnose** — this is not a general support-ticket manager, a case-monitoring
  tool, or a packaging *builder* (it diagnoses and routes; it does not build packages).
- **No case and no Slack thread and no ask** are provided — there is nothing to investigate; ask for at least the
  ask + partner + one case or thread.
- You **cannot confirm a load-bearing fact** from primary sources — do **not** assert it; flag it as an open item
  for PM/support.
- Do **not** share any output before running the data-safety gate (`refs/scrub.md`), and do **not** produce a
  partner-facing doc without scrubbing first.
- Do **not** inflate the blocker count or accept the partner's crisis framing as fact.

## Inputs

The ask (what's needed), the **partner name**, **≥1 support case** (number or record ID), and a **Slack thread**.
Missing pieces are flagged, not blocking — see `refs/intake.md`.

## How it works

A continuous path, two depths. Escalation is **recommend-and-ask**, never automatic.

1. **Intake** — parse ask / partner / case(s) / Slack thread; gap-check; extract the distinct claims.
   → `refs/intake.md`
2. **Triage (always)** — pull the case(s) light, quick-verify each claim, classify, state the likely fix, and
   **always write a short internal doc**. End with the escalation recommendation + ask.
   → `refs/triage.md`
3. **Deep-dive (on approval)** — full verification across the four source classes, per-case root-cause read,
   recommended path, action plan, routing — **expanding the same doc in place**.
   → `refs/deep-dive.md`
4. **Partner-facing doc (on request)** — scrubbed shareable version from `templates/partner-doc.md`.

### Mandatory on every run
- **Adversarial "claimed vs. real"** classification + framing challenges + the required "is there a real issue?"
  verdict. → `refs/adversarial.md`
- **Four source classes** for verification: primary docs, Known Issues, case resolutions + comment threads,
  release notes (the "it worked before" signal). Ready-to-run queries + the claim-verification research prompt:
  → `refs/investigate-snippets.md`
- **Data-safety gate** before any output is shared: raw/sensitive → gitignored `.notes/`; shared docs scrubbed of
  cross-customer identifiers, internal URLs, PII. → `refs/scrub.md`

### Living / multi-session engagements
When the same blocker spans **multiple sessions** — new cases, a call transcript, a CTO Slack update, or a
voice-of-customer post arriving over time, with a growing claim set and a shared/living deliverable — keep the
accreting investigation coherent with **stable claim IDs, new-evidence routing, and doc↔canvas sync discipline**.
→ `refs/living-engagement.md` (also carries the scope check: this skill still *diagnoses and routes*; it is not an
engagement-tracker). Cross-claim patterns that recur across ≥2 claims are named in `refs/adversarial.md` (Step 2.7).

### Output
Always an internal deliverable (`templates/internal-doc.md`); a partner-facing version
(`templates/partner-doc.md`) only on request, after scrubbing.

## Validation
`python3 tests/validate_skill.py` (also run by `.githooks/pre-commit`). Design + plan archived under
`docs/superpowers/specs/` and `docs/superpowers/plans/`.
