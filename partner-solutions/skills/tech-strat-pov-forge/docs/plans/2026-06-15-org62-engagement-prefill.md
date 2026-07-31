# Org62 Engagement Pre-fill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional, per-user Org62 engagement pre-fill that hydrates pov-builder and pie-poc-forge intake from a `Partner_Engagement__c` record (or any Account/Opportunity anchor), via a single shared ref module.

**Architecture:** A self-contained ref module `refs/org62-prefill.md` (structural twin of the existing `slack-insights.md`) owns all resolution + hydration logic. `pov-builder/SKILL.md` and `pie-poc-forge/SKILL.md` each gain a thin, silent Stage-1 hook that loads the module only when the user opts into Org62 enrichment. The module is read-only (`sf data query` / `sf org display`), per-user (identity from the live session, alias from `ORG62_ALIAS` in settings), and strictly additive — every blank field falls through to today's behavior.

**Tech Stack:** Markdown skill refs, Salesforce CLI (`sf`) read-only queries, Python stdlib structural validators (`tests/validate_skill.py`), git pre-commit hooks.

---

## Design source

Spec: `docs/superpowers/specs/2026-06-15-org62-engagement-prefill-design.md` (lives in `pov-builder/docs/specs/`). Read the **Optionality contract** and **Verified Org62 facts** sections before starting — they are load-bearing.

## Conventions to honor (discovered from the codebase)

- The module mirrors `pov-builder/refs/slack-insights.md`: a `> Lazily loaded…` banner line, a statement that SKILL.md carries only thin hooks, then numbered sections.
- Both skills' `tests/validate_skill.py` enforce: **R-ARCH-02** every referenced path exists (no dangling) and **R-ARCH-03** every `refs/` file is referenced by the instructions (no orphans). The instant the module file is added, it MUST be referenced from SKILL.md or the suite fails — so the ref and the hook land in the same task.
- pov-builder's MCP/CLI defaults precedent: Slack defaults live in a dedicated `~/.claude/pov-builder-slack.json`, NOT in `settings.json` (the harness rejects unknown `settings.json` keys). **`ORG62_ALIAS` is an `env` var, which `settings.json` *does* permit** — so it belongs in `settings.json` under `env`. Confirm this distinction holds (Task 1).

## File structure

| File | Skill | Responsibility | Action |
|---|---|---|---|
| `refs/org62-prefill.md` | pov-builder | Owns all Org62 resolution + hydration + role-mapping logic. Canonical copy. | Create |
| `SKILL.md` (Stage 1) | pov-builder | Thin silent hook: offer Org62 enrichment, load the module when opted in. | Modify |
| `refs/org62-prefill.md` | pie-poc-forge | Same module, referenced for `requirements.json` pre-fill. | Create (copy) |
| `SKILL.md` (intake) | pie-poc-forge | Thin hook: offer Org62 pre-fill of `requirements.json`. | Modify |
| `tests/validate_skill.py` | both | Add Org62-module structural checks. | Modify |
| `README.md` | both | Document the optional Org62 enrichment + `ORG62_ALIAS`. | Modify |

> **Module-copy decision (from spec open item):** these two skills are separate git repos with no shared parent, and each already keeps its own copy of cross-skill refs (e.g. `mermaid-diagrams.md`, `ensure-home-link.py` exist in both). So we follow that precedent: author the canonical module in pov-builder, copy it verbatim into pie-poc-forge, and add a parity check (Task 7) that fails if the two copies drift.

---

## Task 1: Confirm settings wiring + capture the canonical SOQL

**Files:**
- Inspect only: `~/.claude/settings.json`, `~/.claude/skills/pov-builder/refs/slack-insights.md`

- [ ] **Step 1: Verify `env` is an accepted settings.json key**

Run:
```bash
cat ~/.claude/settings.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('env present:', 'env' in d); print(json.dumps(d.get('env',{}), indent=2))" 2>/dev/null || echo "no settings.json yet"
```
Expected: prints current `env` block (or "no settings.json yet"). This confirms whether `ORG62_ALIAS` can be added under `env`. If `settings.json` rejects it later, fall back to the slack precedent (a dedicated `~/.claude/org62-prefill.json`) — note which path you took.

