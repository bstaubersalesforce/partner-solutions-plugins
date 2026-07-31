# Kit check.sh spec — validation contract

This document defines what a generated kit's `check.sh` must validate. The scaffolder renders a `check.sh` template that asserts exactly the conditional shape it stamped — so a kit with `needs_org:false` does **not** assert `docs/org-provisioning.md` exists (no false alarms).

Task 10's meta-check verifies this contract: it exercises the scaffolder on fixtures spanning the condition axes, then runs each golden kit's own `check.sh` and asserts it's green.

## Invariant assertions (always present)

1. **Required top-level docs exist:** `README.md`, `GUIDE.md`, `FACILITATOR.md`, `LESSONS-LEARNED.md`.
2. **Config present:** `config/kit.json` exists and is valid JSON.
3. **Scripts present + bash-syntax-valid:** the generated kit includes `lib/common.sh`, `00-preflight.sh`, and (if `needs_org:true`) `deploy.sh` and `assign-perms.sh` in its scripts directory (from `templates/scripts/*.sh.tmpl`). For each script in the OUTPUT kit, run `bash -n <script>` and assert zero exit.
4. **Internal markdown link resolution:** for every `*.md` (excluding `.notes/`, `.git/`, `node_modules/`), extract relative-path internal links `](target)` (skip `http*`, `mailto:`, `#`-only) and assert the target file exists (resolve relative to the link's source file, fallback to repo root).

## Conditional assertions

5. **Org-provisioning doc:** `docs/org-provisioning.md` exists **iff `needs_org:true`**. When `needs_org:false`, the check does **not** assert this file (educate-only / facilitator-demo / shared-backend kits do not provision participant orgs).
6. **Framework/buildability docs:** `docs/framework.md` and `docs/buildability-matrix.md` are **always present as stubs** (author mode fills them). The check always asserts their existence.
7. **Content directories:** assert each `content_dirs` entry (e.g., `slides/`, `commercial/`, `web/`, `showcase/`, `prework/`) exists iff the toggle is `true`. When `false`, skip the assertion.

## Helpers (modeled from headless360's check.sh)

- `req <path>` — assert file exists; fail + exit 1 if missing. Print `PASS: file: <path>`.
- `opt <path>` — if file exists, `PASS`; else `WARN: not yet: <path>` (warn, do not fail).
- Internal-link resolution: iterate all `*.md`, extract relative targets, stat `$dir/$target` or `$ROOT/$target`; collect broken links, fail if any.

## Golden-file coverage (R-TEST-04)

The test suite's fixtures must span the condition axes:
- One `needs_org:true` full multi-surface kit → check.sh asserts org-provisioning doc + deploy scripts.
- One `needs_org:false` educate-only kit → check.sh does **not** assert those files.

Both fixtures' generated `check.sh` must pass when run against their own rendered tree (meta-check).
