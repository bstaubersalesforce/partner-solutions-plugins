# HTML Output Method

The shared method every HTML-producing stage uses to fill a template. Lazily loaded — a stage
(or a fanned-out subagent generating that stage) loads **this** file rather than reproducing the
method from `SKILL.md`, so the instruction is available even when `SKILL.md` is not in context.

**Never regenerate a template's HTML token-by-token in your own output** — the templates are
15–50KB and reproducing them inline is slow and error-prone. Instead:

1. Build a placeholder → value map from the POV data (one entry per `{{TOKEN}}`).
2. Apply it to the template file with a short script: plain string replacement for scalar tokens;
   regex with `re.DOTALL`, anchored on each block's unique placeholder tokens, for variable-length
   tables and lists (rebuild the `<tbody>`/`<ul>` when the row count differs from the template).
3. Write the filled file to the output path.
4. Scan the output for any remaining `{{[A-Z0-9_]+}}` tokens; fix before delivering. Zero unfilled
   tokens is the bar.
5. Delete the fill script after — it is scaffolding, not a deliverable.

This is the validated approach: faster, cheaper, and it guarantees the template's styling survives
intact.

**Markdown-native artifacts use the bundled converter, not an inline parser.** The token-replacement
method above is for templates with `{{TOKEN}}` slots. The POV and Red Team Assessment are Markdown
documents that need their *body* converted to HTML and injected into `templates/document-shell.html`.
Do not hand-write a Markdown→HTML parser for this — use `scripts/md-to-html.py` (it handles headings,
GFM pipe tables, lists, inline formatting, blockquotes, and rules; fills the shell's metadata tokens;
and enforces zero unfilled tokens). Stage 13 documents the exact invocation.

**Caution — placeholder tokens must appear exactly once per file.** Plain string-replace fills *every*
occurrence of a token, including any inside CSS/HTML comments. If a template mentions its own
`{{TOKEN}}` in a comment, the value gets injected twice. Templates here are kept clean of this; if you
add a token reference to a comment, reword it so the literal token appears only at its real fill point.

**Home-page back-link — every HTML artifact carries one (`{{HOME_HREF}}`).** All HTML templates in
`templates/` (the slide decks, the infographic, the marketecture, the MVP/scorecard/assessment pages,
and the `document-shell`) include a back-link anchor reading "← All artifacts". Handle its `{{HOME_HREF}}`
token uniformly in every HTML stage:
- **Part of a package** (a home page is being built — Stage 13 runs): fill `{{HOME_HREF}}` with
  `{SLUG}-index.html`.
- **Standalone artifact** (no home page — a single output the user asked for on its own): remove the
  entire back-link `<a>…All artifacts</a>` line (it is on its own line, flagged by a comment), so no
  dead link and no unfilled token remain.
Either way, the zero-unfilled-token scan at the end must pass — a leftover `{{HOME_HREF}}` is a defect.
