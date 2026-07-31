# Competitive Assessment Artifact (Stage 19) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional **Stage 19 — Competitive Assessment** output to the pov-builder skill: a balanced, four-dimension (commercial, ecosystem, GTM, technology) comparison of Salesforce vs. app platforms, hyperscalers, and AI providers, across two layers (partner platform choice + customer solution choice), that makes the Salesforce case and handles objections in line.

**Architecture:** Follows the established optional-stage pattern (mirrors Stage 18 Consumption Opportunities exactly): a lazily-loaded stage definition under `refs/stages/`, a curated reference file, dual `.md` + `.html` token templates filled via the HTML Output Method, a validation checklist, and wiring into `SKILL.md` (menu + router + dispatch), `refs/parallel-dispatch.md`, `refs/stages/stage-13-output-home-page.md`, `README.md`, and the structural validation suite `tests/validate_skill.py`.

**Tech Stack:** Markdown instruction/template files, HTML template with `{{UPPER_SNAKE}}` tokens, Python 3 validation suite (`tests/validate_skill.py`), git with a pre-commit hook that runs the suite.

**Why the validation suite drives this plan:** The skill has no behavioral unit tests of LLM output; its "tests" are the structural invariants in `tests/validate_skill.py` (file existence, reference integrity, token hygiene, stage contiguity, menu consistency). Several of these hardcode the stage range as 8–18. The suite is therefore the failing test we drive against: Task 1 encodes the Stage-19 expectations into the suite (red), and Tasks 2–8 make it green. The pre-commit hook blocks any commit while the suite fails, so commits land only at green checkpoints.

**Ordering note (mutual invariants):** `t_refs_exist` requires every path named in the instruction corpus to exist, and `t_no_orphans` requires every `templates/`, `validation/`, and top-level `refs/` file to be referenced by the instruction corpus. The new leaf files (ref, templates, checklist) and the stage file that references them are mutually dependent, so the suite only returns to full green once the whole group (Tasks 1–8) is complete. Each task below states the expected suite state honestly; intermediate commits happen with `--no-verify` **only** at the two explicitly marked points, and the final task confirms a clean green commit.

---

## File Structure

**New files:**
- `refs/competitive-landscape.md` — curated, slow-moving platform-level facts per competitor category across the 4 dimensions, confidence-labeled, with a "last reviewed" date. The sourcing spine; the stage tops up fast-movers live.
- `refs/stages/stage-19-competitive-assessment.md` — the stage definition: procedure, layer/dimension/objection logic, boundaries, fairness gate, filename, delivery.
- `templates/competitive-assessment.md` — Markdown template (the download).
- `templates/competitive-assessment.html` — styled HTML template with `{{TOKEN}}` slots (the view).
- `validation/competitive-checklist.md` — pre-delivery contract incl. the per-dimension concession gate.

**Modified files:**
- `tests/validate_skill.py` — add Stage 19 to the structural invariants + two new checks.
- `SKILL.md` — menu option (4th in "Architecture & Growth"), router row 19, dispatch lists, optional-outputs header range.
- `refs/parallel-dispatch.md` — Stage 19 in the threshold list, Wave 1, and a dispatch brief.
- `refs/stages/stage-13-output-home-page.md` — filename convention + card ordering.
- `README.md` — artifact table row, "What it produces" prose, repo structure, freshness section.

---

## Task 1: Encode Stage 19 expectations into the validation suite (the failing test)

**Files:**
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Add Stage 19 to the `DOWNSTREAM_STAGES` map**

In `tests/validate_skill.py`, find the `DOWNSTREAM_STAGES` dict (ends at the line with `18: "refs/stages/stage-18-consumption-opportunities.md",`). Add the Stage 19 entry as the last item before the closing brace:

```python
    18: "refs/stages/stage-18-consumption-opportunities.md",
    19: "refs/stages/stage-19-competitive-assessment.md",
}
```

- [ ] **Step 2: Register the new HTML template in the three template lists**

In `TEMPLATE_HTML`, add the new template after the consumption entry:

```python
    "templates/consumption-opportunities.html",
    "templates/competitive-assessment.html",
]
```

In `HOME_LINK_TEMPLATES`, add it after the consumption entry:

```python
    "templates/consumption-opportunities.html",
    "templates/competitive-assessment.html",
]
```

In `HTML_STAGE_FILES` (the list of stage files that must point to the HTML Output Method ref), add the new stage file after the Stage 17 entry:

```python
    "refs/stages/stage-17-pov-presentation.md",
    "refs/stages/stage-19-competitive-assessment.md",
]
```

- [ ] **Step 3: Extend the stage-contiguity assertion to 1..19**

Find `t_stage_contiguous` and change its assertion range from 19 to 20:

```python
@check("Stages are contiguous 1..19 across the instructions (no gaps or duplicates)")
def t_stage_contiguous():
    nums = sorted(int(n) for n in re.findall(r"^\*\*Stage (\d+) —", instructions(), re.M))
    assert nums == list(range(1, 20)), f"stage sequence is {nums}"
```

(Note: `t_optional_outputs_header_range` derives `want_hi` from `max(DOWNSTREAM_STAGES)`, so adding 19 to the map in Step 1 automatically makes it require the SKILL.md header to read "Stages 8–19" — no edit needed here.)

- [ ] **Step 4: Add a Stage-19 file-wiring check (mirrors the Stage-18 check)**

Immediately after the `t_consumption_stage_files` function, add:

```python
@check("Competitive Assessment stage 19 files exist and are wired")
def t_competitive_stage_files():
    assert exists("refs/stages/stage-19-competitive-assessment.md"), "stage-19 file missing"
    assert exists("templates/competitive-assessment.md"), "competitive md template missing"
    assert exists("templates/competitive-assessment.html"), "competitive html template missing"
    assert exists("validation/competitive-checklist.md"), "competitive checklist missing"
    assert exists("refs/competitive-landscape.md"), "competitive-landscape ref missing"
    skill = read("SKILL.md")
    assert "refs/stages/stage-19-competitive-assessment.md" in skill, "SKILL.md router missing stage 19"
    stage = read("refs/stages/stage-19-competitive-assessment.md")
    assert re.search(r"^\*\*Stage 19 —", stage, re.M), "stage-19 missing '**Stage 19 —' heading"
```

- [ ] **Step 5: Add a Stage-13 filename check and a dispatch check for Stage 19**

