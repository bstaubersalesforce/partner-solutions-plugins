# Consumption Opportunities Pre-Delivery Validation Checklist

Run every check before delivering the Consumption Opportunities artifact (.md + .html).

## Structure
- [ ] Consumption Opportunity Map table present and ranked (Priority H/M/L)
- [ ] Agentforce Agents section: 2–4 opportunities, each with topics & actions, objects, supporting components, and build steps
- [ ] Data Cloud section: 2–4 opportunities, each with DMOs/streams/sources, mapping & identity resolution, activation target, and build steps
- [ ] Sizing-Band Anchor note present: names the band, the reason, and the #Entities scaling driver
- [ ] Every Agentforce and Data Cloud opportunity has a Directional Estimate: assumptions (U/F/A/#Entities or volume/frequency/usage-type) → volume → credit band
- [ ] Directional estimates are credits-only and labeled directional; assumptions are shown so they can be edited in the real calculator
- [ ] Other Salesforce SKU Opportunities table present (Shield, Backup & Archive, sandboxes, other resellable products) with resellable-by-partner column
- [ ] HTML carries the standardized home-page back-link pill (`{{HOME_HREF}}` → `{SLUG}-index.html`); removed if standalone
- [ ] No `{{PLACEHOLDER}}` tokens remain in the rendered output

## Scope discipline (no overlap)
- [ ] No dollar figures anywhere — "Consumption signal" entries are qualitative and the Directional Estimate is credits-only (dollar/PUPM/contract sizing belongs to sf-flex-estimator)
- [ ] Does not restate the core-solution architecture (that is Stage 16) — only consumption-growth components
- [ ] Does not restate the license pull-through commercial model (that is the POV ISV Commercial Model)
- [ ] Every opportunity is confidence-labeled (`[confirmed]` / `[proposed — confirm]` / `[TBD]`); nothing invented beyond what the POV/vertical supports

## Failure → Repair
**Unfilled token:** Fill from POV/vertical data or mark `[TBD]` with an owner.
**Dollar figure in consumption signal:** Replace with a qualitative signal; point to sf-flex-estimator for sizing.
**Dollar figure in directional estimate:** Convert to a credit band; remove the dollar amount. Point to sf-flex-estimator for cost.
**Missing directional estimate on an Agent/Data opportunity:** Add the assumptions → volume → credit-band block per `refs/consumption-estimation.md`, or mark the assumptions `[TBD]` if the POV lacks the inputs.
**Invented opportunity:** Remove. Only opportunities grounded in the POV or matched vertical may appear.
