# Technical & Architectural Assessment Pre-Delivery Validation Checklist

Run every check before delivering the assessment. If any check fails, repair before delivering.

## Part 1 — Current-State Assessment (Well-Architected)
All eight qualities present, each with Finding / Evidence / Pattern-Anti-pattern / Gap; grouped under their pillars (Trusted / Easy / Adaptable).
- [ ] Trusted — Secure assessed (Finding, Evidence, Pattern/Anti-pattern, Gap)
- [ ] Trusted — Compliant assessed
- [ ] Trusted — Reliable assessed
- [ ] Easy — Intentional assessed
- [ ] Easy — Automated assessed
- [ ] Easy — Engaging assessed
- [ ] Adaptable — Resilient assessed
- [ ] Adaptable — Composable assessed

## Content Rules
- [ ] Every quality has an Evidence line; the Evidence is sourced and carries a confidence label (`[confirmed]` / `[proposed — confirm]` / `[TBD]`)
- [ ] A quality with no evidence renders `[TBD]` with a "what to confirm" note — never invented
- [ ] Every Pattern/Anti-pattern is named specifically (not "good architecture" / "bad design")

## Part 0 — Executive Readiness Summary
- [ ] RAG table present with all 8 qualities rated, each with a one-line finding
- [ ] Pillar rollup present (Trusted / Easy / Adaptable)
- [ ] Every RAG rating traces to the matching Part 1 finding (no orphan scores)
- [ ] Top 3 technical risks present, each tied to a quality + severity
- [ ] Build-readiness verdict present (Go / Conditional-Go / Not-ready)

## Part 2 — Target-State Architecture
- [ ] All seven layers present (packaging, data, integration, component, security, scale, AI/data) — each a recommendation or explicit `[TBD]`
- [ ] Salesforce capabilities named specifically (not "the Salesforce platform")

## Part 3 — Build-Ready Spec & Stubs
- [ ] Metadata blueprint present (objects → fields → relationships); standard objects named, not redefined
- [ ] Component inventory present, each with responsibility + traceability
- [ ] Integration contracts present for each named external system (or "No external integrations")
- [ ] Skeleton stubs are signatures/scaffolding only — no business-logic bodies (bodies are `// TODO (build): …`)
- [ ] Every object/field/class/Flow traces to a POV use case or Part 2 decision — untraceable artifacts removed
- [ ] Under-specified items marked `[TBD — confirm in build]`, not guessed

## Part 4 — Roadmap & Handoff
- [ ] Gap-closing items listed, each mapped to the quality it closes, with priority
- [ ] Explicit handoff to the MVP Build Plan (Stage 8) present
- [ ] Overall Well-Architected readiness score (0.0–1.0) with at least one named assumption

## Failure → Repair Instructions
**Orphan RAG score (no matching Part 1 finding):** every Part 0 rating must derive from a Part 1 finding. Either add the finding to Part 1 or correct the rating; do not score a quality that was not assessed.
**Stub contains business logic:** strip the body to a `// TODO (build): …` line with the intent. The assessment scaffolds; the build implements.
**Untraceable metadata artifact:** remove it, or add the POV use case / Part 2 decision it serves. If it serves nothing, it does not belong in the spec.
**Generic Salesforce reference:** replace "the Salesforce platform" with the specific cloud/SKU/API/capability (e.g., "Service Cloud + Platform Events").
