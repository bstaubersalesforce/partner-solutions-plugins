# Mermaid diagrams (SLDS-themed)

Diagrams in ps-npi-forge artifacts are authored in **Mermaid**, themed to the SLDS palette, and
rendered live in the HTML view (`templates/document-shell.html` embeds the Mermaid `@11` CDN with
`startOnLoad: true`). The same fence renders natively on GitHub/GitLab. This ref is the self-contained
copy of the theme directive (source of truth: `style-conventions.md`); keep it in sync if the palette
changes.

## The single-source theme directive

Prepend this verbatim to every diagram fence:

```
%%{init: {"theme":"base","themeVariables":{"primaryColor":"#f0f5fc","primaryTextColor":"#032d60","primaryBorderColor":"#0176d3","lineColor":"#444444","secondaryColor":"#f8fafc","tertiaryColor":"#ffffff","fontFamily":"Salesforce Sans, Helvetica Neue, Arial, sans-serif"}} }%%
```

Border = SLDS `$brand-accessible` `#0176d3`; line = `$color-text-weak` `#444444`.

## Authoring

The generator (the draft->refine->validate cycle) fills each artifact's diagram token with a themed
fence whose CONTENT reflects the effort's real data -- diagrams are not static template strings. A
fence goes in a ` ```mermaid ` block (the converter emits it verbatim as `<pre class="mermaid">`).

## Named diagram types (which artifact, what it shows)

| Token | Artifact | Diagram |
|-------|----------|---------|
| `{{STATUS_ROLLUP_DIAGRAM}}` | #00 executive-summary | Status / blocker rollup: each artifact node colored by status, blockers called out. |
| `{{COMPOSITION_DIAGRAM}}` | #06 license-entitlements | Entitlement composition: parent product -> grant rows (by derived category). |
| `{{TIER_DIAGRAM}}` | #07 addon-tiering | Tier-decision view: Required / Recommended / Optional add-ons. |
| `{{PARTNER_FIT_DIAGRAM}}` | #10 partner-profile-pov | Partner-fit logic: why embedded/OEM fit *because* poor direct-SF target. |
| `{{INFOGRAPHIC_DIAGRAM}}` | #11 solution-infographic | Solution overview: problem -> solution -> outcomes, built on Salesforce. |
| `{{MARKETECTURE_DIAGRAM}}` | #12 marketecture | Layered marketecture: partner layer over Agentforce / platform / data layers. |

## Rendering wide diagrams (no clipping)

Long node labels can overflow their container and clip in the browser view. Two guards:

1. **Render-surface config.** `document-shell.html` and `slide_deck.py` initialise Mermaid with
   `flowchart: { useMaxWidth: true, htmlLabels: true, wrappingWidth: 220 }` and constrain the
   injected SVG with `.mermaid svg { max-width: 100%; height: auto; }` so a diagram scales to its
   card instead of clipping.
2. **Authoring.** Keep node labels short. Break a long `·`-joined list across `<br/>` lines rather
   than one wide line (e.g. `Data 360 · MuleSoft<br/>Zero-Copy · EHR/FHIR`), so no single label is
   wider than the container.

## SVG / PNG for decks (capability-gated)

`@mermaid-js/mermaid-cli` (`mmdc -i x.mmd -o x.svg`) exports a fence to SVG/PNG for decks. It is
**capability-gated**: if `mmdc` is absent, keep the fence/`.mmd` source and report the install
(`npm i -g @mermaid-js/mermaid-cli`) -- never block the artifact. `scripts/mermaid_export.py` handles
the detect/export/report path.
