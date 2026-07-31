# Discovery Questions by Section

Ask these when a section is missing or underspecified. Capture verbatim answers — do not paraphrase.

> **Two discovery axes.** This file is organized by **POV output section** and is used reactively (Stage 3) to fill gaps in a specific POV section. The **Discovery Framework** (`refs/discovery-framework.md`, Stage 15) is organized by **discovery dimension** and is used proactively. When running Stage 15, reuse the question wording here rather than duplicating it; when filling a POV gap, this file is the primary source.

## Problem Space

**If Problem Statement is missing or too vague:**
- Who specifically experiences this problem? (role, organization type)
- What are they doing today instead — and why does that fall short?
- What is the measurable consequence when the problem is not solved? (hours lost, errors, cost, risk)

**If Significance is missing:**
- How many people or organizations face this problem?
- What does this cost at scale — to the customer, to the market, to the patient?

**If industry trends and market context are missing:**
- What are the 2–3 most significant trends or regulatory imperatives driving demand for this solution right now? (Name them — not "digital transformation.")
- What does this industry's core challenge look like as a business problem, not a technology problem?
- What does the status quo cost — in dollars, time, patient outcomes, or regulatory risk?

**If Challenges are missing:**
- What has prevented people from solving this before?
- What organizational or technical barriers make the status quo sticky?

**If Risks are missing:**
- What could prevent this solution from succeeding after launch?
- Are there competing initiatives, regulatory constraints, or partner execution risks to name?

## Vision

**If Vision Statement is vague or missing:**
- In one sentence: what will a specific user be able to do with this solution that they cannot do today?
- What is the measurable outcome for that user — not for the market, for the individual?

**If partnership vision is missing:**
- How would you describe the proposed Salesforce partnership vision in one sentence?
- What does success look like for this partnership in 24 months — for your company, your customers, and Salesforce?

## Solution

**If Solution Statement is too technical or jargon-heavy:**
- Describe what the solution does in plain language for a non-technical executive.
- What does the customer actually see and interact with?

**If Benefits are missing:**
- What are the top three things a customer gains by using this solution?
- Which of those is most defensible and measurable?

**If KPIs are missing:**
- How will the customer know the solution is working?
- What will they measure at 30, 90, and 180 days?

**If Product-Market Fit (Viable/Feasible/Desirable/Ethical) is missing:**
- Viable: How does the partner make money from this? What is the commercial model?
- Feasible: Can this be built natively on Salesforce, or does it require significant external infrastructure?
- Desirable: Do existing customers or prospects want this today? Who has asked for it?
- Ethical: Are there data privacy, patient safety, or compliance considerations to name explicitly?

## Use Cases

**If use cases are feature descriptions rather than outcome statements:**
- Who is the user in this scenario?
- What job are they trying to get done?
- What does the solution enable them to do that they couldn't before?
- What is the measurable outcome for that user?

**If fewer than three use cases are available:**
- What is the most common workflow this solution changes?
- What is the highest-value workflow this solution changes?
- Who else in the organization benefits — a different persona?

## Target Markets

**If primary market is not named:**
- What type of organization is the ideal first customer? (size, vertical, geography)
- Are there specific pilot customers already in conversation?

**If secondary/adjacent markets are missing:**
- Where does the solution extend naturally — different vertical, different buyer, different region?

## Personas

**If personas are missing or generic:**
- Who configures or administers this solution? What do they care about?
- Who uses it day-to-day internally? What problem does it solve for them specifically?
- Is there an external user — customer, patient, partner? What do they experience?

## Architecture

**If architecture section is empty:**
- Is this a native managed package, a composite app, or a hybrid? Describe briefly.
- What external systems does it integrate with? What APIs?
- Which Salesforce clouds or SKUs does it depend on? (e.g., Service Cloud, Health Cloud, Data Cloud)
- What does the UI look like — native LWC, Canvas app, custom portal?

**If SF cloud dependencies are missing:**
- Which Salesforce licenses does the customer need to already own for this to work?
- Does this add value to any specific Industry Cloud?

