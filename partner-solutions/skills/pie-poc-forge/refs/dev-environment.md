# Dev environment — scratch org definition + org-template decision

Produces the `10-dev-environment` canvas artifact AND the deployable `config/project-scratch-def.json` package file.

## Org template / snapshot decision (Phase A prompt)
Always offer the question in Phase A; **emphasize it when `appType` is OEM/Embedded** (the skill knows the app type from `requirements.json`). OEM/Embedded partners often already have a base org or packaging org to clone from.

- **If an org template / scratch-org snapshot ID is provided:** wire it into the scratch def via `snapshot` (scratch org snapshot name) or document a `sourceOrg` clone path. Record `decisions.orgTemplateId` in `requirements.json`.
- **If none:** generate a standard edition-based definition (the fallback). Record `decisions.orgTemplateId: null` and note in the artifact that a standard edition org will be created.

Never silently assume a template; absence is a valid, recorded answer.

## Scratch org shape (edition + features)
Derive `edition` and `features` from `buildTypes` and dependencies:
- **platform** → `Developer` edition baseline.
- **agent** → enable Agentforce-related features/settings; note any that require a snapshot or pre-provisioned org rather than a feature flag.
- **data360** → Data Cloud is typically NOT enableable via a scratch feature alone — flag it as requiring a snapshot/pre-provisioned org or a trial, and say so explicitly in the artifact.
- Map declared SF dependencies (FSC, Shield, Slack) to features where a scratch feature exists; where none exists, route the item to pre-instance config and note it here.

When a required capability cannot be turned on via a scratch `features` flag, say so — do not emit a scratch def that silently won't support the build.

## config/project-scratch-def.json
When `buildTypes` includes `agent` or `data360`, the scratch def MUST enable the Agentforce/Einstein features or the org cannot preview/deploy the agent (validator checks 6.1, 6.2). Required for any Agentforce build:
- `features`: `"EinsteinGPT"`, `"EnableAIGenerative"`, `"SalesforceAgent"` (and `"Einstein1AIPlatform"` **when MCP is in scope** — validator 7.8, so MCP server registration works in the scratch org).
- `settings.aiSettings`: `enableEinsteinGPT: true`, `enableAgentforce: true`.

Emit a valid scratch definition, e.g. (agent + MCP build):
```json
{
  "orgName": "<Partner> PoC Dev",
  "edition": "Developer",
  "features": [
    "EnableSetPasswordInApi",
    "EinsteinGPT",
    "EnableAIGenerative",
    "SalesforceAgent",
    "Einstein1AIPlatform"
  ],
  "settings": {
    "lightningExperienceSettings": { "enableS1DesktopEnabled": true },
    "aiSettings": { "enableEinsteinGPT": true, "enableAgentforce": true }
  }
}
```
Drop `Einstein1AIPlatform` if there is no MCP integration; drop the AI features entirely only for a pure-platform (no agent, no Data 360) build. If a snapshot is used, add `"snapshot": "<SnapshotName>"` and omit `edition`/`features` it conflicts with (snapshot defines the shape). Place the file at `config/project-scratch-def.json` (standard SFDX location); it is dev tooling, not deployed metadata.

## Create commands (for the artifact)
```bash
sf org create scratch --definition-file config/project-scratch-def.json --alias <partner>-poc --duration-days 30 --set-default
# or, from a snapshot:
sf org create scratch --definition-file config/project-scratch-def.json --alias <partner>-poc --duration-days 30
```
Note: a Dev Hub must be enabled and authenticated; snapshots require the Scratch Org Snapshot feature on the Dev Hub.

## Developer Quickstart — explicit step-by-step (REQUIRED in the artifact)
Always emit a concrete, numbered, copy-pasteable sequence a developer can run from a clean machine to a working org. Do not leave this as prose — give exact commands and what each does. Standard sequence (adapt the alias/org-template to the recorded decisions):
```bash
# 1. Clone / open the package in an IDE (VS Code + Salesforce Extensions, or your IDE of choice).
git clone <repo-url> && cd <partner>-poc        # or open the folder directly

# 2. Authenticate a Dev Hub (one-time per machine).
sf org login web --set-default-dev-hub --alias DevHub

# 3. Create the scratch org (standard def, or add --snapshot for an OEM/Embedded base org).
sf org create scratch --definition-file config/project-scratch-def.json \
  --alias <partner>-poc --duration-days 30 --set-default

# 4. (If a managed-package dependency was chosen) install it before deploying.
sf package install --package <04t...> --target-org <partner>-poc --wait 20 --no-prompt

# 5. Deploy the source.
sf project deploy start --manifest manifest/package.xml --target-org <partner>-poc

# 6. Assign the generated permission set so the objects/Apex are usable.
sf org assign permset --name <PermissionSetName> --target-org <partner>-poc

# 7. (If data is needed for the demo) load sample records.
#    sf data import tree --plan data/sample-data-plan.json --target-org <partner>-poc   # only if a data plan was generated

# 8. Open the org and validate.
sf org open --target-org <partner>-poc
sf apex run test --target-org <partner>-poc --wait 10   # if tests exist

# 9. (Optional) Pre-deploy validation without deploying.
sf project deploy start --manifest manifest/package.xml --target-org <partner>-poc --dry-run
```
Mark any step that does not apply (e.g. no managed-package dependency, no sample data) as "skipped — N/A" rather than omitting it silently, so the developer sees the full path. Post-deploy manual steps (Named Credentials, Data 360 streams, agent activation) live in the Post-Config Steps artifact, not here.
