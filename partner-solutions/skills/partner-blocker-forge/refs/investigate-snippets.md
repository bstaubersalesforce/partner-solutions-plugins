# refs/investigate-snippets.md — ready-to-run investigation assets

Verify claims against **four source classes**. Not docs alone.

**On "mandatory" vs. availability (resolving the contradiction):** the four classes are the *required verification
standard* for any claim stated at Med/High confidence in a **deep-dive** or **partner-facing** doc. They are not a
promise that every source is reachable on every run. When a source is unavailable (no org auth, unreadable channel,
unreleased capability no doc covers), you do **not** silently proceed as if verified — you enter **degraded mode**:
every unchecked claim is tagged **`UNVERIFIED — no primary source checked`** (not "Low confidence"), the doc's
verdict says which sources were and weren't checked, and the **partner-facing doc is blocked** until at least the
primary-doc + case classes are covered. Triage may run on fewer sources by design (see refs/triage.md) — but a
triage-only doc is stamped as such and may not carry Med/High confidence.

## The four source classes (mandatory breadth)

1. **Primary product/packaging docs** — `developer.salesforce.com` (2GP `pkg2_dev`, Data Kits, Package
   Ancestors, packageable Agentforce metadata, extensibility/readiness matrices), `help.salesforce.com`.
   *(help.salesforce.com is often JS-rendered/unreadable by fetch — fall back to developer.salesforce.com +
   release notes, and say so.)*
2. **Known Issues + precedent** — is this a logged/known defect (`issues.salesforce.com` / Trailblazer)? And has
   this blocker been **solved before for another partner**? Search cases/docs for a **precedent resolution** — a
   prior partner who hit the same wall and how it was cleared (a precedent case — e.g. one partner's 1GP→2GP
   precedent case). A precedent is often the fastest route to the fix + the routing.
3. **Case resolutions + comment threads — READ THE COMMENTS, not just the record.** The Case record's Status/
   Subject/Description tells you almost nothing about *why*; the **CaseComment thread** is where support/R&D state
   what they found — bug vs. workaround vs. config, and whether a **root cause was given** or it was "check and
   see." Reading a case record without its comments is the same shallow mistake as noting a Slack reply-count
   without opening the thread. In deep-dive, comment threads are read **in full** (resolution tail especially).
4. **Release notes** — did platform behavior change under the partner? The **"it worked before"** signal is the
   tell (e.g. a Flex Template rejecting a ContentDocument ID that previously worked). Search
   "<feature> release notes Winter/Spring/Summer '<yy>".

## Pull the cases (sf CLI, against the support org — usually `org62`)

