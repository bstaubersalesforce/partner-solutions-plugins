# Mermaid Diagrams — shared method

> Lazily loaded by artifacts that embed a diagram (currently `09-agentscript`, the
> agent routing diagram). Defines the single-source theme, the authoring recipe, the
> live HTML render, and the capability-gated PNG/SVG export. Diagram source is generated
> at runtime and injected into a template token; it renders live in the artifact's HTML
> via the Mermaid CDN in `document-shell.html` (see "HTML render" below), on GitHub, and
> to PNG/SVG via the `mmdc` export for decks.

## What you produce
A Mermaid source string for the artifact, which is:
1. injected into the artifact's `{{..._MERMAID}}` token (renders on GitHub/GitLab), and
2. optionally exported to PNG/SVG for the Kickoff (`11`) / Engagement-Review (`12`) decks
   (capability-gated — see Export).

## Single-source theme (Salesforce-aligned)
Every diagram opens with **one** init directive carrying the palette. Prepend it
verbatim to the diagram body. **Authoritative source:** the Salesforce Lightning Design
System (SLDS) design tokens (https://www.lightningdesignsystem.com/design-tokens/) —
brand `#0176d3` is `$brand-accessible`, navy `#032d60` is `$palette-blue-20`,
slate `#444444` is `$color-text-weak`. The workspace capture lives in
`~/.claude/style-conventions.md`; keep this directive in sync with it.

```
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f0f5fc","primaryTextColor":"#032d60","primaryBorderColor":"#0176d3","lineColor":"#444444","secondaryColor":"#f8fafc","tertiaryColor":"#ffffff","fontFamily":"Salesforce Sans, Helvetica Neue, Arial, sans-serif"}} }%%
```

The same directive drives the GitHub render and the `mmdc` export — one definition.

## Recipe — subagent routing diagram (09-agentscript)
Render how the agent routes a user request through its planner to the right subagent/
topic and on to actions. Draw it **only from the authored agent** (the handoff brief in
step 1, then the real `.agent` after authoring) — never invent subagents or actions.

- Use `flowchart TD` (top-down) for routing, or `sequenceDiagram` if the PoC's value is
  in the turn-by-turn exchange. Default to `flowchart TD`.
- One node per **subagent/topic**; one leaf per **action/tool** it can call. For MCP
  tools, label the action with its `mcpTool://<Registration>` target (see
  `refs/agentscript-handoff.md`).
- Show the planner as the routing hub: `User --> Planner`, `Planner --> SubagentA`, etc.
- A subagent that is **delegated — pending authoring** (degraded mode) still renders as
  a node, labeled `[pending authoring]` — mirrors the artifact's pending-not-fabricated rule.

Minimal shape (prepend the theme directive):

```
flowchart TD
  U[User] --> P{Planner}
  P --> A[answer_questions]
  P --> G[off_topic guardrail]
  A --> ACT[Action: ...]
```

## HTML render (live)
Pie renders `.md → .html` via the golden-fixture-tested `scripts/md-to-html.py`. It emits a
` ```mermaid ` fence as a `<pre class="mermaid">` block with the source kept **verbatim**
(any other fenced language becomes an escaped `<pre><code>` source block). `document-shell.html`
carries the Mermaid ESM CDN (`mermaid@11`) with `startOnLoad`, so the block renders live in the
artifact's HTML — no extra step. (Closed B8; was backlog B7.) The render is brace-safe: the
`%%{init}%%` theme directive lives in the diagram source, never in a template token.

## Export to PNG/SVG (capability-gated)
For the decks, render the `.mmd` to a file with the Mermaid CLI.

1. **Capability check.** Probe `mmdc --version` (or `npx --yes @mermaid-js/mermaid-cli --version`).
2. **If available:** write the source to `docs/09-agentscript-routing.mmd`, then
   `mmdc -i docs/09-agentscript-routing.mmd -o docs/09-agentscript-routing.svg`
   (use `.png` for raster). Embed the file in the `11`/`12` deck outlines and report the path.
3. **If NOT available (graceful fallback):** do **not** dead-stop — this mirrors the
   skill's degraded-mode contract for missing companion skills. Keep the `.mmd` source as
   the deliverable, state plainly that `@mermaid-js/mermaid-cli` is not installed so the
   PNG/SVG export was skipped, and give the one-line install (`npm i -g @mermaid-js/mermaid-cli`).
   The GitHub-rendered source block still conveys the diagram.
