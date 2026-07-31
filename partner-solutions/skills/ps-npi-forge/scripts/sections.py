#!/usr/bin/env python3
"""
Section addressing + edit-preservation diff for ps-npi-forge. Stdlib-only, side-effect-free.

One section = one '## H2' block of an artifact (the Phase-3a templates make this exact). The H1 +
gap-banner before the first '## ' and the footer (the '---' immediately preceding '**Sources:**' onward) are
tool-owned and excluded from section addressing. `locked_sections` is the heart of per-section
edit-preservation: any H2 body that diverged from its last-generated baseline is human-locked and
must be carried over verbatim on regeneration.
"""
import re

H2_RE = re.compile(r"^## (.+?)\s*$")

def _footer_start(lines):
    """Index of the '---' line that begins the artifact footer (the one immediately preceding a
    '**Sources:**' line), or len(lines) if there is no such footer. Only this '---' is the footer
    delimiter; standalone '---' rules inside a body section are NOT footers.

    Anchors on the LAST ---/**Sources:** pair, not the first, so a human typing a lookalike
    --- / **Sources:** line INSIDE a body section (with a real H2 section after it) does not
    truncate the split and drop later sections."""
    candidate = None
    for i, line in enumerate(lines):
        if line.strip() == "---":
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].lstrip().startswith("**Sources:**"):
                candidate = i
    return candidate if candidate is not None else len(lines)

def split(md):
    lines = md.splitlines()
    end = _footer_start(lines)
    sections = {}
    cur = None
    buf = []
    for line in lines[:end]:
        m = H2_RE.match(line)
        if m:
            if cur is not None:
                sections[cur] = "\n".join(buf)
            cur = m.group(1).strip()
            buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        sections[cur] = "\n".join(buf)
    return sections

def locked_sections(live_md, baseline_md):
    live = split(live_md)
    base = split(baseline_md)
    locked = set()
    for heading, body in live.items():
        if heading not in base or body.strip() != base[heading].strip():
            locked.add(heading)
    return locked
