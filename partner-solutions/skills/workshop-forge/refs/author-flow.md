# Author Flow

Author mode writes intelligent content onto a scaffolded workshop kit: GUIDE module bodies, provisioning doc, framework + buildability-matrix docs, commercial talk-track, and slide outlines. It reads `config/kit.json` to know what to write; it **updates, never regenerates** from scratch (re-entrant).

**Prerequisite:** a scaffolded kit tree must exist (stamped by scaffold mode). If not, direct the user to run scaffold mode first.

---

## Step A1: Detect input

Author mode needs source material to write from. Detect and prioritize per `refs/input-contract.md`:

### Priority 1: Upstream family artifact (preferred)

An existing **pie-poc-forge PoC package** or **pov-builder POV** — the most workshop-ready sources.

**Detect:**
- User says "use the PoC at `/path/to/partner-headless360-poc/`" or "author from the nCino Treasury POV."
- User points to a directory with `sfdx/`, `canvas.md`, `config/build.json` (pie-poc-forge shape) or `artifacts/` with numbered files (pov-builder shape).

**What to extract:**
- **pie-poc-forge PoC:** the SFDX reference build (`sfdx/force-app/`), execution canvas (config/gaps/limitations), technical overlay (surfaces, features, dependencies). The agent story, setup steps, and edge cases seed the GUIDE, org-provisioning doc, and buildability-matrix.
- **pov-builder POV:** demo script (→ GUIDE Module 0 Comprehend), pilot framework (→ FACILITATOR), required-capabilities matrix + gaps (→ buildability-matrix), value-prop narrative (→ commercial talk-track).

### Priority 2: Freeform sources (fallback)

Unstructured input when no upstream artifact exists:
- Product brief (feature overview, architecture).
- Research notes (e.g., `.notes/` directory with findings, risks).
- Pasted requirements ("This workshop teaches … surfaces: Slack + React. Duration: 2 days. Educate-first.").
- Prior workshop slide decks or run guides.

**Parse what's explicit; flag what's inferred.** Example: "Inferred that participants need per-team orgs (hands-on build mentioned), but provisioning model unclear — defaulting to DE-per-team (Agentforce-centric, no Data Cloud connectors). Confirm if Data Cloud is load-bearing."

### Priority 3: Interview (last resort)

If no upstream artifact or freeform sources, conduct a **structured interview** to elicit:
- **Agent story:** what the agent does, which surfaces, the pilot use case.
- **Module arc details:** where do 🔴 checkpoints land? What's the validation command at each checkpoint?
- **Provisioning constraints:** are participant orgs required? Load-bearing features?
- **Commercial overlay (if `commercial/` enabled):** OEM/resale motion, pricing dependencies, partner value-add.
- **Gaps and disclaimers:** what's out of scope, known limitations.

Ask one question at a time; each answer narrows the next. The interview is conversational — the user can paste a paragraph or link to notes at any step to short-circuit.

**The "wrap, do not invent" rule:**

workshop-forge **never generates agent or SFDX metadata** (`.agent` scripts, Apex, flows, DMOs, MCP tool bindings). Generating the reference build is **pie-poc-forge's job** (or a freeform hand-built package the user provides).

If the user asks "generate the agent for this workshop," **redirect to pie-poc-forge**:

> "Generating the agent and SFDX metadata is pie-poc-forge's role. I can help you run pie-poc-forge to build the reference PoC package, then return here to wrap it into the workshop kit. Would you like to start the pie-poc-forge build now, or do you already have a reference build I should import?"

---

## Step A2: Wrap the reference build into `sfdx/`

If the input includes an SFDX reference build (pie-poc-forge PoC or freeform package), **import it** into the kit's `sfdx/` directory (per `kit.json.reference_build.path`).

**Import, never regenerate:**

