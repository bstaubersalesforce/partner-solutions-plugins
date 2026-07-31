# Discovery Auto-Capture Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Stage 15 (Discovery Framework) an auto-capture mode that produces a pre-filled discovery document with per-dimension capture slots in every package run, linked from the home page, with a versioning guard and a capture-readback loop into the POV.

**Architecture:** Stage 15 becomes two-mode, selected by invocation (package/dispatch → auto-capture; explicit pick → workshop). The shared `discovery-document.{md,html}` templates gain a per-dimension "Discussion capture" slot (with a `[pending]` sentinel) and a mode/status header. The orchestrator runs a capture-preservation check before any regenerating run (archive/apply/skip/overwrite). Re-invocation reads filled capture slots and applies them to the POV via the existing confirms/contradicts/adds handshake. This is a documentation/instruction skill: the test harness is `tests/validate_skill.py` (structural invariant checks), so each task adds/extends a validator check (RED) before making the instruction/template change (GREEN).

**Tech Stack:** Markdown instruction files, HTML templates with `{{TOKEN}}` placeholders, Python 3 stdlib validator (`tests/validate_skill.py`), git with a pre-commit hook that runs the validator.

---

## File Structure

- `templates/discovery-document.md` — Markdown template; add per-dimension `> _Discussion capture: [pending]_` block + mode/status header line.
- `templates/discovery-document.html` — HTML view; add a styled capture slot per dimension + mode/status header; already in `HOME_LINK_TEMPLATES` (back-link invariant).
- `refs/discovery-framework.md` — full process; add two-mode resolution, auto-capture pre-fill behavior, and the capture-readback / re-invocation procedure.
- `refs/stages/stage-15-discovery-framework.md` — per-stage router file; document auto-capture mode + dispatch inclusion; remove the "never in All outputs" framing.
- `refs/parallel-dispatch.md` — add Stage 15 to Wave 1 (auto-capture) + the pre-dispatch capture-preservation check.
- `SKILL.md` — post-POV orchestration (Discovery in packages as auto-capture), "All outputs" description, Discovery menu wording, and the capture-preservation `AskUserQuestion` step.
- `refs/stages/stage-13-output-home-page.md` — Discovery card + `{SLUG}-discovery-document` filename in the convention list and card ordering.
- `validation/discovery-checklist.md` — auto-capture-mode checks.
- `tests/validate_skill.py` — new structural checks (capture slot, Wave 1 inclusion, Stage 13 filename, header token).

**Conventions to match (from the existing codebase):**
- The standardized back-link pill (verbatim, one per HTML template):
  `<a href="{{HOME_HREF}}" style="position:fixed;top:14px;left:14px;z-index:9999;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:12px;font-weight:700;letter-spacing:0.04em;text-decoration:none;color:#fff;background:#0070d2;padding:7px 14px;border-radius:100px;box-shadow:0 2px 8px rgba(0,0,0,0.25);">&#8592; All artifacts</a>`
- Confidence labels: `[confirmed]` / `[proposed — confirm]` / `[TBD]`.
- Run the validator with: `python3 tests/validate_skill.py` from the skill root. All work happens under `/Users/bstauber/.claude/skills/pov-builder` on branch `discovery-auto-capture`.

---

## Task 1: Capture slot + status header in the Markdown template

**Files:**
- Modify: `templates/discovery-document.md`
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Write the failing validator check**

Add this check function in `tests/validate_skill.py` next to the other discovery checks (after `t_discovery_dimension_parity` or the discovery HTML check — search for `discovery` to locate them). Use the existing `@check(...)` decorator and `read()` helper:

