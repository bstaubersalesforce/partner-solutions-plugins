# Red Team Lenses for Partner Solution Assessment

Six adversarial frameworks adapted for ISV partner evaluation in the Salesforce OG Tech Strategy Framework.
Load this file when running Stage 9 or when deepening the Risks section of a POV or MVP Build Plan.

**Ground rules (apply in every framework):**
- Named competitors must be real — do not invent plausible-sounding companies
- If a named comparable is required and none is known, write "No verified comparable identified — flag as TBD"
- Every vulnerability is rated on two axes: Likelihood (High / Medium / Low) and Severity (Critical / High / Medium / Low)
- Lead with the conclusion — state the most important finding first, evidence follows
- No hedging: "this could potentially be a risk" → "this is a risk"

---

## Framework 1: Competitive War Game

**Adversarial role:** You are this partner's most dangerous competitor — an established software vendor, a large SI with similar capability, or Salesforce itself deciding to build this natively. You know their pricing, their roadmap, and which Salesforce customers they are targeting.

**Goal:** Make this partner's solution irrelevant within 18 months.

**Attack vectors to consider:**
- **Direct competition**: Build or acquire a competing solution and target the same Salesforce install base
- **Platform play**: Pitch Salesforce's own product team on adding this capability natively to an Industry Cloud
- **Distribution leverage**: Bundle a comparable (even inferior) solution into an existing enterprise contract at no incremental cost
- **Price compression**: Undercut the partner's pricing to win key design customers and starve them of reference accounts

**Output contract — must produce:**
1. Top 3 specific competitive threats (name the company, SI, or "Salesforce native" — not generic "incumbents")
2. For each threat: the specific attack vector and the partner vulnerability it exploits
3. The single biggest competitive vulnerability to close before MVP launch

---

## Framework 2: Customer Exit Simulation

**Adversarial role:** You are the VP of CRM or Salesforce platform owner at a healthcare system or financial institution. You championed this AppExchange install 6 months ago — you put your credibility on the line to get budget approved. You are now writing the renewal cancellation message to the partner's rep, already dreading the internal conversation with your CIO.

**Be specific, not polite.**

**Common ISV churn triggers to probe:**
- **Implementation drag**: Took 3× longer or cost 2× more than the SOW estimated; your IT team resents it
- **Salesforce native displacement**: At last month's release notes review, your admin flagged that Salesforce now does 80% of this natively for free
- **Compliance surprise**: Security review post-purchase surfaced a data residency or HIPAA concern that the sales cycle glossed over
- **ROI failure**: 90-day check-in — couldn't produce the numbers that were in the business case; stakeholder lost confidence
- **Support ceiling**: Your enterprise has an issue at 2am. The partner has 3 engineers on their team. SLA is unenforceable.

**Output contract — must produce:**
1. The specific churn trigger (not a general complaint — name the moment)
2. Where the customer went instead: named competitor, Salesforce native feature, in-house build, or do-nothing
3. The one thing that would have kept this customer — specific, not "better support"

---

## Framework 3: Platform Dependency Scan

**Adversarial role:** You are auditing this ISV solution for single points of failure specific to the Salesforce platform context.

**Five dependency categories to audit:**

**API Fragility** — Which Salesforce APIs does this solution depend on? What happens if Salesforce changes rate limits, deprecates an endpoint, or changes authentication requirements? (Example: solutions built on legacy SOAP APIs or undocumented internal APIs carry high fragility risk.)

**Feature Overlap / Native Displacement Risk** — Which part of this solution's core value proposition could Salesforce ship natively in the next 18 months? Check: Einstein AI roadmap, Industry Cloud release notes, recent Dreamforce announcements in this vertical. If the overlap is high, the partner is building in the shadow of the platform.

**Licensing Dependency** — Which Salesforce SKUs must the customer already own for this solution to work? If those SKUs are not in the typical install base of the partner's target customer, the TAM is smaller than the POV claims.

**Partner Technical Capacity** — Can this partner support enterprise clients at scale? Red flags: single engineer who knows the codebase, no 24/7 support model, no documented runbook, no security certifications. This is a risk to Salesforce's reputation if the partner can't deliver.

**Customer Concentration** — Does the partner have >30% of their revenue (or OG Tech Strategy Framework engagement momentum) from 1–2 customers? If a key design partner withdraws, does the OG Tech Strategy Framework engagement lose its proof point?

**Architectural Runway** — Can the current architecture support the scale of the partner's enterprise target customers? Red flags: built for SMB volume and targeting enterprise SLAs, no horizontal scaling model, monolithic design with no documented path to multi-tenant isolation, or architecture tightly coupled to a Salesforce API version currently on a deprecation path. If runway is zero, the MVP timeline is fictional.

**Technical Debt Ceiling** — Is there accumulated debt that would block AppExchange Security Review, enterprise SLA delivery, or the OG Tech Strategy Framework MVP timeline? Partners routinely understate this. Ask specifically: what percentage of engineering capacity goes to maintenance vs. new features? Has the solution passed a Salesforce security review? If not, what are the open findings?

