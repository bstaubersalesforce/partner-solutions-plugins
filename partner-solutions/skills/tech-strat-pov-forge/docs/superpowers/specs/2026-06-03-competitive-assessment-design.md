# Competitive Assessment Artifact (Stage 19) — Design Spec

**Date:** 2026-06-03
**Status:** Approved (brainstorming)
**Skill:** pov-builder

## Overview

A new optional output, **Stage 19 — Competitive Assessment.** A balanced, four-dimension comparison of Salesforce against three competitor categories, viewed through two layers (the partner's build-platform choice and the customer's solution choice). It makes a credible case for Salesforce while handling objections in line, dimension by dimension.

Like every optional stage (8–18), it draws from the **approved POV** and the matched vertical file, is lazily loaded, and follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`. Dual-format (`.md` + own styled `.html`). Slots into the "Architecture & Growth" menu group, included in every "All outputs + home page" package, and available as a standalone pick.

This is a single, self-contained feature: one new stage, one new ref, two new templates, one new checklist, plus wiring edits to `SKILL.md`, the parallel-dispatch ref, and `README.md`.

---

## Purpose & boundaries

A **platform/tooling-comparison artifact**. It compares Salesforce as a foundation against alternative platforms and AI tools, across four dimensions, for two distinct buyers. It is **independent** — stands alone, may run without Stage 16.

**Anti-overlap guard (must be stated in the instructions):**
- **Not the Red Team (Stage 9).** Red Team attacks *the partner's solution* (how it fails, who steals its customers). This assesses *Salesforce vs. alternative platforms/tools*. Opposite direction — do not restate Red Team threats here.
- **Not the pull-through commercial model** — that is the POV's ISV Commercial Model section + `refs/pull-through-gtm.md`. This compares commercial *models across platforms*, not the partner's own SKU pull-through math.
- **Not Flex Credit dollar sizing** — that is the `sf-flex-estimator` skill. The Commercial dimension gives a qualitative comparison only and points to `sf-flex-estimator` for dollars.
- **Not the core-solution architecture** — that is Stage 16. Technology comparison here is platform-vs-platform, not this partner's target-state architecture.

## Structural spine (Approach B — dimension-major)

One pass through four dimensions. Each dimension is a self-contained block: **scorecard → two-layer read → in-line objection→response → mandatory concession.** No layer-level repetition — each dimension is analyzed once, and the two audiences are threaded *within* each dimension.

### The three competitor categories (fixed, with POV-named specifics inside each)

- **App / low-code platforms** — seed specifics: Microsoft Power Platform, ServiceNow, OutSystems
- **Hyperscalers** — AWS, Azure, GCP
- **AI providers** — OpenAI, Anthropic, Google (Gemini / Vertex)

Categories are fixed every run for completeness. Within each, name the **specific** competitors the partner actually faces (drawn from Stage 1 research and the POV's competitive-differentiation section) rather than generic placeholders.

### The four dimensions

1. **Commercial Model** — pricing shape, license vs. consumption, partner economics (rev-share / marketplace take-rate), cost-to-customer predictability.
2. **Ecosystem** — marketplace reach (AppExchange vs. alternatives), pre-built data model & integrations, installed base, ISV tooling maturity.
3. **GTM Program** — co-sell motion, AE activation, partner program structure & incentives, marketplace distribution, field reach.
4. **Technology** — platform completeness (data + app + AI in one), trust/compliance layer, AI stack (Agentforce / Data Cloud vs. raw model APIs), build-vs-assemble effort, lock-in / portability.

### What each dimension block contains

- **Scorecard** — Salesforce vs. the 3 categories, with a qualitative rating + one-line rationale per category. Every claim confidence-labeled with the skill's existing labels (`[confirmed from research]` / `[proposed — confirm]` / `[TBD — clarification needed]`) and sourced or attributed.
- **Two-layer read** — two short lenses: *"For the partner building on it"* and *"For the customer buying the result."*
- **In-line objection → response** — the sharpest pushback a buyer raises in this dimension, with a response that **concedes the valid part before countering**.
- **Mandatory concession** — at least one area where a competitor is genuinely stronger in this dimension. (Validation fails without it — see contract.)

### Document structure (both `.md` and `.html`)

1. **Header** — partner name, date, Org62 stage, "Built on Salesforce" badge, standardized home-page back-link pill (`{{HOME_HREF}}`).
2. **Framing intro** — names the two layers (partner's platform choice + customer's solution choice) and the three competitor categories with the POV-named specifics. Short.
3. **Four dimension blocks** — Commercial, Ecosystem, GTM Program, Technology, each as specified above (scorecard + two-layer read + objection→response + concession).
4. **Synthesis** — the 3–4 strongest Salesforce arguments, the 2–3 objections most likely to land, and a one-line "where Salesforce is genuinely not the right choice" honesty note.
5. **Footer note** — pointer to `sf-flex-estimator` (Commercial dollars), Stage 9 Red Team (solution risk), and Stage 16 (core architecture).

## Sourcing flow (curated ref + live top-up)

1. Load `refs/competitive-landscape.md` for durable, slow-moving platform facts per category across the 4 dimensions (confidence-labeled, carries a "last reviewed" date).
2. Pull the **POV-named specific competitors** from Stage 1 research + the POV's differentiation section.
3. **Live top-up** only for fast-moving specifics (AI-provider model capabilities, recent program/pricing changes).
4. Confidence-label every claim. On research failure, apply the existing degradation rule (log one status line, mark the affected claim `[TBD — clarification needed]`, proceed).

## Files

| File | Status | Purpose |
|---|---|---|
| `refs/stages/stage-19-competitive-assessment.md` | new | Stage definition — procedure, layer/dimension/objection logic, boundaries, fairness gate |
| `refs/competitive-landscape.md` | new | Curated ref — durable per-category facts across the 4 dimensions, confidence-labeled, "last reviewed" date |
| `templates/competitive-assessment.md` | new | Markdown template, `{{TOKEN}}` slots |
| `templates/competitive-assessment.html` | new | HTML template with visual scorecards |
| `validation/competitive-checklist.md` | new | Contract — per-dimension concession gate + vendor-pitch language ban |
| `SKILL.md` | edit | Add menu option, router row 19, dispatch-list inclusion |
| `refs/parallel-dispatch.md` | edit | Add Stage 19 to package fan-out |
| `README.md` | edit | Add to "Keeping industry data fresh" (ref freshness) + artifact list |

Both templates are filled via the HTML Output Method; fill every `{{TOKEN}}`; do not invent comparisons the POV/research does not support.

## Validation contract (`validation/competitive-checklist.md`)

Run all checks simultaneously; repair in one pass before delivering. The artifact **fails** unless:

- **Per-dimension concession (hard gate):** each of the 4 dimensions names at least one area where a competitor is genuinely stronger.
- **Concede-then-counter:** each dimension's objection→response concedes the valid part of the objection before countering.
- Every scorecard claim is confidence-labeled and sourced/attributed.
- Both layers ("for the partner" + "for the customer") are present in every dimension.
- POV-named specific competitors appear inside each category (not just generic category names).
- No vendor-pitch language or unsourced superlatives (per `SKILL.md` Delivery Voice).
- Synthesis includes the honesty note ("where Salesforce is genuinely not the right choice").
- No unfilled `{{TOKEN}}` or `[placeholder]` text.
- Anti-overlap respected (no Red Team / pull-through / Flex-dollar / Stage-16 restatement).

## Menu wiring (`SKILL.md` Stage 7)

- Add as the **4th option in the "Architecture & Growth" question group**:
  > **Competitive Assessment** — "Balanced 4-dimension comparison (commercial, ecosystem, GTM, technology) of Salesforce vs. app platforms, hyperscalers, and AI providers — across both the partner's platform choice and the customer's solution choice. Makes the Salesforce case and handles objections in line. (Stage 19)"
- Add **router row 19** pointing to `refs/stages/stage-19-competitive-assessment.md`.
- Add to the **"All outputs + home page"** dispatch list (Stages 8–18 → 8–19) and to `refs/parallel-dispatch.md`, so the full package generates it and the home page links it. It is independent (no ordering dependency), so it joins the Wave-1 independent generators.
- **Trigger phrases:** "competitive assessment", "competitive analysis", "Salesforce vs", "why Salesforce over [AWS/Azure/OpenAI]", "platform comparison", "objection handling".

**Filename convention (Stage 13):** `{SLUG}-competitive-assessment.md` + `{SLUG}-competitive-assessment.html`.

## Delivery

When run non-interactively (package dispatch), produce both `.md` and `.html` in one pass — do not pause for approval. Standalone: deliver the file path(s), surface the Synthesis before appending the full assessment.

## Out of scope (YAGNI)

- No menu-group restructuring — fits the existing "Architecture & Growth" slot.
- No new research engine — reuses Stage 1's tooling and degradation rules.
- No quantitative/dollar comparison — qualitative only; defers to `sf-flex-estimator`.
- No per-competitor deep-dive files — one curated `competitive-landscape.md` covers all three categories.
