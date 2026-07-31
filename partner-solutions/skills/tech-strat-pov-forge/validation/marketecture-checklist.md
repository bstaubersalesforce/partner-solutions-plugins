# Marketecture Pre-Delivery Validation Checklist

Run every check before delivering the Marketecture diagram HTML.
If any check fails, repair before delivering.

## Structure
- [ ] All architecture layers present and populated (no empty layer)
- [ ] No unfilled `{{PLACEHOLDER}}` tokens remain (scan the output)
- [ ] Partner name and "Built on Salesforce" framing present

## Content integrity (matches the POV architecture)
- [ ] Salesforce cloud/SKU dependencies name specific clouds (Platform, Sales, Service, Industry Cloud, Add-On SKUs) — not "Salesforce platform"
- [ ] Integrations name specific external systems/APIs from the POV — not "third-party systems"
- [ ] Application type (Native / Composite / Hybrid) matches the POV Architecture Summary
- [ ] Data model and UI layers reflect what the POV's Architecture Summary states — no invented components
- [ ] Nothing in the diagram contradicts the POV's SF Cloud/SKU Dependencies or External Dependencies

## Failure → Repair
**Vague dependency:** Return to the POV Architecture Summary — SF Cloud/SKU Dependencies; name each specific cloud/SKU and how it is used.
**Invented component:** Remove anything not grounded in the POV Architecture Summary; if the POV is silent, leave the layer minimal rather than fabricating.