**If marketecture or solution flow is missing:**
- Walk me through the solution marketecture — how does data flow, which systems connect, and where does Salesforce sit in the architecture?
- Where does the Salesforce platform begin and end? What does the partner own vs. what Salesforce provides?

## Commercial Model

**If commercial model is missing:**
- Is this packaged as an ISVforce managed package, an OEM/embedded license, or something else?
- How is it priced — per user per month, per org, tiered?
- Does it generate pull-through for Salesforce SKUs?

**If revenue activation is not addressed:**
- How does the revenue share model work, and what triggers activation?
- Beyond cost reduction — what new revenue does this solution enable for the customer?
- What is the revenue story for Salesforce from this partnership: pull-through SKUs, expanded seats, new logos?

**If pull-through SKUs are not identified (ISVforce):**
- Which specific Salesforce edition does your app require — and are most of your target customers already on that edition?
- Does your app require or materially benefit from Health Cloud, Financial Services Cloud, or another Industry Cloud? Is that license already in your target customer's install base?
- Does your app use or surface Einstein features, Agentforce agents, or Data Cloud — and have you scoped what licenses those require?
- Walk me through the total Salesforce license spend in a typical deal with your app — what does Salesforce ACV look like before and after?

**If OEM/Embedded model (confirm mechanics):**
- Are you licensing Salesforce at OEM wholesale pricing, or at standard list?
- Does your end customer know they're running on Salesforce, or is it fully embedded under your brand?
- Who manages the end-customer support, renewal, and expansion — you or Salesforce?
- Is there a path for customers to graduate from your OEM bundle to a full Salesforce platform relationship?

**If GTM motion is undefined:**
- What percentage of your current pipeline involves a Salesforce AE in the deal — zero, some, or most?
- Have you done deal registration in Salesforce Partner Community? If not, is that a process gap or a deliberate choice?
- What does a Salesforce AE get out of carrying your solution — quota credit, SPIFF, or just goodwill?
- Is the PADA signed? If yes, what does it specify for co-sell commitment and revenue share?

**If partner seller activation is not addressed:**
- Can your sales team explain to a customer why running natively on Salesforce matters vs. a point solution?
- Do your AEs know when to bring in a Salesforce AE vs. handle the Salesforce conversation themselves?
- What is the one objection your sellers can't yet answer when a customer asks "why not just use [named alternative] instead of Salesforce + your app"?

## Risks & Competitive Threats

Ask these when the Risks section is thin, no competitive context has been surfaced, or Stage 9 is being prepared.
These questions often surface the most important content in the POV — push for specific answers, not general ones.

**Competitive landscape:**
- Who are the top 2–3 alternatives a customer would evaluate alongside this solution? (Name them.)
- What does this solution offer that none of those alternatives do?
- If Salesforce decided to build this capability natively and bundle it into [relevant Industry Cloud], what would the partner do?

**Churn / customer risk:**
- Describe a scenario where a customer buys this solution and abandons it 12 months later. What is the trigger?
- What is the most common objection you hear from prospects who don't buy? What does that tell you about retention risk?
- What does a successful customer look like at 12 months? What does a churned customer look like?

**Platform dependency:**
- Which specific Salesforce APIs or features is this solution built on? Are any of those on a deprecation path?
- Which Salesforce SKUs must the customer already own for this to work? Are those typically in the install base of your target customer?
- Who on the partner's team knows the full codebase? What happens if that person leaves?

**Market & regulatory:**
- What regulatory development in [vertical] would most disrupt the problem this solution solves?
- Is there any pending legislation, CMS/ONC/CFPB guidance, or industry enforcement action that could affect this solution in the next 18 months?
- What acquisition or consolidation in [vertical] would most threaten this solution's market position?

## Strategic Fit & Mutual Value

Ask these when the Solution Alignment section is thin or when preparing for internal Salesforce stakeholder review.

**Why this partnership is strategic:**
- Why is Salesforce the right technology and business partner for you — over building on AWS, Azure, or another hyperscaler?
- What aspect of the Salesforce platform is most critical to your product roadmap, and why can't that be replicated elsewhere?
- How does this partnership accelerate your roadmap in ways organic development cannot?

