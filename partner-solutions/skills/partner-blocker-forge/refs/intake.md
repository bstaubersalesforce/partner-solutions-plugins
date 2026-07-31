# refs/intake.md — parse the inputs, gap-check, proceed

## Expected inputs (minimum)

1. **The ask** — content outlining what's needed (a thread summary, a note, a request).
2. **Partner name.**
3. **≥1 support case** — a case number or a record ID (or a link containing one).
4. **A Slack thread** — channel + message, or pasted content.

## Access preflight (run first — sets what the run can actually verify)

Before investigating, check tool/access availability and **record the result** — it determines which source
classes are reachable and whether degraded mode applies (refs/investigate-snippets.md):
- **Org access:** `sf org display -o <org>` succeeds? If not, you **cannot** pull cases/comments — every
  case-derived claim is `UNVERIFIED`, and the case-pull script will fail. Don't fake it.
- **Slack access:** can you read the named channel/thread? If not, note it — claims resting on the thread are
  unconfirmed.
- **Web/docs research:** available? If not, primary-doc + release-note + Known-Issues verification can't run.

**Degraded mode (any source unreachable):** proceed with what's available, but the doc **visibly downgrades**
every claim that couldn't be checked to `UNVERIFIED — no primary source checked`, the verdict states which
classes were/weren't checked, and the **partner-facing doc is blocked** until at least primary-doc + case classes
are covered. Fail *loud*, not silent — never emit a confident doc off sources you couldn't reach.

## Steps

1. **Confirm what's present; flag gaps — but proceed anyway.** Missing pieces don't block. State plainly what
   you have and what's absent (e.g. "no Slack thread provided — working from the case + note"). Combine with the
   preflight result: "no org auth → cases UNVERIFIED" is a gap that changes the output, not just a note.
2. **Resolve case identifiers.** A number → query by `CaseNumber`. A record ID (`500…`) or a Lightning link →
   query by `Id`. If a cited "old case number" returns nothing, resolve via the record ID/link — partners often
   quote a legacy number that differs from the CaseNumber (see refs/investigate-snippets.md).
3. **Read the Slack thread** (if provided) for: the partner's stated claims, the emotional/persuasive framing
   (feeds refs/adversarial.md Step 2), any embedded case links/IDs, and who's involved (PSM / PIE / account team)
   for later routing.
4. **Extract the distinct claims.** Separate what the partner asserts into discrete claims — each will be
   classified in triage. Split compound claims ("retrievers excluded, so prompt templates can't package either")
   into their parts.
5. **Note the requested output** — internal only (default), or internal + partner-facing (ask if unstated;
   partner-facing is produced on request per SKILL.md).

Hand off to refs/triage.md with: the claim list, the case identifier(s), the thread context, and the gap list.
