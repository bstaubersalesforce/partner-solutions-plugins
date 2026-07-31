# partner-blocker-forge — Design Spec

*Date: 2026-07-27 · Author flow via skill-forge · Family: *-forge (joins pov/poc/npi/workshop/skill-forge).*
*Location: `~/.claude/skills/partner-blocker-forge/`*

---

## Purpose

Turn a **partner technical blocker** into an **evidence-based diagnosis + structured deliverable** — separating what the
partner *claims* from what is *real*, and producing a doc the internal team (and optionally the partner) can act on.

Modeled on three exemplars from this workspace:
- `revenova-1gp-2gp-resolution-plan.md` (1GP→2GP migration blocker + precedent case + action plan)
- `maxval-agentforce-packaging-deep-dive.md` / `maxval-packaging-adversarial-review.md` (Agentforce/Data Kit packaging claims, verified + adversarially reviewed)
- `gainsight-private-connect-redshift-brief.md` (Data 360 Private Connect "stuck allocating" troubleshooting brief)

Shared DNA: **partner hits a blocker → verify claims against primary sources + actual support cases → adversarial "what's
real" verdict → action plan + escalation/routing, with honest unknowns flagged.**

## Inputs (trigger context)

The skill expects, at minimum:
- **The ask** — some content outlining what's needed (a thread summary, a note, a request).
- **Partner name.**
- **≥1 support case** (number or record ID).
- **A Slack thread** (channel + message, or pasted content).

Missing pieces → the skill flags the gap and proceeds with what's available (does not block).

## Core job (both, equally)

1. **Investigate + adversarially diagnose** — the rigor: pull the real cases, verify each claim against primary sources,
   classify what's actually going on, challenge the framing.
2. **Produce the deliverable** — stamp the finding into the house format (TL;DR → root cause/claims → cases → action
   plan → routing → sources).

Neither is secondary.

## Flow — one continuous path, two depths

```
INTAKE → parse ask / partner / case(s) / Slack thread; confirm provided, flag gaps.
   ↓
TRIAGE (always) → pull case record(s) + resolution; quick-verify each claim vs. sources;
                  land the adversarial verdict; state likely fix/workaround.
                  → ALWAYS writes a short INTERNAL .md (verdict + evidence-so-far + open items).
   ↓
   └─ Recommend escalation? (triggers: a claim is contradicted/overstated; a real product bug appears;
      multiple cases; partner-facing output requested; high stakes) → RECOMMEND + ASK the user.
   ↓  (on user yes)
DEEP-DIVE → expand the SAME .md IN PLACE: full claim verification across the four source classes;
            per-case root-cause read (comment threads, not just record); recommended architecture/path;
            partner-executable action plan; routing; sources.
   ↓
PARTNER-FACING (on request) → produce a scrubbed shareable version from the internal doc.
```

- **Triage → Deep-Dive is expand-in-place**, never redo. Deep-dive reads the triage `.md` and grows it.
- **Escalation = recommend + ask** (user decides), never silent auto-escalation.

## The adversarial method (MANDATORY core — `refs/adversarial.md`)

Every run must separate claimed-vs-real. For each claimed issue, classify as exactly one of:
- **Confirmed product bug** — reproduced/acknowledged by support/R&D (e.g. Maxval record-context: Record ID passed as
  literal `currentRecordId`).