```python
@check("Discovery template (md+html) carries the capture slot + mode/status header")
def t_discovery_capture_slot():
    md = read("templates/discovery-document.md")
    html = read("templates/discovery-document.html")
    # Markdown: per-dimension capture sentinel + a mode/status header line
    assert "Discussion capture: [pending]" in md, "md template missing capture sentinel"
    assert re.search(r"Mode:.*(Auto-capture|Workshop)", md), "md template missing mode/status header"
    # HTML: a capture slot token family + mode/status token
    assert "{{MODE_STATUS}}" in html, "html template missing {{MODE_STATUS}} token"
    assert "discussion-capture" in html, "html template missing discussion-capture slot styling/markup"
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL line — `Discovery template (md+html) carries the capture slot + mode/status header` (md template missing capture sentinel), overall count drops one (e.g. 34/35).

- [ ] **Step 3: Add the mode/status header to the Markdown template**

In `templates/discovery-document.md`, change the header block at the top. Current third line reads:
`**Discovery Confidence:** [0.0–1.0] · **Associated POV:** [link or "none — standalone"]`

Add a mode/status line immediately after it:

```markdown
**Discovery Confidence:** [0.0–1.0] · **Associated POV:** [link or "none — standalone"]
**Mode:** [Auto-capture | Workshop] · **Discussion capture:** [pending | captured YYYY-MM-DD | captured YYYY-MM-DD, applied to POV]
```

- [ ] **Step 4: Add the capture block to each dimension's structure**

In `templates/discovery-document.md`, each dimension currently has three blocks (**What we know**, **How Might We…**, **What to ask**). Add a fourth block to the dimension pattern. The Part I intro blockquote currently reads:
`> Each dimension has three blocks: **What we know** (with confidence labels), **How Might We…**, and **What to ask**. A dimension with no evidence still renders — fully `[TBD]` — with its questions populated.`

Replace it with:
```markdown
> Each dimension has four blocks: **What we know** (with confidence labels), **How Might We…**, **What to ask**, and **➕ Discussion capture** (a slot for insights added live or async during the POV discussion). A dimension with no evidence still renders — fully `[TBD]` — with its questions populated and its capture slot pending.
```

Then, under **every** dimension's existing `**What to ask:**` block, add the capture block. For the FIRST dimension (Users, Personas & Journeys) the `What to ask` block is followed by the next `####` heading — insert before it:

```markdown
**➕ Discussion capture:**
> _Discussion capture: [pending]_
> _(Type insights from the POV discussion below this line. Keep the "Discussion capture:" marker so the insight can be read back into the POV on a later discovery run.)_
```

Apply the same capture block under the `**What to ask:**` of all 10 dimensions. (The 10 dimensions are the four under Theme A shown in the template plus the remaining six across Themes B and C — add the block to each `####` dimension subsection.)

- [ ] **Step 5: Run the validator to verify the md half passes**

Run: `python3 tests/validate_skill.py`
Expected: the new check still FAILS but now on the HTML assertion (`html template missing {{MODE_STATUS}} token`) — confirms the md half is satisfied. (Task 2 completes the HTML half.)

- [ ] **Step 6: Commit**

```bash
git add templates/discovery-document.md tests/validate_skill.py
git commit -m "Discovery md template: per-dimension capture slot + mode/status header"
```

---

## Task 2: Capture slot + status header in the HTML template

**Files:**
- Modify: `templates/discovery-document.html`

- [ ] **Step 1: Confirm the failing assertion**

