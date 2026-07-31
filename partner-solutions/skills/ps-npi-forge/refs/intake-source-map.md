# Intake & source map

How an effort gets its inputs, and what each source feeds. Org62 entitlement intake is live
(per [refs/org62-entitlements.md](org62-entitlements.md), Phase 4 complete). **Slack *read* intake
is live** (Slack MCP: channel discovery + message/thread read + resource-link harvest, with a pasted
summary as fallback); only Slack *canvas publish* (write) is deferred to Phase 6. **Deep research is
usable as an intake source today** — a grounding-tagged research brief feeds the narrative + technical
artifacts, not just #10 Tier C (Tier C remains the opt-in deep mode). Channels degrade gracefully: a
source being absent never blocks an artifact — it proceeds and the missing input becomes a flagged gap.

## Minimum viable input

The **only required input to open an effort is a parent direct SKU reference** -- "model a
partner/OEM product on *this*" (e.g., Health Cloud EE/UE for an Agentforce-for-Healthcare-OEM
effort). From that alone the skill derives a first-pass entitlement set (06) and a skeletal
brief (01). Everything else is an enricher that raises confidence and fills placeholders.

## The opening prompt + follow-up questions (the intake conversation)

An effort almost always starts from a one-line request shaped like:

> *"I'd like to create an ISV Embedded SKU based on the standard `<parent>` SKU."*
> (e.g., *"...based on the standard Health Cloud SKU."*)

That single line is enough to open the effort. Then ask these follow-ups, **one at a time**, to
firm up the parent-SKU modeling spine -- but never block on them (an unanswered question becomes a
flagged gap, not a stop):

1. **Planned name of the ISV Embedded SKU?** -- what the OEM/Embedded product will be called (e.g.,
   *"Agentforce for Healthcare"*). Drives `{{PRODUCT_NAME}}` and the naming-difference delta in 06.
   If unknown, proceed with a working name and flag it.
2. **Which edition(s)?** -- EE, UE, or both (e.g., *EE and UE*). Sets which parent `Product2`
   variants to resolve in Org62 and which OEM SKU rows 06/07 carry.
3. **Required add-ons?** -- the add-ons the solution genuinely needs (e.g., *Community Cloud and
   Community Cloud Plus* for patient/caregiver portals). These become the **Required** tier in 07.
4. **Any other add-ons?** -- recommended/optional ones, or "none expected." Anything named goes to
   the Recommended/Optional tiers in 07; "none expected" is recorded so the tiering reads complete,
   not empty.
