# Mermaid Diagrams — Design Spec (pov-builder)

**Date:** 2026-06-11
**Status:** implemented
**Origin:** Brandon — "can we build mermaid charts? I may want to add some to our POV and POC skills." Scoped to one high-impact area per skill, the rest backlogged.

## Problem
The Technical & Architectural Assessment describes the target-state architecture
in prose + `.layer` cards but never *shows* it. A technical stakeholder reading the
artifact has no at-a-glance picture of how the layers connect. A diagram is the
single most impactful add for that artifact, and it should render live in the
shareable HTML and also export to PNG/SVG for decks (e.g. narrative-canvas).

## Approach
Add a target-state **architecture flowchart** (Mermaid) to Stage 16.

- **Single-source theme.** One `%%{init}%%` directive carrying a Salesforce-aligned
  palette (drawn from the artifact's existing palette: `#0070d2`, `#032d60`,
  `#54698d`, `#f0f5fc`, `#f8fafc`) lives in `refs/mermaid-diagrams.md`. The generator
  prepends it to every `.mmd`, so the same definition drives the live HTML render,
  the GitHub markdown render, and the `mmdc` export.
- **HTML live render.** The artifact embeds the Mermaid ESM CDN and calls
  `mermaid.initialize({ startOnLoad: true })`. The flowchart source is injected into
  a `<pre class="mermaid">` via the `{{ARCH_DIAGRAM_MERMAID}}` token.
- **Markdown render.** A ` ```mermaid ` fenced block in the `.md` template renders
  natively on GitHub/GitLab.
- **PNG/SVG export.** `mmdc` (`@mermaid-js/mermaid-cli`) renders the `.mmd` to a file
  for decks. Capability-gated: if `mmdc` is not installed, fall back to "source-only"
  and tell the user how to install it — never dead-stop.

## Why this is brace-safe (the validator constraint)
`tests/validate_skill.py` counts `{{`/`}}` pairs and rejects non-`UPPER_SNAKE`
`{{tokens}}` in the HTML templates. Mermaid's `%%{init: {…}}%%` directive contains
adjacent braces that *would* trip those checks. It is kept out of the template
entirely: the template holds only the `{{ARCH_DIAGRAM_MERMAID}}` placeholder, and the
brace-heavy directive lives in the runtime-injected token value. The HTML
`initialize()` call is minimal single-brace JS, formatted so no `{{`/`}}` adjacency
occurs.

## Non-goals / backlog
- Gantt timeline for the MVP Build Plan (Stage 8).
- Marketecture solution-layer flowchart (Stage 14).
- Consumption data/agent interaction flow (Stage 18).
These graduate later via their own spec→plan cycle.

## Validation
`python3 tests/validate_skill.py` stays green; no new orphans, balanced braces,
`{{ARCH_DIAGRAM_MERMAID}}` is `UPPER_SNAKE` and appears once; the new
`refs/mermaid-diagrams.md` is referenced by Stage 16 (satisfies `t_no_orphans`).
