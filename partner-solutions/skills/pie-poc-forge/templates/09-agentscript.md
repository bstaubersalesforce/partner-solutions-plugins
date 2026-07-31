# {{PARTNER}} — Agentscript (Review Copy)

**Generated:** {{DATE}}

Review rendering of the `.agent` document authored via `agentforce-adlc:developing-agentforce`. The deployable file lives in `force-app/main/default/`.

## Routing diagram
How the agent routes a request: user → planner → subagent/topic → action. Built only from the authored agent per `refs/mermaid-diagrams.md` (prepend the theme directive); a subagent pending authoring renders as `[pending authoring]`, never invented. Renders natively on GitHub; exported to PNG/SVG for the kickoff/review decks when `mmdc` is available.

```mermaid
{{ROUTING_DIAGRAM_MERMAID}}
```

## Agentscript
{{AGENTSCRIPT_BODY}}