**The Salesforce perspective (ask the partner to articulate this):**
- Why would Salesforce be strategically interested in your solution? What gap in the Salesforce ecosystem does it fill?
- What would a Salesforce AE say to a customer to explain why your solution matters alongside their core Salesforce investment?
- What does this partnership unlock for Salesforce that Salesforce could not achieve on its own?

## Partner Enablement & Sales Motion

Ask these when the go-to-market section is underdeveloped or when the partner has not sold through a platform ecosystem before.

- What does the current sales motion look like — direct, channel, or marketplace?
- What would your sellers need to co-sell effectively alongside a Salesforce AE?
- What does a joint customer engagement look like end-to-end: who sources the deal, who runs the demo, who manages the close?
- What resources does the Salesforce ISV program provide that are most relevant to your team right now — PADA co-sell commitment, technical architect access, AE enablement, MDF?

## AI & Responsible Use

Ask these when the solution involves AI, ML, automation, or data-driven recommendations.

- Where does AI play a role in your solution — prediction, recommendation, automation, or generation?
- What data does the AI model use, and how is customer data isolated and protected?
- What guardrails have you built against bias, incorrect recommendations, or unintended automation?
- How do you explain AI-generated outputs to end users — is there transparency in how decisions are made?
- Has the solution been reviewed against Salesforce's Trusted AI principles or an equivalent ethical AI framework?

## Technical Assessment

Ask these when evaluating build plan feasibility, preparing for a technical stakeholder review, or running Stage 9. Push for specifics — "we have some debt" is not an answer.

**Architectural Runway:**
- Does the current architecture support the scale of your largest 3 enterprise prospects? What breaks first at 10× current load?
- Which parts of the architecture were designed for your current customer size and must be redesigned before you can support enterprise SLAs?
- How does the architecture account for Salesforce's evolving platform — Agentforce, Data Cloud, Einstein AI? Where does it have headroom and where does it create lock-in to a specific API version?
- What is the single most architecturally risky dependency in the solution today?

**Technical Debt:**
- Where is the most significant technical debt in the codebase? (Name the component, the trade-off made, and when.)
- Has the solution passed Salesforce's AppExchange Security Review? If not, what are the known blockers?
- What share of engineering capacity per sprint goes to debt maintenance vs. new feature development?
- Is there debt that must be resolved before the solution can support a named enterprise customer at full scale?

**MVP Definition & Roadmap:**
- Is the MVP scope written down and bounded? Can it be delivered within the OG Tech Strategy Framework engagement timeline?
- What is explicitly in scope for MVP, what is explicitly out, and what is the sequencing rationale?
- What are the top 3 dependencies that could delay the MVP? (Name the system, the approval, or the resource.)
- Who is the design partner for the MVP — a named customer who has committed to pilot it? If none exists, what is the path to naming one?
- How does the MVP unlock H1 and H2? What does completing it make possible that isn't possible today?

## Partner Concerns to Surface

These are questions the partner will ask during the engagement. Surface them early so answers can be documented or prepared before stakeholder reviews.

**On competitive risk from Salesforce:**
- "What is stopping Salesforce from building this capability natively and making our solution irrelevant?" → Document the moat (unique data, workflow lock-in, domain expertise) and address native-displacement risk honestly using red-team Frameworks 1 and 3.

**On technical migration:**
- "Do we need to move our technology off our current platform to work with Salesforce?" → Document the migration path, scope, and timeline. If no migration is required, state that explicitly.

**On program resources:**
- "What training and enablement does the Salesforce ISV program actually provide?" → Document specific program benefits: PADA co-sell commitment, technical architect access, AE enablement support, Trailhead certifications, MDF, AppExchange listing support.

**On the working relationship:**
- "What does working with Salesforce day-to-day actually look like for our team?" → Document the PAM cadence, technical resources available, escalation path, and what the partner handles independently vs. with Salesforce support.
