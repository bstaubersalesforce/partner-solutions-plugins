# Tech Strat POV Forge

A packaged [Claude](https://claude.com/claude-code) skill for building **Point of View (POV) documents** for Salesforce ISV partners against the **OG Tech Strategy Framework**.

Give it two inputs — a partner company name and a URL — and it researches the partner, pre-fills every POV section with confidence-labeled findings, asks only the gaps it can't resolve, and delivers a stakeholder-ready POV. From there it can run a structured discovery workshop and generate a technical & architectural assessment, an MVP build plan, an adversarial red team assessment, an investor deck, a one-page solution infographic, and a partner readiness scorecard.

> This skill **questions bad framing** — it does not answer whatever it is asked. It will push back before drafting if no discovery has occurred or if the input names a solution before diagnosing the constraint.

---

## Using the skill

Invoke it in Claude Code with `/tech-strat-pov-forge`, then give it the two inputs it asks for: the **partner company name** and a **company or product URL**. That's the whole setup — you don't pre-load research, fill a brief, or pick a vertical. From there the skill drives the engagement and pauses only where your input actually changes the output.

The general flow, from your side of the conversation:

1. **You provide name + URL.** The skill defaults to **Quick POV** (lean path); a deeper **Full Discovery** workshop is available if you ask for it up front.
2. **It researches and pre-fills, silently.** It fetches the site and runs parallel searches (AppExchange, competitors, customers, market data, leadership), then populates every POV section with confidence labels — `[confirmed from research]`, `[proposed — confirm]`, `[TBD]`. No permission-seeking; it reports progress as it goes.
3. **It asks you ≤5 targeted questions** — only the gaps it genuinely can't resolve, and only where your answer matters (e.g. the named pilot customer, the exec sponsor, the commercial model). It won't re-ask anything research already settled.
4. **It drafts the POV, self-checks, and shows you Markdown first.** You review, reply with specific changes, and it applies them in one pass. Nothing is committed to HTML until you reply **Approve**.
5. **After approval, it offers the optional outputs** as a multi-select menu — build plan, red team, scorecard, decks, infographic, architecture assessment, consumption map, or **All outputs + home page**. Pick what you want; the skill generates them (fanning out to parallel subagents when you request several) and links them from one HTML home page.

You stay in control at three points — the Quick-vs-Full choice, the clarifying questions, and the **Approve** gate. Everything between those is automatic. For the stage-by-stage mechanics behind this, see **How it works** below.

### Coming back to an existing POV

The first pass is not the end. A POV is a Markdown file on disk, and you can re-invoke the skill against it to deepen or refine it — just point it at the existing POV (e.g. *"open the Tekion POV and refine it"* or *"run discovery on the existing POV"*). Two common second passes:

- **Run discovery after the first pass.** Ask to run the discovery workshop against the approved POV — this is the skill's **workshop mode** (the interactive, question-driven discovery pass, as opposed to the auto-capture document generated in a package). In workshop mode the skill asks the 10-dimension questions, then presents its findings as a **confirms / contradicts / adds** diff against the current POV and offers to apply them — so discovery sharpens what you already have rather than starting over. (If a pre-filled Discovery Document already exists with notes captured live or async during a call, ask to **apply the discovery captures** and the skill reads them back into the POV the same way.)
- **Refine via dialogue.** Re-open the POV and talk through changes — correct a fact, tighten the vision, swap a pilot customer, revise the commercial model. The skill applies edits and re-runs its self-checks before re-committing.

In both cases the Markdown file is the source of truth and the HTML is regenerated from it — but they are *two different* files. The POV's own `{SLUG}-pov.md` is authoritative for the POV (refining via dialogue edits this; its HTML and downstream artifacts regenerate from it). The separate `{SLUG}-discovery-document.md` is authoritative for discovery captures (readback parses this `.md`, not its HTML view). When you apply discovery findings, the skill reads the discovery `.md` and writes the changes into the POV `.md`.

---

## Pulling in Slack insights (optional)

The skill can enrich a POV with intelligence from **internal Salesforce partner/deal Slack channels** — pre-filling sections (exec sponsor, pilot, commercial model, blockers, timeline) and shrinking the Stage 3 questions to genuine gaps. It is **opt-in** and reads nothing without your explicit pick.

**How channels are found.** If a Slack tool is connected, during research the skill discovers candidate channels, ranks them, and presents a short **3–6 channel** shortlist (Medium + High confidence only) for you to choose from — a **confirm-before-read** gate that never reads a channel you didn't pick. You can also **name a channel directly** to skip discovery. With no Slack tool, it falls back to a **paste/export** path: point it at exported channel text.

**How facts are handled.** Each extracted fact carries `@author, date` attribution and a dedicated `[from internal Slack — confirm]` label — high value, but it never hardens into a confirmed fact without partner confirmation. A short sentiment **narrative** lands in the POV's Confidence & Assumptions, informing the confidence score. The channels read, window, and attributed facts are logged in Research Provenance.

**Connecting Slack.** Two separate steps:

1. **Register the Slack MCP server** (the connection) — this is harness-managed and is a normal MCP server registration, **not** a custom block in `settings.json`'s schema. The hosted Slack MCP is an HTTP server with OAuth:

   ```bash
   claude mcp add --transport http slack https://mcp.slack.com/mcp
   ```

   Then authorize it once: run `/mcp` in a session and complete the OAuth sign-in flow in the browser. After that, `claude mcp list` should show `slack … ✔ Connected`. (One caveat: an OAuth-authenticated server like this may be **absent in headless/cron runs** — the skill detects that and falls back to the paste/export path.)
2. **Add the skill's defaults** in a dedicated file, **`~/.claude/tech-strat-pov-forge-slack.json`** (the skill reads it directly each run — `settings.json` rejects an unknown `slack` key, so the defaults live here instead):

```json
{
  "tool_name": "slack",
  "workspace": "salesforce-org62",
  "channel_conventions": ["#partner-*", "#*-partnership", "#gp-*", "#isv-*"],
  "read_window_days": 90
}
```

- `tool_name` — the connected Slack MCP tool's name (lets the skill confirm availability instead of blindly probing). **Must match the name the MCP server registers under in step 1** — if they differ, the skill won't detect the tool and silently falls back to the paste/export path.
- `workspace` — the Org62-linked workspace discovery searches.
- `channel_conventions` — your team's channel naming patterns; improves discovery ranking.
- `read_window_days` — history window to read (default **90**).

The connection is harness-managed — the skill only reads whether the configured tool is available. With no `tech-strat-pov-forge-slack.json` and no tool, behavior is identical to today.

## Optional: Org62 engagement pre-fill

When you accept the Stage-1 offer, Tech Strat POV Forge can hydrate the POV from an existing
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

```json
{ "env": { "ORG62_ALIAS": "org62" } }
```

## What it produces

| Output | Format | Trigger |
|--------|--------|---------|
| **Point of View** (problem space, vision, product strategy, solution statement, 1–3 use cases, target markets & personas, solution alignment, commercial model, architecture summary, KPIs) | Markdown | Default — the core deliverable |
| **Discovery Document** (10 discovery dimensions, *How Might We* reframes, Value Proposition Canvas + Business Model Canvas) | Markdown + HTML | "All outputs" (auto-capture, pre-filled) · "discovery"/Full Discovery (workshop) — Stage 15 |
| **MVP Build Plan** (scope by horizon, feature breakdown, user stories + acceptance criteria, success metrics, Salesforce platform requirements, phase plan, next-step decisions) | Markdown + HTML | "build plan" / "MVP plan" |
| **Technical & Architectural Assessment** (Well-Architected RAG across 3 pillars / 8 qualities, target-state 7-layer architecture + an embedded **Mermaid architecture diagram**, build-ready metadata blueprint + skeleton stubs) | Markdown + HTML | "architecture assessment" / "Well-Architected review" (Stage 16) |
| **Red Team Assessment** (6 adversarial frameworks — competitive war game, customer-exit simulation, platform-dependency scan, 18-month invalidation, Salesforce investment teardown, commercial-model pressure test — plus synthesis with blind spot & stopping rule) | Markdown | "red team" / "how would this fail" |
| **Investor Presentation** (covers problem, solution, market, product, traction, business model, team, partnership, ask) | HTML (10-slide deck) | "investor deck" / "pitch deck" |
| **Solution Infographic** (problem, solution-flow, proven-outcomes, and market panels) | HTML (one-pager) | "infographic" / "visual summary" |
| **Partner Readiness Scorecard** (18 strategy attributes scored RAG + 1–3 rank, with a readiness snapshot) | Markdown + HTML | "readiness scorecard" / "partner scorecard" |
| **Marketecture** (layered diagram: UI, data model, integration, named Salesforce clouds/SKUs, external systems) | HTML diagram | When architecture is populated |
| **Consumption Opportunities** (ranked agent/data/SKU consumption-growth map with named-component build blueprints) | Markdown + HTML | "All outputs" · "consumption" / "agent & data opportunities" — Stage 18 |
| **Competitive Assessment** (balanced Salesforce-vs-platforms comparison across commercial, ecosystem, GTM, technology — two layers, objections handled in line) | Markdown + HTML | "All outputs" · "competitive assessment" / "Salesforce vs AWS/Azure/OpenAI" — Stage 19 |
| **POV Presentation** (12-slide deck rendering the approved POV for a stakeholder readout — problem, vision, product strategy (2 slides), solution, use cases, markets, alignment, roadmap, commercial model, recommendation) | HTML (12-slide deck) | "POV deck" / "POV presentation" / "slide version of the POV" |
| **Solution Package (home page)** (HTML index linking every generated artifact — View ↗ + Markdown ↓ download) | HTML index | "All outputs + home page", or 2+ outputs in one session |

After a POV is approved, the skill presents the optional outputs as a multi-select (including an **All outputs + home page** option) so you don't have to type each one. When you generate several, the skill renders every artifact as a viewable HTML page — Markdown-native ones (POV, Red Team) are wrapped in a shared styled shell — and builds a home page that links them all: HTML for live viewing, Markdown for download where a source exists.

### Diagrams (Mermaid)

The **Technical & Architectural Assessment** (Stage 16) embeds a target-state architecture flowchart authored in **Mermaid**, themed to the Salesforce palette. The theme, recipes, and export rules live in `refs/mermaid-diagrams.md`, anchored to the SLDS design tokens (also captured in `~/.claude/style-conventions.md`). Three render surfaces from one diagram source:

- **Live HTML** — the assessment's HTML embeds the Mermaid CDN, so the diagram renders in any browser (needs internet at view-time).
- **Markdown** — a fenced ` ```mermaid ` block renders natively on GitHub/GitLab.
- **PNG/SVG for decks** — optional, via `@mermaid-js/mermaid-cli` (`mmdc`). Capability-gated: if `mmdc` is not installed, the diagram source is kept and the export is skipped with an install hint — the run never blocks. Install with `npm i -g @mermaid-js/mermaid-cli` for deck-ready images.

More diagram types (build-plan Gantt, marketecture flowchart, consumption flow) are backlogged (see `BACKLOG.md` R8) and reuse the same single-source theme.

---

## How it works

The skill runs a 19-stage flow. The core sequence:

1. **Intake** — asks only for partner name + URL. Offers a path choice: **Quick POV** (default) or **Full Discovery** (run the Discovery Framework first, then feed the POV).
2. **Research** — fetches the site and runs parallel searches (AppExchange listing, competitors, customers/traction, market context, leadership). No permission prompts; it reports progress in plain English as it goes.
3. **Pre-fill + Propose** — populates every POV section with confidence labels (`[confirmed from research]`, `[proposed — confirm]`, `[TBD]`), proposes industry-specific KPIs, and surfaces ≤5 clarifying questions.
4. **Clarify** — asks only the targeted gaps.
5. **Draft** — generates the POV against a strict output contract.
6. **Contradict** — self-checks for ~20 failure patterns (vague vision, feature-framed use cases, missing pull-through SKUs, no defensible moat, undefined MVP, etc.).
7. **Validate** — runs the delivery checklist; won't ship a POV that fails its own contract.
8. **Interactive Review** — Markdown draft first; HTML is only committed on your **Approve**.

Stages 8–12, 14, 15, 16, 17, 18, and 19 (MVP build plan, red team, investor deck, infographic, partner readiness scorecard, marketecture, the **auto-capture Discovery Document**, the **technical & architectural assessment**, the **POV presentation deck**, the **Consumption Opportunities** map, and the **Competitive Assessment**) are optional outputs that run on request and together make up "All outputs"; Stage 13 assembles the generated artifacts into a linked HTML home page. The architectural assessment (Stage 16) evaluates the partner's architecture against Salesforce **Well-Architected**, prescribes the target-state Salesforce architecture, and emits a build-ready blueprint + stubs that feed the MVP build plan. Stage 15 (**Discovery Framework**) runs two ways. In a package ("All outputs") it generates in **auto-capture mode** in Wave 1 — a pre-filled Discovery Document (10 dimensions, How Might We, Value Proposition + Business Model canvases) with per-dimension *Discussion-capture* slots that can be filled in live or async during a discovery conversation and later read back into the POV. The interactive discovery **workshop** (question-driven, applies findings as a diff to the POV) remains a separate pick, available on request or up front as the **Full Discovery** intake path. Per-stage definitions live under `refs/stages/` (one file per output, selectively loaded only when that output is requested); deep-definition references for Stages 15 and 16 remain in `refs/discovery-framework.md` and `refs/architecture-assessment.md`.

As of 2026-06-08, each Agentforce and Data Cloud opportunity in the **Consumption Opportunities** map also carries a **directional, credits-only consumption pre-estimate** anchored to a single customer-size band (S/M/L/XL), with the U/F/A and entity-count assumptions shown so the figures can be carried into the official Agentforce Credit Estimator / Data 360 calculator. Rates live in `refs/consumption-estimation.md`. This seeds the calculator; authoritative dollar sizing stays with the `sf-flex-estimator` skill.

When 3 or more independent downstream artifacts are requested together (e.g. "All outputs + home page"), the skill fans them out to concurrent subagents via `refs/parallel-dispatch.md` rather than generating them sequentially — each subagent receives a compact payload (the approved POV file path + its one stage file + the output directory), never the full conversation, to keep token cost bounded. Execution is dependency-aware: Stage 16 (Architectural Assessment) runs first because it feeds Stage 8 (MVP Build Plan), whose subagent brief carries the Stage 16 output path; Stages 8, 9, 10, 11, 12, 14, 15, 17, 18, and 19 run concurrently in the next wave (Stage 15 generates the auto-capture Discovery Document; Stage 14 only when the Architecture Summary is populated); Stage 13 (home page) runs last via the orchestrator. Two QA critic loops run on this fan-out path: the three analytically heavy artifacts (MVP Build Plan, Red Team, Architectural Assessment) each run a `generate → critic → repair` pipeline where an independent critic subagent attacks the artifact's internal rigor, and a Wave-2 package completeness-critic checks every artifact against the POV and against each other for contradictions, unexplained confidence drift, and scope overlap. Repairs run in a single bounded round, behind a post-repair re-validation gate that discards any repair which regresses an artifact's own checklist; the loops never fabricate a value to close a gap the POV already discloses as a known TBD. Contradiction and confidence-drift findings auto-repair; scope-overlap (anti-overlap) findings are advisory — surfaced for review rather than auto-repaired, since that judgment proved less stable in testing. Both loops are skipped on the inline 1–2-artifact path. If subagent dispatch is unavailable, the skill falls back to sequential generation automatically.

---

## Delivery voice

Output is written as a **senior Salesforce industry advisor briefing an ISV partner's executive team** — McKinsey-style:

- **Lead with the conclusion**, evidence follows.
- **Quantify or qualify** — every claim is a number, a named source, or explicit uncertainty.
- **No hedging, no jargon-as-substance.**
- Every section answers the partner's implicit *"so what — what should I do?"*

---

## Repository structure

```
tech-strat-pov-forge/
├── SKILL.md                          # Orchestration: stages, delivery voice, refusal conditions
├── BACKLOG.md                        # Tracked ideas/improvements not yet actioned
├── refs/
│   ├── og-tech-strategy-framework.md # OG Tech Strategy Framework reference
│   ├── industry-alignment.md         # Slim router: vertical → file lookup (lazy-loaded)
│   ├── verticals/                    # One file per vertical; only the matched one is loaded
│   │   ├── healthcare-life-sciences.md
│   │   ├── financial-services.md
│   │   ├── manufacturing.md
│   │   ├── retail-consumer-goods.md
│   │   ├── public-sector.md
│   │   ├── energy-utilities.md
│   │   ├── travel-hospitality.md
│   │   ├── transportation-logistics.md
│   │   └── automotive.md
│   ├── pull-through-gtm.md           # ISVforce pull-through + OEM/Embedded resale + GTM activation
│   ├── red-team-lenses.md            # 6 adversarial frameworks
│   ├── discovery-framework.md        # Stage 15 — Discovery Framework definition (lazy-loaded)
│   ├── architecture-assessment.md    # Stage 16 — Technical & Architectural Assessment definition (lazy-loaded)
│   ├── mermaid-diagrams.md           # Shared Mermaid theme (SLDS) + recipes + capability-gated mmdc export
│   ├── parallel-dispatch.md          # Parallel dispatch protocol (fan-out when 3+ artifacts requested)
│   ├── competitive-landscape.md      # Stage 19 — curated platform facts (app platforms, hyperscalers, AI providers)
│   └── stages/                       # Per-stage output definitions (one file per output, selectively loaded)
│       ├── stage-08-mvp-build-plan.md
│       ├── stage-09-red-team.md
│       ├── stage-10-investor-presentation.md
│       ├── stage-11-solution-infographic.md
│       ├── stage-12-partner-readiness-scorecard.md
│       ├── stage-13-output-home-page.md
│       ├── stage-14-marketecture.md
│       ├── stage-15-discovery-framework.md
│       ├── stage-16-architecture-assessment.md
│       ├── stage-17-pov-presentation.md
│       ├── stage-18-consumption-opportunities.md
│       └── stage-19-competitive-assessment.md
├── scripts/
│   └── discovery-questions.md        # Targeted questions by POV section
├── templates/
│   ├── pov-output.md                 # POV output contract
│   ├── mvp-build-plan.md / .html     # MVP build plan (Markdown + styled HTML)
│   ├── red-team-assessment.md        # Red team output structure
│   ├── investor-presentation.html    # 10-slide investor deck
│   ├── solution-infographic.html     # One-page visual overview
│   ├── partner-readiness-scorecard.md / .html  # 18-attribute readiness scorecard (Markdown + styled HTML)
│   ├── document-shell.html           # Styled HTML wrapper for Markdown-native artifacts (POV, Red Team)
│   ├── output-index.html             # Home page linking every generated artifact
│   ├── marketecture.html             # 4-layer architecture diagram
│   ├── discovery-document.md / .html # Discovery Document (Markdown + styled HTML; VPC + BMC canvases)
│   ├── technical-architecture-assessment.md / .html  # Architecture assessment (Markdown + styled HTML)
│   ├── pov-presentation.html         # 12-slide POV readout deck
│   ├── consumption-opportunities.md / .html  # Consumption Opportunities map (Markdown + styled HTML)
│   └── competitive-assessment.md / .html     # Competitive Assessment (Markdown + styled HTML)
├── validation/
│   ├── checklist.md                  # POV pre-delivery validation
│   ├── mvp-checklist.md              # MVP build plan validation
│   ├── scorecard-checklist.md        # Partner readiness scorecard validation
│   ├── red-team-checklist.md         # Red team assessment validation
│   ├── investor-checklist.md         # Investor presentation validation
│   ├── infographic-checklist.md      # Solution infographic validation
│   ├── marketecture-checklist.md     # Marketecture diagram validation
│   ├── discovery-checklist.md        # Discovery Document validation
│   ├── architecture-checklist.md     # Architecture assessment validation
│   ├── pov-presentation-checklist.md # POV presentation deck validation
│   ├── consumption-checklist.md      # Consumption Opportunities validation
│   └── competitive-checklist.md      # Competitive Assessment validation
├── docs/superpowers/
│   ├── specs/                        # Design specs (one per feature, brainstormed first)
│   └── plans/                        # TDD implementation plans (task-by-task)
├── tests/
│   └── validate_skill.py             # Structural validation suite (run before committing edits)
├── .githooks/
│   └── pre-commit                    # Tracked hook: runs the suite before each commit (opt in via core.hooksPath)
└── .github/workflows/
    └── validate.yml                  # CI: runs the validation suite on push/PR
```

---

## Validating the skill

After editing any template, reference, or `SKILL.md`, run the validation suite:

```bash
python3 tests/validate_skill.py
```

It asserts the skill's structural invariants (stdlib only, no dependencies) — file/reference integrity, `{{TOKEN}}` hygiene and brace balance, scorecard token + attribute-name parity, discovery-dimension and Well-Architected pillar/quality parity, canvas and RAG token families, contiguous Stage numbering, menu↔stage consistency (including that the "Optional outputs" header range tracks the stage map and each menu question agrees with its header chip — so a new stage or a renamed menu can't leave stale wording), the canonical Org62 Opportunity stage vocabulary, and the program-rename invariant (the retired brand name must not reappear outside `LICENSE`). It also includes **behavioral tests for the deterministic `scripts/`** — a golden-file check that `md-to-html.py` renders a fixture exactly, plus inject/repair/idempotency checks for `ensure-home-link.py` (fixtures live in `tests/fixtures/`). Exit code is `0` on all-pass, `1` on any failure. It validates structure, contracts, and the converters' behavior — but not the quality of the LLM-generated prose itself.

A **pre-commit hook** runs this suite automatically and blocks any commit that fails (bypass with `git commit --no-verify`). The hook is tracked in the repo at `.githooks/pre-commit`, so it survives a fresh clone — activate it once with:

```bash
git config core.hooksPath .githooks
```

(CI in `.github/workflows/validate.yml` runs the same suite on every push/PR, so the hook is a fast local guard, not the only safety net.)

### Backlog

Ideas and improvements not yet actioned — maintainability, complexity hygiene, distribution friction, and the open question of an output-quality signal for the LLM prose — are tracked in [`BACKLOG.md`](BACKLOG.md) so they stay visible. Items graduate to a spec → plan → implementation cycle (under `docs/superpowers/`) when picked up.

---

## Installation

This is a personal Claude skill. Clone it into your skills directory:

```bash
git clone https://github.com/bstaubersalesforce/tech-strat-pov-forge.git \
  ~/.claude/skills/tech-strat-pov-forge
```

If you intend to edit the skill, activate the tracked pre-commit hook once so the validation suite guards your commits:

```bash
git config core.hooksPath .githooks
```

Then invoke it in Claude Code:

```
/tech-strat-pov-forge
```

When prompted, provide the partner company name and URL.

> **Note:** If you are the author, your working copy already lives at `~/.claude/skills/tech-strat-pov-forge` and *is* this repo — no clone needed. The command above is for setting up a fresh machine or sharing with a collaborator.

### Reducing permission prompts (optional)

By default Claude Code prompts before reading the skill's files or running its scripts. If you trust this skill and don't want to approve each step, allow-list the operations it uses in your settings. Add to `~/.claude/settings.json` (applies everywhere) or the repo's own `.claude/settings.local.json` (scoped to this skill, git-ignored):

```jsonc
{
  "permissions": {
    "allow": [
      "Read(~/.claude/skills/tech-strat-pov-forge/**)",  // read the skill's refs, templates, stages
      "Bash(python3 *)",                          // run the validation suite
      "Bash(ls:*)", "Bash(grep:*)", "Bash(cat:*)", "Bash(find:*)",  // simple read-only inspection
      "WebFetch", "WebSearch"                     // the research stage (Stage 2)
    ]
  }
}
```

Scope these to what you're comfortable with — `Read` on the skill tree and the read-only `Bash` verbs are low-risk; `WebFetch`/`WebSearch` let the research run without prompting. Everything here is *opt-in*; with no rules, Claude simply asks each time.

If you also want to skip the local validation gate while iterating, the pre-commit hook can be bypassed per-commit with `git commit --no-verify` — but CI still runs the suite on push/PR, so a broken commit won't merge silently.

---

## Verticals covered

Healthcare & Life Sciences · Financial Services · Manufacturing · Retail & Consumer Goods · Public Sector · Energy & Utilities · Travel & Hospitality · Transportation & Logistics · Automotive

Each vertical lives in its own file under `refs/verticals/` and ships with sourced market data, focus areas, aligned use cases, regulatory drivers, and suggested KPIs. `refs/industry-alignment.md` is a slim router that maps a partner to the right file — only the matched vertical is loaded at runtime. Partners outside these verticals are flagged with a named owner to source the data before delivery.

---

## Keeping industry data fresh

Market figures, KPIs, and regulatory drivers age. Refresh them on a cadence (suggested: **every 6–12 months**, or before any high-stakes deliverable) so the skill never cites stale numbers.

**Competitive landscape.** `refs/competitive-landscape.md` carries durable platform-level facts about app platforms, hyperscalers, and AI providers, used by the **Competitive Assessment** (Stage 19). It has its own **"Last reviewed"** date at the top. AI-provider capabilities and pricing drift fastest — re-verify this file before any high-stakes competitive deliverable, and update the "Last reviewed" date when you do.

### To refresh an existing vertical

1. Open the file in `refs/verticals/` (e.g., `healthcare-life-sciences.md`).
2. Re-source each figure in the **Market snapshot** — confirm the market size, CAGR, and year against a current named analyst report (Gartner, Grand View, MarketsandMarkets, IDC, etc.). Update the inline `*(Source, Year)*` citation.
3. Review **Regulatory drivers** for new or amended mandates (new CMS/ONC rules, state privacy laws, EU directives).
4. Sanity-check **Suggested KPIs** and targets against what partners in that vertical are actually measuring.
5. Commit with a message like `Refresh <vertical> market data (Q2 2026)`.

### To add a new vertical

1. Copy an existing vertical file as a template — keep the **exact section order**: Industry Cloud → Market snapshot → Key focus areas → Top aligned use cases → Regulatory drivers → Suggested KPIs → MVP alignment signal.
2. Populate every figure from a **named, dated source** — do not estimate market size without attribution. Label unverified figures "Estimated."
3. Map it to the right **Salesforce Industry Cloud** (or the closest core-cloud analog if no dedicated SKU exists).
4. Add a row to the lookup table in `refs/industry-alignment.md` (trigger keywords → file path → Industry Cloud).
5. Add the file to the `refs/verticals/` tree in this README and to the "Verticals covered" list above.

### Ground rules (enforced by the skill)

- **No fabricated numbers.** Every market figure carries a named source and year, or is labeled "Estimated."
- **One vertical per file.** This keeps runtime context lean — only the matched vertical loads.
- **The router stays slim.** `industry-alignment.md` holds the lookup table and guidance only — never the vertical data itself.

---

## License & Usage

**Proprietary — internal and authorized use only.** See [LICENSE](LICENSE).

This repository contains confidential material on Salesforce Partner ("OG Tech Strategy") Program mechanics and partner GTM economics. Do not publish it, redistribute it outside the authorized audience, or represent its contents as official Salesforce guidance — the framework references here are working interpretations, not official program documentation.