1. **Copy the SFDX payload** — the `force-app/` tree and `sfdx-project.json`, preserving structure. If the source is a pie-poc-forge PoC, copy from `<poc-path>/sfdx/`; if freeform, from wherever the user points.
2. **Read the metadata** to understand what the agent does — parse `.agent` scripts, DMO definitions, flow metadata. This becomes the demo narrative in GUIDE Module 0.
3. **Extract setup dependencies** — read the execution canvas (if pie-poc-forge), or parse `package.json`, `.forceignore`, connected-app config, to enumerate pre-work (MCP server setup, Data Cloud connector config, ECA/OAuth, permission-set assignments). Write this into the GUIDE's Build module and `docs/org-provisioning.md`.
4. **Extract gaps and edge cases** — limitations from the pie-poc-forge canvas (e.g., "Data Cloud Zero Copy requires BigQuery project pre-provisioned") become disclaimers in FACILITATOR and buildability-matrix.

**Do not edit the reference build's metadata** — it is read-only to workshop-forge. If the user requests a change to the agent itself (e.g., "add a new tool"), redirect to pie-poc-forge to regenerate the PoC, then re-import the updated package.

**If no reference build:** `kit.json.reference_build.source: "none"` means the kit is Educate-only or demo-driven — skip this step.

---

## Step A3: Author onto the scaffolded tree

Write the content per the overlay + input sources. The scaffolder stamped headers and stubs; author mode fills the bodies.

### GUIDE module bodies (per `refs/guide-conventions.md`)

Write hands-on steps, explanations, code snippets, validation commands, and links to framework.md or provisioning docs.

**Module 0: Comprehend** — conceptual orientation before build:
- What the reference build is (surfaces, architecture, problem it solves).
- How it works (which services talk to which; which metadata types carry logic).
- Where the extension seams are (what a partner would customize in a paid SOW).

Source: demo script from pov-builder POV, or agent-story extraction from the pie-poc-forge canvas, or interview.

**Modules 1 through N−1** — hands-on build phases:
- Step-by-step: provision/access org → deploy reference build → configure connectors (MCP, Data Cloud) → smoke-test one surface → exercise all surfaces → observe behavior → understand customization seams.
- At **🔴 checkpoints** (stamped by scaffolder where `kit.json.modules[].checkpoint: true`): write the validation command ("Run X; you should see Y; if not, revisit step Z") and the reason order matters.

**Module N: Extend** — always the final module:
- Participants modify/extend the reference build: add a new action, integrate a new data source, wire a new surface, scope a paid-SOW enhancement.
- The "you own it now" milestone.

**Method: deriving module sequence, validation commands, and checkpoint reasons**

When authoring from a pie-poc-forge PoC (or freeform reference build), derive the Module 1→N−1 arc from the **deployment and configuration dependencies** in the source, not by invention:

