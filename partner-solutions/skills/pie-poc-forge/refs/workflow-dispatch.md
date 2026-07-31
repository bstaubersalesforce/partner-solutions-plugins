# Workflow dispatch — Phase B fan-out + Phase C update

## Inline-vs-fanout heuristic
Count formula (exact): `len(objects) + len(components) + len(integrations)` from `requirements.json`.
- ≤ 6 → run generators inline, sequentially.
- > 6 → dispatch the Phase-B generators as parallel subagents (Workflow), then a barrier synthesis step.

Fan-out is purely a latency optimization — **the inline path is always correct** and may be used at any count. Do not treat fan-out as required for large plans; treat it as faster.

## Phase B generators (independent, read-only on requirements.json)
1. Packaging analysis (refs/packaging-analysis.md)
2. Security assessment (refs/security-review.md)
3. Gaps document (refs/gaps-document.md)
4. SFDX scaffold + manifests (refs/sfdx-scaffold.md → delegate to adlc-engineer)
5. Agentscript (refs/agentscript-handoff.md → delegate to developing-agentforce) — only if agentInScope

## Barrier synthesis (needs all of the above)
Assemble `01-execution-plan` and `08-component-manifest` from the generators' outputs, then run the two reconciliation steps below BEFORE rendering, then render the full canvas using the recipe.

