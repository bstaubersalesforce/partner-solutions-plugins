# partner-blocker-forge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `partner-blocker-forge` skill — turns a partner technical blocker (ask + partner + ≥1 case + Slack thread) into an adversarial, evidence-based diagnosis and a structured deliverable, via a triage→deep-dive path.

**Architecture:** A *-forge-family skill: lean `SKILL.md` router + lazy-loaded `refs/` (intake, triage, deep-dive, investigate-snippets, adversarial, scrub) + two output `templates/` + a `validation/check.sh`. One continuous path with two depths: Triage always writes a short internal `.md`; on a recommend-and-ask gate it escalates into Deep-Dive, which expands that same file in place; a scrubbed partner-facing doc is produced on request.

**Tech Stack:** Markdown (skill content), Bash (validator), `sf` CLI + web/Slack research invoked at runtime (not hard-required). Conventions mirror sibling forges (`pie-poc-forge`, `skill-forge`).

**Authoring driver — skill-forge (REQUIRED):** This skill is authored *through* **skill-forge (author flow)**, not hand-built. Before Task 1, invoke skill-forge author mode on this spec to (a) confirm the **tier** (expected 2–3) and the tier-appropriate required practices, and (b) generate the scaffold shape (SKILL.md frontmatter, refs/ lazy-loading pattern, validation suite, refusal-conditions block) per `skill-forge/refs/rubric.md` + `tiers.md`. The tasks below then fill that scaffold. After Task 8, run skill-forge **audit** mode and close the tier-gap (Task 9). If skill-forge's scaffold conventions differ from any file layout below, **skill-forge wins** — adjust the tasks to match what it emits.

## Global Constraints

- **Location:** `~/.claude/skills/partner-blocker-forge/` (alongside the other forges).
- **Family conventions (copy from siblings):** `SKILL.md` with YAML frontmatter (`name`, `description`); lazy `refs/`; `templates/`; `validation/check.sh`; `README.md`.
- **`SKILL.md` stays lean** — it routes to refs; detail lives in refs, loaded on demand.
- **Adversarial classification is MANDATORY every run:** each claimed issue → exactly one of {confirmed product bug, config/permission, knowledge-gap/overstated, question-not-issue}; plus framing challenges; plus a required "Is there a real issue to resolve?" verdict.
- **Four source classes are MANDATORY verification breadth:** (1) primary product/packaging docs, (2) Known Issues, (3) case resolutions + comment threads, (4) release notes.
- **Data-safety gate is MANDATORY before sharing:** raw/sensitive → gitignored `.notes/`; committed/shared → scrubbed of unrelated customers, internal-only URLs, PII.
- **Escalation is recommend-and-ask**, never silent auto-escalate.
- **Output:** always an internal `.md`; partner-facing scrubbed version only on request.
- **Honesty:** confidence-tag claims (High/Med/Low) with sources + dates; flag unconfirmable facts as PM/support open items; never fabricate case outcomes; don't inflate blocker counts or accept crisis framing as fact.
- **House format spine (both templates):** TL;DR → claims-verified / verified-root-cause → the cases (what they actually say) → recommended path/architecture → partner-executable action plan → risks & open questions → routing → sources.

---

### Task 0: skill-forge author-flow kickoff (REQUIRED — do first)

**Files:** none created here — this task sets the scaffold conventions the rest follow.

- [ ] **Step 1: Invoke skill-forge in author mode** on the design spec (`docs/2026-07-27-partner-blocker-forge-design.md`). Let it read `refs/rubric.md`, `tiers.md`, `author-flow.md`.
- [ ] **Step 2: Record the confirmed tier + required practices** (expected Tier 2–3): the exact SKILL.md frontmatter fields, the refs lazy-loading convention, the validation-suite shape, and whether it mandates a refusal-conditions section / CI. Note any deltas from the file layout in Tasks 1–8.
- [ ] **Step 3: Reconcile** — if skill-forge's scaffold differs from this plan's paths/shape, **adopt skill-forge's** and adjust the affected task steps before proceeding. (skill-forge wins on conventions.)

---

### Task 1: Scaffold + validator + git init

**Files:**
- Create: `~/.claude/skills/partner-blocker-forge/README.md`
- Create: `~/.claude/skills/partner-blocker-forge/validation/check.sh`
- Create: `~/.claude/skills/partner-blocker-forge/.gitignore`
- (dirs) `refs/`, `templates/`, `validation/`, `docs/` (docs already exists)

**Interfaces:**
- Produces: `validation/check.sh` — exits 0 when all required files exist + SKILL.md has valid frontmatter + internal `](rel)` links resolve; non-zero otherwise. Every later task re-runs this. **Align its required-file list + checks with whatever skill-forge's Task 0 scaffold prescribes.**

