# Technical & Architectural Assessment (Stage 16)

Lazily loaded by the tech-strat-pov-forge skill. Follow the Execution Principles in `SKILL.md` and the HTML Output Method in `refs/html-output-method.md`. Produces the assessment via `templates/technical-architecture-assessment.md` (the build-consumable source of truth) and `templates/technical-architecture-assessment.html`; validate against `validation/architecture-checklist.md` before delivering.

## Overview
A build-guiding artifact: it evaluates the partner's current-state architecture against Salesforce Well-Architected (3 pillars / 8 qualities), prescribes the target-state Salesforce architecture, and emits a build-ready metadata blueprint plus skeleton stubs. It requires an approved POV and feeds the MVP Build Plan (Stage 8).

## Process

1. **Load inputs.** Read the approved POV (always) — especially "Partner App Strategy & Technical Summary," "MVP & Development Priorities," and architecture-related sections. If a Discovery Document exists, load its Theme B (Technical Architecture & Readiness, Salesforce Ecosystem Footprint, Data Landscape & Sources). If the POV's technical sections are thin and no Discovery exists, pull from `scripts/discovery-questions.md` (Technical Assessment block) and flag `[TBD]`s.
2. **Targeted technical research.** Fill gaps the POV/Discovery did not cover — current stack, named integration systems, public API/security signals, scale indicators. Output one plain-English status line per action; note and skip failed fetches.
3. **Current-state assessment (Part 1).** Walk the eight Well-Architected qualities per the method above.
4. **Score the RAG (Part 0).** Derive each quality's 🟢/🟡/🔴 **from its Part 1 finding** (never guessed) — 🟢 Strong, 🟡 Emerging, 🔴 Gap. Roll up to the three pillars, surface the top 3 technical risks (quality + severity), and state the build-readiness verdict (Go / Conditional-Go / Not-ready).
5. **Design target state (Part 2).** Map POV use cases, solution, and KPIs onto the seven architecture layers. Name concrete Salesforce capabilities; `[TBD]` where the POV under-specifies.
6. **Build-ready spec & stubs (Part 3).** Per the Build-Ready Spec & Stubs rules.
7. **Roadmap + handoff (Part 4).** Sequence the gap-closing work, map each item to the quality it closes, and frame the explicit handoff to the MVP Build Plan (Stage 8).
8. **Target-state architecture diagram.** Build a Mermaid flowchart of the Part 2 layers per `refs/mermaid-diagrams.md` — one node per layer the POV populates, edges showing dependency/data direction. Inject it into the `{{ARCH_DIAGRAM_MERMAID}}` token (HTML) and the ` ```mermaid ` block (Markdown); on Approve, optionally export PNG/SVG via `mmdc` for decks (capability-gated, graceful fallback). Diagram only what the POV supports; `[TBD]` layers render as `[TBD — confirm in build]`, never invented.

**Requires an approved POV** — one that has been through the Stage 7 review or was provided directly by the user. Thinness is **not** a reason to refuse: a POV with sparse or `[TBD]` technical sections still counts. Only when **no** POV exists at all do you stop and tell the user to build the POV first (do not fabricate one). Otherwise proceed even under thin input, surfacing `[TBD]`s. No other refusal conditions.

**Delivery follows the Stage 7 Interactive Review process:**
1. Present the Markdown draft first — do not generate HTML.
2. Prompt: "Review the draft above. Reply with specific changes, or reply **Approve** when ready to commit the HTML version."
3. Apply feedback, show only changed sections, repeat until Approve.
4. On Approve: run `validation/architecture-checklist.md`, then fill `templates/technical-architecture-assessment.html` via the HTML Output Method (`refs/html-output-method.md`) and deliver the file path.
5. Append: overall Well-Architected readiness score (0.0–1.0), named assumptions, explicit `[TBD]` list.

**Core rule: every finding, RAG rating, target-state decision, and stub traces to evidence or is marked `[TBD]` — never invented.**

## Well-Architected Assessment Method

Assess the partner's current-state architecture against the Salesforce **Well-Architected** framework, used as a decision compass. Three pillars, eight qualities:

- **Trusted** (protect stakeholders): **Secure** · **Compliant** · **Reliable**
- **Easy** (deliver value fast): **Intentional** · **Automated** · **Engaging**
- **Adaptable** (evolve with the business): **Resilient** · **Composable**

For **each** of the eight qualities, produce four elements:
- **Finding** — what the current architecture actually does for this quality.
- **Evidence** — sourced from the POV, Discovery (Theme B if present), or research; tag each line `[confirmed]` / `[proposed — confirm]` / `[TBD]`.
- **Pattern / Anti-pattern** — name the Well-Architected pattern the partner follows, or the anti-pattern they exhibit (compass language; be specific, not generic).
- **Gap** — what is missing to be Salesforce-grade for this quality.

A quality with no evidence still renders — **Finding** `[TBD]` with a "what to confirm" note. Never invent a finding or a rating.

**Quality reference (what each quality covers):**
- **Secure** — access control, data protection, org/credential security.
- **Compliant** — legal/ethical/regulatory obligations and data residency.
- **Reliable** — efficient, dependable operation; error handling; governor-limit headroom.
- **Intentional** — delivers business value now and over time; aligned to the POV use cases.
- **Automated** — gets work done faster and at scale; minimal manual intervention.
- **Engaging** — delights users and drives adoption; UX quality.
- **Resilient** — handles change well; loosely coupled; tolerant of platform/API change.
- **Composable** — adjusts quickly with stability; packageability, modularity, reuse.

## Target-State Architecture

Prescribe the Salesforce target architecture across seven layers. Each layer: the recommendation, the POV use case(s)/quality it serves, and `[TBD]` where the POV under-specifies. Name concrete Salesforce capabilities — never "the Salesforce platform" generically.

1. **App type & packaging** — managed package vs. composite vs. hybrid; namespace strategy; 2GP considerations (serves Composable).
2. **Data architecture** — standard vs. custom objects; large-data-volume strategy; Data Cloud where relevant; data residency (serves Reliable, Compliant).
3. **Integration architecture** — named external systems; API style (REST/Platform Events/CDC/Bulk); auth (Named Credentials, OAuth); sync vs. async; middleware if any (serves Resilient).
4. **Component architecture** — division across LWC / Apex / Flow; where logic lives; why (serves Automated, Engaging).
5. **Security & sharing model** — permission sets, sharing model, field/object security, Shield/encryption if needed (serves Secure).
6. **Scale & multi-tenancy** — governor-limit strategy, bulkification, async patterns, horizontal scale for enterprise volume (serves Reliable, Resilient).
7. **AI & data layer** — Agentforce / Einstein / Data Cloud usage and the licenses they require, where applicable (serves Intentional).

## Build-Ready Spec & Stubs

The Markdown output is the build-consumable source of truth. From the Part 2 target state, produce:

- **Metadata blueprint** — a table of custom objects → fields (API name, type, description) → relationships, plus a short ERD-style block. Standard objects reused are named, not redefined.
- **Component inventory** — each LWC / Apex class / Flow with a one-line responsibility and the use case/quality it serves.
- **Integration contracts** — per external system: named API, auth method, sync/async, the Salesforce-side mechanism (e.g., Named Credential + External Service, Platform Event), and the data exchanged.
- **Skeleton stubs** — fenced code blocks: Apex class + method signatures with doc-comment intent (no bodies; bodies are `// TODO (build): …`), LWC component shells (`@api` props + skeleton template), and declarative object/field definitions. Every stub carries the header `// STUB — scaffolding from Architecture Assessment; flesh out in build`.

**Guardrails (so stubs stay scaffolding, not invented product):**
- **Traceability** — every object/field/class/Flow traces to a named POV use case or a Part 2 decision (a Traceability note/column). Traceability values must be **verbatim** — the exact use-case label from the POV or the exact Part 2 layer/decision name; a paraphrased or invented reference fails the check. If it can't be traced, do not emit it.
- **Scaffolding only** — signatures and shells, never fabricated business-logic bodies or invented algorithms.
- **Under-specification** — emit `[TBD — confirm in build]` rather than guessing.
