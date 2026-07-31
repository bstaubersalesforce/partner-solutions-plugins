# MVP / PoC opinion — how to form the recommendation

Produce the `02-mvp-pov-opinion` artifact AND confirm it with the user in Phase A step 4 before generating.

> **Voice:** human-facing prose — write it in the **Delivery Voice** (SKILL.md): lead with the recommendation, quantify or qualify, answer "so what?". Never fabricate a metric to satisfy that — mark `[Pending — … — owner]` instead.

## Method
1. Identify the single "hero" use case — the one that proves the concept end-to-end and exercises the most architectural layers.
2. Recommend building that hero slice first; explicitly name what to CUT from the MVP and why (defer to Horizon 1+).
3. State the proof the PoC must demonstrate (the riskiest assumption it pressure-tests).
4. Be opinionated: give one recommended scope, not a menu. Name the one trade-off a reviewer might push back on.

## Output format
- **Recommended PoC scope:** <hero use case, one sentence>
- **Build first / cut for now** table.
- **What this proves:** <the riskiest assumption>
- **The trade-off worth a conversation:** <one line>
