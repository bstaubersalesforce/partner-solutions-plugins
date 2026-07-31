# Stage 16 — Technical & Architectural Assessment

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 16 — Technical & Architectural Assessment (optional)**
Triggered when the user selects "Technical & Architectural Assessment" from the output menu, or asks for an architecture assessment / technical assessment / build-guiding architecture / Well-Architected review.

Load `refs/architecture-assessment.md` and follow it end to end — it carries the full process, the Salesforce Well-Architected evaluation method (3 pillars / 8 qualities), the seven target-architecture layers, and the build-ready spec + stub construction rules.

**Target-state architecture diagram.** This artifact embeds a Mermaid flowchart of the Part 2 target-state layers. Build it per `refs/mermaid-diagrams.md` (single-source theme directive + the architecture-flowchart recipe), inject it into the `{{ARCH_DIAGRAM_MERMAID}}` token in the HTML and the ` ```mermaid ` block in the Markdown, and — when `mmdc` is available — optionally export PNG/SVG for decks (capability-gated, graceful fallback). The diagram draws only from layers the POV populates; a `[TBD]` layer renders as `[TBD — confirm in build]`, never invented.
It produces `templates/technical-architecture-assessment.md` (Markdown output and the build-consumable source of truth) and, on Approve, `templates/technical-architecture-assessment.html` (shareable HTML view).
Run every check in `validation/architecture-checklist.md` before delivering.

**Output filenames — pin to the Stage 13 convention exactly.** Write the artifact as `{SLUG}-technical-architecture-assessment.md` and `{SLUG}-technical-architecture-assessment.html` in the output directory. Do **not** shorten it to `{SLUG}-architecture-assessment` or any variant — Stage 13 links the home page by this exact name, and a mismatch silently drops the card from the package. When this stage runs as a fanned-out subagent, the dispatch brief restates this filename; honor it verbatim.

Requires an approved POV. It is a downstream artifact (built from the POV) and **feeds the MVP Build Plan (Stage 8)**: when both the Assessment and the MVP Build Plan are generated in one session, run the Assessment **first**. Include it in "All outputs + home page".
