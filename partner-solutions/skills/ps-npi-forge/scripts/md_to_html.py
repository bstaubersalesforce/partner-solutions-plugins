#!/usr/bin/env python3
"""
md_to_html.py — render a ps-npi-forge artifact's Markdown into the SLDS document shell.

The one sanctioned Markdown->HTML converter (do not reinvent inline). Handles the subset the
artifact templates emit: ATX headings, GFM pipe tables, ordered/unordered lists, blockquotes,
horizontal rules, fenced code blocks, paragraphs, and inline bold/italic/code/links. Injects the
rendered body into templates/document-shell.html and fills its metadata tokens. Note: GFM table
cells cannot contain an escaped/literal pipe (\\|), and nested list indentation is flattened to a
single level.

A ```mermaid fence renders as <pre class="mermaid"> with its source kept VERBATIM (not HTML-escaped)
so the shell's Mermaid CDN renders it live; any other ```lang fence renders as an escaped
<pre><code> block. Ported from pie-poc-forge/scripts/md-to-html.py.

Usage:
    python3 md_to_html.py --md <artifact.md> --shell templates/document-shell.html \
        --out <artifact.html> --title "Agentforce for Healthcare" --label "Executive Summary" \
        --release "summer-26" --date "2026-06-23" --home "index.html"   # omit --home for standalone
Exits non-zero if any {{TOKEN}} remains unfilled.
"""
import argparse, html, re, sys

# Tokens that are intentionally left pending and must RENDER (visibly) rather than block the artifact:
#  - the named *_DIAGRAM slots are filled by a generator-cycle run, not by render
#  - pricing placeholders are out of scope (owned elsewhere) and render as a visible pending marker
INTENTIONAL_PLACEHOLDERS = {
    "STATUS_ROLLUP_DIAGRAM", "COMPOSITION_DIAGRAM", "TIER_DIAGRAM", "PARTNER_FIT_DIAGRAM",
    "INFOGRAPHIC_DIAGRAM", "MARKETECTURE_DIAGRAM", "DEMAND_DIAGRAM", "EXEC_DIAGRAM",
    "PRICE_PENDING", "DISCOUNT_PENDING",
}

def _is_external(href):
    # external links open in a new tab; internal relative links (index.html, <slug>.html) stay same-tab
    return href.startswith(("http://", "https://", "//"))

def _anchor(href, text):
    if _is_external(href):
        return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{text}</a>'
    return f'<a href="{href}">{text}</a>'

def _autolink_bare_urls(segment):
    # linkify bare http(s) URLs in a non-anchor segment; trim trailing sentence punctuation
    def repl(m):
        url = m.group(0)
        trail = ""
        while url and url[-1] in ".,;:!?)]":
            trail = url[-1] + trail
            url = url[:-1]
        return _anchor(url, url) + trail
    return re.sub(r"https?://[^\s<]+", repl, segment)

def _inline(text):
    text = html.escape(text)
    # split on inline-code spans so bold/italic/links never reach inside <code>
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for part in parts:
        if len(part) >= 2 and part.startswith('`') and part.endswith('`'):
            out.append('<code>' + part[1:-1] + '</code>')
        else:
            part = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', part)
            part = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', part)
            # markdown links -> anchors (external get new-tab); then autolink bare URLs in the
            # remaining text, splitting on the just-built anchors so a URL inside an href is never re-wrapped
            part = re.sub(r'\[(.+?)\]\((.+?)\)', lambda m: _anchor(m.group(2), m.group(1)), part)
            segs = re.split(r'(<a\b[^>]*>.*?</a>)', part)
            part = ''.join(s if s.startswith('<a ') else _autolink_bare_urls(s) for s in segs)
            out.append(part)
    return ''.join(out)

