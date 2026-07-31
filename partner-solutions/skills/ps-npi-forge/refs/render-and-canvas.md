# Render and canvas

The render recipe for an effort: how to turn artifact Markdown into the shareable SLDS HTML set and
assemble the Key Resources hub. Lazily loaded -- a stage (or a fanned-out Phase 7 Deep Build
subagent) loads **this** file rather than reproducing the method from SKILL.md, so the instruction is
available even when SKILL.md is not in context. The three scripts are the sanctioned path:
`scripts/md_to_html.py` (Markdown -> document HTML), `scripts/slide_deck.py` (Markdown -> SLDS slide
deck), and `scripts/canvas.py` (hub assembly). Do not hand-roll any of them.

## 1. The format rule (which artifacts get HTML)

Not every artifact renders to HTML. The split:

- **Narrative / shareable artifacts render to MD + HTML:** `00-executive-summary`, `01-brief`,
  `02-slide-summary`, `03-internal-enablement`, `05-external-faq`, `10-partner-profile-pov`,
  `11-solution-infographic`, `12-marketecture`, `13-demand-plan`, `14-exec-infographic`.
- **Reference artifacts stay MD-only:** `04-internal-faq`, `08-setup-guide`,
  `09-org-provisioning-validation` -- UNLESS one carries a diagram (none of these three do today).
- **Diagram-carrying reference artifacts DO render to HTML:** `06-license-entitlements` and
  `07-addon-tiering` carry Mermaid diagrams (composition / tier), so they render to HTML to show the
  live diagram.
- **`02-slide-summary` ALSO renders a slide deck** (`<slug>-slides.html` via `scripts/slide_deck.py`,
  section 2b) in addition to its document HTML -- it is the deck artifact.

So the typical HTML set is `00,01,02,03,05,06,07,10,11,12,13,14` (+ the `02-slide-summary-slides.html`
deck); `04,08,09` stay MD-only. The canvas decides
each card's link from the **actual presence of a `<slug>.html` file** -- never from a hardcoded list.
A doc that has not been rendered gets a no-link gap card (see section 4), so the format rule and the
canvas stay self-consistent: render the right set, and the canvas reflects it.

## 1b. The merged poster view (#14)

