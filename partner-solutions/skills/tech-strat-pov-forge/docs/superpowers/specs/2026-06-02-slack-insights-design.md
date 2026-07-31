# Slack Insights for POV Builder — Design

**Date:** 2026-06-02
**Status:** Approved (brainstorming) — ready for implementation planning
**Scope:** v1 = ingestion + POV pre-fill + Stage 3 pruning + auditable provenance (A + C). Scorecard wiring is a documented fast-follow.

---

## 1. Purpose

Enrich a POV with intelligence from **named internal Salesforce partner/deal Slack channels** — pre-filling POV sections and pruning the Stage 3 clarifying questions — while keeping every Slack-sourced fact **attributed, noise-filtered, and held at a distinct must-confirm trust level**.

Slack is *internal* intelligence. It tends to carry exactly the items the skill otherwise has to ask the user in Stage 3: the named exec sponsor, the pilot customer, the commercial model, stakeholder needs, the real blocker, and timeline/next-steps. The feature's payoff is to surface those internal-only facts so they both **pre-fill the draft** and **shrink/sharpen the question set**.

**Target source (locked):** internal Salesforce Slack, scoped to specific partner/deal channels, noise filtered. NOT partner Slack Connect, NOT community/ecosystem channels.

---

## 2. Architecture & file structure

Follows the skill's established pattern: **thin hooks in the always-loaded `SKILL.md`, all real logic in a lazily-loaded reference** (mirrors `refs/industry-alignment.md`, `refs/pull-through-gtm.md`).

| File | Change |
|---|---|
| **`refs/slack-insights.md`** (new) | Owns all Slack logic: config read, capability check + fallback, channel discovery/ranking, the consent gate, extraction schema, attribution format, confidence tiers, noise rules, narrative synthesis, Stage 3 reconciliation, and the Research Provenance entry format. Loaded only when Slack is in play. |
| **`SKILL.md`** (edit) | Three thin hooks (Stage 1 tooling check, Stage 2 pre-fill label, Stage 3 reconciliation + relaxed question target). No Slack logic inlined. |
| **`refs/stages/stage-12-partner-readiness-scorecard.md`** (edit) | One-line fast-follow note only. No v1 behavior change. |
| **`README.md`** (edit) | Document the opt-in capability, the MCP-vs-paste split, the confirm-before-read gate, the `[slack]` config schema, and the `settings.json` connection setup. |

**Opt-in trigger.** Slack ingestion never runs automatically. It activates only when (a) the user names a channel, or (b) a Slack tool is present and the user confirms a discovered channel. No channel + no tool → the skill behaves exactly as today. The default Quick POV path is unchanged.

---

## 3. Configuration (set once, read every run)

> **Amendment (2026-06-02, post-implementation):** §3 originally specified the `slack` defaults block living in `settings.json`. During wire-up this proved **wrong** — the Claude Code harness validates `settings.json` against a strict schema and rejects an unknown top-level `slack` key (despite the published schema showing `additionalProperties: {}`). **Corrected design:** the MCP *connection* is registered normally (`claude mcp add` / `.mcp.json`, harness-managed); the skill's *defaults block* lives in a dedicated file, **`~/.claude/pov-builder-slack.json`**, read directly by the skill. The subsections below retain their original `settings.json` wording for historical record; the shipped skill (ref §1, SKILL.md hook, README) reflects the corrected `pov-builder-slack.json` location.

A dedicated Org62-linked Slack connection is the happy path. Config turns "discover the tool each run" into "we already know the tool; just use it." **Config is an accelerator, not a requirement** — the feature works with zero config.

### 3.1 One config surface, two concerns
Both live in **`settings.json`** (the single config surface — no second config file):
1. **The tool connection** — the Slack MCP server/tool wiring. Harness territory; the `update-config` skill owns this. The skill *reads* whether the configured tool is available; it does not manage the connection.
2. **A `slack` defaults block** (§3.2) — read by the skill at Stage 1 to know the tool name, workspace, conventions, and window. The **README documents this schema** (canonical reference), but the skill reads the values from `settings.json`, not from the README.

If no `slack` block is present, the skill uses built-in defaults (`read_window_days: 90`, the conventions baked into the ref) and falls back to a blind capability probe — see §3.3.

### 3.2 `slack` defaults schema (read from `settings.json`)
- `tool_name` — name of the connected Slack MCP tool, so the Stage 1 check is a *confirmation* ("is the configured tool present?") not a blind probe.
- `workspace` — the Org62-linked workspace/team, so discovery searches the right place.
- `channel_conventions` — list of the team's naming patterns (`#partner-*`, `#*-deal`, account-named). Promoted from hardcoded guesses to configured input; directly improves Medium/High ranking quality.
- `read_window_days` — default `90`, overridable.

