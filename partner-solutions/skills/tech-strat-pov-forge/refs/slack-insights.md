# Slack Insights Reference

> Lazily loaded. Load this only when Slack enrichment is in play — i.e. the user named a partner/deal channel, OR a Slack tool is configured/present and the partner has a plausible channel. If no channel is named and no Slack tool is available, do not load this file; the POV flow is unchanged.

This file owns all Slack-insight logic. `SKILL.md` carries only thin hooks (Stage 1 tooling check, Stage 2 label, Stage 3 reconciliation). Slack is **internal Salesforce intelligence** — scoped to named partner/deal channels — used to pre-fill the POV and prune Stage 3 questions. It is never read without explicit user consent.

## Source scope (fixed)

Internal Salesforce Slack, partner/deal channels only. NOT partner Slack Connect, NOT community/ecosystem channels. Those are out of scope.

## 1. Configuration (read from ~/.claude/tech-strat-pov-forge-slack.json)

Two separate concerns, two separate homes:
- **The Slack MCP tool connection** is harness-managed — registered via `claude mcp add` / `.mcp.json` (owned by the `update-config` skill). The skill does not manage it; it only *detects* whether the configured tool is present.
- **The skill's defaults** live in a dedicated file, **`~/.claude/tech-strat-pov-forge-slack.json`** — NOT in `settings.json` (the harness validates `settings.json` against a strict schema and rejects an unknown `slack` key). Read this file directly at Stage 1.

The `tech-strat-pov-forge-slack.json` file is shaped like this:

```json
{
  "tool_name": "slack",
  "workspace": "salesforce-org62",
  "channel_conventions": ["#partner-*", "#*-partnership", "#gp-*", "#isv-*"],
  "read_window_days": 90
}
```

- `tool_name` — name of the connected Slack MCP tool. Lets the Stage 1 capability check be a *confirmation* ("is the configured tool present?") rather than a blind probe.
- `workspace` — the Org62-linked workspace, so discovery searches the right place.
- `channel_conventions` — the team's channel naming patterns; feeds discovery ranking (§3).
- `read_window_days` — history window to read. **Default 90** when absent.

If `~/.claude/tech-strat-pov-forge-slack.json` does not exist: use built-in defaults (`read_window_days` = 90; conventions `#partner-*`, `#*-deal`) and fall back to a blind capability probe (§2). The feature works with zero config — config only makes it faster and sharper.

## 2. Capability check (Stage 1, silent)

Mirrors the existing WebSearch-vs-WebFetch resolution. Confirm/detect a Slack MCP tool (list/search/history capability):
- **Tool present** → discovery path (§3).
- **No tool** → **fallback**: note that Slack enrichment is available via **export** (the user can paste channel text or point to an export file), then proceed without stalling. If the user later supplies an export, extract from it via §6 (skip discovery — there is nothing to enumerate).

This is a capability check, not a permission prompt. Resolve it and proceed in the same turn.

## 3. Channel discovery & ranking (MCP-only)

Discovery requires a tool that can list/search channels, so it is **MCP-only**. In the export fallback there is nothing to enumerate — the user names or pastes the channel directly.

List/search workspace channels; score each candidate against the partner identity (name, slug, known aliases) and the configured `channel_conventions`. Assign a confidence tier:
- **High** — partner name/slug in the channel name, and active.
- **Medium** — convention match, OR partner name in topic/purpose, OR name match but dormant.
- **Low** — weak keyword-only. **Dropped from the suggestion list.**

Ranking signal strength: name match > convention match > recency/activity > membership/topic hints.

## 4. Consent gate — present the shortlist (HARD GATE, every time)

Present **only Medium + High** candidates, **target 3–6**, via `AskUserQuestion` (multi-select). Each option shows its tier and a one-line "why it matched", e.g. `#particle-health-deal — High — name match, active this week`.

- **Mind the tool's 4-option-per-question cap.** `AskUserQuestion` renders at most **4 options per question**. With 1–4 candidates, present them as one multi-select question. With 5–6, split across **two** questions in the **same** `AskUserQuestion` call (e.g. "Top channels (1 of 2)" / "More channels (2 of 2)"), highest-confidence first — never silently truncate to 4. Multi-select lets the user pick across both.
- The skill **never reads a discovered channel without an explicit pick** (confirm-before-read).
- More than 6 Medium+High matches → **cap at the top 6 by confidence and disclose**: "showing top 6 of 9 matches — name a channel directly if the one you want isn't here." (The 6 still render across two questions per the cap above.)
- Nothing Medium+ found → say so plainly and invite the user to name a channel.
- **Direct naming bypasses discovery** — naming a channel *is* the consent, so read it directly. Config never pre-authorizes reading a specific channel; it only supplies workspace + conventions.

