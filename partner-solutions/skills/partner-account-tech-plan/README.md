# partner-account-tech-plan

Assembles a **Partner Account Tech Plan** for a Tier-1 / strategic ISV or OEM partner. It does
not re-implement the deliverable-forge family — it **orchestrates** the existing skills as
subagents (`partner-blocker-forge`, `tech-strat-pov-forge` and its commercial / red-team /
readiness / architecture stages, `pie-poc-forge`, `workshop-forge`), adds a built-in Org62
case scan and a trust/relationship-posture overlay, and binds everything into one coherent,
executive-ready, *living* plan framed as a Salesforce **V2MOM**.

The plan leads with a **Theory of Growth**, nests each workstream's KPIs as Measures under its
Method, maps every gap to a closure action with a named owner and horizon, and sets a QBR
re-review cadence so it stays current. Output is one internal plan document, optionally posted
as an internal Slack canvas.

## Invoke
`/partner-account-tech-plan`

Give it the partner name (required) and, ideally, the Org62 Account ID, Slack deal channels,
background notes, and the PAM. Missing inputs are flagged, not blocking.

## Tier
Built as a Tier 3 (Platform) skill — a stage-router that orchestrates subagents and produces
multiple distinct artifacts (see the skill-forge tier model).

## Design & dogfood
The shape was proven against a real engagement (Riskonnect) before the skill was authored.
Design + plan are archived under `docs/superpowers/specs/` and `docs/superpowers/plans/`.

## Validating
```bash
python3 tests/validate_skill.py
```
A pre-commit hook runs this automatically; activate it once with
`git config core.hooksPath .githooks`.

## Data safety
Read-only against Org62 (production). Raw case captures and any live credentials go to a
gitignored `.notes/` directory only; partner-facing versions are scrubbed first.