### 3.3 Degradation matrix
| State | Behavior |
|---|---|
| Configured + tool present | Fast path: confirm tool → discover channels → consent gate → read. |
| Configured + tool absent (headless, connection down) | Fall back to paste/export, note it, proceed. Never stall. |
| Not configured | Today's behavior: blind capability probe → discover-or-fallback. |

**Consent boundary:** config tells the skill *which workspace and conventions* — it does **not** pre-authorize reading any specific channel. The confirm-before-read gate (§4.3) stays even when fully configured.

### 3.4 README must document `settings.json` setup
The README section includes:
- How to register the Slack MCP server/tool in `settings.json` (pointer to the `update-config` skill for the actual wiring).
- How the `settings.json` connection and the `slack` defaults block relate (both in `settings.json`; connection = wiring, block = skill-read values).
- A worked example of a populated `slack` block.
- An explicit note that the connection is harness-managed and the skill only reads availability.

---

## 4. Channel discovery & consent

### 4.1 Capability check (Stage 1, silent)
Mirrors the existing WebSearch-vs-WebFetch resolution. Probe for / confirm a Slack MCP tool (list/search/history capability).
- **Tool present** → discovery path (§4.2).
- **No tool** → fallback: note Slack enrichment is available via export; proceed without stalling. If the user later pastes an export or names a file, extract from that.

### 4.2 Discover & rank (MCP-only)
List/search workspace channels; score each candidate against partner identity (name, slug, known aliases) and configured `channel_conventions`. Assign a confidence tier:
- **High** — partner name/slug in channel name, and active.
- **Medium** — convention match, OR partner name in topic/purpose, OR name match but dormant.
- **Low** — weak keyword-only. **Dropped from the suggestion list.**

Ranking signals: name match (strongest) > convention match > recency/activity > membership/topic hints.

### 4.3 Present the shortlist (HARD GATE, every time)
Present **only Medium + High** candidates, **target 3–6**, as a multi-select. Each shows its tier + a one-line "why it matched" (e.g. `#particle-health-deal — High — name match, active this week`). User selects which to pull; **the skill never reads a discovered channel without an explicit pick.**
- If more than 6 Medium+High matches: **cap at top 6 by confidence and disclose the count** ("showing top 6 of 9 matches — name a channel directly if the one you want isn't here").
- If discovery finds nothing Medium+: say so plainly and invite the user to name a channel.

**Direct naming bypasses discovery.** Naming a channel *is* the consent, so the skill reads it directly (no shortlist needed).

### 4.4 Read
Fetch recent message history from each confirmed channel. Default window **90 days** (from `read_window_days`), overridable. Hand off to extraction (§5).

---

## 5. Extraction, attribution & confidence

### 5.1 Bucketed extraction (the noise filter)
Extract only facts that map to a POV-relevant bucket. Everything else (banter, scheduling, decision-free threads) is dropped.

| Bucket | Feeds POV section |
|---|---|
| Exec sponsor (named champion, either side) | Solution Alignment / Provenance (Scorecard later) |
| Pilot / design partner (named customer for the SF motion) | Target Markets |
| Commercial model (app type, licensing, PADA status) | ISV Commercial Model |
| Stakeholder needs (Product / Advisory / Sales asks) | Solution Alignment |
| Blocker / risk (the real reason a thing is stuck) | Problem Space → Risks |
| Proof point (named account, traction, outcome) | Solution / Target Markets |
| Timeline / next-steps (target dates, meetings, milestones) | MVP & Roadmap / TBD owner-and-date fields |

### 5.2 Per-fact attribution
Every extracted fact rides with a compact source tag: **`@author, MMM DD`** (e.g. `@jane.doe, May 28`). Multiple corroborating messages → cite the most authoritative/recent, note "+N more." Makes each fact traceable and verifiable.

### 5.3 Confidence tiers (Slack gets its own)
Trust ordering:
1. `[confirmed from research]` — partner's own public source.
2. **`[from internal Slack — confirm]`** — a colleague said it internally; high *value*, unconfirmed *certainty*. **Never hardens to "confirmed" without partner confirmation.**
3. `[proposed — confirm]` — model inference.

### 5.4 Conflict handling
When Slack contradicts web research, **surface both with their tags rather than silently picking**, and route the conflict into a Stage 3 question. Slack does not overwrite a confirmed public fact; it flags the discrepancy.

### 5.5 Channel narrative (sentiment synthesis)
Beyond the discrete buckets, produce **one short narrative paragraph (2–4 sentences)** synthesizing broad sentiment across the selected channels — is the deal energized or stalling, is the partner responsive or going quiet, where's the friction, what's the momentum.
- **Placement:** the **Confidence & Assumptions** section — because sentiment is a confidence signal (an energized channel raises real confidence; a going-quiet channel should lower it), placing it next to the 0.0–1.0 score lets it visibly inform that number.
- **Framing label:** `[internal Slack sentiment — not partner-confirmed]`. Never a basis for a hardened POV assertion on its own; it is advisor context.
- **Basis attribution:** notes its sample (e.g. "synthesized from 14 messages across #particle-health-deal, May–Jun") so it stays auditable. No per-fact `@author` tags (it is a synthesis).

