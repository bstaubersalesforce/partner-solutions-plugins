# Clean Rebuild from the Canonical Intake — Agentforce for Healthcare

**Date:** 2026-06-24
**Effort:** `summer-26 / agentforce-healthcare-oem` (rebuilt from scratch)
**Trigger:** Brandon — codify the intake flow, run a full validate pass (no agent timeout this time),
then async remove the old dogfood and run a clean build from the canonical intake questions (which
match the Agentforce-for-Healthcare example). Resource links to be included in the artifacts.

## What ran

This is a **from-scratch rebuild**: the prior dogfood effort was deleted and the effort recreated from
the **canonical intake conversation** (refs/intake-source-map.md, codified this session) captured in
`sources/intake.md`:
- **Opening request:** "create an ISV Embedded SKU based on the standard Health Cloud SKU."
- **Name:** Agentforce for Healthcare. **Editions:** EE + UE. **Required add-ons:** Community Cloud +
  Community Cloud Plus. **Other add-ons:** none expected. **Slack:** #help-sell-health-cloud.
  **Resource links:** the Agentforce 360 for Health FCDs, Summer '26 Release Enablement Deck, Health
  Resources Canvas, Global Enablement Hub, Administer Health Cloud, Health Cloud Developer Guide.
  **Anything else:** Template ID PENDING (Manish/John), 2GP packaging TBD, pricing out of scope.

**Live Org62 (read-only)** grounded #06/#07: the OEM SKUs (`Health Cloud - Service - Enterprise /
Unlimited Edition - OEM`, `OPT-SS-EE/UE-HLS-OEM-ASP`), the Community add-on family (External Remote
Caregiver, `OPT-CC-EE-CCM-USE/LOG-ASP`), and the real entitlement grants (EE Sites qty 500,000 / UE
Sites qty 1,000,000, cloud Sites). Saved under `sources/`.

## Batched generation — no timeout (the hardening worked)

The original build timed out generating all 11 artifacts in one subagent. This rebuild followed the
new batching discipline (refs/quality-loops.md): **four sequential batches**, each writing files
immediately, each updating only its own manifest slots:
- **A:** 01-brief, 06-license-entitlements, 07-addon-tiering (source-grounded spine)
- **B:** 04-internal-faq, 08-setup-guide, 09-org-provisioning-validation (reference + gap carriers)
- **C:** 02-slide-summary, 03-internal-enablement, 05-external-faq, 10-partner-profile-pov (narrative)
- **D:** 00-executive-summary last (rollup reflects the others' real state)

All four batches completed cleanly; **no timeout**.

## Golden signals — verified in the bytes (not subagent self-reports)

- **11/11 artifacts** generated; the only unfilled tokens are the intended placeholders
  (`{{*_DIAGRAM}}` slots, `{{PRICE_PENDING}}`/`{{DISCOUNT_PENDING}}`). No unexpected unfilled tokens.
- **Overall confidence 0.35**, floor = #09 org-provisioning-validation; all four loop verdicts set on
  every artifact.
- **Template-ID blocker** traces #08 + #09 -> #00's Next Steps & Blockers register as the #1 blocker,
  owner Manish Jiandani / John Chung; #09 VALIDATION_RESULT = blocked.
- **#06** carries the real Org62 grants (EE/UE Sites) + the naming delta, flagged for human
  confirmation (sparse pull). **#07** Required tier = Community Cloud + CC+ (the External Remote
  Caregiver SKUs); pricing left as pending markers.
- **#01** Additional Resources lists the intake resource links; **#05** is a clean safe subset (no
  Template ID / ProductCode / pricing internals leaked).

## Render + canvas — calibrated cards, render-safe

Rendered the §6 HTML set (00,01,02,03,05,06,07,10; 04/08/09 stay MD-only) and assembled
`canvas/index.html`. Verified in the bytes:
- **Cards before the task list**; sibling card chrome (kind pill -> titled link -> summary ->
  status/confidence meta).
- **M1 link-and-tag:** rendered drafted artifacts (e.g. #06/#07) LINK and are tagged "— drafted, not
  yet final"; un-rendered MD-only artifacts (#04/#08/#09) are no-link gap cards "— not yet rendered".
- **#09** shows the 0.35 floor badge; the blocker register lists the Template-ID gap with its owner.
- **Render-safety:** #07's HTML shows "Diagram pending — populated on the next generate cycle." and
  two `(pending)` price cells — render-safe, no hard failure (the bug that would have blocked this
  before tonight's fixes).

## Verdict

**PASS.** The skill builds a complete, internally-consistent, sibling-calibrated artifact family +
canvas from the canonical intake, grounded in live Org62 data, with every uncertainty flagged and the
Template-ID blocker rolled up. The batched-generation discipline prevented the original timeout, and
the pipe-in-prose BLOCKER found by the validate pass was fixed before render. Foundation is solid for
Phase 6.

## Validate-pass results folded into this session (for the record)
- **BLOCKER fixed:** `md_to_html.py` silently dropped prose lines containing a `|` pipe — fixed
  (removed the paragraph-loop pipe-exclusion guard), gated by R-MD2H-03. (Inherited from
  pie-poc-forge — back-port tracked as BACKLOG B12.)
- **Minors fixed:** stale "not yet generated" quote in the prior acceptance doc; duplicated P1 header
  in the morning list.
- **Document-only:** scan flags the plain word "pending" (B10), #00-last ordering is advisory (B11),
  pie-poc-forge pipe back-port (B12) — recorded in BACKLOG, not fixed now.
- **Timeout hardening:** generation-batching guidance added to refs/quality-loops.md + gated in
  R-LOOPS-01. Suite 39 -> 40 across the session.