def md_to_html(md):
    # Strip HTML comments (e.g. the template's `<!-- VOICE: ... -->` authoring marker). They are
    # instructions to the generator, never rendered content -- without this they fall through to the
    # paragraph branch and get HTML-escaped into visible `&lt;!-- ... --&gt;` gibberish.
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        mfence = re.match(r'^\s*```\s*([A-Za-z0-9_-]*)\s*$', ln)
        if mfence:
            lang = mfence.group(1).lower(); i += 1; body = []
            while i < len(lines) and not re.match(r'^\s*```\s*$', lines[i]):
                body.append(lines[i]); i += 1
            i += 1
            code = "\n".join(body)
            if lang == "mermaid":
                out.append('<pre class="mermaid">' + code + '</pre>')
            else:
                out.append('<pre><code>' + html.escape(code) + '</code></pre>')
            continue
        if '|' in ln and i + 1 < len(lines) and re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]+\|?\s*$', lines[i + 1]):
            header = [c.strip() for c in ln.strip().strip('|').split('|')]; i += 2; rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            t = ['<table><thead><tr>'] + [f'<th>{_inline(h)}</th>' for h in header] + ['</tr></thead><tbody>']
            for r in rows:
                t.append('<tr>' + ''.join(f'<td>{_inline(c)}</td>' for c in r) + '</tr>')
            t.append('</tbody></table>'); out.append(''.join(t)); continue
        m = re.match(r'^(#{1,4})\s+(.*)$', ln)
        if m:
            lv = len(m.group(1)); out.append(f'<h{lv}>{_inline(m.group(2))}</h{lv}>'); i += 1; continue
        if re.match(r'^\s*>\s?', ln):
            buf = []
            while i < len(lines) and re.match(r'^\s*>\s?', lines[i]):
                buf.append(_inline(re.sub(r'^\s*>\s?', '', lines[i]))); i += 1
            out.append('<blockquote>' + '<br>'.join(buf) + '</blockquote>'); continue
        if re.match(r'^\s*[-*]\s+', ln):
            buf = []
            while i < len(lines) and re.match(r'^\s*[-*]\s+', lines[i]):
                buf.append('<li>' + _inline(re.sub(r'^\s*[-*]\s+', '', lines[i])) + '</li>'); i += 1
            out.append('<ul>' + ''.join(buf) + '</ul>'); continue
        if re.match(r'^\s*\d+\.\s+', ln):
            buf = []
            while i < len(lines) and re.match(r'^\s*\d+\.\s+', lines[i]):
                buf.append('<li>' + _inline(re.sub(r'^\s*\d+\.\s+', '', lines[i])) + '</li>'); i += 1
            out.append('<ol>' + ''.join(buf) + '</ol>'); continue
        if re.match(r'^\s*---+\s*$', ln):
            out.append('<hr>'); i += 1; continue
        buf = []
        while (i < len(lines) and lines[i].strip()
               and not re.match(r'^(#{1,4}\s|\s*[-*]\s|\s*\d+\.\s|\s*>|\s*---+\s*$)', lines[i])):
            buf.append(_inline(lines[i])); i += 1
        if buf:
            out.append('<p>' + '<br>'.join(buf) + '</p>')
        else:
            i += 1
    return '\n'.join(out)

def main():
    ap = argparse.ArgumentParser(description="Render a ps-npi-forge artifact into the SLDS shell.")
    ap.add_argument('--md', required=True); ap.add_argument('--shell', required=True)
    ap.add_argument('--out', required=True); ap.add_argument('--title', required=True)
    ap.add_argument('--label', required=True); ap.add_argument('--release', required=True)
    ap.add_argument('--date', required=True); ap.add_argument('--home', default=None)
    args = ap.parse_args()
    with open(args.md) as f: md = f.read()
    md = re.sub(r'^#\s+.*\n', '', md, count=1)  # drop leading H1; shell header renders the title
    with open(args.shell) as f: shell = f.read()
    body = md_to_html(md)
    filled = (shell.replace("{{TITLE}}", html.escape(args.title))
                   .replace("{{LABEL}}", html.escape(args.label))
                   .replace("{{RELEASE}}", html.escape(args.release))
                   .replace("{{GENERATED_DATE}}", html.escape(args.date))
                   .replace("{{BODY}}", body))
    if args.home:
        filled = filled.replace("{{HOME_HREF}}", html.escape(args.home))
    else:
        filled = re.sub(r'^\s*<a class="home-link".*?</a>\s*\n', '', filled, flags=re.MULTILINE)
        filled = filled.replace("{{HOME_HREF}}", "")
    # Intentional placeholders render as visible pending markers (no {{}}), never block the artifact.
    substituted = []
    for name in sorted(INTENTIONAL_PLACEHOLDERS):
        token = "{{" + name + "}}"
        if token in filled:
            if name.endswith("_DIAGRAM"):
                marker = '<p class="pending-note"><em>Diagram pending — populated on the next generate cycle.</em></p>'
            elif name == "PRICE_PENDING":
                # labeled, scannable price-pending marker (scan.py keys on "$xx (pending)")
                marker = "$xx (pending)"
            elif name == "DISCOUNT_PENDING":
                marker = "xx% (pending)"
            else:
                marker = "pending"
            filled = filled.replace(token, marker)
            substituted.append(name)
    if substituted:
        sys.stderr.write(f"NOTE: rendered {len(substituted)} intentional placeholder(s) as pending markers: {substituted}\n")
    leftover = re.findall(r'\{\{[A-Z0-9_]+\}\}', filled)
    if leftover:
        sys.stderr.write(f"ERROR: unfilled tokens remain (these are not known intentional placeholders — the generator likely missed a fill): {sorted(set(leftover))}\n"); sys.exit(1)
    with open(args.out, 'w') as f: f.write(filled)
    print(args.out)

if __name__ == '__main__':
    main()