- [ ] **Step 2: Confirm the live schema facts the module hardcodes**

Run (requires fresh `org62` auth — if expired, stop and ask the user to run `! sf org login web --alias org62`):
```bash
sf sobject describe --sobject Partner_Engagement__c --target-org "${ORG62_ALIAS:-org62}" --json 2>/dev/null \
  | python3 -c "import sys,json; d=json.load(sys.stdin)['result']; refs={f['name']:f.get('referenceTo') for f in d['fields'] if f['type']=='reference'}; [print(k,'->',refs[k]) for k in ('Account__c','Customer_Account_Lookup__c','Opportunity__c','Customer_Story__c','Partnership__c') if k in refs]"
```
Expected: each of the five fields prints with its `referenceTo`, matching the spec's "Verified Org62 facts" table. If any field is missing/renamed, update the spec AND this plan before continuing.

- [ ] **Step 3: No commit** (inspection only).

---

## Task 2: Create the shared module `refs/org62-prefill.md` in pov-builder

**Files:**
- Create: `~/.claude/skills/pov-builder/refs/org62-prefill.md`
- Test: `~/.claude/skills/pov-builder/tests/validate_skill.py` (run existing suite)

- [ ] **Step 1: Write the module file**

Create `refs/org62-prefill.md` with this exact content:

```markdown
# Org62 Engagement Pre-fill Reference

> Lazily loaded. Load this only when Org62 enrichment is in play — i.e. the user accepted the Stage-1 offer to pull from an engagement, OR named/pasted a record ID. If the user declines, do not load this file; the flow is unchanged.

This file owns all Org62 pre-fill logic. `SKILL.md` carries only a thin Stage-1 hook (offer + load). Org62 is **optional enrichment**: nothing it returns is ever required (see the Optionality contract). It is read-only — `sf data query` / `sf org display` only, never DML or deploy. Org62 is production; honor the workspace guardrails.

## 0. Optionality contract (load-bearing)

1. **No anchor is valid** — user can skip entirely; the skill runs on its normal inputs.
2. **A partial anchor is valid** — only an Account, only an Opp, or only a status all hydrate whatever exists; missing records never stop the flow.
3. **A failed/empty pull is valid** — expired auth, no match, blank lookups all return whatever was retrieved (possibly nothing) and proceed.

Every blank field below renders as `—` and falls through to the skill's existing web-research / ask behavior.

## 1. Identity & config (per-user — never hardcode a username)

- **Alias** comes from the `ORG62_ALIAS` env var (set in `~/.claude/settings.json` under `env`), defaulting to `org62` when unset.
- **Username is discovered at runtime**, never hardcoded: `sf org display --target-org $ORG62_ALIAS --json` → `result.username`. Whoever is logged in is the user queried.
- **Expired/absent session** → tell the user to authenticate THEIR OWN account:
  `! sf org login web --alias $ORG62_ALIAS --instance-url https://org62.my.salesforce.com`
  Non-fatal: if they decline, proceed on normal inputs (contract §3).

## 2. Offer (Stage 1, the only thing SKILL.md triggers)

A single capability-style offer, not a stall: "Want to pull context from an Org62 engagement, or start fresh?" Decline → do not load further; flow unchanged.

## 3. Entry — list-first, any-ID fallback (NEVER fuzzy search)

- **Default (list):** resolve the current username (§1), then list that user's active engagements:
  `sf data query --target-org $ORG62_ALIAS --query "SELECT Id, Name, Project_Status__c, Customer_Account_Name__c FROM Partner_Engagement__c WHERE RecordTypeId = '0123y0000022rMkAAI' AND OwnerId IN (SELECT Id FROM User WHERE Username = '<session-username>') AND Project_Status__c IN ('Not Started','In Progress','On Hold') ORDER BY Project_Status__c, Name"`
  Present as a numbered list; the user picks one. (GTP RecordType id `0123y0000022rMkAAI`.)
