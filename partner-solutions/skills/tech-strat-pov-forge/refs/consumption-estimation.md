# Consumption Estimation — Directional Rate Card

> **Directional only.** This ref lets Stage 18 produce order-of-magnitude
> consumption pre-estimates that *seed* the official Agentforce Credit Estimator
> and Data 360 calculator. It does **not** produce dollar / PUPM / contract
> pricing — `sf-flex-estimator` owns authoritative Flex-Credit cost sizing. If a
> rate here ever diverges from `sf-flex-estimator`, that skill wins; keep the two
> in sync.

## Agentforce — action / prompt credits

| Component | Credits | Note |
|-----------|--------:|------|
| 1 Agentforce Action (production) | 20 | Covers the whole action execution, including any Flow/Apex/prompt bundled inside it |
| 1 Agentforce Action (sandbox) | 16 | 20% off production |
| 1 standalone prompt — Basic | 2 | LLM inference not initiated by an action |
| 1 standalone prompt — Standard | 4 | Higher-performance models |
| 1 standalone prompt — Advanced | 16 | Advanced-tier models |

**Volume → credits (per opportunity, per anchored band):**

```
Total monthly actions = U × F × A × #Entities
Total annual actions   = Total monthly actions × 12
Annual action credits  = Total annual actions × 20         (× 0.8 for sandbox)
Annual prompt credits  = Total annual prompts × (2 | 4 | 16 by tier)
Directional credit band = low–high across reasonable A / prompt-tier assumptions
```

- `U` = est. users per entity
- `F` = monthly invocations per user
- `A` = internal actions per invocation
- `#Entities` = count of the scaling unit (branches, hubs, sites, seats, …)

## Data 360 — volume × frequency × multiplier

```
Annual credits = (Data Volume in millions of rows) × Run Frequency × Usage-Type Multiplier
```

Run Frequency = number of runs per year (e.g. 365 daily, 26 bi-weekly, 12 monthly).
Sandbox usage = 20% off.

**Usage-type multipliers — credits per million rows processed:**

| Usage type | Credits / 1M rows |
|------------|------------------:|
| Profile Unification | 100,000 |
| Streaming Data Pipeline | 5,000 |
| Batch Data Pipeline | 2,000 |
| Streaming Calculated Insights | 800 |
| Streaming Actions | 800 |
| Real-Time Profile API | 900 |
| Batch Data Transforms | 400 |
| Data Federation | 70 |
| Data Shares | 70 |
| Unstructured Data Processed | 60 |
| Segmentation | 20 |
| Batch Calculated Insights | 15 |
| Batch Activation | 10 |
| Data Queries | 2 |
| Internal Data Pipeline | 0 |

## Bottom-up method (journey → step → component)

1. Document each user journey the solution drives.
2. Segment each journey into discrete steps.
3. Map the Agentforce component to each step (Action = 20, standalone prompt = 2/4/16; an action's bundled prompt is already inside the 20).
4. Sum to credits-per-journey-run; multiply by monthly volume, then ×12.

## Customer-size bands (abstract)

S / M / L / XL are **relative labels** for the target customer's size — they carry
**no reference entity-count ranges**. Anchor every estimate to the single band
that fits the POV's target customer, and state it. The concrete `#Entities`
figure comes from the target customer in the POV (or a stated assumption), **not**
from a band lookup. To scale to another band, change `#Entities` (and optionally
U/F); the formula is unchanged.

## Worked example (synthetic — illustration only)

A retail bank operating **N branches** runs a lifecycle-handoff agent:
6 users/branch × 2 runs/user/month × 5 actions = 60 actions/branch/month.
Across N branches → 60 × N monthly actions → ×12 annual → ×20 credits.
For N = 3,000: 180,000 monthly actions → 2,160,000 annual → 43,200,000 action
credits/year (directional). Scale N for a smaller/larger band; rates unchanged.
