# Red Team Expansion — Design Spec

**Date:** 2026-05-30
**Status:** Approved (scope decided)
**Skill:** pov-builder

## Problem

pov-builder's Stage 9 Red Team runs 4 adversarial frameworks. Polling the `business-red-team` skill (8 frameworks) surfaced three gaps worth closing:
1. No **investment-teardown** lens — no adversarial "why would the funder pass," and crucially no *named comparable that tried this and failed*.
2. No **commercial-model attack** — the POV's Commercial Model is asserted but never stress-tested.
3. Synthesis lacks a **blind-spot forcing function** — it has confidence + falsifier but never forces naming a risk no framework surfaced.

(Deliberately NOT adding business-red-team's #8 "Salesforce Platform Moat → SKU mapping" — pov-builder already covers that via Stage 18 Consumption Opportunities, `refs/pull-through-gtm.md`, and Stage 16.)

## Solution Overview

Expand Stage 9 from 4 frameworks to **6**, and enrich the synthesis with a **Biggest Blind Spot** element.

- **Framework 5 — Salesforce Investment Teardown** (new). Adversarial role: the Salesforce investment committee / GTP review board looking for reasons to pass on this partner. Output contract: (a) the 3 biggest holes in the partner case that would justify a "no"; (b) the one question they probably cannot answer yet; (c) a **named comparable ISV that attempted this and failed** (real, from research — or "No verified comparable found during research — gap noted"), with the specific failure mechanism that could repeat here.
- **Framework 6 — Commercial Model Pressure Test** (new). Adversarial role: a skeptic attacking the partner's commercial/pull-through model. Output contract: (a) the specific point where the pull-through math breaks (a price point, an attach-rate assumption, or an edition-dependency the target install base lacks); (b) revenue-share viability — is the PADA economics real at the partner's scale, or does it only work at a customer count they don't have?; (c) one named alternative (a cheaper competitor, a Salesforce-native path, or "do nothing") that makes the partner's commercial premise hard to defend.
- **Synthesis — Biggest Blind Spot** (new element). Add a required "Biggest Blind Spot" line: the one risk that sits outside the partner's normal frame and was NOT surfaced by Frameworks 1–6. This is additive to the existing Governing finding / vulnerability table / Stopping Rule / Confidence / Assumptions / falsifier (all retained).

## Boundaries (anti-overlap)

- **Framework 5 vs. existing Framework 1 (Competitive War Game):** F1 is "a competitor kills you in the market"; F5 is "the Salesforce funder declines to invest." Different adversary (market rival vs. internal investment board), different artifact (competitive moves vs. go/no-go holes + named-failure precedent).
- **Framework 6 vs. the POV Commercial Model section and `pull-through-gtm.md`:** those *build* the commercial model; F6 *attacks* it. F6 must reference the POV's stated model and find where it breaks — it does not restate or re-derive it.
- **Framework 5/6 vs. Stage 18 Consumption Opportunities:** Stage 18 maps consumption *growth*; F5/F6 are adversarial risk lenses. No overlap.

## Files Touched

**Modified:**
- `refs/red-team-lenses.md` — add Framework 5 (Salesforce Investment Teardown) and Framework 6 (Commercial Model Pressure Test), each with adversarial role + attack vectors + output contract, matching the existing 4 lenses' structure. Update the intro line "Four adversarial frameworks" → "Six adversarial frameworks".
- `templates/red-team-assessment.md` — add `## Framework 5: Salesforce Investment Teardown` and `## Framework 6: Commercial Model Pressure Test` sections (after Framework 4, before Synthesis), each with the fill structure for its output contract. Add a **Biggest Blind Spot** line to the Synthesis section.
- `refs/stages/stage-09-red-team.md` — update "Run all 4 frameworks" → "Run all 6 frameworks" and add the two new framework lines (5, 6) to the numbered list. Note the Biggest Blind Spot requirement in the deliver list.
- `validation/red-team-checklist.md` — update "All 4 frameworks present" → "All 6 frameworks present: …" (add the two names). Add specificity checks: Investment Teardown names a real comparable-failure (or explicit gap); Commercial Model Pressure Test names the specific break point. Add a Synthesis check: Biggest Blind Spot present and is not a restatement of a Framework 1–6 finding.
- `SKILL.md` — the Stage 5 progress-reporting example mentions "Framework 2 — Customer Exit Simulation" (no change). The Red Team menu option description (line ~211) lists the framework lenses ("competitive threats, customer churn scenarios, platform dependency scan, and 18-month invalidation scenarios") — extend it to add the two new lenses (Salesforce investment teardown, commercial model pressure test). No hard "4" count appears in SKILL.md.
- `tests/validate_skill.py` — new check `t_red_team_frameworks`: `refs/red-team-lenses.md`, `templates/red-team-assessment.md`, and `validation/red-team-checklist.md` all reference Framework 5 and Framework 6 by name (Investment Teardown, Commercial Model Pressure Test), and the checklist says "6 frameworks". This keeps the three red-team files in sync the way the discovery dimension-parity check does.
- `README.md` — two spots: the Red Team Assessment table row (line ~19) "4 adversarial frameworks" → "6 adversarial frameworks" with the two new lens names added; and the repo-structure tree comment (line ~81) "# 4 adversarial frameworks" → "# 6 adversarial frameworks".

## Validation Additions (`tests/validate_skill.py`)

1. `t_red_team_frameworks` — assert all three red-team files (lenses ref, template, checklist) contain "Salesforce Investment Teardown" and "Commercial Model Pressure Test"; assert the checklist contains "6 frameworks" (and no longer "4 frameworks"); assert the template has `## Framework 5:` and `## Framework 6:` headings and a "Biggest Blind Spot" line.

**Existing checks that must stay green:** orphan/reference integrity, no-hardcoded-literals, brace checks (template has no `{{TOKEN}}` — it's Markdown-native, rendered via document-shell at Stage 13), stage-file schema (`**Stage 9 —` heading intact).

## Testing Approach

TDD against `validate_skill.py` (add check → RED → implement → GREEN → commit), per-task subagent execution with spec + quality review, final whole-feature review. The red team artifact is Markdown-native (no own HTML template); its HTML view is rendered via `scripts/md-to-html.py` + document-shell at Stage 13 — no template/token work needed here.

## Out of Scope (YAGNI)

- business-red-team's Framework 8 (Salesforce Platform Moat / SKU mapping) — already covered by Stage 18 + pull-through-gtm + Stage 16.
- No change to the red team's dispatch placement (already in Wave 1) or filename.
- No new HTML template (red team stays Markdown-native, rendered via the shared shell).

## Success Criteria

- Stage 9 runs 6 frameworks; the lenses ref, template, stage doc, and checklist all agree on the 6 (and the two new ones are named identically everywhere).
- Framework 5 forces a named comparable-failure (or an explicit research gap); Framework 6 names the specific commercial break point.
- Synthesis requires a Biggest Blind Spot distinct from Frameworks 1–6, alongside the retained confidence/assumptions/falsifier/stopping-rule.
- Validator passes with the new check; nothing else regresses.
- README and any SKILL.md framework-count references updated.