- **Fallback (any ID):** user pastes a 15/18-char Id. Detect type by key prefix:
  - `a26` → `Partner_Engagement__c` (confirmed live in Org62, 2026-06-15).
  - `001` → Account. `006` → Opportunity.
  - Unrecognized prefix → tell the user the expected prefixes; let them re-enter or skip.

## 4. Normalize an Account/Opportunity anchor to its PE

- **PE id** → use directly.
- **Account id** → `SELECT Id FROM Partner_Engagement__c WHERE Account__c = :id OR Customer_Account_Lookup__c = :id`
  - 0 rows → anchor on the bare Account (hydrate Account fields only).
  - 1 row → use it. Many → list them, user picks.
- **Opportunity id** → `SELECT Id FROM Partner_Engagement__c WHERE Opportunity__c = :id` (same 0/1/many handling).

## 5. Hydrate (one SOQL, traversing lookups)

```
SELECT Name, Project_Status__c, Project_Type__c, Customer_Account_Name__c,
       Account__r.Name, Account__r.Industry, Account__r.Website, Account__r.RecordType.DeveloperName,
       Customer_Account_Lookup__r.Name, Customer_Account_Lookup__r.RecordType.DeveloperName,
       Opportunity__r.Name, Opportunity__r.StageName, Opportunity__r.Amount,
       Opportunity__r.CloseDate, Opportunity__r.Description,
       Customer_Story__r.Name, Owner.Name
FROM Partner_Engagement__c WHERE Id = :peId
```

## 6. Role mapping (RecordType-aware, INFORMATIONAL only — never a gate)

- **POV subject = `Account__c`** ("Partner Account").
  - RT DeveloperName = `Partner` → label "Partner ✓".
  - Any other RT → label "Direct/other account (exploring partnership)". This is a LEGITIMATE case (a direct customer exploring a partnership), not an error, warning, or gate.
- **Pilot customer = `Customer_Account_Lookup__r`** (any RT) → proof point ("partner is already piloting with {customer}"). Blank → `Customer_Account_Name__c` text → `—`.
- There is NO single "Customer" Account RecordType — do not match one; customer = any non-Partner account in the lookup.

## 7. Emit the engagement-context block

```
PARTNER (POV subject)   : {Account__r.Name}   [Partner ✓ | Direct/other (exploring partnership)]
  industry / website    : {Account__r.Industry} / {Account__r.Website}
PILOT CUSTOMER (proof)  : {Customer_Account_Lookup__r.Name}   (or text fallback, or —)
OPPORTUNITY             : {Opp.Name} · {StageName} · {Amount} · {CloseDate}
  use-case              : {Opp.Description}
CUSTOMER STORY          : {Customer_Story__r.Name}   (or —)
ENGAGEMENT              : {Name} · {Project_Type__c} · {Project_Status__c} · owner {Owner.Name}
```

Each `—` field is handed to the host skill's normal intake (web research / clarifying questions).

## 8. Host integration

- **pov-builder:** fold populated fields into the Stage-2 pre-fill alongside web/Slack, tagged `[from Org62 engagement — confirm]`. Blanks become Stage-3 questions as today.
- **pie-poc-forge:** map fields into `requirements.json` (partner, pilot customer, use-case); blanks stay unset for the normal intake to fill.

## 9. Provenance

