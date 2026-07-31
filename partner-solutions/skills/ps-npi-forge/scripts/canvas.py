#!/usr/bin/env python3
"""
canvas.py — assemble the Key Resources hub (canvas/index.html) from an effort manifest.

Local HTML is the source of truth; the Slack canvas (Phase 6) is a projection of this. Reads the
loaded manifest + a slug->bool map of which artifacts have an .html view, and emits an SLDS-themed
index: effort title/release, overall confidence + status rollup, the aggregated Next Steps & Blockers
register, then one card per artifact. A `pending` artifact renders as a labeled gap card (NOT a dead
link). Stdlib-only, pure: build_index(manifest, html_present) -> str.
"""
import html as _html
import re as _re

# status -> RAG-ish swatch (SLDS-aligned; decorative)
_STATUS_COLOR = {
    "verified": "#2e7d32", "drafted": "#e65100", "in_progress": "#e65100",
    "pending": "#c62828", "pulled": "#444444",
}
_LABEL = {
    "00-executive-summary": "Executive Summary", "01-brief": "Use-Case & Details Brief",
    "02-slide-summary": "Slide Summary", "03-internal-enablement": "Internal Enablement",
    "04-internal-faq": "Internal FAQ", "05-external-faq": "External FAQ",
    "06-license-entitlements": "License & Entitlements", "07-addon-tiering": "Add-On Tiering",
    "08-setup-guide": "Setup Guide", "09-org-provisioning-validation": "Org-Provisioning Validation",
    "10-partner-profile-pov": "Ideal-Partner POV",
    "11-solution-infographic": "Solution Infographic", "12-marketecture": "Marketecture",
    "13-demand-plan": "Demand Plan", "14-exec-infographic": "Executive Overview",
}

# short uppercase kind word per slug — drives the pill badge
_KIND = {
    "00-executive-summary": "Summary", "01-brief": "Brief", "02-slide-summary": "Deck",
    "03-internal-enablement": "Enablement", "04-internal-faq": "FAQ", "05-external-faq": "FAQ",
    "06-license-entitlements": "Entitlements", "07-addon-tiering": "Add-ons",
    "08-setup-guide": "Setup", "09-org-provisioning-validation": "Validation",
    "10-partner-profile-pov": "POV",
    "11-solution-infographic": "Infographic", "12-marketecture": "Marketecture",
    "13-demand-plan": "Demand", "14-exec-infographic": "Exec",
}

# one-line blurb per slug — from each artifact's real purpose (refs/artifact-templates.md)
_SUMMARY = {
    "00-executive-summary": "The front door: vision, the messaging hierarchy (key message → product → four pillars → features), top use cases, ideal-partner summary, and the rolled-up Next Steps & Blockers register.",
    "01-brief": "The product narrative plus the Key Use Cases grid (category, opportunity, example, key features, what partners package) — the canonical use-case and details story for the new OEM/Embedded SKU.",
    "02-slide-summary": "One-screen summary derived from the brief, ready to drop into a slide or stakeholder review.",
    "03-internal-enablement": "Internal positioning, sales-motion rules, and the entitlement implications field teams need.",
    "04-internal-faq": "PS/NPI question-and-answer coverage — OEM/VAR, shared-org, and packageability for the internal audience.",
    "05-external-faq": "The partner-facing, safe subset derived from the internal FAQ.",
    "06-license-entitlements": "Licenses, PSLs, features, and storage inherited from the parent SKU, with every delta flagged.",
    "07-addon-tiering": "Required / Recommended / Optional add-on tiering — minimalist, only what the solution needs.",
    "08-setup-guide": "Basic Info, TrialForce, 2GP scratch, and managed-package setup steps — grounded in official docs only.",
    "09-org-provisioning-validation": "Static Template-ID check plus an optional live org diff to confirm provisioning is correct.",
    "10-partner-profile-pov": "Whitespace point of view on the ideal partner — Tier B always, Tier C opt-in.",
    "11-solution-infographic": "A single-screen visual overview — problem, solution, outcomes, and the OEM/Embedded build-on-Salesforce story.",
    "12-marketecture": "A layered marketecture: how the partner solution stacks on the parent SKU's platform, Salesforce clouds, and data layer.",
    "13-demand-plan": "A commercial-team discussion grid: segments × SKU bundles, keyed to the ideal-partner profile and TAM, with internal business case and cross-cloud halo ACV.",
    "14-exec-infographic": "An exec single-screen: vision, value proposition, key use cases, ideal partners, and the market opportunity (TAM).",
}

