# Discovery Auto-Capture Mode — Design Spec

**Date:** 2026-05-30
**Status:** Approved (brainstorming)
**Skill:** pov-builder

## Problem

Stage 15 (Discovery Framework) today is a single-mode, questions-driven workshop. It is explicitly **excluded** from "All outputs + home page" and only runs when the user picks it or chooses Full Discovery at intake. As a result, a typical Quick-POV package ships with no discovery artifact at all.

The user wants a discovery document **always produced** as part of the package — pre-filled from research and the approved POV, with the rest of the structure serving as a capture scaffold. Insights from the live POV discussion can be typed into the document during or after the run, then fed back into the POV later.

## Solution Overview

Give Stage 15 **two modes**, selected by *how it is invoked* — never by asking the user:

- **Auto-capture mode (new):** runs inside every package/dispatch run. Pre-fills the 10 dimensions and both canvases from research + the approved POV (no questions), and emits an empty "Discussion capture" slot per dimension for live/async note-taking. The POV handshake is deferred to a later re-invocation.
- **Workshop mode (existing, unchanged):** runs on the explicit "Discovery Framework" menu pick, "run discovery workshop," or Full Discovery at intake. Asks the 10-dimension questions and runs the confirms/contradicts/adds POV handshake immediately.

A later **re-invocation** against a filled-in document reads the capture slots and applies the captured insights to the POV as a confirms/contradicts/adds diff (the existing Stage 15 handshake). This closes the loop the user described: always-produce → capture async → re-merge into POV.

## Mode Resolution (the one branch)

The first thing Stage 15 does is resolve its mode:

- Invoked via parallel-dispatch / package, or the brief contains an "auto-capture" / "non-interactive" directive → **auto-capture mode**.
- Invoked via the explicit "Discovery Framework" menu selection, the phrase "run discovery / discovery workshop / refine the POV with discovery", or the Full Discovery intake fork → **workshop mode**.
- Default in any non-interactive or dispatched context: **auto-capture**. Stage 15 must never block a package run waiting for question answers (consistent with the non-interactive dispatch rule already in `refs/parallel-dispatch.md`).

## Document Structure

The template `templates/discovery-document.{md,html}` gains one new repeating element and a header status line. Everything else is preserved.

**Each of the 10 dimensions renders four blocks** (was three):
1. **What we know** — pre-filled from research/POV, confidence-labeled (`[confirmed]` / `[proposed — confirm]` / `[TBD]`).
2. **How Might We…** — reframe prompts (existing).
3. **What to ask** — targeted gap questions (existing).
4. **➕ Discussion capture (NEW)** — a visually distinct empty slot. HTML: a styled fillable area (dashed border, placeholder text "Add insights from the POV discussion"). Markdown: a clearly marked, sentinel-bearing block:
   `> _Discussion capture: [pending]_`

**Canvases:** the Value Proposition Canvas and Business Model Canvas are pre-filled from current knowledge in both modes; any cell without evidence shows `[TBD]` rather than rendering blank.

**Header status line (NEW):** indicates mode and capture state, e.g.
- `Mode: Auto-capture · Discussion capture: pending`
- `Mode: Workshop · captured 2026-05-30`
- `Mode: Auto-capture · captured 2026-05-30, applied to POV`

## Capture-Readback Loop (re-invocation)

The capture slot is designed to be machine-readable on re-entry.

1. **First run (auto-capture):** every dimension's capture slot carries the stable sentinel `> _Discussion capture: [pending]_`. Header status: "Discussion capture: pending".
2. **Async edit:** the user types insights into the slots — in the `.md` directly, or in the HTML then pasted back. Users type **under/after** the sentinel marker, replacing `[pending]` with notes; the marker line itself stays so the slot remains findable.
3. **Re-invocation:** the user runs discovery again and a `{SLUG}-discovery-document.md` already exists in the output directory. Stage 15 detects this, reads each dimension's capture slot, and:
   - Skips slots still marked `[pending]` (nothing captured).
   - For slots with content, runs the existing Stage 15 POV handshake: present captured insights as a **confirms / contradicts / adds** diff against the current POV; offer to apply.
   - On apply: update the POV's affected sections; flip the discovery doc header to "captured {date}, applied to POV".

**Design choices:**
- The `.md` is the **source of truth** for capture; the HTML is the shareable view. Readback parses the `.md`.
- **Idempotent:** re-running with no new captures yields a no-op diff ("nothing new to apply").
- **Detection rule:** re-invocation = an **explicit user discovery request** (menu pick / "run discovery again" / "apply discovery captures") AND `{SLUG}-discovery-document.md` already exists in the output dir with at least one non-`[pending]` capture slot. A package/dispatch run is **always** a fresh auto-capture generation that overwrites the doc (it is regenerating the whole package), and therefore never triggers readback. Overwriting is guarded by the capture-preservation check below, so it can never silently destroy captured insights.

## Capture-Preservation Check (versioning the original before overwrite)

Any run that would **regenerate** the discovery doc (a package/auto-capture run, or a fresh standalone discovery run) must first protect existing captured insights. This check runs at the **orchestrator** level, before dispatch — not inside the (non-interactive) discovery subagent — because it is the orchestrator that holds the user in the loop and already does pre-dispatch prep (persist POV, derive SLUG).

**Procedure (orchestrator, pre-dispatch):**
1. If `{SLUG}-discovery-document.md` does **not** exist, or exists but every capture slot is still `[pending]` → proceed normally, regenerate fresh (nothing to lose). No prompt.
2. If it exists **with at least one filled** (non-`[pending]`) capture slot → do **not** silently overwrite. Surface a single `AskUserQuestion` offering:
   - **Archive original, then regenerate (recommended/default)** — copy the existing `.md` and `.html` to a versioned archive filename, then regenerate the live doc fresh. Captures preserved in the archive.
   - **Apply captures first (re-invocation)** — run the readback handshake to fold the captured insights into the POV before regenerating, so they are not stranded.
   - **Skip discovery regeneration** — leave the captured doc untouched; regenerate the rest of the package around it.
   - **Overwrite anyway** — discard captures and regenerate (explicit, eyes-open).
