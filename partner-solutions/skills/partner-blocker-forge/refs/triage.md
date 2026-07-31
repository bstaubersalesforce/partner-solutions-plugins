# refs/triage.md — the fast path (always runs; always writes the internal doc)

Goal: a defensible verdict fast, written to a short internal `.md`, ending in a recommend-and-ask escalation gate.

## Steps

1. **Pull the case(s) — light.** Records + resolution tail (refs/investigate-snippets.md): status, subject, and
   what the resolution says (bug / workaround / config / question). Full comment-thread reading is deep-dive.
2. **Quick-verify each claim.** For each claim from intake, a fast check against the highest-value source:
   primary docs first; Known Issues if it smells like a defect; the case resolution for what support found.
   Don't do the full four-source sweep here — that's deep-dive. Tag confidence.
3. **Classify — apply refs/adversarial.md.** Assign each claim its class (confirmed bug / config / knowledge-gap /
   question / accurate-by-design) and run the Step-2 framing challenges (strip rhetoric, count the *real*
   blockers, test the partner's own choice, root-caused vs. workaround).
4. **State the likely fix / workaround / path** for each real issue, at triage depth.
5. **Write the short internal `.md`** from `templates/internal-doc.md` (triage variant): TL;DR + §1 claims (quick)
   + §2 cases (from records/resolution) + the required verdict block + the escalation recommendation. Save it;
   this is the file the deep-dive expands in place. Sensitive raw capture → `.notes/` (refs/scrub.md).
   **🔴 A triage-only doc is PROVISIONAL and must say so, visibly:**
   - Stamp the TL;DR and the verdict block with **`⚠️ TRIAGE — single-source, unverified; not a deep-dive`**.
   - The verdict block's **"verification depth" field = `triage`**.
   - **No claim may carry High confidence** in a triage-only doc — cap at Med, and use `UNVERIFIED` where no source
     was actually checked. High confidence is earned only by deep-dive's four-source verification.
   - **No partner-facing doc** off a triage-only run (deep-dive first — see refs/deep-dive.md).

## The escalation gate — recommend and ASK (never auto-escalate)

End triage with a recommendation, then ask the user whether to proceed to deep-dive. Recommend escalation when any
trigger fires:
- A claim is **contradicted or overstated** (needs full doc verification to state precisely).
- A **confirmed product bug** appears in the mix.
- **Multiple cases** or a tangled multi-issue picture.
- A **partner-facing output** is requested (deep-dive first, then scrub).
- **High stakes** (relationship at risk, exec visibility, production decision pending).

Phrase it as: "Triage verdict: <one line>. Recommend <escalate / stop here> because <trigger/none>. Proceed to
the full deep-dive?" Then wait for the user.