# Card DISPLAY order on the canvas (presentation only — NOT the generation/registry order, which
# stays ARTIFACT_REGISTRY for #00-last + parity). Visual deliverables (posters) lead; tech canvases last.
# Any artifact not listed here falls to the end in registry order (so a future slug still appears).
DISPLAY_ORDER = [
    "14-exec-infographic",        # exec poster
    "11-solution-infographic",    # solution infographic (document-only)
    "00-executive-summary",
    "01-brief",                   # use-cases & details
    "02-slide-summary",
    "10-partner-profile-pov",
    "12-marketecture",
    "13-demand-plan",
    "03-internal-enablement",
    "04-internal-faq",
    "05-external-faq",
    "06-license-entitlements",
    "07-addon-tiering",
    "08-setup-guide",
    "09-org-provisioning-validation",
]

def _ordered_slugs(manifest):
    present = list(manifest["artifacts"])
    ranked = [s for s in DISPLAY_ORDER if s in present]
    rest = [s for s in present if s not in DISPLAY_ORDER]  # unlisted → registry order, at the end
    return ranked + rest

def _overall(manifest):
    vals = [r["confidence"] for r in manifest["artifacts"].values() if r.get("status") != "pulled"]
    return min(vals) if vals else 0.0

def _card(slug, rec, has_html, has_poster=False):
    status = rec.get("status", "pending")
    conf = rec.get("confidence", 0.0)
    color = _STATUS_COLOR.get(status, "#444444")
    label = _LABEL.get(slug, slug)
    kind = _html.escape(_KIND.get(slug, "Artifact"))
    summary = _html.escape(_SUMMARY.get(slug, ""))
    badge = (f'<span class="badge" style="background:{color}">{_html.escape(status)}</span>'
             f'<span class="conf">conf {conf:.2f}</span>')
    if has_poster:
        # poster IS the visual deliverable → the card title links to the poster;
        # the plain document view is a small secondary link so the two can't be confused.
        title = f'<a href="{slug}-poster.html">{_html.escape(label)}</a>'
        if has_html:
            title += f' <a class="secondary-link" href="{slug}.html">(document)</a>'
        if status != "verified":
            title += f' <span class="tag-pending">— {_html.escape(status)}, not yet final</span>'
        cls = "card"
    elif has_html:
        title = f'<a href="{slug}.html">{_html.escape(label)}</a>'
        if status != "verified":
            title += f' <span class="tag-pending">— {_html.escape(status)}, not yet final</span>'
        cls = "card"
    else:
        # not rendered → labeled gap card, no dead link
        title = f'{_html.escape(label)} <span class="gap">— not yet rendered</span>'
        cls = "card gap-card"
    return (f'<div class="{cls}">'
            f'<span class="card-kind">{kind}</span>'
            f'<h3 class="card-title">{title}</h3>'
            f'<p class="card-desc">{summary}</p>'
            f'<div class="card-meta">{badge}</div></div>')

# Bare render-placeholder tokens must never surface as a "blocker" in the register: a *_DIAGRAM
# token is stale once the diagram is rendered (drop it), and a pricing token reads as machine noise
# (relabel it to a human gap). This is the front-door safety net — the canvas stays clean even if the
# effort manifest still carries a raw placeholder string.
_TOKEN_RE = _re.compile(r"^\{\{[A-Z0-9_]+\}\}$")
_PRICING_LABEL = {
    "{{PRICE_PENDING}}": "Pricing — pending (out of scope, owned elsewhere)",
    "{{DISCOUNT_PENDING}}": "Discount — pending (out of scope, owned elsewhere)",
}

def _blockers(manifest):
    rows = []
    for slug in manifest["artifacts"]:
        for ph in manifest["artifacts"][slug].get("placeholders") or []:
            raw_item = str(ph.get("item", "")).strip()
            if _TOKEN_RE.match(raw_item):
                if raw_item.endswith("_DIAGRAM}}"):
                    continue  # stale: the diagram is rendered, not a real open gap
                raw_item = _PRICING_LABEL.get(raw_item, "Pending item (owned elsewhere)")
            item = _html.escape(raw_item)
            owner = _html.escape(str(ph.get("owner", "")))
            nxt = _html.escape(str(ph.get("next_step", "")))
            rows.append(f'<tr><td>{_html.escape(_LABEL.get(slug, slug))}</td><td>{item}</td><td>{owner}</td><td>{nxt}</td></tr>')
    if not rows:
        return '<p>No open blockers.</p>'
    return ('<table class="blockers"><thead><tr><th>Artifact</th><th>Gap</th><th>Owner</th>'
            '<th>Next step</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table>')