**Caveats learned in practice:**
- `Product_Area__c` does **not** exist on `Case` — don't select it.
- For large `--json` results, write to a file then parse — inline parsing of big payloads truncates.
- Query by **`Id`** when given a record ID (`500…`); by **`CaseNumber`** otherwise. (A partner's "old case
  number" may differ from the CaseNumber — resolve via the record ID/link if the number returns nothing.)

### 🔎 Resolving a partner-cited number (do this FIRST — it bit every real dogfood)

Partners quote all sorts of identifiers; most are **not** the `CaseNumber` you query by. Work this ladder until a
record resolves — don't give up when the first query returns 0 rows:

1. **Try it as a `CaseNumber`** (`WHERE CaseNumber='<n>'`). Modern numbers (`67…`, `62…`) usually resolve here.
2. **Legacy/display number** (often `473…`, `474…`, `255…`): these are **NOT** CaseNumbers. Resolve by:
   - **Account + subject keyword** — `WHERE Account.Name LIKE '%<Partner>%' AND Subject LIKE '%<distinctive phrase>%'`
     (the partner's issue description usually names the symptom). This is the reliable fallback.
   - a **parenthetical alt-ID** the partner pasted (e.g. `(255979698)`) — try it as CaseNumber too; sometimes it's
     the real one and the leading number is the legacy display ID.
3. **A Lightning record-ID / link:**
   - **`500…`** = the Case itself → `WHERE Id='500…'`.
   - **`0D5…`** = a **FeedItem** (a Chatter/CaseCommentPost, e.g. a "voice of customer" post) — its `Body` is often
     null; the real content is on the parent case. Hop via its parent:
     `SELECT ParentId, Type FROM FeedItem WHERE Id='0D5…'` → then query the Case by that `ParentId`.
   - **`00a…`** = a CaseComment; **`aDG…`/`a…`** = a custom object (e.g. a Security_Review__c record) — query that
     sObject by `Id` directly.
4. **Record the mapping in the doc** (`<partner-cited number> → CaseNumber <real>`) so the Sources list is
   traceable and the same number isn't re-resolved next session.

> Prefix cheat-sheet: `500`=Case · `0D5`=FeedItem · `00a`=CaseComment · `a…`=custom object. When a number returns
> nothing, it's almost always a legacy display number → fall back to **account + subject keyword**.

**Fastest path — the helper script** (`scripts/pull_cases.sh`): pulls records **and** comment tails to a
`.notes/` file in one call, handling case-numbers and record-IDs, with the field caveats baked in:
```bash
scripts/pull_cases.sh --org org62 --out .notes/cases.md 66996591 66716628 500ed00000tXs6oAAC
```
Output is **raw sensitive capture → `.notes/` only**; run `scripts/scrub_check.py` before any doc is shared.

**Or the raw queries — case summary (records):**
```bash
sf data query -o org62 --json -q "SELECT CaseNumber, Subject, Status, IsClosed, CreatedDate, ClosedDate, Account.Name, Description FROM Case WHERE CaseNumber IN ('<n1>','<n2>',...)" > /tmp/cases.json
# or by record id:  ... WHERE Id='500ed00000XXXXXAAX'
```

**Comment threads (the root-cause evidence — deep-dive):**
```bash
sf data query -o org62 --json -q "SELECT Parent.CaseNumber, CreatedDate, CommentBody FROM CaseComment WHERE Parent.CaseNumber IN ('<n1>',...) ORDER BY Parent.CaseNumber, CreatedDate" > /tmp/comments.json
```
Read the **resolution tail** (last few comments) for each case: did R&D repro it? Root cause stated? Or
"resolved by workaround"? This is what distinguishes a confirmed bug from a config fix from a workaround.

## Claim-verification research prompt (dispatch to a research subagent)

> Verify this claim against PRIMARY Salesforce docs (developer.salesforce.com, release notes) as of <date>.
> Return: **TRUE / PARTLY TRUE / FALSE**, the evidence, **source URLs + dates**, a **confidence** (High/Med/Low),
> whether each fact is **documented vs. inference**, and any **roadmap signal**. Do not fabricate; if a fact
> isn't in public docs, say so and mark it an open item for PM/support. Distinguish the claim's sub-parts if
> they have different answers.

Run one per distinct capability claim. Cross-check the four source classes above, not docs alone.

## Read the Slack thread — INTERROGATE the replies, don't stop at the parent

🔴 **A parent message states the problem; the REPLIES carry the resolution, the pushback, and the real story.**
Reading a channel's parent messages and noting "Thread: N replies" *without opening them* is a shallow read — the
Slack equivalent of reading a case record without its comments. It is a mandatory step, not optional:
- **Open every thread with replies** that is relevant to the blocker (use the Slack read-thread tool on the
  parent's timestamp). Reply-count-without-reading is not evidence.
- When reviewing a whole **channel** (e.g. a #help-* support channel), the adjacent threads often contain the
  engineering resolution / workaround for the *same* class of blocker — read those too; they're precedent
  (source class 2).
- From the threads capture: the partner's stated claims, the **emotional framing** (for Step 2 of
  `adversarial.md`), any **case links / IDs** embedded, the **actual resolution or workaround** stated in replies,
  and **who is involved** (PSM, PIE, account team) for routing.
- ⚠️ Cross-customer safety: support-channel threads name *other* partners' orgs/cases — that content is raw
  sensitive capture → `.notes/` only (refs/scrub.md).
