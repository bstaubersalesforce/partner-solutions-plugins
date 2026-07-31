# Mermaid Diagrams — Implementation Plan (pov-builder)

**Date:** 2026-06-11 · **Spec:** `../specs/2026-06-11-mermaid-diagrams-design.md`

## Steps
1. **`refs/mermaid-diagrams.md`** (new) — the shared diagram ref:
   - the single-source `%%{init}%%` theme directive (Salesforce palette);
   - the HTML CDN + `initialize` snippet (brace-safe);
   - the architecture-flowchart authoring recipe (layers → nodes, top-down);
   - the `mmdc` capability check + PNG/SVG export, with graceful fallback.
2. **`templates/technical-architecture-assessment.html`** — in Part 2, after
   `{{TARGET_ARCH_HTML}}`, add a diagram sub-region: `.mermaid` CSS, a
   `<pre class="mermaid">{{ARCH_DIAGRAM_MERMAID}}</pre>`, the ESM CDN `<script>` before
   `</body>`, and a `ARCH_DIAGRAM_MERMAID` entry in the token-reference glossary.
3. **`templates/technical-architecture-assessment.md`** — add a ` ```mermaid ` fenced
   block placeholder in Part 2 (renders on GitHub).
4. **`refs/stages/stage-16-architecture-assessment.md`** — instruct: build the `.mmd`
   from the Part 2 layers using `refs/mermaid-diagrams.md`, fill the token in both
   templates, and optionally export PNG/SVG. This reference satisfies `t_no_orphans`.
5. **`refs/architecture-assessment.md`** — add the diagram-construction step to the
   end-to-end process the stage follows (so a fanned-out subagent that loads only this
   file still knows to build the diagram).
6. **`BACKLOG.md`** — record the deferred diagram areas.

## Verify
`python3 tests/validate_skill.py` → green. Spot-check the HTML opens and the
`{{ARCH_DIAGRAM_MERMAID}}` placeholder is the only new token.