1. **Sequencing the module arc:** Linearize the PoC's metadata (Apex classes, permission sets, Lightning components, flows, agents, MCP server configs) into a Module 0→N Comprehend→Extend sequence by **following deploy/enable dependencies**:
   - **Module 0 (Comprehend)** = conceptual anchor (always first).
   - **Early modules (1–2)** = dependencies first — org provisioning, permission-set assignment, feature-flag enablement, foundational configuration (e.g., MCP server registration, Data Cloud connector setup).
   - **Middle modules (3–N−2)** = the core skill/action build — deploy the SFDX reference build, configure the agent, wire surfaces (Slack, CLT, React Agent API), smoke-test each.
   - **Penultimate module (N−1)** = observe and understand — exercise all surfaces, trace behavior, identify extension seams.
   - **Module N (Extend)** = participants modify/extend the reference build (always final).

   The heuristic: **what must be in place before X can work?** Permission sets before agent invocation; ECA/JWT setup before MCP discovery; connector config before data ingestion. Read the pie-poc-forge canvas's execution section (if present) or parse the SFDX metadata's inter-dependencies (e.g., an agent's `.agent` script references a flow → the flow must deploy before the agent is tested; a flow calls Apex → the Apex must exist before the flow deploys). Map these dependencies to the Comprehend→…→Extend arc.

2. **Validation commands:** Source these from the pie-poc-forge canvas's execution/config section or from the SFDX metadata itself:
   - **If the source provides smoke-tests:** an Apex test class in `force-app/` → write `sf apex run test --class-names <ClassName> --target-org <alias>`; a manual invocation step in the canvas → transcribe it as the validation command.
   - **If the source has NO explicit smoke-test:** author a concrete `sf` CLI verification command per module that exercises the step's output (e.g., after permission-set assignment → `sf org list user --target-org <alias> | grep <PermSetName>`; after agent deploy → `sf data query --query "SELECT Id, DeveloperName FROM Bot WHERE DeveloperName='<BotName>'" --target-org <alias>` to confirm the bot exists). **Flag these as author-supplied** in a comment: `<!-- validation command: author-supplied; source had no explicit smoke-test -->`.
   - **Make them specific and runnable** — "verify it works" is not a validation command; `sf apex run test --class-names EmployeeAgentTest --target-org team01` is.

3. **Checkpoint reasons (why 🔴):** Checkpoints mark **silent-failure or order-dependent** steps. Source the reason from the provisioning-models.md buildability patterns or from known failure modes:
   - **JWT token / ECA setup** → "Required before MCP discovery; success is a 201 response that doesn't prove functionality until the agent calls the tool. If skipped, MCP tools appear in Setup but invocations fail silently."
   - **Permission-set assignment** → "Required before agent invocation; no UI clue if it fails. If skipped, agent returns 'access denied' with no stack trace pointing to the missing permission."
   - **Deploy-before-assign ordering** → "Metadata must exist before permission sets can reference it. If reversed, the permission set references an unknown object and silently fails to grant access."
   - **Feature-flag enable (e.g., Agentforce)** → "Silent until you try to use the feature; manifests as 'feature not available' errors in agent sessions."

   **Name the specific failure mode** in the checkpoint reason, not "this step is important." The reason anchors the facilitator's response when a team hits the failure.

**Voice:** senior Salesforce advisor briefing a partner team. Lead with the conclusion; no hedging; flag uncertainty explicitly. Example uncertainty flag: "⚠️ Unverified: whether free DE includes Hosted MCP + `mcp_api` scope out of the box (headless360 uses this; confirm pre-event)."

### `docs/org-provisioning.md` (iff `kit.json.provisioning.needs_org: true`)

Reason through `refs/provisioning-models.md` (the three-step method) to produce:

1. **A recommendation with rationale** — "Provision one free DE per team (Option C), because this workshop is Agentforce-centric with no hard Data Cloud dependency, and DE is the officially-modeled path (Try Headless 360)."
2. **Feature-dependency → org-type reasoning** — why the recommended model fits the load-bearing features (Agentforce, Data Cloud connectors, managed packages, etc.).
3. **Universal operational rules** — preflight T-minus 3 business days, safety-net reference org, per-org ECA/PKCE/JWT MCP setup script (never auto-provisioned), smoke-test the real flow (not just the status dot), orphaned-metadata fix pre-staged.
4. **Residual confirmations flagged** — "Three items remain before final lock: (1) does free DE include Hosted MCP + `mcp_api` scope? (2) can we provision 4–8 DE orgs cleanly for one event? (3) does an SDO template offer a genuinely faster pre-baked path for this exact stack?"

**Do not just list options** — reason to a recommendation. The provisioning doc is decision support, not a menu.

### `docs/framework.md` (discretionary)

Write this **iff the kit involves teaching a multi-component architecture** (e.g., MCP bridges, CLT + Slack + React Agent API in headless360). Explains:
- The architecture (which components, how they talk, what each owns).
- The contract between components (e.g., MCP tool discovery → CLT tool-call invocation → MCP server response).
- Extension patterns (where to add a new surface, new data source, new action).

Source: pie-poc-forge canvas, pov-builder architecture narrative, or freeform research notes.

**Skip if:** the reference build is a single-surface agent with no multi-component teaching moment.

### `docs/buildability-matrix.md` (discretionary)

Write this **iff the kit teaches partners how to scope/price a paid-SOW extension** of the reference build. Enumerates:
- What's in the reference build (baseline; free/delivered in the kit).
- Common paid extensions (e.g., "add Provider Search action → 20–40 hours; integrate Redshift connector → 40–80 hours").
- Dependency reasoning (e.g., "Data Cloud Zero Copy requires BigQuery project pre-provisioned; org edition constraint").

Source: pie-poc-forge execution canvas (gaps/limitations), pov-builder required-capabilities matrix, or interview.

**Skip if:** the workshop is Educate-only or the commercial motion is out of scope.

### `commercial/` talk-track (iff `kit.json.content_dirs.commercial: true`)

Write **stub outlines** for partner-facing commercial materials:
- `commercial/01-value-prop.md` — OEM/resale motion, pricing dependencies, partner margin.
- `commercial/02-positioning.md` — competitive differentiation, target segments, key messages.
- `commercial/03-objection-handling.md` — common objections + responses.

Source: pov-builder POV commercial artifacts, freeform brief, or interview.

**Voice:** partner-facing sales enablement, not internal strategy. Lead with the partner's business outcome.

### `slides/` outline (iff `kit.json.content_dirs.slides: true`)

Write a **stub slide outline** (markdown list, not a deck):
- `slides/00-outline.md` — Module 0 Comprehend key concepts (10–15 slides), Module arc summary (1 slide per module), Extension patterns (3–5 slides), Q&A.

The outline is a scaffolding prompt for the facilitator or a slide-deck author. workshop-forge does not generate PowerPoint/Keynote files (out of scope; delegate to a deck-authoring tool or human).

---

## Step A4: Re-run `check.sh`

Validate the authored tree:

```bash
cd <kit-name>
bash {generated-kit}/check.sh
```

**Must be green.** The generated `check.sh` asserts:
- All expected files exist (common skeleton + conditional parts per the overlay).
- No orphaned refs — e.g., GUIDE links to `docs/org-provisioning.md` only if `needs_org: true`; GUIDE mentions framework.md only if that file was authored.
- Module numbering in GUIDE matches FACILITATOR.

If `check.sh` fails, fix the issue (missing link target, broken ref, orphaned stub) and re-run.

**Why run it now?** Authored content introduces links and cross-refs that the scaffolder couldn't validate. The kit's own check enforces internal consistency.

---

## Step A5: Handoff

Report what was authored vs stubbed vs residual gaps:

```
✅ Authored content onto <kit-name>/:

**Authored:**
  - GUIDE.md: all 6 module bodies (Comprehend → Extend), 🔴 checkpoints validated (Modules 1 + 3)
  - docs/org-provisioning.md: free DE-per-team recommendation + rationale (3 residual confirmations flagged)
  - docs/framework.md: MCP bridge + multi-surface architecture (Slack / React Agent API / CLT)
  - docs/buildability-matrix.md: baseline + 4 common paid extensions (20–80 hour ranges)
  - sfdx/: imported pie-poc-forge PoC (headless360-employee-agent, 8 files)

**Stubbed (outlines written, detail deferred):**
  - commercial/01-value-prop.md, commercial/02-positioning.md, commercial/03-objection-handling.md
  - slides/00-outline.md (Module 0 + arc summary + extension patterns)

**Residual gaps:**
  1. ⚠️ Unverified: whether free DE includes Hosted MCP + `mcp_api` scope out of the box (confirm pre-event).
  2. Per-org ECA/PKCE/JWT setup script (named `04-mcp-connect-setup.sh` in the generated kit — not yet a template) is referenced but not yet implemented — pie-poc-forge's canvas flags this as manual; consider scripting the ECA card generation.
  3. Smoke-test checklist in org-provisioning.md references "invoke the agent and see data flow back" — FACILITATOR should carry the exact CLI commands / Slack test-message for facilitator dry-run.

Next: review the kit, resolve residual gaps, and run a preflight dry-run per `docs/org-provisioning.md`.
```

**The handoff is explicit about what's done vs what's deferred.** Authored content is source-grounded and uncertainty-flagged; stubs are clearly marked; residual gaps are enumerated with enough context for the user (or facilitator) to resolve them.

**Re-entrancy:** if the user says "update Module 3 to add a troubleshooting step," author mode re-reads the kit (including the existing authored content), makes the edit, and re-runs `check.sh`. It does not regenerate the entire kit — only the requested change.

---

## Re-entrant updates

Author mode is **re-entrant** — it updates, never regenerates from scratch.

**Update scenarios:**
- "Add a troubleshooting step to Module 3" → read GUIDE.md, insert the step, re-run `check.sh`.
- "Expand the framework.md to cover the MCP server's authentication flow" → read framework.md, append the section, re-run `check.sh`.
- "Fill in the commercial stub for value-prop" → read `commercial/01-value-prop.md`, replace stub with full content.
- "Import a new reference build" → re-run Step A2 (wrap the new SFDX payload), then re-sync GUIDE Module 0 (Comprehend) to match the updated agent story.

**What author mode does NOT regenerate:**
- The scaffolded skeleton (headers, lifecycle scripts, `check.sh`, common.sh) — those are scaffold mode's output and are idempotent; author mode leaves them alone unless the user explicitly requests a change.
- Module headers and checkpoint markers — those are stamped by the scaffolder from `kit.json.modules[]`; if the user wants to reorder modules or add a checkpoint, edit `kit.json` and re-run scaffold mode (or manually edit GUIDE.md).

**Detection:** if the user says "update the kit" or "enrich Module X" while in a directory with an existing scaffolded tree (presence of `config/kit.json` + `GUIDE.md`), author mode knows this is a re-entrant update — it does not re-scaffold.

---

## Limitations of author mode

Author mode is **assistive synthesis**, not fully-automated final kit generation:

- **Does not invent validation commands it can't source.** If the pie-poc-forge canvas or SFDX metadata lacks explicit smoke-tests, author mode writes a plausible `sf` CLI verification command and flags it as author-supplied — human review must confirm it's correct.
- **Does not guarantee completeness.** Authored content is grounded in the upstream sources provided (PoC canvas, POV artifacts, freeform brief). If those sources omit a critical step (e.g., a manual OAuth setup, a Data Cloud connector pre-requisite), author mode can only flag the gap, not fill it.
- **Requires human review before delivery.** The generated GUIDE, provisioning doc, and commercial stubs are drafts — they reflect what the sources say and what the method infers, but they are not validated against a live workshop run. The facilitator or kit owner must review, test, and complete them.

Scaffolded output (skeleton, `check.sh`, lifecycle scripts) is deterministic and tested; authored content is source-grounded synthesis that makes gaps explicit.

---

## Summary

Author mode:
1. Detects input (upstream artifact > freeform > interview).
2. Wraps the reference build into `sfdx/` (import, never regenerate).
3. Drafts onto the scaffolded tree: GUIDE bodies (per `guide-conventions.md`), provisioning doc (per `provisioning-models.md`), framework + buildability docs, commercial stubs, slide outlines — source-grounded, uncertainty-flagged, gaps explicit.
4. Re-runs `check.sh` (links resolve, no orphaned refs).
5. Handoffs: authored vs stubbed vs residual gaps.

Re-entrant: updates, never regenerates. Assumes a scaffolded tree exists; if not, directs the user to scaffold mode first.
