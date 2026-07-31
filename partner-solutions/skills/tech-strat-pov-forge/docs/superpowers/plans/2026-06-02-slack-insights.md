# Slack Insights Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in capability that ingests internal Salesforce partner/deal Slack channels to pre-fill the POV and prune Stage 3 clarifying questions, with attributed facts, a dedicated confidence tier, a sentiment narrative, and auditable provenance.

**Architecture:** All Slack logic lives in a new lazily-loaded `refs/slack-insights.md`; `SKILL.md` gets only three thin hooks so base context stays lean. Config (tool name + defaults) is read from `settings.json`. The skill's "tests" are `@check`-decorated structural invariants in `tests/validate_skill.py`, run by the pre-commit hook — each task adds checks there first (watch FAIL), then makes the edit (watch PASS).

**Tech Stack:** Markdown instruction files; Python 3 validation harness (`tests/validate_skill.py`, a `@check("name")` registry); git pre-commit hook runs the suite.

---

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `refs/slack-insights.md` | All Slack logic: config read, capability check + fallback, channel discovery/ranking, consent gate, 7-bucket extraction schema, attribution format, confidence tiers, conflict handling, narrative synthesis, Stage 3 reconciliation, provenance entry format | Create |
| `SKILL.md` | Three thin hooks: Stage 1 tooling check, Stage 2 pre-fill label, Stage 3 reconciliation + relaxed ~5–8 target | Modify |
| `refs/stages/stage-12-partner-readiness-scorecard.md` | One-line fast-follow note (no v1 behavior change) | Modify |
| `README.md` | Document the opt-in capability, MCP-vs-paste split, consent gate, `slack` config schema, and `settings.json` connection setup | Modify |
| `tests/validate_skill.py` | New `@check` invariants guarding all of the above | Modify |

**Build order rationale:** The validation harness checks that *every referenced path exists* and *every ref file is referenced by the instructions (no orphans)*. So `refs/slack-insights.md` and the `SKILL.md` hook that references it must land **in the same commit** or the existing suite breaks. Tasks 1–2 are therefore committed together; Task 1 creates the file and its checks, Task 2 adds the referencing hook, and the commit happens at the end of Task 2.

---

## Task 1: Create `refs/slack-insights.md` and its content checks

**Files:**
- Create: `refs/slack-insights.md`
- Modify: `tests/validate_skill.py` (add checks; do not commit yet)

- [ ] **Step 1: Write the failing checks**

Add this block to `tests/validate_skill.py` immediately before the `# ---- runner` section (the line starting `def main():`). It defines a helper to read the new ref and a set of content invariants.

```python
# ---- 9. Slack insights -------------------------------------------------
SLACK_REF = "refs/slack-insights.md"

@check("Slack insights ref file exists")
def t_slack_ref_exists():
    assert exists(SLACK_REF), f"{SLACK_REF} is missing"

@check("Slack ref defines the seven extraction buckets")
def t_slack_buckets():
    txt = read(SLACK_REF).lower()
    buckets = ["exec sponsor", "pilot", "commercial model",
               "stakeholder needs", "blocker", "proof point", "timeline"]
    missing = [b for b in buckets if b not in txt]
    assert not missing, f"buckets missing from slack ref: {missing}"

@check("Slack ref defines the Slack-specific confidence + sentiment labels")
def t_slack_labels():
    txt = read(SLACK_REF)
    assert "[from internal Slack — confirm]" in txt, "missing fact confidence tier label"
    assert "[internal Slack sentiment — not partner-confirmed]" in txt, "missing sentiment label"

@check("Slack ref defines capability check, fallback, and MCP-only discovery")
def t_slack_capability():
    txt = read(SLACK_REF).lower()
    assert "capability check" in txt, "missing capability check"
    assert "fallback" in txt and "export" in txt, "missing paste/export fallback"
    assert "mcp-only" in txt or "mcp only" in txt, "discovery must be flagged MCP-only"

@check("Slack ref defines the confirm-before-read gate and 3-6 Medium+High shortlist")
def t_slack_gate():
    txt = read(SLACK_REF).lower()
    assert "confirm-before-read" in txt or "confirm before read" in txt, "missing consent gate"
    assert "medium" in txt and "high" in txt, "missing Medium+High tiers"
    assert "top 6" in txt or "3-6" in txt or "3–6" in txt, "missing 3-6 shortlist cap"

@check("Slack ref reads config from settings.json with a 90-day default window")
def t_slack_config():
    txt = read(SLACK_REF)
    assert "settings.json" in txt, "must read config from settings.json"
    assert "read_window_days" in txt, "missing read_window_days key"
    assert "90" in txt, "missing 90-day default"
```

