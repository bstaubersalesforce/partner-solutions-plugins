# refs/deep-dive.md — full investigation (expands the triage doc IN PLACE)

Runs only after the user approves escalation at the triage gate. **Grow the same `.md` file the triage step
wrote — but RECLASSIFY, don't just append.** Expansion means the full evidence can *overturn* a triage call, not
only add to it. If a full comment thread changes a claim's class (e.g. triage said "config/validation rule," the
thread shows an R&D-reproduced bug), **strike the triage class, record the correction inline, and update the
TL;DR + verdict.** Remove the triage provisional stamp only once the four-source verification is actually done.

## Steps

1. **Full claim verification across ALL FOUR source classes** (refs/investigate-snippets.md), per claim:
   1. **Primary docs** — the authoritative page (readiness matrix, packageable-metadata list, Package Ancestors,
      etc.). Get the exact wording; split sub-claims that differ.
   2. **Known Issues** — is it a logged defect?
   3. **Case comment threads — read in full.** The resolution tail tells you bug vs. workaround vs. config, and
      whether R&D stated a root cause. This is where triage's "from resolution summary" upgrades to real evidence.
   4. **Release notes** — did behavior change under the partner? (the "it worked before" signal.)
   For each: TRUE / PARTLY / FALSE, documented-fact vs. inference, source + date, confidence, roadmap signal.
   Dispatch the claim-verification research prompt (refs/investigate-snippets.md) per distinct claim.
   **When sources CONFLICT** (docs say "supported," a case shows it failing, release notes show a change): do not
   silently reconcile. **Precedence: a reproduced case or an org-observed fact beats a doc's "supported" claim**
   (the doc describes intent; the case describes reality). State the disagreement explicitly in §1, and treat the
   gap between doc-claim and observed-reality as itself a finding (often a bug or a behavior change). If no source
   covers the claim at all (an **unreleased/roadmap** capability), it's `UNVERIFIED` → a PM/support open item,
   never asserted.
2. **Per-case root-cause read.** For each case, land its class with evidence from the thread. Note explicitly any
   case assessed from record/summary only (don't imply you read a thread you didn't).
3. **Re-run the adversarial verdict at full depth** (refs/adversarial.md Step 3): what's real, what's overstated,
   the underlying issue (capability / operational / confidence), and the "so what."
4. **Build the recommended path/architecture** — the viable approach today given the confirmed constraints
   (packageable-via-X + per-org-Y + post-install-Z), citing Salesforce guidance.
5. **Write the phased action plan and routing** — reframe → correct overstatement → show supported path →
   address the real underlying issue; split capability vs. operational tracks; note scope caveats.
6. **Expand the internal `.md` in place** to the full `templates/internal-doc.md` shape (all sections), with
   dated/confidence-tagged sources. Keep raw/sensitive material in `.notes/` (refs/scrub.md).

## Then: partner-facing doc (on request only)

If a partner-facing deliverable was requested, produce it from `templates/partner-doc.md` — **run refs/scrub.md
first**. Never generate the partner doc without the scrub gate.

## Honesty rules (throughout)

- Confidence-tag every claim; flag any unconfirmable fact as an **open item for PM/support** — never assert it.
- Don't inflate the blocker count or accept crisis framing as fact.
- Don't fabricate case outcomes; state where a case was assessed from record/summary only.
