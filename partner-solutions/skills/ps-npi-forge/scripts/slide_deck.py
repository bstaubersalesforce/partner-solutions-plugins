#!/usr/bin/env python3
"""
slide_deck.py — render a ps-npi-forge artifact's Markdown as an SLDS-themed slide deck. Stdlib-only.

A second render surface alongside md_to_html.py (the document view): this turns an artifact into a
full-bleed presentation — a **cover slide** (title + the gap-banner status line) followed by **one
content slide per `## H2` section** (heading + that section's body, inline-rendered). Modeled on
pov-builder's pov-presentation.html slide system (1280x720 slides, SLDS navy/blue, print-to-PDF via
page-break-after), but generic + manifest-driven rather than per-slide hand-authored.

Mermaid fences inside a section render live via the CDN (each `<pre class="mermaid">` is kept
verbatim, same contract as md_to_html.py); intentional pending diagram markers render as a visible
note. The footer/Sources block is dropped from slides (it's document chrome, not a slide).

Pure core: `to_slides(md) -> list[(heading, body_html)]` and `build_deck(md, title, label, release,
date, home) -> str`. CLI mirrors md_to_html.py.
"""
import argparse, html, re, sys

# reuse the inline + fence rendering contract from the document converter, kept local to stay stdlib-only
_TOKEN_PENDING_DIAGRAM = re.compile(r"\{\{([A-Z0-9_]+_DIAGRAM)\}\}")

def _inline(text):
    text = html.escape(text)
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for part in parts:
        if len(part) >= 2 and part.startswith('`') and part.endswith('`'):
            out.append('<code>' + part[1:-1] + '</code>')
        else:
            part = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', part)
            part = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', part)
            part = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', part)
            out.append(part)
    return ''.join(out)

def _render_body(lines):
    """Render a section body (list of md lines) to slide HTML: paragraphs, lists, mermaid fences,
    pending diagram markers. Compact — slides favour brevity over full doc fidelity."""
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        mfence = re.match(r'^\s*```\s*([A-Za-z0-9_-]*)\s*$', ln)
        if mfence:
            lang = mfence.group(1).lower(); i += 1; buf = []
            while i < len(lines) and not re.match(r'^\s*```\s*$', lines[i]):
                buf.append(lines[i]); i += 1
            i += 1
            code = "\n".join(buf)
            if lang == "mermaid":
                out.append('<pre class="mermaid">' + code + '</pre>')
            else:
                out.append('<pre class="code">' + html.escape(code) + '</pre>')
            continue
        # a lone intentional diagram token on its own line -> visible pending note
        if _TOKEN_PENDING_DIAGRAM.fullmatch(ln.strip()):
            out.append('<p class="pending-note"><em>Diagram pending — populated on the next generate cycle.</em></p>')
            i += 1; continue
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
        # blockquote / status line -> muted note
        if re.match(r'^\s*>\s?', ln):
            buf = []
            while i < len(lines) and re.match(r'^\s*>\s?', lines[i]):
                buf.append(_inline(re.sub(r'^\s*>\s?', '', lines[i]))); i += 1
            out.append('<p class="note">' + '<br>'.join(buf) + '</p>'); continue
        buf = []
        while (i < len(lines) and lines[i].strip()
               and not re.match(r'^(#{1,4}\s|\s*[-*]\s|\s*\d+\.\s|\s*>|\s*```|\s*---+\s*$)', lines[i])):
            buf.append(_inline(lines[i])); i += 1
        if buf:
            out.append('<p>' + '<br>'.join(buf) + '</p>')
        else:
            i += 1
    return '\n'.join(out)

def to_slides(md):
    """Split an artifact's markdown into (heading, body_html) content slides, one per ## H2 section.
    Stops at the footer '---'/**Sources:** block (document chrome, not a slide)."""
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)  # strip HTML comments (e.g. the VOICE marker)
    lines = md.split("\n")
    # find the footer boundary (the '---' immediately preceding '**Sources:**'), mirror sections.py
    end = len(lines)
    for idx, line in enumerate(lines):
        if line.strip() == "---":
            j = idx + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].lstrip().startswith("**Sources:**"):
                end = idx; break
    slides, cur, buf = [], None, []
    for line in lines[:end]:
        m = re.match(r'^##\s+(.+?)\s*$', line)
        if m:
            if cur is not None:
                slides.append((cur, _render_body(buf)))
            cur = m.group(1).strip(); buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        slides.append((cur, _render_body(buf)))
    return slides