- [ ] **Step 2: Run the checks to verify they fail**

Run: `python3 tests/validate_skill.py 2>&1 | grep -i slack`
Expected: every Slack check prints `FAIL` (the ref file does not exist yet), e.g.
`FAIL  Slack insights ref file exists  → refs/slack-insights.md is missing`

- [ ] **Step 3: Create the ref file with the full Slack logic**

Create `refs/slack-insights.md` with exactly this content:

````markdown
# Slack Insights Reference

> Lazily loaded. Load this only when Slack enrichment is in play — i.e. the user named a partner/deal channel, OR a Slack tool is configured/present and the partner has a plausible channel. If no channel is named and no Slack tool is available, do not load this file; the POV flow is unchanged.

This file owns all Slack-insight logic. `SKILL.md` carries only thin hooks (Stage 1 tooling check, Stage 2 label, Stage 3 reconciliation). Slack is **internal Salesforce intelligence** — scoped to named partner/deal channels — used to pre-fill the POV and prune Stage 3 questions. It is never read without explicit user consent.

## Source scope (fixed)

Internal Salesforce Slack, partner/deal channels only. NOT partner Slack Connect, NOT community/ecosystem channels. Those are out of scope.

## 1. Configuration (read from settings.json)

Both the tool connection and the skill's defaults live in **`settings.json`** — one config surface, no second file. The skill *reads* config; it does not manage the connection (that is harness territory, owned by the `update-config` skill).

Read a `slack` defaults block shaped like this:

```json
{
  "slack": {
    "tool_name": "slack",
    "workspace": "salesforce-org62",
    "channel_conventions": ["#partner-*", "#*-deal", "#*-partnership"],
    "read_window_days": 90
  }
}
```

- `tool_name` — name of the connected Slack MCP tool. Lets the Stage 1 capability check be a *confirmation* ("is the configured tool present?") rather than a blind probe.
- `workspace` — the Org62-linked workspace, so discovery searches the right place.
- `channel_conventions` — the team's channel naming patterns; feeds discovery ranking (§3).
- `read_window_days` — history window to read. **Default 90** when absent.

If no `slack` block exists: use built-in defaults (`read_window_days` = 90; conventions `#partner-*`, `#*-deal`) and fall back to a blind capability probe (§2). The feature works with zero config — config only makes it faster and sharper.

## 2. Capability check (Stage 1, silent)

Mirrors the existing WebSearch-vs-WebFetch resolution. Confirm/detect a Slack MCP tool (list/search/history capability):
- **Tool present** → discovery path (§3).
- **No tool** → **fallback**: note that Slack enrichment is available via **export** (the user can paste channel text or point to an export file), then proceed without stalling. If the user later supplies an export, extract from it via §4 (skip discovery — there is nothing to enumerate).

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

- The skill **never reads a discovered channel without an explicit pick** (confirm-before-read).
- More than 6 Medium+High matches → **cap at the top 6 by confidence and disclose**: "showing top 6 of 9 matches — name a channel directly if the one you want isn't here."
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
| Timeline / next-steps (target dates, meetings, milestones) | MVP & Roadmap / TBD owner-and-date fields |

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
````

- [ ] **Step 4: Run the checks to verify they pass**

Run: `python3 tests/validate_skill.py 2>&1 | grep -i slack`
Expected: every Slack check prints `PASS`. (The existing "no orphans" check will still FAIL here — that is expected and fixed in Task 2, which is why these two tasks share one commit. Do **not** commit yet.)