3. Honor the choice, then proceed with the rest of the run.

**Archive filename convention:** `{SLUG}-discovery-document.archived-{YYYY-MM-DD}.{md,html}`. If an archive for that date already exists, append `-2`, `-3`, … The archive is a standalone copy (its back-link is removed — it is not linked from the home page; it is a point-in-time record).

**Why orchestrator, not subagent:** the package dispatch rule (`refs/parallel-dispatch.md`) requires Wave 1 subagents to run non-interactively and never block on questions. The preservation prompt is interactive, so it must be resolved *before* the discovery subagent is dispatched. By the time the subagent runs, the original is already archived (or the user chose overwrite/skip), and the subagent just regenerates or is omitted.
- **Marker dependency (documented limitation):** readback finds notes by the `Discussion capture:` marker. If a user deletes the marker while editing, that dimension's notes are not auto-detected. The spec/instructions tell users to type under the marker, not replace it.

## Dispatch, Filenames, Wiring

**Dispatch:** Stage 15 (auto-capture) joins **Wave 1** of `refs/parallel-dispatch.md`, alongside Stages 8, 9, 10, 11, 12, 14, 17. It depends only on the approved POV — no upstream feeder. Its subagent brief explicitly states auto-capture mode (pre-fill, no questions), the standardized back-link, and the pinned filename. Stage 15 thus becomes **dual-nature**: included in packages as auto-capture, still available standalone as the workshop.

**Filenames (Stage 13 convention):** `{SLUG}-discovery-document.md` + `{SLUG}-discovery-document.html`. Stage 13 gains a Discovery card (View ↗ + Markdown ↓), ordered right after POV/Presentation and before Build.

**HTML:** rendered via `templates/discovery-document.html`; standardized fixed-position back-link pill; `{{HOME_HREF}}` filled with `{SLUG}-index.html` in a package, anchor removed when standalone.

## Files Touched

- `templates/discovery-document.md` — add the Discussion capture block (with `[pending]` sentinel) per dimension + mode/status header line.
- `templates/discovery-document.html` — add the styled Discussion capture slot per dimension + mode/status header; ensure standardized back-link pill + single `{{HOME_HREF}}`.
- `refs/discovery-framework.md` — add the two-mode resolution logic, the auto-capture pre-fill behavior, and the capture-readback / re-invocation procedure.
- `refs/stages/stage-15-discovery-framework.md` — document auto-capture mode and dispatch inclusion; note it is no longer "never in All outputs".
- `refs/parallel-dispatch.md` — add Stage 15 to Wave 1 (auto-capture); state the mode directive belongs in its brief.
- `SKILL.md` — update post-POV orchestration (Discovery now in packages as auto-capture), "All outputs + home page" description, the Discovery menu wording (clarify the standalone pick = workshop mode), and add the **capture-preservation check** as a pre-dispatch orchestrator step (the `AskUserQuestion` offering archive / apply-first / skip / overwrite).
- `refs/parallel-dispatch.md` — add the capture-preservation check to the "Prepare the shared inputs (before dispatching)" step, so the original is archived/handled before the discovery subagent goes out.
- `refs/stages/stage-13-output-home-page.md` — add the Discovery card + filename to the convention list and card ordering.
- `tests/validate_skill.py` — new checks (see below).
- `validation/discovery-checklist.md` — add auto-capture-mode checks (capture slot present and sentinel intact; canvases pre-filled with `[TBD]` for gaps; header status line present).

## Validation Additions

1. `discovery-document.md` and `.html` each contain a Discussion-capture block / sentinel.
2. `refs/parallel-dispatch.md` lists Stage 15 in Wave 1.
3. `refs/stages/stage-13-output-home-page.md` references `{SLUG}-discovery-document` in its filename convention.
4. The discovery template carries a mode/status header token.
5. `discovery-document.html` carries exactly one `{{HOME_HREF}}` token (existing home-link invariant extended to it — it is already in `HOME_LINK_TEMPLATES`).

## Out of Scope (YAGNI)

- **Regenerate-downstream-after-capture** — re-running build plan/scorecard/etc. from the refreshed POV. (User chose "refine POV", not "regenerate downstream.")
- **Auto-extraction of insights** from external notes/transcripts. Capture is manual typing into the slots.
- **Changing the workshop mode's behavior** — it is preserved verbatim apart from the shared template additions.

## Success Criteria

- A standard "All outputs + home page" run produces `{SLUG}-discovery-document.{md,html}` with: pre-filled dimensions, pre-filled VPC+BMC (gaps `[TBD]`), an empty `[pending]` capture slot per dimension, the auto-capture header status, and a working back-link — without asking any questions.
- The HTML matches the other artifacts (shell + standardized pill) and is linked from the home page.
- Re-invoking discovery against a doc with filled capture slots presents a confirms/contradicts/adds diff to the POV and applies it on approval; an unfilled doc yields a no-op.
- A run that would overwrite a discovery doc holding **filled** capture slots first offers archive / apply-first / skip / overwrite, defaulting to archive; a doc with only `[pending]` slots regenerates silently. The archive copy lands at `{SLUG}-discovery-document.archived-{date}.{md,html}` and is not linked from the home page.
- The explicit "Discovery Framework" menu pick still runs the questions-driven workshop.
- Validator passes with the new checks.