### Synthesis step 1 — Re-sync `requirements.json` to what was actually built (MANDATORY, before fileHashes)
Generation often diverges from the Phase-A plan — a delegated agent/MCP build, a real integration that differs from the build plan, an object resolved differently than assumed. `requirements.json` was populated from the *plan*; after generation it MUST be re-synced to reality so it stays the source of truth (Phase C, fileHashes, and re-runs all depend on it):
- **`components[]`** — replace planned entries with what is actually in `force-app/` (real component names/types, e.g. the actual agent's API name, generated Apex/LWC, MCP metadata). Remove planned components that were cut; add ones that were generated.
- **`integrations[]`** — update to the real integration facts discovered during generation (verified endpoints, auth, tool lists, mock-vs-production — see the mock/production fields in `refs/requirements-schema.md`).
- **`objects[]`** — reflect how external/managed-package references were actually resolved (placeholder vs real lookup).
Do this re-sync FIRST; only then compute `fileHashes` over the final tree.

### Synthesis step 2 — Plan-vs-built reconciliation check (MANDATORY)
Before rendering, check the assembled artifacts against each other and against the re-synced `requirements.json` for contradictions, and resolve them — do NOT ship a self-contradictory package:
- **Hero/scope consistency:** the MVP/PoC opinion (`02`), the execution plan (`01`) hero, and the actual delegated build (e.g. the agent in `09`) must describe the SAME thing. If the real integration forced the build to differ from the plan's hero (common when a mock/real service exposes different capabilities than the build plan assumed), reconcile explicitly: update `01`/`02` to state what was actually built, and add a one-line **"Plan-vs-built divergence"** note naming what changed and why (e.g. "build plan assumed inbound covenant MCP; the available BA tools are advisory, so the PoC agent is advisory — covenant platform scaffold ships separately").
- **Component agreement:** every component named in `01`/`08` exists in `force-app/` and in `requirements.json.components[]`; no artifact references a component that was cut.
- **Integration agreement:** `06` (security), `08` (manifest), and the agent (`09`) describe the same integration shape (direction, auth, mock-vs-production) as `requirements.json.integrations[]`.
Record any unresolved divergence as a row in the Gaps document (`07`) rather than leaving it silently contradictory.

### Synthesis step 3 — Bundle validation gate (MANDATORY when the package contains an agent, MCP, or invocable Apex)
Before declaring the package done, run **`isv-validate-agentforce`** over the engagement package (full-suite mode, scan root = the package's `force-app/main/default` plus `config/` and `manifest/`). It mechanically checks the artifacts this skill generates — Apex packaging modifiers, Agent Script, packaging config, scratch-org features, and MCP registration — against ISV/2GP rules that the per-file authoring hooks do not catch.
- Run it, capture the PASS/WARN/FAIL scorecard, and **fold every FAIL (and material WARN) into the package** before finishing — fixing the generator-side defect, not just the file. Common ones this skill must get right up front (see `refs/sfdx-scaffold.md`, `refs/dev-environment.md`, `refs/mcp-integration.md`): `global`/`@JsonAccess` on 2GP invocable Apex (1.1–1.5), no `AiAuthoringBundle` in `package.xml` (5.4), Agentforce scratch features (6.1/6.2/7.8), MCP postInstall handler (7.5/7.9).
- Record the final scorecard summary in the Gaps document (`07`) — any remaining WARN that is intentional for a PoC (e.g. stub Apex without try/catch, placeholder namespace) is logged there with the reason, not silently dropped.
- If `isv-validate-agentforce` is not installed, note that the validation gate was skipped and recommend installing it.

## Rendering recipe (exact — do not reinvent per run)
Token contract — three filling layers, do not confuse them:
- **Skill-filled (before render):** the artifact `.md` body content tokens (`{{EXEC_SUMMARY}}`, `{{COMPONENT_INVENTORY}}`, `{{PARTNER}}`, `{{DATE}}`, etc.). Replace EVERY body token with real content first; copy `templates/NN-*.md` to `docs/NN-*.md` and fill.
- **Script-filled (during render):** the shell tokens, filled by `md-to-html.py` flags — `{{PARTNER_NAME}}`←`--partner`, `{{DOC_LABEL}}`←`--label`, `{{OPPORTUNITY_STAGE}}`←`--stage`, `{{GENERATED_DATE}}`←`--date`, `{{HOME_HREF}}`←`--home`, `{{CONTENT}}`←the rendered md body. NEVER put these shell-token names in an artifact `.md` body — they belong to the shell only.
- **Manually-filled index:** `output-index.html` is NOT rendered through `md-to-html.py`. Fill its tokens (`{{PARTNER_NAME}}`, `{{GENERATED_DATE}}`, `{{BUILD_TYPES}}`, `{{CHANGELOG}}`) by direct substitution, then assert zero `{{...}}` remain (see step 3).

Per artifact (01..08, 10, 11, 12 always; 09 only if agentInScope), from the engagement package root:
```bash
SKILL=<path-to>/pie-poc-forge
python3 "$SKILL/scripts/md-to-html.py" \
  --md   "docs/<slug>.md" \
  --shell "$SKILL/templates/document-shell.html" \
  --out  "docs/<slug>.html" \
  --partner "<Partner>" --label "<Artifact Label>" --stage "<Org62 stage>" \
  --date "<YYYY-MM-DD>" --home "index.html"
```
`--home index.html` is REQUIRED (flat docs/ layout uses a single `index.html`); omit it and the back-link is dropped.

Then build and verify the index:
1. Substitute the index tokens into `templates/output-index.html` → `docs/index.html`. The index ships pre-built with one descriptive card per artifact, grouped by the PIE engagement cycle (Align & Kickoff → Scope & Build → Deploy → Review). Tokens to fill: `{{PARTNER_NAME}}`, `{{ARTIFACT_COUNT}}`, `{{GENERATED_DATE}}`, `{{BUILD_TYPES}}`, `{{CHANGELOG}}`. If `agentInScope` is false, REMOVE the `09 · Agentscript` card `<div class="card">…</div>` from the Scope & Build group (and set `{{ARTIFACT_COUNT}}` accordingly).
2. Run the home-link enforcer over the docs dir (flat layout, explicit index):
   `python3 "$SKILL/scripts/ensure-home-link.py" --dir docs --index index.html`
3. **Index zero-token assertion:** `grep -l '{{' docs/index.html` MUST return nothing. If any token remains, the index is unfilled — fix before declaring the canvas done. (`md-to-html.py` enforces this for artifacts automatically; the index needs this explicit check because it is not rendered through the script.)

## In-artifact links (cross-reference what we generated)
When an artifact's body text references another file THIS skill generated, write it as a Markdown link so `md-to-html.py` renders a clickable relative anchor. Links are relative to `docs/` (where the rendered HTML lives):
- **Another canvas doc** → link to its `.html`: `[Pre-Instance Config](03-pre-instance-config.html)`, `[Gaps Document](07-gaps-document.html)`.
- **A generated package file** → link with the `../` prefix (package files sit above `docs/`): `[package.xml](../manifest/package.xml)`, `[scratch org definition](../config/project-scratch-def.json)`, `[BankingAdvisorMcpService.cls](../force-app/main/default/classes/BankingAdvisorMcpService.cls)`.
Only link to files that actually exist in this package. Do NOT link to external docs this way, and never invent a path. Plain prose stays plain; the link is added only on the first meaningful mention.

## Phase C — re-entrant update
1. Diff new requirements vs stored requirements.json.
2. Regenerate only affected artifacts + manifest.
3. Edit-preservation: for each file, compare on-disk sha256 to `fileHashes`. If different, do NOT overwrite — write `<name>.regen` beside it and flag "preserved — manual edits detected; review needed" in the changelog.
4. Bump a changelog entry in the index (changed / preserved / added).

### `.regen` hygiene
`.regen` files are review siblings, not deliverables. `.forceignore` already excludes `**/*.regen` from deploy, but they should not accumulate silently inside `force-app/`:
- At the end of every synthesis run, **list any `.regen` files present** and surface them to the user ("N files have un-merged regenerations awaiting review: …").
- Once the human has merged (or rejected) a `.regen`, delete it. A stale `.regen` left in `force-app/` is clutter that misleads the next reader — treat a lingering `.regen` as an open review item, not a permanent artifact.