---

## Task 2: Add the three SKILL.md hooks and commit Tasks 1+2

**Files:**
- Modify: `SKILL.md` (Stage 1 tooling check, Stage 2, Stage 3)
- Modify: `tests/validate_skill.py` (add hook-presence check)

- [ ] **Step 1: Write the failing check**

Add to `tests/validate_skill.py`, directly after the `t_slack_config` function from Task 1:

```python
@check("SKILL.md carries the three thin Slack hooks and references the ref")
def t_slack_hooks_in_skill():
    skill = read("SKILL.md")
    assert "refs/slack-insights.md" in skill, "SKILL.md must reference the Slack ref"
    assert "[from internal Slack — confirm]" in skill, "Stage 2 hook label missing"
    low = skill.lower()
    assert "slack" in low and "reconcile" in low, "Stage 3 reconciliation hook missing"
    assert "5–8" in skill or "5-8" in skill or "~5" in skill, "relaxed 5-8 question target missing"
```

- [ ] **Step 2: Run the check to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep "three thin Slack hooks"`
Expected: `FAIL  SKILL.md carries the three thin Slack hooks ...  → SKILL.md must reference the Slack ref`

- [ ] **Step 3: Add Hook 1 — Stage 1 tooling check**

In `SKILL.md`, find the Stage 1 "Research-tooling check" paragraph (it discusses `WebSearch` vs `WebFetch`). Immediately after that paragraph's bullet list, add this paragraph:

```markdown
**Slack-tooling check (same pass, silent).** Read the `slack` config block from `settings.json` (keys: `tool_name`, `workspace`, `channel_conventions`, `read_window_days` — default 90). Then resolve Slack availability the same way you resolve web search:
- If a Slack MCP tool is configured/present **and** the partner plausibly has an internal deal channel, load `refs/slack-insights.md` and run its discovery + consent gate before Stage 2.
- If the user **names** a channel directly, load `refs/slack-insights.md` regardless of config.
- If no Slack tool is available and no channel is named, do not load the ref — the POV flow is unchanged. This is a capability check, not a permission prompt; never stall on it.
```

- [ ] **Step 4: Add Hook 2 — Stage 2 label**

In `SKILL.md`, find Stage 2's confidence-label list (the lines defining `[confirmed from research]`, `[proposed — confirm]`, `[TBD — clarification needed]`). Add this line to that list:

```markdown
- `[from internal Slack — confirm]` — sourced from an internal partner/deal Slack channel with `@author, date` attribution; high value but unconfirmed certainty — never hardens to confirmed without partner confirmation (see `refs/slack-insights.md`)
```

- [ ] **Step 5: Add Hook 3 — Stage 3 reconciliation**

In `SKILL.md`, find the **Stage 3 — Clarify** section. Immediately after its first paragraph, add:

```markdown
**Reconcile against Slack first (when `refs/slack-insights.md` was loaded).** Before asking, suppress questions Slack already answered, narrow partially-answered ones to the residual, and convert any Slack-vs-research conflict into a question. The hard ≤5 cap relaxes to a soft target of **~5–8** when genuine gaps remain — close a TBD now rather than ship it. Still one batched pass; still capture named entities in that pass. Make the pruning visible (e.g. "4 gaps pre-answered from #partner-channel; 6 genuine gaps remain").
```

- [ ] **Step 6: Run the full suite to verify all pass**

Run: `python3 tests/validate_skill.py`
Expected: final line `N/N passed` with N = previous count + 7 (six from Task 1, one from Task 2). No FAIL lines — including the "no orphans" and "referenced path exists" checks, now satisfied because SKILL.md references the ref.

- [ ] **Step 7: Commit Tasks 1 + 2 together**

```bash
git add refs/slack-insights.md SKILL.md tests/validate_skill.py
git commit -m "feat: add Slack insights ingestion (ref + SKILL.md hooks)

