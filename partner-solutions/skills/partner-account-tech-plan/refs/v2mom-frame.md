# V2MOM frame

The whole plan is organized as a Salesforce **V2MOM**. This mirrors how Salesforce (and often
the partner) already plans, and it forces the plan to answer "what are we doing, why, and how
will we know it worked" rather than listing activities.

## The five parts

- **Vision** — where the partnership is going. One or two sentences. This is distinct from the
  Theory of Growth at the very top of the plan (which is the *narrative* of potential); the
  Vision is the single destination statement.
- **Values** — the principles that govern how we partner. Always includes
  **elevation-not-encroachment** (see `trust-posture.md`): we make the partner the platform
  leader in their domain; we do not compete into their whitespace.
- **Methods** — the workstreams. Each Method is a lane of work (e.g. "Tech-debt &
  package modernization", "Architectural runway", "Product innovation / PLG"). Map Methods to
  the partner's own strategic frame where one exists.
- **Obstacles** — what stands in the way. These are drawn from the Current-State Assessment,
  the Blocker Scan, and the Red Team. Every Obstacle must reappear in the Go-Forward
  Gap-Closure matrix (Stage 7) with a closure action.
- **Measures** — see the convention below.

## Convention: Measures are CHILDREN of their Method

Do **not** collect all KPIs in one flat Measures list at the bottom. **Each Method carries its
own Measures nested beneath it** — the KPIs that tell you *that workstream* is working. Only
**cross-cutting measures** (partnership health: # active exec relationships, # gaps closed per
QBR, consumption growth, joint pipeline) sit at the top-level Measures line.

Rendered shape:

```
Method 1 — <workstream>
  Measures:
    • <KPI> — baseline <x> → target <y> by <horizon>
    • <KPI> — ...
Method 2 — <workstream>
  Measures:
    • ...
Cross-cutting Measures (partnership health)
  • # active exec relationships (target ≥3 before H1)
  • # gaps moved RAG 🔴→🟡→🟢 per QBR
  • consumption growth / joint pipeline
```

## Proposing KPIs when baselines are absent

Partners rarely hand over baselines. Where you lack a specific number, **propose** a KPI and a
target and tag it `[proposed]`. A proposed KPI is a conversation-starter for the next QBR, not
a fabricated fact. Never present a `[proposed]` target as a confirmed metric.