**Output contract — must produce:**
1. Each identified vulnerability rated: Likelihood (H/M/L) × Severity (Critical/H/M/L)
2. The #1 priority vulnerability — highest combined rating, called out explicitly
3. One vulnerability the partner has almost certainly not considered (often: feature overlap or licensing dependency)

---

## Framework 4: 18-Month Invalidation Scenarios

**Adversarial role:** Generate 3 plausible scenarios in the next 18 months that would seriously damage this partner's solution or market position. These must be realistic — not doomsday fantasies.

**Three scenario types for Salesforce ISV solutions:**

**Scenario Type A — Salesforce Native Capability**
Salesforce announces a feature at Dreamforce or in a quarterly release that covers this solution's core differentiation. The customer's admin enables it from Setup. The renewal conversation changes from "what does this ISV give us?" to "why are we paying for what Salesforce ships for free?"

*Early warning signals to name:* Salesforce product blog posts on this topic, Einstein AI roadmap items, Trailhead modules appearing for this capability, similar AppExchange solutions being acquired by Salesforce.

**Scenario Type B — Vertical Regulation Shift**
A regulatory change in the partner's primary vertical (CMS rule, ONC guidance, CFPB action, state-level legislation) changes what data can be processed, what workflows must look like, or what certifications a vendor must hold. If the partner's solution is not built to comply, the customer can't use it.

*Early warning signals to name:* Named pending legislation, enforcement actions against comparable vendors, industry association guidance documents, pilot program results.

**Scenario Type C — Market Consolidation**
A large established vendor (Epic, Veeva, Oracle Health, Workday, etc.) acquires a competing point solution or bundles comparable capability into an existing enterprise contract. The partner's differentiation narrows overnight, and the distribution advantage of the acquirer is decisive.

*Early warning signals to name:* Named acquirer's recent M&A activity, competitor fundraising rounds (typically precede acquisition), acquirer's public roadmap announcements, hiring patterns (building adjacent capability vs. acquiring it).

**Output contract — must produce for each scenario:**
1. What specifically changes (name the Salesforce feature, the regulation, or the acquirer)
2. Impact on this solution's revenue, customer base, or competitive position
3. Two observable early warning signs that are checkable today — not vague, name the signal
4. What the partner should do differently if this scenario is unfolding

---

## Framework 5: Salesforce Investment Teardown

**Adversarial role:** You are the Salesforce investment committee / GTP review board. You have seen many ISV partner pitches and you are looking for reasons to **pass** on committing OG Tech Strategy Framework resources to this one. You are not the partner's market competitor — you are the internal funder deciding whether this partnership earns Salesforce's investment.

**Attack vectors to consider:**
- **Thin proof:** No named pilot, no reference account willing to go on record, KPIs that are targets not results
- **Undifferentiated bet:** The partner's value could be replicated by three other ISVs in the same vertical, or by Salesforce natively
- **Commercial fragility:** The pull-through case rests on assumptions the install base does not support (see also Framework 6)
- **Execution doubt:** The team cannot demonstrably build and support at the scale of the enterprise prospects named in the POV
- **Precedent of failure:** A comparable ISV pursued this exact play and did not make it — and the same mechanism could repeat here

**Output contract — must produce:**
1. The 3 biggest holes in the partner case that would justify a "no" — specific, not "needs more traction"
2. The single question the partner most likely cannot answer yet (the one that ends the meeting)
3. A **named comparable ISV that attempted this and failed** (real, from research) and the specific failure mechanism that could repeat here. If no verified comparable is known, write "No verified comparable identified — flag as TBD" and state what kind of precedent would need checking.

---

## Framework 6: Commercial Model Pressure Test

**Adversarial role:** You are a skeptic attacking the partner's commercial and pull-through model. You accept the product works — you do not accept that the money works. Your job is to find where the commercial premise breaks.

**Attack vectors to consider:**
- **Pull-through math break:** The point where the pull-through revenue case collapses — a price point, an attach-rate assumption, or a Salesforce edition/SKU the target install base does not already own
- **Revenue-share viability:** Whether the PADA / revenue-share economics are real at the partner's actual scale, or only work at a customer count they do not have
- **Buyer alternative:** A cheaper competitor, a Salesforce-native path, or "do nothing" that makes the partner's commercial premise hard to defend to a budget-constrained buyer
- **Edition dependency:** If the solution requires Enterprise/Unlimited edition or specific add-on SKUs, is that already in the target customer's stack — or is it a hidden cost that shrinks the real TAM?

**Output contract — must produce:**
1. The specific point where the pull-through math breaks — name the price point, attach-rate, or edition/SKU dependency (not "pricing is risky")
2. Revenue-share viability verdict: at what customer count / ACV does the PADA economics actually work, and does the partner have it?
3. One named alternative (cheaper competitor, Salesforce-native path, or do-nothing) that makes the partner's commercial premise hard to defend — and the one change that would make the model defensible
