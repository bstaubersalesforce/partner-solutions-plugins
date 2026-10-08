# External research sources

A catalog of the external, public-web sources the plan draws on — primarily in **Stage 1
(Profile & trust posture)** and **Stage 4 (Red Team / Commercial)**. Use them to generate the
partner picture first-hand rather than relying on someone else's pre-written canvas. Each
source lists **what it is**, **what plan section it feeds**, and **how to pull it**.

## Source classes

### 1. Executive & org research — LinkedIn
- **What:** the partner's LinkedIn **company page** (headcount, headcount trend, locations) and
  **individual exec profiles** (title, tenure, prior roles, recent moves).
- **Feeds:** the **stakeholder / power map** (Stage 1) — who holds which lever, who is new, who
  just left; activation targeting; and **key-person risk** in the Red Team (a recent exec
  departure is a risk signal).
- **How:** profiles are often login-gated to bots — pull the public company page, then use the
  search tool for `"<name>" <partner> <title>` snippets; fall back to press releases and the
  partner's own leadership page for exec names/titles. **Confirm every title against a second
  source** before putting a name in the plan.

### 2. SEC filings — 10-K / 10-Q / 8-K / S-1 / DEF 14A
- **What:** mandatory financial disclosures for **publicly traded** companies, via SEC EDGAR
  (`sec.gov/cgi-bin/browse-edgar`). The **10-K** (annual) carries segment revenue, strategy,
  M&A, and — most valuable — the company's **own stated risk factors**.
- **Feeds:** profile scale/financials, **Red Team** (their stated risks are red-team gold; named
  competitors), Commercial (segment revenue → where consumption could land).
- **⚠️ Public-vs-private branch:** most ISV partners are **private / PE- or VC-owned → no SEC
  filings. Say so explicitly** and use *Funding & ownership* (class 6) instead. If a **parent**
  is public (an acquirer or PE holding co that files), check the parent's filings and attribute
  the segment.

### 3. Press releases / newsroom
- **What:** the partner's newsroom + PR wires (Business Wire, PR Newswire) + trade press.
- **Feeds:** profile + **traction/deals** (customer wins, funding, certifications), **Red Team /
  Commercial** (product launches signal roadmap direction and roadmap-overlap risk), and
  partnership signals (a co-announcement with Salesforce or a competitor).
- **How:** partner `/news` or `/press` path first; then a dated search for
  `<partner> announces OR launches OR raises`.

### 4. Events
- **What:** conference presence — Salesforce events (Dreamforce, TDX, Connections, Agentforce
  World) and the partner's **own vertical/industry conferences**: sponsorships, speaking slots,
  booths, awards.
- **Feeds:** **partnership-health signal** (presence warming or cooling — cross-check against the
  Org62 event-sponsorship opportunities, which show declined/dead = a cooling signal), **ICP**
  (which verticals they show up in), and *where to meet the execs* you want to activate.

### 5. Analyst & review sources
- **What:** Gartner / Forrester (Magic Quadrant / Wave position) and peer-review sites
  (G2, Capterra, TrustRadius) for sentiment, named competitors, and recurring pain points.
- **Feeds:** **Red Team** (competitive landscape, where customers are unhappy) and the
  Current-State Assessment (reported performance/usability gaps).

### 6. Funding & ownership
- **What:** Crunchbase / PitchBook — rounds, valuation, investors, and **who owns them**
  (PE / VC / public / founder).
- **Feeds:** the **trust posture** (a PE owner wary of a platform vendor = build-vs-buy /
  exit-pressure dynamic; see `trust-posture.md`) and Commercial (runway, acquisition appetite).

## Cross-cutting rules

- **Weight a source by what *only it* can tell you**, not by count — a blocked LinkedIn is a
  bigger loss for the stakeholder map than a blocked review-site is for anything.
- **Corporate sites and LinkedIn frequently 403 bots.** On a block, run the fallback chain
  (about/news pages → a cached/alternate search render → the partner's LinkedIn page →
  AppExchange → trade press) before declaring a fact unavailable.
- **Accuracy gate (load-bearing):** confirm any load-bearing fact (a financial figure, an exec's
  current title, a named competitor) from a **primary** source. AI-generated canvases and search
  snippets are **leads, not facts** — if a canvas carries an "AI-generated, review for accuracy"
  disclaimer, treat its claims as unconfirmed and verify before asserting.
- **Data safety:** public external facts are fine to cite; still scrub cross-customer identifiers
  and anything non-public from partner-facing versions (see `org62-case-scan.md`).

## What feeds what

| Source | Primary plan section |
|--------|----------------------|
| LinkedIn (execs/org) | Stage 1 stakeholder/power map; Red Team key-person risk |
| SEC 10-K/10-Q/8-K | Profile financials; Red Team (stated risks, competitors); Commercial |
| Press / newsroom | Profile; traction/deals; Red Team roadmap-overlap |
| Events | Partnership-health signal; ICP; exec-activation targeting |
| Analyst / reviews | Red Team competitive; Current-State Assessment |
| Funding / ownership | Trust posture; Commercial |
