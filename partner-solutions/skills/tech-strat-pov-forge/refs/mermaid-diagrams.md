# Mermaid Diagrams — shared method

> Lazily loaded by stages that embed a diagram (currently Stage 16, the Technical &
> Architectural Assessment). Defines the single-source theme, the HTML live-render
> snippet, the authoring recipes, and the capability-gated PNG/SVG export. Diagram
> source is generated at runtime and injected into a template token — it never lives
> brace-first inside a validated template (see "Brace safety" below).

## What you produce
For a diagram-bearing stage, generate one Mermaid source string and:
1. inject it into the artifact's `{{..._MERMAID}}` token (HTML + Markdown), and
2. optionally export it to PNG/SVG for decks (capability-gated — see Export).

## Single-source theme (Salesforce-aligned)
Every diagram opens with **one** init directive carrying the palette. Prepend it
verbatim to the diagram body. The palette matches the artifact's existing colors —
brand `#0176d3` (`$brand-accessible`), navy `#032d60` (`$palette-blue-20`),
slate `#444444` (`$color-text-weak`), panels `#f0f5fc` / `#f8fafc`.
**Authoritative source:** the Salesforce Lightning Design System (SLDS) design tokens
(https://www.lightningdesignsystem.com/design-tokens/), captured for this workspace in
`~/.claude/style-conventions.md` — keep this directive in sync with that file.

```
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f0f5fc","primaryTextColor":"#032d60","primaryBorderColor":"#0176d3","lineColor":"#444444","secondaryColor":"#f8fafc","tertiaryColor":"#ffffff","fontFamily":"Salesforce Sans, Helvetica Neue, Arial, sans-serif"}} }%%
```

This same directive drives the live HTML render, the GitHub Markdown render, and the
`mmdc` export — one definition, three surfaces.

## Recipe — target-state architecture flowchart (Stage 16)
Render the **Part 2 seven layers** as a top-down flowchart, one node per layer that
the POV actually populates (skip "Not applicable" layers — never draw an empty box).
Edges show the dependency/data direction (channel ← components ← data ← integration).

- Use `flowchart TD`.
- Node text = the layer name + the concrete Salesforce capability named in Part 2
  (e.g. `LWC[Component layer<br/>LWC + Apex]`). Keep labels short.
- Group related layers with `subgraph` only when it aids clarity; don't over-nest.
- **Never invent a layer the POV doesn't support.** A `[TBD]` layer renders as a node
  labeled `[TBD — confirm in build]`, mirroring the artifact's no-fabrication rule.

Minimal shape (theme directive omitted here for brevity — always prepend it):

```
flowchart TD
  CH[Channel layer<br/>Experience Cloud] --> CMP[Component layer<br/>LWC + Apex]
  CMP --> DATA[Data architecture<br/>Custom objects + Data Cloud]
  DATA --> INT[Integration<br/>Named Credential + External Services]
  CMP --> AI[AI &amp; data layer<br/>Agentforce]
```

## HTML live render (brace-safe)
The artifact template carries the Mermaid ESM CDN and a minimal initialize call:

```html
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({ startOnLoad: true, securityLevel: "loose" });
</script>
```

The diagram source (theme directive + body) is injected into
`<pre class="mermaid">{{ARCH_DIAGRAM_MERMAID}}</pre>`. `startOnLoad` renders every
`.mermaid` block when the page loads. Live render needs internet at view-time; the
PNG/SVG export below is the offline/deck path.

### Brace safety
Mermaid's `%%{init: {…}}%%` directive contains adjacent `{{`/`}}`. It MUST stay out
of the template file — the template holds only the `{{ARCH_DIAGRAM_MERMAID}}`
placeholder; the directive lives in the injected token value. The `initialize({…})`
call above is single-brace JS, formatted so no `{{` or `}}` adjacency appears. This
keeps `tests/validate_skill.py`'s brace-balance and token checks green.

## Export to PNG/SVG (capability-gated)
For decks (e.g. narrative-canvas), render the `.mmd` to a file with the Mermaid CLI.

1. **Capability check.** Probe `mmdc --version` (or `npx --yes @mermaid-js/mermaid-cli --version`).
2. **If available:** write the source to `{SLUG}-architecture.mmd`, then
   `mmdc -i {SLUG}-architecture.mmd -o {SLUG}-architecture.svg` (use `.png` for raster).
   Report the file path.
3. **If NOT available (graceful fallback):** do **not** dead-stop. Keep the `.mmd`
   source file as the deliverable, state plainly that `@mermaid-js/mermaid-cli` is not
   installed so PNG/SVG export was skipped, and give the one-line install
   (`npm i -g @mermaid-js/mermaid-cli`) so the user can render later. The live HTML
   render still works regardless.
