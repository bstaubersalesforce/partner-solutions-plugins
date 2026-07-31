#!/usr/bin/env python3
"""
md-to-html.py — render a Markdown-native POV artifact into the styled document shell.

Purpose: Stage 13 must give every Markdown-native artifact (the POV, the Red Team
Assessment) an HTML view. Before this script existed, each run reinvented an ad-hoc
Markdown→HTML parser inline — slow and inconsistent. This is the one sanctioned converter.

It handles the Markdown subset the POV/Red Team templates actually emit: ATX headings,
GFM pipe tables, ordered/unordered lists, blockquotes, horizontal rules, paragraphs, and
inline bold / italic / code / links. It then injects the rendered body into
templates/document-shell.html and fills the shell's metadata tokens.

Usage:
    python3 md-to-html.py \
        --md       /path/to/{slug}-pov.md \
        --shell    /path/to/templates/document-shell.html \
        --out      /path/to/{slug}-pov.html \
        --partner  "CitNOW (Auto360)" \
        --label    "Point of View" \
        --stage    "03-Contract" \
        --date     "2026-05-30" \
        --home     "{slug}-index.html"      # omit for a standalone doc (drops the back-link)

Notes:
- --home sets the "← All artifacts" home-page back-link. OMIT it when the document is
  generated standalone (no home page); the script then removes the back-link anchor entirely,
  per Stage 13 and the home-page back-link rule.
- The first top-level "# Title" line in the Markdown is dropped — the shell header already
  renders the title from --label, so keeping it would double the heading.
- Exits non-zero if any {{TOKEN}} remains unfilled in the output (zero-unfilled-tokens bar).
"""
import argparse
import html
import re
import sys


def _inline(text):
    """Inline Markdown → HTML. Escapes first, then applies bold/italic/code/links."""
    text = html.escape(text)
    # `code` first so ** inside code isn't treated as bold
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    # links: [text](href) — href was escaped, & became &amp; which is fine in HTML attrs
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    return text


def md_to_html(md):
    lines = md.split("\n")
    out, i, n = [], 0, len(md.split("\n"))
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        # GFM pipe table: header row followed by a |---|---| separator
        if '|' in ln and i + 1 < len(lines) and re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]+\|?\s*$', lines[i + 1]):
            header = [c.strip() for c in ln.strip().strip('|').split('|')]
            i += 2
            rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            t = ['<table><thead><tr>'] + [f'<th>{_inline(h)}</th>' for h in header] + ['</tr></thead><tbody>']
            for r in rows:
                t.append('<tr>' + ''.join(f'<td>{_inline(c)}</td>' for c in r) + '</tr>')
            t.append('</tbody></table>')
            out.append(''.join(t))
            continue
        # ATX heading
        m = re.match(r'^(#{1,4})\s+(.*)$', ln)
        if m:
            lv = len(m.group(1))
            out.append(f'<h{lv}>{_inline(m.group(2))}</h{lv}>')
            i += 1
            continue
        # blockquote
        if re.match(r'^\s*>\s?', ln):
            buf = []
            while i < len(lines) and re.match(r'^\s*>\s?', lines[i]):
                buf.append(_inline(re.sub(r'^\s*>\s?', '', lines[i])))
                i += 1
            out.append('<blockquote>' + '<br>'.join(buf) + '</blockquote>')
            continue
        # unordered list
        if re.match(r'^\s*[-*]\s+', ln):
            buf = []
            while i < len(lines) and re.match(r'^\s*[-*]\s+', lines[i]):
                buf.append('<li>' + _inline(re.sub(r'^\s*[-*]\s+', '', lines[i])) + '</li>')
                i += 1
            out.append('<ul>' + ''.join(buf) + '</ul>')
            continue
        # ordered list
        if re.match(r'^\s*\d+\.\s+', ln):
            buf = []
            while i < len(lines) and re.match(r'^\s*\d+\.\s+', lines[i]):
                buf.append('<li>' + _inline(re.sub(r'^\s*\d+\.\s+', '', lines[i])) + '</li>')
                i += 1
            out.append('<ol>' + ''.join(buf) + '</ol>')
            continue
        # horizontal rule
        if re.match(r'^\s*---+\s*$', ln):
            out.append('<hr>')
            i += 1
            continue
        # paragraph — accumulate consecutive plain lines
        buf = []
        while (i < len(lines) and lines[i].strip()
               and not re.match(r'^(#{1,4}\s|\s*[-*]\s|\s*\d+\.\s|\s*>|\s*---+\s*$)', lines[i])
               and '|' not in lines[i]):
            buf.append(_inline(lines[i]))
            i += 1
        if buf:
            out.append('<p>' + '<br>'.join(buf) + '</p>')
        else:
            i += 1
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(description="Render a Markdown POV artifact into the document shell.")
    ap.add_argument('--md', required=True)
    ap.add_argument('--shell', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--partner', required=True)
    ap.add_argument('--label', required=True, help='DOC_LABEL, e.g. "Point of View"')
    ap.add_argument('--stage', required=True, help='OPPORTUNITY_STAGE, e.g. "03-Contract"')
    ap.add_argument('--date', required=True)
    ap.add_argument('--home', default=None, help='home-page href; omit for standalone (drops back-link)')
    args = ap.parse_args()

    with open(args.md) as f:
        md = f.read()
    # drop the leading H1 — the shell header already renders the title
    md = re.sub(r'^#\s+.*\n', '', md, count=1)

    with open(args.shell) as f:
        shell = f.read()

    content = md_to_html(md)
    filled = (shell
              .replace("{{PARTNER_NAME}}", html.escape(args.partner))
              .replace("{{DOC_LABEL}}", html.escape(args.label))
              .replace("{{OPPORTUNITY_STAGE}}", html.escape(args.stage))
              .replace("{{GENERATED_DATE}}", html.escape(args.date))
              .replace("{{CONTENT}}", content))

    if args.home:
        filled = filled.replace("{{HOME_HREF}}", html.escape(args.home))
    else:
        # standalone: remove the entire home-link anchor line, then any stray token
        filled = re.sub(r'^\s*<a class="home-link".*?</a>\s*\n', '', filled, flags=re.MULTILINE)
        filled = filled.replace("{{HOME_HREF}}", "")

    leftover = re.findall(r'\{\{[A-Z0-9_]+\}\}', filled)
    if leftover:
        sys.stderr.write(f"ERROR: unfilled tokens remain: {sorted(set(leftover))}\n")
        sys.exit(1)

    with open(args.out, 'w') as f:
        f.write(filled)
    print(args.out)


if __name__ == '__main__':
    main()