- [ ] **Step 1: Write `.gitignore`** — include `.notes/` (data-safety), OS cruft.

```
# raw/sensitive capture — never commit (cross-customer cases, Slack threads, PII)
.notes/
.DS_Store
```

- [ ] **Step 2: Write `validation/check.sh`** (model on `pie-poc-forge`/`data360-workshop` check.sh — file presence + frontmatter + relative-link resolution).

```bash
#!/usr/bin/env bash
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0
pass(){ echo "PASS: $1"; }; fail(){ echo "FAIL: $1" >&2; FAIL=1; }
req(){ [ -f "$ROOT/$1" ] && pass "file: $1" || fail "missing: $1"; }
echo "== required files =="
for f in SKILL.md README.md \
  refs/intake.md refs/triage.md refs/deep-dive.md refs/investigate-snippets.md refs/adversarial.md refs/scrub.md \
  templates/internal-doc.md templates/partner-doc.md; do req "$f"; done
echo "== SKILL.md frontmatter =="
head -1 "$ROOT/SKILL.md" 2>/dev/null | grep -q '^---$' && grep -q '^name:' "$ROOT/SKILL.md" && grep -q '^description:' "$ROOT/SKILL.md" && pass "frontmatter ok" || fail "SKILL.md frontmatter (need --- / name: / description:)"
echo "== internal links resolve =="
lf=0
while IFS= read -r f; do
  grep -oE '\]\(([^)#]+)' "$f" 2>/dev/null | sed 's/](//' | while IFS= read -r t; do
    case "$t" in http*|mailto:*|"") continue;; esac
    d="$(cd "$(dirname "$f")" && pwd)"; [ -e "$d/$t" ] || [ -e "$ROOT/$t" ] || echo "BROKEN $f -> $t"
  done
done < <(find "$ROOT" -name '*.md' -not -path '*/.git/*' -not -path '*/.notes/*') > /tmp/pbf_links.txt 2>/dev/null
[ -s /tmp/pbf_links.txt ] && { cat /tmp/pbf_links.txt; fail "broken links"; } || pass "links resolve"
[ $FAIL -eq 0 ] && echo "check.sh: ALL GREEN" || echo "check.sh: FAILURES"
exit $FAIL
```

- [ ] **Step 3: `chmod +x validation/check.sh`**
- [ ] **Step 4: Run it — expect FAIL** (SKILL.md + refs + templates not yet written). Confirms the validator actually checks.

Run: `cd ~/.claude/skills/partner-blocker-forge && ./validation/check.sh; echo "exit=$?"`
Expected: FAILs listing missing SKILL.md/refs/templates; `exit=1`.

- [ ] **Step 5: git init + first commit**

```bash
cd ~/.claude/skills/partner-blocker-forge
git init -q && git add -A && git commit -q -m "chore: scaffold partner-blocker-forge (validator + gitignore + spec/plan)"
```

---

### Task 2: `refs/adversarial.md` — the mandatory core method

**Files:** Create: `refs/adversarial.md`

**Interfaces:**
- Produces: the 4-way classification vocabulary + framing-challenge checklist + the required "Is there a real issue?" verdict format — referenced by `triage.md` and `deep-dive.md`.

- [ ] **Step 1: Write `refs/adversarial.md`** containing, with a worked example per class drawn from the exemplars:
  - The 4 classes: **confirmed product bug** (Maxval record-context: Record ID passed as literal `currentRecordId`), **config/permission** (enable-connected-app), **knowledge-gap/overstated** ("Data Kits exclude retrievers" — no-code *is* packageable), **question-not-issue** (2GP non-linear versioning Q).
  - Framing challenges: strip persuasive language; count *real* blockers vs. padded totals; test if the partner's own choice is reasonable; distinguish "resolved (root-caused)" vs. "resolved (workaround, no cause)".
  - The required verdict block: **"Is there a real issue to resolve?"** → what's real / what's overstated / what's the underlying issue (capability vs. confidence/enablement).
- [ ] **Step 2: Run `./validation/check.sh`** — expect the `refs/adversarial.md` line to PASS (others still fail). 
- [ ] **Step 3: Commit** — `git add refs/adversarial.md && git commit -m "feat: adversarial claimed-vs-real method (mandatory core)"`

---

### Task 3: `refs/investigate-snippets.md` — ready-to-run assets (4 source classes)

**Files:** Create: `refs/investigate-snippets.md`

**Interfaces:**
- Produces: runnable case-pull queries + the claim-verification research prompt + Known-Issues/release-note search patterns — referenced by `triage.md` (light) and `deep-dive.md` (full).

