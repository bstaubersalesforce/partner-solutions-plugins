# Partner Readiness Scorecard Pre-Delivery Validation Checklist

Run every check before delivering the Partner Readiness Scorecard.
If any check fails, repair before delivering — do not deliver a failing scorecard.

## Structure

- [ ] All 18 attributes present, in the exact order defined in `templates/partner-readiness-scorecard.md` — none dropped, renamed, or reordered
- [ ] Definitions are filled for all 18 rows (definitions are never blank)
- [ ] Header metadata filled: Partner Name, Scorecard Date, POV Reference, Org62 Opportunity Stage — not placeholder text
- [ ] No source-mapping bracket notes (e.g. "[Source: …]") remain in the final output
- [ ] No unfilled `{{PLACEHOLDER}}` tokens remain (HTML) — including every `{{A1_…}}` through `{{A18_…}}` cell

## Population Rule (evidence or blank — never guess)

- [ ] Every filled Status/Rank is one of: 🟢 Strong · 3, 🟡 Emerging · 2, 🔴 Gap · 1 — no other values
- [ ] Every filled Status/Rank traces to a specific POV section or research signal named in the Notes cell — no rank without a reason
- [ ] Attributes with no evidence in the POV or research are left blank in Status, Rank, Owner, and Notes — not filled with "TBD", "N/A", or a guessed rank
- [ ] No Notes cell asserts a fact not supported by the POV or research (e.g. naming a customer or exec who never appeared in source material)
- [ ] In the HTML, blank attributes use `rag-na` class with an em dash (—) — not an empty colored pill

## Snapshot Integrity

- [ ] Assessed count = number of attributes with a non-blank Status/Rank (matches the table)
- [ ] 🟢 / 🟡 / 🔴 tallies sum to the Assessed count
- [ ] Avg rank is computed only over assessed attributes (blank rows excluded) and is between 1.0 and 3.0
- [ ] "Top gaps to close before 03-Contract" names actual 🔴/🟡 attributes from the table, or states "No material gaps identified in assessed attributes" — does not invent gaps

## Assessment Basis

- [ ] Confidence score stated (0.0–1.0) and calibrated: lower when many attributes are blank; not 0.85+ unless a majority of attributes are evidence-backed
- [ ] At least 1 named assumption stated
- [ ] "Not yet assessed" lists each blank attribute with the owner who should close it before 03-Contract

## Failure → Repair Instructions

**Attribute ranked without evidence:**
Either find the supporting POV section / research signal and cite it in Notes, or blank the row. A rank with no traceable basis is not allowed.

**"TBD" written into a table cell:**
Replace with a blank cell. "Not yet assessed" belongs in the Assessment Basis block at the bottom, not in the scorecard body.

**Snapshot counts don't match the table:**
Recount directly from the Status column. Assessed = non-blank rows; tallies by color; avg rank = mean of assessed numeric ranks. Fix the snapshot to match the table, never the reverse.

**Invented fact in a Notes cell:**
Remove it. Notes may only restate or cite what the POV or research established. If the partner's exec sponsor is unknown, the Executive Sponsor row stays blank and is listed under "Not yet assessed."

**Confidence not calibrated:**
Start at 0.5 when fewer than half the attributes are assessed; +0.1 per quartile of attributes that are evidence-backed; cap at 0.85 unless the partner has demonstrated the solution and named pilot customers. Name the assumptions the score rests on.
