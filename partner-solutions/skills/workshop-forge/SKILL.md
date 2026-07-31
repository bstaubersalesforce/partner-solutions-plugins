---
name: workshop-forge
description: Use when scaffolding or drafting a Salesforce partner workshop/lab kit — stamps the shared kit skeleton (GUIDE/FACILITATOR/kit validator) from templates, then drafts modules, provisioning, and commercial content from upstream sources; output requires human review. Joins the pov-builder / pie-poc-forge / ps-npi-forge family.
---

# workshop-forge

## Overview
Scaffolds and drafts Salesforce partner workshop kits from the pattern proven across data360 / headless360 /
ncino kits. Two modes share one overlay (`config/kit.json`) and one anatomy (`refs/kit-anatomy.md`). Scaffold mode is deterministic and tested; author mode drafts source-grounded content that requires human review and completion.

## Delivery Voice
Write authored content as a senior Salesforce industry advisor briefing a partner team. Lead with the
conclusion; no hedging; flag uncertainty explicitly.

## Refusal / scope conditions
- Not a workshop-kit request (neither scaffold nor author) → clarify before acting.
- Scaffold: the target kit directory already exists → **refuse**, ask for a new name (never overwrite).
- Author: no scaffolded tree present → direct the user to scaffold mode first.
- Asked to generate the reference-build **agent/SFDX metadata** → redirect to pie-poc-forge; workshop-forge
  **wraps**, does not invent, the reference build.
- Do not fabricate provisioning specifics that can't be verified — flag residual confirmations.

## Mode detection
- "scaffold / new kit / stamp …" → **Scaffold**: load `refs/scaffold-flow.md` (deterministic skeleton generation).
- "author / enrich / fill / draft the modules …" → **Author**: load `refs/author-flow.md` (assembles source-grounded drafts; flags gaps for review).
- Ambiguous → ask which mode.

## Shared spine
Both flows read `refs/kit-anatomy.md` (skeleton vs overlay), `refs/guide-conventions.md` (Module 0→N +
🔴 checkpoints), and `refs/provisioning-models.md` (the picker + decision guide). Author also reads
`refs/input-contract.md`. The generated kit's self-check is specified in `refs/kit-check-spec.md`.

## Companion (logistics, not content)
This skill produces workshop **content**. The **PIE Lab Slack Skills** own the **logistics** around a lab
(nominations, registry, partner channels, ISV Technical Briefs). Load `refs/lab-logistics-companion.md` when a
request touches lab setup / nominations / onboarding, or when a partner's ISV Technical Brief is offered as an
author-mode input — it maps the seam and the handoff.

## Self-validation
workshop-forge satisfies its own rubric at Tier 3. After editing it, run `python3 tests/validate_skill.py`
(also enforced by `.githooks/pre-commit` and CI).
