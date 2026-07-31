# refs/living-engagement.md — the multi-session, accreting investigation

Most runs are bounded: intake → triage → (maybe) deep-dive → done. But a real, high-stakes partner engagement
often becomes a **living investigation** — new evidence arrives across many sessions (fresh cases, a call
transcript, a CTO Slack update, a voice-of-customer post), the claim set grows, and the internal doc is edited
collaboratively (often as a shared canvas) between sessions. The diagnosis discipline is unchanged; what this ref
adds is how to keep a *growing* investigation coherent instead of re-deriving it each session.

**Use this when:** the same blocker/engagement spans ≥2 sessions, the claim count is growing, or the deliverable is
a shared/living doc (e.g. a Slack canvas) that others also edit. Otherwise ignore it — a one-pass run doesn't need it.

## 1. Stable claim IDs (the backbone)

Give every distinct claim a **stable ID** the first time it appears (A1, A2, … — or a scheme that fits) and
**never renumber**. New evidence attaches to an *existing* ID or opens a *new* one; it does not shuffle the set.

- When new input arrives, first ask **"which existing claim does this touch?"** before creating a new one — a CTO
  quote confirming a known gap is *evidence on that claim*, not a new claim.
- Keep IDs monotonic and append-only. A claim that turns out false stays in the table marked overstated/false —
  don't delete it (deleting loses the "we checked this" record and invites re-litigation).
- Split a compound claim into sub-IDs (A3 / A3b) rather than overloading one.

## 2. New-evidence routing (each new input)

For every new artifact (case, transcript, thread, VoC), do a quick triage before folding it in:

1. **Resolve any cited identifiers** (refs/investigate-snippets.md — the number-resolution ladder).
2. **Route it:** which existing claim(s) does it confirm / contradict / sharpen? Or is it genuinely new (new ID)?
3. **Re-verify only what it touches** — don't re-run the whole four-source sweep; verify the delta, keep the rest.
4. **Reclassify if it overturns** (per refs/deep-dive.md — evidence can flip a class; strike + correct in place,
   don't just append).
5. **Watch for a cross-claim pattern** (refs/adversarial.md Step 2.7) — the Nth instance of a shape is often the
   real headline.

## 3. Doc ↔ canvas sync discipline

The internal `.md` (source of record) and any shared canvas (Slack/Google) will drift unless you're deliberate:

- **The internal `.md` in `.notes/` is the source of truth.** The canvas is a *view* for collaborators.
- **On any material update: edit the `.md` first, then propagate to the canvas** — never let the canvas be the only
  copy of a finding.
- **Collaborators edit the canvas.** Before you overwrite a canvas section, **read the current canvas state** and
  **preserve their edits** (owners, notes, status changes) — reconcile, don't clobber. Re-fetch section IDs each
  time; they change after every update.
- Note in the `.md` when the two were last reconciled, so the next session knows the drift window.

## 4. Session hygiene (so the next session resumes cleanly)

- **Stamp new material with its date + source** ("🆕 CTO Slack, 2026-07-30: …") so the doc reads as a dated log,
  not a flat blob.
- **Keep a short "open items / awaiting" block** — what's inbound, what's gated on PM/support, what's unverified.
- **Update the persistent memory** (if the workflow uses one) with the new claim IDs + status so a future session
  starts from current state, not from scratch.
- **Never let a `.notes/` draft with raw capture graduate to a shared surface without the scrub gate** (refs/scrub.md)
  — a living doc is edited often, which is exactly when an unscrubbed identifier slips through.

## 5. Scope check — is this still partner-blocker-forge?

This skill **diagnoses and routes a blocker**; it is not a program-management or engagement-tracking tool. A living
investigation is in-scope as long as the work is still *diagnosing claims and routing them*. If it has become
ongoing **status-tracking / action-item management** (owners, dates, deliverable pipelines) that no longer turns on
"what's real vs. claimed," that's a different tool's job — say so rather than stretching this skill to fit.
