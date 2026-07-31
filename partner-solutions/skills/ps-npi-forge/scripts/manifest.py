#!/usr/bin/env python3
"""
Effort manifest model for ps-npi-forge. Stdlib-only.

The manifest is the per-effort state: status, confidence, placeholders, and sources for each
artifact in ARTIFACT_REGISTRY. This module is the single place that reads/writes it. The YAML handled here is the
*known, flat* manifest shape only (not general YAML) — kept dependency-free on purpose.
"""
import re

STATUS_VOCAB = ["pending", "in_progress", "drafted", "verified", "pulled"]
ARTIFACT_REGISTRY = [
    "00-executive-summary", "01-brief", "02-slide-summary", "03-internal-enablement",
    "04-internal-faq", "05-external-faq", "06-license-entitlements", "07-addon-tiering",
    "08-setup-guide", "09-org-provisioning-validation", "10-partner-profile-pov",
    "11-solution-infographic", "12-marketecture", "13-demand-plan", "14-exec-infographic",
]
LOOP_REGISTRY = ["claim_verification", "completeness", "uncertainty", "partner_lens"]
VERDICT_VOCAB = ["pass", "flag", "fail"]

# Derivation graph: derived-artifact-slug -> source-of-record slug.
# Derived artifacts are GENERATED FROM their source (grounded transform, not re-research).
# 00 is a special derivation: rollup(01-brief) PLUS manifest state (blockers/confidence).
# 07 is PARTIALLY derived: its Required tier is grounded in 06; Recommended/Optional stay 07-authored.
DERIVES_FROM = {
    "00-executive-summary":    "01-brief",
    "02-slide-summary":        "01-brief",
    "11-solution-infographic": "01-brief",
    "14-exec-infographic":     "01-brief",
    "05-external-faq":         "04-internal-faq",
    "07-addon-tiering":        "06-license-entitlements",
}

def new_effort(release, product_slug, parent_sku):
    return {
        "release": release,
        "product_slug": product_slug,
        "parent_sku": parent_sku,
        "slack_channel": "",
        "artifacts": {
            a: {"status": "pending", "confidence": 0.0, "rationale": "",
                "sources": [], "placeholders": [],
                "loops": {lp: {"verdict": "", "note": ""} for lp in LOOP_REGISTRY},
                "last_generated": ""}
            for a in ARTIFACT_REGISTRY
        },
    }

def set_status(manifest, artifact, status):
    if artifact not in manifest["artifacts"]:
        raise ValueError(f"unknown artifact: {artifact}")
    if status not in STATUS_VOCAB:
        raise ValueError(f"unknown status: {status} (allowed: {STATUS_VOCAB})")
    manifest["artifacts"][artifact]["status"] = status
    return manifest

def set_loop_verdict(manifest, artifact, loop, verdict, note=""):
    if artifact not in manifest["artifacts"]:
        raise ValueError(f"unknown artifact: {artifact}")
    if loop not in LOOP_REGISTRY:
        raise ValueError(f"unknown loop: {loop} (allowed: {LOOP_REGISTRY})")
    if verdict not in VERDICT_VOCAB:
        raise ValueError(f"unknown verdict: {verdict} (allowed: {VERDICT_VOCAB})")
    manifest["artifacts"][artifact].setdefault("loops", {})[loop] = {"verdict": verdict, "note": note}
    return manifest

def set_last_generated(manifest, artifact, pointer):
    if artifact not in manifest["artifacts"]:
        raise ValueError(f"unknown artifact: {artifact}")
    manifest["artifacts"][artifact]["last_generated"] = pointer
    return manifest

def overall_confidence(manifest):
    vals = [rec["confidence"] for rec in manifest["artifacts"].values()
            if rec["status"] != "pulled"]
    return min(vals) if vals else 0.0

def generation_order():
    """Artifact slugs ordered so every source precedes its derivatives.
    Stable: within a readiness wave, ARTIFACT_REGISTRY order is preserved.
    Raises ValueError on a cycle or a source that never becomes available."""
    order, emitted, remaining = [], set(), list(ARTIFACT_REGISTRY)
    progress = True
    while remaining and progress:
        progress = False
        for a in list(remaining):
            src = DERIVES_FROM.get(a)
            if src is None or src in emitted:
                order.append(a); emitted.add(a); remaining.remove(a); progress = True
    if remaining:
        raise ValueError(f"derivation cycle or missing source among: {remaining}")
    return order

