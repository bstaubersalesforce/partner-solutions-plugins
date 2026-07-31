# pie-poc-forge — Backlog

Ideas and improvements not yet actioned, kept here so they stay visible. Each
item records where it came from, why it matters, and what "done" looks like.
This is a working list, not a commitment — items graduate to a spec → plan →
implementation cycle (see `docs/superpowers/`) when picked up.

## How to add an item

Use this shape so each entry is actionable:

```
- **<short-id> — <title>.** Origin: <where it came from>. Why: <why it matters>.
  Done when: <observable definition of done>.
```

---

## Open

- **B9 — Proactively generate the canvas-minted MCP action shape (+ behavioral test).** Origin:
  the 2026-06-11 nCino Phase-D run. The *documentation* half is shipped (see B9-doc in Done): the
  refs now describe the correct `mcpTool://mcptoolx5fx5f<tool>` target, the remove/re-add-in-org
  binding that mints the hashed/`source:`/`outputs:`-free action shape, the runtime perm-set
  assignment, and the MCP Workbench diagnostic. What remains (deeper, optional): the skill still
  *authors* the un-publishable `mcpTool://<ESR-name>` placeholder and relies on a manual in-org
  remove/re-add + source re-sync. Done when: either (a) the scaffold/handoff emits the minted action
  shape directly when the tool identities are obtainable pre-publish (so no manual rebind is needed),
  or (b) a check/heuristic flags any agent action whose target is `mcpTool://<ESR-name>` (server
  name) as not-publishable before Phase D, so the binding step is never skipped silently.

- **B3 — Generate the index card grid from the registry.** Origin: the card-rename and
  numbering changes. Updated 2026-06-11: the skill-forge remediation rewrote `R-TEST-03`
  to enforce bidirectional *slug* parity (the index links no unknown artifact, and every
  `ALWAYS` artifact is linked) — so the href-level drift is now caught. What remains: card
  **titles, descriptions, order, and phase grouping** are still hand-maintained HTML in
  `templates/output-index.html` and can drift from the `ALWAYS`/`CONDITIONAL` registry and
  the artifact titles with nothing to catch it. Why: every artifact add/remove/rename
  still requires hand-editing the card grid. Done when: the card grid is generated from the
  registry (label, description, phase group, order) so the index can't drift from the
  artifact set, and a check enforces card↔registry parity beyond the href slug (label +
  order + description).

- **B4 — Branded deck output (optional).** Origin: flagged when artifacts 11/12 were
  added. Why: the Kickoff/Engagement-Review decks are currently slide-by-slide *content
  outlines* a PIE pastes into the official PDF/Slides template. A generator that emits a
  branded `.pptx` or branded HTML matching the deck visuals would remove the manual
  transfer step. Large scope (templating + brand assets). Done when: the skill can emit a
  branded deck artifact (not just an outline) for 11 and 12 from the same source content.

- **B5 — Mechanical enforcement of the validation gate (optional).** Origin: wiring
  `isv-validate-agentforce` as synthesis step 3. Why: the gate is an instruction, not a
  check — a run could skip it and nothing would catch that. Done when: a run that
  produced an agent/MCP/invocable-Apex package records evidence the validation gate ran
  (e.g. a stored scorecard), and its absence is surfaced.

- **B7 — Mermaid diagrams in more artifacts.** Origin: the 2026-06-11 Mermaid add
  (`09-agentscript` routing diagram shipped first as the highest-leverage area). Spec/plan:
  `docs/superpowers/{specs,plans}/2026-06-11-mermaid-diagrams*`. Why: the same single-source
  theme (`refs/mermaid-diagrams.md`) + `mmdc` export extends to an **execution-plan Gantt**
  (`01`), a **component-manifest dependency graph** (`08`), and a **security trust-boundary /
  data-flow diagram** (`06`). Done when: chosen artifacts build their `.mmd` from the shared
  theme and reuse the export path. (The live-HTML-render half of the original B7 is now
  closed — see B8 in Done.)

---

## Done

- **B9-doc — Document the real MCP action binding + runtime perm-set + ordering (from the nCino run).**
  Closed 2026-06-11. Translated the full Phase-D run into ref edits:
  - `refs/mcp-integration.md` validator-7.10 **corrected** — the working target is
    `mcpTool://mcptoolx5fx5f<tool>` (encoded `mcptool__<tool>`), NOT a `1XO…` Record ID; documents the
    remove/re-add-in-org binding that mints the hashed action key + `source:` + `outputs:`-free body,
    the retrieve-and-sync step, the `preview --use-live-actions` diagnostic, and the **MCP Workbench**
    GitHub/install links. Added: ESR `<status>` must be stripped before deploy (was B11); runtime MCP
    perm-set must be assigned to the **Platform Integration User** (`--on-behalf-of`, the agent's
    callouts run as it — W-21685162).
  - `refs/agentscript-handoff.md` — replaced the inaccurate "target is `mcpTool://<ESR>`" guidance
    with the publish-fails-without-binding gotcha + the correct sequence.
  - `refs/finalize.md` — **reordered Gate 2** so MCP config + tool binding precede `sf agent publish`
    (publishing first 500s); added 4 new known-failure-taxonomy rows (pre-root-comment conversion
    error, ESR `<status>`, opaque publish-500 → invalid MCP target, runtime perm-set/integration-user)
    and corrected the two rows that referenced the wrong canvas-Record-ID story.
  Verified on nCino: agent published v1 + active, live `get_client_financial_summary` returned real
  data. Remaining proactive-generation work tracked as B9 (Open). Validator 17/17.

