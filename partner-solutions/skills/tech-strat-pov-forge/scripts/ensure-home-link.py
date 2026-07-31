#!/usr/bin/env python3
"""ensure-home-link.py — guarantee the "← All artifacts" home-link pill on every
package artifact, mechanically. Run by Stage 13 (output home page) over the output
directory once the home page exists.

Why this exists: fanned-out subagents (parallel-dispatch) decide for themselves
whether they are "standalone" and strip the back-link when no home page is on disk
yet. In a package run a home page IS coming, so that judgment is wrong — and it was
wrong for ~half the artifacts in production. The pill is a fixed snippet, so we
enforce it with a script instead of trusting each subagent to get the call right.

Behavior, per HTML artifact in the directory (the index itself is skipped):
- If a home-link anchor is present (detected by the "All artifacts</a>" marker),
  rewrite its href to {slug}-index.html — repairs a leftover {{HOME_HREF}} token or
  a wrong/relative target.
- If it is absent, inject the standard pill immediately after the opening <body> tag.

Idempotent: running twice changes nothing the second time. Exits non-zero only on a
real error (e.g. an HTML file with no <body> to inject into).

Two layouts, one script — `--slug` is optional:
- WITH `--slug` (tech-strat-pov-forge layout): artifacts are `{slug}-*.html` in a shared
  output dir; globs `{slug}-*.html`, default index `{slug}-index.html`.
- WITHOUT `--slug` (pie-poc-forge flat layout): a dedicated docs/ dir with a single
  `index.html` and `NN-name.html` artifacts; globs `*.html`, default index `index.html`.

Usage:
  python3 scripts/ensure-home-link.py --dir <output-dir> --slug <slug>
  python3 scripts/ensure-home-link.py --dir <output-dir> --slug <slug> --index <slug>-index.html
  python3 scripts/ensure-home-link.py --dir <docs-dir>                       # flat layout, index.html
  python3 scripts/ensure-home-link.py --dir <docs-dir> --index <name>.html   # flat layout, custom index
"""
import argparse
import re
import sys
from pathlib import Path

MARKER = "All artifacts</a>"  # present in every template's pill, both ← and &#8592; forms

# Canonical pill markup (matches templates/document-shell.html). {HOME} is filled per-run.
PILL = (
    '<a href="{home}" style="position:fixed;top:14px;left:14px;z-index:9999;'
    "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;"
    "font-size:12px;font-weight:700;letter-spacing:0.04em;text-decoration:none;"
    "color:#fff;background:#0070d2;padding:7px 14px;border-radius:100px;"
    'box-shadow:0 2px 8px rgba(0,0,0,0.25);">&#8592; All artifacts</a>'
)

BODY_RE = re.compile(r"(<body[^>]*>)", re.IGNORECASE)
# An <a ...>...All artifacts</a> anchor, capturing the href value for repair.
ANCHOR_RE = re.compile(
    r'<a\s+[^>]*href="(?P<href>[^"]*)"[^>]*>\s*(?:&#8592;|&larr;|←)?\s*All artifacts</a>',
    re.IGNORECASE,
)


def process(path: Path, home: str) -> str:
    """Return a one-word status: 'repaired', 'injected', 'ok', or 'error:<reason>'."""
    html = path.read_text(encoding="utf-8")

    if MARKER in html:
        # Pill present — ensure its href points at the index.
        m = ANCHOR_RE.search(html)
        if not m:
            # Marker present but anchor shape unexpected; leave it alone, report ok.
            return "ok"
        if m.group("href") == home:
            return "ok"
        fixed = ANCHOR_RE.sub(
            lambda mm: mm.group(0).replace('href="%s"' % mm.group("href"), 'href="%s"' % home, 1),
            html,
            count=1,
        )
        path.write_text(fixed, encoding="utf-8")
        return "repaired"

    # Pill absent — inject after the opening <body> tag.
    if not BODY_RE.search(html):
        return "error:no <body> tag"
    injected = BODY_RE.sub(lambda mm: mm.group(1) + "\n" + PILL.format(home=home), html, count=1)
    path.write_text(injected, encoding="utf-8")
    return "injected"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="package/canvas output directory")
    ap.add_argument("--slug", help="partner slug, e.g. tekion (omit for the flat NN-name.html layout)")
    ap.add_argument("--index", help="index filename (default: {slug}-index.html with --slug, else index.html)")
    args = ap.parse_args()

    out = Path(args.dir)
    # With --slug: {slug}-*.html artifacts + {slug}-index.html default.
    # Without --slug: every *.html + index.html default (flat docs/ layout).
    if args.slug:
        index_name = args.index or f"{args.slug}-index.html"
        pattern = f"{args.slug}-*.html"
    else:
        index_name = args.index or "index.html"
        pattern = "*.html"
    home = index_name

    if not out.is_dir():
        print(f"error: {out} is not a directory", file=sys.stderr)
        return 1

    errors = 0
    for html in sorted(out.glob(pattern)):
        if html.name == index_name:
            continue
        status = process(html, home)
        print(f"{status:>10}  {html.name}")
        if status.startswith("error:"):
            errors += 1

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
