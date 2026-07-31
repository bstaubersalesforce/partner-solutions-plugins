# Scaffold Flow

Scaffold mode stamps the workshop kit skeleton from an overlay (`config/kit.json`). The scaffolder owns structure (directory tree, headers, generated `check.sh`); author mode owns substance (module bodies, provisioning doc, commercial content).

## Step 1: Intake overlay conversationally

Build the `config/kit.json` overlay through conversation, asking only where values are not inferable from the user's prompt. Read `refs/kit-anatomy.md` for the full schema.

**Core overlay keys:**

```jsonc
{
  "name": "headless360",                    // short identifier (no spaces)
  "title": "Headless 360 Partner Activation Workshop",
  "mode": "lab",                            // "lab" (multi-partner) | "engagement" (1:1)
  "duration": "2-day",
  "partner_overlay": "reference",           // "reference" (neutral) | "<partner>" (retargeted)
  "surfaces": { "slack": true, "react_agent_api": true, "clt_lex": true, "mobile": false },
  "provisioning": {
    "needs_org": true,                      // false ⇒ Educate-only (first-class outcome)
    "model": "de-per-team",                 // see provisioning-models.md
    "required_features": ["Agentforce", "HostedMCP"]
  },
  "modules": [                              // ordered; scaffolder stamps headers, author fills bodies
    { "n": 0, "title": "Comprehend", "checkpoint": false },
    { "n": 1, "title": "Provision Your Environment", "checkpoint": true },
    // …
    { "n": 7, "title": "Extend", "checkpoint": false }
  ],
  "content_dirs": { "slides": true, "commercial": true, "web": false, "showcase": false, "prework": false },
  "reference_build": { "source": "pie-poc-forge", "path": "sfdx/" }  // "pie-poc-forge|freeform|none"
}
```

**Infer when possible:**
- If the user says "2-day Agentforce workshop for multiple partners teaching Slack + React Agent API," infer: `mode: "lab"`, `duration: "2-day"`, `surfaces: {slack:true, react_agent_api:true, …}`, `provisioning.required_features: ["Agentforce"]`.
- If "educate-only, no hands-on builds," infer: `provisioning.needs_org: false`.
- If "extend the nCino Treasury PoC into a 1:1 workshop," infer: `mode: "engagement"`, `partner_overlay: "nCino"`, `reference_build.source: "pie-poc-forge"`.

**Ask only where ambiguous:**
- The module arc (how many modules; which are checkpoints) is not inferrable from a one-line request — ask: "What's the hands-on module sequence? Example: Module 0 Comprehend → Module 1 Provision (🔴 checkpoint) → Module 2 Deploy → Module 3 Test → Module 4 Extend."
- If the user mentions "hands-on builds" but doesn't state provisioning constraints, ask: "Do participants need their own orgs (hands-on builds), or is this facilitator-demo / shared-backend? If hands-on, which features are load-bearing (Agentforce, Data Cloud connectors, managed packages)?"

**One conversational pass.** Do not serialize into a form. Example intake:

> **User:** "Build a 2-day lab teaching partners Headless 360 — Slack, React Agent API, CLT. Educate First, then hands-on. Free DE per team."
>
> **workshop-forge:** "Got it — 2-day multi-partner lab, Agentforce surfaces (Slack / React Agent API / CLT), free DE provisioning. What's the module arc? Example: Module 0 Comprehend → Module 1 Provision (checkpoint) → Module 2 Deploy → Module 3 Configure MCP (checkpoint) → Module 4 Test All Surfaces → Module 5 Extend."
>
> **User:** "Yes, that arc. Modules 1 and 3 are checkpoints."
>
> **workshop-forge:** "Perfect. Last question: do you want `slides/` and `commercial/` directories for deck outlines and talk-track, or just the core docs?"
>
> **User:** "Both."
>
> **workshop-forge:** [writes `kit.json`, runs scaffolder]

---

## Step 2: Refuse if target directory already exists

**Before writing anything,** check if `<kit-name>/` (the directory named by `kit.json.name`) already exists in the current working directory.

```bash
if [ -d "<kit-name>" ]; then
  echo "Target directory '<kit-name>/' already exists. Never overwrite. Choose a new name."
  exit 1
fi
```

