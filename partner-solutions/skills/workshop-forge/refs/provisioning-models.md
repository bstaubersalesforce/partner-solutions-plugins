# Provisioning Models — Decision Guide

A reusable framework for determining whether a Salesforce partner workshop needs participant orgs, and if so, which org model and operational shape. Extracted from battle-tested kits (`data360-workshop`, `headless360-workshop`, `ncino-workshop`) — this is the IP that workshop-forge reasons from.

## `provisioning.model` enum (single source of truth)

Valid values for `kit.json.provisioning.model`:

| Value | Meaning |
|-------|---------|
| `none` | No participant orgs (`needs_org:false`) — conceptual / educate-only / shared-backend. |
| `de-per-team` | One free Developer Edition per team (Agentforce-centric). |
| `sdo-per-team` | One SDO (Enterprise) per team (Data-Cloud-connector-centric). |
| `assigned-preconfigured` | Pre-baked orgs handed out as aliases (managed-package / multi-cloud). |
| `scratch-pool` | Scratch-org pool + snapshot (facilitator/CI; not for participants). |
| `tiered-fallback` | ⚠️ Recognized vocabulary, **not yet scaffolded** — a sequenced fallback (partner org → facilitator pool → shared reference). Deferred; documented so the enum is complete. |

Other refs (`kit-anatomy.md`, `README.md`) reference this table rather than re-listing it.

## The three-step method

### Step 1: Does the workshop need participant orgs at all?

**`needs_org: false` is a first-class outcome** — not degraded, not a fallback. Many effective activations run entirely org-free.

**Conceptual / educate-only workshops are the canonical `needs_org:false` case.** When org shape is
lower-priority (the workshop teaches concepts, patterns, or architecture rather than hands-on
build), set `needs_org:false` and `model:"none"`; note in `docs/org-provisioning.md`'s absence that
this is deliberate, not a gap.

Ask: **"What are participants physically doing during hands-on time?"**