- [ ] **Step 1: Write `refs/investigate-snippets.md`** with:
  - **sf CLI case pull** (record: `CaseNumber, Subject, Status, IsClosed, CreatedDate, ClosedDate, Account.Name, Description`; `CaseComment` threads; resolution tails). Include the caveats: **no `Product_Area__c` on Case**; write large `--json` results to a file then parse; query by `Id` when a record ID (`500…`) is given, by `CaseNumber` otherwise.
  - **Claim-verification research prompt** — the structured template: verify each claim TRUE/PARTLY/FALSE, primary sources + dates + confidence, documented-fact vs. inference, roadmap signal.
  - **Four-source-class search patterns:** primary docs (developer.salesforce.com paths), **Known Issues** (issues.salesforce.com / Trailblazer search), **case comment threads** (the CaseComment query), **release notes** ("<feature> release notes Winter/Spring/Summer '26" + the "it worked before → behavior change" heuristic).
- [ ] **Step 2: Run `./validation/check.sh`** — `refs/investigate-snippets.md` PASSes.
- [ ] **Step 3: Commit** — `git commit -am "feat: investigate snippets (case queries, claim-verify prompt, 4 source classes)"`

---

### Task 4: `refs/scrub.md` — data-safety gate

**Files:** Create: `refs/scrub.md`

**Interfaces:**
- Produces: the scrub checklist + `.notes` vs. output separation rule — referenced by `SKILL.md` (gate) and both templates.

- [ ] **Step 1: Write `refs/scrub.md`:** raw/sensitive → gitignored `.notes/`; before sharing, remove unrelated customers' org IDs/case numbers/names, internal-only URLs (GUS/Splunk/internal Slack archives), PII; partner-facing doc additionally strips internal routing + case-comment specifics. A concrete "safe vs. unsafe to share" checklist.
- [ ] **Step 2: Run `./validation/check.sh`** — `refs/scrub.md` PASSes.
- [ ] **Step 3: Commit** — `git commit -am "feat: data-safety scrub discipline (.notes vs scrubbed output)"`

---

### Task 5: `templates/internal-doc.md` + `templates/partner-doc.md`

**Files:** Create: `templates/internal-doc.md`, `templates/partner-doc.md`

**Interfaces:**
- Produces: the two output shells (house-format spine); consumed by `triage.md` (writes the short internal doc) and `deep-dive.md` (expands it) + the partner step.

- [ ] **Step 1: Write `templates/internal-doc.md`** — the spine as fill-in sections with guidance comments: front-matter (partner, date, cases, prepared-for), TL;DR, claims-verified/root-cause (with the 4-way classification + confidence tags), the cases table (what they actually say), recommended path/architecture, action plan (phased), risks & open questions (PM/support items), routing, sources (dated). Include a "Triage" minimal variant marker so triage writes a short version the deep-dive expands.
- [ ] **Step 2: Write `templates/partner-doc.md`** — same spine, scrubbed: neutral tone, no internal routing, no cross-customer refs, no internal URLs; adds a "verify before external use" note.
- [ ] **Step 3: Run `./validation/check.sh`** — both template lines PASS.
- [ ] **Step 4: Commit** — `git commit -am "feat: internal + partner-facing doc templates (house format)"`

---

### Task 6: `refs/intake.md` + `refs/triage.md`

**Files:** Create: `refs/intake.md`, `refs/triage.md`

**Interfaces:**
- Consumes: `adversarial.md`, `investigate-snippets.md`, `templates/internal-doc.md`.
- Produces: the intake gap-check + the triage fast-path procedure ending in the short internal `.md` + the recommend-and-ask escalation gate.

- [ ] **Step 1: Write `refs/intake.md`** — parse the 4 inputs (ask, partner, case(s), Slack thread); confirm what's present; flag gaps (proceed anyway); resolve case number vs. record ID; read the Slack thread for the claimed issues + any linked case.
- [ ] **Step 2: Write `refs/triage.md`** — fast path: pull case record(s) + resolution (light), quick-verify each claim against docs+Known-Issues, apply `adversarial.md` classification, state likely fix/workaround, **always write the short internal `.md`** from the template's triage variant. End with the **escalation triggers** (claim contradicted/overstated; real product bug; multiple cases; partner-facing requested; high stakes) → **recommend + ASK**.
- [ ] **Step 3: Run `./validation/check.sh`** — both PASS; links resolve.
- [ ] **Step 4: Commit** — `git commit -am "feat: intake gap-check + triage fast-path with recommend-and-ask escalation"`

---

### Task 7: `refs/deep-dive.md`

**Files:** Create: `refs/deep-dive.md`

**Interfaces:**
- Consumes: the triage `.md`, `investigate-snippets.md`, `adversarial.md`, `templates/internal-doc.md`.
- Produces: the full-investigation procedure that expands the triage doc in place.

