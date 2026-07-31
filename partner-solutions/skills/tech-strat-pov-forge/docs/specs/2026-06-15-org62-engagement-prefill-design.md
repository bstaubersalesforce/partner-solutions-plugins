# Org62 Engagement Pre-fill — Design

**Date:** 2026-06-15
**Status:** Approved design, pending spec review
**Skills affected:** `pov-builder`, `pie-poc-forge` (shared module; `team-projects` is a future potential consumer)

---

## Optionality contract (load-bearing — read first)

The entire Org62 pull is **optional enrichment**. Nothing it returns is ever required, individually or collectively. Implementation MUST honor all three rules:

1. **No anchor is valid.** The user can skip the list and skip the ID and run the skill exactly as today (web-research + ask). The Org62 step is an *offer*, not a gate.
2. **A partial anchor is valid.** A record with only an Account, only an Opportunity, only a status — or any combination — hydrates whatever exists. Missing Account / Opportunity / Project never stops the flow.
3. **A failed or empty pull is valid.** Expired auth, no matching engagement, a deleted lookup, or an early-stage record with nothing populated all return whatever was retrieved (possibly nothing) and the skill proceeds on its normal inputs.

The dependency is strictly **additive**: best case it pre-fills several fields and saves typing; worst case it contributes zero and the user is no worse off than today. Every blank field falls through to the skill's existing web-research / ask behavior.

---

## Goal

Let pov-builder and pie-poc-forge optionally hydrate their intake from an existing Org62 `Partner_Engagement__c` record — partner identity, pilot customer, opportunity use-case, and a linked customer story — instead of (or in addition to) web research and manual entry. Anchored deterministically (list-pick or exact ID), never fuzzy search.

## Non-goals

- No writes to Org62 — read-only (`sf data query`) throughout.
- No fuzzy/keyword search of engagements (deterministic anchors only).
- Does not replace web research or clarifying questions — it is a pre-fill layer in front of them.
- No new auth mechanism — reuses the configured org alias and existing login flow.
- Per-user, not per-machine — identity is resolved from the logged-in session, never a hardcoded username.

---

## Architecture

A **shared ref module**, `refs/org62-prefill.md`, defines the resolution + hydration procedure and the normalized output contract. Both skills invoke it and fold its output into their existing intake:

- **pov-builder** → Stage-2 pre-fill (partner context, pilot customer, commercial signals).
- **pie-poc-forge** → `requirements.json` normalization.

A single module (vs. duplicated logic per skill) keeps the SOQL, key-prefix detection, and role mapping in one place. `team-projects` can consume the same engagement-context contract later for free.

### Flow

```
1. ENTRY (offered, never forced)
   ├─ Default: run team-projects' owned-by-me PE query → numbered list → user picks one
   ├─ Fallback: user pastes any 15/18-char ID
   │     key-prefix detect:  a0x… = Partner_Engagement__c
   │                         001  = Account
   │                         006  = Opportunity
   └─ Skip: user declines → skill runs on normal inputs (web research + ask)

2. NORMALIZE TO A PE (or accept a bare anchor)
   ├─ PE id          → use directly
   ├─ Account id     → query PE WHERE Account__c = :id OR Customer_Account_Lookup__c = :id
   │                    0 matches → anchor on the Account alone
   │                    many      → list them, user picks
   └─ Opportunity id → query PE WHERE Opportunity__c = :id  (same 0 / many handling)

3. HYDRATE (one SOQL on the PE, traversing lookups)
   SELECT Name, Project_Status__c, Project_Type__c, Customer_Account_Name__c,
          Account__r.Name, Account__r.Industry, Account__r.Website, Account__r.RecordType.DeveloperName,
          Customer_Account_Lookup__r.Name, Customer_Account_Lookup__r.RecordType.DeveloperName,
          Opportunity__r.Name, Opportunity__r.StageName, Opportunity__r.Amount,
          Opportunity__r.CloseDate, Opportunity__r.Description,
          Customer_Story__r.Name, Owner.Name
   FROM Partner_Engagement__c WHERE Id = :peId

4. EMIT engagement-context block. Every blank field → "—" → falls through to ask/web-research.
```

### Emitted engagement-context block (shape)

```
PARTNER (POV subject)   : {Account__r.Name}   [Partner ✓ | Direct/other (exploring partnership)]
  industry / website    : {Account__r.Industry} / {Account__r.Website}
PILOT CUSTOMER (proof)  : {Customer_Account_Lookup__r.Name}   (or text fallback, or —)
OPPORTUNITY             : {Opp.Name} · {StageName} · {Amount} · {CloseDate}
  use-case              : {Opp.Description}
CUSTOMER STORY          : {Customer_Story__r.Name}   (or —)
ENGAGEMENT              : {Name} · {Project_Type__c} · {Project_Status__c} · owner {Owner.Name}
```

---

## Role mapping (RecordType-aware, informational only)

- **POV subject = `Account__c`** ("Partner Account" lookup).
  - RT = `Partner` → label "Partner ✓".
  - RT = anything else → label "Direct/other account (exploring partnership)". This is a **legitimate** case (a direct customer exploring a partnership), not an error — informational label only, never a warning or gate.
