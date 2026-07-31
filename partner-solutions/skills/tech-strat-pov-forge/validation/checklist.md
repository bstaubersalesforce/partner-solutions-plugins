# Pre-Delivery Validation Checklist

Run every check before delivering. If any check fails, repair the output — do not deliver a failing POV.

## Required Sections Present

- [ ] Problem Statement — present and non-empty
- [ ] Vision Statement — present and non-empty
- [ ] Solution Statement — present and non-empty
- [ ] Benefits — at least 3 named
- [ ] KPIs — at least 2 named
- [ ] Use Cases — at least 1 complete (target: 3)
- [ ] Target Markets — primary market named
- [ ] Personas — at least 2 named
- [ ] Architecture Summary — present with app type specified
- [ ] Commercial Model — app type and licensing model specified
- [ ] Confidence Score — stated with named assumptions

## Quality Checks

### Vision Statement
- [ ] Names a specific persona (not "customers" or "users")
- [ ] Names a specific capability (not "leverage," "harness," or "unlock")
- [ ] Names a measurable outcome (not "transform," "revolutionize," "next-gen," "end-to-end")
- [ ] Is one sentence

### Use Cases
- [ ] Each use case names a persona
- [ ] Each use case frames an outcome, not a feature ("resulting in [measurable result]" is present)
- [ ] No use case is a restatement of the Solution Statement

### Problem Statement
- [ ] Names a specific persona or role
- [ ] Names a specific pain — not a market observation
- [ ] Names a measurable consequence

### Architecture
- [ ] Salesforce cloud/SKU dependencies are named (not "various Salesforce products")
- [ ] App type is specified (native / composite / hybrid)

### Commercial Model
- [ ] App type specified (ISVforce / OEM / Mixed / etc.)
- [ ] Licensing model specified (PUPM / POPM / Tiered / etc.)

### Proof Points
- [ ] At least one named pilot customer OR one named existing customer validation is present
- [ ] If none available, section is explicitly flagged "TBD — owner: [name]" not silently omitted

### Blueprint Alignment
- [ ] At least one specific Blueprint capability gap is named
- [ ] If unknown, flagged as "TBD — owner: [name]" not silently omitted

## Framing Checks

- [ ] Problem Statement does not pre-commit to the solution (e.g., does not say "we need [solution name] because...")
- [ ] Vision Statement is specific to this partner's solution, not generic to the category
- [ ] Use cases are differentiated — each names a different persona or workflow

## Failure → Repair Instructions

**Vague Vision Statement:** Return to scripts/discovery-questions.md → Vision section. Ask the specific persona + outcome question. Redraft.

**Feature-framed Use Cases:** Reframe using the template: "When [persona] needs to [job-to-be-done], [solution] provides [capability], resulting in [measurable outcome]."

**Missing Proof Points:** Flag explicitly as TBD. Do not invent customer names. Do not silently omit the section.

**Missing Architecture:** Flag as TBD with note: "To be completed with partner's technical lead." Do not omit the section header.

**Missing Commercial Model:** Flag as TBD. This is a required exit criterion — note it as a blocker for advancing the opportunity to 03-Contract.
