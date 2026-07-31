# Product Pull-Through & GTM Activation Reference

Load this file during Stage 2 (Pre-fill + Propose) when populating Commercial Context, and during Stage 3 (Clarify) when revenue model is underdeveloped.

**How to use:** Identify the partner's commercial model type (ISVforce or OEM/Embedded). Map their solution to the pull-through opportunity table. Populate the Commercial Context section with specific SKUs, activation triggers, and GTM motion. Flag revenue share activation as a required decision before the opportunity reaches 03-Contract.

---

## Part 1: ISVforce Pull-Through Model

ISVforce apps run on the customer's existing Salesforce org. The partner's app creates dependencies that drive customers to buy additional Salesforce licenses they don't currently own. This is the pull-through revenue opportunity — and it is the primary Salesforce commercial rationale for investing in an ISVforce partnership.

**The core question:** When a customer adopts this ISVforce app, which Salesforce SKUs must they add or upgrade?

### SKU Pull-Through by Category

**Edition Upgrades**
ISVforce apps frequently require Enterprise Edition (EE) or Unlimited Edition (UE) features. Customers on Professional Edition are common upgrade targets.

| Trigger | Edition Required | Typical Delta |
|---------|-----------------|---------------|
| Advanced automation (Process Builder / Flow features) | Enterprise+ | ~$50–75/user/month |
| API access at volume | Enterprise+ | ~$50–75/user/month |
| Custom app permissions, profiles, object-level security | Enterprise+ | ~$50–75/user/month |
| Unlimited sandbox environments, Governor Limit increases | Unlimited | ~$75–125/user/month |

**Industry Cloud Add-Ons**
Vertical ISVforce apps that complement an Industry Cloud create the strongest pull-through case. The customer needs the Industry Cloud for the ISVforce app to realize its full value.

| ISV Vertical | Pull-Through SKU | Est. ACV per User |
|---|---|---|
| Healthcare / Life Sciences | Health Cloud Enterprise | ~$300–360/user/year |
| Financial Services | Financial Services Cloud | ~$225–300/user/year |
| Manufacturing | Manufacturing Cloud | ~$240/user/year |
| Retail / CPG | Consumer Goods Cloud / Commerce Cloud | Varies by module |
| Public Sector | Public Sector Solutions | ~$240–360/user/year |
| Energy & Utilities | Energy & Utilities Cloud | ~$240/user/year |

**Einstein & Agentforce Add-Ons**
ISVforce apps that surface AI recommendations, next-best-action, or automated agents drive Einstein/Agentforce seat license pull-through.

| Feature Used | Pull-Through SKU | Notes |
|---|---|---|
| Next Best Action recommendations | Einstein for Sales/Service | Required for NBA on record pages |
| Agentforce agents embedded in app | Agentforce for Service (or Sales) | $2/conversation or seat-based |
| AI-powered scoring or predictions | Einstein Prediction Builder | Included in higher EE/UE tiers |
| Generative AI / LLM features | Einstein 1 / Agentforce foundation | Requires specific seat license |

**Data Cloud Add-Ons**
ISVforce apps doing customer data unification, AI model training, or real-time CDP functions require Data Cloud.

| Use Case | Pull-Through SKU |
|---|---|
| Unified customer profile across sources | Data Cloud for CRM |
| Real-time segmentation and activation | Data Cloud Add-On |
| AI model training on customer data | Data Cloud for Industries |

**Platform Expansion**
Customers who have one Salesforce cloud and adopt an ISVforce app with cross-cloud requirements get pulled into adjacent clouds.

| ISVforce Scenario | Pull-Through SKU |
|---|---|
| Sales Cloud customer adds field ops ISV | Field Service Lightning (FSL) |
| Service Cloud customer adds knowledge AI ISV | Einstein for Service add-on |
| Any cloud adding external partner/customer portal | Digital Experiences (Communities) |
| Cross-system integration layer | MuleSoft Anypoint (if no API middleware exists) |
| Reporting and analytics overlay | Tableau Creator or Explorer |

---

## Part 2: OEM / Embedded Partner Model

OEM and Embedded partners build a Salesforce-powered product that the end customer may not know runs on Salesforce. The partner licenses Salesforce at OEM wholesale pricing and resells it embedded in their own product.

### Model Types

| Type | Description | Customer Sees |
|------|-------------|---------------|
| **Full OEM** | Salesforce completely embedded, custom domain, rebranded UI | Partner's product only |
| **Light OEM** | Salesforce UI with partner branding; SF may be visible in URL/footer | Blended |
| **Platform OEM** | Salesforce platform (Apex/LWC/data) only; fully custom UI | Partner's custom interface |
| **ISV OEM / Reseller** | Partner resells Salesforce licenses as part of a bundled offer | Salesforce product, partner bundle |

### Revenue Mechanics