Record in the host's provenance section: the PE Id + Name used, which lookups resolved, and a note that values are `[from Org62 — confirm]` (never hardened without confirmation).
```

- [ ] **Step 2: Run the pov-builder structural suite to confirm the orphan check now fails**

Run:
```bash
cd ~/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -20
```
Expected: FAIL on the no-orphans check — `present but never referenced: ['refs/org62-prefill.md']`. This is the expected red state; Task 3 (the SKILL.md hook) makes it green. Do NOT commit yet.

---

## Task 3: Add the thin Stage-1 hook to pov-builder SKILL.md

**Files:**
- Modify: `~/.claude/skills/pov-builder/SKILL.md` (Stage 1 region, near the existing Slack-tooling check ~line 100)
- Test: `~/.claude/skills/pov-builder/tests/validate_skill.py`

- [ ] **Step 1: Insert the hook**

In `SKILL.md`, immediately after the Slack-tooling check block (the bullets ending "...never stall on it." around line 103), add:

```markdown
**Org62 engagement check (same pass, silent).** Offer optional pre-fill from an existing Org62 engagement: "Want to pull context from an Org62 engagement, or start fresh?" The alias comes from the `ORG62_ALIAS` env var (default `org62`); identity is the logged-in session user (never hardcoded).
- If the user accepts, or names/pastes a `Partner_Engagement__c`/Account/Opportunity ID, load `refs/org62-prefill.md` and follow it (list-pick or ID → hydrate → emit the engagement-context block into Stage 2).
- If the user declines, do not load the ref — the POV flow is unchanged. This is an offer, not a gate; never stall, and nothing it returns is ever required.
```

- [ ] **Step 2: Add the Org62 confidence tag to the trust-tier list**

Find the confidence-tier list (the `[from internal Slack — confirm]` bullet ~line 126) and add directly after it:

```markdown
- `[from Org62 engagement — confirm]` — sourced from a linked Org62 `Partner_Engagement__c` (partner, pilot customer, opportunity use-case); high value but unconfirmed — never hardens to confirmed without partner confirmation (see `refs/org62-prefill.md`)
```

- [ ] **Step 3: Run the suite — expect green**

Run:
```bash
cd ~/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -15
```
Expected: PASS — the orphan check clears because `refs/org62-prefill.md` is now referenced, and the dangling-ref check passes because the file exists.

- [ ] **Step 4: Commit**

```bash
cd ~/.claude/skills/pov-builder
git add refs/org62-prefill.md SKILL.md
git commit -m "feat: optional Org62 engagement pre-fill (shared module + Stage-1 hook)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Add Org62-module structural checks to pov-builder validator

**Files:**
- Modify: `~/.claude/skills/pov-builder/tests/validate_skill.py`

- [ ] **Step 1: Add a check that the module is referenced and read-only**

Add a new `@check` near the other ref checks:

```python
@check("Org62 pre-fill module exists, is referenced, and is read-only")
def t_org62_prefill():
    path = "refs/org62-prefill.md"
    assert os.path.exists(os.path.join(SKILL, path)), f"missing {path}"
    body = read(path)
    # read-only guarantee: no write/DML/deploy commands in the module
    forbidden = ["sf project deploy", "sf data create", "sf data update",
                 "sf data delete", "sf data upsert", "DELETE FROM", "UPDATE "]
    hits = [tok for tok in forbidden if tok in body]
    assert not hits, f"module must be read-only, found: {hits}"
    # optionality contract must be present
    assert "Optionality contract" in body, "module missing Optionality contract section"
    # hooked from SKILL.md
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"
```

- [ ] **Step 2: Run the suite — expect green**

Run:
```bash
cd ~/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -15
```
Expected: PASS, including the new `t_org62_prefill` check.

- [ ] **Step 3: Verify the check actually fails against a broken module (mutation test)**

Run:
```bash
cd ~/.claude/skills/pov-builder
cp refs/org62-prefill.md /tmp/org62-backup.md
printf '\n\nsf data delete --sobject Foo\n' >> refs/org62-prefill.md
python3 tests/validate_skill.py 2>&1 | grep -i "read-only" && echo "MUTATION CAUGHT"
cp /tmp/org62-backup.md refs/org62-prefill.md && rm /tmp/org62-backup.md
```
Expected: prints "MUTATION CAUGHT" then restores the file. Confirms the check has teeth.

- [ ] **Step 4: Commit**

