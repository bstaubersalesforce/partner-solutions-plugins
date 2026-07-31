#!/usr/bin/env python3
"""
Poster renderer for ps-npi-forge. Stdlib-only.

Projects an artifact's markdown (the source of truth) into a styled SLDS-light "poster" HTML
template by mapping each H2 section's body into the matching {{PANEL_*}} slot. Reuses the sanctioned
splitter (sections.split) and block converter (md_to_html.md_to_html); does NOT re-implement markdown.
"""
import html as _html, os, re, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from sections import split            # split(md) -> {H2-title: section-text}
from md_to_html import md_to_html     # block converter (paragraphs, lists, inline)

TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

# the section->panel contract. Each panel names its SOURCE artifact slug and the exact H2 heading
# in that source. The merged exec poster draws from BOTH #14 and #11. Keep this the single source of truth.
SECTION_MAP = {
    "14-exec-infographic": {
        "PANEL_VISION":         ("14-exec-infographic", "Vision"),
        "PANEL_PROBLEM":        ("11-solution-infographic", "The problem (why this matters)"),
        "PANEL_SOLUTION":       ("11-solution-infographic", "The solution (what we built on Salesforce)"),
        "PANEL_OUTCOMES":       ("11-solution-infographic", "Outcomes (the proof)"),
        "PANEL_TAM":            ("14-exec-infographic", "Market opportunity (TAM)"),
        "PANEL_IDEAL_PARTNERS": ("14-exec-infographic", "Ideal partners"),
        "PANEL_BUILT_ON":       ("11-solution-infographic", "Built on Salesforce (the OEM/Embedded stack)"),
    },
}

def PANELS_FOR(slug):
    return set(SECTION_MAP.get(slug, {}).keys())

def SOURCES_FOR(slug):
    return {src for (src, _h2) in SECTION_MAP.get(slug, {}).values()}

# Rich single-source views: an artifact whose PRIMARY <slug>.html is a bespoke projected layout
# (not the generic doc shell). Each maps PANEL_* slots -> (source_slug, exact H2 heading in that source).
# Keys must equal the {{PANEL_*}} tokens in the referenced template (guarded by R-RICH-01/R-POSTER-03).
RICH_VIEWS = {
    "11-solution-infographic": {
        "template": "templates/solution-infographic.html",
        "map": {
            "PANEL_PROBLEM":  ("11-solution-infographic", "The problem (why this matters)"),
            "PANEL_SOLUTION": ("11-solution-infographic", "The solution (what we built on Salesforce)"),
            "PANEL_OUTCOMES": ("11-solution-infographic", "Outcomes (the proof)"),
            "PANEL_MARKET":   ("11-solution-infographic", "Market & who it's for"),
            "PANEL_BUILT_ON": ("11-solution-infographic", "Built on Salesforce (the OEM/Embedded stack)"),
        },
    },
    "12-marketecture": {
        "template": "templates/marketecture.html",
        "map": {
            "PANEL_STORY":    ("12-marketecture", "The architecture story (top to bottom)"),
            "PANEL_PARTNER":  ("12-marketecture", "Partner solution layer (what the ISV builds & sells)"),
            "PANEL_AGENT":    ("12-marketecture", "Agent & experience layer (Agentforce, portals, channels)"),
            "PANEL_PLATFORM": ("12-marketecture", "Platform layer (the parent SKU + Salesforce clouds)"),
            "PANEL_DATA":     ("12-marketecture", "Data & integration layer (Data 360, MuleSoft, Zero-Copy, source systems)"),
            "PANEL_TRUST":    ("12-marketecture", "Trust & compliance (Einstein Trust Layer, data protection, regulatory posture)"),
        },
    },
}

def render_view(slug, sources, template_text, meta):
    """Project a rich single-source view. Mirrors render_poster but reads its PANEL->(src,H2) map
    from RICH_VIEWS[slug]. Returns (filled_html, unfilled_tokens)."""
    if slug not in RICH_VIEWS:
        raise ValueError(f"{slug} is not a registered rich view")
    section_map = RICH_VIEWS[slug]["map"]
    fills = {k: _html.escape(str(v)) for k, v in meta.items()}
    split_cache = {}
    for panel, (src, h2) in section_map.items():
        if src not in sources:
            raise ValueError(f"{slug}: panel {panel} needs source '{src}' but it was not provided")
        if src not in split_cache:
            split_cache[src] = split(sources[src])
        secs = split_cache[src]
        if h2 not in secs:
            raise ValueError(f"{slug}: section '{h2}' not found in source '{src}'")
        fills[panel] = md_to_html(_body_after_h2(secs[h2]))
    unfilled = []
    def repl(m):
        k = m.group(1)
        if k in fills:
            return str(fills[k])
        if k not in unfilled:
            unfilled.append(k)
        return m.group(0)
    out = TOKEN_RE.sub(repl, template_text)
    return out, unfilled

def panels_for_view(slug):
    return set(RICH_VIEWS.get(slug, {}).get("map", {}).keys())

def sources_for_view(slug):
    return {src for (src, _h2) in RICH_VIEWS.get(slug, {}).get("map", {}).values()}

def _body_after_h2(section_text):
    # sections.split returns the section text; strip a leading "## Heading" line if present
    lines = section_text.splitlines()
    if lines and lines[0].lstrip().startswith("## "):
        lines = lines[1:]
    return "\n".join(lines).strip()

def render_poster(slug, sources, template_text, meta):
    """Return (filled_html, unfilled_tokens). `sources` is {source_slug: md_text} — every artifact this
    poster draws from. meta supplies TITLE/LABEL/RELEASE/GENERATED_DATE/HOME_HREF."""
    # metadata are plain scalars -> HTML-escape (matches md_to_html.py / canvas.py). Panel fills are NOT
    # re-escaped: md_to_html already produced escaped HTML.
    fills = {k: _html.escape(str(v)) for k, v in meta.items()}
    split_cache = {}
    for panel, (src, h2) in SECTION_MAP.get(slug, {}).items():
        if src not in sources:
            raise ValueError(f"{slug}: panel {panel} needs source '{src}' but it was not provided")
        if src not in split_cache:
            split_cache[src] = split(sources[src])
        secs = split_cache[src]
        if h2 not in secs:
            raise ValueError(f"{slug}: poster section '{h2}' not found in source '{src}'")
        fills[panel] = md_to_html(_body_after_h2(secs[h2]))
    unfilled = []
    def repl(m):
        k = m.group(1)
        if k in fills:
            return str(fills[k])
        if k not in unfilled:
            unfilled.append(k)
        return m.group(0)
    out = TOKEN_RE.sub(repl, template_text)
    return out, unfilled