Run: `python3 tests/validate_skill.py`
Expected: FAIL — `html template missing {{MODE_STATUS}} token` (from Task 1's check). This is the RED state for this task.

- [ ] **Step 2: Add the mode/status header token to the HTML**

In `templates/discovery-document.html`, locate the header area that renders `{{DISCOVERY_CONFIDENCE}}` and `{{ASSOCIATED_POV}}` (search for `{{ASSOCIATED_POV}}`). Add a sibling element rendering the mode/status:

```html
<div class="doc-meta-line"><strong>Mode:</strong> {{MODE_STATUS}}</div>
```

Place it adjacent to the existing confidence/POV meta line, matching the surrounding markup style.

- [ ] **Step 3: Add capture-slot styling**

In the `<style>` block of `templates/discovery-document.html`, add a rule for the capture slot (match the file's existing color variables / palette — use the SF blue `#0070d2` accent already used elsewhere):

```css
    .discussion-capture {
      margin-top: 12px;
      border: 1.5px dashed #9db8d8;
      border-radius: 6px;
      background: #f7faff;
      padding: 12px 14px;
      color: #54698d;
      font-size: 13.5px;
    }
    .discussion-capture .dc-label {
      font-weight: 700; color: #0070d2; text-transform: uppercase;
      letter-spacing: 0.05em; font-size: 11px; display: block; margin-bottom: 6px;
    }
    .discussion-capture .dc-pending { font-style: italic; opacity: 0.7; }
```

- [ ] **Step 4: Add the capture slot to the dimension render**

The HTML template renders dimensions through a `{{DIMENSIONS_HTML}}` token (the dimension markup is generated at fill time, not hard-coded per dimension). In the comment/instructions near `{{DIMENSIONS_HTML}}` (search for it), document that each dimension block must end with a capture slot. Add an HTML comment immediately before the `{{DIMENSIONS_HTML}}` token:

```html
<!-- Each dimension block rendered into {{DIMENSIONS_HTML}} MUST end with a capture slot:
     <div class="discussion-capture"><span class="dc-label">➕ Discussion capture</span>
       <span class="dc-pending">Discussion capture: [pending] — add insights from the POV discussion</span>
     </div>
     In auto-capture mode the slot is pending; when captured, replace the dc-pending span with the noted insights. -->
```

- [ ] **Step 5: Run the validator to verify it passes**

Run: `python3 tests/validate_skill.py`
Expected: PASS — `Discovery template (md+html) carries the capture slot + mode/status header`. Overall count back to full (one more than baseline, e.g. 35/35).

- [ ] **Step 6: Verify HTML still has exactly one back-link token**

Run: `grep -c '{{HOME_HREF}}' templates/discovery-document.html`
Expected: `1` (the home-link invariant check `t_home_link_token_once` already covers this template; confirm we didn't add a stray token).

- [ ] **Step 7: Commit**

```bash
git add templates/discovery-document.html
git commit -m "Discovery html template: capture slot styling + mode/status token"
```

---

## Task 3: Two-mode logic + capture-readback in the discovery reference

**Files:**
- Modify: `refs/discovery-framework.md`
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Write the failing validator check**

Add to `tests/validate_skill.py` near the other discovery checks:

```python
@check("Discovery reference defines auto-capture mode + capture-readback")
def t_discovery_two_mode():
    ref = read("refs/discovery-framework.md")
    low = ref.lower()
    assert "auto-capture" in low, "discovery-framework.md missing auto-capture mode"
    assert "workshop" in low, "discovery-framework.md missing workshop mode"
    assert "readback" in low or "re-invocation" in low or "capture slot" in low, \
        "discovery-framework.md missing capture-readback procedure"
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL — `Discovery reference defines auto-capture mode + capture-readback`.

- [ ] **Step 3: Add the two-mode resolution section**

Near the top of `refs/discovery-framework.md` (after its overview, before the dimension walkthrough), add:

```markdown
## Mode Resolution (resolve first, never ask)

Discovery runs in one of two modes, chosen by **how it was invoked** — never by prompting the user:

- **Auto-capture mode** — invoked via the package/parallel-dispatch run, or any brief containing an "auto-capture" / "non-interactive" directive. Pre-fill all 10 dimensions and both canvases from research + the approved POV using the confidence labels (`[confirmed]` / `[proposed — confirm]` / `[TBD]`). Ask **no** questions. Emit each dimension's **➕ Discussion capture** slot as the sentinel `Discussion capture: [pending]`. Set the header to `Mode: Auto-capture · Discussion capture: pending`. Do **not** run the POV handshake now — it is deferred to a later re-invocation.
- **Workshop mode** — invoked via the explicit "Discovery Framework" menu pick, the phrases "run discovery / discovery workshop / refine the POV with discovery", or the Full Discovery intake fork. Ask the 10-dimension questions, fill the capture slots from the answers, set the header to `Mode: Workshop · captured {today}`, and run the confirms/contradicts/adds POV handshake immediately.

Default in any non-interactive or dispatched context: **auto-capture**. Never block a package run waiting for answers.
```

- [ ] **Step 4: Add the capture-readback / re-invocation procedure**

Add a section after the POV-handshake material in `refs/discovery-framework.md`:

```markdown
## Capture Readback (re-invocation)

When discovery is re-invoked **explicitly** (menu pick / "run discovery again" / "apply discovery captures") and a `{SLUG}-discovery-document.md` already exists in the output directory with at least one filled (non-`[pending]`) capture slot, do not regenerate blindly — read the captures back into the POV:

1. Read the existing `{SLUG}-discovery-document.md`. For each dimension, parse the text under its `Discussion capture:` marker.
2. Skip any slot still reading `[pending]` (nothing captured).
3. For slots with real content, run the standard POV handshake: present the captured insights as a **confirms / contradicts / adds** diff against the current POV; offer to apply.
4. On apply: update the POV's affected sections, then set the discovery doc header to `Mode: <mode> · captured {date}, applied to POV`.
5. **Idempotent:** if no slot has new content, report "nothing new to apply" and make no changes.

**Marker dependency:** readback finds notes by the `Discussion capture:` marker line. Tell users to type **under** the marker, not delete it — a removed marker means that dimension's notes are not auto-detected.

**The `.md` is the source of truth** for capture; the `.html` is the shareable view. Readback always parses the `.md`.
```

- [ ] **Step 5: Run the validator to verify it passes**

Run: `python3 tests/validate_skill.py`
Expected: PASS — `Discovery reference defines auto-capture mode + capture-readback`.

- [ ] **Step 6: Commit**

```bash
git add refs/discovery-framework.md tests/validate_skill.py
git commit -m "Discovery ref: two-mode resolution + capture-readback procedure"
```

---

## Task 4: Update the Stage 15 router file

**Files:**
- Modify: `refs/stages/stage-15-discovery-framework.md`

- [ ] **Step 1: Verify the current "never in All outputs" framing**

Run: `grep -n "All outputs\|upstream" refs/stages/stage-15-discovery-framework.md`
Expected: shows the line stating Discovery is "not included in All outputs + home page".

- [ ] **Step 2: Replace the upstream-only framing with dual-nature wording**

In `refs/stages/stage-15-discovery-framework.md`, replace the final paragraph (the one beginning "Unlike Stages 8–14, Discovery is an **upstream refinement**…") with:

```markdown
Discovery is **dual-nature**:
- **Auto-capture mode (in every package):** Included in "All outputs + home page" and dispatched in Wave 1 (see `refs/parallel-dispatch.md`). It pre-fills the discovery document from research + the approved POV, asks no questions, and emits a per-dimension **Discussion capture** slot for insights added live or async. Filenames: `{SLUG}-discovery-document.md` + `{SLUG}-discovery-document.html`.
- **Workshop mode (on explicit request):** The questions-driven discovery workshop, run when the user selects "Discovery Framework" from the menu, asks to run discovery, or chooses Full Discovery at intake. It can run with no POV present and applies its findings to the POV immediately via the confirms/contradicts/adds handshake.

Both modes share `templates/discovery-document.{md,html}` and the process in `refs/discovery-framework.md`, which carries the mode-resolution rule and the capture-readback (re-invocation) procedure. Run every check in `validation/discovery-checklist.md` before delivering.
```

- [ ] **Step 3: Verify the stage heading is intact**

Run: `grep -n '^\*\*Stage 15 —' refs/stages/stage-15-discovery-framework.md`
Expected: one match (the load-bearing heading the validator's `t_stage_file_schema` and contiguity checks require). Do not alter it.

- [ ] **Step 4: Run the validator**

Run: `python3 tests/validate_skill.py`
Expected: all PASS (no regression; this task changes prose the existing checks already tolerate).

- [ ] **Step 5: Commit**

```bash
git add refs/stages/stage-15-discovery-framework.md
git commit -m "Stage 15 router: document dual-nature (auto-capture in package + workshop)"
```

---

## Task 5: Add Stage 15 to Wave 1 + capture-preservation check in dispatch

**Files:**
- Modify: `refs/parallel-dispatch.md`
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Write the failing validator check**

Add to `tests/validate_skill.py`:

```python
@check("Parallel dispatch includes Stage 15 auto-capture in Wave 1 + capture-preservation check")
def t_dispatch_discovery():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "stage 15" in low, "parallel-dispatch.md does not mention Stage 15"
    assert "auto-capture" in low, "parallel-dispatch.md missing auto-capture directive for discovery"
    assert "capture-preservation" in low or "archive" in low, \
        "parallel-dispatch.md missing the capture-preservation/archive check"
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL — `Parallel dispatch includes Stage 15 auto-capture in Wave 1 + capture-preservation check`.

- [ ] **Step 3: Update the threshold-count and Wave 1 lists**

In `refs/parallel-dispatch.md`:

Find: `Count only the independent **downstream artifact** stages: 8, 9, 10, 11, 12, 14, 16.`
Replace with: `Count only the independent **downstream artifact** stages: 8, 9, 10, 11, 12, 14, 15 (auto-capture), 16, 17.`

Find the Wave 1 bullet: `- **Wave 1 — all other selected artifacts** (Stages 8, 9, 10, 11, 12, 14), dispatched **concurrently**,`
Replace the stage list with: `- **Wave 1 — all other selected artifacts** (Stages 8, 9, 10, 11, 12, 14, 15, 17), dispatched **concurrently**,`

Update the Stage 15 exclusion note that currently reads `**Stage 15** (Discovery Framework) — an upstream refinement that runs as its own separate pass, never inside the concurrent waves.` Replace with:
```markdown
- **Stage 15** (Discovery Framework) runs in Wave 1 in **auto-capture mode** (pre-fill, no questions); its brief must state auto-capture explicitly. Its **workshop** mode is a separate, interactive, standalone pass and never runs inside the concurrent waves.
```

- [ ] **Step 4: Add the capture-preservation check to the prepare step**

In `refs/parallel-dispatch.md`, in the "## Prepare the shared inputs (before dispatching)" section, add a new numbered item after the POV-persistence step:

```markdown
4. **Capture-preservation check (before regenerating discovery).** If `{output-dir}/{SLUG}-discovery-document.md` already exists **with at least one filled** (non-`[pending]`) Discussion-capture slot, do not let the discovery subagent overwrite it silently. Surface a single `AskUserQuestion` offering: **(a) Archive original, then regenerate** (default/recommended — copy the existing `.md` and `.html` to `{SLUG}-discovery-document.archived-{YYYY-MM-DD}.{md,html}`, suffix `-2`/`-3` if that name exists, then regenerate fresh); **(b) Apply captures first** — run the discovery readback (`refs/discovery-framework.md` → Capture Readback) to fold insights into the POV before regenerating; **(c) Skip discovery regeneration** — keep the captured doc, regenerate the rest of the package around it (omit Stage 15 from Wave 1 this run); **(d) Overwrite anyway**. Resolve this **before** dispatching Wave 1, because the discovery subagent runs non-interactively and cannot prompt. A doc that does not exist, or whose slots are all `[pending]`, regenerates silently — no prompt.
```

- [ ] **Step 5: Note the auto-capture directive in the brief**

In `refs/parallel-dispatch.md`, in the "## Compact shared payload" section (where it describes what each subagent's brief contains), add a sentence:

```markdown
**Discovery (Stage 15) brief.** When Stage 15 is dispatched in a package, its brief must state **auto-capture mode** verbatim: "Run in auto-capture mode: pre-fill all dimensions and both canvases from the POV, ask no questions, emit each Discussion-capture slot as `[pending]`, and do not run the POV handshake." Without this, the discovery subagent could fall into workshop mode and stall on questions.
```

- [ ] **Step 6: Run the validator to verify it passes**

Run: `python3 tests/validate_skill.py`
Expected: PASS — `Parallel dispatch includes Stage 15 auto-capture in Wave 1 + capture-preservation check`.

- [ ] **Step 7: Commit**

```bash
git add refs/parallel-dispatch.md tests/validate_skill.py
git commit -m "Dispatch: Stage 15 auto-capture in Wave 1 + capture-preservation check"
```

---

## Task 6: Wire SKILL.md orchestration, menu, and preservation prompt

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: Update the "All outputs + home page" menu description**

In `SKILL.md`, find the `All outputs + home page` option description (currently lists "Stages 8–12, 14, 16, 17"). Replace the stage list with `Stages 8–12, 14, 15 (auto-capture discovery), 16, 17` and keep the rest of the sentence. The clause "but does NOT include Discovery (Stage 15), which is an upstream refinement" is now wrong — replace it with: "Discovery (Stage 15) is included in **auto-capture** mode (pre-filled capture document); its interactive **workshop** mode remains a separate pick."

- [ ] **Step 2: Update the Discovery menu option wording**

In the Analysis & Readiness question, find the `Discovery Framework` option description. Replace with:
```
"Run the interactive discovery **workshop** (10 dimensions, How Might We, Value Proposition + Business Model canvases) and apply findings to the POV. (A pre-filled auto-capture discovery document is already produced in 'All outputs'; this pick is the full question-driven workshop.) (Stage 15)"
```

- [ ] **Step 3: Update the post-POV orchestration prose**

In `SKILL.md`, find the orchestration bullets after the menu. Update the dispatch-rule bullet's stage list to include 15, and the ordering bullet's Wave-1 list to include 15. Then replace the bullet that currently reads `**"Discovery Framework" selected** — load refs/discovery-framework.md and run Stage 15 separately (it is upstream)...` with:

```markdown
- **Discovery in a package** — when "All outputs + home page" runs, Stage 15 is generated in **auto-capture mode** in Wave 1 (pre-filled document with per-dimension capture slots, no questions). Before regenerating it, run the **capture-preservation check** (see below).
- **"Discovery Framework" selected on its own** — load `refs/discovery-framework.md` and run Stage 15 in **workshop mode** (interactive questions). A POV already exists, so follow the POV handshake: present findings as a diff (confirms / contradicts / adds) and offer to apply.
- **Capture-preservation check (before overwriting a discovery doc).** If a `{SLUG}-discovery-document.md` with filled capture slots already exists, present an `AskUserQuestion` with four options — **Archive original then regenerate** (default), **Apply captures first**, **Skip discovery regeneration**, **Overwrite anyway** — and honor the choice before (re)generating discovery. A doc that is absent or all-`[pending]` regenerates with no prompt. Full procedure in `refs/parallel-dispatch.md`.
```

- [ ] **Step 4: Run the validator**

Run: `python3 tests/validate_skill.py`
Expected: all PASS. In particular `Output menu offers the Discovery Framework and cites Stage 15` must still pass (the option still names Stage 15), and the stage-contiguity / menu-stage-ref checks remain green.

- [ ] **Step 5: Commit**

```bash
git add SKILL.md
git commit -m "SKILL.md: discovery auto-capture in packages, workshop on explicit pick, preservation prompt"
```

---

## Task 7: Stage 13 home-page card + filename for discovery

**Files:**
- Modify: `refs/stages/stage-13-output-home-page.md`
- Modify: `tests/validate_skill.py`

- [ ] **Step 1: Write the failing validator check**

Add to `tests/validate_skill.py`:

```python
@check("Stage 13 references the discovery-document filename")
def t_stage13_discovery_filename():
    s = read("refs/stages/stage-13-output-home-page.md")
    assert "discovery-document" in s, "Stage 13 does not reference {SLUG}-discovery-document"
```

- [ ] **Step 2: Run the validator to verify it fails**

Run: `python3 tests/validate_skill.py`
Expected: FAIL — `Stage 13 references the discovery-document filename`.

- [ ] **Step 3: Add the filename to the convention list**

In `refs/stages/stage-13-output-home-page.md`, in the filename-convention bullet list, add (place it right after the POV entries, before the build plan):

```markdown
- `SLUG-discovery-document.md` + `SLUG-discovery-document.html`
```

- [ ] **Step 4: Add the discovery card to the ordering rule**

Find the card-ordering line (currently `Order cards: POV (Core) first, then Presentation, Build, Risk, Sales, Visual, Readiness, Architecture ...`). Replace the order with:
`Order cards: POV (Core) first, then Presentation, Discovery, Build, Risk, Sales, Visual, Readiness, Architecture — listing only what exists.` Keep the trailing note. Then add, after that line:

```markdown
   (Discovery = the auto-capture discovery document; View ↗ + Markdown ↓. Do **not** list `*-discovery-document.archived-*` files — archives are point-in-time copies, not live package artifacts.)
```

- [ ] **Step 5: Run the validator to verify it passes**

Run: `python3 tests/validate_skill.py`
Expected: PASS — `Stage 13 references the discovery-document filename`.

- [ ] **Step 6: Commit**

```bash
git add refs/stages/stage-13-output-home-page.md tests/validate_skill.py
git commit -m "Stage 13: discovery-document card + filename, exclude archives"
```

---

## Task 8: Auto-capture checks in the discovery checklist

**Files:**
- Modify: `validation/discovery-checklist.md`

- [ ] **Step 1: Inspect the current checklist**

Run: `sed -n '1,40p' validation/discovery-checklist.md`
Expected: shows the existing discovery validation items (dimensions, canvases, etc.).

- [ ] **Step 2: Add an auto-capture-mode section**

Append to `validation/discovery-checklist.md`:

```markdown

## Auto-Capture Mode (when produced in a package)

- [ ] Header shows `Mode: Auto-capture` and a `Discussion capture:` status (pending on first generation)
- [ ] All 10 dimensions are pre-filled from research/POV with confidence labels — no question was asked
- [ ] Value Proposition Canvas and Business Model Canvas are pre-filled; cells without evidence show `[TBD]` (not blank)
- [ ] Every dimension ends with a **➕ Discussion capture** slot carrying the `Discussion capture: [pending]` sentinel
- [ ] HTML carries the standardized home-page back-link pill (`{{HOME_HREF}}` → `{SLUG}-index.html`); removed if standalone
- [ ] No `{{PLACEHOLDER}}` tokens remain in the rendered output

## Capture Readback (re-invocation)

- [ ] Filled (non-`[pending]`) capture slots are presented as a confirms/contradicts/adds diff to the POV
- [ ] `[pending]` slots are skipped; a doc with no filled slots yields a no-op
- [ ] On apply, the header flips to `captured {date}, applied to POV`
```

- [ ] **Step 3: Run the validator**

Run: `python3 tests/validate_skill.py`
Expected: all PASS (the `discovery dimension parity` check counts dimensions; confirm the appended prose did not introduce a stray `####` dimension-like heading — it does not).

- [ ] **Step 4: Commit**

```bash
git add validation/discovery-checklist.md
git commit -m "Discovery checklist: auto-capture mode + readback checks"
```

---

## Task 9: Full-skill verification + README refresh

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Run the full validator**

Run: `python3 tests/validate_skill.py`
Expected: all checks PASS, count = prior 34 + 4 new (`t_discovery_capture_slot`, `t_discovery_two_mode`, `t_dispatch_discovery`, `t_stage13_discovery_filename`) = **38/38**. (If a count mismatch, reconcile — every `@check` defined must pass.)

- [ ] **Step 2: Update the README outputs table + flow**

In `README.md`, update the Discovery row of the "What it produces" table to note it is produced in auto-capture mode in every package plus the workshop on request. Find the Discovery Document row and set its Trigger cell to:
`"All outputs" (auto-capture, pre-filled) · "discovery"/Full Discovery (workshop) — Stage 15`

Then find the sentence stating Discovery is excluded from "All outputs" / is upstream-only and update it to state Discovery now runs in Wave 1 in auto-capture mode (pre-filled capture document with per-dimension capture slots), while the workshop remains a separate interactive pick.

- [ ] **Step 3: Render a live discovery doc end-to-end (smoke test)**

Use the existing CitNOW POV to confirm the template fills with zero unfilled tokens. Run:

```bash
python3 - <<'PYEOF'
import re
html = open('/Users/bstauber/.claude/skills/pov-builder/templates/discovery-document.html').read()
# crude smoke check: the template's tokens are all UPPER_SNAKE and the back-link + mode token exist
assert '{{MODE_STATUS}}' in html
assert html.count('{{HOME_HREF}}') == 1
assert 'discussion-capture' in html
print("discovery-document.html structural smoke test OK")
PYEOF
```
Expected: `discovery-document.html structural smoke test OK`

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "README: discovery auto-capture in packages + workshop on request"
```

---

## Self-Review Checklist (run before handing off to execution)

- [ ] **Spec coverage:** every spec section maps to a task — mode resolution (T3), document structure/capture slot (T1,T2), canvases pre-fill (T8 checklist + T3 behavior), capture-readback (T3), capture-preservation/versioning (T5,T6), dispatch Wave 1 (T5), filenames + home-page card (T7), SKILL/menu wiring (T6), validation (each task), README (T9).
- [ ] **Placeholder scan:** no TBD/TODO/"handle appropriately" in the plan steps — all code/markdown shown verbatim.
- [ ] **Type/name consistency:** token names match across tasks — `{{MODE_STATUS}}`, `discussion-capture` (CSS class), `Discussion capture: [pending]` (md sentinel), `{SLUG}-discovery-document.{md,html}`, archive `{SLUG}-discovery-document.archived-{YYYY-MM-DD}.{md,html}`. Validator check names unique: `t_discovery_capture_slot`, `t_discovery_two_mode`, `t_dispatch_discovery`, `t_stage13_discovery_filename`.
- [ ] **Validator count:** 4 new checks added across T1, T3, T5, T7 → baseline 34 → 38.
