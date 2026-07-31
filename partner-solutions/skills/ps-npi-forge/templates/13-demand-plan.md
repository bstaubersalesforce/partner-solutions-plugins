<!-- VOICE: narrative — first-person exec/architect McKinsey register; see refs/voice-and-style.md -->
# {{PRODUCT_NAME}} — Demand Plan Framework

> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
>
> {{GAP_BANNER}}

## How to use this framework
{{FRAMEWORK_INTRO}}

## The demand grid

Rows are identified segments (each with a TAM estimate and an Ideal-Partner-Profile fit indicator from
#10). The SKU-bundle columns are **Core / Required SKUs**, **Standard add-ons**, and **Conditional
(NPI-dependent) add-ons**. The **Halo ACV (est.)** column captures cross-cloud pull-through (Data
Cloud / MuleSoft / Tableau Next) the PAM is credited for alongside the OEM licenses — a flagged
estimate, not partner-facing pricing.

| Segment | TAM (est.) | IPP-fit | Core / Required SKUs | Standard add-ons | Conditional (NPI-dependent) add-ons | Halo ACV (est.) |
|---------|-----------|---------|----------------------|------------------|-------------------------------------|-----------------|
| {{DEMAND_GRID}} | | | | | | |

## Segment & TAM basis
{{SEGMENT_TAM_BASIS}}

## Internal business case (estimates)

Internal planning inputs — **flagged estimates** from internal Salesforce insights, **not
partner-facing pricing**. Each is an estimate pending commercial-team confirmation.

| Segment | TAM (est.) | ASP (est.) | Penetration % (est.) | Attrition % (est.) | Modeled ACV (est.) |
|---------|-----------|-----------|----------------------|--------------------|--------------------|
| {{BUSINESS_CASE_TABLE}} | | | | | |

## Conditional (NPI-dependent) add-ons — inclusion rule

A cell in the **Conditional (NPI-dependent) add-ons** column is filled **only when the NPI process has
identified that add-on as required** for that segment (for example, the CC / CC+ elements for
Agentforce for Healthcare). Otherwise the cell stays empty — do not populate it speculatively.

{{CONDITIONAL_ADDONS_NOTE}}

## Demand logic (diagram)
{{DEMAND_DIAGRAM}}

---
**Sources:** {{SOURCES}}
**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}