- **B10 — SFDX scaffold pre-root XML comment broke source conversion.** Closed 2026-06-11.
  `refs/sfdx-scaffold.md` stub conventions now require the `<!-- Serves: … -->` comment as the first
  line **inside** the root element (with an example), so generated object/field `-meta.xml` convert
  and deploy cleanly. (Surfaced as nCino finalize-report M1; affected all 9 object/field files,
  fixed in-run by relocating the comments.)

- **B11 — MCP ESR shipped a non-deployable system-managed `<status>`.** Closed 2026-06-11.
  `refs/mcp-integration.md` now instructs stripping `<status>` from the ESR metadata before deploy
  (it is org-derived, not writable — fails `Unable to create/update fields: Status`). Noted the
  toolkit CLI v1.1.0+ should not emit it; strip if a captured/legacy ESR carries it. (nCino M2.)

- **B8 — Live Mermaid HTML render + fenced-code converter fix.** Closed 2026-06-11.
  Surfaced when the nCino PoC dogfood showed the `09-agentscript` routing diagram **mangled**
  in the HTML (literal backticks + the diagram body spilled into `<p>…<br>…</p>`). Root cause:
  `scripts/md-to-html.py` had **no fenced-code-block handling at all** — a ```` ```lang ````
  fence fell through to the paragraph branch (so *any* fenced code mangled, not just Mermaid).
  Fix: added a fenced-code branch — a ```` ```mermaid ```` fence emits `<pre class="mermaid">`
  with source **verbatim** (unescaped) and any other language emits an escaped
  `<pre><code>`; added the Mermaid ESM CDN (`mermaid@11`) to `document-shell.html` so the
  block renders live (brace-safe `initialize` call, token-hygiene preserved). Extended the
  golden fixture with a mermaid + an apex fence, regenerated `expected-body.html`, and added a
  behavioral check **R-SCRIPT-04** (mermaid verbatim, other langs escaped, no leaked fences /
  no `<br>` mangling) — **mutation-verified** (broke the mermaid branch → R-SCRIPT-04 failed →
  restored). Suite 16/16 → 17/17. Re-rendered the nCino `09-agentscript.html`: diagram now a
  clean live-rendering `<pre class="mermaid">`. This closes the live-render half of the
  original B7.

- **B1 — Org-connected "finalize" mode (Phase D).** Closed 2026-06-11. Added an opt-in,
  re-entrant Phase D that runs the org-dependent lifecycle against an authenticated org in two
  gates — Gate 1 validate (non-mutating: dry-run, agent validate, MCP env/reachability) runs by
  default; Gate 2 deploy (real deploy, perm-set assign, agent publish, MCP deploy-and-configure
  + validate-end-to-end) is offered only after Gate 1 is green. Production requires explicit
  typed confirmation (reworked the old absolute "never deploys to production" refusal). Writes a
  new CONDITIONAL `13-finalize-report` artifact with per-step results, returned IDs, and a
  detailed Mitigation block per failure (Symptom / Likely cause / Fix / Resume) from a
  known-failure taxonomy in `refs/finalize.md`. Stop-on-first-failure. Procedure in
  `refs/finalize.md`; wired into SKILL.md (Phase D section + reworded refusal); `finalize` run
  block documented in `refs/requirements-schema.md`. Suite 16/16; skill-forge audit clean (no
  tier gap, no new orphans).

- **B2 — Behavioral tests for the reused scripts.** Closed 2026-06-11. Ported pov-builder's
  shipped R1 into `tests/validate_skill.py` as three behavioral checks (R-SCRIPT-01/02/03):
  golden-file render of `md-to-html.py` (fixtures under `tests/fixtures/md-to-html/`, golden
  generated from the real script), HTML-escaping + leading-H1-drop, and
  inject/repair/idempotency/error-report for `ensure-home-link.py` (adapted to the flat
  `index.html` + `NN-*.html` layout). Verified the checks have teeth via three mutants
  (drop escaping, swap `<strong>`→`<b>`, skip inject) — each failed the matching check;
  suite restored to 16/16. Added `.gitignore` for `__pycache__`.

- **B6 — Delivery Voice (match pov-builder).** Closed 2026-06-11 (commit `a21310c`).
  Added a `## Delivery Voice` section to `SKILL.md` (senior-advisor briefing voice:
  lead-with-conclusion, no-hedging, quantify-or-qualify, "so what?"), scoped to
  human-facing prose only (deterministic artifacts stay literal) and explicitly
  subordinate to the source-or-pending / no-fabrication rules. Wired the voice into the
  prose refs: `mvp-opinion`, `security-review`, `gaps-document`, `engagement-decks`.
  Verified RED→GREEN: a baseline Security Assessment had no voice contract; the GREEN
  draft led with the verdict, kept finding rows factual, and fabricated nothing.

- **N2 — Hard dependency on external skill names.** Closed 2026-06-11 (commit `a21310c`).
  The skill now degrades gracefully when a companion (`agentforce-adlc`,
  `sf-mcp-partner-toolkit`, `isv-validate-agentforce`) is missing: never hand-authors the
  delegate's output, never dead-stops the run, marks the affected component pending in
  `01`/`07`/`08`, generates everything not blocked, and tells the user which delegate is
  missing + what was skipped + to install and re-run. Top-level contract in `SKILL.md`
  Delegation; per-delegate branches in `refs/agentscript-handoff.md` and
  `refs/mcp-integration.md` (validator branch already existed in `workflow-dispatch.md`).
  Verified RED→GREEN: baseline dead-stopped the whole run; GREEN continues with non-agent
  components and refuses to hand-author. (README N1 prerequisite note was the prior partial.)

---

## Withdrawn

_(none yet)_
