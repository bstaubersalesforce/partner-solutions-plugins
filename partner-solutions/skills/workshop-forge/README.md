# workshop-forge

**Scaffolds and drafts Salesforce partner workshop kits** — the enablement/activation member of the `*-forge` skill family
(`tech-strat-pov-forge` → `pie-poc-forge` → `ps-npi-forge` → **`workshop-forge`**).

Where `pie-poc-forge` builds the *what* (an installable proof-of-concept), `workshop-forge` builds the *how-to-teach-it*:
a multi-partner, hands-on activation kit — GUIDE modules, a facilitator run-of-show, provisioning, scripts, and a
self-validating harness — from the pattern proven across the data360, headless360, and nCino workshop kits.

---

## When to use it

- You're standing up a **hands-on partner workshop or lab** around a Salesforce capability (Agentforce, Data Cloud, MCP, …)
  and want the kit skeleton + drafted content instead of hand-building it for the Nth time.
- You have an upstream **`pie-poc-forge` PoC** or **`tech-strat-pov-forge` POV** (or freeform source material) and want to wrap it in a
  teachable kit.

**Not for:** generating the agent/SFDX metadata itself (that's `pie-poc-forge` — this skill *wraps*, never invents, the
reference build), a strategy POV (`tech-strat-pov-forge`), or an NPI artifact family (`ps-npi-forge`).

**Also not for — lab *logistics*:** nominations, the Lab Registry, partner channels, and ISV Technical Briefs are owned
by the separate **PIE Lab Slack Skills** (Lab Creation / Nominee Sign-Up / Partner Onboarding). Those run the
operational lifecycle (Stages 1–4); workshop-forge produces the *content* the lab delivers (Stage 5). They hand off
cleanly — the onboarding skill's ISV Technical Brief is a ready author-mode input. See
[refs/lab-logistics-companion.md](./refs/lab-logistics-companion.md).

---

## Two modes

| Mode | What it does | Confidence |
|------|--------------|-----------|
| **Scaffold** | Stamps the kit skeleton from a `config/kit.json` overlay via `scripts/scaffold_kit.py`. Deterministic, idempotent, golden-file-tested. Emits a self-validating `check.sh` matching the kit's shape. | **Proven** (tested + dogfooded) |
| **Author / enrich** | Drafts module bodies, the provisioning doc, and commercial/slides content onto a scaffolded tree, grounded in upstream sources; flags what it inferred vs. sourced. **Re-entrant** — updates, never regenerates. | **Assistive** — drafts require human review before delivery |

The split is the point: **structure is deterministic; substance is source-grounded draft + human judgment.**

---

## Quick start

Invoke by describing the work — the skill routes on intent:

- *"Scaffold a workshop kit for a Data Cloud identity-resolution lab"* → **scaffold mode**
- *"Author the modules for the acme-datacloud kit from this pie-poc-forge PoC"* → **author mode**

### Scaffold, hands-on

1. Write a `config/kit.json` overlay (see below), then:
   ```bash
   python3 scripts/scaffold_kit.py path/to/kit.json ./my-kit
   ```
2. Verify the generated kit self-validates:
   ```bash
   cd my-kit && bash scripts/check.sh      # expect: ALL GREEN
   ```
3. Run **author mode** to draft the module bodies + provisioning doc onto the scaffold, then review before delivery.

---

## The overlay (`config/kit.json`)

The single source of truth — the scaffolder reads it to render; author mode reads it to know what to write.

```jsonc
{
  "name": "acme-datacloud",              // kit slug → dir/identifier (auto-slugged for safety)
  "title": "Acme Data Cloud Workshop",   // human title (markdown prose)
  "mode": "lab",                          // "lab" (multi-partner) | "engagement" (1:1)
  "duration": "2-day",
  "partner_overlay": "reference",         // "reference" (neutral) | "<partner>" (retargeted)
  "surfaces": { "slack": false, "react_agent_api": false },   // descriptive; {} = none by design, omit = TBD
  "provisioning": {
    "needs_org": true,                    // false ⇒ educate-only: no org doc / deploy scripts / org env keys
    "model": "sdo-per-team",              // enum owned by refs/provisioning-models.md (tiered-fallback = reserved, not yet scaffolded)
    "required_features": ["DataCloud"]    // drives the provisioning decision-guide reasoning
  },
  "modules": [                            // Module 0 "Comprehend" … Module N "Extend"
    { "n": 0, "title": "Comprehend" },
    { "n": 2, "title": "Model (DMO)", "checkpoint": true },       // 🔴 order-sensitive step
    { "n": 5, "title": "BYO Dataset", "modes": ["lab"] },         // lab-only; omitted in engagement kits
    { "n": 6, "title": "Agent Grounding", "optional": true },     // renders "(Optional)"
    { "n": 7, "title": "Extend" }
  ],
  "content_dirs": { "slides": true, "commercial": true },
  "reference_build": { "source": "pie-poc-forge", "path": "sfdx/", "sample_data_path": "data/" }
}
```

