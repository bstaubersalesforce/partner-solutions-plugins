# <Partner> <Blocker Topic> — Case Deep-Dive & Path Forward

*Prepared <date>. Internal (Partner Solutions). Basis: cited Org62 cases (records + comment threads); capability
claims verified against primary developer.salesforce.com docs (<release> / API <n>).*

> **Triage variant:** on a triage-only run, fill TL;DR + §1 (claims, quick) + §2 (cases, from records/resolution)
> + the required verdict + the escalation recommendation, and stop. Deep-dive EXPANDS this same file in place —
> it does not start over.

---

## TL;DR
<3–5 bullets: the headline. Lead with the verdict — what's real vs. overstated, the likely fix/path (or that there
is none), and whether this is a capability / operational / confidence problem. State the "is there a real issue?"
answer here. **Verification depth: triage | deep-dive** (state which). If triage-only, stamp:
**⚠️ TRIAGE — single-source, unverified; not a deep-dive.**>

## 1. The claims — verified
<For each claimed issue: the claim, the verdict from refs/adversarial.md (confirmed bug / config / knowledge-gap /
question / accurate-by-design), the evidence (doc line or case), source + date, confidence (High/Med/Low).
Split sub-claims that have different answers. Use a table when there are several.>

## 2. The cases — what they actually say
<Table of the cited cases: number, subject, and what the thread actually shows — bug vs. workaround vs. config vs.
question. Call out any confirmed product bug and any "resolved by workaround, no stated root cause." Note where a
case was assessed from record/summary only vs. full comment thread.>

## 3. Recommended path / architecture — OR: no supported path
<The viable path today given the constraints — e.g. the multi-package + template + post-install design; or the
concrete fix + workaround. Cite Salesforce guidance. Distinguish what's packageable/supported from what's per-org.
**Do NOT manufacture a path.** If the honest answer is that there is no supported path today (a hard constraint,
no workaround, no roadmap — the "Accurate + hard constraint" class), title this section **"No supported path
today"** and state exactly that: the constraint, why "wait" is or isn't viable, and the specific PM/roadmap ask.
An empty "path forward" is a real finding, not a gap to fill with optimism.>

## 4. Action plan
<Phased, partner-executable: reframe → correct the overstated claim → show the supported path → address the real
underlying issue (often confidence: request root-cause writeups). Number the phases. **If §3 is "no supported
path,"** the action plan is the escalation itself: the PM/roadmap ask, the interim mitigation (if any), and honest
expectation-setting — not synthesized build steps.>

## 5. Risks & open questions
<The load-bearing unknowns that need PM/support — especially any fact not confirmable from public docs. Flag,
never assert. Note which retriever/agent/etc. specifics the partner must confirm.>

## 6. Routing
<Who owns what: capability/architecture/roadmap track vs. operational/support track. Note scope caveats (e.g. PIE
not scoped for packaging/security review → advisory + post-install-runner, not packaging support).>

## Sources
<Primary, dated, confidence-tagged. developer.salesforce.com doc paths; the verified Org62 case list; any precedent
doc. Note where help.salesforce.com was JS-rendered/unread and corroborated elsewhere.>
