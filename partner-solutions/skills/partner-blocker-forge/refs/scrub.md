# refs/scrub.md — data-safety gate (mandatory before any output is shared)

Slack threads and Org62 cases carry **cross-customer data**: other partners' org IDs, case numbers, tenant IDs,
internal GUS/Splunk/Slack-archive links, and PII. This gate is required before any doc leaves your hands, and
always before a partner-facing doc.

## The separation rule

- **Raw / sensitive capture → gitignored `.notes/`.** Full case comment threads, the raw Slack export, any
  internal IDs/links go here. Never committed. (`.notes/` is in `.gitignore`.)
- **Draft internal doc is BORN in `.notes/` too.** Write the internal deliverable into `.notes/` first; it only
  moves to a shareable/committed location **after** this scrub passes. This prevents an unscrubbed draft landing
  in a git-tracked dir and being committed. (Nothing outside `.notes/` is auto-ignored.)
- **Committed / shared docs → scrubbed.** The internal deliverable and the partner-facing deliverable contain
  only what is safe for their audience.

## 🔴 The highest-risk leak is the case-pull itself — handle at the source

`CommentBody` and `Account.Name` (refs/investigate-snippets.md) routinely contain **other** customers' 18-char
org IDs (`00D…`), adjacent case numbers, account names, and pasted Splunk/GUS links. So:
- Case-pull output is **raw sensitive capture → `.notes/` only.** Never paste a raw `CommentBody` straight into a
  shared doc.
- When §2 of the doc summarizes "what the thread shows," **paraphrase the finding**; do not quote the comment
  verbatim. If you must quote, redact any `00D…`/`500…` ID, foreign account name, and internal URL first.
- **Run the scrub-check gate before sharing:** `python3 scripts/scrub_check.py <draft.md>` — it flags org IDs
  (`00D…`), case IDs (`500…`), `gus.`/`splunk`/`*.internal.salesforce.com` URLs, internal Slack-archive links,
  phone numbers, and GUS work-items. Exit 0 = clean; non-zero = review each hit (confirm it's this partner's own
  data or remove it). This is the mechanical backstop to the checklist above — not a replacement for judgment
  (it can't know which account name is foreign), but it catches the ID/URL/PII shapes that slip through.

## Scrub checklist — run before sharing

Remove / confirm absent:
- [ ] **Other customers' identifiers** — org IDs, case numbers, tenant IDs, account names that are NOT this
      partner. (The support channel is full of them; a case-pull can surface adjacent orgs.)
- [ ] **Internal-only URLs** — `gus.lightning.force.com`, Splunk (`splunk-web-*`), `*.internal.salesforce.com`,
      internal Slack archive links, GHO/Sev channel links.
- [ ] **PII** — direct phone numbers, personal emails, individual names where a role suffices.
- [ ] **Internal system identifiers** that would confuse or leak (pod names, work-item IDs) unless needed and safe.

## Partner-facing doc — additional strips (on top of the above)

- [ ] **Internal routing** (who to escalate to, PSM/PIE mechanics, "traditional support vs PIE" reasoning).
- [ ] **Case-comment specifics** and internal case IDs — reference the partner's own case number only.
- [ ] **Adversarial framing about the partner** — the "is their claim overstated" analysis stays internal;
      the partner-facing doc states the corrected facts neutrally, not "you were wrong."
- [ ] Add a **"verify before external use"** note for any fact tagged Med/Low confidence or awaiting PM/support.

## Rule of thumb

If you can't point to why a specific identifier or link is safe for *this* audience, strip it. When in doubt,
it goes in `.notes/`, not the shared doc.
