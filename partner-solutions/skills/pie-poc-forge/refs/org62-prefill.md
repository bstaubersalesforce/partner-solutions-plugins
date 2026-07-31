# Org62 Engagement Pre-fill Reference

> Lazily loaded. Load this only when Org62 enrichment is in play — i.e. the user accepted the Stage-1 offer to pull from an engagement, OR named/pasted a record ID. If the user declines, do not load this file; the flow is unchanged.

This file owns all Org62 pre-fill logic. `SKILL.md` carries only a thin Stage-1 hook (offer + load). Org62 is **optional enrichment**: nothing it returns is ever required (see the Optionality contract). It is read-only — `sf data query` / `sf org display` only, never DML or deploy. Org62 is production; honor the workspace guardrails.

## 0. Optionality contract (load-bearing)

1. **No anchor is valid** — user can skip entirely; the skill runs on its normal inputs.
2. **A partial anchor is valid** — only an Account, only an Opp, or only a status all hydrate whatever exists; missing records never stop the flow.
3. **A failed/empty pull is valid** — expired auth, no match, blank lookups all return whatever was retrieved (possibly nothing) and proceed.

Every blank field below renders as `—` and falls through to the skill's existing web-research / ask behavior.

## 1. Identity & config (per-user — never hardcode a username)

- **Alias** comes from the `ORG62_ALIAS` env var (set in `~/.claude/settings.json` under `env`), defaulting to `org62` when unset (if `$ORG62_ALIAS` is unset, use `org62` as the alias).
- **Username is discovered at runtime**, never hardcoded: `sf org display --target-org $ORG62_ALIAS --json` → `result.username`. Whoever is logged in is the user queried.
- **Expired/absent session** → tell the user to authenticate THEIR OWN account:
  `! sf org login web --alias $ORG62_ALIAS --instance-url https://org62.my.salesforce.com`
  Non-fatal: if they decline, proceed on normal inputs (contract §3).

## 2. Offer (Stage 1, the only thing SKILL.md triggers)

A single capability-style offer, not a stall: "Want to pull context from an Org62 engagement, or start fresh?" Decline → do not load further; flow unchanged.

## 3. Entry — list-first, any-ID fallback (NEVER fuzzy search)

- **Default (list):** resolve the current username (§1), then list that user's active engagements:
  `sf data query --target-org $ORG62_ALIAS --query "SELECT Id, Name, Project_Status__c, Customer_Account_Name__c FROM Partner_Engagement__c WHERE RecordTypeId = '0123y0000022rMkAAI' AND OwnerId IN (SELECT Id FROM User WHERE Username = '<session-username>') AND Project_Status__c IN ('Not Started','In Progress','On Hold') ORDER BY Project_Status__c, Name"`
  > Replace `<session-username>` with the username resolved in §1 before running (SOQL has no client-side bind var here — compose the literal string).
  Present as a numbered list; the user picks one. (GTP RecordType id `0123y0000022rMkAAI`.)
- **Fallback (any ID):** user pastes a 15/18-char Id. Detect type by key prefix:
  - `a26` → `Partner_Engagement__c` (confirmed live in Org62, 2026-06-15).
  - `001` → Account. `006` → Opportunity.
  - Unrecognized prefix → tell the user the expected prefixes; let them re-enter or skip.

## 4. Normalize an Account/Opportunity anchor to its PE

- **PE id** → use directly.
- **Account id** → `SELECT Id FROM Partner_Engagement__c WHERE Account__c = :id OR Customer_Account_Lookup__c = :id`
  - 0 rows → hydrate the Account directly: `SELECT Name, Industry, Website, RecordType.DeveloperName FROM Account WHERE Id = :id`. Emit the §7 block with the partner fields filled and PE/Opportunity/Customer Story shown as `—`.
  - 1 row → use it. Many → list them, user picks.
- **Opportunity id** → `SELECT Id FROM Partner_Engagement__c WHERE Opportunity__c = :id`
  - 0 rows → hydrate the Opportunity directly: `SELECT Name, StageName, Amount, CloseDate, Description FROM Opportunity WHERE Id = :id`. Emit §7 with the opportunity fields filled and partner/customer as `—`.
  - 1 row → use it. Many → list them, user picks.

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
- There is NO single "Customer" Account RecordType — do not match one; customer = any non-Partner account in the lookup (including accounts with no RecordType).

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

- **tech-strat-pov-forge:** fold populated fields into the Stage-2 pre-fill alongside web/Slack, tagged `[from Org62 engagement — confirm]`. Blanks become Stage-3 questions as today.
- **pie-poc-forge:** map fields into `requirements.json` (partner, pilot customer, use-case); blanks stay unset for the normal intake to fill.

## 9. Provenance

Record in the host's provenance section: the PE Id + Name used, which lookups resolved, and a note that values are `[from Org62 — confirm]` (never hardened without confirmation). e.g. "Org62: PE a26... '<engagement name>' — Account ✓, Opportunity ✓, Customer Story —."
