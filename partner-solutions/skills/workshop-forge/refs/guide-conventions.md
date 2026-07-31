# GUIDE Conventions

Every workshop-forge kit's `GUIDE.md` follows a consistent **module arc**, **checkpoint semantics**, and
**framing** that have proven across data360, headless360, and nCino kits. The scaffolder stamps the *structure*
(Module 0→N headers + checkpoint markers); author mode writes the *bodies* (hands-on steps, explanations,
links).

## Module arc: Comprehend → Extend

The standard module sequence is:

- **Module 0: Comprehend** — conceptual orientation. What the reference build is, what surfaces it spans, what
  problem it solves, how the architecture fits together. Read before build; participants anchor before touching
  code.
- **Modules 1 through N−1** — hands-on build phases. Typically: provision/access the org → deploy the reference
  build → configure connectors (MCP, Data Cloud) → smoke-test one surface → exercise all surfaces → observe
  behavior → understand customization seams.
- **Module N: Extend** — always the final module. Participants modify/extend the reference build: add a new action,
  integrate a new data source, wire a new surface, scope a paid-SOW enhancement. The "you own it now" milestone.

**Why this arc works:** Educate First (Module 0), build confidence through a validated reference path (Modules
1→N−1), then prove ownership via extension (Module N). Participants leave having *changed* something, not just
deployed it.

## Sequencing principle: capability-first vs. build-live

**Default recommendation: don't have participants build the fragile core live.** When the reference build has a
brittle, high-setup core (an agent that must be deployed + published + activated, credential-gated connectors),
**pre-stage that core and have participants *tour* it, then spend hands-on time wiring it to surfaces** — the
transferable skill. This is the headless360 lesson (a mid-build reorder): live builds of the core were the
friction and burned the hands-on block on the least-reusable, most-failure-prone work.

- **Front-load the one hard ordering gate.** If a downstream module can't work until the core is deployed +
  activated, the facilitator pre-stages it in an early "The Capability" module (guided tour + one confirming
  query), so every surface module after it just plugs in. Participants still *see* the whole build; they don't
  *hand-assemble* the fragile part live.
- **Spend hands-on where the reusable skill is.** Surface-wiring (ECAs, MCP connect, an API client, a Slack card)
  and the take-home fork are what a partner repeats on their own product — that's where the minutes should go.
- **When build-live is still right:** if the core build IS the teaching objective (the partner must learn to
  author the agent/flow themselves), keep it live — but isolate its credential setup into the cookbook
  (`docs/credential-setup-cookbook.md`) so the friction is contained.
- **Not every kit needs this** — a low-setup, fast-to-deploy reference build can be built live without the pain.
  Apply capability-first when the core is fragile/high-setup; say so in FACILITATOR's rationale either way.

This is a *pedagogy* choice the author encodes in the module order + the `optional`/`modes` flags; the scaffolder
stamps whatever module sequence the overlay defines.

## 🔴 Checkpoint semantics

A **🔴 checkpoint** marks a step where:
1. **Order matters** — skipping it or running it out of sequence silently breaks downstream steps.
2. **Failure is silent** — if the step fails, participants see no immediate error, but a later step mysteriously
   fails.

Common 🔴 checkpoints:
- **ECA setup / JWT credential install** — required before MCP discovery, but "success" is a 201 response that
  doesn't prove *functionality* until the agent calls the tool.
- **Permission-set assignment** — participants see no UI clue it didn't work; only manifests when the agent
  returns "access denied."
- **Feature-flag enable** — silent until you try to use the feature.

**Rendering:** The scaffolder writes `🔴 **Checkpoint:** <reason>` wherever the overlay's `modules[]` array sets
`checkpoint: true`. Author mode must write the step description **and the validation command** ("Run X; you should
see Y; if not, revisit step Z").

**Why explicit checkpoints matter:** They reduce facilitator interrupts and participant confusion in multi-team
labs. Experienced facilitators know the silent-failure patterns; first-time facilitators need them called out.

## Educate-First framing

Module 0 exists because **understanding precedes building**. The reference build is not a black box to be
deployed and forgotten — it's a **pattern to internalize**, a **framework to extend**, and a **commercial baseline
to scope from**.

Author mode's Module 0 content must explain:
- **What it does** (the participant-facing behavior).
- **How it works** (the architecture: which services talk to which; which metadata types carry which logic).
- **Where the extension seams are** (what a partner would customize in a paid SOW).

This is not documentation generation — it's judgment. The senior-advisor voice surfaces what matters for partner
agency, not a recitation of every metadata file.

## Module bodies are authored, not scaffolded

The scaffolder stamps **headers**:

```markdown
## Module 0: Comprehend

<!-- body stub: author mode fills this -->

## Module 1: Provision Your Environment

<!-- body stub: author mode fills this -->

🔴 **Checkpoint:** Org access validated before deploy
```

**Author mode writes the bodies** — the hands-on steps, code snippets, what-to-expect explanations, links to
framework.md or provisioning docs, validation commands at checkpoints.

**Why not scaffold bodies?** Module content is engagement-specific judgment (what to emphasize, which fallback to
surface, how deep to go on MCP bridge mechanics) that can't be mechanically interpolated. The scaffolder owns
structure; author mode owns substance.

## Facilitation-aware structure

GUIDE.md is participant-facing. `FACILITATOR.md` holds the facilitator-facing mirror: timing per module,
common snags, demo scripts, how to pivot if the group is ahead/behind. workshop-forge generates both, keeping
their module numbering in sync (so "Module 3 snag" in FACILITATOR unambiguously maps to GUIDE's Module 3).

The 🔴 checkpoints in GUIDE are where FACILITATOR's "common snags" section must provide the fix — they are the
load-bearing facilitation surfaces.

## Optional & mode-gated modules

- **Optional modules** (`optional: true` in the overlay) render with an `(Optional)` suffix in the
  module header, e.g. `## Module 6: Agent Grounding (Optional)`. Use for modules a team can skip
  without breaking the arc (e.g. data360's "(Optional) Agent Grounding").
- **Mode-gated modules** (`modes: ["lab"]` or `["engagement"]`) appear in GUIDE.md only when the
  kit's top-level `mode` matches. A `lab`-only "BYO Dataset" module is omitted from an
  `engagement` kit's GUIDE, and vice-versa. The module still lives in `config/kit.json` (the
  authored overlay); only the participant-facing GUIDE is filtered.