- **Config / permission** — org setup, not a platform defect (e.g. enable-connected-app requests).
- **Knowledge gap / overstated claim** — the claim is inaccurate or too broad vs. the docs (e.g. "Data Kits exclude
  retrievers" — no-code retrievers *are* packageable).
- **Question, not an issue** — an inquiry that was answered (e.g. the 2GP non-linear versioning question).

Plus framing challenges: strip emotional/persuasive language; count the *real* blockers (not padded totals); test whether
the partner's own choice (e.g. "go manual for the pilot") is actually reasonable; check whether "resolved" means
root-caused or worked-around. Output a required **"Is there a real issue to resolve?"** verdict.

## The four source classes (MANDATORY verification breadth)

Diagnosis must check claims against all four when relevant — not docs alone:
1. **Primary product/packaging docs** — developer.salesforce.com (2GP `pkg2_dev`, Data Kits, Package Ancestors,
   packageable Agentforce metadata), help.salesforce.com, extensibility/readiness matrices.
2. **Known Issues** — is this a logged/known defect? (search Known Issues / Trailblazer).
3. **Case resolutions + comment threads** — what support/R&D actually found: bug vs. workaround vs. config; whether a
   root cause was stated or the fix was "check and see."
4. **Release notes** — did platform behavior change under the partner? (the "it worked before" signal — e.g. Flex
   Template validation change). Winter/Spring/Summer release notes + release-note search.

## Components

```
partner-blocker-forge/
├── SKILL.md                      # lean router: triggers, the flow, refusal conditions, scrub gate
├── refs/                         # lazy-loaded
│   ├── intake.md                 # parse ask/partner/cases/thread; gap-check
│   ├── triage.md                 # fast path: quick verify + the adversarial verdict rubric
│   ├── deep-dive.md              # full verification (4 source classes), per-case root-cause read, architecture, action plan
│   ├── investigate-snippets.md   # READY-TO-RUN: sf CLI case queries (record, comments, resolution tails);
│   │                             #   claim-verification research-prompt template; Known-Issues + release-note search patterns
│   ├── adversarial.md            # the mandatory claimed-vs-real classification + framing challenges
│   └── scrub.md                  # data-safety discipline (.notes vs scrubbed output)
├── templates/
│   ├── internal-doc.md           # TL;DR → claims/root-cause → cases → action plan → routing → open items → sources
│   └── partner-doc.md            # scrubbed shareable shell
├── tests/ + validation/          # check.sh-style validation (family convention)
└── docs/                         # this spec + README
```

## Ready-to-run snippets (the hybrid automation — `refs/investigate-snippets.md`)

Portable, invoked when org/tools are available (skill does not hard-require them):
- **sf CLI case pull:** record (CaseNumber/Subject/Status/IsClosed/Account/Description), CaseComment threads, resolution
  tails — with the field-name caveats learned this session (no `Product_Area__c`; parse to file for large results).
- **Claim-verification research prompt:** the structured deep-research template (verify each claim TRUE/PARTLY/FALSE with
  primary sources + dates + confidence; distinguish documented fact from inference).
- **Known-Issues + release-notes search patterns.**

## Data safety (MANDATORY gate — `refs/scrub.md`)

Slack threads + Org62 cases carry cross-customer data (other partners' org IDs, cases, internal GUS/Splunk links, PII).
- **Raw/sensitive capture → gitignored `.notes/`.**
- **Committed/shared docs → scrubbed** of unrelated customers, internal-only URLs, and PII.
- A **required safety step before any output is shared**, and always before a partner-facing doc.

## Output — always internal, partner on request

- **Always:** an internal evidence-based `.md` (routing, case IDs, root-cause detail retained).
- **On request:** a scrubbed partner-facing version (internal routing + case-comment specifics + cross-customer refs removed).

## House format (both templates share the spine)

TL;DR → (claims verified / verified root cause) → the cases (what they actually say) → recommended path/architecture →
partner-executable action plan → risks & open questions → routing → sources (primary, dated, confidence-tagged).

## Refusal / honesty conditions

- If a load-bearing fact can't be confirmed from public sources, **flag it as an open item for PM/support** — never assert
  it (e.g. the prompt-template-grounded-on-retriever question).
- Don't inflate the blocker count; don't accept crisis framing as fact.
- Don't fabricate case outcomes — if comment threads weren't read, say the case was assessed from record/summary only.
- Confidence-tag claims (High/Med/Low) with sources + dates.

## Build

Authored via **skill-forge** (author flow: spec → plan → implement), inheriting the family's validation suite + lazy-ref
discipline. Estimated **Tier 2–3** (multi-ref, templates, validation, refusal conditions).

## Non-goals (YAGNI)

- Not a general support-ticket manager or a live case-monitoring tool.
- Not a packaging *tool* (doesn't build packages) — it diagnoses and routes.
- No audience branching beyond internal + optional scrubbed partner doc.
- Triage is not a separate competing mode — it's the fast front door on the same path.
