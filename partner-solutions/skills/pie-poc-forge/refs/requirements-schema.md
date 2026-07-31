# requirements.json — schema & normalization

The normalized source-of-truth for a PoC engagement. Lives at the package root and is listed in `.forceignore` so it never deploys.

## Top-level shape
- `partner` — string (slug-able partner name)
- `buildTypes` — array subset of `["agent","data360","platform"]`
- `decisions` — `{ packaging: "1GP"|"2GP", target: "partnerOrg"|"demoInstance", agentInScope: bool, orgTemplateId: string|null }` (`orgTemplateId` = an existing org template / scratch-org snapshot to clone from; null = standard edition-based scratch def. See `refs/dev-environment.md`.)
- `appType` — string (ISVforce / OEM/Embedded / Reseller / Consumption / Mixed) — drives whether the org-template prompt is emphasized
- `mvpOpinion` — the confirmed PoC scope (set after Phase A step 4)
- `features` — array of `{ id, title, persona, userStory, acceptanceCriteria[] }`
- `objects` — array of `{ apiName, fields[], relationships[] }`
- `components` — array of `{ name, type, responsibility, phase }`
- `integrations` — array of `{ system, type, direction, auth }`, plus optional MCP/stand-in fields: `isMock` (bool — true when the endpoint is a demo stand-in, not the real partner service), `mcpUrl`, `oauthTokenUrl`, `clientId` (NEVER the secret), `serverInfo`, `tools` (array from live `tools/list`), `demoClients`, and a `productionTarget` note describing the real server's intended shape when `isMock` is true. See `refs/mcp-integration.md`.
- `dependencies` — array of `{ name, type, mustHave, status }`
- `securitySignals` — array of free-text risks for the security-review generator
- `confidence` — float 0.0–1.0 (lowered if Tech & Arch Assessment absent)
- `fileHashes` — map of `generated/file/path -> sha256` (edit-preservation; see below)

## Normalization rules
- Map POV MVP Build Plan sections → fields above (Feature Breakdown → features, Technical Requirements → objects/components/integrations, Dependencies & Blockers → dependencies).
- Agentforce Labs output → one agent component + agentInScope=true.
- Pasted free-text → best-effort parse; flag every inferred field as `"inferred": true`.

## Edit-preservation (fileHashes)
On generation, store `sha256` of each written file. On re-run, before overwriting, recompute and compare; if it differs, the file was hand-edited — do not overwrite (see refs/workflow-dispatch.md Phase C).

**Populating fileHashes is mandatory and is the LAST step of Phase B synthesis** — not optional. After every generated file (force-app source, manifests, and each `docs/*.md`/`*.html`) is written, compute its sha256 and record it in `fileHashes` keyed by package-relative path, then save `requirements.json`. A generate run that leaves `fileHashes` empty is incomplete: the entire Phase C edit-preservation mechanism depends on it. Compute with the stdlib only, e.g.:
```python
import hashlib, json, os
hashes = {}
for root, _, files in os.walk(pkg_root):
    for f in files:
        p = os.path.join(root, f)
        rel = os.path.relpath(p, pkg_root)
        if rel == "requirements.json":  # never hash the state file itself
            continue
        hashes[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
```

## finalize (Phase D, optional)
Records the last Phase-D finalize run; absent until a finalize run occurs. Shape:
- `date` — run date (YYYY-MM-DD).
- `targetOrg` — `{ "alias": "<alias>", "type": "scratch|sandbox|demo|production", "confirmed": <bool> }`. `confirmed` is true only when a production run was typed-confirmed.
- `gate1` — array of `{ "step", "result": "PASS|FAIL|SKIP", "notes" }`.
- `gate2` — array of the same shape, or `"not-run"` when Gate 1 was not green.
- `ids` — returned identifiers worth keeping (`{ "deployId", "agentId", "mcpRegistrationId" }`), keys present only when produced.
- `stoppedAt` — the step name where the run halted, or `null` if it completed.

This block is informational state for the next finalize run; it is NOT part of `fileHashes` edit-preservation (it records a run, it is not a generated artifact).

## confidence adjustment rule (reproducible)
Start from the POV/source confidence. Apply, deterministically:
- −0.05 if the Technical & Architectural Assessment was NOT provided.
- −0.05 for each unresolved P1-class gap (e.g. an external object reference left unresolved, agent authoring still pending).
Floor at 0.0. Record the starting value and each deduction in `_confidenceNote` so the number is auditable.
