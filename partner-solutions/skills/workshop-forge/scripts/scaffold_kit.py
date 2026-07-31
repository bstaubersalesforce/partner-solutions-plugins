#!/usr/bin/env python3
"""Deterministic workshop-kit scaffolder. Stdlib only. Idempotent, no deletes."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TPL  = os.path.join(os.path.dirname(HERE), "templates")

VALID_MODES = {"lab", "engagement"}

def _render(tpl_rel, tokens):
    """Render a template by substituting all {{TOKEN}} with values from tokens dict."""
    with open(os.path.join(TPL, tpl_rel), encoding="utf-8") as f:
        s = f.read()
    for k, v in tokens.items():
        s = s.replace("{{"+k+"}}", str(v))
    if not s.endswith("\n"):
        s += "\n"
    return s

def _write(out_dir, rel, content):
    """Write content to out_dir/rel, creating parent directories as needed."""
    p = os.path.join(out_dir, rel)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def _validate(cfg):
    """
    Validate required fields in the kit config overlay.
    Raises ValueError with clear message on violation.
    """
    # Check required top-level scalar keys
    required = ["name", "title", "mode", "duration"]
    for k in required:
        if k not in cfg:
            raise ValueError(f"Error: kit.json missing required field '{k}'")
        if not cfg[k] or (isinstance(cfg[k], str) and not cfg[k].strip()):
            raise ValueError(f"Error: kit.json field '{k}' cannot be empty")

    # Check modules have required fields
    for i, m in enumerate(cfg.get("modules", [])):
        if "n" not in m:
            raise ValueError(f"Error: module {i} missing required field 'n'")
        if "title" not in m:
            raise ValueError(f"Error: module {i} (n={m.get('n', '?')}) missing required field 'title'")
        if not m["title"] or (isinstance(m["title"], str) and not m["title"].strip()):
            raise ValueError(f"Error: module {i} field 'title' cannot be empty")
        if "optional" in m and not isinstance(m["optional"], bool):
            raise ValueError(f"Error: module {i} (n={m.get('n', '?')}) field 'optional' must be true/false")
        if "modes" in m:
            modes = m["modes"]
            if not isinstance(modes, list) or not modes:
                raise ValueError(f"Error: module {i} (n={m.get('n', '?')}) field 'modes' must be a non-empty list")
            bad = [x for x in modes if x not in VALID_MODES]
            if bad:
                raise ValueError(f"Error: module {i} (n={m.get('n', '?')}) field 'modes' has unknown mode(s) {bad}; valid: {sorted(VALID_MODES)}")

def _slug(s):
    """
    Slugify a string for use in identifiers/paths/bash.
    Lowercase, replace runs of non-alphanumeric with underscore, strip edges.
    """
    import re
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")

def _safe_path(s):
    """
    Sanitize a path string for use in bash scripts.
    Permits only [A-Za-z0-9/_.-] to preserve legitimate paths while stripping shell metacharacters.
    Examples:
      "sfdx/" → "sfdx/"
      "sfdx/force-app" → "sfdx/force-app"
      "sfdx/$(echo PWNED)" → "sfdx/echoPWNED"
    """
    import re
    # Strip all characters except alphanumeric, /, _, ., and -
    return re.sub(r"[^A-Za-z0-9/_.-]", "", s)

def _tokens(cfg):
    """
    Build the complete token substitution dict from config.
    Covers 60 base tokens (initialized as stubs, then selectively overridden) plus
    CONTENT_DIR_CHECKS (computed conditionally below). REQUIRED_FILES is built separately
    in _render_check. Total: 62 tokens in templates.
    Tokens that are author-mode content use stub markers.
    """
    # Start with 60 base tokens as stubs
    canonical = [
        "BUILD_ARTIFACT_DESCRIPTION", "BUILDABILITY_MATRIX_TABLE", "BUILDABILITY_REFERENCES",
        "CHECKPOINT_TROUBLESHOOTING", "COMMERCIAL_SECTION", "CONFIG_SUMMARY",
        "CONTENT_DIRS_JSON", "CONTENT_DIRS_LIST",
        "CONTINGENCY_SECTION", "DEFAULT_ORG_ALIAS", "DEPLOY_SOURCE_DIR",
        "DRY_RUN_ARC", "DURATION", "EDUCATE_TOPICS", "FACILITATOR_PURPOSE",
        "FACILITATOR_RATIO", "FRAMEWORK_APPLICATION_GUIDE", "FRAMEWORK_DOC_NOTE",
        "FRAMEWORK_EXAMPLES", "FRAMEWORK_KIT_CONNECTION", "FRAMEWORK_OVERVIEW",
        "FRAMEWORK_TIERS", "FRAMEWORK_TITLE", "HONESTY_NOTES", "KEY_CAVEATS",
        "KIT_DESCRIPTION", "KIT_NAME", "KIT_TITLE", "KIT_TOPIC",
        "LESSONS_SEEDED", "MODE", "MODULE_ARC_SUMMARY", "MODULE_LIST",
        "MODULES_JSON", "NEEDS_ORG", "ORG_PREFLIGHT_BLOCK", "ORG_PROVISIONING_NOTE",
        "ORG_SHAPE_DETAILS", "PARTNER_OVERLAY", "PERMSET_NAME", "PREFLIGHT_VERIFICATION_COMMANDS",
        "PREREQUISITES_SUMMARY", "PROVISIONING_CHECKLIST", "PROVISIONING_MODEL",
        "PROVISIONING_MODEL_DESCRIPTION", "PROVISIONING_TROUBLESHOOTING", "QUICK_START_COMMANDS",
        "REFERENCE_BUILD_PATH", "REFERENCE_BUILD_SOURCE", "REFERENCE_BUILD_SUMMARY",
        "REQUIRED_FEATURES_JSON", "REQUIRED_FEATURES_LIST",
        "RUN_OF_SHOW", "SCRIPTS_SUMMARY", "SFDX_PROJECT_DIR",
        "SHOWCASE_DESCRIPTION", "SHOWCASE_MECHANICS", "SURFACES_JSON",
        "VERIFICATION_CHECKLIST", "VERIFICATION_DATE"
    ]

    # Initialize all as author-mode stubs
    tokens = {k: "_(author mode fills this)_" for k in canonical}

    # Now override with computed values from cfg
    modules = cfg.get("modules", [])
    # Build MODULE_LIST as full sections: header + stub comment + checkpoint line if needed
    kit_mode = cfg.get("mode")
    module_sections = []
    for m in modules:
        gate = m.get("modes")
        if gate and kit_mode not in gate:
            continue  # mode-gated out for this kit's mode
        title = m["title"] + (" (Optional)" if m.get("optional") else "")
        section = f"## Module {m['n']}: {title}\n\n<!-- body stub: author mode fills this -->"
        if m.get("checkpoint"):
            section += "\n\n🔴 **Checkpoint:** _(reason to be filled by author)_"
        module_sections.append(section)
    module_list = "\n\n".join(module_sections)

    prov = cfg.get("provisioning", {})
    needs_org = prov.get("needs_org", False)
    prov_model = prov.get("model", "none")
    required_features = prov.get("required_features", [])

    surfaces = cfg.get("surfaces", {})
    content_dirs = cfg.get("content_dirs", {})
    ref_build = cfg.get("reference_build", {})

    # Scrub scalar values: strip newlines to prevent injection
    def scrub(v):
        if isinstance(v, str):
            return v.replace("\n", " ").replace("\r", " ")
        return v

    # Compute content dirs list and checks (sanitize keys)
    content_dirs_list = ""
    content_dir_checks = ""
    if content_dirs:
        enabled = [(k, _slug(k)) for k, on in content_dirs.items() if on]
        content_dirs_list = "\n".join(
            f"- **`{slugged}/`** — content directory"
            for k, slugged in enabled
        )
        if enabled:
            # Build check assertions for each enabled content dir (use slugged names)
            checks = [f'[ -d "$ROOT/{slugged}" ] && pass "content dir: {slugged}/" || {{ fail "missing content dir: {slugged}/"; FAILED=1; }}' for k, slugged in enabled]
            content_dir_checks = "\necho \"== content dirs ==\"\n" + "\n".join(checks)

    # Build no-org-aware tokens for .env.example, README quick start, and 00-preflight.sh
    # QUICK_START_COMMANDS is author-mode filled, so use stub for now
    quick_start_commands_stub = "bash scripts/00-preflight.sh  # verify setup\n# additional steps filled by author"

    if needs_org:
        env_example_body = f"# Copy to .env and set your assigned org alias\nORG_ALIAS=workshop"
        quick_start_section = f"""```bash
cp .env.example .env          # set ORG_ALIAS to your assigned org alias
{quick_start_commands_stub}
```"""
        org_resolution_line = 'ORG="$(resolve_org "$@")"'
        tooling_checks = 'command -v sf >/dev/null 2>&1 && pass "sf CLI present" || { fail "sf CLI not found — https://developer.salesforce.com/tools/salesforcecli"; FAILED=1; }'
        preflight_purpose_suffix = " + org connectivity"
        org_preflight_block = """[ -n "$ORG" ] || { fail "no org (pass --org <alias> or set ORG_ALIAS in .env)"; FAILED=1; }