```bash
cd ~/.claude/skills/pov-builder
git add tests/validate_skill.py
git commit -m "test: structural + read-only checks for Org62 pre-fill module

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Copy the module into pie-poc-forge and add its intake hook

**Files:**
- Create: `~/.claude/skills/pie-poc-forge/refs/org62-prefill.md` (verbatim copy)
- Modify: `~/.claude/skills/pie-poc-forge/SKILL.md` (intake section, near `requirements.json` collection)
- Test: `~/.claude/skills/pie-poc-forge/tests/validate_skill.py`

- [ ] **Step 1: Copy the canonical module verbatim**

Run:
```bash
cp ~/.claude/skills/pov-builder/refs/org62-prefill.md ~/.claude/skills/pie-poc-forge/refs/org62-prefill.md
```

- [ ] **Step 2: Add the intake hook to pie-poc-forge SKILL.md**

In `pie-poc-forge/SKILL.md`, in the inputs-collection step (where it lists "POV MVP Build Plan / Assessment / pasted requirements"), add:

```markdown
**Optional Org62 pre-fill.** Before/alongside collecting pasted inputs, offer to hydrate from an Org62 engagement: "Want to pull partner + use-case context from an Org62 engagement, or work only from the inputs you provide?" If accepted (or the user names/pastes a `Partner_Engagement__c`/Account/Opportunity ID), load `refs/org62-prefill.md`, follow it, and map the emitted engagement-context block into `requirements.json` (partner account, pilot customer, opportunity use-case). Alias = `ORG62_ALIAS` env (default `org62`); identity = logged-in session user. Declining changes nothing; any field it cannot supply is filled by the normal intake. Read-only.
```

- [ ] **Step 3: Run the pie-poc-forge suite — expect green**

Run:
```bash
cd ~/.claude/skills/pie-poc-forge && python3 tests/validate_skill.py 2>&1 | tail -15
```
Expected: PASS — module exists and is now referenced (no orphan, no dangling ref).

- [ ] **Step 4: Commit**

```bash
cd ~/.claude/skills/pie-poc-forge
git add refs/org62-prefill.md SKILL.md
git commit -m "feat: optional Org62 engagement pre-fill for requirements.json intake

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Add the read-only/structural check to pie-poc-forge validator

**Files:**
- Modify: `~/.claude/skills/pie-poc-forge/tests/validate_skill.py`

- [ ] **Step 1: Add the same `t_org62_prefill` check**

Add to `pie-poc-forge/tests/validate_skill.py` (same body as Task 4 Step 1):

```python
@check("Org62 pre-fill module exists, is referenced, and is read-only")
def t_org62_prefill():
    path = "refs/org62-prefill.md"
    assert os.path.exists(os.path.join(SKILL, path)), f"missing {path}"
    body = read(path)
    forbidden = ["sf project deploy", "sf data create", "sf data update",
                 "sf data delete", "sf data upsert", "DELETE FROM", "UPDATE "]
    hits = [tok for tok in forbidden if tok in body]
    assert not hits, f"module must be read-only, found: {hits}"
    assert "Optionality contract" in body, "module missing Optionality contract section"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"
```

- [ ] **Step 2: Run the suite — expect green**

Run:
```bash
cd ~/.claude/skills/pie-poc-forge && python3 tests/validate_skill.py 2>&1 | tail -15
```
Expected: PASS including `t_org62_prefill`.

- [ ] **Step 3: Commit**

```bash
cd ~/.claude/skills/pie-poc-forge
git add tests/validate_skill.py
git commit -m "test: structural + read-only checks for Org62 pre-fill module

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Add a cross-skill parity check (the two copies must not drift)

**Files:**
- Modify: `~/.claude/skills/pov-builder/tests/validate_skill.py` (the canonical-copy owner)

- [ ] **Step 1: Add a parity check that compares the two module copies when both exist**

Add to `pov-builder/tests/validate_skill.py`:

```python
@check("Org62 module copy in pie-poc-forge is in sync (skipped if sibling absent)")
def t_org62_module_parity():
    sibling = os.path.join(SKILL, "..", "pie-poc-forge", "refs", "org62-prefill.md")
    if not os.path.exists(sibling):
        return  # sibling skill not installed here — nothing to compare (n-a)
    here = read("refs/org62-prefill.md")
    there = open(sibling, encoding="utf-8").read()
    assert here == there, "refs/org62-prefill.md differs between pov-builder and pie-poc-forge — re-sync the copies"