**Hard refusal.** workshop-forge never overwrites an existing kit — the risk of destroying hand-authored content (module bodies, retro notes, facilitator observations) is unacceptable. Ask the user for a different `name` and re-run Step 1.

---

## Step 3: Write `kit.json` and run the scaffolder

Write the overlay to `<kit-name>/config/kit.json`, then invoke the scaffolder:

```bash
mkdir -p <kit-name>/config
cat > <kit-name>/config/kit.json <<'EOF'
{
  "name": "headless360",
  "title": "Headless 360 Partner Activation Workshop",
  // … full overlay
}
EOF

python3 scripts/scaffold_kit.py <kit-name>/config/kit.json <kit-name>/
```

**What the scaffolder does (deterministic, idempotent):**

1. **Always renders:** `README.md`, `GUIDE.md`, `FACILITATOR.md`, `LESSONS-LEARNED.md`, `.env.example`, `.gitignore` (from `templates/*.tmpl`), shared shell library, lifecycle scripts (numbered to match the provisioning model, from `templates/scripts/*.sh.tmpl`).
2. **Conditionally renders:**
   - Org-provisioning doc + preflight validator + deploy/assign scripts (from `templates/docs/org-provisioning.md.tmpl` + `templates/scripts/*.sh.tmpl`) **iff `provisioning.needs_org: true`**.
   - `docs/framework.md`, `docs/buildability-matrix.md` (placeholders; author mode decides whether to fill them).
   - `content_dirs` subdirectories per the overlay (`slides/`, `commercial/`, etc.) with stub READMEs.
   - `sfdx/` placeholder per `reference_build.path` (non-`none` source).
3. **Stamps GUIDE.md module headers** from `modules[]` array, inserting `🔴 **Checkpoint:** <reason>` where `checkpoint: true`. Module bodies are stubs (`<!-- author mode fills this -->`).
4. **Generates the kit's own `check.sh`** enumerating exactly the files rendered (so assertions match the conditional shape — e.g., no org-provisioning doc assertion if `needs_org: false`).

The scaffolder is **read-only to this skill's own directory** — it writes into `<kit-name>/`, never into `~/.claude/skills/workshop-forge/`.

---

## Step 4: Run the generated kit's `check.sh`

Validate the scaffolded tree:

```bash
cd <kit-name>
bash {generated-kit}/check.sh
```

**Must be green.** The generated `check.sh` asserts:
- All expected files exist (common skeleton + conditional parts per the overlay).
- No orphaned refs (e.g., GUIDE links to `docs/org-provisioning.md` only if `needs_org: true`).
- Template placeholders are replaced (e.g., `{{KIT_NAME}}` → the actual name).

If `check.sh` fails, the scaffolder has a bug — do not proceed. Report the failure and the exact error to the user.

**Why run it now?** The scaffolder is deterministic and golden-file-tested, but running the kit's own check before handoff catches any template-rendering edge case the golden fixtures didn't exercise.

---

## Step 5: Handoff

Report the scaffolded tree and direct the user to author mode:

```
✅ Scaffolded workshop kit: <kit-name>/

Tree:
  README.md, GUIDE.md, FACILITATOR.md, LESSONS-LEARNED.md
  config/kit.json
  {generated kit scripts/}
  docs/org-provisioning.md, docs/framework.md, docs/buildability-matrix.md
  slides/, commercial/
  sfdx/

GUIDE modules (headers stamped, bodies stubbed):
  Module 0: Comprehend
  Module 1: Provision Your Environment  🔴 Checkpoint
  Module 2: Deploy the Reference Build
  Module 3: Configure MCP and Connectors  🔴 Checkpoint
  Module 4: Test All Surfaces
  Module 5: Extend

Next: Run **author mode** to fill module bodies, provisioning doc, framework, commercial talk-track, and import the reference build.
```

Include the directory path (absolute or relative) so the user knows where to find the kit. The report is concise — no need to explain every file; the user can read the tree.

**Do not run author mode automatically.** Scaffold and author are independent stages — the user may want to inspect the skeleton, adjust `kit.json`, or prepare upstream artifacts before authoring.
