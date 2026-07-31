# Gaps document — ingest & extend the Tech & Arch Assessment

Produce the `07-gaps-document` artifact.

> **Voice:** any narrative/lead-in prose is human-facing — write it in the **Delivery Voice** (SKILL.md): lead each section with the highest-severity gap, name what it blocks, answer "so what?". The gap rows stay factual; an unresolved gap is stated as open, never papered over.

## If the Technical & Architectural Assessment is provided
Ingest its Part 1 (Well-Architected gaps), Part 3 (build-ready spec gaps), and Part 4 (gap-closing roadmap). Carry forward each open `[TBD]` and Top-3 technical risk as a gap row.

## If it is absent
Build the gaps doc from the build plan alone and set `confidence` lower; add a banner: "Tech & Arch Assessment not provided — gaps derived from build plan only; confidence reduced."

## Gap categories (each gets a section)
- **Open questions** — unresolved decisions blocking build.
- **Technical gaps** — missing architecture detail, unproven integrations, undefined data model.
- **Architectural items** — scale, security topology, residency, packaging decisions still open.

## Output format
Per gap: id | category | description | blocks (what it blocks) | owner | target. Lead each section with the single highest-severity gap.