if [ -n "$ORG" ]; then
  sf org display --target-org "$ORG" >/dev/null 2>&1 && pass "org connectivity: $ORG" || { fail "cannot connect to org $ORG"; FAILED=1; }
fi"""
    else:
        env_example_body = "# No participant orgs required for this educate-only kit."
        quick_start_section = f"""```bash
# No org setup needed — this is an educate-only workshop
{quick_start_commands_stub}
```"""
        org_resolution_line = "# No org needed for this educate-only kit"
        tooling_checks = '# Educate-only: no tooling checks needed\npass "educate-only kit (no org required)"'
        preflight_purpose_suffix = ""
        org_preflight_block = ""

    # Override computed values (use slugged name for identifiers)
    kit_name_slug = _slug(cfg["name"])
    # Sanitize path values that reach bash scripts (D-01: harden against shell metacharacters)
    safe_ref_build_path = _safe_path(ref_build.get("path", "sfdx/"))
    safe_sfdx_project_dir = _safe_path(ref_build.get("path", "sfdx/").rstrip("/"))
    safe_deploy_source_dir = _safe_path("force-app")

    tokens.update({
        "KIT_NAME": kit_name_slug,  # slugged for use in bash/paths
        "KIT_TITLE": scrub(cfg["title"]),  # human title, keep as-is but scrub newlines
        "MODE": scrub(cfg["mode"]),
        "DURATION": scrub(cfg["duration"]),
        "PARTNER_OVERLAY": scrub(cfg.get("partner_overlay", "reference")),
        "MODULE_LIST": module_list,
        "MODULES_JSON": json.dumps(modules, indent=2),
        "PROVISIONING_MODEL": prov_model,
        "NEEDS_ORG": str(needs_org).lower(),
        "REQUIRED_FEATURES_JSON": json.dumps(required_features, indent=2),
        "REQUIRED_FEATURES_LIST": "\n".join(f"- {scrub(f)}" for f in required_features) if required_features else "_(none)_",
        "SURFACES_JSON": json.dumps(surfaces, indent=2),
        "CONTENT_DIRS_JSON": json.dumps(content_dirs, indent=2),
        "CONTENT_DIRS_LIST": content_dirs_list if content_dirs_list else "",
        "CONTENT_DIR_CHECKS": content_dir_checks,
        "REFERENCE_BUILD_SOURCE": scrub(ref_build.get("source", "none")),
        "REFERENCE_BUILD_PATH": safe_ref_build_path,
        "DEFAULT_ORG_ALIAS": "workshop",
        "SFDX_PROJECT_DIR": safe_sfdx_project_dir,
        "DEPLOY_SOURCE_DIR": safe_deploy_source_dir,
        "PERMSET_NAME": f"{kit_name_slug}_user",  # slugged name for permset
        "ORG_PREFLIGHT_BLOCK": org_preflight_block,
        "ORG_PROVISIONING_NOTE": f"**Org required:** {'Yes' if needs_org else 'No'}" if needs_org else "",
        "CONFIG_SUMMARY": "overlay JSON (name, duration, surfaces, modules, provisioning model)",
        "KIT_TOPIC": scrub(cfg["title"]),
        "VERIFICATION_DATE": "_(author sets at build time)_",
        # FIX #3: no-org-aware tokens
        "ENV_EXAMPLE_BODY": env_example_body,
        "QUICK_START_SECTION": quick_start_section,
        "QUICK_START_COMMANDS": quick_start_commands_stub,  # for legacy/other uses
        "ORG_RESOLUTION_LINE": org_resolution_line,
        "TOOLING_CHECKS": tooling_checks,
        "PREFLIGHT_PURPOSE_SUFFIX": preflight_purpose_suffix,
    })

    return tokens

# Always-present templates
ALWAYS = [
    ("README.md.tmpl", "README.md"),
    ("GUIDE.md.tmpl", "GUIDE.md"),
    ("FACILITATOR.md.tmpl", "FACILITATOR.md"),
    ("LESSONS-LEARNED.md.tmpl", "LESSONS-LEARNED.md"),
    ("KNOWN-GAPS.md.tmpl", "KNOWN-GAPS.md"),
    ("env.example.tmpl", ".env.example"),
    ("gitignore.tmpl", ".gitignore"),
    ("docs/framework.md.tmpl", "docs/framework.md"),
    ("docs/buildability-matrix.md.tmpl", "docs/buildability-matrix.md"),
    ("scripts/lib/common.sh.tmpl", "scripts/lib/common.sh"),
    ("scripts/00-preflight.sh.tmpl", "scripts/00-preflight.sh")
]

def render_kit(kit_json_path, out_dir):
    """
    Render the workshop kit from overlay JSON to out_dir.
    Returns sorted list of relative paths written.
    """
    try:
        with open(kit_json_path, encoding="utf-8") as f:
            cfg = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error: kit.json is not valid JSON: {e}")

    _validate(cfg)
    tok = _tokens(cfg)
    written = []

    # Render always-present files
    for tpl, rel in sorted(ALWAYS):
        _write(out_dir, rel, _render(tpl, tok))
        written.append(rel)

    # Write config/kit.json (canonical, sorted for byte-stability)
    _write(out_dir, "config/kit.json", json.dumps(cfg, indent=2, sort_keys=True) + "\n")
    written.append("config/kit.json")

    # Conditional rendering: org-related files
    prov = cfg.get("provisioning", {})
    if prov.get("needs_org"):
        _write(out_dir, "docs/org-provisioning.md", _render("docs/org-provisioning.md.tmpl", tok))
        written.append("docs/org-provisioning.md")
        _write(out_dir, "docs/credential-setup-cookbook.md", _render("docs/credential-setup-cookbook.md.tmpl", tok))
        written.append("docs/credential-setup-cookbook.md")
        for tpl, rel in [("scripts/01-check-env.sh.tmpl", "scripts/01-check-env.sh"),
                         ("scripts/02-deploy.sh.tmpl", "scripts/02-deploy.sh"),
                         ("scripts/03-assign-perms.sh.tmpl", "scripts/03-assign-perms.sh")]:
            _write(out_dir, rel, _render(tpl, tok))
            written.append(rel)

    # Conditional rendering: content dirs (use slugged names)
    for dirname, on in cfg.get("content_dirs", {}).items():
        if on:
            slugged = _slug(dirname)
            _write(out_dir, f"{slugged}/.gitkeep", "")
            written.append(f"{slugged}/.gitkeep")

    # Conditional rendering: sfdx placeholder
    if cfg.get("reference_build", {}).get("source") != "none":
        _write(out_dir, "sfdx/.gitkeep", "")
        written.append("sfdx/.gitkeep")

    # Conditional rendering: sample-data directory
    sample_data = cfg.get("reference_build", {}).get("sample_data_path")
    if sample_data and str(sample_data).strip():
        _write(out_dir, "data/.gitkeep", "")
        written.append("data/.gitkeep")
        _write(out_dir, "data/README.md", _render("data/README.md.tmpl", tok))
        written.append("data/README.md")

    # Render check.sh (overlay-driven required-file list)
    written += _render_check(out_dir, cfg, tok)

    return sorted(written)

def _render_check(out_dir, cfg, tok):
    """
    Render scripts/check.sh with overlay-driven REQUIRED_FILES list.
    Base required list derived from ALWAYS tuple (single source of truth).
    """
    # Derive base list from ALWAYS (output paths, excluding scripts/check.sh itself)
    req = [rel for tpl, rel in ALWAYS]
    # Add config/kit.json (written separately)
    req.append("config/kit.json")
    # Append org-related files if needed
    if cfg.get("provisioning", {}).get("needs_org"):
        req += ["docs/org-provisioning.md", "docs/credential-setup-cookbook.md", "scripts/01-check-env.sh", "scripts/02-deploy.sh", "scripts/03-assign-perms.sh"]
    _sdp = cfg.get("reference_build", {}).get("sample_data_path")
    if _sdp and str(_sdp).strip():
        req.append("data/README.md")
    tok["REQUIRED_FILES"] = " ".join(req)
    _write(out_dir, "scripts/check.sh", _render("scripts/check.sh.tmpl", tok))
    return ["scripts/check.sh"]

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: scaffold_kit.py <kit.json> <out_dir>")
        sys.exit(1)
    out = render_kit(sys.argv[1], sys.argv[2])
    print("\n".join(out))
