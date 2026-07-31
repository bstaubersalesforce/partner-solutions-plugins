# PS-NPI-FORGE Phase 5 — Canvas assembly + HTML render + Mermaid

**Date:** 2026-06-23
**Author:** Brandon Stauber (with Claude Code)
**Status:** Approved for planning
**Builds on:** Phases 1-4 (manifest model, the 11 artifact templates, the generate->refine->validate cycle, live Org62 composition). Implements design-spec.md §6 (outputs, canvas assembly). Models on the sibling `pie-poc-forge` (`scripts/md-to-html.py`, `templates/document-shell.html`, `refs/mermaid-diagrams.md`), as §6/§7 direct, and on `style-conventions.md` (SLDS palette + the Mermaid output pipeline).

---

## 1. Scope & boundary

Phase 5 delivers design-spec §6: turn the per-effort artifact markdown into shareable **HTML** and
assemble the **Key Resources canvas** (`canvas/index.html`), with **Mermaid** diagrams themed to SLDS.

**In scope:**
- A stdlib **Markdown->HTML converter** (`scripts/md_to_html.py`) injecting artifact bodies into an
  SLDS **document shell** (`templates/document-shell.html`).
- The **Mermaid pipeline**: themed ```mermaid fences in artifact markdown -> live render via the
  Mermaid CDN in the HTML shell + native render in Markdown; **`mmdc` SVG/PNG export is
  capability-gated** (absent on this machine -> keep source, report the install, never block).
- A **canvas assembler** (`scripts/canvas.py`) building `canvas/index.html` from the effort manifest:
  effort title/release, overall confidence + status rollup, the Next Steps & Blockers register, and a
  linked card per artifact with a status + confidence badge. A `pending` artifact renders as a
  labeled gap card, **not a dead link**.
- `refs/mermaid-diagrams.md` carrying the canonical SLDS `%%{init}%%` theme directive + the named
  diagram types (self-contained copy per the style-conventions rule).

**Explicitly out of scope:**
- **B3** (SF price-list / Heroku pricelist-tool fetchability for #07) -- stays a separate BACKLOG
  spike; it is an intake-source question, not a rendering one.
- Slack sync / publish gate (Phase 6); Deep Build C-mode (Phase 7).
- Pricing determination (out of scope entirely); Org62 writes (read-only always).

## 2. Components (mechanical -> Python, CI-tested; judgment -> refs)

| Component | Responsibility | Notes |
|-----------|----------------|-------|
| `scripts/md_to_html.py` | Render an artifact's Markdown into the SLDS document shell. Handles the subset the templates emit: ATX headings, GFM pipe tables, ordered/unordered lists, blockquotes, horizontal rules, fenced code blocks, paragraphs, inline bold/italic/code/links. Fills the shell's metadata tokens. Exits non-zero on any surviving `{{TOKEN}}`. | Ported + adapted from `pie-poc-forge/scripts/md-to-html.py`. A ```mermaid fence -> `<pre class="mermaid">` with source kept **verbatim** (not HTML-escaped) so the shell's CDN renders it live; any other ```lang fence -> escaped `<pre><code>`. |
| `scripts/canvas.py` | Assemble `canvas/index.html` from `manifest.yaml`: effort title/release, overall confidence (`manifest.overall_confidence`), status rollup, the aggregated **Next Steps & Blockers register** (from per-artifact placeholders), then a linked card per `ARTIFACT_REGISTRY` slug with a status + confidence badge. Applies the §6 **format rule** (below). | Reads `scripts/manifest.py`. A `pending` artifact -> a labeled gap card (no dead link). Stdlib-only; pure (takes manifest + an artifact-file presence map, returns HTML). |
| `scripts/mermaid_export.py` | Capability-gated SVG/PNG export: detect `mmdc`; if present, export each `.mmd`/fence to SVG; if absent, **report the install line and skip** (never block). | `mmdc` is absent here -> the report-and-skip path is the tested one. |
| `templates/document-shell.html` | SLDS-themed HTML shell: palette + `'Salesforce Sans', ...` stack + `print-color-adjust: exact` on dark fills; embeds the Mermaid ESM CDN (`mermaid@11`, `mermaid.initialize({ startOnLoad: true })`); carries `{{TITLE}}`, `{{LABEL}}`, `{{RELEASE}}`, `{{DATE}}`, `{{BODY}}`, `{{HOME_LINK}}`. | One sanctioned shell; the converter is the only thing that fills it. |
| `refs/mermaid-diagrams.md` | The canonical `%%{init}%%` SLDS directive (verbatim from style-conventions) + the named diagram types and when to use them. Lazy-loaded. | Self-contained copy; parity-checked against the directive. |

### 2.1 The §6 format rule (enforced, not hardcoded)

Narrative/shareable artifacts (00, 01, 02, 03, 05, 10) get **MD + HTML**. Internal reference
artifacts (04, 08, 09) stay **MD-only unless they carry a diagram**. `canvas.py` decides per artifact
from the format rule + actual file presence (does an `.html` exist for this slug?), not a frozen list,
so an #08 that gains a diagram (and thus an HTML view) links correctly without a code change.

## 3. Mermaid pipeline (matches style-conventions.md exactly)

