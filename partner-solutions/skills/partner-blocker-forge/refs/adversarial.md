# refs/adversarial.md — the mandatory "claimed vs. real" method

This runs on **every** partner-blocker-forge invocation (triage and deep-dive alike). Its job: separate
what the partner *claims* from what is *real*, and land a defensible verdict. Do not accept the partner's
framing — or your own first read — as fact.

## Step 1 — Classify every claimed issue

For each distinct issue the partner raises, assign a **primary class** (and note a secondary if it genuinely
spans two — e.g. a config issue that surfaced a bug):

| Class | What it is | How to confirm | Exemplar |
|-------|-----------|----------------|----------|
| **Confirmed product bug** | A defect support/R&D reproduced or acknowledged | Case comment thread shows R&D repro / investigation / a code-level root cause | e.g. a Record ID passed to an agent as the literal string `currentRecordId` instead of the value → "RECORD NOT FOUND"; R&D reproduced it |
| **Config / permission** | Org setup or entitlement, not a platform defect | Case resolved by enabling a permission / changing a setting | e.g. "enable connected app creation" requests; a package-upload email-format workaround |
| **Knowledge gap / overstated claim** | The claim is inaccurate or broader than the docs support | Primary doc contradicts or narrows the claim | e.g. "Data Kits exclude retrievers" — **no-code** retrievers ARE packageable; only Ensemble/Pro-code excluded |
| **Question, not an issue** | An inquiry that was answered; nothing is broken | Case is a "please confirm…" that got a correct answer | e.g. a 2GP non-linear versioning "is this supported?" question |
| **Accurate + by-design (workaround exists)** | True, intended behavior, with a supported path | Doc confirms the constraint AND names the intended workaround | e.g. "parent agents can't be packaged" — true; path = BotTemplate + AgentExchange + per-org instantiation |
| **Accurate + hard constraint (no supported path)** | True, and there is **no** viable workaround/roadmap today | Doc confirms the constraint; no source names a path, or the only path ("wait") is indefinite | e.g. `EmailTemplatePage` unsupported in 2GP conversion — "remove or wait," waiting is indefinite (no roadmap) |
| **Roadmap / unreleased — unverifiable** | The claim is about a capability no released source covers | No doc / Known Issue / case / release note covers it → `UNVERIFIED` | "will X be packageable next release?" — PM/support open item, never asserted |

A claim can be partly true — split it (e.g. "retrievers excluded" = false for no-code, true for Ensemble/Pro-code).

**By-design is not a dodge.** A constraint being "by-design" does **not** close the analysis. If the supported path
imposes material cost/manual effort on the partner, flag it as a **product-gap candidate to escalate to PM** — don't
let the "by-design" label pre-empt the real-issue verdict.

## Step 2 — Challenge the framing

Interrogate the presentation, not just the facts:

- **Strip persuasive language.** "Big blow," "all-in," "turned them away," "numerous blockers" are doing
  rhetorical work. Restate each claim neutrally before judging it.
- **Count the *real* blockers.** A list of "numerous" issues is often padded with questions, config tickets,
  and one genuine bug. Count how many survive Step 1 as real capability constraints.
- **Test the partner's own choice.** Is what they decided (e.g. "go manual for the pilot") actually
  reasonable on its merits? Sometimes the answer is yes — say so; it makes the rest credible.
- **"Resolved" ≠ "root-caused."** Distinguish a case fixed *with a stated cause* from one fixed *by workaround
  with no explanation*. A pile of workaround-only resolutions is a legitimate reason for a partner to lack
  production confidence — and it's a different problem than a capability gap.
- **Separate the layers.** Capability gaps, operational/config friction, and confidence/trust are three
  different problems with three different owners. Don't let them blur into one "packaging is broken" narrative.

## Step 2.5 — Name the underlying issue (capability / operational / confidence)

The classes above sort *individual claims*; this step names the **partner's real problem** — often not the one
they stated. It's the skill's highest-value judgment (in one real case the blocker was framed as "packaging
capability gaps," but the real issue was **confidence**). Decide which of three it is (it can be more
than one — rank them):

| Underlying issue | Signals it's this | What resolves it |
|------------------|-------------------|------------------|
| **Capability** | Confirmed bugs and/or accurate hard-constraints dominate; a supported path is genuinely missing or costly | Product fix / roadmap / a real architecture change — engineering + PM |
| **Operational / config** | The cases are mostly config, permission, setup, or environment; each is individually fixable | Better setup guidance, enablement, a post-install runner — support + PS advisory |
| **Confidence / enablement** | The *facts* mostly check out (claims overstated, questions, by-design) or issues were "fixed" without stated root cause — but the partner has lost trust and is retreating (going manual, abandoning a strategy) | Correct the overstated facts, show the supported path, and **request root-cause writeups** on the recurring cases so they can regain production confidence |

**The tell:** if you fix every named issue and the partner still wouldn't move to production, the real issue is
**confidence**, not capability. Say so in the verdict — recommending a product fix for a confidence problem (or
vice-versa) is the most common way this analysis goes wrong.

## Step 2.7 — Name the recurring PATTERN across claims (when ≥2 claims share a shape)

Step 1 classifies each claim; Step 2.5 names the partner's *underlying* problem. This step catches a third thing:
**a shape that recurs across multiple claims and is more persuasive than any single one.** Once you have ≥2 claims
(especially in a multi-case or living engagement), ask: *do several of these fail the same way?*

- **Look for the repeated mechanism**, not the repeated symptom. E.g. three different cases that are each "a
  mandatory/unannounced platform change broke a long-working setup" (a TTL change, an outbound-message change, a
  Shield-encryption change) are **one pattern with three instances** — far stronger evidence than three unrelated
  tickets.
- **Name the pattern explicitly** and **count its instances** with the case IDs behind each. "N independent,
  case-verified instances of X" is the most defensible sentence you can hand a PM — it converts a pile of tickets
  into a *trend*.
- **Distinguish it from Step 2.5.** Step 2.5 is the partner's problem *type* (capability/operational/confidence);
  this is a *cross-claim mechanism* ("SF platform changes destabilize their long-working builds"). A pattern can
  cut across the 2.5 buckets.
- **When it changes the verdict:** a strong pattern often reframes "~N scattered blockers" into "one systemic
  issue worth a roadmap conversation" — surface it in the verdict's "what's real" and "so what."
- No pattern? Say so and move on — don't manufacture one from two coincidences (that's the inverse of the
  don't-inflate rule).

## Step 3 — The required verdict

Every run MUST produce this block (short in triage, full in deep-dive):

> **Is there a real issue to resolve?**
> - **What's real:** (confirmed bugs + accurate-by-design constraints)
> - **What's overstated / not an issue:** (knowledge gaps, questions, padded count)
> - **Recurring pattern (if any):** the cross-claim shape from Step 2.7 + its instance count — often the strongest
>   single finding.
> - **The underlying issue:** name it per Step 2.5 — *capability*, *operational/config*, or
>   *confidence/enablement* (rank if more than one). Often not the one the partner named.
> - **So what:** the one-line implication for how to re-engage.

Anchor every judgment to evidence (a case comment, a doc line) and tag confidence **High/Med/Low** — plus a
distinct **`UNVERIFIED`** tag (separate from the confidence scale) for any claim you could **not** actually check.
`UNVERIFIED` is not "Low confidence": Low means checked-but-weak-evidence; `UNVERIFIED` means no source was
checked. Every `UNVERIFIED` claim is a **PM/support open item** and must never be asserted as fact. The verdict
block must state the **verification depth** (triage vs. deep-dive) and which source classes were actually checked.