def build_deck(md, title, label, release, date, home=None):
    slides = to_slides(md)
    total = len(slides) + 1  # +1 cover
    # cover: pull the gap-banner status line if present (the '> **Status:** ...' blockquote)
    status_line = ""
    sm = re.search(r'^>\s*(\*\*Status:\*\*.+)$', md, re.M)
    if sm:
        status_line = _inline(re.sub(r'^\*\*Status:\*\*', 'Status:', sm.group(1)))
    home_pill = (f'<a class="home-link" href="{html.escape(home)}">&#8592; Key Resources</a>'
                 if home else "")
    cover = (f'<section class="slide slide-cover">{home_pill}'
             f'<div class="eyebrow">{html.escape(label)} · {html.escape(release)}</div>'
             f'<h1 class="hero">{html.escape(title)}</h1>'
             + (f'<p class="note" style="opacity:.8;margin-top:20px">{status_line}</p>' if status_line else "")
             + f'<div class="slide-foot-rule"></div><span class="slide-num">1 / {total}</span></section>')
    body = [cover]
    for n, (heading, html_body) in enumerate(slides, start=2):
        body.append(
            f'<section class="slide slide-content">'
            f'<h2 class="title">{_inline(heading)}</h2>'
            f'<div class="slide-body">{html_body}</div>'
            f'<div class="slide-foot-rule"></div><span class="slide-num">{n} / {total}</span></section>')
    slides_html = "\n".join(body)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — {html.escape(label)} (slides)</title>
<style>
 :root {{ --navy:#032d60; --blue:#0176d3; --teal:#0b827c; --light:#f7f9fc; }}
 * {{ box-sizing:border-box; margin:0; padding:0; }}
 body {{ font-family:"Salesforce Sans","Helvetica Neue",Arial,sans-serif; background:#e8ecf0; color:#181818; }}
 .deck {{ display:flex; flex-direction:column; align-items:center; gap:24px; padding:32px 0 64px; }}
 .slide {{ width:1280px; min-height:720px; position:relative; overflow:hidden; box-shadow:0 8px 40px rgba(0,0,0,.18);
           display:flex; flex-direction:column; background:#fff; padding:64px 80px; }}
 .slide-cover {{ background:linear-gradient(135deg,var(--navy) 0%,#001a3e 60%,#003366 100%); color:#fff; justify-content:center; padding:80px 100px; }}
 .slide-content {{ background:var(--light); }}
 .eyebrow {{ font-size:13px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; opacity:.65; margin-bottom:14px; }}
 h1.hero {{ font-size:60px; font-weight:800; line-height:1.05; }}
 h2.title {{ font-size:40px; font-weight:800; line-height:1.1; color:var(--navy); border-bottom:3px solid var(--blue); padding-bottom:14px; margin-bottom:24px; }}
 .slide-body {{ font-size:20px; line-height:1.55; flex:1; }}
 .slide-body p {{ margin:0 0 14px; }}
 .slide-body ul, .slide-body ol {{ margin:0 0 14px 26px; }}
 .slide-body li {{ margin:0 0 8px; }}
 .slide-body a {{ color:var(--blue); }}
 .slide-body code {{ background:#eef2f7; padding:1px 6px; border-radius:4px; font-size:.92em; }}
 .slide-body pre.code {{ background:#0f1117; color:#e6edf3; border-radius:8px; padding:16px; font-size:14px; overflow-x:auto; }}
 .slide-body pre.mermaid {{ background:#fff; text-align:center; }}
 .mermaid svg{{max-width:100%;height:auto;}}
 .note {{ opacity:.75; }}
 .pending-note {{ color:#e65100; }}
 .slide-foot-rule {{ position:absolute; bottom:0; left:0; right:0; height:5px; background:linear-gradient(90deg,var(--blue),var(--teal)); }}
 .slide-num {{ position:absolute; bottom:16px; right:24px; font-size:11px; font-weight:600; letter-spacing:.08em; opacity:.45; text-transform:uppercase; }}
 .slide-cover .slide-num {{ color:#fff; }}
 .home-link {{ position:absolute; top:18px; left:24px; font-size:12px; font-weight:700; letter-spacing:.04em; text-decoration:none; color:#fff; background:var(--blue); padding:7px 14px; border-radius:100px; }}
 @media print {{ body {{ background:#fff; }} .deck {{ gap:0; padding:0; }} .slide {{ page-break-after:always; box-shadow:none; }} .slide-foot-rule,.slide-cover {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }} }}
 @media (max-width:1320px) {{ .slide {{ width:100%; }} }}
</style></head>
<body><div class="deck">
{slides_html}
</div>
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({{ startOnLoad: true, securityLevel: "loose", flowchart: {{ useMaxWidth: true, htmlLabels: true, wrappingWidth: 220 }} }});
</script>
</body></html>"""

def main():
    ap = argparse.ArgumentParser(description="Render a ps-npi-forge artifact as an SLDS slide deck.")
    ap.add_argument('--md', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--title', required=True); ap.add_argument('--label', required=True)
    ap.add_argument('--release', required=True); ap.add_argument('--date', required=True)
    ap.add_argument('--home', default=None)
    args = ap.parse_args()
    with open(args.md) as f:
        md = f.read()
    md = re.sub(r'^#\s+.*\n', '', md, count=1)  # drop leading H1; the cover renders the title
    deck = build_deck(md, args.title, args.label, args.release, args.date, args.home)
    with open(args.out, 'w') as f:
        f.write(deck)
    print(args.out)

if __name__ == '__main__':
    main()