Lazily-loaded refs/slack-insights.md owns channel discovery, consent gate,
7-bucket extraction, the [from internal Slack — confirm] tier, sentiment
narrative, and Stage 3 reconciliation. SKILL.md gains three thin hooks.
Config read from settings.json. Guarded by 7 new validation checks.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

Expected: the pre-commit hook runs the suite and prints `N/N passed`, then the commit succeeds.

---

## Task 3: Scorecard fast-follow note (documentation only)

**Files:**
- Modify: `refs/stages/stage-12-partner-readiness-scorecard.md`
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Write the failing check**

Add to `tests/validate_skill.py`, after `t_slack_hooks_in_skill`:

```python
@check("Scorecard carries the Slack fast-follow note (documentation only)")
def t_slack_scorecard_note():
    txt = read("refs/stages/stage-12-partner-readiness-scorecard.md").lower()
    assert "slack" in txt and "fast-follow" in txt, "missing Slack fast-follow note"
    assert "not wired in v1" in txt or "not v1" in txt, "fast-follow must state it is not v1"
```

- [ ] **Step 2: Run the check to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep "fast-follow"`
Expected: `FAIL  Scorecard carries the Slack fast-follow note ...  → missing Slack fast-follow note`

- [ ] **Step 3: Add the note**

In `refs/stages/stage-12-partner-readiness-scorecard.md`, at the end of the file, add:

```markdown

---

> **Fast-follow (not wired in v1):** Slack evidence from `refs/slack-insights.md` can drive the **Executive Sponsor**, **Executive Alignment Sponsorship**, and **Partner's Technical Engagement** attributes — a named sponsor or active technical thread in a partner/deal channel is direct RAG evidence. Planned as a fast-follow; the scorecard does not consume Slack in v1.
```

- [ ] **Step 4: Run the suite to verify all pass**

Run: `python3 tests/validate_skill.py`
Expected: `N/N passed`, N = previous + 1, no FAIL lines.

- [ ] **Step 5: Commit**

```bash
git add refs/stages/stage-12-partner-readiness-scorecard.md tests/validate_skill.py
git commit -m "docs: note Slack scorecard wiring as a fast-follow (not v1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

Expected: pre-commit suite passes, commit succeeds.

---

## Task 4: README documentation (capability + settings.json setup)

**Files:**
- Modify: `README.md`
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Write the failing check**

Add to `tests/validate_skill.py`, after `t_slack_scorecard_note`:

```python
@check("README documents the Slack capability, settings.json, and the consent gate")
def t_slack_readme():
    txt = read("README.md")
    low = txt.lower()
    assert "slack" in low, "README missing Slack section"
    assert "settings.json" in txt, "README must document the settings.json connection"
    assert "read_window_days" in txt, "README must show the slack config schema"
    assert "confirm" in low and "read" in low, "README must state the confirm-before-read gate"
    assert "export" in low, "README must document the paste/export fallback"
```

- [ ] **Step 2: Run the check to verify it fails**

Run: `python3 tests/validate_skill.py 2>&1 | grep "README documents the Slack"`
Expected: `FAIL  README documents the Slack capability ...  → README missing Slack section` (or a later assertion if "slack" already appears incidentally).

- [ ] **Step 3: Add the README section**

In `README.md`, find the `## What it produces` section (the table of outputs). Immediately **before** that section's heading, insert this new section:

````markdown
## Pulling in Slack insights (optional)

The skill can enrich a POV with intelligence from **internal Salesforce partner/deal Slack channels** — pre-filling sections (exec sponsor, pilot, commercial model, blockers, timeline) and shrinking the Stage 3 questions to genuine gaps. It is **opt-in** and reads nothing without your explicit pick.

**How channels are found.** If a Slack tool is connected, during research the skill discovers candidate channels, ranks them, and presents a short **3–6 channel** shortlist (Medium + High confidence only) for you to choose from — a **confirm-before-read** gate that never reads a channel you didn't pick. You can also **name a channel directly** to skip discovery. With no Slack tool, it falls back to a **paste/export** path: point it at exported channel text.

