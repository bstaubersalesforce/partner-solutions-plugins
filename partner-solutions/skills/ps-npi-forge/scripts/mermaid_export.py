#!/usr/bin/env python3
"""
mermaid_export.py — capability-gated SVG/PNG export for Mermaid diagrams. Stdlib-only.

SVG/PNG export for decks uses @mermaid-js/mermaid-cli (`mmdc`). It is CAPABILITY-GATED: if `mmdc`
is not on PATH, export reports the install line and SKIPS -- it never raises and never blocks an
artifact (the live HTML CDN + the .mmd/fence source remain the primary paths). See
refs/mermaid-diagrams.md.
"""
import shutil, subprocess

_INSTALL = "mmdc not found -- install with: npm i -g @mermaid-js/mermaid-cli (SVG export skipped; live HTML render unaffected)"

def mmdc_available():
    return shutil.which("mmdc") is not None

def export_svg(mmd_path, out_path):
    if not mmdc_available():
        return {"ok": False, "skipped": True, "message": _INSTALL}
    try:
        subprocess.run(["mmdc", "-i", mmd_path, "-o", out_path], check=True,
                       capture_output=True, text=True)
        return {"ok": True, "skipped": False, "message": out_path}
    except Exception as exc:  # never raise — report and move on
        return {"ok": False, "skipped": False, "message": f"mmdc export failed: {exc}"}
