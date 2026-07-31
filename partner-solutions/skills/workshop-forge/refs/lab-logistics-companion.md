# Companion tooling — PIE Lab Slack Skills (logistics, not content)

> **Internal reference (Salesforce-internal Slack; links are SSO-gated — not for partner-facing output).**
> workshop-forge produces the **content** of a lab (GUIDE / FACILITATOR / modules / provisioning / commercial).
> A separate set of **Slackbot skills** owns the **operational logistics** around it. They are complementary,
> not overlapping — know the seam so you hand off cleanly and never try to do the other's job.

## What the PIE Lab Skills do (and don't)

Three AI Slackbot skills run the PIE-lab logistics lifecycle inside Slack (DM Slackbot, describe what you need):

| # | Skill | Who / When | Output |
|---|-------|-----------|--------|
| 1 | **Lab Creation** | PIE Moderators · once per lab | PAM Nomination Guide canvas · Partner Nominees list · **Lab Registry** entry · PAM Notice slide |
| 2 | **Nominee Sign-Up** | PAMs · while a lab is Active | Partners written to the nominee list + deadline reminders |
| 3 | **Partner Onboarding** | PIE Moderators · post-approval | `#tmp-[location]-[partner]` channel + a pre-filled **ISV Technical Brief** per partner |

Explicit scope (from the skills' own quick-reference): *"These skills handle operational logistics only — lab
setup, nominations, and onboarding. They do not create workshop content, agendas, or delivery materials."*

## The seam with workshop-forge

The lab lifecycle is: **1 Lab Setup → 2 Nominations → 3 Review → 4 Onboarding → 5 Lab Delivery.**
- **Stages 1–4 = PIE Lab Skills** (logistics: registry, nominations, partner channels, briefs).
- **Stage 5 = the content workshop-forge produces** (the kit the lab actually delivers).

They hand off cleanly in both directions:
- **Into workshop-forge:** the onboarding skill's **ISV Technical Brief** + the registry's **use-case summary** are
  a ready freeform input for **author mode** (see [input-contract.md](./input-contract.md) §2) — partner, use case,
  and requirements already structured.
- **Out of workshop-forge:** the **Lab Registry**'s standardized lab description + requirements describe *which*
  lab type is being run (Build / Optimize / Ideate / Data360); use it to pick the kit's overlay and depth.

## The Lab Registry — the logistics source of truth

The **Lab Registry** canvas is a **live listing of the actual labs held / scheduled** — and the single source of
truth the nomination + creation skills read at runtime (active/coming-soon/closed labs, per-lab requirements,
standardized descriptions, nomination-list IDs). Real entries seen include a **Chicago Agentforce Build Lab** and a
**New York Data360 Lab** — so it doubles as a running record of past + upcoming labs. Lab types it tracks:
🔨 **Build** · 📈 **Optimize** · 💡 **Ideate** · 📊 **Data360**. workshop-forge kits map naturally onto **Build** and
**Data360** labs (hands-on delivery); **Ideate/Optimize** are lighter-touch and may not need a full kit.

## Guardrails to respect (theirs, not ours)
- **Never hand-edit the Lab Registry** — always via the Lab Creation skill; manual edits break the other skills at runtime.
- Slackbot **can't** delete lists, create Slack Connect channels, or pin messages — those stay manual.
- Registry list/column IDs are load-bearing; wrong IDs break the nomination skill.

## Pointers (internal, SSO-gated — do not reproduce in partner-facing material)
- PIE Lab Skills quick-reference canvas (skill map + end-to-end flow + key rules).
- Lab Registry canvas (source of truth for active/upcoming labs).
- Full Skills Guide canvas (detailed instructions, limitations, FAQs).

*(Canvas IDs intentionally omitted here — reach them via the PIE Slack workspace. They're workspace docs, not skill code.)*