- [ ] **Step 1: Write `refs/deep-dive.md`** — expand-the-same-file-in-place: full claim verification across **all four source classes** (docs, Known Issues, **case comment threads read in full**, release notes); per-case root-cause read (bug vs. workaround vs. config; note where only record/summary was read); recommended architecture/path; phased partner-executable action plan; routing; dated/confidence-tagged sources. Explicit rule: **never redo triage — grow it.**
- [ ] **Step 2: Run `./validation/check.sh`** — PASS.
- [ ] **Step 3: Commit** — `git commit -am "feat: deep-dive expand-in-place across four source classes"`

---

### Task 8: `SKILL.md` (router) + `README.md`

**Files:** Create: `SKILL.md`, `README.md`

**Interfaces:**
- Consumes: all refs + templates (routes to them).
- Produces: the entry point with frontmatter the validator checks.

- [ ] **Step 1: Write `SKILL.md`** — YAML frontmatter (`name: partner-blocker-forge`; `description:` with trigger language: "Use when a partner reports a technical blocker / packaging or platform issue and you need to verify what's real vs. claimed against cases + docs and produce a diagnosis/deliverable…"). Body = the linear flow (Intake → Triage → recommend-ask → Deep-Dive → partner-on-request), the **mandatory** callouts (adversarial classification, four source classes, scrub gate), and lazy links to each ref/template. Keep lean — route, don't inline.
- [ ] **Step 2: Write `README.md`** — one-paragraph what/why, the 3 exemplars it generalizes, inputs, output anatomy (internal + optional partner), how to run the validator.
- [ ] **Step 3: Run `./validation/check.sh` — expect ALL GREEN** (all files present, frontmatter valid, links resolve).

Run: `cd ~/.claude/skills/partner-blocker-forge && ./validation/check.sh`
Expected: `check.sh: ALL GREEN`.

- [ ] **Step 4: Commit** — `git commit -am "feat: SKILL.md router + README (partner-blocker-forge complete)"`

---

### Task 9: Dogfood against TWO known exemplars + audit

**Files:** Create: `.notes/dogfood-maxval.md`, `.notes/dogfood-revenova.md` (gitignored — not committed)

**Interfaces:** Consumes: the whole skill. Produces: validation that the skill reproduces both exemplar outcomes across two different problem domains (Agentforce packaging vs. 1GP→2GP migration).

- [ ] **Step 1a: Dry-run against the Maxval inputs** (ask + partner + the 10 cases + the Slack thread) — confirm the skill would classify the two claims correctly (retrievers = overstated/knowledge-gap; agents = true-by-design), catch the record-context bug as a confirmed product bug, and land the "confidence not capability" verdict. Capture gaps in `.notes/dogfood-maxval.md`.
- [ ] **Step 1b: Dry-run against the Revenova inputs** (the 1GP→2GP migration blocker — `~/claude-projects/revenova-1gp-2gp-resolution-plan.md`) — confirm the skill's flow reproduces its shape: verified root cause, the precedent case (Jidoka/Compliatric), the three removal sub-paths, action plan, and routing (traditional support, no PIE). This tests a *different domain* than Maxval — good generalization check. Capture gaps in `.notes/dogfood-revenova.md`.
- [ ] **Step 2: Fix any ref/template gaps the dogfood exposes;** re-run `./validation/check.sh` (ALL GREEN).
- [ ] **Step 3: skill-forge AUDIT (REQUIRED)** — run skill-forge audit mode against the finished skill; record the tier-gap report; **close the gaps** it flags (or explicitly note any deferred with reason). Re-run `./validation/check.sh` after fixes.
- [ ] **Step 4: Commit** — `git commit -am "test: dogfood vs Maxval + skill-forge audit; close tier-gap"`

---

## Self-Review

**Spec coverage:** ✅ authored-via-skill-forge (Task 0 author kickoff + Task 9 required audit) · purpose/inputs (Task 6 intake, README) · both-equally core (investigate refs + templates) · triage→deep-dive path w/ recommend-ask (Tasks 6–7) · triage-always-writes-.md (Task 6) · expand-in-place (Task 7) · mandatory adversarial (Task 2) · four source classes (Tasks 3,7 + Global Constraints) · scrub gate (Task 4) · always-internal/partner-on-request (Task 5) · house format (Task 5) · refusal/honesty (Global Constraints, Tasks 2/7) · build-via-forge conventions (Tasks 0–1) · validation suite (Task 1). No spec section unmapped.

**Placeholder scan:** No TBD/TODO; each task names exact files, the validator command, and concrete content requirements (the prose files specify *what must be in them* with exemplar-anchored examples rather than fabricated final copy — appropriate for a content skill).

**Type consistency:** File paths + the `validation/check.sh` required-file list in Task 1 exactly match the files created in Tasks 2–8. Ref/template names are consistent throughout (`adversarial.md`, `investigate-snippets.md`, `scrub.md`, `intake.md`, `triage.md`, `deep-dive.md`, `internal-doc.md`, `partner-doc.md`).