Diagrams are authored as themed ```mermaid fences in the artifact markdown, each prepended with the
canonical SLDS directive:

```
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f0f5fc","primaryTextColor":"#032d60","primaryBorderColor":"#0176d3","lineColor":"#444444","secondaryColor":"#f8fafc","tertiaryColor":"#ffffff","fontFamily":"Salesforce Sans, Helvetica Neue, Arial, sans-serif"}} }%%
```

Three render surfaces:
1. **Live HTML** -- `document-shell.html` embeds the `mermaid@11` ESM CDN with `startOnLoad: true`;
   `md_to_html.py` emits the fence as `<pre class="mermaid">` (verbatim source) so it renders live.
2. **Markdown** -- the same fence renders natively on GitHub/GitLab.
3. **SVG/PNG for decks** -- `@mermaid-js/mermaid-cli` (`mmdc -i x.mmd -o x.svg`). **Capability-gated:**
   `mmdc` is absent on this machine, so Phase 5 keeps the fence/`.mmd` source and reports the install
   (`npm i -g @mermaid-js/mermaid-cli`); the artifact is never blocked.

**The named diagrams (spec §6) are authored by the generator, not baked as static template strings.**
Their content depends on the effort's actual data (e.g. #00's status/blocker rollup reflects the live
manifest), so each relevant template carries a `{{...}}` slot the generator fills with a themed fence,
guided by `refs/mermaid-diagrams.md` and the `quality-loops.md` cycle: #00 status/blocker rollup, #06
entitlement-composition, #07 tier-decision view, #10 partner-fit logic.

## 4. Data flow

Effort `manifest.yaml` (state) drives rendering:

1. For each artifact whose format rule yields HTML: `md_to_html.py(artifacts/<slug>.md, document-shell.html)
   -> <slug>.html`, home-linked back to the canvas index.
2. `canvas.py(manifest, artifact-file presence) -> canvas/index.html`: reads per-artifact
   status/confidence/placeholders, emits the rollup + the aggregated blocker register + one card per
   artifact (HTML link or labeled gap card).
3. Mermaid fences inside any artifact render live in its HTML view (and in the canvas where embedded).

**Local HTML/canvas is the source of truth; the Slack projection is Phase 6.** Re-running regenerates
idempotently from the current manifest + artifact state. Effort output lives outside the repo under
`ps-npi-efforts/<release>/<product-slug>/` (`artifacts/`, `canvas/`); nothing there is committed.

## 5. Validation additions & acceptance

**New checks** (extend `tests/validate_skill.py`, stdlib + golden fixtures under `tests/fixtures/`):
- **`md_to_html` subset** -- headings/tables/lists/blockquotes/inline render correctly against a
  fixture; a ```mermaid fence becomes a verbatim `<pre class="mermaid">` (NOT escaped); a non-mermaid
  fence is escaped; the zero-unfilled-`{{TOKEN}}` bar holds (exits non-zero on a leftover token).
- **`document-shell.html`** -- carries the Mermaid CDN (`mermaid@11` + `startOnLoad`), the SLDS theme
  (`Salesforce Sans` + the brand palette), and the required tokens (`{{BODY}}`, `{{TITLE}}`, ...).
- **`canvas.py`** -- emits one card per `ARTIFACT_REGISTRY` slug with a status + confidence badge;
  a `pending` artifact renders as a labeled gap card (no dead link); the Next Steps & Blockers
  register aggregates the manifest placeholders; overall confidence shown = `manifest.overall_confidence`.
- **`mmdc` gating** -- with `mmdc` absent, the export path reports-and-skips gracefully (asserted),
  never raises.
- **`refs/mermaid-diagrams.md`** -- carries the canonical `%%{init}%%` directive (substring parity
  with the style-conventions theme: border `#0176d3`, line `#444444`, `Salesforce Sans`); added to
  `EXPECTED_REFS`; referenced by SKILL.md.

**Acceptance (manual, controller-driven):** render the `summer-26 / agentforce-healthcare-oem` effort
artifacts to HTML and assemble `canvas/index.html`. Verify: the canvas shows a card per artifact with
the real status/confidence badges (e.g. #09 as a flagged card at the 0.35 floor; verified artifacts
green); the blocker register lists the Template-ID + entitlement + pricing gaps with owners; a
```mermaid fence (e.g. #00's status rollup) renders live in the HTML; `mmdc` absent -> SVG export
reports-and-skips. Record in `docs/superpowers/acceptance/`.

## 6. Out of scope (explicit, this phase)

- **B3** SF price-list / Heroku pricelist-tool fetchability (separate BACKLOG spike).
- Slack sync + publish gate (Phase 6); Deep Build C-mode (Phase 7).
- Pricing determination (placeholders only); Org62 writes (read-only).
- A live `mmdc` install (capability-gated; report-and-skip when absent).

## 7. Anticipated task decomposition (~6 tasks)

1. `templates/document-shell.html` (SLDS shell + Mermaid CDN + metadata tokens) + a shell-content check.
2. `scripts/md_to_html.py` (port + adapt the sibling converter) + render checks (subset, mermaid fence
   verbatim, non-mermaid escaped, zero-unfilled-token bar).
3. `refs/mermaid-diagrams.md` (SLDS directive + diagram types) + directive-parity check; add the
   themed-fence `{{...}}` slot + generator guidance to the named templates (#00/#06/#07/#10).
4. `scripts/canvas.py` (index.html from manifest: rollup, blocker register, per-artifact cards with
   badges, pending -> labeled gap card, §6 format rule) + canvas checks.
5. `scripts/mermaid_export.py` capability-gated SVG export (detect `mmdc` / report-and-skip) + gating
   check; SKILL.md canvas/outputs section; wire `refs/mermaid-diagrams.md` into SKILL.md + EXPECTED_REFS.
6. Acceptance: render the Healthcare effort -> HTML + `canvas/index.html`; verify badges/blocker
   register/live diagram/mmdc-skip; record.

(Exact task count/ordering finalized in the plan; ~6 tasks.)
