# Stage 13 — Output Home Page / Solution Package

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 13 — Output Home Page / Solution Package (optional)**
Triggered when the user selects "All outputs + home page," generates 2+ outputs in one session, or asks for a home page, landing page, index, or "package" of the artifacts. Runs **last**, after the artifacts it links already exist.

**Goal:** every artifact is viewable as HTML, and the home page links them all — HTML for live viewing and Markdown for download where a Markdown source exists.

**Filename convention (all in one output directory, links are relative):**
Derive `SLUG` = the partner name lowercased and hyphenated (e.g. "Alvee Health" → `alvee-health`). Name every artifact:
- `SLUG-pov.md` + `SLUG-pov.html`
- `SLUG-discovery-document.md` + `SLUG-discovery-document.html`
- `SLUG-mvp-build-plan.md` + `SLUG-mvp-build-plan.html`
- `SLUG-red-team.md` + `SLUG-red-team.html` (artifact slug is `red-team`; the template/`--label` are "Red Team Assessment")
- `SLUG-investor-presentation.html`
- `SLUG-solution-infographic.html`
- `SLUG-readiness-scorecard.md` + `SLUG-readiness-scorecard.html`
- `SLUG-marketecture.html`
- `SLUG-technical-architecture-assessment.md` + `SLUG-technical-architecture-assessment.html`
- `SLUG-pov-presentation.html`
- `SLUG-consumption-opportunities.md` + `SLUG-consumption-opportunities.html`
- `SLUG-competitive-assessment.md` + `SLUG-competitive-assessment.html`
- `SLUG-index.html` (the home page)

**Give every artifact an HTML view.** HTML-native outputs (Investor, Infographic, Marketecture) and the dual-format outputs (MVP Build Plan, Scorecard) already produce HTML. For Markdown-native outputs (POV, Red Team), render an HTML view with the bundled converter — **do not hand-roll a Markdown→HTML parser inline** (that was reinvented every run and varied in quality). **Always re-render these from the current `.md` — never reuse an existing `.html`.** On a regeneration run, a wave subagent may refresh only the Markdown-native `.md` (HTML is Stage 13's job), leaving a stale `.html` from a prior run on disk; re-rendering every time guarantees the HTML view matches the current Markdown. Use `scripts/md-to-html.py`, which renders the Markdown subset these artifacts use (headings, GFM pipe tables, lists, bold/italic/code, links, blockquotes, rules) into `templates/document-shell.html`, fills the metadata tokens, drops the duplicate leading H1, and exits non-zero if any `{{TOKEN}}` is left unfilled:

```bash
python3 scripts/md-to-html.py \
  --md {SLUG}-pov.md \
  --shell templates/document-shell.html \
  --out {SLUG}-pov.html \
  --partner "{Partner Name}" \
  --label "Point of View" \
  --stage "{Org62 Opportunity Stage}" \
  --date "{YYYY-MM-DD}" \
  --home "{SLUG}-index.html"
```

Run it once per Markdown-native artifact (POV → `--label "Point of View"`, Red Team → `--label "Red Team Assessment"`). **Omit `--home`** when a document is generated standalone with no home page — the script then strips the `home-link` anchor entirely. Always keep the `.md` file too — it is the download. (If the script is genuinely unavailable in the runtime, fall back to filling `templates/document-shell.html` by hand via the HTML Output Method — but the script is the default.)

**Build the home page** from `templates/output-index.html` via the HTML Output Method (`refs/html-output-method.md`):
1. Fill `{{PARTNER_NAME}}`, `{{PACKAGE_DATE}}`, `{{OPPORTUNITY_STAGE}}`, `{{ARTIFACT_COUNT}}`.
2. Rebuild `{{ARTIFACT_CARDS}}` with one card per artifact actually generated (follow the card template in the index file's trailing comment). Always include the **View ↗** button (`SLUG-*.html`); include the **Markdown ↓** button only when a `.md` source exists (POV, MVP Build Plan, Red Team, Scorecard, Technical & Architectural Assessment, Consumption Opportunities, Competitive Assessment).
3. Order cards: POV (Core) first, then Presentation, Discovery, Build, Risk, Sales, Visual, Readiness, Architecture, Consumption, Competitive — listing only what exists. (POV Presentation = HTML-native, View ↗ only, no Markdown button.)
   (Consumption = the Consumption Opportunities artifact; View ↗ + Markdown ↓.)
   (Competitive = the Competitive Assessment artifact; View ↗ + Markdown ↓.)
   (Discovery = the auto-capture discovery document; View ↗ + Markdown ↓. Do **not** list `*-discovery-document.archived-*` files — archives are point-in-time copies (`{SLUG}-discovery-document.archived-YYYY-MM-DD.md`, suffixed `-2`, `-3`, … for same-day repeats), not live package artifacts.)
4. Scan the filled index for unfilled `{{...}}` tokens and confirm every `href` points to a file that was actually generated. Zero broken links is the bar.

**Guarantee the home-link pill on every artifact (required final step).** Once the home page exists, run:

```bash
python3 scripts/ensure-home-link.py --dir {output-dir} --slug {SLUG}
```

Every HTML artifact carries a `← All artifacts` pill that should link back to `{SLUG}-index.html`. Whether produced inline or by a fanned-out subagent, artifacts frequently misjudge themselves as "standalone" and strip the pill (about half of them in production), so the link is enforced mechanically here rather than left to the generator. The script is idempotent: it injects the pill where missing, repairs a wrong or leftover `{{HOME_HREF}}` href, and leaves correct ones untouched. It exits non-zero only on a real error (an HTML file with no `<body>`). Run it on every package — inline or dispatched.

Deliver the home page path (`SLUG-index.html`) as the primary entry point, and list the artifact files beneath it.
