# MCP integration handoff to sf-mcp-partner-toolkit

> **Canonical toolkit:** SF MCP Partner Toolkit — `github.com/mvogelgesang/sf-mcp-partner-toolkit` (installed here as the `sf-mcp-partner-toolkit` plugin). When the PoC includes an MCP integration, MCP client/registration metadata MUST be generated through these skills — never hand-author it inside pie-poc-forge.

## When (detection)
Trigger MCP delegation when any of these hold:
- an `integrations[]` entry has a `type` containing "MCP" (case-insensitive), or
- the build plan / input describes an MCP server, MCP bridge, or "Model Context Protocol", or
- an agent action is defined as calling an external tool over MCP.

Record the MCP integration(s) in `requirements.json` under `integrations` with `auth` (e.g. Named Credential + scoped OAuth) and `direction`.

## Mock vs production stand-in (capture explicitly — common in PoC work)
The real partner MCP server frequently does not exist yet at PoC time; a **mock/demo stand-in** (e.g. a Cloudflare Worker) is the build target. Capture this honestly — never present a mock as the production endpoint:
- On the `integrations[]` entry, set `isMock: true`, name the mock in `system` (e.g. "… (MOCK — Cloudflare Worker)"), and add a separate `productionTarget` note describing the real server's intended shape/direction and that it is future. See the integration fields in `refs/requirements-schema.md`.
- The agent + metadata are built against the **mock** (its real, verified tool surface). The Gaps document MUST carry "production MCP does not exist yet — cutover from mock" as an open question, and the Execution Plan must not imply the production bridge is live.
- A mock that only exposes a subset of the planned capabilities will force the build to diverge from the plan's hero use case — that divergence MUST be reconciled at synthesis (see `refs/workflow-dispatch.md` "Plan-vs-built reconciliation").

## Introspect the live server — do NOT trust the build plan's tool list
If the MCP endpoint is reachable (mock or real) and you have credentials, enumerate the REAL tools rather than assuming the build plan's list:
1. Get a token: `POST <oauthTokenUrl>` with `grant_type=client_credentials` + client id/secret (form-encoded or JSON).
2. `POST <mcpUrl>` JSON-RPC `initialize` then `tools/list` with `Authorization: Bearer <token>` — capture each tool's `name`, `description`, and `inputSchema`.
3. (Optional) one `tools/call` to confirm the response shape.
Use the discovered schemas to (a) enrich the External Service Registration `schema` (the scaffold wizard may emit `tools:[]`), and (b) author agent actions against real tool names/params. The build plan's named use cases may not match what the tools actually do — build on the verified surface, and reconcile any gap at synthesis. NEVER put the client secret in source/package; store it in the External Credential principal at deploy.

**ESR `<status>` is system-managed — strip it before deploy (nCino run).** A scaffolded/older `externalServiceRegistration-meta.xml` that carries `<status>Incomplete</status>` (or any `<status>`) fails to deploy with `Unable to create/update fields: Status` — `status` is derived by the org (Complete/Incomplete from whether schema + credential resolve) and is not writable on deploy. Remove the `<status>` element from the ESR metadata before deploying (the tool schema + credential refs are untouched). The current toolkit CLI (`create-sf-mcp-client-metadata` v1.1.0+) should not emit it; if a captured/legacy ESR carries it, strip it.

## The toolkit skills (sequence)
1. **`sf-mcp-partner-toolkit:setup-workspace`** — verify Node.js, Salesforce CLI, org connection, SFDX project structure. Run first.
2. **`sf-mcp-partner-toolkit:scaffold-mcp-integration`** — generate the four Salesforce metadata files that register the partner's MCP server (needs: integration name in PascalCase letters-only, the HTTPS MCP server URL, and the auth method). This is the build step.
3. **`sf-mcp-partner-toolkit:deploy-and-configure`** — deploy the metadata, assign permission sets, walk post-deploy OAuth credential configuration.
4. **`sf-mcp-partner-toolkit:diagnose-connection`** — troubleshoot connectivity if the integration does not work.
5. **`sf-mcp-partner-toolkit:validate-end-to-end`** — confirm tool discovery, schema correctness, and agent invocation from Agentforce.

## Handoff — explicit, sequenced (NOT inline)
Like the agent handoff, these require invoking another skill and cannot run inside the automated generate loop:
1. **During generate:** capture the MCP integration contract in the Component Manifest and Execution Plan (system, URL placeholder, auth, direction), and add an Execution-Plan task "Scaffold MCP registration via sf-mcp-partner-toolkit". Mark MCP registration metadata `DELEGATION PENDING`.
2. **Pause generate** and run the toolkit sequence above (at minimum `setup-workspace` → `scaffold-mcp-integration`; `deploy-and-configure` / `validate-end-to-end` when an org is available).
3. **Resume:** the generated MCP metadata lands in `force-app/`; add it to `package.xml`, and note OAuth/Named-Credential setup as a step in the Post-Config Steps artifact (it is environment-bound, not packaged with live secrets).

## If `sf-mcp-partner-toolkit` is not installed (degraded mode — do NOT hand-author)
A missing toolkit does not license hand-authoring MCP client/registration metadata. Mirror the validator's degraded path (`refs/workflow-dispatch.md`):
1. Keep the MCP integration contract captured in the Component Manifest (`08`) and Execution Plan (`01`) (system, URL placeholder, auth, direction), with the "Scaffold MCP registration via sf-mcp-partner-toolkit" task marked `DELEGATION PENDING`.
2. Add a gap row in `07` so the un-scaffolded registration is tracked.
3. **Continue generating everything not blocked.** If the build is also agentic and the agent references the MCP tool, the agent cannot be authored against a verified tool surface — defer that wiring too and note it (see `refs/agentscript-handoff.md`).
4. State plainly to the user: `sf-mcp-partner-toolkit` is not installed, so MCP registration metadata was specified but not generated; install it (`github.com/mvogelgesang/sf-mcp-partner-toolkit`) and re-run. Name what was skipped.