```

- [ ] **Step 2: Run the suite — expect green**

Run:
```bash
cd ~/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -15
```
Expected: PASS — the two copies are identical (Task 5 copied verbatim).

- [ ] **Step 3: Verify the parity check fails on drift (mutation test)**

Run:
```bash
cd ~/.claude/skills/pov-builder
cp ../pie-poc-forge/refs/org62-prefill.md /tmp/sib-backup.md
printf '\n<!-- drift -->\n' >> ../pie-poc-forge/refs/org62-prefill.md
python3 tests/validate_skill.py 2>&1 | grep -i "differs" && echo "DRIFT CAUGHT"
cp /tmp/sib-backup.md ../pie-poc-forge/refs/org62-prefill.md && rm /tmp/sib-backup.md
```
Expected: prints "DRIFT CAUGHT" then restores. Confirms the parity guard works.

- [ ] **Step 4: Commit**

```bash
cd ~/.claude/skills/pov-builder
git add tests/validate_skill.py
git commit -m "test: parity guard between pov-builder and pie-poc-forge Org62 module copies

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Document `ORG62_ALIAS` and the feature in both READMEs

**Files:**
- Modify: `~/.claude/skills/pov-builder/README.md`
- Modify: `~/.claude/skills/pie-poc-forge/README.md`

- [ ] **Step 1: Add an Org62 pre-fill section to pov-builder README**

