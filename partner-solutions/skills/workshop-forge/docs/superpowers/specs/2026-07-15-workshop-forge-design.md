# workshop-forge — Design Spec

**Date:** 2026-07-15
**Status:** Approved (brainstorming complete; plan next)
**Tier:** 3 (Platform) — multi-stage, router, multiple mutually-consistent outputs, ships deterministic `scripts/`.

## Purpose

A Tier-3 Claude skill that scaffolds and authors **Salesforce partner workshop kits** — extracting the
repeating pattern proven across three existing kits (`data360-workshop`, `headless360-workshop`,
`ncino-workshop`). It joins the `*-forge` family (pov-builder → pie-poc-forge → ps-npi-forge) as the
**enablement/activation** member: where pie-poc-forge builds the *what* (an installable PoC), workshop-forge
builds the *how-to-teach-it* (a multi-partner, hands-on activation kit).

**Why it's skill-worthy (rule of three):** the pattern has been hand-built three times. Evidence: data360 and
headless360 are near-isomorphic (same four top-level docs, `config/kit.json` overlay, `docs/` genres,
`scripts/` spine + `check.sh`, Module-0→7 / 🔴-checkpoint GUIDE convention); nCino is an earlier, flatter
instance **missing exactly the elements a scaffolder would add** (no `kit.json`, no `docs/`, no preflight, no
`check.sh`, no FACILITATOR) — evidence the template raises consistency rather than fighting the grain.

## Scope & decisions (confirmed in brainstorming)

1. **Two modes** (like skill-forge): **scaffold** (stamp the skeleton) and **author/enrich** (author content
   onto a scaffolded tree). Re-entrant: author updates, never regenerates from scratch.
2. **Author-mode inputs, priority order:** prefer an upstream **pie-poc-forge PoC package / pov-builder POV**
   if pointed at one; else **freeform** sources (brief, research notes, pasted requirements); else interview.
3. **Wrap, do not invent, the reference build.** Generating working Agentforce/SFDX metadata is
   pie-poc-forge's job. workshop-forge **imports/references** the reference build into `sfdx/`; it never
   regenerates agent metadata.
4. **Provisioning = a picker + decision guide, with "no org needed" as a first-class outcome.** Whether a
   workshop needs participant orgs at all is the *first* branch; org-type selection is a
   feature-dependency → org-type heuristic; universal operational rules apply to every org-backed model.
5. **Every generated kit carries its own self-validating `check.sh`** (matching the conditional shape it was
   rendered with). workshop-forge ships that `check.sh` as a **template** and **golden-file-tests the
   generator** (R-TEST-04: byte-equal fixtures + mutation-verified).
6. **workshop-forge itself is a full Tier-3 skill** — its own `tests/validate_skill.py`, pre-commit hook, CI,
   and spec+plan archive.

## Architecture (Approach 2 — deterministic scaffolder + prompt-authored content)

Clean split of two machineries:
- **`scripts/scaffold_kit.py`** owns deterministic *structure* (the skeleton + the generated `check.sh`) —
  reproducible, golden-file-tested.
- **`refs/*-flow.md`** prompt flows own intelligent *content* (module bodies, provisioning doc, framework /
  buildability / commercial docs) — source-grounded, uncertainty-flagged, in the family's advisor voice.

Author mode assumes a scaffolded tree exists (or tells the user to run scaffold first) — it does **not** run
the scaffolder. Keeps the two modes independent and independently testable (YAGNI).

### Skill file tree