5. **Slack channel(s) for the parent SKU?** -- the existing `#help-sell-...` channel(s) for the
   parent (e.g., *#help-sell-health-cloud*). Recorded as the effort's coordination channel + the
   future canvas-publish target (Phase 6). If none, leave the manifest `slack_channel` empty.
6. **Resource links?** -- actual URLs to FCDs, release decks, enablement hubs, official docs. **If
   real links are provided, include them in the artifacts** (08 setup guide + 01 "Additional
   resources" + the canvas), subject to the official-docs allowlist below -- official links are
   cited; non-official links are recorded as flagged sources, not citations.
7. **Anything else to consider?** -- an open catch-all for shared-org constraints, packageability
   timing, a pilot customer, related efforts (e.g., a prior NPI the parent shares add-ons with), or
   known gaps. Whatever surfaces is routed to the relevant artifact or recorded as a flagged gap.

The answers seed the manifest (`product_slug`, `parent_sku`, `slack_channel`) and the parent-SKU
modeling spine below; anything left unanswered is a flagged gap with an owner + next step.

## The six channels (each degrades gracefully)

A source being absent **never blocks** an artifact -- the artifact proceeds and the missing input
becomes a flagged gap (manifest placeholder with an owner + next step), recorded so the
00-executive-summary's Next Steps & Blockers register can roll it up.

| Channel | Feeds | Access | If absent |
|---------|-------|--------|-----------|
| **Paste** (baseline) | 01-05 | User drops FCD text, draft Quip content, notes | Artifacts stay skeletal, low confidence |
| **Link / source-fetch** | 08, 10, 01 | Official Salesforce docs only (allowlist below); non-official links flagged, not fetched | Resource links left as `pending` |
| **Org62** | 06, parent-SKU modeling | Read-only `sf` CLI vs. the `org62` alias (session identity): `Product2` + `productEntitlements` for the parent `pId` | 06 from paste/knowledge, low confidence, gap flagged |
| **Slack channel (read — live)** | Coordination context; the NPI working channel's facts (e.g. Template ID, scratch-org feature params) -> 08/09; harvested resource links -> 01/05; canvas publish (write) is Phase 6 | Slack MCP **live read**: discover channels, read messages/threads, harvest decks/links; pasted summary as fallback | No coordination context; the working-channel facts stay flagged gaps; canvas exported locally only |
| **SF price-list catalog** | 07 (which SKUs/add-ons exist) | Reference catalog (the SF price-list tool) | Tiering from knowledge + Org62, flagged for catalog check |
| **Deep research (live) / Web research** | research-grounded brief -> 01/03/06/08/10/11/12; 10 Tier C deep candidate-research is opt-in | A grounding-tagged (`[SOURCED]`/`[INFERRED]`/`[PENDING]`) research brief feeds the family today; Tier C is the opt-in deep fan-out (citations + verify loop) | Artifacts fall back to model knowledge, flagged; POV stays at Tier B (archetypes + illustrative companies) |

**TAM and target segments** are **estimated during research using internal Salesforce insights**,
captured once as effort data (value + basis + confidence + `estimate` flag), and reused by
13-demand-plan, 14-exec-infographic, 00-executive-summary, and 11-solution-infographic as a single
source of truth. When TAM or segments are not provided, all consumers degrade gracefully to a flagged
`pending` gap rather than diverging guesses. **Business-case inputs** (ASP, penetration, attrition,
cross-cloud halo ACV) are likewise **research-derived flagged estimates** from internal Salesforce
insights, confined to #13, never partner-facing pricing.

## Slack read intake (the method)

Slack is read **live via the Slack MCP** (read-only at intake — publishing a canvas is the Phase-6
write path, which always confirms first). The repeatable steps:

1. **Discover channels** — search for the parent SKU's channel(s) (`#help-sell-...`) and any NPI
   working channel for the effort (e.g. a `#temp-...-npi-...` channel). Record their IDs in the
   effort's `sources/slack-intake.md`.
2. **Read the working channel** — pull the messages/threads that carry NPI facts: the Template ID
   status + owners, scratch-org definition / feature parameters, packaging decisions. These feed
   **08-setup-guide** and **09-org-provisioning-validation** (the Template-ID gap carriers).
3. **Harvest resources** — collect decks, FCDs, enablement hubs, canvases, and doc links posted in
   the channels. Official links (allowlist below) are cite-able and flow into **01** (Additional
   resources) and the safe public subset of **05**; internal links are recorded **flagged internal**
   (named + linked, never an external-FAQ citation).
4. **Fallback** — if a channel is private/unreachable, a **pasted summary** is an equal-authority
   source; capture it the same way. A channel that yields nothing is a flagged gap, never a blocker.

Capture everything to `sources/slack-intake.md` and record each item against the artifact it grounds
(see "Recording sources"). Pricing seen in channels stays **out of scope** — direct-sell promos are
context, never the OEM SKU price.

## Official-docs allowlist

Technical guidance (08-setup-guide, 09, the technical parts of 01/03) cites **official Salesforce
sources only**. The operational allowlist:

- `help.salesforce.com`
- `developer.salesforce.com`
- `architect.salesforce.com`
- Trailhead
- the Partner Community
- Org62-internal tools

Anything else is **flagged as non-official and excluded** from technical-guidance artifacts --
never silently included, never silently dropped. A non-official link the user pastes is recorded
as a flagged source, not used as a citation.

## Parent-SKU modeling (the spine of the technical artifacts)

Given the parent `Product2` (e.g., Health Cloud EE/UE), the skill:

1. Reads the parent's entitlement composition -- licenses, PSLs, features, storage (Phase 4 pulls
   this from Org62; until then, from paste/knowledge, flagged low-confidence).
2. Proposes the Embedded/OEM equivalent, **flagging naming differences** ("Health Cloud" ->
   "Agentforce for Healthcare") and **deltas** (what changes for OEM vs. the direct SKU).
3. Applies partner-motion rules (OEM-only, shared-org restrictions, packageability timing) as a
   validation pass.
4. Derives the minimalist Required / Recommended / Optional add-on tiers (07).

The skill **drafts and flags; a human confirms.** It never silently asserts an entitlement -- a
proposed license/PSL/feature/storage set is always presented for human confirmation.

## Out of scope

**Pricing and discounts are out of scope** -- not the skill's to determine. SKU/add-on tables
surface *which* SKUs exist and tier them; price and discount cells stay as marked placeholders
owned elsewhere. Do not invent or infer a price.

## Recording sources

Every input is recorded against the artifact it grounded (the manifest `sources` list). This is
what later lets the claim-verification loop ask "is this sentence traceable to a provided
source?" and what drives the confidence score down when a claim is ungrounded.
