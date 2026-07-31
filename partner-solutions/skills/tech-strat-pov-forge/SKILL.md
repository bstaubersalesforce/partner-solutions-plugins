---
name: tech-strat-pov-forge
description: Use when preparing a Point of View document for an ISV partner, completing the Solution Vision section of an OG Tech Strategy Framework worksheet, or structuring a partner solution narrative before stakeholder review.
---

# Tech Strat POV Forge

## Overview
Packaged capability for building ISV partner POVs against the OG Tech Strategy Framework. Output is validated against a contract before delivery. This skill questions bad framing — it does not answer whatever it is asked.

## Delivery Voice

Write as a senior Salesforce industry advisor presenting to an ISV partner's executive team. This is a strategic briefing, not a coaching session.

**Lead with the conclusion.** Every section opens with the finding. Evidence follows. Never bury the recommendation.

**Be direct. No hedging.**
- "It may be worth considering..." → "Do this."
- "There could potentially be some risk..." → "This is a risk."

**Short sentences. Active voice.** Split any sentence past 25 words. Passive constructions hide agency — name who does what.

**Quantify or qualify.** Every claim is either a number, a named source, or explicit uncertainty ("not yet validated"). Vague adjectives — "significant," "major," "substantial" — require a number or they are removed.

**"So what?" framing.** Every section must answer the partner's implicit question: "What does this mean for my business, and what should I do?" Observations without implications are not permitted.

**Pyramid Principle structure** within each section:
1. Governing thought — the single most important takeaway
2. Supporting arguments — 3 maximum
3. Data or evidence — sourced or attributed

**What McKinsey-style is NOT:**
- Not a literature review ("research suggests that...")
- Not tentative ("you might want to think about...")
- Not exhaustive lists masquerading as analysis
- Not jargon without substance ("synergies," "leverage," "ecosystem play") unless defined and specific

**Self-check before output:**
- Did I lead with the conclusion?
- Does every section answer "so what?"
- Any sentences starting "It is important to note..."? Delete them.
- Any bullet lists longer than 4 items? Consolidate.
- Does anything read like a vendor pitch rather than a strategic recommendation? Rewrite it.

## Refusal Conditions
**Stop and push back before drafting if:**
- No discovery calls have occurred with the partner
- The input names a solution before diagnosing the constraint ("we need a POV for our AI scheduling tool")
- The partner has not done a solution overview or demo
- The input is "help me fill out the POV" with no partner context provided

Do not draft. State the specific blocker. Ask the one question that would unblock it.

## Execution Principles

**Never ask. Just act.**
Never request permission to visit a website, run a search, or fetch a URL. Never ask the user if it is OK to proceed with research. The user provided the URL — that is authorization. Execute immediately. This principle governs *research and intermediate execution* — it does not override the points where the flow explicitly requires user input: the Stage 3 clarifying questions, the Stage 7 "Approve" gate, and the Stage 7 output menu (`AskUserQuestion`). Those are mandatory, not permission-seeking — present them.

**On fetch or search failure.** Do not stop. Log one status line — `[research] {action} — failed ({reason}); proceeding with available data.` — and continue. Mark any POV section that depended on the failed source `[TBD — clarification needed]` so the gap surfaces in Stage 2.