```
~/.claude/skills/workshop-forge/
├── SKILL.md                      # router: overview, delivery voice, refusal/scope, mode detection
├── README.md                     # what it does + how to invoke
├── refs/
│   ├── kit-anatomy.md            # common skeleton vs per-engagement overlay (the templatizable core)
│   ├── scaffold-flow.md          # mode 1
│   ├── author-flow.md            # mode 2 (re-entrant)
│   ├── provisioning-models.md    # the picker + decision guide (incl. the "no org" branch)
│   ├── guide-conventions.md      # Module 0 Comprehend → Module N Extend, 🔴 checkpoints, Educate-First
│   ├── input-contract.md         # author-mode input detection (upstream artifact | freeform | interview)
│   └── kit-check-spec.md         # what the generated kit's check.sh must validate
├── templates/                    # the kit skeleton, rendered by scaffold_kit.py
│   ├── README.md.tmpl  GUIDE.md.tmpl  FACILITATOR.md.tmpl  LESSONS-LEARNED.md.tmpl
│   ├── kit.json.tmpl  env.example.tmpl  gitignore.tmpl
│   ├── docs/{org-provisioning.md.tmpl, framework.md.tmpl, buildability-matrix.md.tmpl}   # conditional
│   └── scripts/{lib/common.sh.tmpl, 00-preflight.sh.tmpl, deploy.sh.tmpl,
│                assign-perms.sh.tmpl, check.sh.tmpl}
├── scripts/scaffold_kit.py       # deterministic renderer (overlay → skeleton); the tested core
├── tests/
│   ├── validate_skill.py         # Tier-3 structural + router-parity suite
│   └── fixtures/                 # golden kits: one needs_org:true (full), one needs_org:false (educate-only)
├── docs/superpowers/{specs,plans}/
├── .githooks/pre-commit
└── .github/workflows/validate.yml
```

## The overlay — `config/kit.json` (single source of truth)

The scaffolder reads it to render; author mode reads it to know what to write.

```jsonc
{
  "name": "headless360",
  "title": "Headless 360 Partner Activation Workshop",
  "mode": "lab",                      // "lab" (multi-partner) | "engagement" (1:1)
  "duration": "2-day",
  "partner_overlay": "reference",     // "reference" (neutral) | "<partner>" (retargeted reskin)
  "surfaces": { "slack": true, "react_agent_api": true, "clt_lex": true, "mobile": false },
  "provisioning": {
    "needs_org": true,                // false ⇒ skip org-provisioning doc + deploy scripts + tier keys
    "model": "de-per-team",           // de-per-team | sdo-per-team | tiered-fallback |
                                      // assigned-preconfigured | scratch-pool | none
    "required_features": ["Agentforce", "HostedMCP"]
  },
  "modules": [ /* ordered {n, title, checkpoint?:true}; Module 0 Comprehend … Module N Extend */ ],
  "content_dirs": { "slides": true, "commercial": true, "web": false, "showcase": false, "prework": false },
  "reference_build": { "source": "pie-poc-forge|freeform|none", "path": "sfdx/" }
}
```

### `scaffold_kit.py` behavior (deterministic, idempotent, no deletes)
1. Read `kit.json`; create the dir tree.
2. Always render: `README/GUIDE/FACILITATOR/LESSONS-LEARNED`, `.env.example`, `.gitignore`,
   `scripts/lib/common.sh` + numbered lifecycle scripts.
3. Conditionally render: `docs/org-provisioning.md` + deploy/assign scripts + preflight org-reminders **iff
   `needs_org`**; `slides/`,`commercial/`,`web/`,`showcase/`,`prework/` per `content_dirs`; `sfdx/`
   placeholder per `reference_build`.
4. **Generate the kit's own `check.sh`** enumerating exactly the files rendered — so the harness matches the
   conditional shape (no org ⇒ no org-doc assertion).
5. Stamp GUIDE with the `modules[]` arc + 🔴 markers where `checkpoint:true`; module bodies are stubs for
   author mode.

## Mode flows

### Mode detection (SKILL.md)
"scaffold / new kit / stamp" → scaffold flow; "author / enrich / fill / write modules" → author flow;
ambiguous → ask.

### Scaffold mode (`refs/scaffold-flow.md`)
1. Intake overlay conversationally (one question only where not inferable).
2. **Refuse if `<kit-name>/` already exists** — never overwrite; ask for a new name.
3. Write `config/kit.json`; run `scaffold_kit.py`.
4. Run the generated kit's `check.sh` → must be green.
5. Handoff: tree + "run author mode to fill content."

### Author/enrich mode (`refs/author-flow.md`) — re-entrant
1. **Detect input** (`input-contract.md`): upstream pie-poc-forge/pov-builder artifact | freeform | interview.
2. **Wrap the reference build** into `sfdx/` — import, never regenerate metadata.
3. **Author onto the scaffolded tree:** GUIDE module bodies (`guide-conventions.md`), the provisioning doc
   (decision guide), framework + buildability-matrix docs, `commercial/` talk-track, `slides/` outline —
   source-grounded, uncertainty-flagged.
