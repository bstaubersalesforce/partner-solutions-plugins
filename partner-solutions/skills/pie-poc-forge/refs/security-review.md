# Security Assessment checklist

Produce the `06-security-review` artifact (titled **"Security Assessment"** — keep the `06-security-review` filename slug for the router registry) from `securitySignals` + the component/integration inventory. Flag issues; do not silently pass.

> **Naming:** this is a PIE **Security Assessment** — advisory findings for the PoC. "Security Review" has a specific meaning in the release process; do not use that label for this artifact.

> **Voice:** the verdict line and any narrative framing are human-facing prose — write them in the **Delivery Voice** (SKILL.md): lead with the verdict, state each risk as a risk (no hedging), quantify or qualify. The finding rows stay factual; do not soften a Critical into advice.

## Checklist (one finding row per applicable item)
- **Sharing model** — every custom object has an explicit sharing decision (private/public/controlled-by-parent).
- **CRUD/FLS** — Apex marked `with sharing`; stubs note `Security.stripInaccessible` / `WITH SECURITY_ENFORCED` obligations.
- **Secrets** — no hardcoded keys; external auth via Named Credential, never inline.
- **OAuth scopes** — least-privilege scopes named for each integration.
- **PII in transit** — flag any payload crossing an org boundary (esp. external AI stacks); recommend minimization.
- **MCP integration surface** — when an MCP integration is present (see `refs/mcp-integration.md`), flag it explicitly: scoped OAuth (least-privilege), Named/External Credential (no inline secrets), PII minimization in the MCP payload, and — for bidirectional/inbound MCP — inbound authentication + replay protection (nonce/timestamp).
- **Shield** — flag regulated data (KYC/AML, lending, health) needing Platform Encryption + Event Monitoring.

## Output format
Table: finding | severity (Critical/High/Medium/Low) | component | recommendation | owner.
End with a "Security Assessment verdict: Go / Conditional-Go / Not-ready" line.