**Key behaviors:**
- **`needs_org: false` is first-class** — educate-only kits emit no org-provisioning doc, no deploy/assign scripts, and no
  `ORG_ALIAS`/`.env` org references. Not a degraded mode.
- **`surfaces` is descriptive** (drives narrative/module focus); **`content_dirs` controls emitted directories.** They're
  independent knobs.
- **Modules can be `optional`** (renders an `(Optional)` marker) or **mode-gated** (`modes:["lab"]`)
  so a module appears only in the matching workshop mode; the overlay still records every module.
- **`reference_build.sample_data_path`** — set it for kits that ship sample datasets; the scaffolder
  stamps a `data/` dir + README stub (data360-style kits ship dozens of data files).
- Values that reach generated shell scripts are **scrubbed/slugged** (no shell-metachar injection from a hand-authored overlay).
- Missing required fields (`name`/`title`/`mode`/`duration`, or a module's `n`/`title`) produce a **clear error**, not a traceback.

---

## What a generated kit contains

```
<kit>/
├── README.md  GUIDE.md  FACILITATOR.md  LESSONS-LEARNED.md   # top-level docs
├── config/kit.json                                           # the overlay, canonicalized
├── docs/framework.md  docs/buildability-matrix.md            # framework refs (author-filled)
│   └── docs/org-provisioning.md                              # only when needs_org
├── scripts/                                                  # lib/common.sh + preflight + (deploy/assign when needs_org)
│   └── check.sh                                              # self-validating harness (overlay-driven)
├── slides/ commercial/ …                                     # per content_dirs
└── sfdx/                                                     # reference-build payload (wrapped from pie-poc-forge)
```

GUIDE modules follow the **Module 0 "Comprehend" → Module N "Extend"** arc with **🔴 checkpoints** on order-sensitive /
silent-failure steps. Module *bodies* are drafted by author mode; the scaffolder stamps the headers + checkpoint markers.

## Anatomy of the output — what each piece is for

A generated kit is one coherent deliverable read by four audiences across the workshop lifecycle:

| Artifact | Audience | When it's used |
|----------|----------|----------------|
| `README.md` | everyone | first contact — what this is, who it's for, how to run |
| `docs/org-provisioning.md` | ops / facilitator | **T-minus 5+ days** — provision + preflight orgs (only for `needs_org` kits) |
| `scripts/` (`00-preflight` … `check.sh`) | ops / facilitator | T-minus prep + morning-of alias checks; `check.sh` validates kit shape |
| `FACILITATOR.md` | facilitator | prep + in-room — run-of-show, timing, fallbacks, demo reminders |
| `docs/framework.md`, `docs/buildability-matrix.md` | facilitator / partner-exec | prep + debrief — the teaching model and the paid-extension scoping story |
| `GUIDE.md` | participant | **in-room** — the hands-on Module 0→N arc with 🔴 checkpoints |
| `data/`, `sfdx/` | participant / facilitator | in-room — the sample data and reference build the modules operate on |
| `slides/`, `commercial/`, `showcase/` (per `content_dirs`) | facilitator / partner-exec | prep + delivery — decks and commercial framing |
| `LESSONS-LEARNED.md` | facilitator | **after** — retro: what to fix before the next run |

**How they compose:** provisioning + scripts stand up the environment before the room opens;
FACILITATOR + framework prime the facilitator; GUIDE (against `data/`/`sfdx/`) is what participants
actually do; slides/commercial wrap the business narrative; LESSONS-LEARNED closes the loop. For a
**conceptual / educate-only** kit (`needs_org:false`), the provisioning + scripts + `sfdx/` rows
drop out and the kit is GUIDE + slides + framework — a fully valid, non-degraded shape.

---

## The provisioning decision guide

The skill's reusable IP (`refs/provisioning-models.md`): reasons from **required features → org model**, with
`needs_org:false` as a first-class outcome. It correctly discriminates (verified across both dogfoods):
**Developer Edition** for Agentforce-centric kits, **SDO (Enterprise)** for Data-Cloud-connector-centric kits — and carries
⚠️ flags on claims still awaiting on-network confirmation.

---

## Validate

```bash
python3 tests/validate_skill.py     # Tier-3 rubric suite (13 checks)
python3 tests/test_scaffold.py      # golden-file + meta-check behavioral tests
```
Both run automatically via `.githooks/pre-commit` and CI (`.github/workflows/validate.yml`).

---

## Status & docs

- **Built, dogfooded (headless360 full + data360 mock), and adversarially hardened.** Author mode is a validated *assistive
  drafter*, not a final generator — kits require human review before delivery.
- **[BACKLOG.md](./BACKLOG.md)** — known limits + next improvements (schema richness, `data/` stubs, template de-biasing).
- **Design:** `docs/superpowers/specs/2026-07-15-workshop-forge-design.md` · **Plan:** `docs/superpowers/plans/2026-07-15-workshop-forge.md`
- **Dogfood findings:** `docs/superpowers/dogfood-headless360.md`, `docs/superpowers/dogfood-data360.md`
