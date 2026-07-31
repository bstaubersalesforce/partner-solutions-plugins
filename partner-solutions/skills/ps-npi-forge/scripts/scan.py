#!/usr/bin/env python3
"""
Uncertainty / gap scanner for ps-npi-forge. Stdlib-only, side-effect-free.

Implements the mechanical half of the uncertainty-surfacing loop: find every place a rendered
artifact admits an unknown so the agent can attach an owner + next step and the manifest can carry
it. Never silently drops an uncertainty -- the scanner's whole job is to make gaps loud.
"""
import re

_PATTERNS = [
    (re.compile(r"Template ID[^\n]*(?:\n[^\n]*)?\b(?:PENDING|TBD|missing|not provided)\b", re.I), "missing Template ID"),
    # labeled price-pending marker emitted by md_to_html ($xx (pending) / xx% (pending)) -- runs
    # BEFORE the generic patterns so the clearer pricing label wins for these markers.
    (re.compile(r"(?:\$[xX]{2,}|[xX]{2,}%)\s*\(pending\)", re.I), "pricing pending (out of scope -- owned elsewhere)"),
    (re.compile(r"\bPENDING\b", re.I), "PENDING marker"),
    (re.compile(r"\bTBD\b", re.I), "TBD marker"),
    (re.compile(r"\$[xX]{2,}\b"), "price stub"),
    (re.compile(r"\{\{[A-Z0-9_]+\}\}"), "unfilled token"),
]

def scan(md):
    gaps = []
    seen = set()
    claimed = []  # list of (start, end) spans already claimed by more specific patterns
    for rx, label in _PATTERNS:
        for m in rx.finditer(md):
            s, e = m.span()
            # skip if this match overlaps any already-claimed span
            if any(s < ce and cs < e for cs, ce in claimed):
                continue
            key = (label, m.group(0))
            if key in seen:
                continue
            seen.add(key)
            claimed.append((s, e))
            gaps.append({"item": f"{label}: {m.group(0).strip()}"})
    return gaps
