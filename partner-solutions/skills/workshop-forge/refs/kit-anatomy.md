# Kit Anatomy

workshop-forge scaffolds a Salesforce partner workshop kit around a single **overlay** (`config/kit.json`) that
declares which conditional parts to render. The anatomy divides into three layers: the **common skeleton**
(always present), the **conditional parts** (rendered per overlay keys), and the **per-engagement overlay** that
controls which conditional parts are stamped.

All kit artifacts are stamped from templates under `templates/` (see `templates/README.md.tmpl`, `templates/GUIDE.md.tmpl`, `templates/FACILITATOR.md.tmpl`, `templates/LESSONS-LEARNED.md.tmpl`, `templates/KNOWN-GAPS.md.tmpl`, `templates/kit.json.tmpl`, `templates/env.example.tmpl`, `templates/gitignore.tmpl`, `templates/scripts/check.sh.tmpl`, `templates/scripts/00-preflight.sh.tmpl`, `templates/scripts/01-check-env.sh.tmpl`, `templates/scripts/02-deploy.sh.tmpl`, `templates/scripts/03-assign-perms.sh.tmpl`, `templates/scripts/lib/common.sh.tmpl`, `templates/docs/org-provisioning.md.tmpl`, `templates/docs/credential-setup-cookbook.md.tmpl`, `templates/docs/framework.md.tmpl`, `templates/docs/buildability-matrix.md.tmpl`, `templates/data/README.md.tmpl`). The scaffolder (`scripts/scaffold_kit.py`) replaces `{{TOKENS}}` with overlay values. When this documentation describes the OUTPUT kit structure, those paths refer to files in the generated kit, not in the workshop-forge skill itself.

## Common skeleton (always rendered)

Every scaffolded kit includes:

- **`README.md`** — overview, target audience, what's inside, how to run.
- **`GUIDE.md`** — participant-facing hands-on module sequence (Module 0 Comprehend → Module N Extend arc).
- **`FACILITATOR.md`** — facilitator-facing delivery guide, timing, tech dependencies, fallback plans, demo reminders.
- **`LESSONS-LEARNED.md`** — retro template (pre-workshop risks, in-workshop observations, post-workshop improvements).
- **`KNOWN-GAPS.md`** — always stamped. The single definitive list of what's open / unverified / watch-before-the-event (technical/build gaps + provisioning/logistics open items), with a status legend and a re-verify-at-dry-run rule. Author mode + rehearsals populate the rows; each 🔴 checkpoint is a candidate gap until smoke-tested. Distilled from the headless360 kit's KNOWN-GAPS doc.
- **`.env.example`** — placeholder env vars for org-backed kits (aliases, URLs, MCP config); committed.
- **`.gitignore`** — excludes `.env`, logs, temp state.
- **Shared shell library** (generated as `lib/common.sh` in the kit's scripts directory, from `templates/scripts/lib/common.sh.tmpl`) — colored logging, preflight reminders, error handling.
- **Lifecycle scripts** — numbered scripts matching the provisioning model's phases (stamped from `templates/scripts/*.sh.tmpl`); the exact set is model-specific.
- **Kit validator** (generated as `check.sh` in the scripts directory, from `templates/scripts/check.sh.tmpl`) — enumerates exactly the files rendered (so assertions match the conditional shape stamped for this engagement).

## Conditional parts (rendered per overlay)

These are included **only if the overlay declares them**:

- **`docs/credential-setup-cookbook.md`** — iff `provisioning.needs_org: true`. Isolates the highest-friction
  setup (connected app / ECA / tokens / permission grants) into one gotcha-by-gotcha doc, separate from the GUIDE,
  because credential failures are usually silent (a green status that doesn't prove function). Topic-neutral
  structure (what-to-create / the-gotcha / the-verify-step); author mode fills the engagement-specific gotchas.
  Distilled from the headless360 credential-setup cookbook.
- **`docs/org-provisioning.md`** — iff `provisioning.needs_org: true`. The selected provisioning model, feature
  dependencies → org-type reasoning, operational rules, ECA/PKCE/JWT MCP connector-setup instructions, and
  preflight checklist. Suppressed for educate-only kits.
- **Deploy + assign scripts** (from `templates/scripts/02-deploy.sh.tmpl` and `templates/scripts/03-assign-perms.sh.tmpl`) — iff `needs_org: true`. Numbered to match the provisioning model's phase sequence. Skipped for educate-only kits.
- **Check-env script** (from `templates/scripts/01-check-env.sh.tmpl`) — iff `needs_org: true`. Lightweight env sanity check (.env present, sfdx/ present).
- **Preflight org validator** (from `templates/scripts/00-preflight.sh.tmpl`) — iff `needs_org: true`.
- **Content directories** — `content_dirs: { slides, commercial, web, showcase, prework }` controls which
  subdirectories are created under `docs/`. Each enabled dir is stamped with a stub README explaining its purpose.
- **`docs/framework.md`** — iff the kit involves teaching a multi-component architecture (e.g., MCP bridges, CLT +
  Slack + React Agent API in headless360). Conditional on engagement scope, not a boolean key — author mode
  decides whether to write it.
- **`docs/buildability-matrix.md`** — iff the kit teaches partners how to scope/price a paid-SOW extension of the
  reference build. Same author-mode discretion as framework.md.
- **`sfdx/` placeholder** — iff `reference_build.source` is set (non-`none`). The reference SFDX package is
  imported here (never regenerated by the scaffolder).
- **`data/` directory** (from `templates/data/README.md.tmpl`) — iff `reference_build.sample_data_path` is set (non-empty). Holds sample datasets the workshop references (CSV/JSON seed files, load scripts, generators). Author mode fills it.

## The overlay — `config/kit.json`

The overlay is the single source of truth for both the scaffolder (which files to stamp) and author mode (what
content to write). It sits at the root of every kit.

Schema:

```jsonc
{
  "name": "headless360",
  "title": "Headless 360 Partner Activation Workshop",
  "mode": "lab",                      // "lab" (multi-partner) | "engagement" (1:1)
  "duration": "2-day",
  "partner_overlay": "reference",     // "reference" (neutral) | "<partner>" (retargeted reskin)
  "surfaces": { "slack": true, "react_agent_api": true, "clt_lex": true, "mobile": false },
                                      // {} = no surfaces by design; key omitted = not yet decided
  "provisioning": {
    "needs_org": true,                // false ⇒ skip org-provisioning doc + deploy scripts + tier keys
    "model": "de-per-team",           // enum owned by refs/provisioning-models.md
    "required_features": ["Agentforce", "HostedMCP"]
  },
  "modules": [ /* ordered {n, title, checkpoint?, optional?, modes?:["lab"|"engagement"]};
                  Module 0 Comprehend … Module N Extend */ ],
  "content_dirs": { "slides": true, "commercial": true, "web": false, "showcase": false, "prework": false },
  "reference_build": { "source": "pie-poc-forge|freeform|none", "path": "sfdx/",
                       "sample_data_path": "data/"  /* optional: set ⇒ emit data/ dir + README stub */ }
}
```

**Key overlay behaviors:**

- `provisioning.needs_org: false` → **no** org-provisioning doc, **no** deploy/assign scripts, **no** preflight
  org-reminders. `.env.example` is still rendered (for shared backend/MCP configs that may reference an org alias), 
  but org-specific instructions are omitted. Educate-only kits are a first-class outcome, not degraded.
- `content_dirs` → each `true` key creates a corresponding `docs/<key>/` directory with a stub README.
- `modules[]` → ordered array of `{ n, title, checkpoint? }` objects; the scaffolder stamps Module 0→N headers in
  GUIDE.md, with 🔴 checkpoint markers where `checkpoint: true`. Module **bodies** are authored (not scaffolded).
- `modules[].optional: true` → the GUIDE header is stamped `## Module N: Title (Optional)`.
- `modules[].modes: ["lab"|"engagement"]` → the module is rendered in GUIDE.md **only** when the
  kit's top-level `mode` is in the list; otherwise it is omitted from GUIDE.md (but retained in
  `config/kit.json`, which records the overlay as authored).
- `reference_build.sample_data_path` (optional) → when set, the scaffolder emits a `data/`
  directory with a `data/README.md` stub and the kit validator requires it. Absent ⇒ no `data/`.
- `surfaces: {}` means **no surfaces, by design** (e.g. a Data-Cloud pipeline kit); omitting the
  `surfaces` key entirely means **not yet decided**. `surfaces` remains descriptive-only.
- `reference_build.source` → directs author mode which input contract to expect; the scaffolder creates the
  placeholder directory at `path` (default `sfdx/`).

## Per-engagement overlay differences

Each kit's overlay reflects its engagement specifics:
- **Multi-partner lab** (data360, headless360): `mode: "lab"`, partner-neutral reference build, broader
  provisioning scope (per-team orgs).
- **1:1 engagement** (nCino): `mode: "engagement"`, partner-targeted overlay (`partner_overlay: "nCino"`),
  narrower provisioning (assigned-preconfigured model, one pre-loaded org).
- **Educate-only** (hypothetical): `needs_org: false`, no deploy scripts, no org docs — the scaffolder
  short-circuits the org-provisioning branch entirely.

The full `provisioning.model` enum is owned by `refs/provisioning-models.md`.

The overlay schema is **stable** — new engagements reuse the same keys with different values. The scaffolder and
author flows are overlay-driven, not engagement-specific.
