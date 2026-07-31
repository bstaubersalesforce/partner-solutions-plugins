# Competitive Landscape — Platform & Tooling Reference

> Curated, slow-moving platform-level facts used by **Stage 19 — Competitive Assessment**.
> This is the sourcing spine; the stage tops up fast-moving specifics (AI-model
> capabilities, recent program/pricing changes) with live research and confidence-labels
> everything. Keep this file balanced — it must read as a fair baseline, not a pitch.
>
> **Last reviewed:** 2026-06-03. AI-provider facts drift fastest — re-verify before use.
> Refresh cadence and procedure: see README → "Keeping industry data fresh".

Confidence labels match the skill convention: `[confirmed]` (durable, widely documented),
`[proposed — confirm]` (directionally true but verify for the specific partner/date).

---

## Category A — App / low-code platforms
Specific competitors a partner most often faces: **Microsoft Power Platform, ServiceNow, OutSystems** (name the partner's actual ones from POV research).

- **Commercial model** — Per-user and per-app subscription licensing, often bundled with a broader suite (Microsoft 365, ServiceNow ITSM). Predictable seat cost; consumption add-ons (AI, automation) increasingly metered. `[confirmed]`
  - *Where they can be stronger:* a customer already standardized on the suite sees the platform as near-zero marginal cost. `[confirmed]`
- **Ecosystem** — Established app marketplaces and large installed bases; ServiceNow strong in ITSM/workflow, Power Platform strong where Microsoft 365 is entrenched. Partner-app distribution exists but is smaller and less ISV-monetization-oriented than AppExchange. `[proposed — confirm]`
- **GTM program** — Partner programs exist; co-sell maturity and ISV revenue-share economics vary and are generally less developed than Salesforce's AppExchange + co-sell motion. `[proposed — confirm]`
- **Technology** — Strong low-code app building and workflow; CRM/industry data models are thinner or bolt-on. AI is being added rapidly (Copilot/Now Assist). Lock-in to the parent suite is real. `[proposed — confirm]`

## Category B — Hyperscalers (AWS, Azure, GCP)

- **Commercial model** — Pure consumption (pay-per-use compute/storage/managed services). Maximum flexibility and no seat minimums, but cost is unpredictable at scale and shifts the FinOps burden to the customer/ISV. `[confirmed]`
  - *Where they can be stronger:* unbeatable for raw infrastructure elasticity and for workloads with no CRM/business-app component. `[confirmed]`
- **Ecosystem** — Vast catalogs of primitives and a large SI/marketplace ecosystem, but these are infrastructure building blocks, not pre-built business applications, CRM data models, or industry clouds. The ISV assembles the application layer itself. `[confirmed]`
- **GTM program** — Mature marketplace co-sell and partner programs (e.g., ISV accelerate motions); reach is broad but oriented to infrastructure spend, not line-of-business app buyers. `[proposed — confirm]`
- **Technology** — Best-in-class infrastructure breadth, AI/ML platform depth (Bedrock, Azure AI, Vertex), and portability. But "data + app + AI + trust layer in one governed platform" is the customer's/ISV's integration project, not a delivered product. `[confirmed]`

## Category C — AI providers (OpenAI, Anthropic, Google Gemini/Vertex)
> Fastest-moving category — model capabilities and pricing change frequently. Treat the points below as the durable shape and verify specifics live.

- **Commercial model** — Token/usage-metered API pricing, plus enterprise tiers. Very low entry cost; cost scales with usage and can be hard to forecast for high-volume inference. `[confirmed]`
  - *Where they can be stronger:* frontier model quality and the fastest access to the newest model capabilities. `[confirmed]`
- **Ecosystem** — Rich developer ecosystems and tooling, but no business-application layer, CRM data model, or enterprise app marketplace for distributing packaged solutions to business buyers. `[confirmed]`
- **GTM program** — Emerging partner/marketplace motions; no established enterprise field co-sell comparable to a CRM-platform vendor's AE-activated motion. `[proposed — confirm]`
- **Technology** — Frontier model quality and agentic primitives. But the buyer must supply data grounding, identity, security/compliance, workflow, and system-of-record integration — i.e., raw model APIs vs. an end-to-end governed agent platform (Agentforce + Data Cloud + trust layer). `[proposed — confirm]`

---

## Salesforce baseline (for the comparison's "home" column)
- **Commercial model** — Subscription license + consumption (Agentforce/Data Cloud Flex Credits). For ISVs: AppExchange distribution with partner revenue-share economics and PADA. `[confirmed]`
- **Ecosystem** — AppExchange (the largest enterprise B2B app marketplace), pre-built CRM + industry data models, large installed base, mature ISV tooling (managed packages, security review). `[confirmed]`
- **GTM program** — Structured partner program with AE co-sell activation, deal registration, and field reach to line-of-business buyers. `[confirmed]`
- **Technology** — Data + app + AI + trust layer in one governed platform (Agentforce, Data Cloud, Einstein Trust Layer) on a shared metadata model. Trade-off: less raw infrastructure flexibility than a hyperscaler and platform lock-in. `[confirmed]`

> **Honesty anchor:** Salesforce is *not* the right foundation for every workload — pure-infrastructure or model-only use cases with no CRM/business-app component favor a hyperscaler or AI provider. The Stage 19 synthesis must say so.