| Pattern | `needs_org` | Why |
|---------|-------------|-----|
| **Educate-only** — slideware, demos, Q&A, conceptual walkthroughs | `false` | No hands-on build; participants consume, not create |
| **Facilitator-driven demo** — live demo from one reference org; participants observe | `false` | One facilitator org suffices; no per-team isolation needed |
| **Shared hosted backend** — participants call a centralized service (API, MCP Worker, pre-deployed agent) via web/Slack/CLI | `false` | The *backend* is org-backed, but participants hit it as clients (nCino's shared MCP Worker model) |
| **Hands-on build** — participants author metadata, deploy code, configure agents, wire integrations | `true` | Needs data isolation + "you built it" agency → Step 2 |

**Outcome:** if `false`, skip org-provisioning doc, deploy scripts, tier keys, preflight checks — the kit renders conditionally. If `true` → Step 2.

---

### Step 2: Feature-dependency → org-type heuristic

When hands-on participant orgs are required, the **load-bearing features** dictate the org type. No single type fits every workshop; reason from the requirements.

| Required features | Recommended model | Why | Gotchas |
|-------------------|-------------------|-----|---------|
| **Agentforce-centric, no hard Data Cloud dependency** | **Developer Edition (free, with Agentforce + Data 360)**, one per team | Officially modeled (Salesforce's own "Try Headless 360" workshop uses self-provisioned DE); free; ships Agentforce + Data Cloud pre-provisioned; Hosted MCP went GA on DE Apr 2026; no internal pipeline dependency | DE deprovisions after ~45 days idle — provision close to the date + keep active; the ECA/PKCE/JWT MCP setup is **never auto-provisioned** (per-org scripted step required; assume not pre-enabled and verify — see Step 3); ⚠️ unverified whether free DE includes `mcp_api` scope out of the box or requires per-org enablement (confirm pre-event) |
| **Data Cloud connectors load-bearing** (S3, GCS, Redshift, BigQuery Zero Copy) | **SDO (Enterprise)**, one per team | Trial/DE Data Cloud *connectors* were unreliable in the data360-workshop experience (~May 2026 — trial orgs couldn't authenticate to S3/GCS; only SDO + the BRIX Data Cloud setup worked); ⚠️ as of mid-2026; re-verify at workshop time whether this remains true for free DE or if connector reliability improved | Depends on an SDO/AE provisioning channel; heavier than needed for Agentforce-only stacks |
| **Managed package + multi-cloud pre-enabled** (FSC, Health Cloud, nCino) | **Assigned pre-configured orgs**, one per team | Can't stand up managed-package + multi-cloud stacks quickly per-team morning-of; pre-bake and hand out as aliases | Still needs a provisioning source (PBO/AE); per-org setup script required (assign permsets, load sample data) |
| **Reproducible/disposable, features scratch-viable** (LWC, Apex, simple flows) | **Scratch-org pool + snapshot** (def file → snapshot → dispenser) | Version-controlled, reproducible, disposable; great for facilitator dev/CI of the reference build | **Not for participants** — Agentforce/Einstein + Data Cloud *can* be enabled, but Hosted MCP/Slack-connect/Agent-API on scratch are unverified; snapshots exclude connected apps / external & named credentials → OAuth ECA can't be pre-baked; Data Cloud on scratch needs a PBO Dev-Hub Partner-Community case; bounded by Dev Hub `ActiveScratchOrgs`/`DailyScratchOrgs` limits |
| **Simple stack, no data isolation needed** (conceptual, low contention) | **Shared org + per-user permission sets** | One org to provision & verify; simplest ops | No data isolation; contention on shared agent/MCP config; weak "you built it" story — **contingency only** |

**Reasoning discipline:** pick the *lightest viable* model (free DE over SDO if Data Cloud connectors aren't load-bearing), then **reason to a recommendation and flag residual confirmations** — don't just list options. Example from headless360: "DE is recommended for this Agentforce-centric workshop (no hard Data Cloud dependency), superseding the kit's original SDO assumption. Three residual confirmations remain: (1) does the free DE include Hosted MCP + `mcp_api` scope out of the box? (2) can we provision 4–8 DE orgs cleanly for one event? (3) does an SDO template offer a genuinely faster pre-baked path for *this exact* stack?"

**Uncertainty discipline:** since the ref's own Step 3 preaches "flag residual confirmations," the ref must **practice it** — any claim sourced from an unverified or time-bounded datapoint gets an explicit uncertainty flag (⚠️ "unverified: …" or "as of <date>; re-verify"). Keep verified claims firm; flag the specific unverified bits.

**Outcome:** set `kit.json.provisioning.model` to match; author `docs/org-provisioning.md` with the chosen model + its rationale + residual confirmations.

---

### Step 3: Universal operational rules (every org-backed model)

These apply **regardless of org type** — distilled from three mature kits' battle scars.

#### Rule 1: Pre-provision + preflight T-minus days, never morning-of

**Morning-of provisioning failure is the #1 engagement killer.** Provision orgs **T-minus 5+ business days**, gate every org through a preflight check (run `00-preflight.sh --org <alias>` from the generated kit's scripts directory, stamped from `templates/scripts/00-preflight.sh.tmpl`) **T-minus 3 business days**, and smoke-test the real flow (not just the green status dot — async half-states are invisible to UI checks).

For orgs that deprovision after idle (DE ~45 days), provision close to the date and keep them active (weekly preflight re-runs work).

**Workshop-morning checklist = aliases, not provisioning.**

#### Rule 2: Keep a safety-net reference org

A fully-built, pre-verified **reference org** rescues any team whose participant org stalls (deploy conflict, orphaned metadata, OAuth misconfiguration). The facilitator can demo from it or hand it out as a shared fallback.

This org also serves as the **golden source** for preflight validation — "if it works here, the issue is participant-org-specific."

#### Rule 3: Per-org ECA/PKCE/JWT MCP setup is never auto-provisioned

**No org type auto-provisions the External Client App (ECA) + PKCE + JWT config for Hosted MCP.** This is always a **scripted per-org setup step** after provisioning. Snapshots exclude connected apps / external & named credentials; SDO templates don't pre-bake OAuth client secrets; DE doesn't ship the ECA.

**Generate a setup helper** (named `04-mcp-connect-setup.sh` in the generated kit — not yet a template) that (a) deploys preparatory metadata (permsets, custom settings), (b) checks org edition/LEX, and (c) either fully automates the ECA (`ExternalClientApplication` metadata + `ConnectedApp` OAuth settings for `mcp_api` + JWT toggle — if the API supports it) or prints an **exact-values ECA card** for the facilitator to manually create.

The per-org MCP setup is also a **teaching moment** (Module 2 in most kits) — participants see how OAuth/PKCE/JWT wiring works, not just the finished state.

#### Rule 4: Smoke-test the real flow, not the status dot

A green "Connected" indicator in Setup does not prove the integration works. Smoke-test the **actual end-to-end flow** (invoke the agent, call the MCP tool, see the data flow back) on the preflight org and on one participant org pre-workshop.

**Async half-states are invisible:** an orphaned `AiAuthoringBundle` reserving a Bot DeveloperName, a stalled Einstein enablement, a half-deployed flow — none show as errors until you try to use them. Only `sf org list metadata --metadata-type <Type>` reveals orphans; only a live invocation reveals runtime failures.

#### Rule 5: Pre-stage the orphaned-metadata fix

A partial/interrupted first deploy leaves **invisible orphan metadata** (e.g., an orphaned `AiAuthoringBundle` reserving a Bot DeveloperName) that blocks the real deploy. Only `sf org list metadata --metadata-type AiAuthoringBundle` (and similar for `Bot`, `GenAiPlannerBundle`) reveals it.

Pre-stage the fix in the generated kit's common shell library (from `templates/scripts/lib/common.sh.tmpl`) — a reusable `check_orphaned_metadata()` function that scans for known orphan types and prints the delete command. It recurs for any team; make it a copy-paste remediation.

---

## Output contract

When workshop-forge reasons through this guide, it produces:

1. **A recommendation with rationale** — "provision one free DE per team (Option C), because this workshop is Agentforce-centric with no hard Data Cloud dependency, and DE is the officially-modeled path (Try Headless 360)."
2. **Residual confirmations flagged** — "three items remain before final lock: (1) …, (2) …, (3) …"
3. **Conditional kit rendering** — `kit.json.provisioning.needs_org` and `.model` set; org-provisioning doc, preflight validator, deploy/assign scripts (from `templates/docs/org-provisioning.md.tmpl` + `templates/scripts/*.sh.tmpl`) rendered iff `needs_org: true`; the generated kit validator asserts only the files rendered.
4. **Operational discipline baked in** — preflight timing, safety-net org, per-org MCP setup script, smoke-test checklist, orphan-metadata fix — documented in the generated org-provisioning doc and enforced by the generated preflight validator.

---

## Evidence base (for audit/update)

This guide distills three production kits:

- **data360-workshop** — SDO-per-team (3-tier fallback) because Data Cloud *connectors* break on trial/DE; scratch explicitly rejected for Data Cloud.
- **headless360-workshop** — free DE-per-team (Agentforce + Data 360) after deep-research (25/25 claims verified) ruled out scratch for participants (MCP/Slack/Agent-API unverified; ECA can't be snapshot-baked) and found DE is the officially-modeled path (Try Headless 360).
- **ncino-workshop** — pre-provisioned, pre-configured orgs assigned per team (managed package + multi-cloud can't be stood up quickly) + one shared hosted MCP backend (Cloudflare Worker) to remove per-team moving parts; scratch shipped only as an optional self-service rebuild, deliberately not the workshop path.

**Cross-cutting lessons:** morning-of provisioning kills the engagement; preflight T-minus 3 business days is non-negotiable; safety-net reference org rescues stalled teams; per-org ECA/PKCE/JWT is never auto-provisioned; async half-states are invisible to UI checks; orphaned metadata recurs.

When the pattern evolves (new org type, new Salesforce entitlement model, new MCP setup API), update this guide and re-sync the exemplar docs (headless360's `org-provisioning-options.md` is the living reference; data360's is the Data-Cloud-connector scar tissue).
