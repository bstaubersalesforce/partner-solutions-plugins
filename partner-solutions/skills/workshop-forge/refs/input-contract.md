# Author-mode input contract

How workshop-forge **author mode** detects and prioritizes its sources when authoring content onto a scaffolded kit.

## Priority order

Author mode looks for input in this order, taking the first match:

### 1. Upstream family artifact (preferred)

An **existing pie-poc-forge PoC package** or **pov-builder POV** — if the user points at one. These are the most workshop-ready sources: they already carry the technical overlay, a working reference build, and strategic framing that maps cleanly to the workshop kit's structure.

- **pie-poc-forge PoC package:** an SFDX reference build (the installable agent/flows/DMOs) + execution canvas (config/gaps/limitations) + the technical overlay (surfaces, features, dependencies). Author mode wraps this into the kit's `sfdx/` directory and extracts the agent story, setup steps, and edge cases from the canvas to seed the GUIDE, org-provisioning doc, and buildability-matrix.

- **pov-builder POV:** 12 strategic artifacts including the value-prop narrative, pilot framework, demo script, and required-capabilities matrix. Author mode lifts the demo script into the GUIDE's Comprehend module, the pilot framework into the facilitator reference, and the capabilities + gaps into the buildability-matrix.

**Handoff shape:** either a directory path (`/path/to/partner-headless360-poc/`) or a direct pointer to the package's root / POV artifact directory.

### 2. Freeform sources (fallback)

Unstructured input the user provides or points to when an upstream family artifact isn't available. Author mode reads these to infer the workshop overlay and content; it asks clarifying questions to fill residual gaps.

Common freeform sources:
- **Product brief** — feature overview, use cases, architecture.
- **Research notes** — e.g., a `.notes/` directory with exploration findings, open questions, risks.
- **Pasted requirements** — inline in the conversation: "This workshop teaches partners how to … surfaces: Slack, React. Duration: 2 days. Educate-first, no participant orgs needed."
- **Prior workshop slide decks or run guides** — extracts the module arc and key teaching moments.

Author mode treats these as a starting point, not a specification — it reasons to fill gaps (provisioning model, checkpoint placement, residual commercial talk-track) and **flags what it inferred vs what was explicit** in the handoff.

### 3. Interview (last resort)

If no upstream artifact or freeform sources are available, author mode conducts a **structured interview** to elicit the overlay + content. Questions are focused and skip anything already in `config/kit.json` (the scaffolder wrote that; author mode reads it).

The interview extracts:
- **Agent story:** what the agent does, which surfaces it spans, the pilot use case.
- **Module arc:** Comprehend (demo) → Build (step-by-step) → Test → Troubleshoot → Extend. Where do 🔴 checkpoints land?
- **Provisioning constraints:** Are participant orgs required? If yes, what features are load-bearing (Agentforce, Data Cloud, MCP, managed packages)? Pre-provisioning timeline?
- **Commercial overlay (if `commercial/` is enabled):** OEM/resale motion, pricing dependencies, partner value-add.
- **Gaps and disclaimers:** what's out of scope, what requires manual follow-up, what's a known limitation.

Author mode asks one question at a time; each answer narrows the next. The interview is conversational, not a form — the user can paste a paragraph or link to notes at any step to short-circuit remaining questions.

## The "wrap, do not invent" rule

**Hard constraint:** workshop-forge **wraps the reference build into `sfdx/`; it never regenerates agent or SFDX metadata.**

Generating working Agentforce/SFDX metadata — `.agent` scripts, Apex actions, DMOs, flows, MCP tool bindings, permission sets — is **pie-poc-forge's job** (or pov-builder's notional reference agent, or a freeform hand-built package the user provides). workshop-forge assumes the reference build already exists and is installable; its task is to **scaffold the teaching layer around it** (modules, provisioning doc, facilitation guide, commercial talk-track) and **import the SFDX payload**, not create it.

### When the user asks workshop-forge to generate metadata

If the user says "build the agent for this workshop" or "generate the SFDX package," **redirect to pie-poc-forge**:

> "Generating the agent and SFDX metadata is pie-poc-forge's role. I can help you run pie-poc-forge to build the reference PoC package, then return here to wrap it into the workshop kit. Would you like to start the pie-poc-forge build now, or do you already have a reference build I should import?"

### What workshop-forge does with an existing reference build

When the user provides a pie-poc-forge PoC package (or freeform SFDX tree):

1. **Import the SFDX payload** into the kit's `sfdx/` directory — copy the `force-app/` tree and `sfdx-project.json`, preserving structure.
2. **Extract the story** — read the agent script / DMO definitions / flow metadata to understand what the agent does; lift this into the GUIDE's Comprehend module (the demo narrative).
3. **Extract setup dependencies** — parse the execution canvas (if pie-poc-forge), or read `package.json` / `.forceignore` / connected-app config, to enumerate the pre-work (MCP server setup, Data Cloud connector config, ECA/OAuth, permission-set assignments). Write this into the GUIDE's Build module and `docs/org-provisioning.md`.
4. **Extract gaps and edge cases** — the limitations from the pie-poc-forge canvas (e.g., "Data Cloud Zero Copy requires BigQuery project pre-provisioned") become disclaimers in the FACILITATOR doc and the buildability-matrix.

The reference build's metadata is **read-only to workshop-forge** — it does not edit `.agent` files, flows, or Apex. If the user requests a change to the agent itself (e.g., "add a new tool"), workshop-forge redirects to pie-poc-forge to regenerate the PoC, then re-imports the updated package.

## The family seam

pie-poc-forge's **build** (an installable PoC SFDX package + execution canvas) becomes workshop-forge's **`sfdx/` payload** (the thing participants install and drive). This seam is why upstream family artifacts are the preferred input — they're already shaped for the handoff.

**pov-builder** sits one step earlier: its **POV** (strategic narrative + demo script + pilot framework) informs pie-poc-forge's build spec, which in turn seeds workshop-forge's teaching overlay. The three skills form a **POV → PoC → workshop** pipeline for partner activation.

## Detecting the input in practice

Author mode runs this heuristic on the user's prompt + conversation context:

1. **Directory path or "use the PoC at …"** → check if it's a pie-poc-forge shape (has `sfdx/`, `canvas.md`, `config/build.json`) or a pov-builder shape (has `artifacts/` with numbered files). If yes → upstream artifact path.
2. **Pasted requirements or linked brief** → freeform path; parse what's explicit, flag what's inferred.
3. **"I don't have a reference build yet" or ambiguous** → ask: "Do you have an existing pie-poc-forge PoC package or pov-builder POV I should use, or would you like me to infer the workshop content from a brief / notes / interview?" Then route to freeform or interview based on the answer.

The heuristic prioritizes **not guessing** — if the input is ambiguous, author mode asks one clarifying question before committing to a path.