- **Pilot customer = `Customer_Account_Lookup__r`** (any RT) → emitted as a proof point ("partner is already piloting with {customer}"). Blank → text fallback → "—".
- **Fallback label** when the partner lookup is empty: `Customer_Account_Name__c` (text).

---

## Verified Org62 facts (confirmed live 2026-06-15)

Lookups on `Partner_Engagement__c` (all real `reference` fields):

| Field | → references | Role |
|---|---|---|
| `Account__c` ("Partner Account") | Account | POV subject (partner) |
| `Customer_Account_Lookup__c` ("Customer Account Lookup") | Account | Pilot customer / proof point |
| `Opportunity__c` | Opportunity | Use-case, stage, amount, close |
| `Customer_Story__c` | Customer_Story__c | Reference case study |
| `Partnership__c` | Alliance_Enrollment__c | Alliance/partnership record |
| `Customer_Account_Name__c` (text) | — | Customer-name fallback label |

- `Auto_created_from_Opportunity__c` (boolean) exists → some PEs are born from an Opp, so the Opp link is frequently populated.
- **Account `Partner` RecordType:** `01230000000A5JxAAK` (DeveloperName `Partner`).
- **No single "Customer" Account RecordType** — end customers span `Sales`, `Global_Headquarters`, `Global_Ultimate`, `B2C`, etc. Therefore "pilot customer" = any non-Partner Account in the customer lookup; do NOT match on a single customer RT.
- **PE GTP RecordType:** `0123y0000022rMkAAI` (used by `team-projects` for the owned-by-me list query).

---

## Auth & safety

The module is **per-user** — it must never assume a specific person's identity. Org identity comes from Claude settings, not a hardcoded username.

- **Config source.** Read the org alias (and, where needed, the authenticated username) from Claude `settings.json` rather than baking in a literal. Proposed key:
  ```json
  { "env": { "ORG62_ALIAS": "org62" } }
  ```
  The module resolves the alias from `ORG62_ALIAS`, defaulting to `org62` only if unset. The **username is never hardcoded** — it is discovered at runtime from the alias's own authenticated session (`sf org display --target-org $ORG62_ALIAS`), so whichever user is logged in is the user queried.
- **Owned-by-me list query.** The `team-projects`-style "engagements owned by me" query must derive the current user from the live session (e.g. resolve the username via `sf org display`, then filter `OwnerId`), NOT from a literal `bstauber@salesforce.com`. Each user sees their own engagements.
- **Re-auth.** On expired/absent session, direct the user to authenticate **their own** account:
  `! sf org login web --alias $ORG62_ALIAS --instance-url https://org62.my.salesforce.com`
- Read-only: `sf data query` / `sf org display` only. The module never deploys, updates, or deletes. (Org62 is production — see workspace guardrails.)
- Auth failure is non-fatal per the optionality contract: surface the re-auth hint, then proceed on normal inputs if the user declines.

> Settings wiring is done via the `update-config` skill (owner of `settings.json`). The default `ORG62_ALIAS=org62` works for the current machine with no config change; the key exists so other users can point at their own alias.

---

## Error / edge handling

| Situation | Behavior |
|---|---|
| User declines the Org62 offer | Skip silently; normal skill flow. |
| Expired / no auth | Show re-auth hint; non-fatal; proceed on normal inputs. |
| ID prefix unrecognized | Tell the user the expected prefixes; let them re-enter or skip. |
| Account/Opp id → 0 PEs | Anchor on the bare record; hydrate what that record offers. |
| Account/Opp id → many PEs | List the matches; user picks one. |
| PE found, lookups blank | Hydrate populated fields only; blanks → "—" → fall through. |
| Subject Account RT ≠ Partner | Label "Direct/other (exploring partnership)"; proceed normally. |

---

## Testing

- **Key-prefix detection:** `a0x…`→PE, `001…`→Account, `006…`→Opportunity, unknown→graceful prompt.
- **Resolution fan-out:** Account/Opp id resolving to 0 / 1 / many PEs each take the correct branch.
- **Optionality:** skill completes end-to-end with (a) no anchor, (b) a PE with only a status and no lookups, (c) a simulated auth failure — none halt.
- **Role mapping:** Partner-RT account labels "Partner ✓"; non-Partner labels "Direct/other"; blank partner lookup falls back to `Customer_Account_Name__c`.
- **Read-only assertion:** the module issues only `sf data query` / `sf org display` — no deploy/DML commands.
- **Per-user identity:** with `ORG62_ALIAS` unset the alias defaults to `org62`; with it set, the module targets that alias. The owned-by-me list filters on the *session's* username (from `sf org display`), not a literal — a different logged-in user sees their own engagements.

---

## Open items for spec review

- Spec location: saved under `pov-builder/docs/specs/` (no git repo in workspace, so no commit step).
- Whether the shared module physically lives in `pov-builder/refs/` and is referenced by `pie-poc-forge`, or in a neutral shared location both point to. (Default: author in `pov-builder/refs/org62-prefill.md`; pie-poc-forge references it by path.)
