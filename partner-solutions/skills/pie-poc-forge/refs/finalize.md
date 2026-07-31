# Phase D — Finalize (org-connected lifecycle)

Opt-in, re-entrant. Runs ONLY when explicitly invoked against an existing package plus an
authenticated org alias (e.g. "finalize the <partner> PoC against org <alias>"). Phases A–C
stay org-free; Phase D never runs as an automatic tail of B or C.

This phase exists because six lifecycle steps are org-dependent and otherwise defer to the
build session: deploy dry-run, real deploy, agent validate, agent publish, MCP
deploy-and-configure, MCP validate-end-to-end.

## Preconditions
- A package exists (force-app/ + manifest/ + requirements.json).
- An org alias is provided AND authenticated (`sf org display --target-org <alias>` succeeds).
- If no org alias is provided: do NOT run. State that Phase D cannot run without an org, and
  surface the Gate 1 commands below for manual use. (Consistent with the prior "skipped — no
  org" behavior, now centralized here.)

## Step 0 — Identify the org (guardrail)
Run `sf org display --target-org <alias>` and read the edition / instance / org type.
- **Scratch, sandbox, or demo org** → proceed normally.
- **Production** (production edition, or not a scratch/sandbox/demo org) → require an explicit
  **typed confirmation** from the user before ANY mutating Gate-2 step (e.g. the user types the
  org alias or "DEPLOY TO PRODUCTION"). Gate 1 (non-mutating) still runs without confirmation.
  Record the confirmation in the report.

## Gate 1 — Validate (non-mutating; runs by default)
Run each applicable step, capture PASS/FAIL + output:
1. `sf project deploy start --manifest manifest/package.xml --dry-run --target-org <alias>`
2. Agent **validate** — when an agent is in the package, delegate to `agentforce-adlc`
   (`developing-agentforce` validate path). Never hand-run agent metadata validation here.
3. MCP **environment + endpoint reachability** — when MCP metadata is present, delegate to
   `sf-mcp-partner-toolkit:setup-workspace` (env/CLI/org readiness). NOTE: the MCP registration
   is not deployed yet at Gate 1, so there is nothing in the org to connect to — the live
   connectivity test belongs to Gate 2.

If ANY Gate-1 step FAILs → STOP. Write the report (Gate 1 results + Mitigation), do NOT offer
Gate 2. The user fixes the package (usually re-run Phase C) and re-finalizes.

## Gate 2 — Deploy (mutating; offered ONLY after Gate 1 is fully green)
Offer to proceed. On confirmation (and the §0 prod gate, if applicable), run in order.
**Ordering correction from the 2026-06-11 nCino run: when the agent calls MCP tools, MCP must be
fully configured AND each tool bound on the agent BEFORE `sf agent publish` — publishing first
fails with an opaque 500.** The corrected order:
1. `sf project deploy start --manifest manifest/package.xml --target-org <alias>` (real deploy).
2. Assign the generated permission set(s) to the running user: `sf org assign permset --name <PermSet> --target-org <alias>`.
3. **MCP first (when the agent uses MCP tools):**
   a. **deploy-and-configure** → `sf-mcp-partner-toolkit:deploy-and-configure` (deploy MCP metadata if not already; enter the OAuth client id/secret in the External Credential principal — browser/out-of-band; register the tools so they are "available for agent action").
   b. **Assign the MCP perm set to the Platform Integration User** (the agent's callouts run as it, not the admin): `sf org assign permset --name <PermSet> --on-behalf-of "<platform-integration-user>"` (confirm the user is `cloud@…`).
   c. **Bind each MCP tool on the agent** — remove + re-add each tool on the agent in-org (mints the hashed action key + `source:` + `outputs:`-free body + `mcpTool://mcptoolx5fx5f<tool>` target), then **retrieve the bundle and sync the hashed actions back into source**. See `refs/mcp-integration.md` validator 7.10. Confirm with `sf agent preview start --use-live-actions` (it must start cleanly — no "invalid target ID").
4. Agent **publish** → delegate to `agentforce-adlc` (now resolves), then **activate**.
5. MCP **validate-end-to-end** → `sf-mcp-partner-toolkit:validate-end-to-end` — confirm the agent invokes a tool with a sample utterance.

(For a non-MCP agent, the original order — deploy → perm sets → publish → activate — is unchanged; steps 3a–3c apply only when the agent references MCP tools.)

Stop-on-first-failure applies in Gate 2 too: a failed step halts the run and writes its
Mitigation; later steps are recorded SKIP.

## Report contract (`13-finalize-report`)
Fill the `templates/13-finalize-report.md` tokens:
- `{{PARTNER}}`, `{{DATE}}`, `{{TARGET_ORG}}` — partner, run date, and the org identity from §0
  (alias + edition/instance; mark "PRODUCTION (confirmed)" when the prod gate was used).
- `{{GATE1_RESULTS}}` / `{{GATE2_RESULTS}}` — one table row per step: `step | command | result
  (PASS/FAIL/SKIP) | returned id/notes`. Gate 2 reads "Not run — Gate 1 not green" when stopped
  at Gate 1.
- `{{MITIGATIONS}}` — one block per FAILed step (see below); "None — all steps passed" if clean.

Then render via the standard recipe (`refs/workflow-dispatch.md` rendering recipe) and add a
`13-finalize-report` card to the index (it is CONDITIONAL — present only after a finalize run).
Record the run in `requirements.json.finalize` (see `refs/requirements-schema.md`).

## Detailed mitigation on failure (REQUIRED)
A failed step is NEVER recorded as a bare "FAIL". For each failure, write a Mitigation block:
- **Symptom** — the captured error / CLI output (verbatim, not paraphrased) + which gate/step.
- **Likely cause** — from the taxonomy below, keyed by step + error signature. If no entry
  matches, label it "unclassified — inspect output" (never invent a cause).
- **Fix** — the concrete next action, routed to the owning artifact/delegate.
- **Resume** — the exact command/phase to re-run once fixed, so the lifecycle resumes without
  restarting.

### Known-failure taxonomy (step × error signature → cause + fix)
| Step | Error signature | Likely cause | Fix | Resume |
|------|-----------------|--------------|-----|--------|
| dry-run / deploy | `ConversionError: Invalid XML tags or unable to find matching parent xml file for CustomField "<field>"` | A `<!-- … -->` comment sits **between the `<?xml?>` declaration and the root element** in an object/field `-meta.xml` — source conversion fails before reaching the org | Relocate the comment to the first line **inside** the root element. See `refs/sfdx-scaffold.md` stub conventions. | re-run Gate 1 |
| dry-run / deploy | `ExternalServiceRegistration … Unable to create/update fields: Status` | The ESR metadata ships a system-managed `<status>` element (not writable on deploy) | Strip the `<status>` element from the `externalServiceRegistration-meta.xml` (schema/credential refs untouched). See `refs/mcp-integration.md`. | re-run Gate 1 |
| dry-run / deploy | `INVALID_FIELD` / `INVALID_TYPE` on a managed-package object (e.g. `Loan__c`) | Unresolved managed-package reference — placeholder not resolved in the target org | Install the nCino managed package (or use a snapshot that carries it); or resolve the reference per `refs/sfdx-scaffold.md`. See Pre-Instance Config (`03`). | re-run Gate 1 |
| dry-run / deploy | `INSUFFICIENT_ACCESS` / perm-set or Platform Integration User errors | Perm set not assignable, or MCP postInstall (re-grant `UserExternalCredential`) not run | Confirm perm sets deploy; ensure the MCP postInstall InstallHandler is present (see `refs/mcp-integration.md`). | re-run Gate 1 |
| agent publish | opaque HTTP 500 `Internal Error, try again later` (validate PASSED first) | An MCP action target is `mcpTool://<ESR-name>` (server name) — invalid. The 500 hides the real cause; run `sf agent preview start --use-live-actions` to see "invalid target ID value" | Remove + re-add each MCP tool on the agent in-org (mints the hashed action key + `source:` + `outputs:`-free body + `mcpTool://mcptoolx5fx5f<tool>` target), retrieve the bundle, sync the hashed actions into source, then publish. Diagnose with MCP Workbench (`github.com/mvogelgesang/MCP-Workbench`). See `refs/mcp-integration.md` validator 7.10. | re-run Gate 2 from agent publish |
| agent validate | Agent Script schema error / `mcpTool://` target unresolved | Agent references an MCP tool whose registration isn't deployed/wired yet | Deploy MCP registration first (Gate 2 ordering scaffolds MCP before agent); then bind the tool on the agent (remove + re-add) per `refs/mcp-integration.md`. See Post-Config (`05`). | re-run Gate 1 agent validate |
| MCP setup-workspace | CLI / Dev Hub / org not ready | Environment precondition missing (CLI version, Dev Hub auth, org connection) | Resolve per `sf-mcp-partner-toolkit:setup-workspace` output (install/auth steps). | re-run Gate 1 |
| MCP deploy-and-configure | `401` / `invalid_client` on the MCP callout | External Credential principal / client secret not entered post-deploy | Enter the secret at Setup → Named Credentials → External Credentials → <ESR> → Principals (out-of-band secret; never in source). See Security Assessment (`06`) + Post-Config (`05`). | re-run Gate 2 from deploy-and-configure |
| runtime / validate-end-to-end | agent published but tool calls fail auth (no data / `We couldn't access the credential(s)`) | MCP perm set assigned only to the admin/running user, not the **Platform Integration User** the agent's callouts run as (W-21685162) | `sf org assign permset --name <PermSet> --on-behalf-of "<platform-integration-user>"` (or the anonymous-Apex equivalent); confirm the `Name LIKE 'Platform%'` match is the agent runtime user (`cloud@…`). See `refs/mcp-integration.md`. | re-run validate-end-to-end |
| MCP validate-end-to-end | tool not discoverable / agent can't invoke | MCP tool not bound on the agent (action still on the `mcpTool://<ESR>` placeholder), or perm-set/runtime-user gap above | Bind the tool (remove + re-add) and sync source; verify the runtime-user perm set; test a sample utterance. See `refs/mcp-integration.md` (validator 7.10) + MCP Workbench. | re-run Gate 2 validate-end-to-end |
| agent publish | publish blocked / activation error (NOT the MCP-target 500 above) | Agent not validated, or required licenses/features absent in the target org | Clear agent validate first; confirm Agentforce licenses/features (Pre-Instance Config `03`). | re-run Gate 2 from agent publish |
| agent publish | `property <X> was not found in the available list of properties [...]`, or a generic `Internal Error` after a hand-authored `outputs:` block | An MCP action carries a hand-authored `outputs:` block that does NOT match the tool's real `outputSchema` by **name and type**. Publish validates outputs against the registered tool schema even though `validate` + live-actions preview both PASS. Inventing an output name, or declaring an `array`/`number` schema property as `string`, fails publish. | Prefer NO `outputs:` block on MCP actions (the re-add path strips it — the tool supplies its own schema). If you must declare outputs, match the tool's `outputSchema.properties` exactly (names from `tools/list`); a subset of the **string-typed scalar** properties is the safe minimum. See `refs/mcp-integration.md` + `refs/agentscript-handoff.md`. | re-run Gate 2 from agent publish |
| dry-run / deploy | `The DeveloperName '<Agent>' is already in use by a Bot Definition` | The package ships BOTH `aiAuthoringBundles/<Agent>` and the compiled `bots/<Agent>` (+ `genAiPlannerBundles/`) under the same name — they collide on a fresh-org deploy (in the source org they co-exist only because publish linked them) | Deploy ONE representation: for a workshop/authoring org, exclude `bots/` + `genAiPlannerBundles/` and deploy the authoring bundle, then publish in-org; for a ready-to-run install, exclude `aiAuthoringBundles/` and ship the compiled bot. See `refs/mcp-integration.md` / `refs/packaging-analysis.md`. | re-run Gate 1 with the excluded dirs |
| runtime / preview | agent routes to the subagent but the tool call returns the wrong/default record (e.g. a fallback persona) | The action binds an arg from a state variable (`with X = @variables.X`) that the router never populated → an empty value is forced into the tool, overriding slot-fill | Bind MCP action args with **LLM slot-fill** (`with <arg> = ...`), not `@variables.X`, unless the variable is reliably set; and add `with <var> = ...` to the router's `@utils.setVariables`. ⚠️ A mock/tool that silently falls back to a default on empty/unknown input is demo-dangerous (confident wrong data) — prefer erroring. See `refs/agentscript-handoff.md`. | re-run preview |
| runtime / preview | employee agent published + active but a specific user can't see/run it | The user lacks **agent access** — an employee agent is invisible until granted | Create/assign an agent-access permission set (e.g. `Employee Agent Access`) to each user who should run the agent. Add as a Post-Config (`05`) step. | assign permset, re-test |

## Companion-skill degradation
If `agentforce-adlc` or `sf-mcp-partner-toolkit` is not installed, the matching Gate step is
recorded SKIP with a Mitigation pointing to install the companion (mirror the degraded-mode
contract in SKILL.md). Phase D never hand-runs a delegated lifecycle step.
