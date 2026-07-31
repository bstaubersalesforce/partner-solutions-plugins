# The generate -> refine -> validate cycle & four quality loops

Every artifact is produced by three passes: **start with what you know, refine against sources,
validate**. The mechanical work runs through the `scripts/` library; the judgment is yours, written
in the first-person exec/architect McKinsey voice (see [voice-and-style.md](voice-and-style.md)).
Confidence and gap state live in the effort `manifest.yaml` (via `scripts/manifest.py`).

## The three passes

1. **Draft.** Produce a substantive v1 from model knowledge. Build the `{{TOKEN}}` fills dict and
   call `scripts/render.py` `render(template_text, fills)` to fill the artifact template. Set the
   artifact's status to `drafted` and a modest confidence with a one-line rationale. Never block on
   missing inputs -- a drafted artifact with flagged gaps beats a blank one.
2. **Refine.** Fold provided sources into the fills: pasted FCD/Quip text (#01-05), the Org62
   entitlement payload from `scripts/org62.py` (#06/#07; see
   [org62-entitlements.md](org62-entitlements.md)), fetched **official** docs (#08/#10), Slack
   context. Tie each claim to a source recorded in the artifact's `sources`. Re-render **only the
   sections you own**: call `scripts/sections.py` `locked_sections(live_md, baseline_md)` against the
   `last_generated` baseline; any human-edited `## H2` section is carried over **verbatim**, only
   model-owned sections regenerate. Write a fresh baseline after every (re)generation. Confidence
   rises as sources land. Note: whitespace-only edits (blank lines/indentation) are NOT treated as
   locks -- the diff compares stripped section bodies, so substantive content is what locks. A
   section the human DELETED from an artifact is not preserved as deleted; on regeneration it returns
   from the template. If a section must stay gone, remove it from the effort after regeneration. Two
   structural cautions for hand-edited artifacts: do not place a standalone `---` rule inside a body
   section -- it is reserved as the footer delimiter, and the section-diff stops at the first one, so
   any section below it would be dropped from the comparison and could be regenerated over your edits.
   Likewise, keep `## H2` headings unique within an artifact -- two sections with the same heading
   collide in the diff and the earlier one's edits are lost. Both are safe in the shipped templates;
   they only arise from manual edits.
3. **Validate.** Run the four loops below, then `scripts/scan.py` `scan(rendered_md)` to catch every
   surviving uncertainty. Each unresolved item becomes a manifest placeholder with an **owner + next
   step** and lowers confidence. Record each loop's outcome with `manifest.set_loop_verdict(...)`
   (verdict `pass` / `flag` / `fail` + note). An artifact reaches `verified` only when the loops pass
   and a human confirms.

## The four loops (one per failure mode)

| Loop | Question it answers | How to run it (Standard mode) |
|------|--------------------|-------------------------------|
| **Claim verification** | Is every factual/positioning claim traceable to a source? Does anything contradict the FCD? | One pass: walk the claims, confirm each maps to a `sources` entry; flag the ungrounded. |
| **Completeness** | Are all canonical sections present and non-empty? Audience-appropriate (PAM / NPI / less-technical)? | Diff the rendered artifact against its template grammar; flag empty personas/rows/sections. |
| **Uncertainty surfacing** | Is every PENDING / TBD / `$xx` / missing Template ID / unfilled token flagged with an owner + next step? | Run `scan.py`; for each gap, attach owner + next step and write it to the manifest placeholders. |
| **Partner-lens rules** | OEM/VAR correct? Shared-org restrictions honored? Packageability timing right? Official-docs-only respected (#08)? | Walk the partner-motion checklist; flag any violation. |

## The POV / opinion exception (important)

Claim verification is **strict for technical and positioning claims** but **lenient for POV / vision**
content (#10 partner-profile POV, and the vision parts of #00). A POV is Brandon's reasoned argument,
not a sourced fact: the loop checks **internal logic and clearly-marked assumptions**, not citations,
so it never strips the judgment the skill exists to express. Do not flag a well-reasoned, clearly
labeled POV as "ungrounded."

## Confidence & the gap banner

Drivers that **lower** confidence: unresolved placeholders, claims not grounded in a provided source,
official-docs-only violations in #08, unverified Tier-C research in #10. The effort's overall
confidence is the **weighted floor** across artifacts (`manifest.overall_confidence`) -- a single
shaky artifact stays visible, never averaged away. Every artifact opens with its gap banner; #00
aggregates all open gaps into the Next Steps & Blockers register. **A gap is never silent** -- always
owner + next step.

## Derivation contract (single-source-of-record)

Some artifacts are **derived**: they are generated FROM another artifact (their *source of record*),
not independently researched. The map lives in `scripts/manifest.py` as `DERIVES_FROM`, and
`manifest.generation_order()` returns the artifacts in an order where **every source is generated
before its derivatives**. Batching (below) and any full-build MUST follow that order.

| Source of record | Derived from it | Transform |
|------------------|-----------------|-----------|
| `01-brief` (narrative of record) | `00-executive-summary` | rollup of 01's narrative **plus** the manifest Next Steps & Blockers register + confidence rollup (00-only) |
| `01-brief` | `02-slide-summary` | condense 01 to a one-screen slide deck |
| `01-brief` | `11-solution-infographic` | render 01's problem/solution/outcomes/built-on as the solution infographic |
| `01-brief` | `14-exec-infographic` | render 01's exec narrative as the leadership poster |
| `04-internal-faq` | `05-external-faq` | partner-safe subset: emit only content 04 does not mark internal-only |
| `06-license-entitlements` | `07-addon-tiering` (Required tier) | ground 07's **Required** tier in 06's entitlement table; Recommended/Optional stay 07-authored |

**Contract for generating a derived artifact:** take its already-generated source as explicit input;
**transform it, do not re-research.** Introduce no claim absent from the source. Where the source is
silent, **flag a gap -- never invent.** The claim-verification loop still applies (fact drift is caught
regardless). `12-marketecture`, `13-demand-plan`, `03`, `08`, `09`, `10` are NOT derived -- they are
authored from effort sources.

## Generation batching (avoid the all-in-one timeout)

When generating a full effort -- especially by dispatching subagents -- **never generate all 15
artifacts in a single subagent.** A subagent asked to draft+refine+validate the whole family in one
pass will exhaust its turn/context budget and time out before it writes anything (this happened on
the first build). Instead:

- **Batch ~3-4 artifacts per subagent**, and have each subagent **write each artifact file
  immediately** after rendering it, so progress persists even if a later step in that batch stalls.
- A dependency-ordered grouping (sources before derivatives; see the Derivation contract above and
  `manifest.generation_order()`):
  **(a) sources first** -- 01-brief, 04-internal-faq, 06-license-entitlements;
  **(b) independents** -- 03-internal-enablement, 08-setup-guide, 09-org-provisioning-validation,
  10-partner-profile-pov, 12-marketecture, 13-demand-plan;
  **(c) derivatives** -- 02-slide-summary, 05-external-faq (subset of 04), 07-addon-tiering
  (Required tier from 06), 11-solution-infographic, 14-exec-infographic;
  **(d) 00-executive-summary LAST** -- its rollup reflects the others' real status/confidence/blockers.
- The manifest is the shared spine: each batch loads it, updates **only its own** artifacts, and
  writes it back -- run batches **sequentially** (not in parallel) so they don't race on
  `manifest.yaml`.
- The controller then **verifies the golden signals against the written bytes** (not the subagents'
  self-reports) before assembling the canvas.

This is generation guidance for a full build; a single-artifact refine in an interactive session
does not need batching.