# ---- minimal YAML for the known flat manifest shape ---------------------
def dumps(manifest):
    lines = []
    for key in ("release", "product_slug", "parent_sku", "slack_channel"):
        lines.append(f"{key}: {_scalar(manifest.get(key, ''))}")
    lines.append("artifacts:")
    for a in ARTIFACT_REGISTRY:
        rec = manifest["artifacts"][a]
        lines.append(f"  {a}:")
        lines.append(f"    status: {rec['status']}")
        lines.append(f"    confidence: {rec['confidence']}")
        lines.append(f"    rationale: {_scalar(rec.get('rationale',''))}")
        lines.append(f"    sources: {_inline_list(rec.get('sources', []))}")
        lines.append("    placeholders:")
        for ph in rec.get("placeholders", []):
            lines.append(f"      - item: {_scalar(ph.get('item',''))}")
            lines.append(f"        owner: {_scalar(ph.get('owner',''))}")
            lines.append(f"        next_step: {_scalar(ph.get('next_step',''))}")
        lines.append("    loops:")
        loops = rec.get("loops") or {}
        for lp in LOOP_REGISTRY:
            v = loops.get(lp) or {"verdict": "", "note": ""}
            lines.append(f"      {lp}:")
            lines.append(f"        verdict: {_scalar(v.get('verdict',''))}")
            lines.append(f"        note: {_scalar(v.get('note',''))}")
        lines.append(f"    last_generated: {_scalar(rec.get('last_generated',''))}")
    return "\n".join(lines) + "\n"

def _scalar(v):
    s = str(v)
    if s == "" or re.search(r'[:#]', s) or s != s.strip():
        return '"' + s.replace('"', '\\"') + '"'
    return s

def _inline_list(items):
    if not items:
        return "[]"
    return "[" + ", ".join(_scalar(i) for i in items) + "]"

def load(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    manifest = {"artifacts": {}}
    cur_art = None
    cur_section = None   # None | "placeholders" | "loops"
    cur_ph = None
    cur_loop = None
    for raw in lines:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0:
            if line == "artifacts:":
                cur_art = None; cur_section = None; continue
            k, _, v = line.partition(":")
            manifest[k.strip()] = _parse_scalar(v.strip())
        elif indent == 2 and line.endswith(":"):
            cur_art = line[:-1].strip()
            manifest["artifacts"][cur_art] = {
                "sources": [], "placeholders": [], "loops": {}, "last_generated": ""}
            cur_section = None; cur_ph = None; cur_loop = None
        elif indent == 4 and cur_art:
            k, _, v = line.partition(":")
            k = k.strip()
            if k == "placeholders":
                cur_section = "placeholders"; cur_ph = None; continue
            if k == "loops":
                cur_section = "loops"; cur_loop = None; continue
            cur_section = None
            if k == "sources":
                manifest["artifacts"][cur_art]["sources"] = _parse_inline_list(v.strip())
            elif k == "confidence":
                manifest["artifacts"][cur_art]["confidence"] = float(v.strip())
            else:
                manifest["artifacts"][cur_art][k] = _parse_scalar(v.strip())
        elif indent == 6 and cur_section == "placeholders" and line.startswith("- item:"):
            cur_ph = {"item": _parse_scalar(line.split(":", 1)[1].strip())}
            manifest["artifacts"][cur_art]["placeholders"].append(cur_ph)
        elif indent == 6 and cur_section == "loops" and line.endswith(":"):
            cur_loop = line[:-1].strip()
            manifest["artifacts"][cur_art]["loops"][cur_loop] = {"verdict": "", "note": ""}
        elif indent == 8 and cur_section == "placeholders" and cur_ph is not None:
            k, _, v = line.partition(":")
            cur_ph[k.strip()] = _parse_scalar(v.strip())
        elif indent == 8 and cur_section == "loops" and cur_loop is not None:
            k, _, v = line.partition(":")
            manifest["artifacts"][cur_art]["loops"][cur_loop][k.strip()] = _parse_scalar(v.strip())
    return manifest

def _parse_scalar(v):
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        return v[1:-1].replace('\\"', '"')
    return v

def _parse_inline_list(v):
    v = v.strip()
    if v in ("", "[]"):
        return []
    inner = v[1:-1] if v[0] == "[" and v[-1] == "]" else v
    return [_parse_scalar(x.strip()) for x in inner.split(",") if x.strip()]
