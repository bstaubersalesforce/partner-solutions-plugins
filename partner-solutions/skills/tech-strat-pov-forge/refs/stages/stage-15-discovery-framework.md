# Stage 15 — Discovery Framework

> Optional output stage, lazily loaded by tech-strat-pov-forge. Loaded only when this output is selected from the Stage 7 menu or requested by name. Draws from the approved POV; follows the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`.

**Stage 15 — Discovery Framework (optional)**
Triggered when the user selects "Discovery Framework" from the output menu, asks to run discovery / a discovery workshop / refine the POV with discovery, or chooses the Full Discovery path at intake (Stage 1).

Load `refs/discovery-framework.md` and follow it end to end — it carries the full discovery process, the 10 dimensions, the *How Might We* method, and the Value Proposition Canvas + Business Model Canvas construction rules.
It produces `templates/discovery-document.md` (Markdown output) and, on Approve, `templates/discovery-document.html` (HTML output with both canvases).
Run every check in `validation/discovery-checklist.md` before delivering.

Discovery is **dual-nature**:
- **Auto-capture mode (in every package):** Included in "All outputs + home page" and dispatched in Wave 1 (see `refs/parallel-dispatch.md`). It pre-fills the discovery document from research + the approved POV, asks no questions, and emits a per-dimension **Discussion capture** slot for insights added live or async. Filenames: `{SLUG}-discovery-document.md` + `{SLUG}-discovery-document.html`.
- **Workshop mode (on explicit request):** The questions-driven discovery workshop, run when the user selects "Discovery Framework" from the menu, asks to run discovery, or chooses Full Discovery at intake. It can run with no POV present and applies its findings to the POV immediately via the confirms/contradicts/adds handshake.

Both modes share `templates/discovery-document.md` + `templates/discovery-document.html` and the process in `refs/discovery-framework.md`, which carries the mode-resolution rule and the capture-readback (re-invocation) procedure. Run every check in `validation/discovery-checklist.md` before delivering.