---

## 6. Stage 2 pre-fill & Stage 3 pruning

### 6.1 Stage 2 (pre-fill)
Slack-extracted facts populate their mapped POV sections alongside web research, each carrying `[from internal Slack — confirm]` + `@author, date`. The narrative drops into Confidence & Assumptions. Where Slack and web agree → fact shown once, both noted. Where they conflict → both shown with tags (§5.4).

### 6.2 Stage 3 (pruning — the core payoff)
Before asking clarifying questions, reconcile the question list against what Slack answered:
- **Supplied** → suppress the question; the answer flows into the draft as `[from internal Slack — confirm]` (the tag means the user still eyeballs it, but it is no longer an active question).
- **Partial** → narrow to the residual ("Slack names Jane as sponsor — is the PADA actually signed?").
- **Conflict** → convert to a question ("Web suggests X, Slack says Y — which holds?").
- **Untouched** → ask as today.

### 6.3 Relaxed question target
- The hard **≤5 guidance is relaxed to a soft target of ~5–8** when genuine gaps remain. Better to ask one more than ship a closable TBD.
- Slack's job is to **remove answerable questions** so the asked questions are the true remaining gaps.
- If real gaps still exceed the old cap after pruning, **ask them anyway (up to ~8)** rather than dropping gaps to hit a number. Still no padding (nothing research/Slack/vertical-file already covers).
- Still **one batched `AskUserQuestion` pass**, still capturing named entities in that pass. (`AskUserQuestion` allows multiple questions per call; ≤4 options each — 5–8 questions in one batch is fine.)
- Make pruning **visible**: e.g. "4 gaps pre-answered from #particle-health-deal; 6 genuine gaps remain — answering them now closes the POV's TBDs."

---

## 7. SKILL.md hooks (thin — all weight stays in the ref)

- **Stage 1 tooling check** → add Slack to the existing capability probe: read `[slack]` config; confirm/detect the tool; if present, run discovery (load `refs/slack-insights.md`); if a channel is named directly, load the ref regardless. No channel + no tool → unchanged.
- **Stage 2** → one line: Slack-sourced pre-fills carry `[from internal Slack — confirm]` with `@author, date`.
- **Stage 3** → one line: reconcile the question list against Slack findings first (suppress/narrow/convert); relax hard ≤5 to a ~5–8 soft target driven by real gaps.

---

## 8. Research Provenance entry (the "C" in A+C scope)

When Slack is read, Provenance logs an auditable record:
- Channels read + confidence tier each (`#particle-health-deal — High`).
- Read window (default 90 days) and message counts.
- The attributed facts pulled, by bucket.
- Discovery disclosure if truncated ("top 6 of 9 shown").
- A note that the narrative was produced (the narrative text itself lives in Confidence & Assumptions, §5.5).

---

## 9. Scorecard fast-follow (documentation only — NOT v1 behavior)

Add a one-line note to `refs/stages/stage-12-partner-readiness-scorecard.md`: *Slack evidence can drive the Executive Sponsor, Executive Engagement, and Partner's Technical Engagement attributes — planned fast-follow, not wired in v1.* Preserves the idea without scope-creeping the build.

---

## 10. Out of scope for v1 (explicit)

- Scorecard wiring (documented fast-follow only).
- Slack feeding downstream artifacts beyond what they inherit from the approved POV.
- Writing *back* to Slack.
- Non-partner / community / Slack-Connect channel ingestion.
- Managing the Slack connection itself (harness/`settings.json` territory).

---

## 11. Success criteria

1. With a configured + connected Slack tool, the skill discovers partner/deal channels, presents a 3–6 Medium+High shortlist, reads only on explicit pick, and never stalls when the tool is absent.
2. Extracted facts appear in the right POV sections with `@author, date` attribution and the `[from internal Slack — confirm]` tier; none harden to confirmed without partner confirmation.
3. Stage 3 visibly suppresses/narrows questions Slack answered; remaining questions are genuine gaps (~5–8 allowed).
4. A channel narrative appears in Confidence & Assumptions, basis-attributed, influencing the confidence score.
5. Research Provenance records the channels, window, and attributed facts.
6. With no config and no tool, skill behavior is identical to today.
7. SKILL.md base context grows only by the three thin hooks; all substantive logic is in the lazily-loaded ref.
8. README documents the `[slack]` schema and the `settings.json` connection setup.
