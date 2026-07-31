# Full Multi-Surface Workshop — Org Provisioning & Shape

## Provisioning Model: sdo

_(author mode fills this)_

## Required Org Features

- Data Cloud
- Agentforce
- MCP

## Provisioning Checklist

_(author mode fills this)_

## Universal Rules (every org-backed model)

- **Pre-provision + preflight T-minus days, never morning-of.** Provisioning at arrival kills the engagement (data360 lesson).
- **Keep a safety-net reference org** for facilitators to demo / troubleshoot from.
- **The per-org ECA/PKCE/JWT MCP step is never auto-provisioned** (if MCP is load-bearing). Generate a numbered setup script (e.g., `04-mcp-connect-setup.sh`) that guides it.
- **Smoke-test the real flow**, not the status dot. Verify the target capability actually works end-to-end.

## Pre-Workshop Verification

Run the following on each assigned org **before participant arrival**:

```bash
./scripts/00-preflight.sh --org <alias>
_(author mode fills this)_
```

Expected: all green.

## Org Shape Reference

_(author mode fills this)_

## Troubleshooting

_(author mode fills this)_
