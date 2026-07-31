# Mermaid Diagrams — Design Spec (pie-poc-forge)

**Date:** 2026-06-11
**Status:** implemented
**Origin:** Brandon — "can we build mermaid charts? I may want to add some to our POV and POC skills." Scoped to one high-impact area, the rest backlogged.

## Problem
The `09-agentscript` artifact is the review copy of the agent the PoC delivers — but
it shows only the `.agent` body. A partner engineer has no at-a-glance picture of how
the agent routes (user → planner → subagent selection → action). A routing diagram is
the highest-leverage visual in the PoC package: it anchors the kickoff and
engagement-review decks.

## Approach
Add a **subagent routing diagram** (Mermaid) to `09-agentscript`.

- **Source + GitHub render.** A ` ```mermaid ` fenced block in `templates/09-agentscript.md`
  carrying a `{{ROUTING_DIAGRAM_MERMAID}}` token. Renders natively on GitHub/GitLab.
- **PNG/SVG export.** `mmdc` renders the `.mmd` to a file that the Kickoff (`11`) and
  Engagement-Review (`12`) decks embed. Capability-gated: if `mmdc` is not installed,
  fall back to source-only and name the install — never dead-stop (mirrors the skill's
  existing degraded-mode discipline for `agentforce-adlc` / `sf-mcp-partner-toolkit`).
- **Single-source theme.** One `%%{init}%%` directive (Salesforce-aligned palette) in
  `refs/mermaid-diagrams.md`, prepended to every `.mmd`.

## Deliberately NOT in scope (this pass)
Live HTML render of the diagram. Pie renders `.md → .html` through the
golden-fixture-tested `scripts/md-to-html.py`; making the diagram render live in the
HTML review copy would require modifying that script (emit `<pre class="mermaid">`),
adding the CDN to `document-shell.html`, and regenerating + mutation-testing the golden
fixture — a change to a script shared by all 13 artifacts. Backlogged as B7. In the HTML
review copy the diagram shows as a fenced code block (source), which is acceptable for a
review artifact; the deck-facing surface is the `mmdc` PNG/SVG export.

## Constraint honored
`templates/09-agentscript.md` is only generated when `agentInScope` is true (it is a
CONDITIONAL artifact). The diagram lives inside it, so it inherits that gating — no
change to the registry or router-parity contract. `{{ROUTING_DIAGRAM_MERMAID}}` is
`UPPER_SNAKE` so `t_token_hygiene` stays green.

## Validation
`python3 tests/validate_skill.py` stays green; the new `refs/mermaid-diagrams.md` is
referenced from SKILL.md (satisfies `t_no_orphans` and the refs index).