- Partner buys Salesforce at **OEM wholesale price** (typically 50–70% of standard list)
- Partner sets their own **retail price** — the margin between wholesale and retail is the revenue model
- Partner owns all end-customer billing, renewals, and account management
- Salesforce gets wholesale revenue; partner takes the margin
- No deal registration or SPIFF process — the partner IS the channel

### OEM Pull-Through Considerations

- OEM partners can still pull through additional Salesforce SKUs when customers expand usage beyond the OEM bundle
- As the embedded solution grows, the customer may want to access the full Salesforce platform — this is the upgrade path that both partner and Salesforce benefit from
- OEM agreements should specify which SKUs are in-bundle vs. eligible for additional pull-through revenue

---

## Part 3: Go-to-Market Approaches

### Motion 1 — AppExchange Co-Sell (Primary for ISVforce)

Best for: ISVforce apps targeting mid-market and enterprise customers; deals where Salesforce AE engagement accelerates close.

**How it works:**
1. Partner identifies a prospect who already has Salesforce (or is buying Salesforce)
2. Partner registers the deal in Salesforce Partner Community before AE engagement deepens
3. Salesforce AE gets notified; AE earns quota credit if the deal involves new Salesforce license revenue
4. Partner and AE co-present — partner owns the ISVforce value story; AE owns the Salesforce platform story
5. Deal closes; partner gets revenue share on net-new Salesforce licenses; AE gets quota credit

**What makes it work:**
- Deal must be registered early — AEs will not retroactively credit a partner
- Partner must have a one-pager the AE can use in the deal
- Pull-through must be real — AE will not carry the app if there's no Salesforce license upside

**What kills it:**
- Partner brings in AE too late
- No identified Salesforce license gap in the deal
- Partner's AE doesn't know how to introduce Salesforce into the conversation

### Motion 2 — AppExchange Marketplace (Self-Serve)

Best for: ISVforce apps with lower ACV, clear trial experience, and strong self-service onboarding.

**How it works:**
- Optimized AppExchange listing with trial or freemium capability
- Trailhead module or guided setup for onboarding without a sales rep
- Customers discover, trial, and buy without Salesforce AE involvement
- Works best for <$15K ACV deals in SMB and commercial segments

**Pull-through implication:** Lower AE involvement means lower pull-through activation. If pull-through is a strategic priority, this motion alone is insufficient.

### Motion 3 — SI Channel

Best for: ISVforce apps that require significant implementation services (>60 days deployment).

**How it works:**
- SI partners (Accenture, Deloitte, Slalom, Cognizant, etc.) include ISVforce app in their project SOW
- SI becomes the primary sales channel — ISVforce partner provides technical support and certification
- Salesforce AE introduces SI when the account is large enough for SI-led delivery
- Requires SI partner enablement, margin/referral agreements, and co-delivery certification

**Pull-through implication:** SI-led deals often include larger Salesforce license expansions — strong pull-through opportunity, but SI must be trained on the pull-through story.

### Motion 4 — Co-Marketing & Joint Pipeline

Best for: Driving awareness and inbound leads at the vertical or industry level.

**Tactics:**
- Joint customer case studies (Salesforce + Partner co-authored)
- Industry Cloud launch partnerships — be featured in Health Cloud or FSC launch marketing
- Dreamforce presence — demo theater, breakout session, partner booth
- Account mapping with Salesforce — identify customers who have Salesforce but not the ISVforce app
- Salesforce+ content — webinars, demos hosted on Salesforce's media channel

---

## Part 4: Partner Sales Org Activation

The partner's own sellers are the first activation bottleneck. A partner whose sales team can't clearly explain the Salesforce value story will fail to create the conditions for co-sell.

### What Partner Sellers Need

**Salesforce product literacy (baseline):**
- What is the Salesforce platform — what does it do, who uses it, why customers buy it
- Difference between Sales Cloud, Service Cloud, Industry Clouds, and platform add-ons
- How AppExchange works — how customers discover and trust ISVforce apps
- The platform trust story — security, compliance, AppExchange certification

**ISVforce positioning:**
- "We run natively on Salesforce" — what this means for the customer's IT org (no additional infrastructure, same security posture, same data model)
- Why native is better than integrated — data residency, latency, admin experience, upgrade path
- How to handle "why don't you just build this yourself?" from the customer's IT team

**AE engagement model:**
- When to bring in a Salesforce AE (before the customer has selected their Salesforce edition, not after)
- How to register the deal (Partner Community portal — step-by-step)
- What the AE needs from the partner in the first meeting: pull-through SKU, deal value, timeline
- What to ask the AE for in return: account introductions, field marketing budget, co-sell support

**Qualification:**
- Tier 1 prospect: already has Salesforce, needs the ISVforce add-on → lowest friction, highest pull-through
- Tier 2 prospect: evaluating Salesforce alongside competing platforms → co-sell opportunity, higher effort
- Tier 3 prospect: no Salesforce, no plans → deferred; Salesforce AE must lead platform sell first

### Partner Seller Enablement Assets (produce these before launching co-sell)