Immediately after the `t_stage13_consumption_filename` function, add:

```python
@check("Stage 13 references the competitive-assessment filename")
def t_stage13_competitive_filename():
    s = read("refs/stages/stage-13-output-home-page.md")
    assert "competitive-assessment" in s, "Stage 13 does not reference {SLUG}-competitive-assessment"
```

Immediately after the `t_dispatch_consumption` function, add:

```python
@check("Parallel dispatch includes Stage 19 (Competitive Assessment) in Wave 1")
def t_dispatch_competitive():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "stage 19" in low or "competitive assessment" in low, \
        "parallel-dispatch.md missing Stage 19 / competitive assessment"
```

- [ ] **Step 6: Run the suite to verify it now fails for the expected reasons**

Run: `python3 tests/validate_skill.py`
Expected: FAIL/ERROR. The newly-added and stage-aware checks fail because the artifact files do not exist yet and the wiring is absent. Expected failing checks include: `Competitive Assessment stage 19 files exist and are wired`, `Stage 13 references the competitive-assessment filename`, `Parallel dispatch includes Stage 19...`, `SKILL.md router and refs/stages/ are in bidirectional sync` (router maps 19 to a missing file), `Stages are contiguous 1..19` (no Stage 19 heading yet), `The 'Optional outputs' section header range...` (header still says 8–18), and ERROR on the brace/token/home-link checks for `templates/competitive-assessment.html` (file not found). This confirms the suite is now demanding Stage 19.