**How facts are handled.** Each extracted fact carries `@author, date` attribution and a dedicated `[from internal Slack — confirm]` label — high value, but it never hardens into a confirmed fact without partner confirmation. A short sentiment **narrative** lands in the POV's Confidence & Assumptions, informing the confidence score. The channels read, window, and attributed facts are logged in Research Provenance.

**Connecting Slack (settings.json).** The Slack tool connection lives in `settings.json` (use the `update-config` skill to wire the MCP server). Add a `slack` defaults block the skill reads each run:

```json
{
  "slack": {
    "tool_name": "slack",
    "workspace": "salesforce-org62",
    "channel_conventions": ["#partner-*", "#*-deal", "#*-partnership"],
    "read_window_days": 90
  }
}
```

- `tool_name` — the connected Slack MCP tool's name (lets the skill confirm availability instead of blindly probing).
- `workspace` — the Org62-linked workspace discovery searches.
- `channel_conventions` — your team's channel naming patterns; improves discovery ranking.
- `read_window_days` — history window to read (default **90**).

The connection is harness-managed — the skill only reads whether the configured tool is available. With no `slack` block and no tool, behavior is identical to today.

````

- [ ] **Step 4: Run the suite to verify all pass**

Run: `python3 tests/validate_skill.py`
Expected: `N/N passed`, N = previous + 1, no FAIL lines.

- [ ] **Step 5: Commit**

```bash
git add README.md tests/validate_skill.py
git commit -m "docs: document Slack insights capability and settings.json setup

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

Expected: pre-commit suite passes, commit succeeds.

---

## Task 5: Full-suite verification

**Files:** none (verification only)

- [ ] **Step 1: Run the complete validation suite**

Run: `python3 tests/validate_skill.py`
Expected: final line `N/N passed` where N = original 47 + 9 new checks = **56/56 passed**. Zero FAIL, zero ERROR.

- [ ] **Step 2: Confirm the git log**

Run: `git log --oneline -4`
Expected: four commits in order — README docs, scorecard fast-follow, Slack ingestion (ref + hooks), and the earlier design spec.

- [ ] **Step 3: Sanity-check base-context leanness**

Run: `git show --stat HEAD~2 | grep -E "SKILL.md|slack-insights"`
Expected: `SKILL.md` shows a small insertion count (three hooks only); `refs/slack-insights.md` holds the bulk. Confirms base context stayed lean.

---

## Self-Review

**Spec coverage:**
- §2 architecture (thin hooks + lazy ref) → Tasks 1–2.
- §3 config / settings.json / `slack` block → Task 1 Step 3 (§1 of ref) + checks `t_slack_config`; README in Task 4.
- §3.3 degradation matrix → ref §2 (capability check + fallback), check `t_slack_capability`.
- §4 discovery/ranking/consent gate/3–6 cap → ref §3–§4, checks `t_slack_gate`.
- §5 extraction/attribution/tiers/conflict/narrative → ref §6, checks `t_slack_buckets`, `t_slack_labels`.
- §6 Stage 2 pre-fill + Stage 3 pruning (~5–8) → ref §7–§8 + SKILL.md hooks 2&3, check `t_slack_hooks_in_skill`.
- §7 SKILL.md hooks → Task 2.
- §8 Research Provenance entry → ref §9.
- §9 scorecard fast-follow → Task 3.
- §3.4 README settings.json → Task 4.
- §11 success criteria → Task 5 verification. All covered.

**Placeholder scan:** No TBD/TODO/"handle appropriately". Every code/content step shows full content. Pass.

**Type/name consistency:** Config keys (`tool_name`, `workspace`, `channel_conventions`, `read_window_days`) identical across ref, README, and checks. Labels `[from internal Slack — confirm]` and `[internal Slack sentiment — not partner-confirmed]` byte-identical across ref, SKILL.md hook, and checks (em-dash `—`, not hyphen). Check function names unique (`t_slack_*`). Pass.

**Ordering note:** Tasks 1 and 2 deliberately share one commit because the "no orphans" / "referenced path exists" invariants require the ref and its SKILL.md reference to land together. Verified in Task 1 Step 4 (do-not-commit) and Task 2 Step 7 (commit).