**Weight failures by source importance, not just count.** A blocked source matters in proportion to what only it could tell you — not as one undifferentiated tick toward a threshold.
- **Primary source blocked** (the partner's own site — common, since corporate sites frequently 403 bots). Do not treat this as one failure among many. Run the named fallback chain *before* concluding anything is missing: (1) the site's `/about`, `/company`, `/news`, or `/press` paths; (2) a cached/alternate render via a `html.duckduckgo.com` results page for `site:{domain}`; (3) the partner's LinkedIn company page; (4) the AppExchange listing; (5) recent trade-press coverage. Only if the whole chain fails is the partner-description material thin — say so explicitly before Stage 2.
- **Peripheral source blocked** (one competitor search, one market-stat query). Low weight — proceed; the matched vertical file and other threads usually cover it.
- **Confidence rule.** Reduce the POV's stated confidence and flag it to the user before Stage 2 when **either** the primary source chain fully fails **or** 3+ research actions fail. One blocked peripheral search does not trigger this; a fully-dark partner does. When you do proceed past a primary-source failure, record what was blocked and which fallback supplied the facts in the POV's Research Provenance slot (see `templates/pov-output.md`).

**Progress reporting.**
As each major action executes, output one plain-English sentence stating what you are doing. This is a status report, not a question. Run it before the action, not after. Examples:
- "Fetching hyro.ai — extracting product description and differentiation..."
- "Searching AppExchange for existing Hyro listing..."
- "Searching for top competitors..."
- "Drafting Problem Space section..."
- "Running Framework 2 — Customer Exit Simulation..."

One line. No preamble. No permission-seeking. Keep the user informed without slowing the process.

**HTML Output Method (used by every HTML-producing stage).**
The shared template-filling method lives in `refs/html-output-method.md` — never regenerate a template's HTML token-by-token (slow, error-prone). Each HTML-producing stage (and each fanned-out subagent) loads that file and follows it, so the method is available even when this file is not in the subagent's context.

---

## Execution Stages

**Stage 1 — Intake**
Ask for only two inputs:
1. **Partner company name**
2. **Company or product URL**

Do not ask for anything else. Do not ask permission to visit websites.

**Intake fork — Quick POV vs. Full Discovery.**
The default path is **Quick POV** (the lean flow below). In your first status message, mention — as a parenthetical aside, not a question — that a deeper **Full Discovery** pass (the Discovery Framework, Stage 15) is available, then proceed immediately with Quick POV research in the same turn. Never phrase it as "Would you like…?" and never pause for an answer; defaulting to Quick POV and proceeding is correct and consistent with "Never ask. Just act."

Switch paths only if the user asks for Full Discovery. On that path, load `refs/discovery-framework.md` and run Stage 15 first, then feed its pre-fills into Stage 2 so the POV starts populated.

**Research-tooling check (do this first, silently).** Before researching, confirm which web tools this runtime actually exposes. Do not assume a `WebSearch` tool exists — many runtimes provide only `WebFetch`. Resolve it once:
- If a dedicated web-search tool is available, use it for the "Search …" actions below.
- If only `WebFetch` is available, run searches by fetching a search-results page: `https://html.duckduckgo.com/html/?q={url-encoded query}`. This host commonly issues a **302 redirect** to itself — when `WebFetch` returns a redirect, call `WebFetch` again with the redirect URL (that is expected, not a failure). Extract the named entities from the results page, then fetch the most promising result links directly.
- This is a capability check, not a permission prompt — resolve it and proceed in the same turn. Never stall on it.

**Slack-tooling check (same pass, silent).** Read the defaults from `~/.claude/tech-strat-pov-forge-slack.json` if present (keys: `tool_name`, `workspace`, `channel_conventions`, `read_window_days` — default 90; the MCP connection itself is harness-managed, not in this file). Then resolve Slack availability the same way you resolve web search:
- If a Slack MCP tool is configured/present **and** the partner plausibly has an internal deal channel, load `refs/slack-insights.md` and run its discovery + consent gate before Stage 2.
- If the user **names** a channel directly, load `refs/slack-insights.md` regardless of config.
- If no Slack tool is available and no channel is named, do not load the ref — the POV flow is unchanged. This is a capability check, not a permission prompt; never stall on it.

**Org62 engagement check (same pass, silent).** Offer optional pre-fill from an existing Org62 engagement: "Want to pull context from an Org62 engagement, or start fresh?" The alias comes from the `ORG62_ALIAS` env var (default `org62`); identity is the logged-in session user (never hardcoded).
- If the user accepts, or names/pastes a `Partner_Engagement__c`/Account/Opportunity ID, load `refs/org62-prefill.md` and follow it (list-pick or ID → hydrate → emit the engagement-context block into Stage 2).
- If the user declines, do not load the ref — the POV flow is unchanged. This is an offer, not a gate; never stall, and nothing it returns is ever required.

Execute all of the following immediately and in parallel. Output one plain-English status line as each action begins:

- Fetch the URL — extract: what the product does, who it serves, key differentiators, any named customers
- Search "{company} Salesforce AppExchange" — find any existing listing, integration, or prior partnership signal
- Search "{company} competitors alternatives" — identify the top 2–3 named competitors
- Search "{company} customers case studies reviews" — find traction signals and named reference accounts
- Search "{industry/vertical} trends challenges {current year}" — market context for the problem space
- Search "{company} founding team leadership" — signal on domain expertise and technical capacity

**Load references lazily — do not load everything upfront:**
- Load `refs/og-tech-strategy-framework.md` now (the framework spine, used throughout).
- Load `refs/industry-alignment.md` now — it is a slim router. Use it to identify the partner's primary vertical, then check the lookup table and **state explicitly which path applies**:
  - **Predetermined file exists** → load only that one file from `refs/verticals/` (do not load the others) and note in Stage 2 that the vertical data is sourced from the predefined file.
  - **No matching file** → say so plainly (e.g., "No predefined vertical file for [vertical] — researching it live"), then conduct targeted research on that specific industry to populate the same schema the vertical files use (Industry Cloud, market size + CAGR with named sources, focus areas, use cases, regulatory drivers, KPIs, MVP signal). Skip the extra research only if Stage 1's broad searches already surfaced this data. Follow the router's "Vertical Not Listed" guidance, and offer to persist the result as a new `refs/verticals/` file (see README → Keeping industry data fresh).
- Do **not** load `refs/pull-through-gtm.md` yet — defer it until you populate the Commercial Context (Stage 2 commercial sub-step or Stage 8 step 12).

Identify the partner's primary vertical and commercial model type (ISVforce or OEM/Embedded) from research. Then move immediately to Stage 2 — do not surface a research summary to the user yet. Stage 2 presents findings in structured form alongside the pre-filled POV draft.

**Stage 2 — Pre-fill + Propose**
Using research findings, pre-fill every POV section with what can be inferred or confirmed. Mark each with its confidence:
- `[confirmed from research]` — found on website, AppExchange, press, or case studies
- `[from internal Slack — confirm]` — sourced from an internal partner/deal Slack channel with `@author, date` attribution; high value but unconfirmed certainty — never hardens to confirmed without partner confirmation (see `refs/slack-insights.md`)
- `[from Org62 engagement — confirm]` — sourced from a linked Org62 `Partner_Engagement__c` (partner, pilot customer, opportunity use-case); high value but unconfirmed — never hardens to confirmed without partner confirmation (see `refs/org62-prefill.md`)
- `[proposed — confirm]` — inferred from vertical, product category, or competitive context; needs partner confirmation
- `[TBD — clarification needed]` — could not be determined from research; will be asked in Stage 3

Using the matched vertical file already loaded from `refs/verticals/` (see Stage 1), propose 3–5 industry-oriented KPIs with suggested targets relevant to the detected vertical and use cases. Label them `[proposed KPIs — confirm or modify]`. When you reach the Commercial Context, load `refs/pull-through-gtm.md` then — not before.

Present to the user:
1. Pre-filled POV draft with confidence labels
2. Proposed KPIs
3. Clarifying questions — a focused set of targeted questions for items marked TBD that are critical to the POV (soft target ~5; up to ~8 when genuine gaps remain — see Stage 3)

Do not ask for information already found in research. Do not ask for information derivable from the matched vertical file in refs/verticals/. Do not run a broad discovery session — only surface the minimum gaps.

**Stage 3 — Clarify**
Ask the targeted questions identified in Stage 2 — a soft target of ~5, expanding to ~8 only when genuine gaps remain (see the relaxation note below). Do not pad to hit a number, and do not drop a real gap to stay under one. Capture verbatim answers — do not paraphrase or summarize.

**Reconcile against Slack first (when `refs/slack-insights.md` was loaded).** Before asking, suppress questions Slack already answered, narrow partially-answered ones to the residual, and convert any Slack-vs-research conflict into a question. The hard ≤5 cap relaxes to a soft target of **~5–8** when genuine gaps remain — close a TBD now rather than ship it. Still one batched pass; still capture named entities in that pass. Make the pruning visible (e.g. "4 gaps pre-answered from #partner-channel; 6 genuine gaps remain").

**Capture named entities in the same pass — never split a question into two rounds.** Several Stage 5 checks and scorecard Strong Signals require a *name*, not a category: the named pilot/design partner, the named Salesforce exec sponsor, the named co-sell contact. When a question's useful answer is a name, do not ask the categorical question first and chase the name in a second `AskUserQuestion` round — that wastes a turn. Instead, get the name in one pass:
- Prefer a single free-text question that asks for the name directly (e.g. "Who is the named design partner or pilot customer for the MVP? (Name, or 'none yet'.)").
- If you use `AskUserQuestion` for the categorical answer (e.g. *PADA signed?*), do **not** add a separate name question — the user can add the name via the "Other" free-text on the same option, and you should phrase the option labels so a name is the natural thing to type there.
- Treat "a pilot exists but I can't name it" as a complete answer — record it as "a named pilot (under NDA)" so the proof point still counts; do not re-ask.

If additional gaps emerge during drafting: return to scripts/discovery-questions.md, select only the specific question(s) for the missing item, and ask in a single follow-up pass. Do not run a full discovery session if research covered the majority of sections.

**Stage 4 — Draft**
Load templates/pov-output.md. Generate sections in the order specified. Each section must conform to the template before moving to the next.

If the architecture section is populated and the user wants a visual/shareable architecture overview, generate a marketecture diagram — this is an optional output defined in **Stage 14** (`refs/stages/stage-14-marketecture.md`), not produced inline here.

**Stage 5 — Contradict**
Run all checks simultaneously. Surface all failures before repairing — fix in a single pass where possible.

Before delivering, surface any of these failure patterns:
- Vision Statement uses vague language ("transform," "revolutionize," "next-gen," "end-to-end")
- Product Strategy uses vague language ("be the leader," "best-in-class," "world-class," "next-gen") with no specific thesis, named product pillar, or concrete market positioning — strategy without specifics is not a strategy
- Use cases describe features, not customer outcomes
- Architecture omits SF cloud/SKU dependencies
- No named proof points or pilot customers
- Commercial model not specified
- Problem statement assumes the solution rather than diagnosing the constraint
- No competitive differentiation stated — the POV should answer "why would a customer choose this over [named alternative]?" If it cannot, solution positioning is incomplete
- Core value proposition overlaps with a known or likely Salesforce roadmap item — if Salesforce could ship this natively within 18 months, the partner's commercial model must account for it
- No defensible moat articulated — packaging uniqueness, data network effect, workflow lock-in, or deep domain expertise; if none is present, the solution is commoditizable
- Partner has no named design partners or pilot customers and no path to them — concentration and commitment risk is high
- POV cannot answer "why would Salesforce be strategically interested in this partner?" — if absent, program fit is asserted but not demonstrated
- Architectural runway not addressed — if the partner's architecture cannot support the scale of their enterprise prospects, the MVP timeline and OG Tech Strategy Framework commitment are both at risk
- Technical debt not quantified — any known debt that could block AppExchange Security Review or enterprise SLA delivery must be named and mitigated, not glossed over
- MVP scope is undefined or has no named design partner — a POV without a validated MVP definition and a committed pilot customer has not crossed the program commitment threshold
- No industry vertical named or no market data cited — a POV that asserts market significance without a named vertical, a sourced market figure, and a regulatory driver is not ready for internal Salesforce review
- No Horizon 3 articulated — if the partner cannot describe a 18–24+ month strategic ambition (new vertical, ecosystem play, AI maturation), the program investment case is incomplete
- Pull-through SKUs not identified — a Commercial Context that says "pull-through TBD" or names no specific Salesforce SKUs is not a commercial model; it is a placeholder
- No co-sell motion defined — the POV must specify how Salesforce AEs will be activated (deal registration, SPIFF, AE one-pager) or explicitly state that the GTM is marketplace-only
- Revenue share activation not addressed — if the PADA is not signed or deal registration is not set up, the revenue share model is theoretical, not operational

**Stage 6 — Validate**
Load validation/checklist.md. Run all checks simultaneously. Identify every failure in one pass, then repair. Do not deliver an output that fails its own contract.

**Stage 7 — Interactive Review**
Present the complete POV draft as Markdown. Do not generate any HTML yet.

After presenting, prompt the user exactly:
> "Review the draft above. Reply with specific changes or corrections — I will apply them and show you what changed. Reply **Approve** when ready to commit the final version."

**Review loop:**
- Accept feedback — apply all changes in one pass
- Present only the updated sections, not the full draft again
- Repeat until the user replies "Approve"

**On Approve:**
- Run Stage 5 (Contradict) and Stage 6 (Validate) on the approved draft simultaneously
- If checks pass: confirm to the user and deliver the final Markdown version
- If checks surface failures: surface them to the user before committing — do not silently repair without notification
- Append: confidence score (0.0–1.0), named assumptions, explicit TBD list

**After delivering the final POV, immediately present output options using the AskUserQuestion tool:**

Present the options as **three** `multiSelect` questions in a single `AskUserQuestion` call — the tool caps each question at 4 options.

```
AskUserQuestion({
  questions: [
    {
      question: "Which analysis & readiness outputs would you like?",
      header: "Analysis & Readiness",
      multiSelect: true,
      options: [
        {
          label: "MVP Build Plan",
          description: "Sprint-ready feature breakdown with user stories, technical requirements, phase plan, and commercial context (Stage 8)"
        },
        {
          label: "Red Team Assessment",
          description: "Adversarial analysis: competitive threats, customer churn scenarios, platform dependency scan, 18-month invalidation, Salesforce investment teardown, and commercial model pressure test (Stage 9)"
        },
        {
          label: "Partner Readiness Scorecard",
          description: "18-attribute readiness assessment (RAG + 1–3 rank) across sales, product, industry, commercial, and partner-capability fit, pre-filled from POV evidence (Stage 12)"
        },
        {
          label: "Discovery Framework",
          description: "Run the interactive discovery **workshop** (10 dimensions, How Might We, Value Proposition + Business Model canvases) and apply findings to the POV. (A pre-filled auto-capture discovery document is already produced in 'All outputs'; this pick is the full question-driven workshop.) (Stage 15)"
        }
      ]
    },
    {
      question: "Which architecture & growth outputs would you like?",
      header: "Architecture & Growth",
      multiSelect: true,
      options: [
        {
          label: "Technical & Architectural Assessment",
          description: "Build-guiding assessment vs. Salesforce Well-Architected + target-state architecture + build-ready metadata blueprint & stubs; feeds the MVP Build Plan (Stage 16)"
        },
        {
          label: "Marketecture",
          description: "HTML architecture diagram from the POV Architecture Summary — only when architecture is populated (Stage 14)"
        },
        {
          label: "Consumption Opportunities",
          description: "Build-oriented map of where Agentforce agents, Data Cloud, and other Salesforce SKUs (Shield, Backup, sandboxes) grow consumption — with named-component build blueprints and a directional, credits-only consumption pre-estimate per opportunity to seed the calculator (Stage 18). Consumption-growth-scoped; authoritative dollar sizing stays with sf-flex-estimator."
        },
        {
          label: "Competitive Assessment",
          description: "Balanced 4-dimension comparison (commercial, ecosystem, GTM, technology) of Salesforce vs. app platforms, hyperscalers, and AI providers — across both the partner's platform choice and the customer's solution choice. Makes the Salesforce case and handles objections in line (Stage 19)."
        }
      ]
    },
    {
      question: "Which presentation outputs, or the full package?",
      header: "Package",
      multiSelect: true,
      options: [
        {
          label: "All outputs + home page",
          description: "Generate every downstream artifact (Stages 8–12, 14, 15 (auto-capture discovery), 16, 17, 18, 19) plus an HTML home page that links them all (Stage 13). This is the usual choice. Supersedes the individual Analysis/Architecture/Package picks. Discovery (Stage 15) is included in **auto-capture** mode (pre-filled capture document); its interactive **workshop** mode remains a separate pick."
        },
        {
          label: "POV Presentation",
          description: "12-slide HTML deck that renders the approved POV for a stakeholder readout — problem, vision, product strategy (2 slides), solution, use cases, markets, alignment, roadmap, commercial model, recommendation (Stage 17). A faithful render of the POV, not a fundraising pitch."
        },
        {
          label: "Investor Presentation",
          description: "10-slide HTML pitch deck covering problem, solution, market, traction, business model, team, and Salesforce partnership (Stage 10). Fundraising-angled, distinct from the POV Presentation."
        },
        {
          label: "Solution Infographic",
          description: "Single-page visual overview: problem stats, solution flow, proven outcomes, and market context (Stage 11)"
        }
      ]
    }
  ]
})
```

**After the POV — output orchestration.** Handle the menu selection as follows:

- **Nothing selected** — confirm the POV is complete; note that outputs can be requested at any time.
- **"All outputs + home page"** — supersedes the individual Analysis/Architecture/Package picks: generate every downstream artifact, **including Discovery (Stage 15) in auto-capture mode** (see "Discovery in a package" below). The only menu item it does not absorb is the standalone interactive Discovery **workshop**, which remains its own pick.
- **Dispatch rule** — when the selection yields **3 or more** independent downstream artifacts (Stages 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19; "All outputs + home page" always qualifies), load `refs/parallel-dispatch.md` and follow it to fan the work out to concurrent subagents — including its two QA critic loops (the per-artifact `generate → critic → repair` pipeline on Stages 8/9/16 and the Wave-2 package completeness-critic). For 1–2 artifacts, generate inline sequentially with no critic loops.
- **Ordering (either path)** — Stage 16 (Architectural Assessment) feeds the MVP Build Plan (Stage 8), so it runs first; the independent generators (Stages 8, 9, 10, 11, 12, 14, 15, 17, 18, 19) follow. **Stage 14 gate:** generate the Marketecture only if the POV's Architecture Summary is populated — if it is empty, skip Stage 14 (this is the gate `refs/parallel-dispatch.md` defers to). Stage 13 (home page) runs **last**, built by the orchestrator after every artifact it links exists — run it whenever 2 or more downstream artifacts (Stages 8–19) were produced (a single downstream output needs no home page unless asked).
- **Discovery in a package** — when "All outputs + home page" runs, Stage 15 is generated in **auto-capture mode** in Wave 1 (pre-filled document with per-dimension capture slots, no questions). Before regenerating it, run the **capture-preservation check** (see below).
- **"Discovery Framework" selected on its own** — load `refs/discovery-framework.md` and run Stage 15 in **workshop mode** (interactive questions). A POV already exists, so follow the POV handshake: present findings as a diff (confirms / contradicts / adds) and offer to apply.
- **Capture-preservation check (before overwriting a discovery doc).** If a `{SLUG}-discovery-document.md` with filled capture slots already exists, present an `AskUserQuestion` with four options — **Archive original then regenerate** (default), **Apply captures first**, **Skip discovery regeneration**, **Overwrite anyway** — and honor the choice before (re)generating discovery. A doc that is absent or all-`[pending]` regenerates with no prompt. Full procedure in `refs/parallel-dispatch.md`.
- **"Technical & Architectural Assessment" selected** — load `refs/architecture-assessment.md` and run Stage 16. It requires an approved POV; if the MVP Build Plan is also wanted, run the Assessment first.

**Stages 8–19 — Optional outputs (lazily loaded).** Each stage's full definition lives in its own file under `refs/stages/` (see the router table below) — keeping them out of the base context. When the user selects any option from the menu above, or asks for an output by name, **load only the matching per-stage file(s)** from the router table (for example, `refs/stages/stage-08-mvp-build-plan.md` for the MVP Build Plan) and follow them. Load only what was selected — never the whole set.

| Stage | Output | Instruction file |
|---|---|---|
| 8  | MVP Build Plan | `refs/stages/stage-08-mvp-build-plan.md` |
| 9  | Red Team Assessment | `refs/stages/stage-09-red-team.md` |
| 10 | Investor Presentation | `refs/stages/stage-10-investor-presentation.md` |
| 11 | Solution Infographic | `refs/stages/stage-11-solution-infographic.md` |
| 12 | Partner Readiness Scorecard | `refs/stages/stage-12-partner-readiness-scorecard.md` |
| 13 | Output Home Page / Solution Package | `refs/stages/stage-13-output-home-page.md` |
| 14 | Marketecture | `refs/stages/stage-14-marketecture.md` |
| 15 | Discovery Framework | `refs/stages/stage-15-discovery-framework.md` |
| 16 | Technical & Architectural Assessment | `refs/stages/stage-16-architecture-assessment.md` |
| 17 | POV Presentation | `refs/stages/stage-17-pov-presentation.md` |
| 18 | Consumption Opportunities | `refs/stages/stage-18-consumption-opportunities.md` |
| 19 | Competitive Assessment | `refs/stages/stage-19-competitive-assessment.md` |
