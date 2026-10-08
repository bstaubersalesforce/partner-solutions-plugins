# Stage 0 — Intake & scope

Capture everything once, centrally, so no downstream subagent re-interrogates the user.

## Capture
- **Partner name** (required).
- **Org62 Account ID** (strongly preferred — enables the case scan + consumption read).
- **Slack deal/engagement channels** (IDs or names).
- **Background** — PDF/notes path, prior POVs, canvases.
- **PAM** — owns forecast/pipeline records (we do not chase pipeline in Org62).
- **Partner's own strategic frame**, if any (e.g. an "AI in X" north star) — Methods will map to it.

## Resolve tooling (silent capability check, not a permission prompt)
- **Org62**: alias from `ORG62_ALIAS` (default `org62`); identity = logged-in session user.
- **Slack**: MCP tool if present (for channel reads and the final canvas).
- **Web**: a search tool if present, else fetch a search-results page.
Resolve and proceed in the same turn; never stall on a missing optional tool.

## Scope gate (apply the SKILL.md refusal conditions)
Confirm this is the right tool before fanning out: a **named ISV/OEM partner** and a request
for the **composite account plan** (not a single deliverable, not a generic customer plan).
If it is a single-deliverable ask, route the user to the specific forge skill instead.

## Gap-check, don't block
Flag missing inputs; proceed with what is available. A missing Account ID means the case scan
and consumption read degrade to research-only (flag lower confidence) — it does not stop the
plan. Then hand the captured context block (see `../orchestration.md`) to the fan-out stages.