- [ ] **Step 7: Commit the failing test (the only `--no-verify` commit besides Task 5's checkpoint)**

```bash
cd ~/.claude/skills/pov-builder
git add tests/validate_skill.py
git commit --no-verify -m "test: require Stage 19 (Competitive Assessment) in the validation suite

Encodes the Stage-19 structural invariants before the artifact exists;
suite is intentionally red until the implementation tasks land."
```

---

## Task 2: Create the curated competitive-landscape reference

**Files:**
- Create: `refs/competitive-landscape.md`

- [ ] **Step 1: Write the reference file**

Create `refs/competitive-landscape.md` with exactly this content:

````markdown
# Competitive Landscape — Platform & Tooling Reference

> Curated, slow-moving platform-level facts used by **Stage 19 — Competitive Assessment**.
> This is the sourcing spine; the stage tops up fast-moving specifics (AI-model
> capabilities, recent program/pricing changes) with live research and confidence-labels
> everything. Keep this file balanced — it must read as a fair baseline, not a pitch.
>
> **Last reviewed:** 2026-06-03. AI-provider facts drift fastest — re-verify before use.
> Refresh cadence and procedure: see README → "Keeping industry data fresh".

Confidence labels match the skill convention: `[confirmed]` (durable, widely documented),
`[proposed — confirm]` (directionally true but verify for the specific partner/date).

---

## Category A — App / low-code platforms
Specific competitors a partner most often faces: **Microsoft Power Platform, ServiceNow, OutSystems** (name the partner's actual ones from POV research).

- **Commercial model** — Per-user and per-app subscription licensing, often bundled with a broader suite (Microsoft 365, ServiceNow ITSM). Predictable seat cost; consumption add-ons (AI, automation) increasingly metered. `[confirmed]`
  - *Where they can be stronger:* a customer already standardized on the suite sees the platform as near-zero marginal cost. `[confirmed]`
- **Ecosystem** — Established app marketplaces and large installed bases; ServiceNow strong in ITSM/workflow, Power Platform strong where Microsoft 365 is entrenched. Partner-app distribution exists but is smaller and less ISV-monetization-oriented than AppExchange. `[proposed — confirm]`
- **GTM program** — Partner programs exist; co-sell maturity and ISV revenue-share economics vary and are generally less developed than Salesforce's AppExchange + co-sell motion. `[proposed — confirm]`
- **Technology** — Strong low-code app building and workflow; CRM/industry data models are thinner or bolt-on. AI is being added rapidly (Copilot/Now Assist). Lock-in to the parent suite is real. `[proposed — confirm]`

## Category B — Hyperscalers (AWS, Azure, GCP)

- **Commercial model** — Pure consumption (pay-per-use compute/storage/managed services). Maximum flexibility and no seat minimums, but cost is unpredictable at scale and shifts the FinOps burden to the customer/ISV. `[confirmed]`
  - *Where they can be stronger:* unbeatable for raw infrastructure elasticity and for workloads with no CRM/business-app component. `[confirmed]`
- **Ecosystem** — Vast catalogs of primitives and a large SI/marketplace ecosystem, but these are infrastructure building blocks, not pre-built business applications, CRM data models, or industry clouds. The ISV assembles the application layer itself. `[confirmed]`
- **GTM program** — Mature marketplace co-sell and partner programs (e.g., ISV accelerate motions); reach is broad but oriented to infrastructure spend, not line-of-business app buyers. `[proposed — confirm]`
- **Technology** — Best-in-class infrastructure breadth, AI/ML platform depth (Bedrock, Azure AI, Vertex), and portability. But "data + app + AI + trust layer in one governed platform" is the customer's/ISV's integration project, not a delivered product. `[confirmed]`

## Category C — AI providers (OpenAI, Anthropic, Google Gemini/Vertex)
> Fastest-moving category — model capabilities and pricing change frequently. Treat the points below as the durable shape and verify specifics live.

- **Commercial model** — Token/usage-metered API pricing, plus enterprise tiers. Very low entry cost; cost scales with usage and can be hard to forecast for high-volume inference. `[confirmed]`
  - *Where they can be stronger:* frontier model quality and the fastest access to the newest model capabilities. `[confirmed]`
- **Ecosystem** — Rich developer ecosystems and tooling, but no business-application layer, CRM data model, or enterprise app marketplace for distributing packaged solutions to business buyers. `[confirmed]`
- **GTM program** — Emerging partner/marketplace motions; no established enterprise field co-sell comparable to a CRM-platform vendor's AE-activated motion. `[proposed — confirm]`
- **Technology** — Frontier model quality and agentic primitives. But the buyer must supply data grounding, identity, security/compliance, workflow, and system-of-record integration — i.e., raw model APIs vs. an end-to-end governed agent platform (Agentforce + Data Cloud + trust layer). `[proposed — confirm]`

---

## Salesforce baseline (for the comparison's "home" column)
- **Commercial model** — Subscription license + consumption (Agentforce/Data Cloud Flex Credits). For ISVs: AppExchange distribution with partner revenue-share economics and PADA. `[confirmed]`
- **Ecosystem** — AppExchange (the largest enterprise B2B app marketplace), pre-built CRM + industry data models, large installed base, mature ISV tooling (managed packages, security review). `[confirmed]`
- **GTM program** — Structured partner program with AE co-sell activation, deal registration, and field reach to line-of-business buyers. `[confirmed]`
- **Technology** — Data + app + AI + trust layer in one governed platform (Agentforce, Data Cloud, Einstein Trust Layer) on a shared metadata model. Trade-off: less raw infrastructure flexibility than a hyperscaler and platform lock-in. `[confirmed]`

> **Honesty anchor:** Salesforce is *not* the right foundation for every workload — pure-infrastructure or model-only use cases with no CRM/business-app component favor a hyperscaler or AI provider. The Stage 19 synthesis must say so.
````

- [ ] **Step 2: Verify the file exists and is non-empty**

Run: `test -s refs/competitive-landscape.md && echo OK`
Expected: `OK`

- [ ] **Step 3: Do NOT commit yet** — this file is an orphan until Task 6 references it (the pre-commit hook would block the commit on `t_no_orphans`). It commits as part of the Task 8 green checkpoint.

---

## Task 3: Create the Markdown template

**Files:**
- Create: `templates/competitive-assessment.md`

- [ ] **Step 1: Write the Markdown template**

Create `templates/competitive-assessment.md` with exactly this content:

````markdown
# [Partner Name] — Competitive Assessment
**Date:** [YYYY-MM-DD] · **Org62 Opportunity Stage:** [stage] · **Built on Salesforce**
**Scope:** Salesforce vs. alternative platforms & tools across four dimensions, viewed through two layers — the **partner's** build-platform choice and the **customer's** solution choice. Makes the Salesforce case and handles objections in line. For solution-risk analysis see the **Red Team Assessment** (Stage 9); for Flex Credit cost sizing see the **sf-flex-estimator** skill; for the partner's own pull-through economics see the POV's **ISV Commercial Model**.

---

## How to read this
Two layers run through every dimension:
- **For the partner building on it** — why Salesforce is the right foundation to build the solution on vs. app platforms, hyperscalers, or AI providers.
- **For the customer buying the result** — why a customer chooses this Salesforce-built solution vs. a hyperscaler-native or AI-API-built equivalent.

Competitor categories (with the partner's actual named competitors): **app / low-code platforms** ([named, e.g. Power Platform / ServiceNow]), **hyperscalers** (AWS / Azure / GCP), **AI providers** (OpenAI / Anthropic / Google). Every claim is confidence-labeled (`[confirmed from research]` / `[proposed — confirm]` / `[TBD — clarification needed]`).

---

## Dimension 1 — Commercial Model

| Platform | Rating | Rationale (one line) |
|----------|--------|----------------------|
| **Salesforce** | [Strong / Moderate / Mixed] | [why] |
| App / low-code ([named]) | [rating] | [why] |
| Hyperscalers (AWS/Azure/GCP) | [rating] | [why] |
| AI providers ([named]) | [rating] | [why] |

**Two-layer read**
- *For the partner:* [the commercial-model argument for building on Salesforce — rev-share, AppExchange economics]
- *For the customer:* [the commercial-model argument for buying this solution — predictability, TCO]

**Objection → response**
- **Objection:** [the sharpest commercial pushback a buyer raises]
- **Response:** [concede the valid part first, then counter with specifics]

**Where a competitor is genuinely stronger:** [name the competitor and the specific commercial area where it wins — REQUIRED]

---

## Dimension 2 — Ecosystem

| Platform | Rating | Rationale (one line) |
|----------|--------|----------------------|
| **Salesforce** | [rating] | [why] |
| App / low-code ([named]) | [rating] | [why] |
| Hyperscalers (AWS/Azure/GCP) | [rating] | [why] |
| AI providers ([named]) | [rating] | [why] |

**Two-layer read**
- *For the partner:* [AppExchange distribution, pre-built data model, ISV tooling]
- *For the customer:* [installed base, integration breadth, pre-built solutions]

**Objection → response**
- **Objection:** [sharpest ecosystem pushback]
- **Response:** [concede, then counter]

**Where a competitor is genuinely stronger:** [REQUIRED]

---

## Dimension 3 — GTM Program

| Platform | Rating | Rationale (one line) |
|----------|--------|----------------------|
| **Salesforce** | [rating] | [why] |
| App / low-code ([named]) | [rating] | [why] |
| Hyperscalers (AWS/Azure/GCP) | [rating] | [why] |
| AI providers ([named]) | [rating] | [why] |

**Two-layer read**
- *For the partner:* [AE co-sell activation, deal registration, field reach]
- *For the customer:* [vendor's ability to bring qualified demand / co-sell]

**Objection → response**
- **Objection:** [sharpest GTM pushback]
- **Response:** [concede, then counter]

**Where a competitor is genuinely stronger:** [REQUIRED]

---

## Dimension 4 — Technology

| Platform | Rating | Rationale (one line) |
|----------|--------|----------------------|
| **Salesforce** | [rating] | [why] |
| App / low-code ([named]) | [rating] | [why] |
| Hyperscalers (AWS/Azure/GCP) | [rating] | [why] |
| AI providers ([named]) | [rating] | [why] |

**Two-layer read**
- *For the partner:* [data + app + AI + trust in one platform; Agentforce/Data Cloud vs. raw APIs; build-vs-assemble effort]
- *For the customer:* [governed AI, trust layer, system-of-record proximity]

**Objection → response**
- **Objection:** [sharpest technology pushback — e.g. lock-in, model freshness, infra flexibility]
- **Response:** [concede, then counter]

**Where a competitor is genuinely stronger:** [REQUIRED]

---

## Synthesis

**Strongest Salesforce arguments (3–4):**
1. [argument]
2. [argument]
3. [argument]

**Objections most likely to land (2–3):**
1. [objection] — [how to handle in the room]
2. [objection] — [how to handle in the room]

**Where Salesforce is genuinely not the right choice:** [one honest line — e.g. pure-infrastructure or model-only workloads with no CRM/business-app component]

---

## Notes
- **Solution risk:** the **Red Team Assessment** (Stage 9) attacks this partner's solution; this artifact compares platforms. They are complementary, not duplicative.
- **Cost sizing:** use the **sf-flex-estimator** skill for Flex Credit dollar modeling — this artifact gives qualitative commercial comparison only.
- **Sourcing:** durable platform facts from `refs/competitive-landscape.md` (see its "last reviewed" date); fast-moving specifics verified live and confidence-labeled.
````

- [ ] **Step 2: Verify the file exists and is non-empty**

Run: `test -s templates/competitive-assessment.md && echo OK`
Expected: `OK`

- [ ] **Step 3: Do NOT commit yet** — orphan until Task 6/8 (see Task 2 Step 3).

---

## Task 4: Create the HTML template

**Files:**
- Create: `templates/competitive-assessment.html`

- [ ] **Step 1: Write the HTML template**

Create `templates/competitive-assessment.html` with exactly this content. The token discipline matters: every `{{TOKEN}}` is `UPPER_SNAKE_CASE`; the block tokens (`_HTML`/`_BLOCKS` suffixes) each appear exactly once in the markup; `{{HOME_HREF}}` appears exactly once (in the pill anchor); the TOKEN REFERENCE comment names tokens **without** braces so a string-replace fill cannot double-fill.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{PARTNER_NAME}} — Competitive Assessment</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: "Salesforce Sans","Helvetica Neue",Helvetica,Arial,sans-serif; font-size: 15px; line-height: 1.6; color: #1a1a1a; background: #f4f6fb; }
  .page-wrapper { max-width: 1000px; margin: 32px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 16px rgba(3,45,96,0.10); overflow: hidden; }
  .doc-header { background: #032d60; color: #fff; padding: 32px 44px 26px; }
  .doc-header .eyebrow { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #7db8f7; margin-bottom: 6px; }
  .doc-header h1 { font-size: 26px; font-weight: 700; margin-bottom: 12px; }
  .doc-meta { font-size: 12.5px; color: #cfe2fb; }
  .content { padding: 32px 44px 48px; }
  .content h2 { font-size: 19px; color: #032d60; margin: 30px 0 12px; padding-bottom: 6px; border-bottom: 2px solid #0070d2; }
  .content h3 { font-size: 15px; color: #032d60; margin: 20px 0 6px; }
  .scope-note { background: #eef4fc; border-left: 4px solid #0070d2; padding: 10px 14px; font-size: 13px; color: #54698d; margin-bottom: 8px; border-radius: 0 4px 4px 0; }
  table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13.5px; margin: 0 0 18px; border: 1px solid #d8e0ec; border-radius: 6px; overflow: hidden; }
  thead tr { background: #032d60; color: #fff; }
  thead th { padding: 9px 13px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
  tbody tr:nth-child(even) { background: #f0f5ff; }
  tbody td { padding: 8px 13px; border-bottom: 1px solid #e8edf5; vertical-align: top; }
  .dim-block { border: 1px solid #d8e0ec; border-radius: 6px; padding: 14px 16px; margin-bottom: 14px; background: #fbfdff; }
  .dim-block .lbl { font-weight: 700; color: #0070d2; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; }
  .concession { background: #fff8ec; border-left: 4px solid #e6a700; padding: 8px 12px; font-size: 13px; margin-top: 8px; border-radius: 0 4px 4px 0; }
  .footer-note { font-size: 12px; color: #54698d; border-top: 1px solid #e0e6f0; padding-top: 14px; margin-top: 8px; }
  @media print { body { background: #fff; } .page-wrapper { box-shadow: none; border-radius: 0; margin: 0; max-width: 100%; } }
</style>
</head>
<body>
<!-- Home-page back-link. Fill the HOME_HREF token in the anchor below with {SLUG}-index.html when part of a package; remove this entire <a> line for a standalone artifact (no home page). The token is intentionally not repeated in this comment so a plain string-replace fills only the anchor. -->
<a href="{{HOME_HREF}}" style="position:fixed;top:14px;left:14px;z-index:9999;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:12px;font-weight:700;letter-spacing:0.04em;text-decoration:none;color:#fff;background:#0070d2;padding:7px 14px;border-radius:100px;box-shadow:0 2px 8px rgba(0,0,0,0.25);">&#8592; All artifacts</a>
<div class="page-wrapper">
  <header class="doc-header">
    <div class="eyebrow">Salesforce ISV Partner · Competitive Assessment</div>
    <h1>{{PARTNER_NAME}}</h1>
    <div class="doc-meta">{{GENERATED_DATE}} · {{OPPORTUNITY_STAGE}} · Built on Salesforce</div>
  </header>
  <main class="content">
    <div class="scope-note">Salesforce vs. app/low-code platforms, hyperscalers, and AI providers across four dimensions and two layers (partner platform choice + customer solution choice). Solution risk &rarr; Red Team Assessment (Stage 9); Flex Credit sizing &rarr; sf-flex-estimator skill; partner pull-through economics &rarr; POV ISV Commercial Model.</div>

    <h2>How to read this</h2>
{{FRAMING_HTML}}

    <h2>Dimensions</h2>
{{DIMENSION_BLOCKS}}

    <h2>Synthesis</h2>
{{SYNTHESIS_HTML}}

    <div class="footer-note">The Red Team Assessment (Stage 9) attacks this partner's solution; this artifact compares platforms. Use the sf-flex-estimator skill for Flex Credit dollar sizing — comparisons here are qualitative.</div>
  </main>
</div>

<!-- =====================================================================
     TOKEN REFERENCE — every token used in this template (fill all).
     Names are written WITHOUT braces here so each literal {{TOKEN}} appears
     exactly once in this file — a plain string-replace must not double-fill a
     glossary copy (see refs/html-output-method.md).
     PARTNER_NAME · GENERATED_DATE · OPPORTUNITY_STAGE · HOME_HREF
     FRAMING_HTML — the "How to read this" two-layer intro (one or more <p>)
     DIMENSION_BLOCKS — one <div class="dim-block">...</div> per dimension
       (Commercial, Ecosystem, GTM Program, Technology). Each block contains:
       a scorecard <table> (Salesforce + 3 categories, Rating + Rationale),
       a "Two-layer read" pair (partner / customer),
       an "Objection -> Response" pair,
       and a <div class="concession">...</div> naming where a competitor wins.
     SYNTHESIS_HTML — strongest arguments, objections likely to land, and the
       honest "where Salesforce is not the right choice" line.
===================================================================== -->
</body>
</html>
```

- [ ] **Step 2: Verify token hygiene against the suite's rules in isolation**

Run:
```bash
python3 - <<'PY'
import re
s = open("templates/competitive-assessment.html", encoding="utf-8").read()
toks = re.findall(r"\{\{([^{}]*)\}\}", s)
assert s.count("{{") == s.count("}}"), "unbalanced braces"
bad = [t for t in toks if not re.fullmatch(r"[A-Z0-9_]+", t)]
assert not bad, f"malformed tokens: {bad}"
for t in set(toks):
    if t.endswith(("_HTML","_ROWS","_BLOCKS")):
        assert s.count("{{"+t+"}}") == 1, f"block token {t} appears more than once"
assert s.count("{{HOME_HREF}}") == 1, "HOME_HREF must appear exactly once"
print("token hygiene OK")
PY
```
Expected: `token hygiene OK`

- [ ] **Step 3: Do NOT commit yet** — orphan until Task 6/8.

---

## Task 5: Create the validation checklist and the stage definition

**Files:**
- Create: `validation/competitive-checklist.md`
- Create: `refs/stages/stage-19-competitive-assessment.md`

- [ ] **Step 1: Write the validation checklist**

Create `validation/competitive-checklist.md` with exactly this content:

```markdown
# Competitive Assessment Pre-Delivery Validation Checklist

Run every check before delivering the Competitive Assessment artifact (.md + .html).

## Structure
- [ ] All four dimensions present: Commercial Model, Ecosystem, GTM Program, Technology
- [ ] Each dimension has a scorecard comparing Salesforce + all three categories (app/low-code, hyperscalers, AI providers)
- [ ] Each dimension has both layers: "for the partner building on it" AND "for the customer buying the result"
- [ ] Each dimension has an in-line Objection → Response pair
- [ ] Synthesis present: strongest arguments + objections likely to land + the honesty note
- [ ] HTML carries the standardized home-page back-link pill (`{{HOME_HREF}}` → `{SLUG}-index.html`); removed if standalone
- [ ] No `{{PLACEHOLDER}}` tokens or `[bracketed placeholder]` text remain in the rendered output

## Fairness (credibility gates — HARD FAIL)
- [ ] **Per-dimension concession:** each of the 4 dimensions names at least one area where a competitor is genuinely stronger — FAIL if any dimension lacks one
- [ ] **Concede-then-counter:** each objection's response concedes the valid part before countering
- [ ] Synthesis includes the honesty note ("where Salesforce is genuinely not the right choice")
- [ ] No vendor-pitch language or unsourced superlatives ("best-in-class", "world-class", "next-gen", "revolutionary") — per SKILL.md Delivery Voice
- [ ] Every scorecard claim is confidence-labeled (`[confirmed from research]` / `[proposed — confirm]` / `[TBD — clarification needed]`) and sourced/attributed
- [ ] POV-named specific competitors appear inside each category (not just generic category names)

## Scope discipline (no overlap)
- [ ] Does not restate Red Team threats (Stage 9 attacks the solution; this compares platforms)
- [ ] Does not restate the partner's license pull-through economics (POV ISV Commercial Model)
- [ ] No dollar/Flex-Credit sizing (that is sf-flex-estimator) — commercial comparison is qualitative
- [ ] Does not restate the core-solution target architecture (Stage 16)

## Failure → Repair
**Missing concession in a dimension:** add a genuine competitor-strength line; if none is real, the dimension's framing is biased — rebalance it.
**Objection without concession:** rewrite the response to acknowledge the valid part first.
**Unfilled token / placeholder:** fill from POV + `refs/competitive-landscape.md` or mark `[TBD — clarification needed]`.
**Vendor-pitch language:** replace superlatives with a number, a named source, or explicit uncertainty.
```

- [ ] **Step 2: Write the stage definition**

Create `refs/stages/stage-19-competitive-assessment.md` with exactly this content:

````markdown
# Stage 19 — Competitive Assessment

> Optional output stage, lazily loaded by pov-builder. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 19 — Competitive Assessment (optional)**
Triggered when the user selects "Competitive Assessment" from the output menu, or asks for a competitive analysis, platform comparison, "Salesforce vs [AWS/Azure/OpenAI/Anthropic]", or objection-handling material.

Load `refs/competitive-landscape.md` (the curated platform-facts spine — note its "last reviewed" date).
Load `templates/competitive-assessment.md` and `templates/competitive-assessment.html`.
Load `validation/competitive-checklist.md`.

**What it is — and its boundaries.** A balanced, four-dimension comparison of Salesforce vs. three competitor categories, viewed through two layers — the **partner's** build-platform choice and the **customer's** solution choice. It makes the Salesforce case and handles objections in line, dimension by dimension. It is **independent** (may run without Stage 16). It must NOT:
- restate Red Team threats — Stage 9 attacks *the partner's solution*; this compares *platforms* (opposite direction);
- restate the partner's license pull-through economics — that is the POV's ISV Commercial Model section + `refs/pull-through-gtm.md`;
- produce Flex Credit dollar sizing — that is the `sf-flex-estimator` skill. Give qualitative commercial comparison only;
- restate the core-solution target architecture — that is Stage 16.

**Competitor categories (fixed, with POV-named specifics).** Always compare against all three for completeness, and inside each, name the specific competitors this partner actually faces (from Stage 1 research and the POV's competitive-differentiation section):
- **App / low-code platforms** (e.g. Microsoft Power Platform, ServiceNow, OutSystems)
- **Hyperscalers** (AWS, Azure, GCP)
- **AI providers** (OpenAI, Anthropic, Google Gemini/Vertex)

**Sourcing.** Use `refs/competitive-landscape.md` for durable platform-level facts; top up fast-moving specifics (AI-model capabilities, recent program/pricing changes) with live research. Confidence-label every claim (`[confirmed from research]` / `[proposed — confirm]` / `[TBD — clarification needed]`). On research failure, apply the SKILL.md degradation rule (log one status line, mark the claim `[TBD]`, proceed).

**Procedure — for each of the four dimensions (Commercial Model, Ecosystem, GTM Program, Technology):**
1. Build the scorecard: Salesforce + the three categories, each with a qualitative rating and a one-line rationale.
2. Write the two-layer read: "for the partner building on it" and "for the customer buying the result."
3. Write one in-line Objection → Response — the response must **concede the valid part before countering**.
4. Name at least one area where a competitor is genuinely stronger in this dimension (the **mandatory concession** — validation fails without it).

Then write the **Synthesis**: the 3–4 strongest Salesforce arguments, the 2–3 objections most likely to land, and one honest line on where Salesforce is genuinely not the right choice.

**Fairness gate (required).** Before delivering, confirm each dimension contains a genuine competitor-strength concession and each objection concedes-then-counters. If any dimension reads one-sided, rebalance it — a competitive piece that never concedes reads as a pitch and loses credibility.

Fill both templates via the HTML Output Method (`refs/html-output-method.md`); fill every `{{TOKEN}}`; do not invent comparisons the POV/research/landscape ref does not support. Run every check in `validation/competitive-checklist.md` before delivering.

**Home-page back-link.** Set `{{HOME_HREF}}` to `{SLUG}-index.html` when part of a package; remove the back-link `<a>` line when standalone.

**Filename (Stage 13 convention):** `{SLUG}-competitive-assessment.md` + `{SLUG}-competitive-assessment.html`.

Deliver the file path(s); surface the Synthesis before appending the full assessment. When run non-interactively (package dispatch), produce both `.md` and `.html` in one pass — do not pause for approval.
````

- [ ] **Step 3: Verify both files exist**

Run: `test -s validation/competitive-checklist.md && test -s refs/stages/stage-19-competitive-assessment.md && echo OK`
Expected: `OK`

- [ ] **Step 4: Verify the stage heading and required references are present**

Run:
```bash
python3 - <<'PY'
s = open("refs/stages/stage-19-competitive-assessment.md", encoding="utf-8").read()
import re
assert re.search(r"^\*\*Stage 19 —", s, re.M), "missing '**Stage 19 —' heading"
for p in ("templates/competitive-assessment.md","templates/competitive-assessment.html",
          "validation/competitive-checklist.md","refs/competitive-landscape.md",
          "refs/html-output-method.md"):
    assert p in s, f"stage file does not reference {p}"
print("stage file OK")
PY
```
Expected: `stage file OK`

- [ ] **Step 5: Commit the artifact files at the first safe checkpoint (`--no-verify`)**

The leaf files are still orphans until SKILL.md is wired in Task 6, so the hook would block a normal commit. Commit the content group with `--no-verify`; Task 8 lands the verified green commit.

```bash
git add refs/competitive-landscape.md templates/competitive-assessment.md \
        templates/competitive-assessment.html validation/competitive-checklist.md \
        refs/stages/stage-19-competitive-assessment.md
git commit --no-verify -m "feat: add Stage 19 Competitive Assessment artifact files

Curated competitive-landscape ref, dual md+html templates, validation
checklist, and the stage-19 definition. Not yet wired into SKILL.md/router;
suite remains red until Tasks 6-8."
```

---

## Task 6: Wire Stage 19 into SKILL.md

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: Add the menu option to the "Architecture & Growth" question group**

In `SKILL.md`, find the "Consumption Opportunities" option inside the `header: "Architecture & Growth"` question (it is the last of the three options in that group). After its closing `}`, add the fourth option. Replace:

```
        {
          label: "Consumption Opportunities",
          description: "Build-oriented map of where Agentforce agents, Data Cloud, and other Salesforce SKUs (Shield, Backup, sandboxes) grow consumption — with named-component build blueprints per opportunity (Stage 18). Consumption-growth-scoped; points to sf-flex-estimator for cost sizing."
        }
      ]
    },
```

with:

```
        {
          label: "Consumption Opportunities",
          description: "Build-oriented map of where Agentforce agents, Data Cloud, and other Salesforce SKUs (Shield, Backup, sandboxes) grow consumption — with named-component build blueprints per opportunity (Stage 18). Consumption-growth-scoped; points to sf-flex-estimator for cost sizing."
        },
        {
          label: "Competitive Assessment",
          description: "Balanced 4-dimension comparison (commercial, ecosystem, GTM, technology) of Salesforce vs. app platforms, hyperscalers, and AI providers — across both the partner's platform choice and the customer's solution choice. Makes the Salesforce case and handles objections in line (Stage 19)."
        }
      ]
    },
```

- [ ] **Step 2: Add Stage 19 to the "All outputs + home page" description**

Find the "All outputs + home page" option description (it lists `Stages 8–12, 14, 15 (auto-capture discovery), 16, 17, 18`). Replace that span:

```
          description: "Generate every downstream artifact (Stages 8–12, 14, 15 (auto-capture discovery), 16, 17, 18) plus an HTML home page that links them all (Stage 13).
```

with:

```
          description: "Generate every downstream artifact (Stages 8–12, 14, 15 (auto-capture discovery), 16, 17, 18, 19) plus an HTML home page that links them all (Stage 13).
```

- [ ] **Step 3: Add Stage 19 to the two dispatch-rule stage lists**

Find the Dispatch rule sentence:

```
- **Dispatch rule** — when the selection yields **3 or more** independent downstream artifacts (Stages 8, 9, 10, 11, 12, 14, 15, 16, 17, 18; "All outputs + home page" always qualifies), load `refs/parallel-dispatch.md`
```

Replace `14, 15, 16, 17, 18;` with `14, 15, 16, 17, 18, 19;`.

Find the Ordering sentence:

```
the independent generators (Stages 8, 9, 10, 11, 12, 14, 15, 17, 18) follow.
```

Replace `14, 15, 17, 18)` with `14, 15, 17, 18, 19)`.

- [ ] **Step 4: Bump the "Optional outputs" section header range (and the prose range)**

Find the section header:

```
**Stages 8–18 — Optional outputs (lazily loaded).**
```

Replace `8–18` with `8–19`. (This is the only range the suite asserts, via `t_optional_outputs_header_range`.)

Also, for accuracy, update the prose `(Stages 8–18)` in the Ordering bullet (the phrase `when 2 or more downstream artifacts (Stages 8–18) were produced`). Replace that single `(Stages 8–18)` with `(Stages 8–19)`. Leave the dispatch-rule and ordering numeric lists handled in Step 3.

- [ ] **Step 5: Add the router-table row**

Find the last router-table row:

```
| 18 | Consumption Opportunities | `refs/stages/stage-18-consumption-opportunities.md` |
```

Add immediately after it:

```
| 19 | Competitive Assessment | `refs/stages/stage-19-competitive-assessment.md` |
```

- [ ] **Step 6: Verify the SKILL.md edits**

Run:
```bash
python3 - <<'PY'
s = open("SKILL.md", encoding="utf-8").read()
assert "Competitive Assessment" in s
assert "refs/stages/stage-19-competitive-assessment.md" in s
assert "**Stages 8–19 — Optional outputs" in s
assert "8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19;" in s
print("SKILL.md OK")
PY
```
Expected: `SKILL.md OK`

- [ ] **Step 7: Do NOT commit yet** — `refs/parallel-dispatch.md` and `stage-13` still need Stage 19, and the suite's `t_dispatch_competitive` / `t_stage13_competitive_filename` checks would fail. Commit at Task 8.

---

## Task 7: Wire Stage 19 into parallel-dispatch and the home page

**Files:**
- Modify: `refs/parallel-dispatch.md`
- Modify: `refs/stages/stage-13-output-home-page.md`

- [ ] **Step 1: Add Stage 19 to the threshold-counting list**

In `refs/parallel-dispatch.md`, find:

```
Count only the independent **downstream artifact** stages: 8, 9, 10, 11, 12, 14, 15 (auto-capture), 16, 17, 18.
```

Replace `16, 17, 18.` with `16, 17, 18, 19.`

- [ ] **Step 2: Add Stage 19 to the Wave 1 list**

Find:

```
- **Wave 1 — all other selected artifacts** (Stages 8, 9, 10, 11, 12, 14, 15, 17, 18), dispatched **concurrently**,
```

Replace `15, 17, 18),` with `15, 17, 18, 19),`.

- [ ] **Step 3: Add the Stage 19 dispatch brief**

Find the "Consumption (Stage 18) brief." paragraph (it ends with `...give qualitative consumption signals, not dollar sizing."`). Add immediately after it a new paragraph:

```
**Competitive (Stage 19) brief.** Stage 19 is independent (needs only the approved POV) and runs in Wave 1. Its brief states: "Produce the Competitive Assessment artifact (.md + .html) in one pass, non-interactively. Compare Salesforce vs. app platforms, hyperscalers, and AI providers across the four dimensions and both layers; load `refs/competitive-landscape.md` for durable facts and top up fast-movers live. Each dimension MUST name at least one area where a competitor is genuinely stronger, and each objection must concede before countering. Do not restate Red Team threats (Stage 9), the pull-through economics (POV Commercial Model), or dollar sizing (sf-flex-estimator)."
```

- [ ] **Step 4: Add the filename to the Stage 13 convention list**

In `refs/stages/stage-13-output-home-page.md`, find:

```
- `SLUG-consumption-opportunities.md` + `SLUG-consumption-opportunities.html`
- `SLUG-index.html` (the home page)
```

Insert the competitive line between them:

```
- `SLUG-consumption-opportunities.md` + `SLUG-consumption-opportunities.html`
- `SLUG-competitive-assessment.md` + `SLUG-competitive-assessment.html`
- `SLUG-index.html` (the home page)
```

- [ ] **Step 5: Add Competitive to the card ordering**

Find the card-order line:

```
3. Order cards: POV (Core) first, then Presentation, Discovery, Build, Risk, Sales, Visual, Readiness, Architecture, Consumption — listing only what exists. (POV Presentation = HTML-native, View ↗ only, no Markdown button.)
   (Consumption = the Consumption Opportunities artifact; View ↗ + Markdown ↓.)
```

Replace with:

```
3. Order cards: POV (Core) first, then Presentation, Discovery, Build, Risk, Sales, Visual, Readiness, Architecture, Consumption, Competitive — listing only what exists. (POV Presentation = HTML-native, View ↗ only, no Markdown button.)
   (Consumption = the Consumption Opportunities artifact; View ↗ + Markdown ↓.)
   (Competitive = the Competitive Assessment artifact; View ↗ + Markdown ↓.)
```

Also find the Markdown-button list in the `{{ARTIFACT_CARDS}}` step:

```
include the **Markdown ↓** button only when a `.md` source exists (POV, MVP Build Plan, Red Team, Scorecard, Technical & Architectural Assessment).
```

Replace `Technical & Architectural Assessment).` with `Technical & Architectural Assessment, Consumption Opportunities, Competitive Assessment).`

- [ ] **Step 6: Verify the dispatch + home-page edits**

Run:
```bash
python3 - <<'PY'
d = open("refs/parallel-dispatch.md", encoding="utf-8").read()
assert "16, 17, 18, 19." in d and "15, 17, 18, 19)" in d
assert "Competitive (Stage 19) brief." in d
s = open("refs/stages/stage-13-output-home-page.md", encoding="utf-8").read()
assert "competitive-assessment" in s
assert "Consumption, Competitive" in s
print("dispatch + stage13 OK")
PY
```
Expected: `dispatch + stage13 OK`

- [ ] **Step 7: Do NOT commit yet** — README still references the stage count/range and the suite's full green is confirmed in Task 8.

---

## Task 8: Run the full suite green and commit the wired feature

**Files:**
- (No new edits — this task verifies and commits Tasks 2–7.)

- [ ] **Step 1: Run the full validation suite**

Run: `python3 tests/validate_skill.py`
Expected: PASS — all checks, including the new `Competitive Assessment stage 19 files exist and are wired`, `Stage 13 references the competitive-assessment filename`, `Parallel dispatch includes Stage 19 (Competitive Assessment) in Wave 1`, `Stages are contiguous 1..19`, and `The 'Optional outputs' section header range matches the downstream stage map (8..max)`. The summary line should read `62/62 passed` (59 prior + 3 new checks).

- [ ] **Step 2: If any check fails, repair before committing**

Read the named failure and fix the corresponding file from Tasks 2–7. Common causes: a token that is not `UPPER_SNAKE_CASE` in the HTML template; the stage heading not matching `^\*\*Stage 19 —`; a SKILL.md list span not updated; a vertical literal accidentally typed into the HTML. Re-run until green.

- [ ] **Step 3: Commit the now-green feature (normal commit — hook runs the suite)**

```bash
git add SKILL.md refs/parallel-dispatch.md refs/stages/stage-13-output-home-page.md \
        refs/competitive-landscape.md templates/competitive-assessment.md \
        templates/competitive-assessment.html validation/competitive-checklist.md \
        refs/stages/stage-19-competitive-assessment.md
git commit -m "feat: wire Stage 19 Competitive Assessment into menu, router, dispatch

Adds the Competitive Assessment to the Architecture & Growth output menu,
the router table, the parallel-dispatch waves, and the home-page card order.
Validation suite green at 62/62."
```

The pre-commit hook re-runs `tests/validate_skill.py`; the commit succeeds only if it passes, confirming the green state.

---

## Task 9: Document the artifact in the README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add the artifact table row**

In `README.md`, find the Consumption Opportunities row in the "What it produces" table (line containing `**Consumption Opportunities**` ... `Stage 18`). Add immediately after it:

```
| **Competitive Assessment** (balanced Salesforce-vs-platforms comparison across commercial, ecosystem, GTM, technology — two layers, objections handled in line) | Markdown + HTML | "All outputs" · "competitive assessment" / "Salesforce vs AWS/Azure/OpenAI" — Stage 19 |
```

- [ ] **Step 2: Add Stage 19 to the "How it works" prose**

Find the sentence beginning `Stages 8–12, 14, 15, 16, 17, and 18 (...)`. Update the range and the parenthetical list to include Stage 19:

Replace `Stages 8–12, 14, 15, 16, 17, and 18 (` with `Stages 8–12, 14, 15, 16, 17, 18, and 19 (`, and within that parenthetical add `, and the **Competitive Assessment**` immediately before the closing `)` that precedes "are optional outputs". Concretely, replace:

```
the **POV presentation deck**, and the **Consumption Opportunities** map) are optional outputs
```

with:

```
the **POV presentation deck**, the **Consumption Opportunities** map, and the **Competitive Assessment**) are optional outputs
```

- [ ] **Step 3: Add the template and validation files to the repo-structure tree**

Find the repo-structure block lines:

```
│   └── consumption-opportunities.md / .html  # Consumption Opportunities map (Markdown + styled HTML)
```

Add immediately after it (same indentation):

```
│   └── competitive-assessment.md / .html     # Competitive Assessment (Markdown + styled HTML)
```

Find:

```
│   └── consumption-checklist.md      # Consumption Opportunities validation
```

Add immediately after it:

```
│   └── competitive-checklist.md      # Competitive Assessment validation
```

- [ ] **Step 4: Add the landscape ref to the "Keeping industry data fresh" section**

In the "## Keeping industry data fresh" section, after the opening paragraph (the one beginning `Market figures, KPIs, and regulatory drivers age.`), add a new paragraph:

```
**Competitive landscape.** `refs/competitive-landscape.md` carries durable platform-level facts about app platforms, hyperscalers, and AI providers, used by the **Competitive Assessment** (Stage 19). It has its own **"Last reviewed"** date at the top. AI-provider capabilities and pricing drift fastest — re-verify this file before any high-stakes competitive deliverable, and update the "Last reviewed" date when you do.
```

- [ ] **Step 5: Run the full suite (README does not affect structural checks, but confirm nothing regressed)**

Run: `python3 tests/validate_skill.py`
Expected: PASS — `62/62 passed`. (README is not asserted by these checks, but the run confirms no accidental edit elsewhere.)

- [ ] **Step 6: Commit the documentation**

```bash
git add README.md
git commit -m "docs: document the Competitive Assessment (Stage 19) in the README"
```

---

## Task 10: Final verification and branch wrap-up

**Files:**
- (No edits — verification only.)

- [ ] **Step 1: Confirm the suite is green from a clean state**

Run: `python3 tests/validate_skill.py`
Expected: `62/62 passed`.

- [ ] **Step 2: Confirm the new files are all tracked and the tree is clean**

Run: `git status --short`
Expected: empty output (everything committed).

- [ ] **Step 3: Confirm the commit history on the branch**

Run: `git log --oneline -6`
Expected: the test, artifact, wiring, and docs commits are present on `feature/competitive-assessment`.

- [ ] **Step 4: Sanity-check the end-to-end wiring with a final grep**

Run:
```bash
python3 - <<'PY'
import re
skill = open("SKILL.md", encoding="utf-8").read()
# menu, router, dispatch, header all reference Stage 19 / the file
assert "Competitive Assessment" in skill
assert "| 19 | Competitive Assessment |" in skill
assert "**Stages 8–19 — Optional outputs" in skill
# stage cited in menu maps to a real heading
assert "(Stage 19)" in skill
stage = open("refs/stages/stage-19-competitive-assessment.md", encoding="utf-8").read()
assert re.search(r"^\*\*Stage 19 —", stage, re.M)
print("end-to-end wiring OK")
PY
```
Expected: `end-to-end wiring OK`

- [ ] **Step 5: Hand off** — the feature is complete on `feature/competitive-assessment`. Use the `superpowers:finishing-a-development-branch` skill to choose merge / PR / cleanup.

---

## Self-Review

**Spec coverage** (checked against `docs/superpowers/specs/2026-06-03-competitive-assessment-design.md`):
- Layered view (partner + customer) → Tasks 3, 4, 5 (two-layer read in every dimension block; checklist gate). ✓
- Per-dimension scorecard with in-line objection→response → Tasks 3, 5. ✓
- Fixed categories + POV-named specifics → Tasks 2, 3, 5 (stage instructions + checklist gate). ✓
- Dual MD+HTML token templates → Tasks 3, 4. ✓
- Architecture & Growth menu slot + included in "All outputs" → Task 6. ✓
- Curated ref + live top-up → Tasks 2, 5. ✓
- Per-dimension mandatory concession (hard fail) → Task 5 checklist + stage fairness gate; Task 1 does not assert prose quality (not unit-testable), which matches the suite's stated scope. ✓
- All five new files + three wiring edits + README → Tasks 2–7, 9. ✓
- Validation suite updated for Stage 19 → Task 1. ✓

**Placeholder scan:** No "TBD"/"TODO" in the plan's own steps. The `[bracketed]` text inside the `.md` template is intentional fill-guide content for the LLM at runtime (the same convention the consumption template uses), not a plan placeholder.

**Type/name consistency:** Filenames are identical everywhere — `stage-19-competitive-assessment.md`, `competitive-assessment.{md,html}`, `competitive-checklist.md`, `competitive-landscape.md`, slug artifact `{SLUG}-competitive-assessment.{md,html}`. The test function names (`t_competitive_stage_files`, `t_stage13_competitive_filename`, `t_dispatch_competitive`) are unique and added once. HTML block tokens (`FRAMING_HTML`, `DIMENSION_BLOCKS`, `SYNTHESIS_HTML`) match between the template and its TOKEN REFERENCE comment.

**Count note:** the suite grows from 59 to 62 checks (three added in Task 1). Task 8/9/10 expect `62/62`.
