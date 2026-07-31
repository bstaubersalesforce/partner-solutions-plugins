# Industry Alignment Router

This is a slim index. Load it during Stage 1 to identify the partner's vertical, then load **only the matching per-vertical file** from `refs/verticals/` — do not load all verticals. This keeps context lean.

**How to use:**
1. From research, identify the partner's primary vertical.
2. Load the one matching file below. It contains: Salesforce Industry Cloud, market snapshot (sourced figures), key focus areas, top aligned use cases, regulatory drivers, suggested KPIs (with targets), and the MVP alignment signal.
3. Map the partner's core use cases to that file's focus areas. Use its market data for the POV Significance section and the MVP Build Plan's Industry Alignment section.
4. Flag mismatches — if the partner's claimed use cases don't appear under their stated vertical, either the vertical is wrong or the positioning is off.

**If the partner spans multiple verticals:** Name the primary vertical (where the first design partner or pilot customer lives) and a secondary if applicable. Load both files. Do not claim all verticals — that is not a position, it is the absence of one.

**Market data calibration:** Figures in the vertical files are analyst estimates current as of 2024–2025. Treat them as directionally correct for framing. Verify specific numbers against current analyst reports before including in a formal deliverable.

---

## Vertical → File Lookup

| Partner's primary vertical | Load this file | Salesforce Industry Cloud |
|---|---|---|
| Healthcare, payer, provider, life sciences, pharma, digital health | `refs/verticals/healthcare-life-sciences.md` | Health Cloud, Life Sciences Cloud |
| Banking, wealth, lending, insurance, fintech | `refs/verticals/financial-services.md` | Financial Services Cloud |
| Industrial, OEM, field service, asset-heavy, ESG | `refs/verticals/manufacturing.md` | Manufacturing Cloud, Net Zero Cloud |
| Retail, eCommerce, CPG, loyalty, trade promotion | `refs/verticals/retail-consumer-goods.md` | Commerce Cloud, Consumer Goods Cloud |
| Government, agency, citizen services, grants, nonprofit, education | `refs/verticals/public-sector.md` | Public Sector Solutions, Nonprofit/Education Cloud |
| Utility, grid, energy, EV, clean energy | `refs/verticals/energy-utilities.md` | Energy & Utilities Cloud, Net Zero Cloud |
| Hotels, airlines, cruise, OTA, restaurants, travel platforms | `refs/verticals/travel-hospitality.md` | Service + Loyalty Management + Data Cloud (no standalone SKU) |
| Carriers, 3PL, freight brokers, shippers, fleet, supply chain | `refs/verticals/transportation-logistics.md` | Service + Field Service + Manufacturing Cloud + MuleSoft (no standalone SKU) |
| OEM, dealer groups, captive finance, mobility, connected vehicle | `refs/verticals/automotive.md` | Automotive Cloud |

---

## Vertical Not Listed

If the partner's primary vertical is **not** in the lookup table above, do not flag it as a dead-end TBD — research it live. State plainly that no predefined file exists, then build the equivalent of a vertical file on the fly:

1. Name the vertical explicitly — do not default to "various industries."
2. Identify the relevant Salesforce Industry Cloud or closest core-cloud analog (name it; if no dedicated SKU exists, say so).
3. Research and cite 2–3 market size / CAGR figures from named analyst sources (Gartner, Grand View, MarketsandMarkets, IDC, etc.) before the POV is delivered. Label any unverified figure "Estimated."
4. Name the top regulatory or compliance driver that makes the problem non-negotiable for customers.
5. Identify 3–5 vertical-specific KPIs with suggested targets, and the MVP alignment signal.
6. **Offer to persist** the researched vertical as a new `refs/verticals/` file and add a router row (see README → Keeping industry data fresh) so the next engagement in this vertical reuses it.

Only fall back to a named-owner TBD if research genuinely cannot source the market data — and say what specifically could not be found.
