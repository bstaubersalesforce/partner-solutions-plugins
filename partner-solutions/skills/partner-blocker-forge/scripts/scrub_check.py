#!/usr/bin/env python3
"""scrub_check — mechanical pre-share leak detector for partner-blocker-forge.

Scans a draft doc for likely cross-customer / internal-only leaks before it is shared or
committed. This is the enforcement behind refs/scrub.md (which is otherwise a manual
checklist). Deterministic + stdlib-only so it is unit-testable (golden-file).

Usage:
    python3 scripts/scrub_check.py <draft.md> [--partner "Acme Corp"]
Exit code 0 = clean, 1 = findings. Findings print as: LINE:PATTERN:excerpt.

--partner is optional context (informational only — the scanner does not need it to flag
foreign identifiers; it flags ID/URL/PII shapes regardless).
"""
import re, sys

# (label, compiled pattern). Ordered; each line is scanned against all.
PATTERNS = [
    ("sfid-org",      re.compile(r"\b00D[A-Za-z0-9]{12,15}\b")),      # 18/15-char Org IDs
    ("sfid-case",     re.compile(r"\b500[A-Za-z0-9]{12,15}\b")),      # Case record IDs
    ("internal-gus",  re.compile(r"\bgus\.lightning\.force\.com\b", re.I)),
    ("internal-splunk", re.compile(r"splunk[-.][\w.-]*", re.I)),
    ("internal-host", re.compile(r"[\w.-]*\.internal\.salesforce\.com\b", re.I)),
    ("internal-slack-archive", re.compile(r"salesforce(?:-internal|\.enterprise)\.slack\.com/archives/\S+", re.I)),
    ("phone",         re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)")),
    ("gus-workitem",  re.compile(r"\bW-\d{6,}\b")),
]

def scan_text(text):
    """Return list of (line_no, label, excerpt) findings. Pure — for testing."""
    findings = []
    for i, line in enumerate(text.splitlines(), 1):
        for label, rx in PATTERNS:
            for m in rx.finditer(line):
                s = max(0, m.start() - 15); e = min(len(line), m.end() + 15)
                findings.append((i, label, line[s:e].strip()))
    return findings

def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: scrub_check.py <draft.md> [--partner NAME]", file=sys.stderr); return 2
    path = args[0]
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"cannot read {path}: {e}", file=sys.stderr); return 2
    findings = scan_text(text)
    if not findings:
        print(f"scrub_check: CLEAN — no leak patterns in {path}"); return 0
    print(f"scrub_check: {len(findings)} potential leak(s) in {path} — review before sharing:")
    for ln, label, excerpt in findings:
        print(f"  {ln}:{label}: …{excerpt}…")
    print("Confirm each is this partner's own data or remove it (see refs/scrub.md).")
    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