`14-exec-infographic` renders a single visual **poster** view — `14-exec-infographic-poster.html` — via
`scripts/poster.py`, in addition to its document HTML. It is a **merged, multi-source** poster: it draws
its 7 panels from BOTH the exec (#14) and solution (#11) markdown — Vision (#14) · The Problem (#11) ·
The Solution (#11) · Outcomes (#11) · Market·TAM (#14) · Ideal Partners (#14) · Built on Salesforce (#11).
`poster.SECTION_MAP["14-exec-infographic"]` maps each `{{PANEL_*}}` slot to a `(source_slug, H2)` pair;
`render_poster(slug, sources, template, meta)` takes `sources={slug: md_text}` for every artifact the
poster needs (use `SOURCES_FOR(slug)` to know which). Each source's markdown stays the source of truth;
the poster is a derived projection. The canvas links the poster as the **primary** title on the #14 card
with the document as a secondary "(document)" link. **#11 has a document view only** (its poster was
consolidated into this merged one). The section→panel contract keys on the exact H2 headings of *each*
source — if an H2 is reworded in #11 or #14, update `SECTION_MAP` (guarded by R-POSTER-02/03).

## 1c. Rich single-source views (#11, #12)

`11-solution-infographic` and `12-marketecture` render their PRIMARY `<slug>.html` from a bespoke
light-scheme layout, NOT the generic document shell. `poster.RICH_VIEWS[slug]` maps each
`{{PANEL_*}}` slot to a `(source_slug, H2)` pair in the artifact's own markdown;
`poster.render_view(slug, sources, template_text, meta)` projects the markdown sections into the
template (`templates/solution-infographic.html` / `templates/marketecture.html`). The markdown stays
the source of truth; the rich HTML is a derived projection (same pattern as the #14 merged poster).
The section→panel contract keys on the exact H2 headings — if an H2 is reworded in #11/#12, update
`RICH_VIEWS` (guarded by R-RICH-01). #11 is a light 3-column problem/solution/outcomes infographic;
#12 is a light layered Partner→Agent→Platform→Data→Trust stack. Neither gets a `-poster.html` (the
`-poster.html` suffix remains #14-only).

## 2. md_to_html.py invocation

Exact CLI for one artifact:

```
python3 scripts/md_to_html.py --md <artifact.md> --shell templates/document-shell.html \
    --out <slug>.html --title "<product>" --label "<artifact label>" \
    --release "<release>" --date "<date>" --home "index.html"
```

Omit `--home` for a standalone doc (no canvas home page): the script then strips the "All artifacts"
back-link line and fills `{{HOME_HREF}}` empty, so no dead link or unfilled token remains.

What it does:

- Fills the shell's 6 metadata tokens: `{{TITLE}}`, `{{LABEL}}`, `{{RELEASE}}`,
  `{{GENERATED_DATE}}`, `{{BODY}}`, `{{HOME_HREF}}`.
- Drops the artifact's leading `# H1` (the shell header renders the title instead).
- Converts the artifact-template Markdown subset: ATX headings, GFM pipe tables, ordered/unordered
  lists, blockquotes, horizontal rules, fenced code, paragraphs, inline bold/italic/code/links. A
  ` ```mermaid ` fence is emitted VERBATIM as `<pre class="mermaid">` (so the shell's CDN renders it
  live); any other ` ```lang ` fence is HTML-escaped `<pre><code>`.

**Exit behavior.** The script exits non-zero ONLY on a genuine unknown token -- a leftover
`{{SOMETHING}}` the generator should have filled. It exits 0 for the INTENTIONAL_PLACEHOLDERS, which
render as visible "pending" markers instead of blocking:

- the 6 named diagram slots `{{STATUS_ROLLUP_DIAGRAM}}`, `{{COMPOSITION_DIAGRAM}}`,
  `{{TIER_DIAGRAM}}`, `{{PARTNER_FIT_DIAGRAM}}`, `{{INFOGRAPHIC_DIAGRAM}}`, `{{MARKETECTURE_DIAGRAM}}`
  -> `Diagram pending -- populated on the next generate cycle.`
- `{{PRICE_PENDING}}` -> `$xx (pending)`; `{{DISCOUNT_PENDING}}` -> `xx% (pending)` (pricing is out of
  scope; scan.py keys on these markers and rolls them into the #00 register).

This is what makes render safe to run at any time: a not-yet-filled diagram or pending price renders
a marker, never a hard failure.

## 2b. slide_deck.py invocation (the slide render format)

`02-slide-summary` (and any artifact you want as a deck) also renders as an SLDS **slide deck** -- a
second render surface alongside the document HTML. It produces a full-bleed presentation: a cover
slide (title + the gap-banner status line) then **one content slide per `## H2` section**, themed to
the SLDS navy/blue system, print-to-PDF friendly (`page-break-after`), with Mermaid fences rendered
live via the same CDN. Exact CLI:

```
python3 scripts/slide_deck.py --md <artifact.md> --out <slug>-slides.html \
    --title "<product>" --label "<artifact label>" --release "<release>" --date "<date>" \
    --home "index.html"
```

It drops the leading `# H1` (the cover renders the title), excludes the footer/`**Sources:**` block
(document chrome, not a slide), keeps mermaid fences verbatim, and renders an intentional pending
diagram token as a visible "Diagram pending" note. Pure core: `to_slides(md)` and `build_deck(...)`.
Convention: write the deck as `<slug>-slides.html` so it sits beside the document `<slug>.html`.

## 3. Regenerate diagrams BEFORE the final render (ordering)

The named diagram slots are filled by the **generate -> refine -> validate** cycle (the generator
writes a themed Mermaid fence reflecting the effort's real data), NOT by render. Render is safe either
way -- an unfilled slot renders the pending marker (section 2). But for a **final canvas** you want
the real diagrams to appear, so the ordering is:

1. Regenerate the diagram-carrying artifacts through the cycle so their slots are filled:
   `#00` (status rollup), `#06` (composition), `#07` (tier), `#10` (partner fit),
   `#11` (infographic), `#12` (marketecture).
2. Then render the HTML set.
3. Then assemble the canvas.

If you render before the cycle has filled a slot, that artifact's HTML shows the pending marker and
the canvas is still valid -- just not final. (This staging is the open part of BACKLOG B9.)

## 4. canvas.py assembly

`build_index(manifest, html_present) -> str` -- pure, stdlib-only. Build `html_present` as a
`slug -> bool` map from which `<slug>.html` files actually exist on disk (not a hardcoded list, so a
deleted/never-rendered file is reflected truthfully). Then write the returned string to
`canvas/index.html`.

**Regenerate cleanup:** When regenerating an effort, artifacts that were previously HTML-rendered
but are now MD-only (per the format rule above) can leave stale `.html` files in `canvas/`. Because
the canvas keys each card's link on the actual presence of a `<slug>.html` file, stale files cause
the canvas to link outdated HTML. The render flow should, after rendering, compute the intended HTML
set via `render.wants_html(artifact_md, template_md)` for each artifact, then remove any
`render.orphan_html(canvas_dir, keep_slugs)` before assembling the canvas — so a regenerated effort
never links stale HTML from a prior build.

Layout (calibrated to the sibling pov-builder / pie-poc-forge chrome):

- **Cards render FIRST** (above the task list), one per artifact, each:
  kind pill -> titled link -> one-line summary -> status + confidence meta. The per-slug kind,
  label, and summary come from `_KIND` / `_LABEL` / `_SUMMARY` in canvas.py.
- A **rendered doc links** to its `<slug>.html` even if it is not yet verified -- but it is TAGGED
  pending/draft (`-- <status>, not yet final`) so a linked non-final doc reads honestly.
- An **un-rendered doc is a no-link gap card** ("-- not yet rendered", dashed border) -- never a dead
  link.
- The **Next Steps & Blockers register renders BELOW the cards** -- a table aggregating every
  manifest placeholder (artifact / gap / owner / next step), including the pricing-pending gaps. All
  values are HTML-escaped (injection-safe).
- The header shows the effort title + release and the overall confidence (the weighted floor across
  non-pulled artifacts).

Local `canvas/index.html` is the **source of truth**; the Slack canvas (Phase 6) is a projection of
it.

## 5. Mermaid

Diagrams are themed ` ```mermaid ` fences (SLDS palette directive in `refs/mermaid-diagrams.md`).
They render **live** via the `mermaid@11` ESM CDN that `templates/document-shell.html` embeds
(`startOnLoad: true`) -- no build step needed in a browser. SVG/PNG export for decks
(`scripts/mermaid_export.py`, `mmdc -i x.mmd -o x.svg`) is **capability-gated** on `mmdc`: if `mmdc`
is absent it reports the install line (`npm i -g @mermaid-js/mermaid-cli`) and SKIPS -- never raises,
never blocks the artifact. See `refs/mermaid-diagrams.md` for the theme directive and the named
diagram types.