| Asset | Purpose | Owner |
|-------|---------|-------|
| Salesforce 101 deck (partner-customized) | Platform literacy for partner sellers | Partner + PAM |
| Co-sell playbook | Who does what in a joint deal | Partner + PAM |
| AE one-pager | What AEs need to know about the app in 2 minutes | Partner |
| Deal registration walkthrough | How to register and track in Partner Community | PAM |
| Pull-through SKU cheat sheet | Which Salesforce licenses this app requires/drives | Partner + PAM |
| Objection handling guide | "Why Salesforce?" and "Why this app?" objections | Partner + SE |

---

## Part 5: Salesforce Sales Org Activation

Salesforce AEs have hundreds of accounts. They will actively carry an ISVforce app only when three conditions are met:

1. **Financial incentive** — deal registration SPIFF or explicit quota credit for influenced Salesforce revenue
2. **Easy to explain** — the app can be described in one sentence tied to a Salesforce Cloud the AE is already selling
3. **Solves a deal blocker** — the ISVforce app closes a gap that was preventing the AE's Salesforce deal from closing

### Activation Tactics for Salesforce AE Teams

**AE one-pager (required, not optional):**
One page. Must answer:
- What problem does this app solve for the customer?
- Which Salesforce Cloud does it extend?
- What new Salesforce licenses does this deal require?
- What does the AE need to do to register and co-sell?
- Who is the partner contact for deal support?

**SE brief:**
- Technical architecture overview (one diagram)
- AppExchange listing and security review status
- Typical implementation timeline and SI delivery model
- Common integration points and data requirements

**Deal registration SPIFF:**
- Partner negotiates a SPIFF with Salesforce (via PAM and regional VP) for AEs who register and progress deals
- SPIFF is typically tied to net-new Salesforce license revenue in the deal (not the ISVforce ACV)
- Timing: SPIFF must be confirmed before AE outreach begins

**Regional enablement sessions:**
- 30-45 minute live demo + Q&A for AE teams in target geographies
- Run through Partner Community or coordinated by PAM
- Focus on: the problem, the Salesforce SKU pulled through, how to identify the target customer in their book

**Ongoing engagement in Slack/Chatter:**
- Partner Community Slack channel for real-time deal support
- AEs can ask questions during live deals without a formal email thread
- Partner's technical contact should be available same-day on these channels

**Named overlay coverage for strategic accounts:**
- For deals >$250K ACV, PAM can provide a named Salesforce resource to support the deal
- This should be documented in the PADA as a commitment, not just a best effort

### Identifying Target AEs and Accounts

The highest-value activation targets are Salesforce AEs who:
- Are actively selling the specific Industry Cloud this ISVforce app extends
- Have accounts with an identified gap the ISVforce app fills
- Are in quota attainment risk — the ISVforce app helps them close faster

Ask the PAM to run an account overlap analysis: which Salesforce accounts have the target Industry Cloud but not the ISVforce app? That is the co-sell target list.

---

## Part 6: Revenue Share Activation

### ISVforce Revenue Share

Revenue share is typically defined in the PADA. Key mechanics:

| Lever | Description |
|-------|-------------|
| Revenue share % | Typically 5–25% of net-new Salesforce license revenue the partner's deal influences; exact % varies by PADA |
| Deal registration | Partner must register the deal in Partner Community BEFORE Salesforce AE closes the license sale |
| Attribution window | Revenue is attributed to the partner if Salesforce license closes within a defined period (typically 90–180 days) after registration |
| Co-sell commitment | PADA specifies what Salesforce commits to — AE introductions, field marketing support, SE overlay |
| Minimum thresholds | Some PADAs include minimum pipeline or closed-won commitments per quarter to maintain co-sell status |

**Critical failure mode:** Partner registers deals late or not at all → Salesforce closes the license → partner gets no credit. This is the most common revenue share activation failure. Fix: automate deal registration as part of the partner's own CRM process.

### OEM/Embedded Revenue

No revenue share process — the margin IS the model. Key tracking considerations:

- Track Salesforce wholesale license costs as COGS, not as a pass-through
- Renewal economics: OEM renewals are the partner's responsibility — Salesforce does not manage them
- Expansion revenue: when OEM customers want to expand beyond the OEM bundle, this is an upsell opportunity for the partner (and a potential cross-sell back to direct Salesforce licensing)

### Revenue Share Readiness Checklist

Before committing to a co-sell motion, confirm:
- [ ] PADA is signed and revenue share % is defined
- [ ] Partner has access to Salesforce Partner Community and deal registration is enabled
- [ ] At least one partner seller has been trained on the deal registration process
- [ ] PAM has confirmed SPIFF structure for Salesforce AE activation in target geos
- [ ] Pull-through SKU is identified and documented — AE knows exactly which license this deal drives
- [ ] Co-sell pipeline target is agreed (e.g., $X of joint pipeline within 90 days of program launch)