Append a section (match the README's existing heading style):

```markdown
## Optional: Org62 engagement pre-fill

When you accept the Stage-1 offer, pov-builder can hydrate the POV from an existing
Org62 `Partner_Engagement__c` — partner account, pilot customer, opportunity use-case,
and any linked customer story. Pick from your active engagements or paste a
`Partner_Engagement__c`/Account/Opportunity ID. It's read-only and entirely optional:
decline and nothing changes; any field it can't supply falls through to web research
and clarifying questions.

**Per-user config.** The org alias is read from the `ORG62_ALIAS` env var in
`~/.claude/settings.json` (defaults to `org62`); the queried user is whoever is logged
into that alias — never hardcoded. Authenticate your own account with:
`sf org login web --alias org62 --instance-url https://org62.my.salesforce.com`.

Example `settings.json`:
\`\`\`json
{ "env": { "ORG62_ALIAS": "org62" } }
\`\`\`
```

- [ ] **Step 2: Add the equivalent section to pie-poc-forge README**

Append:

```markdown
## Optional: Org62 engagement pre-fill

pie-poc-forge can optionally pre-fill `requirements.json` from an Org62
`Partner_Engagement__c` (partner, pilot customer, opportunity use-case) instead of
relying only on pasted inputs. Pick from your active engagements or paste a
PE/Account/Opportunity ID. Read-only and optional; declining changes nothing.
The org alias comes from `ORG62_ALIAS` (default `org62`); identity is the logged-in
session user.
```

- [ ] **Step 3: Run both suites to confirm README doc-checks still pass**

Run:
```bash
cd ~/.claude/skills/pov-builder && python3 tests/validate_skill.py 2>&1 | tail -5
cd ~/.claude/skills/pie-poc-forge && python3 tests/validate_skill.py 2>&1 | tail -5
```
Expected: both PASS.

- [ ] **Step 4: Commit both**

```bash
cd ~/.claude/skills/pov-builder && git add README.md && git commit -m "docs: document optional Org62 engagement pre-fill + ORG62_ALIAS

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
cd ~/.claude/skills/pie-poc-forge && git add README.md && git commit -m "docs: document optional Org62 engagement pre-fill + ORG62_ALIAS

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: Wire `ORG62_ALIAS` into settings via the update-config skill

**Files:**
- Modify: `~/.claude/settings.json` (via the `update-config` skill — do not hand-edit if the skill is available)

- [ ] **Step 1: Add the env var through update-config**

Invoke the `update-config` skill to set `env.ORG62_ALIAS = "org62"` in `~/.claude/settings.json`. (It owns settings.json and validates against the harness schema — per Task 1, `env` is the accepted home for this.) If `update-config` is unavailable, add it manually and validate the JSON parses.

- [ ] **Step 2: Verify it reads back**

Run:
```bash
python3 -c "import json; d=json.load(open('$HOME/.claude/settings.json')); print('ORG62_ALIAS =', d.get('env',{}).get('ORG62_ALIAS'))"
```
Expected: `ORG62_ALIAS = org62`.

- [ ] **Step 3: No commit** (settings.json is user config, typically gitignored / outside the skill repos).

---

## Task 10: End-to-end smoke test (read-only, against live Org62)

**Files:**
- Inspect only

- [ ] **Step 1: List-path smoke — owned engagements resolve**

Run:
```bash
ALIAS="${ORG62_ALIAS:-org62}"
USER=$(sf org display --target-org "$ALIAS" --json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['username'])")
echo "session user: $USER"
sf data query --target-org "$ALIAS" --query "SELECT Id, Name, Project_Status__c FROM Partner_Engagement__c WHERE RecordTypeId = '0123y0000022rMkAAI' AND OwnerId IN (SELECT Id FROM User WHERE Username = '$USER') AND Project_Status__c IN ('Not Started','In Progress','On Hold') ORDER BY Name" 2>&1 | head -20
```
Expected: prints the logged-in user, then a table of that user's active engagements (or "No records" — which is a valid, non-fatal outcome per the optionality contract).

- [ ] **Step 2: Hydration smoke — pick one Id and run the full SELECT**

Run (substitute a real PE Id from Step 1):
```bash
ALIAS="${ORG62_ALIAS:-org62}"
PE_ID="<paste-a-PE-id-from-step-1>"
sf data query --target-org "$ALIAS" --query "SELECT Name, Account__r.Name, Account__r.RecordType.DeveloperName, Customer_Account_Lookup__r.Name, Opportunity__r.Name, Opportunity__r.StageName, Customer_Story__r.Name FROM Partner_Engagement__c WHERE Id = '$PE_ID'" 2>&1 | head -20
```
Expected: the engagement hydrates; the partner account's RecordType DeveloperName prints (so §6 role-mapping has its input); blank lookups simply show empty — confirming graceful fall-through.

- [ ] **Step 3: No commit.** Report results to the user; if the schema or RT id differs from the spec, open a follow-up rather than silently patching.

---

## Self-Review

**Spec coverage:**
- Optionality contract → module §0 (Task 2) + validator assertion (Task 4). ✓
- Shared module, both skills → Tasks 2/3 (pov-builder) + Task 5 (pie-poc-forge) + Task 7 parity. ✓
- List-first / any-ID fallback / key-prefix detection → module §3 (Task 2). ✓
- Account/Opp→PE normalization with 0/1/many → module §4. ✓
- Hydration SOQL traversing lookups → module §5, smoke-tested Task 10. ✓
- RT-aware informational role mapping (Partner vs Direct/other; no single customer RT) → module §6. ✓
- Per-user identity from session + `ORG62_ALIAS` from settings → module §1, Tasks 1/9, READMEs Task 8. ✓
- Read-only guarantee → enforced by `t_org62_prefill` (Tasks 4/6) incl. mutation test. ✓
- Verified Org62 facts (RT ids, lookups) → confirmed live in Task 1 Step 2 before build. ✓
- Auth re-login is per-user and non-fatal → module §1. ✓

**Placeholder scan:** No "TBD/TODO". The only intentional fill-ins are `<session-username>` (resolved at runtime, shown in Task 10), `<paste-a-PE-id>` (manual smoke input), and the PE key-prefix (module §3 instructs confirming the exact 3-char prefix from a real Id — flagged, not hidden).

**Type/name consistency:** Field API names (`Account__c`, `Customer_Account_Lookup__c`, `Opportunity__c`, `Customer_Story__c`, `Partnership__c`, `Customer_Account_Name__c`), RT ids (`0123y0000022rMkAAI` PE-GTP, `01230000000A5JxAAK` Account-Partner), env var `ORG62_ALIAS`, and check name `t_org62_prefill` are used identically across all tasks and match the spec's verified-facts table.

**No open items.** The `Partner_Engagement__c` key prefix was confirmed live as `a26` (Org62, 2026-06-15) and pinned into module §3 (Task 2). `<session-username>` and `<paste-a-PE-id>` remain intentional runtime/manual values, not unknowns.