def build_index(manifest, html_present, poster_present=None):
    poster_present = poster_present or {}
    release = _html.escape(str(manifest.get("release", "")))
    slug = _html.escape(str(manifest.get("product_slug", "")))
    overall = _overall(manifest)
    cards = "\n".join(_card(s, manifest["artifacts"][s], html_present.get(s, False),
                            poster_present.get(s, False))
                      for s in _ordered_slugs(manifest))
    blockers = _blockers(manifest)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{slug} — Key Resources</title>
<style>
 *, *::before, *::after {{ box-sizing:border-box; }}
 body {{ font-family: "Salesforce Sans","Helvetica Neue",Helvetica,Arial,sans-serif; color:#181818; margin:0; background:#f8fafc; }}
 .wrap {{ max-width: 960px; margin: 0 auto; padding: 2.5rem 1.75rem 4rem; }}
 .eyebrow {{ text-transform:uppercase; letter-spacing:0.1em; font-size:0.7rem; color:#444; }}
 h1 {{ color:#032d60; font-size:1.6rem; margin:0.25rem 0; }}
 .release-badge {{ display:inline-block; background:#0176d3; color:#fff; font-size:11px; padding:2px 9px; border-radius:100px; }}
 .overall {{ background:#eef4ff; border-left:4px solid #0176d3; padding:0.7rem 1rem; border-radius:0 6px 6px 0; margin:1.25rem 0; }}
 h2 {{ color:#032d60; border-bottom:1px solid #e5e5e5; padding-bottom:0.2rem; margin-top:2rem; }}
 .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:20px; }}
 .card {{ border:1px solid #d8e0ec; border-radius:8px; padding:20px 20px 18px; display:flex; flex-direction:column; background:#fff; transition:box-shadow 0.15s ease, transform 0.15s ease; }}
 .card:hover {{ box-shadow:0 4px 18px rgba(3,45,96,0.12); transform:translateY(-2px); }}
 .gap-card {{ background:#f8fafc; border-style:dashed; }}
 .card-kind {{ align-self:flex-start; font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:#0176d3; background:#eaf2fd; padding:3px 9px; border-radius:10px; margin-bottom:12px; }}
 .card-title {{ font-size:16px; font-weight:700; color:#032d60; margin:0 0 7px; }}
 .card-title a {{ color:#032d60; text-decoration:none; }}
 .card-title a:hover {{ color:#0176d3; }}
 .card-title a.secondary-link {{ font-size:0.74rem; font-weight:400; color:#0176d3; }}
 .card-desc {{ font-size:13px; color:#444; flex:1; margin:0 0 16px; }}
 .card-meta {{ display:flex; align-items:center; gap:8px; }}
 .gap {{ color:#c62828; font-size:0.82rem; font-weight:400; }}
 .tag-pending {{ color:#e65100; font-size:0.82rem; font-weight:400; }}
 .badge {{ color:#fff; font-size:10px; padding:2px 8px; border-radius:100px; text-transform:uppercase; letter-spacing:0.05em; }}
 .conf {{ font-size:0.78rem; color:#444; }}
 table.blockers {{ border:1px solid #e5e5e5; border-radius:6px; overflow:hidden; border-spacing:0; width:100%; font-size:0.86rem; }}
 table.blockers th {{ background:#eef4ff; color:#032d60; text-align:left; padding:9px 12px; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid #e5e5e5; }}
 table.blockers td {{ border-top:1px solid #eef2f7; padding:9px 12px; }}
 table.blockers tr:nth-child(even) td {{ background:#f8fafc; }}
 @media print {{ .hero, .card-kind {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }} .card {{ break-inside:avoid; }} }}
</style></head>
<body><div class="wrap">
 <div class="eyebrow">Key Resources</div>
 <h1>{slug} <span class="release-badge">{release}</span></h1>
 <div class="overall"><strong>Overall confidence:</strong> {overall:.2f} <span style="color:#444">(floor: minimum across non-pulled artifacts)</span></div>
 <h2>Artifacts</h2>
 <div class="grid">
 {cards}
 </div>
 <h2>Next Steps &amp; Blockers</h2>
 {blockers}
</div></body></html>"""
