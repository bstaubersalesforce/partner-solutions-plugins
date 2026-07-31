# Agentscript handoff to agentforce-adlc

> **Canonical toolkit:** Agentforce ADLC — `github.com/SalesforceAIResearch/agentforce-adlc` (installed here as the `agentforce-adlc` plugin). **All** agentic work in this skill MUST go through the ADLC skills below; never hand-author `.agent` / aiAuthoringBundle / Bot / GenAiPlanner metadata directly inside pie-poc-forge.

## The ADLC skills (use the right one for the task)
- **`agentforce-adlc:developing-agentforce`** — author/modify/debug/deploy `.agent` files and aiAuthoringBundle; design actions, tools, subagents, flow control; write the Agent Spec; preview/publish. This is the primary build delegate.
- **`agentforce-adlc:testing-agentforce`** — write/run structured agent test suites (AiEvaluationDefinition); use when the PoC needs agent test coverage or regression specs.
- **`agentforce-adlc:observing-agentforce`** — analyze production session traces / Data Cloud; out of scope for a fresh PoC build, but cite it as the post-deploy monitoring path.

## When
Agent delegation triggers whenever `decisions.agentInScope` is true OR `buildTypes` includes `"agent"` OR the input describes an Agentforce agent, topics, actions, or an Agent Spec.

## Handoff — an explicit, sequenced step (NOT an inline generator)
Authoring the `.agent` requires invoking another skill, which cannot happen inside an automated generate loop. Sequence it explicitly:

1. **During generate:** write the **handoff brief** to `docs/09-agentscript.md` — agent purpose, topic/subagent breakdown, actions/tools, and the MCP integration contracts from `integrations`. Mark it clearly `DELEGATION PENDING` until step 3 completes. Also build the **routing diagram** from the brief's topic/subagent/action breakdown per `refs/mermaid-diagrams.md`, and fill the `{{ROUTING_DIAGRAM_MERMAID}}` token (subagents not yet authored render as `[pending authoring]`).
2. **Pause generate** and invoke `agentforce-adlc:developing-agentforce`, passing the brief from step 1. (If the PoC scope calls for agent tests, also invoke `agentforce-adlc:testing-agentforce`.)
3. **Resume:** drop the returned `.agent` / aiAuthoringBundle into `force-app/main/default/`, add it to `package.xml`, then re-render `docs/09-agentscript.md` (now containing the real agentscript, brief removed) to HTML. Refresh the routing diagram from the authored agent (replace any `[pending authoring]` nodes with the real subagents/actions) and, when `mmdc` is available, export the `.mmd` to PNG/SVG for the `11`/`12` decks — capability-gated per `refs/mermaid-diagrams.md`.

## If `agentforce-adlc` is not installed (degraded mode — do NOT hand-author)
The delegation is mandatory: a missing delegate does not license hand-authoring `.agent`/aiAuthoringBundle/Bot/GenAiPlanner metadata. Mirror the validator's degraded path (`refs/workflow-dispatch.md`) — degrade gracefully, do not dead-stop the whole run:
1. Leave `docs/09-agentscript.md` as the `DELEGATION PENDING` brief (step 1 output) — it is the complete, ready-to-execute spec for whoever finishes the agent.
2. Mark the agent "delegated — pending authoring (agentforce-adlc not installed)" in the execution plan (`01`) and component manifest (`08`), and add a gap row in `07` so the blocker is tracked, not buried.
3. **Continue generating everything not blocked** — objects/fields, perm set, scratch def, packaging analysis, security assessment, decks. Only the agent metadata and any synthesis step that needs it are deferred.
4. State plainly to the user: the `agentforce-adlc` plugin is not installed, so the agent was scaffolded-as-brief but not authored; install it (`github.com/SalesforceAIResearch/agentforce-adlc`) and re-run to complete the agent. Name what was skipped.

## Interim package state (between steps 1 and 3)
The package is **incomplete-by-design**: `docs/09-agentscript.md` holds the brief, `force-app/` has no agent metadata yet. The execution plan and component manifest MUST mark the agent as "delegated — pending authoring" so this interim state is never mistaken for done.

## Wiring MCP tools into the agent
When the agent calls MCP-registered tools (scaffolded via `refs/mcp-integration.md`), author one action per MCP tool, with `inputs` matching the tool's real `inputSchema` (introspected live — see `refs/mcp-integration.md`), not the build plan's guess. Sequence: scaffold MCP registration first, then author the agent against the verified tool surface.

**Action `outputs:` — prefer NONE; if present, match the schema exactly (nCino 2nd-org run).** The in-org remove+re-add path mints an `outputs:`-free MCP action (the tool supplies its own output schema), and that is the safest shape. Hand-authoring an `outputs:` block is a publish trap: `sf agent validate` and live-actions preview both PASS, but `sf agent publish` validates declared outputs against the tool's real `outputSchema` and fails on (a) an invented property name (`property <X> was not found in [...]`) or (b) a type mismatch — declaring an `array`/`number` schema property (e.g. `accounts`, `recommendations`, `netWorth`) as `string` yields an opaque `Internal Error`. If you must declare outputs, take the names+types verbatim from `tools/list` → `outputSchema.properties`; a subset of just the **string-typed scalar** properties is the safe minimum (the LLM still receives the full tool response at runtime).

**Argument binding — slot-fill, not an unpopulated variable (nCino 2nd-org run).** Bind each MCP action arg with **LLM slot-fill** (`with client_id = ...`) so the planner extracts it from the conversation at call time. Binding to a state variable (`with client_id = @variables.client_id`) forces whatever is in that variable — and if the router's `@utils.setVariables` never actually captured it (a `setVariables` with no `with <var> = ...` line captures nothing), an **empty value is sent to the tool**, which then returns the wrong/default record. Symptom: agent routes correctly and "succeeds," but shows the wrong client. Fix: slot-fill at the action AND give the router's `setVariables` an explicit `with <var> = ...`. ⚠️ A mock/tool that silently falls back to a default on empty/unknown input makes this a confident-wrong-data demo risk — prefer erroring.

## End-user agent access (employee agents)
An **employee agent is invisible to a user until they hold agent access** — publishing + activating is not enough. Create a dedicated permission set (e.g. `Employee Agent Access`) that grants agent access and assign it to each user who should run the agent. This is a Post-Config (`05`) step, distinct from the MCP callout perm set.

**Target gotcha (nCino run — see `refs/mcp-integration.md` validator 7.10):** authoring the action target as `mcpTool://<ExternalServiceRegistrationName>` (e.g. `mcpTool://NCinoBankingAdvisor`) is a convenient placeholder, but **it does NOT publish** — `validate` passes, then `publish` fails with an opaque HTTP 500, and only `preview --use-live-actions` reveals "invalid target ID value." The working action is minted in-org by **removing + re-adding the tool on the agent**, which rewrites the action to a hashed key + `source:` + an `outputs:`-free body + a `mcpTool://mcptoolx5fx5f<tool_name>` target. After binding, **retrieve the bundle and sync the hashed actions back into source** before publish. Sequence MCP scaffold + tool binding BEFORE agent publish; do not assume the `mcpTool://<ESR>` placeholder will compile. Full procedure + the corrected target format live in `refs/mcp-integration.md`.

## If agentInScope is false
Skip entirely; the `09-agentscript` artifact is omitted (the validator's router parity allows its absence).