## Interaction with the agent handoff
If the build is BOTH agentic AND uses MCP (common — an Agentforce agent calling an external tool over MCP): scaffold the MCP registration (this ref) so the tool is callable, then author the agent (`refs/agentscript-handoff.md`) to use it. Sequence MCP scaffold before agent authoring where the agent references the MCP tool.

## Packaging an MCP integration for 2GP (REQUIRED — validator-enforced)
When the PoC will be packaged (2GP) and ships MCP metadata, the scaffold MUST include these or subscribers get non-functional MCP tools:
- **postInstall InstallHandler Apex (validator 7.5 + 7.9).** Known platform issue **W-21685162**: the packaged `UserExternalCredential` read object-permission is silently dropped on install, and the MCP perm set is not assigned to the Platform Integration User. Generate a stub `InstallHandler` Apex class that, on install: (a) queries the Platform Integration User (`Name LIKE 'Platform%'`), (b) assigns the MCP perm set to it, (c) re-grants `UserExternalCredential` read. Without this class the validator FAILs 7.5 and the integration is broken in subscriber orgs. Reference impl: `github.com/mvogelgesang/sf-mcp-registration-api-key` (`*PostInstall.cls`).
- **Perm set object permission (validator 7.5).** Keep the `UserExternalCredential` `<allowRead>true</allowRead>` block the toolkit generates AND ship the postInstall class (both are required — the perm set alone is dropped on install).
- **Runtime: assign the MCP perm set to the Platform Integration User (Post-Config / Phase D — confirmed on the nCino run).** The agent's MCP callouts execute as the **Platform Integration User** (`cloud@…`), not the running/admin user. Assigning the MCP perm set only to the admin (the default) lets the agent publish but tool calls fail auth at runtime. As a Post-Config step (and in Phase D after deploy), assign it to the integration user explicitly — CLI `sf org assign permset --name <PermSet> --on-behalf-of "<integration-user-username>"`, or the equivalent anonymous Apex (query `User WHERE Name LIKE 'Platform%'` → insert `PermissionSetAssignment` if absent). Caveat: `Name LIKE 'Platform%'` can match multiple integration users in some orgs — confirm it resolves to the agent runtime user (`cloud@…`) before relying on it. This is the non-packaged equivalent of what the postInstall InstallHandler does for subscriber installs.
- **`mcpTool://` target + action shape (validator 7.10) — CORRECTED from the 2026-06-11 nCino run.** A scaffolded/authored MCP action of the form `target: "mcpTool://<ESR-name>"` (e.g. `mcpTool://NCinoBankingAdvisor`) **passes `sf agent validate` but fails `sf agent publish` with an opaque HTTP 500.** The real error only surfaces via `sf agent preview start --use-live-actions`: *"the MCP action '<name>' has an invalid target ID value."* The server name is NOT a valid target, and the working target is NOT a `1XO…` Record ID either — it is an **encoded per-tool name**: `mcpTool://mcptoolx5fx5f<tool_name>` (where `x5f` = `_`, so it decodes to `mcptool__<tool_name>`, e.g. `mcpTool://mcptoolx5fx5fget_client_financial_summary`).
  - **How the valid action is produced (the only reliable path observed):** in the org, **remove each MCP tool from the agent and re-add it** (Agent Builder / agent's tool list). This rewrites the ENTIRE action — not just the target: the action key + `@actions.X` reference become an **opaque hash** (e.g. `ac3a4056d315d3e41afa4dc2db5ed77b7`), a `source:` field (= the hash) is added, `label:` → `"<tool> - NCinoBankingAdvisor"`, `require_user_confirmation`/`include_in_progress_indicator` added, and the **`outputs:` block is removed** (the MCP tool supplies its own output schema; a declared `outputs:` is wrong). Then **retrieve the bundle and sync the hash-named actions back into source**, edit the subagents' `reasoning.actions` to reference the hashes, and publish.
  - **For a 2GP/managed package:** these org-specific hashes/targets do NOT transport. The Post-Config Steps artifact MUST instruct subscribers to remove+re-add each MCP tool on the agent in their own org (which mints their org's hashes), then publish — and name the tools + a sample utterance to verify. Do not ship hardcoded hash targets and expect them to bind in another org.
  - **Diagnostic — MCP Workbench (unmanaged package).** Install MCP Workbench to introspect the registered MCP server + tools from inside the org (Connect → List Tools) and confirm the connection/auth before touching the agent. GitHub `https://github.com/mvogelgesang/MCP-Workbench`; install `packaging/installPackage.apexp?p0=04tHs000000iSjcIAE`. Pair it with `sf agent preview start --use-live-actions` (the only reliable surfacer of the "invalid target ID" error — `validate` and the opaque publish 500 both hide it).
- **No GenAiPlannerBundle MCP tool-action references (validator 7.6).** If a planner bundle is retrieved from an org with MCP tools active, strip those tool-action references before packaging — they fail package creation.

## Security + packaging notes
- MCP is a net-new external auth surface — the Security Assessment artifact MUST flag it (OAuth scopes, PII-in-transit, inbound auth/replay if bidirectional); see `refs/security-review.md`.
- MCP registration metadata + Named/External Credentials are typically environment-bound — route live-credential setup to Post-Config, not the deployable package; see `refs/packaging-analysis.md` coverage rules.
- **Validate the bundle** before declaring it done — run `isv-validate-agentforce` over the package (see `refs/workflow-dispatch.md` validation gate); its Group 7 (MCP) checks catch the items above mechanically.
