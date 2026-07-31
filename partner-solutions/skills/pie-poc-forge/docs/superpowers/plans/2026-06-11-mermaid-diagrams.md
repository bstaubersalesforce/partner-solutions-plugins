# Mermaid Diagrams — Implementation Plan (pie-poc-forge)

**Date:** 2026-06-11 · **Spec:** `../specs/2026-06-11-mermaid-diagrams-design.md`

## Steps
1. **`refs/mermaid-diagrams.md`** (new) — shared diagram method: single-source theme
   directive (Salesforce palette), the subagent-routing recipe, and the `mmdc`
   capability check + PNG/SVG export with graceful fallback. Does NOT touch
   `scripts/md-to-html.py`.
2. **`templates/09-agentscript.md`** — add a ` ```mermaid ` fenced block with the
   `{{ROUTING_DIAGRAM_MERMAID}}` token (subagent routing). Renders on GitHub.
3. **`refs/agentscript-handoff.md`** — instruct: during the handoff brief (step 1),
   build the routing `.mmd` per `refs/mermaid-diagrams.md`; on resume (step 3), the
   re-rendered artifact carries the diagram; the deck export feeds `11`/`12`.
4. **`SKILL.md`** — add `refs/mermaid-diagrams.md` to the refs index (satisfies the
   orphan check; every ref must be named in SKILL.md).
5. **`BACKLOG.md`** — record deferred areas (B7 full live-HTML render; execution-plan
   Gantt; component-manifest dependency graph; security trust-boundary diagram).

## Verify
`python3 tests/validate_skill.py` → green (16/16 + any current count). No fixture
regeneration needed — `md-to-html.py` is untouched.