4. Re-run `check.sh` (links resolve, no orphaned refs).
5. Handoff: authored vs stubbed vs residual gaps.

## Provisioning decision guide (`refs/provisioning-models.md`) — the reusable IP

**Step 1 — gating branch: does it need participant orgs at all?** Educate-only / facilitator-demo /
shared-hosted-backend (nCino's shared MCP Worker) → `needs_org:false` (a first-class outcome, not degraded).
Else → Step 2.

**Step 2 — feature-dependency → org-type heuristic:**
| Required features | Recommended model | Why |
|---|---|---|
| Agentforce-centric, no hard Data Cloud | free **DE w/ Agentforce + Data 360**, one per team | officially modeled (Try Headless 360); free; no pipeline dependency |
| Data Cloud connectors load-bearing | **SDO (Enterprise)**, one per team | trial/DE Data-Cloud connectors unreliable (data360 scar) |
| Managed package + multi-cloud pre-enabled | **assigned pre-configured org** | can't stand up per-team quickly (nCino) |
| Reproducible/disposable, features scratch-viable | **scratch pool + snapshot** | but ECA/OAuth can't be snapshot-baked; Dev-Hub limits |

**Step 3 — universal rules (every org-backed model):** pre-provision + preflight **T-minus days, never
morning-of**; keep a **safety-net reference org**; the **per-org ECA/PKCE/JWT MCP step is never
auto-provisioned** (generate a `04-*-setup.sh`-style helper); **smoke-test the real flow**, not the status dot.

**Output:** pick a model, write the matching `docs/org-provisioning.md`, set the `kit.json` provisioning keys,
and flag residual confirmations — *reason to a recommendation*, don't just list options.

## Testing & validation (two layers)

**Layer 1 — Tier-3 suite (`tests/validate_skill.py`, stdlib-only):** R-FM-01, R-REF-01, R-ARCH-01/02/03,
R-TEST-01/02/03, R-TEST-04, R-CI-01, R-CI-02, R-PROC-01, R-DOC-01 (from skill-forge's check-library).

**Layer 2 — golden-file test of the generator (R-TEST-04):** `scripts/scaffold_kit.py` is deterministic, so
the suite EXERCISES it:
- **Fixtures** (`tests/fixtures/`): two `kit.json` inputs spanning the axis — one `needs_org:true` full
  multi-surface kit, one `needs_org:false` Educate-only kit — each with its expected rendered tree.
- **Test:** load the scaffolder as a module, render each fixture to a temp dir, assert **byte-equal** against
  the golden tree — including that the generated `check.sh` differs correctly between org / no-org cases.
- **Mutation-verify** (manual discipline): break the scaffolder, watch the golden test fail, restore.
- **Meta-check:** run each golden kit's own `check.sh` in-test; must be green (we validate what the skill
  generates is itself valid).

## Family relationship

- **pov-builder** → strategic POV/narrative.
- **pie-poc-forge** → installable PoC SFDX package (+ execution/config/gaps canvas).
- **ps-npi-forge** → NPI artifact family.
- **workshop-forge** (new) → multi-partner enablement/activation kit.

**Seam:** pie-poc-forge's reference build (SFDX package) becomes the `sfdx/force-app/` payload workshop-forge
wraps in modules + facilitation. Strengthens the open "package the Tier-3 `*-forge` skills as one plugin +
marketplace" decision — this would be the fourth member.

## Refusal / scope conditions (for SKILL.md)
- Not a workshop-kit request (neither scaffold nor author) → clarify.
- Scaffold: target dir already exists → refuse, ask for a new name.
- Author: no scaffolded tree present → direct to scaffold mode first.
- Asked to generate the reference-build **agent/SFDX metadata** → redirect to pie-poc-forge; workshop-forge
  wraps, does not invent, the reference build.
- Do not fabricate provisioning specifics that can't be verified — flag residual confirmations (the
  headless360 discipline).

## Non-goals (YAGNI)
- No mechanized prose generation (Approach 3 rejected — module content is judgment, not string interpolation).
- Author mode does not run the scaffolder.
- Does not create Salesforce orgs or run live deploys — it generates the kit that a human/facilitator runs.
- Does not generate agent/SFDX metadata (pie-poc-forge's job).
