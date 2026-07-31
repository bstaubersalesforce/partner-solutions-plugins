# Packaging analysis — 1GP vs 2GP + metadata coverage

## Decision inputs
Read `decisions.packaging` and the component inventory. Produce the `04-package-analysis` artifact.

## 1GP vs 2GP rules
- **2GP (recommend by default for PoC):** source-driven, IDE-friendly, supports `sfdx-project.json` package directories, easier versioning, no Dev Hub namespace lock-in for unlocked packages. Reference: dev2gp comparison.
- **1GP:** choose only when the partner's existing managed package is 1GP and the PoC must extend it in place.
- Always state the recommendation, the reason, and the one fact that would flip it.

## Metadata coverage check
For every component in the inventory, classify:
- **Packageable** — supported in the chosen packaging model per the Metadata Coverage Report.
- **Unsupported / manual** — appears in the Unsupported Metadata Types list → moves to pre/post-config as a manual step, NOT into the package.
Emit a per-component table: component | type | packageable? | coverage note | action.

## Coverage verdicts must be VERIFIED, not recalled
Do not assert packageability of a non-obvious metadata type (Agent/Bot/GenAiPlanner, Data Cloud config, Named/External Credential, etc.) from memory. For each such type either:
- fetch the live Metadata Coverage Report for the target API version (WebFetch the report URL, or use context7), OR
- mark the verdict **Unverified** and require user confirmation before the package relies on it.
Every coverage table MUST carry an automatic disclaimer naming which verdicts were verified against the live report and which are unverified. Standard CustomObject/CustomField/ApexClass/LWC are safe to assert as supported.

## Agent: ship ONE representation, not both (nCino 2nd-org run)
An Agentforce agent exists as two metadata representations under the **same DeveloperName**: the authoring `aiAuthoringBundles/<Agent>` (the `.agent` source) and the compiled `bots/<Agent>` + `genAiPlannerBundles/<Agent>_vN` (the published runtime). In the source org they co-exist because publish links them — but deploying **both** into a fresh org fails: `The DeveloperName '<Agent>' is already in use by a Bot Definition`. Decide which to package/deploy:
- **Authoring bundle only** (exclude `bots/` + `genAiPlannerBundles/`) — for a workshop/iteration org where the agent will be published in-org. This is the usual PoC choice.
- **Compiled bot only** (exclude `aiAuthoringBundles/`) — for a ready-to-run install where the subscriber should not author.
Capture the choice in the coverage table and Post-Config; never deploy both under one name. (For 2GP, also recall the `mcpTool://` hashes don't transport — subscribers re-bind tools in their org regardless; see `refs/mcp-integration.md`.)

## Reference sources (consult, cite by name)
- Metadata Coverage Report — https://developer.salesforce.com/docs/metadata-coverage (verify per API version)
- Unsupported Metadata Types
- 1GP vs 2GP (dev2gp) comparison