## 5. Read

Fetch recent message history from each confirmed channel. Window = `read_window_days` (default **90**), overridable if the user asks. Hand off to extraction (§6).

## 6. Extraction, attribution & confidence

### 6.1 Bucketed extraction (the noise filter)

Extract only facts that map to a bucket below. Drop everything else (banter, scheduling, decision-free threads) — that is the noise filter.

| Bucket | Feeds POV section |
|---|---|
| Exec sponsor (named champion, either side) | Solution Alignment / Provenance |
| Pilot / design partner (named customer for the SF motion) | Target Markets |
| Commercial model (app type, licensing, PADA status) | ISV Commercial Model |
| Stakeholder needs (Product / Advisory / Sales asks) | Solution Alignment |
| Blocker / risk (the real reason a thing is stuck) | Problem Space → Risks |
| Proof point (named account, traction, outcome) | Solution / Target Markets |
| Timeline / next-steps (target dates, meetings, milestones) | MVP & Development Priorities / TBD owner-and-date fields |

### 6.2 Per-fact attribution

Every extracted fact rides with a compact tag: **`@author, MMM DD`** (e.g. `@jane.doe, May 28`). Multiple corroborating messages → cite the most authoritative/recent and note "+N more."

### 6.3 Confidence tiers

Trust ordering — Slack gets its own tier:
1. `[confirmed from research]` — partner's own public source.
2. **`[from internal Slack — confirm]`** — a colleague said it internally; high value, unconfirmed certainty. **Never hardens to "confirmed" without partner confirmation.**
3. `[proposed — confirm]` — model inference.

### 6.4 Conflict handling

When Slack contradicts web research, **surface both with their tags rather than silently picking**, and route the conflict into a Stage 3 question. Slack never overwrites a confirmed public fact; it flags the discrepancy.

### 6.5 Channel narrative (sentiment synthesis)

Produce **one short paragraph (2–4 sentences)** synthesizing broad sentiment across the selected channels — is the deal energized or stalling, is the partner responsive or going quiet, where is the friction, what is the momentum.
- **Placement:** the POV's **Confidence & Assumptions** section — sentiment is a confidence signal, so it sits next to the 0.0–1.0 score and visibly informs it (energized channel → supports confidence; going quiet → lowers it).
- **Label:** `[internal Slack sentiment — not partner-confirmed]`. Never a standalone basis for a hardened assertion; it is advisor context.
- **Basis attribution:** note the sample, e.g. "synthesized from 14 messages across #particle-health-deal, May–Jun." No per-fact `@author` tags (it is a synthesis).

## 7. Stage 2 pre-fill

Slack facts populate their mapped POV sections alongside web research, each carrying `[from internal Slack — confirm]` + `@author, date`. The narrative drops into Confidence & Assumptions. Agreement with web → show once, note both. Conflict → show both with tags (§6.4).

## 8. Stage 3 reconciliation (the core payoff)

Before asking the clarifying questions, reconcile the question list against what Slack answered:
- **Supplied** → suppress the question; the answer flows into the draft as `[from internal Slack — confirm]` (still eyeballed via the tag, but no longer an active question).
- **Partial** → narrow to the residual ("Slack names Jane as sponsor — is the PADA actually signed?").
- **Conflict** → convert to a question ("Web suggests X, Slack says Y — which holds?").
- **Untouched** → ask as today.

Question target is relaxed from the hard ≤5 to a **soft ~5–8** when genuine gaps remain — better to close a TBD now than ship it. Slack removes answerable questions so the asked ones are true gaps. Still one batched `AskUserQuestion` pass; still capture named entities in that pass. Make the pruning visible, e.g. "4 gaps pre-answered from #particle-health-deal; 6 genuine gaps remain."

## 9. Research Provenance entry

When Slack is read, record in the POV's Research Provenance section:
- Channels read + confidence tier each (`#particle-health-deal — High`).
- Read window (default 90 days) and message counts.
- The attributed facts pulled, by bucket.
- Discovery disclosure if truncated ("top 6 of 9 shown").
- A note that the narrative was produced (the narrative text itself lives in Confidence & Assumptions, §6.5).
