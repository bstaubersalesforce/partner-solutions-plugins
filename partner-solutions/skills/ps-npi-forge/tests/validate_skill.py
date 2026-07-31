#!/usr/bin/env python3
"""
Validation suite for the ps-npi-forge skill. Stdlib-only.

Asserts the structural invariants that must hold for the skill to run correctly and to satisfy the
skill-forge Tier-3 rubric. Validates files, references, and the manifest model — it does NOT judge
LLM output quality.

Run:   python3 tests/validate_skill.py
Exit:  0 = all pass, 1 = one or more failures.
"""
import os, re, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- tiny test harness --------------------------------------------------
RESULTS = []
def check(name):
    def deco(fn):
        RESULTS.append((name, fn)); return fn
    return deco

def read(rel):
    with open(os.path.join(SKILL, rel), encoding="utf-8") as f:
        return f.read()

def exists(rel):
    return os.path.exists(os.path.join(SKILL, rel))

# ---- artifact registry (single source of truth) ------------------------
ARTIFACT_REGISTRY = [
    "00-executive-summary", "01-brief", "02-slide-summary", "03-internal-enablement",
    "04-internal-faq", "05-external-faq", "06-license-entitlements", "07-addon-tiering",
    "08-setup-guide", "09-org-provisioning-validation", "10-partner-profile-pov",
    "11-solution-infographic", "12-marketecture", "13-demand-plan", "14-exec-infographic",
]
STATUS_VOCAB = ["pending", "in_progress", "drafted", "verified", "pulled"]
LOOP_REGISTRY = ["claim_verification", "completeness", "uncertainty", "partner_lens"]
VERDICT_VOCAB = ["pass", "flag", "fail"]

INSTRUCTION_FILES = ["SKILL.md"]
def instructions():
    return "\n".join(read(f) for f in INSTRUCTION_FILES if exists(f))

# ---- R-FM-01: frontmatter ----------------------------------------------
@check("R-FM-01: SKILL.md opens with frontmatter carrying non-empty name + description")
def t_frontmatter():
    s = read("SKILL.md")
    m = re.match(r"^---\n(.*?)\n---\n", s, re.S)
    assert m, "SKILL.md must open with a YAML frontmatter block"
    fm = m.group(1)
    name = re.search(r"^name:\s*(\S.*)$", fm, re.M)
    desc = re.search(r"^description:\s*(\S.*)$", fm, re.M)
    assert name and name.group(1).strip(), "frontmatter missing non-empty name:"
    assert desc and desc.group(1).strip(), "frontmatter missing non-empty description:"

# ---- R-REF-01: refusal conditions present ------------------------------
@check("R-REF-01: SKILL.md states refusal/scope conditions")
def t_refusal_present():
    s = read("SKILL.md").lower()
    assert "refusal" in s or "scope conditions" in s, \
        "SKILL.md must have a refusal/scope-conditions section"
    assert "does not" in s or "do not" in s or "refuse" in s, \
        "refusal section must state what the skill will not do"

# ---- R-REF-02: out-of-scope rules named -------------------------------
@check("R-REF-02: SKILL.md names the four hard out-of-scope rules")
def t_out_of_scope():
    s = read("SKILL.md").lower()
    for needle in ["pricing", "non-official", "read-only", "without confirmation"]:
        assert needle in s, f"refusal section missing rule about: {needle}"
    # the pricing carve-out must be stated: internal business-case inputs allowed as flagged estimates
    assert "business-case" in s or "business case" in s, \
        "refusal section must state the internal-business-case carve-out"
    assert "asp" in s and "halo" in s and "estimate" in s, \
        "carve-out must name ASP + halo ACV as flagged estimates"

# ---- R-ARCH-02: every referenced path exists ----------------------------
@check("R-ARCH-02: every file path referenced in SKILL.md exists")
def t_refs_exist():
    skill = instructions()
    paths = set(re.findall(r"(?:templates|refs|scripts|tests|docs)/[A-Za-z0-9._/-]+", skill))
    missing = [p.rstrip(".") for p in paths if not exists(p.rstrip("."))]
    assert not missing, f"referenced but missing: {sorted(missing)}"

# ---- R-PROC-01: spec->plan archive exists -------------------------------
@check("R-PROC-01: spec->plan archive exists under docs/superpowers/")
def t_spec_plan_archive():
    specs = os.path.join(SKILL, "docs/superpowers/specs")
    plans = os.path.join(SKILL, "docs/superpowers/plans")
    assert os.path.isdir(specs) and any(f.endswith(".md") for f in os.listdir(specs)), \
        "no spec under docs/superpowers/specs/"
    assert os.path.isdir(plans) and any(f.endswith(".md") for f in os.listdir(plans)), \
        "no plan under docs/superpowers/plans/"

# ---- R-MANIFEST: behavioral tests for scripts/manifest.py ---------------
def _load_script(rel, name):
    import importlib.util
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, os.path.join(SKILL, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

@check("R-MANIFEST-01: new_effort seeds all 11 artifacts at pending/0.0")
def t_manifest_new():
    m = _load_script("scripts/manifest.py", "manifest_mod1")
    eff = m.new_effort("summer-26", "agentforce-healthcare-oem", "Health Cloud EE/UE")
    assert eff["release"] == "summer-26"
    assert eff["parent_sku"] == "Health Cloud EE/UE"
    assert set(eff["artifacts"].keys()) == set(ARTIFACT_REGISTRY), "all 11 artifacts must be seeded"
    for a, rec in eff["artifacts"].items():
        assert rec["status"] == "pending", f"{a} should start pending"
        assert rec["confidence"] == 0.0, f"{a} should start at 0.0"

@check("R-MANIFEST-02: round-trip load(dumps(x)) preserves the manifest")
def t_manifest_roundtrip():
    m = _load_script("scripts/manifest.py", "manifest_mod2")
    eff = m.new_effort("summer-26", "x-oem", "Parent EE")
    eff = m.set_status(eff, "01-brief", "drafted")
    eff["artifacts"]["01-brief"]["confidence"] = 0.6
    eff["artifacts"]["09-org-provisioning-validation"]["placeholders"] = [{"item": "Template ID", "owner": "Manish/John", "next_step": "request template ID"}]
    import tempfile, os as _os
    d = tempfile.mkdtemp()
    p = _os.path.join(d, "manifest.yaml")
    open(p, "w").write(m.dumps(eff))
    back = m.load(p)
    assert back["artifacts"]["01-brief"]["status"] == "drafted"
    assert abs(back["artifacts"]["01-brief"]["confidence"] - 0.6) < 1e-9
    assert back["release"] == "summer-26"
    ph = back["artifacts"]["09-org-provisioning-validation"]["placeholders"]
    assert len(ph) == 1, "placeholder lost in round-trip"
    assert ph[0]["item"] == "Template ID" and ph[0]["owner"] == "Manish/John" and ph[0]["next_step"] == "request template ID", "placeholder fields corrupted in round-trip"

@check("R-MANIFEST-03: set_status rejects unknown artifact or status")
def t_manifest_set_status_guard():
    m = _load_script("scripts/manifest.py", "manifest_mod3")
    eff = m.new_effort("r", "p", "parent")
    try:
        m.set_status(eff, "99-nope", "drafted"); assert False, "unknown artifact should raise"
    except ValueError: pass
    try:
        m.set_status(eff, "01-brief", "banana"); assert False, "bad status should raise"
    except ValueError: pass

@check("R-MANIFEST-04: overall_confidence is the weighted floor, ignoring pulled artifacts")
def t_manifest_floor():
    m = _load_script("scripts/manifest.py", "manifest_mod4")
    eff = m.new_effort("r", "p", "parent")
    for a in ARTIFACT_REGISTRY:
        eff["artifacts"][a]["confidence"] = 0.8
        eff["artifacts"][a]["status"] = "verified"
    eff["artifacts"]["06-license-entitlements"]["confidence"] = 0.3   # the floor
    eff = m.set_status(eff, "10-partner-profile-pov", "pulled")        # excluded
    eff["artifacts"]["10-partner-profile-pov"]["confidence"] = 0.0
    assert abs(m.overall_confidence(eff) - 0.3) < 1e-9, "floor should be 0.3, ignoring the pulled artifact"

@check("R-MANIFEST-05: manifest template + fixture exist and parse")
def t_manifest_files():
    m = _load_script("scripts/manifest.py", "manifest_mod5")
    assert exists("templates/manifest.yaml"), "templates/manifest.yaml missing"
    assert exists("tests/fixtures/manifest/sample-manifest.yaml"), "sample fixture missing"
    parsed = m.load(os.path.join(SKILL, "tests/fixtures/manifest/sample-manifest.yaml"))
    assert set(parsed["artifacts"].keys()) == set(ARTIFACT_REGISTRY), "fixture must list all 11 artifacts"

@check("R-MANIFEST-06: manifest.py constants match the validation suite's registry/vocab")
def t_manifest_constant_parity():
    m = _load_script("scripts/manifest.py", "manifest_mod6")
    assert m.ARTIFACT_REGISTRY == ARTIFACT_REGISTRY, "ARTIFACT_REGISTRY drift between manifest.py and validate_skill.py"
    assert m.STATUS_VOCAB == STATUS_VOCAB, "STATUS_VOCAB drift between manifest.py and validate_skill.py"
    assert m.LOOP_REGISTRY == LOOP_REGISTRY, "LOOP_REGISTRY drift between manifest.py and validate_skill.py"
    assert m.VERDICT_VOCAB == VERDICT_VOCAB, "VERDICT_VOCAB drift between manifest.py and validate_skill.py"

# ---- R-CI: hook + workflow run the validation suite --------------------
@check("R-CI-01: tracked .githooks/pre-commit runs the validation suite")
def t_precommit_hook():
    assert exists(".githooks/pre-commit"), ".githooks/pre-commit missing"
    assert "validate_skill.py" in read(".githooks/pre-commit"), \
        "pre-commit hook does not run validate_skill.py"

@check("R-CI-02: CI workflow runs the validation suite")
def t_ci_workflow():
    wdir = os.path.join(SKILL, ".github/workflows")
    assert os.path.isdir(wdir), ".github/workflows missing"
    yml = "\n".join(read(f".github/workflows/{f}") for f in os.listdir(wdir) if f.endswith(".yml"))
    assert "validate_skill.py" in yml, "no workflow runs validate_skill.py"

# ---- R-VOICE: authorial voice ref carries the spec's voice invariants ----
@check("R-VOICE-01: voice-and-style ref exists, is referenced by SKILL.md, and states the McKinsey/exec voice + audience + reference-factual rule")
def t_voice_ref():
    path = "refs/voice-and-style.md"
    assert exists(path), f"missing {path}"
    body = read(path).lower()
    for needle in ["mckinsey", "first-person", "exec", "architect",
                   "pyramid", "action title", "so what"]:
        assert needle in body, f"voice ref missing voice marker: {needle}"
    # audience calibration: PAM / NPI / less-technical
    assert "account manager" in body or "pam" in body, "voice ref missing PAM audience"
    assert "less-technical" in body or "non-technical" in body, "voice ref missing non-technical audience"
    # the narrative-vs-reference split must be explicit
    assert "reference artifact" in body and "factual" in body, \
        "voice ref must state that reference artifacts stay factual"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"

# ---- R-INTAKE: intake source-map ref documents all six channels + rules ----
@check("R-INTAKE-01: intake-source-map ref exists, is referenced by SKILL.md, and documents the 6 channels, allowlist, graceful degradation, min-viable input, and parent-SKU spine")
def t_intake_ref():
    path = "refs/intake-source-map.md"
    assert exists(path), f"missing {path}"
    body = read(path).lower()
    # the six channels
    for needle in ["paste", "source-fetch", "org62", "slack", "price-list", "web research"]:
        assert needle in body, f"intake ref missing channel: {needle}"
    # official-docs allowlist domains
    for dom in ["help.salesforce.com", "developer.salesforce.com",
                "architect.salesforce.com", "trailhead", "partner community"]:
        assert dom in body, f"intake ref missing allowlist entry: {dom}"
    # graceful degradation + never-blocked
    assert ("graceful" in body or "degrade" in body), "intake ref missing graceful-degradation concept"
    assert ("never blocked" in body or "flagged gap" in body or "flag a gap" in body), \
        "intake ref must state that a missing source flags a gap, not blocks"
    # minimum viable input = a parent direct SKU
    assert "minimum" in body and "parent" in body and "sku" in body, \
        "intake ref must state the minimum-viable input is a parent direct SKU"
    # parent-SKU modeling spine + human-confirm
    assert "naming difference" in body and "delta" in body, "intake ref missing parent-SKU delta/naming-difference modeling"
    assert "human" in body and "confirm" in body, "intake ref must state the skill drafts and flags; a human confirms"
    # pricing out of scope reminder
    assert "pricing" in body and "out of scope" in body, \
        "intake ref must note pricing is out of scope"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"

@check("R-INTAKE-02: intake ref documents the opening prompt + the 7 follow-up intake questions (name, edition, required/other add-ons, parent slack channel, resource links, anything-else)")
def t_intake_questions():
    body = read("refs/intake-source-map.md").lower()
    # the opening request shape (parent-SKU one-liner)
    assert "embedded sku based on" in body or "based on the standard" in body, \
        "intake ref must show the opening 'create an ISV Embedded SKU based on <parent>' request shape"
    # the follow-up questions, by topic
    assert "planned name" in body or "name of the isv embedded sku" in body, \
        "intake ref must ask the planned Embedded SKU name"
    assert "edition" in body, "intake ref must ask which edition(s)"
    assert "required add-on" in body, "intake ref must ask required add-ons"
    assert "other add-on" in body, "intake ref must ask about other add-ons"
    assert "slack channel" in body, "intake ref must ask the parent SKU's slack channel(s)"
    assert "resource link" in body and ("include them in the artifacts" in body or "included in the artifacts" in body), \
        "intake ref must ask for resource links AND state real links are included in the artifacts"
    assert "anything else" in body, "intake ref must include the open 'anything else to consider' question"
    # one-at-a-time, never-block discipline
    assert "one at a time" in body, "intake ref must say to ask the follow-ups one at a time"

# ---- R-ARCH-03/04: refs manifest + no-orphans -------------------------
# refs/ holds SKILL.md-referenced instruction modules. scripts/ and templates/
# are infrastructure wired via tests/scripts (not the instruction router), so the
# no-orphans check is scoped to refs/ only.
EXPECTED_REFS = [
    "refs/voice-and-style.md",
    "refs/intake-source-map.md",
    "refs/artifact-templates.md",
    "refs/org62-entitlements.md",
    "refs/quality-loops.md",
    "refs/mermaid-diagrams.md",
    "refs/render-and-canvas.md",
]

@check("R-ARCH-03: every expected ref exists")
def t_expected_refs_exist():
    missing = [r for r in EXPECTED_REFS if not exists(r)]
    assert not missing, f"expected refs missing: {missing}"

@check("R-ARCH-04: every file under refs/ is referenced by SKILL.md (no orphans)")
def t_refs_no_orphans():
    refs_dir = os.path.join(SKILL, "refs")
    if not os.path.isdir(refs_dir):
        raise AssertionError("refs/ directory missing")
    skill = read("SKILL.md")
    orphans = []
    for f in os.listdir(refs_dir):
        if f.startswith(".") or not os.path.isfile(os.path.join(refs_dir, f)):
            continue
        if f"refs/{f}" not in skill:
            orphans.append(f"refs/{f}")
    assert not orphans, f"refs present but never referenced by SKILL.md: {sorted(orphans)}"

# ---- R-TEST-02: token hygiene over templates/ ---------------------------
TOKEN_RE = re.compile(r"\{\{([^{}]*)\}\}")

@check("R-TEST-02: every {{TOKEN}} in templates/*.md is UPPER_SNAKE_CASE with balanced braces")
def t_token_hygiene():
    tdir = os.path.join(SKILL, "templates")
    assert os.path.isdir(tdir), "templates/ directory missing"
    bad = []
    for f in os.listdir(tdir):
        if not f.endswith(".md"):
            continue
        for tok in TOKEN_RE.findall(read(f"templates/{f}")):
            if not re.fullmatch(r"[A-Z0-9_]+", tok):
                bad.append(f"templates/{f}: {{{{{tok}}}}}")
    assert not bad, f"malformed tokens: {bad}"

# ---- R-TPL-01/02: artifact-template registry parity + shared convention -
@check("R-TPL-01: every ARTIFACT_REGISTRY slug has a templates/<slug>.md, and no template is an unknown slug")
def t_template_registry_parity():
    missing = [f"templates/{s}.md" for s in ARTIFACT_REGISTRY if not exists(f"templates/{s}.md")]
    assert not missing, f"artifact templates missing: {missing}"
    tdir = os.path.join(SKILL, "templates")
    known = set(ARTIFACT_REGISTRY)  # manifest.yaml is .yaml, excluded by the .md filter below
    unknown = []
    for f in os.listdir(tdir):
        if not f.endswith(".md"):
            continue
        slug = f[:-3]
        if slug not in known:
            unknown.append(f"templates/{f}")
    assert not unknown, f"template files that are not a known artifact slug: {sorted(unknown)}"

@check("R-TPL-02: every artifact template carries the literal gap-banner header block and sources/confidence footer block")
def t_template_shared_convention():
    header_line = "> **Status:** {{STATUS}} · **Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}"
    gap_line = "> {{GAP_BANNER}}"
    footer = "---\n**Sources:** {{SOURCES}}\n**Confidence:** {{CONFIDENCE}} — {{CONFIDENCE_RATIONALE}}"
    bad = []
    for s in ARTIFACT_REGISTRY:
        body = read(f"templates/{s}.md")
        if header_line not in body:
            bad.append(f"templates/{s}.md missing the literal gap-banner status line")
        if gap_line not in body:
            bad.append(f"templates/{s}.md missing the '> {{{{GAP_BANNER}}}}' blockquote line")
        if footer not in body:
            bad.append(f"templates/{s}.md missing the literal sources/confidence footer block")
        if "VOICE:" not in body:
            bad.append(f"templates/{s}.md missing VOICE register comment")
    assert not bad, f"shared-convention violations: {bad}"

# ---- R-TPL-03: demand-grid carries its required columns + the inclusion rule ----
@check("R-TPL-03: 13-demand-plan carries the three SKU-bundle columns and the NPI-dependent inclusion rule")
def t_demand_grid_structure():
    body = read("templates/13-demand-plan.md")
    for col in ["Core / Required SKUs", "Standard add-ons", "Conditional (NPI-dependent) add-ons"]:
        assert col in body, f"demand grid missing required column label: {col}"
    # The inclusion rule text spans multiple lines in the template, so remove newlines for matching
    body_normalized = body.replace("\n", " ")
    assert "only when the NPI process has identified that add-on as required" in body_normalized, \
        "demand grid missing the conditional-add-on inclusion rule"
    assert "CC / CC+" in body, "demand grid should name the CC/CC+ worked example"

# ---- R-TPL-04: #13 carries the internal business-case columns + the estimate/not-pricing framing ----
@check("R-TPL-04: 13-demand-plan carries the business-case columns (ASP/penetration/attrition) and the estimate-not-pricing framing")
def t_business_case_structure():
    body = read("templates/13-demand-plan.md")
    for col in ["ASP (est.)", "Penetration % (est.)", "Attrition % (est.)", "Halo ACV (est.)"]:
        assert col in body, f"#13 business case missing column: {col}"
    flat = " ".join(body.split())
    assert "not partner-facing pricing" in flat, \
        "#13 must frame the business-case inputs as estimates, not partner-facing pricing"
    assert "flagged estimate" in body.lower(), "#13 business case must call the inputs flagged estimates"

# ---- R-TPL-05: #01 carries the Key Use Cases table section + its 5 columns ----
@check("R-TPL-05: 01-brief carries a Key use cases section with the five required column headers and a fill token")
def t_use_case_table():
    body = read("templates/01-brief.md")
    assert "## Key use cases" in body, "#01 must carry a '## Key use cases' section"
    assert "{{KEY_USE_CASES_TABLE}}" in body, "#01 must carry the {{KEY_USE_CASES_TABLE}} fill token"
    for col in ["Category", "Opportunity", "Example Use Case", "Key Features", "What Partners Package"]:
        assert col in body, f"#01 use-case grammar missing column: {col}"
    # Req 1D: the Additional resources section prompts for the FCD / COA / trial-org categories
    assert "## Additional resources" in body, "#01 must keep the Additional resources section"
    flat = " ".join(body.split()).lower()
    for needle in ["fcd", "coa", "trial"]:
        assert needle in flat, f"#01 Additional resources grammar missing prompt for: {needle}"

# ---- R-TPL-06: #00 carries the Messaging Hierarchy section ----
@check("R-TPL-06: 00-executive-summary carries a Messaging hierarchy section naming key message, product, pillars, features, plus a fill token")
def t_messaging_hierarchy():
    body = read("templates/00-executive-summary.md")
    assert "## Messaging hierarchy" in body, "#00 must carry a '## Messaging hierarchy' section"
    assert "{{MESSAGING_HIERARCHY}}" in body, "#00 must carry the {{MESSAGING_HIERARCHY}} fill token"
    flat = " ".join(body.split()).lower()
    for tier in ["key message", "product", "pillar", "feature"]:
        assert tier in flat, f"#00 messaging hierarchy grammar missing tier: {tier}"

# ---- R-MANIFEST-07/08: loop verdicts + last_generated -------------------
@check("R-MANIFEST-07: loops + last_generated survive round-trip and re-dump is stable")
def t_manifest_loops_roundtrip():
    m = _load_script("scripts/manifest.py", "manifest_mod7")
    eff = m.new_effort("summer-26", "x-oem", "Parent EE")
    # every artifact seeded with all four loops at the not-yet-run verdict
    for a in ARTIFACT_REGISTRY:
        assert set(eff["artifacts"][a]["loops"].keys()) == set(LOOP_REGISTRY), f"{a} loops not seeded"
        for lp in LOOP_REGISTRY:
            assert eff["artifacts"][a]["loops"][lp]["verdict"] == "", "seed verdict should be '' (not run)"
        assert eff["artifacts"][a]["last_generated"] == ""
    eff = m.set_loop_verdict(eff, "06-license-entitlements", "claim_verification", "flag",
                             "PSL naming delta unconfirmed")
    eff = m.set_last_generated(eff, "06-license-entitlements", "artifacts/.baseline/06-license-entitlements.md")
    import tempfile, os as _os
    p = _os.path.join(tempfile.mkdtemp(), "manifest.yaml")
    open(p, "w").write(m.dumps(eff))
    back = m.load(p)
    lp = back["artifacts"]["06-license-entitlements"]["loops"]["claim_verification"]
    assert lp["verdict"] == "flag" and lp["note"] == "PSL naming delta unconfirmed", "loop verdict lost"
    assert back["artifacts"]["06-license-entitlements"]["last_generated"] == \
        "artifacts/.baseline/06-license-entitlements.md", "last_generated lost"
    # re-dump is byte-stable
    assert m.dumps(back) == m.dumps(eff), "round-trip is not stable"

@check("R-MANIFEST-08: set_loop_verdict rejects unknown loop or verdict")
def t_manifest_loop_guard():
    m = _load_script("scripts/manifest.py", "manifest_mod8")
    eff = m.new_effort("r", "p", "parent")
    try:
        m.set_loop_verdict(eff, "01-brief", "nope_loop", "pass"); assert False, "unknown loop should raise"
    except ValueError: pass
    try:
        m.set_loop_verdict(eff, "01-brief", "completeness", "banana"); assert False, "bad verdict should raise"
    except ValueError: pass
    try:
        m.set_loop_verdict(eff, "99-nope", "completeness", "pass"); assert False, "unknown artifact should raise"
    except ValueError: pass

@check("R-DERIVE-01: DERIVES_FROM keys+values are registry slugs; graph is acyclic; generation_order topological")
def t_derivation_graph():
    m = _load_script("scripts/manifest.py", "manifest_derive")
    reg = set(m.ARTIFACT_REGISTRY)
    df = m.DERIVES_FROM
    # keys and values must all be real registry slugs
    for k, v in df.items():
        assert k in reg, f"DERIVES_FROM key not in registry: {k}"
        assert v in reg, f"DERIVES_FROM source not in registry: {v}"
        assert k != v, f"artifact derives from itself: {k}"
    # a source must not itself be derived (2-level, acyclic by construction)
    for k, v in df.items():
        assert v not in df, f"source {v} is itself derived — graph not shallow/acyclic"
    # generation_order returns all 15, every source before its derivatives, no dup
    order = m.generation_order()
    assert sorted(order) == sorted(m.ARTIFACT_REGISTRY), "generation_order must return every artifact exactly once"
    pos = {slug: i for i, slug in enumerate(order)}
    for derived, src in df.items():
        assert pos[src] < pos[derived], f"generation_order places source {src} after its derivative {derived}"

@check("R-DERIVE-02: quality-loops states the derivation contract + sources-before-derivatives, and generation_order backs it")
def t_derivation_contract():
    txt = read("refs/quality-loops.md")
    low = txt.lower()
    # the contract: derived artifacts transform their source, not re-research
    assert "derivation contract" in low, "quality-loops.md must carry a 'Derivation contract' subsection"
    assert "generation_order" in txt, "quality-loops.md must reference manifest.generation_order() as the ordering authority"
    assert ("source" in low and "before" in low and ("derivativ" in low or "derived" in low)), \
        "quality-loops.md must state that sources are generated before their derivatives"
    assert ("transform" in low or "do not re-research" in low or "not re-research" in low), \
        "quality-loops.md must state derived artifacts transform the source (not re-research)"
    # every derived slug is named in the ref so a builder knows its source
    m = _load_script("scripts/manifest.py", "manifest_der2")
    for derived, src in m.DERIVES_FROM.items():
        assert derived in txt, f"quality-loops.md must name derived artifact {derived}"
    # the mechanism is valid (topological — reuses Task 1 guarantee, fails loudly if it regressed)
    m.generation_order()

@check("R-DERIVE-03: every derived template carries a DERIVED header naming its actual source slug")
def t_derived_headers():
    m = _load_script("scripts/manifest.py", "manifest_der3")
    for derived, src in m.DERIVES_FROM.items():
        body = read(f"templates/{derived}.md")
        head = body[:600]  # top-of-file region (comment block + H1 + gap banner)
        assert "DERIVED" in head.upper(), f"{derived}.md missing a DERIVED header comment"
        assert src in head, f"{derived}.md DERIVED header must name its source slug {src}"
    # artifact-templates.md documents the map
    ref = read("refs/artifact-templates.md")
    assert "DERIVES_FROM" in ref or "derivation" in ref.lower(), \
        "artifact-templates.md must document the derivation map"
    for derived, src in m.DERIVES_FROM.items():
        assert derived in ref and src in ref, f"artifact-templates.md must name {derived} and its source {src}"

# ---- R-RENDER-01: token fill + unfilled reporting -----------------------
@check("R-RENDER-01: render fills known tokens, reports unfilled, and a complete fill leaves no surviving {{TOKEN}}")
def t_render():
    r = _load_script("scripts/render.py", "render_mod")
    tmpl = "# {{PRODUCT_NAME}}\n{{VISION}} and {{VISION}}\n{{SOURCES}}\n"
    out, unfilled = r.render(tmpl, {"PRODUCT_NAME": "Agentforce for Healthcare", "VISION": "win healthcare"})
    assert "Agentforce for Healthcare" in out and "win healthcare" in out
    assert unfilled == ["SOURCES"], f"expected ['SOURCES'], got {unfilled}"
    assert "{{SOURCES}}" in out, "unfilled token must stay literal"
    # complete fill across every token in every shipped template leaves nothing behind
    import re as _re, os as _os
    tdir = _os.path.join(SKILL, "templates")
    survivor = []
    for f in _os.listdir(tdir):
        if not f.endswith(".md"):
            continue
        body = read(f"templates/{f}")
        toks = set(_re.findall(r"\{\{([A-Z0-9_]+)\}\}", body))
        rendered, left = r.render(body, {t: "X" for t in toks})
        if "{{" in rendered or left:
            survivor.append((f, left))
    assert not survivor, f"complete fill left tokens behind: {survivor}"
    # new-token presence guard (Tasks 2-5): these must exist in their templates
    expect = {
        "templates/06-license-entitlements.md": ["{{REQUIRED_LICENSING_TABLE}}"],
        "templates/07-addon-tiering.md": ["{{STANDARD_ISV_ADDONS}}"],
        "templates/13-demand-plan.md": ["{{DEMAND_GRID}}", "{{DEMAND_DIAGRAM}}", "{{BUSINESS_CASE_TABLE}}"],
        "templates/14-exec-infographic.md": ["{{TAM_PANEL}}", "{{EXEC_DIAGRAM}}"],
        "templates/10-partner-profile-pov.md": ["{{ANCHOR_PARTNER}}"],
        "templates/03-internal-enablement.md": ["{{CHANNEL_CONFLICT}}"],
        "templates/04-internal-faq.md": ["{{CHANNEL_CONFLICT_FAQ}}"],
    }
    missing_tok = []
    for path, toks in expect.items():
        body = read(path)
        for t in toks:
            if t not in body:
                missing_tok.append(f"{path}: {t}")
    assert not missing_tok, f"expected token(s) missing from template: {missing_tok}"

# ---- R-SECT-01: H2 split + per-section lock diff ------------------------
@check("R-SECT-01: split keys by H2; locked_sections flags exactly the human-edited section")
def t_sections():
    s = _load_script("scripts/sections.py", "sections_mod")
    base = ("<!-- VOICE -->\n# Title\n> banner\n\n"
            "## Licenses\nbase licenses\n\n## Features\nbase features\n\n"
            "---\n**Sources:** x\n")
    secs = s.split(base)
    assert set(secs.keys()) == {"Licenses", "Features"}, f"unexpected sections: {set(secs.keys())}"
    assert "base licenses" in secs["Licenses"]
    # human edits the Features body only
    live = base.replace("base features", "HUMAN-EDITED features")
    assert s.locked_sections(live, base) == {"Features"}, "only the edited section should lock"
    # identical files lock nothing
    assert s.locked_sections(base, base) == set(), "no edits -> no locks"
    # a human-added section locks too
    live2 = base.replace("## Features", "## Storage\nadded\n\n## Features")
    assert "Storage" in s.locked_sections(live2, base), "human-added section should lock"

# ---- R-SCAN-01: uncertainty / gap scan ----------------------------------
@check("R-SCAN-01: scan catches each canonical gap type and a clean artifact scans empty")
def t_scan():
    sc = _load_script("scripts/scan.py", "scan_mod")
    md = ("## Template ID\nPENDING -- not yet provided\n"
          "## Pricing\nlist price $xx; discount TBD\n"
          "## Composition\n{{ENTITLEMENT_COMPOSITION}}\n")
    items = [g["item"] for g in sc.scan(md)]
    joined = " | ".join(items)
    assert "Template ID" in joined, "missing-Template-ID gap not caught"
    assert any("PENDING" in i for i in items), "PENDING marker not caught"
    assert any("TBD" in i for i in items), "TBD marker not caught"
    assert any("price" in i.lower() for i in items), "price stub not caught"
    assert any("token" in i.lower() for i in items), "surviving token not caught"
    # same-line Template ID gap (regression guard: must catch both two-line and one-line forms)
    inline = [g["item"] for g in sc.scan("## Provisioning\nTemplate ID: PENDING\n")]
    assert any("Template ID" in i for i in inline), "same-line 'Template ID: PENDING' gap not caught"
    # M3: a rendered pending-price marker is flagged as a PRICING gap (rolls into #00 register)
    pricing = [g["item"] for g in sc.scan("| SKU | Price | Discount |\n|--|--|--|\n| X | $xx (pending) | xx% (pending) |\n")]
    assert any("pricing pending" in i.lower() for i in pricing), "price-pending marker must flag as a pricing gap"
    # M3 de-noise: a pending-price cell yields the pricing-pending label, not redundant generic rows for the same text
    prow = sc.scan("| X | $xx (pending) | xx% (pending) |")
    labels = [g["item"] for g in prow]
    assert any("pricing pending" in i.lower() for i in labels), "must flag pricing pending"
    assert not any(i == "PENDING marker: pending" for i in labels), "must not also emit a generic PENDING row for the same cell"
    assert not any(i == "price stub: $xx" for i in labels), "must not also emit a generic price-stub row for the same $xx (pending)"
    assert sc.scan("## All set\nfully grounded prose with no gaps.\n") == [], "clean artifact must scan empty"

# ---- R-ENT-01: Org62 composition parser ---------------------------------
@check("R-ENT-01: parse_composition maps the real entitlement-map fixture to grant rows with a derived category, and degrades on empty/malformed")
def t_org62_composition():
    o = _load_script("scripts/org62.py", "org62_mod1")
    import json
    with open(os.path.join(SKILL, "tests/fixtures/org62/entitlement-composition.json"), encoding="utf-8") as f:
        grants = o.parse_composition(json.load(f))
    assert isinstance(grants, list) and len(grants) == 1, grants
    g = grants[0]
    assert g["grant"] == "UE Sites", g
    assert g["cloud"] == "Sites", g
    assert g["quantity"] == 1000000, g
    assert g["service_enabling"] is True, g
    assert g["addon_sku"] is None, g
    assert g["category"] in ("License", "PSL", "Feature", "Storage", "Add-on", "Other"), g
    # empty + malformed degrade to [] without raising
    for bad in [{"result": {"records": []}}, {"result": {"records": "oops"}},
                {"result": {"records": [None]}}, None, {}]:
        assert o.parse_composition(bad) == [], f"must degrade to [] on {bad}"

# ---- R-ENT-02: Org62 candidate-resolve parser ---------------------------
@check("R-ENT-02: parse_candidates maps the product2-candidates fixture and degrades on empty/malformed")
def t_org62_candidates():
    o = _load_script("scripts/org62.py", "org62_mod2")
    import json
    with open(os.path.join(SKILL, "tests/fixtures/org62/product2-candidates.json"), encoding="utf-8") as f:
        cands = o.parse_candidates(json.load(f))
    assert isinstance(cands, list) and len(cands) == 2, cands
    names = [c["name"] for c in cands]
    assert "Health Cloud - Service - Enterprise Edition - OEM" in names, cands
    assert cands[0]["product_code"] == "OPT-SS-EE-HLS-OEM-ASP", cands
    assert all(set(c.keys()) >= {"id", "name", "product_code", "family"} for c in cands), cands
    for bad in [{"result": {"records": []}}, {"result": {"records": "oops"}},
                {"result": {"records": [None]}}, None, {}]:
        assert o.parse_candidates(bad) == [], f"must degrade to [] on {bad}"

# ---- R-ORG62-01: entitlements ref pins the query spine ------------------
@check("R-ORG62-01: org62-entitlements ref exists, is referenced by SKILL.md, and pins the real two-step read-only schema + human-confirm")
def t_org62_ref():
    path = "refs/org62-entitlements.md"
    assert exists(path), f"missing {path}"
    body = read(path).lower()
    for needle in ["sfbase__entitlementdefinitionmap__c", "product2", "sf data query", "--json",
                   "org62", "read-only", "resolve", "compose", "pinned", "category",
                   "naming difference", "delta", "human"]:
        assert needle in body, f"org62 ref missing: {needle}"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"

# ---- R-LOOPS-01: quality-loops ref documents the cycle + four loops -----
@check("R-LOOPS-01: quality-loops ref exists, is referenced by SKILL.md, and documents the 3-pass cycle, 4 loops, POV exception, and the scripts it drives")
def t_loops_ref():
    path = "refs/quality-loops.md"
    assert exists(path), f"missing {path}"
    body = read(path).lower()
    for phase in ["draft", "refine", "validate"]:
        assert phase in body, f"cycle phase missing: {phase}"
    for loop in ["claim verification", "completeness", "uncertainty", "partner-lens"]:
        assert loop in body, f"loop missing: {loop}"
    # POV/opinion exception: strict on fact, lenient on POV
    assert "pov" in body and ("lenient" in body or "internal logic" in body), \
        "loops ref must state the POV/opinion exception"
    # names the mechanical scripts it drives
    for script in ["render.py", "sections.py", "scan.py", "org62.py", "manifest.py"]:
        assert script in body, f"loops ref should name the script it drives: {script}"
    # writes verdicts back to the manifest
    assert "verdict" in body and "manifest" in body, "loops ref must say verdicts are written to the manifest"
    # generation batching guidance (the all-in-one-subagent timeout lesson)
    assert "batch" in body, "loops ref must give generation-batching guidance"
    assert ("all 11" in body or "all-in-one" in body or "single subagent" in body), \
        "loops ref must warn against generating all 13 artifacts in one subagent"
    assert ("write each artifact file immediately" in body or "writes each artifact file immediately" in body
            or "write each" in body), "loops ref must say to write each artifact file immediately"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"

# ---- R-SECT-02: in-body --- does not truncate the split -----------------
@check("R-SECT-02: a standalone --- inside a body section does not drop later sections; the footer is the ---/**Sources:** block")
def t_sections_inbody_rule():
    s = _load_script("scripts/sections.py", "sections_mod2")
    md = ("<!-- VOICE -->\n# Title\n> banner\n\n"
          "## Overview\nintro\n\n---\n\nmid-section rule above\n\n"
          "## Details\nbody two\n\n"
          "---\n**Sources:** x\n**Confidence:** 0.5 — ok\n")
    secs = s.split(md)
    assert set(secs.keys()) == {"Overview", "Details"}, f"in-body --- truncated the split: {set(secs.keys())}"
    assert "mid-section rule above" in secs["Overview"], "content after an in-body --- was dropped"
    assert "body two" in secs["Details"], "a later section was dropped by an in-body ---"
    # footer (Sources/Confidence) is excluded from sections
    assert not any("Sources" in body for body in secs.values()), "footer leaked into a section"
    # edit detection still works across the in-body rule
    live = md.replace("body two", "HUMAN-EDITED body two")
    assert s.locked_sections(live, md) == {"Details"}, "edit after an in-body --- not detected"
    # last-pair regression: in-body ---/**Sources:** lookalike does NOT truncate when real footer follows
    md_lookalike = ("<!-- VOICE -->\n# Title\n> banner\n\n"
                    "## Overview\nintro\n\n---\n**Sources:** inline citation here\n\n"
                    "## Later\nsection after lookalike\n\n"
                    "---\n**Sources:** x\n**Confidence:** 0.5 — ok\n")
    secs_look = s.split(md_lookalike)
    assert "Later" in secs_look, f"later section dropped by lookalike footer: {set(secs_look.keys())}"
    assert "section after lookalike" in secs_look["Later"], "later section body lost"
    # edit to the later section is detected
    live_look = md_lookalike.replace("section after lookalike", "EDITED section after lookalike")
    assert "Later" in s.locked_sections(live_look, md_lookalike), "edit to later section not detected"

# ---- R-HTML-01: SLDS document shell carries the CDN, theme, and tokens --
@check("R-HTML-01: document-shell.html carries the Mermaid CDN, SLDS theme, and the required metadata tokens")
def t_document_shell():
    path = "templates/document-shell.html"
    assert exists(path), f"missing {path}"
    s = read(path)
    assert "cdn.jsdelivr.net/npm/mermaid@11" in s, "shell missing the mermaid@11 CDN"
    assert "startOnLoad: true" in s or "startOnLoad:true" in s, "shell missing mermaid.initialize startOnLoad"
    assert "Salesforce Sans" in s, "shell missing the Salesforce Sans font stack"
    assert "#0176d3" in s, "shell missing the SLDS brand-blue"
    assert "print-color-adjust" in s, "shell missing print-color-adjust for dark fills"
    for tok in ("{{TITLE}}", "{{LABEL}}", "{{RELEASE}}", "{{GENERATED_DATE}}", "{{BODY}}", "{{HOME_HREF}}"):
        assert tok in s, f"shell missing token {tok}"

# ---- R-MD2H-01: markdown -> HTML converter (subset + mermaid verbatim) --
@check("R-MD2H-01: md_to_html renders the artifact subset; a mermaid fence becomes a verbatim <pre class=mermaid>, other fences escaped")
def t_md_to_html():
    m = _load_script("scripts/md_to_html.py", "md2h_mod")
    md = read("tests/fixtures/render/sample-artifact.md")
    h = m.md_to_html(md)
    assert "<h1>Sample Artifact</h1>" in h, "H1 not rendered"
    assert "<h2>Section One</h2>" in h, "H2 not rendered"
    assert "<strong>bold</strong>" in h and "<em>italic</em>" in h and "<code>code</code>" in h, "inline not rendered"
    assert '<a href="https://help.salesforce.com" target="_blank" rel="noopener noreferrer">link</a>' in h, "external link not rendered with new-tab attrs"
    assert "<table>" in h and "<th>Grant</th>" in h and "<td>UE Sites</td>" in h, "GFM table not rendered"
    assert "<blockquote>" in h, "blockquote not rendered"
    assert "<ul><li>one</li><li>two</li></ul>" in h, "list not rendered"
    # mermaid fence: verbatim <pre class="mermaid">, NOT escaped
    assert '<pre class="mermaid">' in h, "mermaid fence not emitted as <pre class=mermaid>"
    assert "graph TD; A[Parent] --> B[OEM];" in h, "mermaid source must be kept verbatim (not escaped)"
    assert "&lt;pre" not in h, "mermaid/source should not be double-escaped"
    # a non-mermaid fence would be escaped — verify the escaper path exists by a direct call
    esc = m.md_to_html("```python\nx = 1 < 2\n```")
    assert "<pre><code>" in esc and "1 &lt; 2" in esc, "non-mermaid fence must be escaped <pre><code>"
    # inline code containing bold/italic markers must NOT be converted (code runs are protected)
    edge = m.md_to_html("Text with `**asterisks**` and `*solo*` inside code.")
    assert "<code>**asterisks**</code>" in edge, "inline code with ** must stay literal, not <strong>"
    assert "<code>*solo*</code>" in edge, "inline code with * must stay literal, not <em>"
    # bold/italic OUTSIDE code still convert
    assert "<strong>real</strong>" in m.md_to_html("a **real** bold"), "bold outside code must still convert"

# ---- R-MERMAID-01: mermaid ref carries the canonical SLDS directive -----
@check("R-MERMAID-01: mermaid-diagrams ref exists, is referenced by SKILL.md, and carries the canonical SLDS %%{init}%% directive + named diagram types")
def t_mermaid_ref():
    path = "refs/mermaid-diagrams.md"
    assert exists(path), f"missing {path}"
    body = read(path)
    assert '%%{init:' in body and '"theme":"base"' in body, "missing the %%{init}%% base-theme directive"
    for tok in ('"primaryBorderColor":"#0176d3"', '"lineColor":"#444444"', 'Salesforce Sans'):
        assert tok in body, f"directive missing SLDS value: {tok}"
    low = body.lower()
    for diagram in ("status", "composition", "tier", "partner"):
        assert diagram in low, f"ref missing named diagram type: {diagram}"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"

# ---- R-MERMAID-02: render surfaces size the injected SVG to the container (no clipping) ----
@check("R-MERMAID-02: document-shell + slide_deck set flowchart useMaxWidth and constrain .mermaid svg width so long-label diagrams don't clip")
def t_mermaid_no_clip():
    shell = read("templates/document-shell.html")
    assert "useMaxWidth" in shell, "shell mermaid.initialize must set flowchart useMaxWidth"
    assert ".mermaid svg" in shell and "max-width" in shell.split(".mermaid svg")[1][:80], \
        "shell must constrain .mermaid svg to max-width:100%"
    sd = read("scripts/slide_deck.py")
    assert "useMaxWidth" in sd, "slide_deck mermaid.initialize must set flowchart useMaxWidth"
    ref = read("refs/mermaid-diagrams.md").lower()
    assert "usemaxwidth" in ref or "max-width" in ref, "mermaid ref must document the useMaxWidth/scaling fix"
    assert "short" in ref and "label" in ref, "mermaid ref must advise short node labels"

# ---- R-CANVAS-01: Key Resources hub assembly ---------------------------
@check("R-CANVAS-01: build_index emits a card per artifact with status+confidence badges, a labeled gap card for pending (no dead link), and the aggregated blocker register")
def t_canvas_index():
    c = _load_script("scripts/canvas.py", "canvas_mod")
    mani = _load_script("scripts/manifest.py", "canvas_manifest_mod")
    eff = mani.new_effort("summer-26", "agentforce-healthcare-oem", "Health Cloud EE/UE")
    eff = mani.set_status(eff, "01-brief", "verified")
    eff["artifacts"]["01-brief"]["confidence"] = 0.75
    eff = mani.set_status(eff, "09-org-provisioning-validation", "drafted")
    eff["artifacts"]["09-org-provisioning-validation"]["confidence"] = 0.35
    eff["artifacts"]["09-org-provisioning-validation"]["placeholders"] = [
        {"item": "Template ID", "owner": "Manish/John", "next_step": "request Template ID"}]
    # 00 left pending → must render as a labeled gap card, not a link
    html_present = {a: (a == "01-brief") for a in mani.ARTIFACT_REGISTRY}
    page = c.build_index(eff, html_present)
    assert "agentforce-healthcare-oem" in page and "summer-26" in page, "effort title/release missing"
    assert "01-brief.html" in page, "verified artifact with HTML must link to its .html"
    assert "0.75" in page and "0.35" in page, "confidence badges missing"
    # pending #00 → labeled gap card, no dead link
    assert "00-executive-summary.html" not in page, "pending artifact must NOT link to a nonexistent .html"
    assert "pending" in page.lower(), "pending status not shown"
    # blocker register aggregates placeholders with owner + next step
    assert "Template ID" in page and "Manish/John" in page and "request Template ID" in page, "blocker register missing the gap"
    # overall confidence (weighted floor = 0.0 here since pendings sit at 0.0) is shown
    assert "Overall confidence" in page or "overall confidence" in page, "overall confidence not shown"
    # regression: injection via evil slug (both blocker path + card path must escape)
    eff_evil = mani.new_effort("summer-26", "x-oem", "Parent EE")
    eff_evil["artifacts"]["evil<x>slug"] = {"status": "pending", "confidence": 0.0, "placeholders": [{"item": "test", "owner": "x", "next_step": "x"}], "loops": {}, "last_generated": ""}
    page_evil = c.build_index(eff_evil, {})
    assert "evil<x>slug" not in page_evil, "evil slug appeared raw (not escaped)"
    assert "evil&lt;x&gt;slug" in page_evil, "evil slug must appear escaped"
    # refined M1: a rendered-but-not-verified doc links AND is tagged pending (linked pending is OK if tagged)
    present2 = {a: (a in ("01-brief", "09-org-provisioning-validation")) for a in mani.ARTIFACT_REGISTRY}
    page2 = c.build_index(eff, present2)
    assert "09-org-provisioning-validation.html" in page2, "rendered drafted artifact must link"
    assert "not yet final" in page2 or "drafted" in page2.lower(), "linked non-verified doc must be tagged pending/draft"
    # an un-rendered artifact still does NOT link (no dead link)
    assert "00-executive-summary.html" not in page2, "un-rendered artifact must not link"
    # consolidation: #14 is the only poster-bearing card (title links the poster, document is secondary)
    page_poster = c.build_index(eff, {a: (a in ("14-exec-infographic","11-solution-infographic")) for a in mani.ARTIFACT_REGISTRY},
                                {"14-exec-infographic": True})
    assert "14-exec-infographic-poster.html" in page_poster, "merged poster (primary) link missing on #14"
    assert 'class="secondary-link" href="14-exec-infographic.html"' in page_poster, "#14 document must be the secondary link"
    assert ">(document)</a>" in page_poster, "secondary link must be labeled '(document)'"
    # #11 reverts to a plain document card — NO poster link anywhere for #11
    assert "11-solution-infographic.html" in page_poster, "#11 document link missing"
    assert "11-solution-infographic-poster.html" not in page_poster, "#11 must NOT have a poster link (consolidated)"
    # a non-poster artifact still single-links
    assert "01-brief-poster.html" not in page_poster, "non-poster artifact must not get a poster link"
    # poster present but document absent → poster link still renders, no dead document link
    page_only = c.build_index(eff, {a: False for a in mani.ARTIFACT_REGISTRY},
                              {"14-exec-infographic": True})
    assert "14-exec-infographic-poster.html" in page_only, "poster-only link must render"
    assert "14-exec-infographic.html\"" not in page_only, "no dead document link when document absent"

# ---- R-TABLE-01: one consistent light styled-table treatment across shell + rich templates + canvas ----
@check("R-TABLE-01: doc shell, both rich templates, and the canvas use the SAME light styled-table (tint header, navy text) — no navy-background table headers remain")
def t_table_consistency():
    shell = read("templates/document-shell.html")
    canvas = read("scripts/canvas.py")
    info = read("templates/solution-infographic.html")
    mkt = read("templates/marketecture.html")
    # the light standard: th uses the tint background + navy text, NOT a navy fill
    for name, body in [("document-shell", shell), ("solution-infographic", info), ("marketecture", mkt)]:
        assert "#eef4ff" in body or "var(--tint)" in body, f"{name}: table header must use the tint background"
    # the doc shell's content-table header must no longer be a navy fill
    # (find the '.content th' rule and confirm it is not 'background: var(--navy)' / '#032d60')
    m = re.search(r"\.content th\s*\{[^}]*\}", shell)
    assert m, "shell must define a .content th rule"
    th_rule = m.group(0)
    assert "#032d60" not in th_rule and "var(--navy)" not in th_rule.split("color")[0], \
        "shell .content th must not use a navy BACKGROUND (light scheme: tint bg, navy text)"
    # canvas blockers table also moves to the light header
    mb = re.search(r"table\.blockers th\s*\{[^}]*\}", canvas)
    assert mb, "canvas must define a table.blockers th rule"
    assert "#032d60" not in mb.group(0).split("color")[0], \
        "canvas blockers th must not use a navy BACKGROUND (light scheme)"

# ---- R-CANVAS-03: blocker register never surfaces a raw render placeholder token --
@check("R-CANVAS-03: build_index never emits a bare {{TOKEN}} as a blocker — stale *_DIAGRAM placeholders are dropped; pricing tokens render as human labels")
def t_canvas_no_raw_tokens():
    c = _load_script("scripts/canvas.py", "canvas_tok_mod")
    mani = _load_script("scripts/manifest.py", "canvas_tok_manifest")
    eff = mani.new_effort("summer-26", "x-oem", "Parent EE")
    # simulate the post-diagram-fill stale state: a *_DIAGRAM token + the pricing tokens as placeholders
    eff["artifacts"]["00-executive-summary"]["placeholders"] = [
        {"item": "{{STATUS_ROLLUP_DIAGRAM}}", "owner": "x", "next_step": "y"}]
    eff["artifacts"]["07-addon-tiering"]["placeholders"] = [
        {"item": "{{PRICE_PENDING}}", "owner": "pricing", "next_step": "confirm"},
        {"item": "{{DISCOUNT_PENDING}}", "owner": "pricing", "next_step": "confirm"},
        {"item": "Real gap: add-on TBD", "owner": "product", "next_step": "decide"}]
    page = c.build_index(eff, {a: False for a in mani.ARTIFACT_REGISTRY})
    assert "{{" not in page, "no raw {{...}} token may appear anywhere in the canvas"
    assert "STATUS_ROLLUP_DIAGRAM" not in page, "a stale *_DIAGRAM placeholder must be dropped (diagram is rendered)"
    assert "Pricing — pending" in page or "Pricing" in page, "a pricing token must render as a human label"
    assert "Real gap: add-on TBD" in page, "a genuine (non-token) blocker must still surface"

# ---- R-CANVAS-04: highlight-card blurbs mention the new #00/#01 components ----
@check("R-CANVAS-04: canvas _SUMMARY blurbs for #00 and #01 name the messaging hierarchy and the key use-case grid")
def t_canvas_highlight_mentions():
    c = _load_script("scripts/canvas.py", "canvas_hl_mod")
    s00 = c._SUMMARY["00-executive-summary"].lower()
    s01 = c._SUMMARY["01-brief"].lower()
    assert "messaging hierarchy" in s00, "#00 blurb must mention the messaging hierarchy"
    assert "use case" in s01 or "use-case" in s01, "#01 blurb must mention the key use-case grid"

# ---- R-CANVAS-02: mmdc export is capability-gated (report-and-skip) -----
@check("R-CANVAS-02: mermaid_export reports mmdc availability and skips gracefully (never raises) when absent")
def t_mermaid_export_gating():
    e = _load_script("scripts/mermaid_export.py", "mmdc_mod")
    assert isinstance(e.mmdc_available(), bool), "mmdc_available must return a bool"
    # export to a path under a tmp dir; with mmdc absent it must report-and-skip, not raise
    import tempfile, os as _os
    d = tempfile.mkdtemp()
    res = e.export_svg(_os.path.join(d, "x.mmd"), _os.path.join(d, "x.svg"))
    assert isinstance(res, dict) and "ok" in res and "skipped" in res and "message" in res, res
    if not e.mmdc_available():
        assert res["skipped"] is True and res["ok"] is False, "absent mmdc must skip, not succeed"
        assert "mermaid-cli" in res["message"], "skip message must carry the install line"

# ---- R-MD2H-02: intentional placeholders render (don't block); genuine tokens still fail --
@check("R-MD2H-02: md_to_html treats the named diagram + price placeholders as render-safe pending markers, but a genuine unknown token still hard-fails")
def t_md_to_html_placeholders():
    m = _load_script("scripts/md_to_html.py", "md2h_ph_mod")
    assert hasattr(m, "INTENTIONAL_PLACEHOLDERS"), "md_to_html must declare INTENTIONAL_PLACEHOLDERS"
    for tok in ("STATUS_ROLLUP_DIAGRAM", "COMPOSITION_DIAGRAM", "TIER_DIAGRAM",
                "PARTNER_FIT_DIAGRAM", "INFOGRAPHIC_DIAGRAM", "MARKETECTURE_DIAGRAM",
                "DEMAND_DIAGRAM", "EXEC_DIAGRAM",
                "PRICE_PENDING", "DISCOUNT_PENDING"):
        assert tok in m.INTENTIONAL_PLACEHOLDERS, f"{tok} should be an intentional placeholder"
    # the CLI-level substitution is exercised by running main() via subprocess on a temp shell+md;
    # here we assert the set is the contract the morning/Phase-6 work and R-MD2H-01 rely on.

# ---- R-RENDER-02: wants_html + orphan_html helpers ---------------------
@check("R-RENDER-02: render.wants_html computes the format rule (narrative OR has-mermaid); orphan_html returns stale <slug>.html paths to remove")
def t_render_format_rule_helpers():
    r = _load_script("scripts/render.py", "render_fmt_mod")
    # wants_html: narrative template → True
    tmpl_narr = "<!-- VOICE: narrative — first-person exec register -->\n# T\nbody\n"
    assert r.wants_html("## Section\nbody with no diagram", tmpl_narr) is True, \
        "narrative template should want HTML"
    # wants_html: reference template with a mermaid fence → True
    tmpl_ref = "<!-- VOICE: ARTIFACT_SLUG — reference artifact, factual register -->\n# T\nbody\n"
    md_with_diagram = "## License\n```mermaid\ngraph TD;\n```\n"
    assert r.wants_html(md_with_diagram, tmpl_ref) is True, \
        "reference artifact with a mermaid fence should want HTML"
    # wants_html: reference template with NO diagram → False
    md_no_diagram = "## FAQ\nQ: what? A: answer.\n"
    assert r.wants_html(md_no_diagram, tmpl_ref) is False, \
        "reference artifact with no diagram should NOT want HTML"
    # wants_html: reference template with "narrative" in BODY (VOICE says factual) → False (false-positive guard)
    tmpl_ref_body_narrative = ("<!-- VOICE: 04-internal-faq — reference artifact, factual register -->\n"
                               "# FAQ\nThis document provides a narrative overview of the product.\n")
    assert r.wants_html("## FAQ\nQ: what? A: answer.\n", tmpl_ref_body_narrative) is False, \
        "reference template with 'narrative' only in BODY (VOICE says factual) must NOT want HTML"
    # wants_html: missing VOICE marker falls back to has-mermaid only
    assert r.wants_html(md_with_diagram, "# Title\nbody") is True, \
        "missing VOICE marker should fall back to has-mermaid (True)"
    assert r.wants_html(md_no_diagram, "# Title\nbody") is False, \
        "missing VOICE marker + no diagram should be False"

    # orphan_html: temp dir with several files, keep_slugs = {"01-brief"}
    import tempfile, os as _os
    d = tempfile.mkdtemp()
    for f in ["04-internal-faq.html", "08-setup-guide.html", "01-brief.html",
              "index.html", "14-exec-infographic-poster.html", "02-slide-summary-slides.html"]:
        open(_os.path.join(d, f), "w").write("x")
    orphans = r.orphan_html(d, {"01-brief"})
    # expect exactly the two orphans: 04 and 08 (NOT index.html, NOT the poster, NOT the slides, NOT 01-brief)
    names = [_os.path.basename(p) for p in orphans]
    assert set(names) == {"04-internal-faq.html", "08-setup-guide.html"}, \
        f"orphan_html should return exactly 04 and 08, got {names}"
    # each returned path is absolute
    assert all(_os.path.isabs(p) for p in orphans), "orphan_html must return absolute paths"

# ---- R-RENDER-REF-01: render-and-canvas ref ----------------------------
@check("R-RENDER-REF-01: render-and-canvas ref exists, is referenced by SKILL.md, and documents the md_to_html invocation, the format rule, and the canvas assembly")
def t_render_canvas_ref():
    path = "refs/render-and-canvas.md"
    assert exists(path), f"missing {path}"
    body = read(path).lower()
    for needle in ["md_to_html", "canvas.py", "build_index", "document-shell.html",
                   "format rule", "html_present", "mermaid", "intentional", "pending",
                   "slide_deck.py", "slide deck"]:
        assert needle in body, f"render-canvas ref missing: {needle}"
    assert "refs/render-and-canvas.md" in read("SKILL.md"), "ref not referenced by SKILL.md"
    assert "rich view" in body or "rich_views" in body or "render_view" in body, \
        "render-canvas ref must document the #11/#12 rich-view render path"

# ---- R-SLIDE-01: slide-deck render surface -----------------------------
@check("R-SLIDE-01: slide_deck renders an artifact as a cover + one slide per H2 section, mermaid verbatim, footer excluded, no surviving tokens")
def t_slide_deck():
    s = _load_script("scripts/slide_deck.py", "slide_mod")
    md = ("# Demo Artifact\n\n> **Status:** drafted · **Confidence:** 0.6 — sample\n\n"
          "## First Section\nA point with **bold** and a [link](https://help.salesforce.com).\n\n"
          "## A Diagram\n```mermaid\ngraph TD; A-->B;\n```\n\n"
          "---\n**Sources:** x\n**Confidence:** 0.6 — sample\n")
    slides = s.to_slides(md)
    headings = [h for h, _ in slides]
    assert headings == ["First Section", "A Diagram"], f"one slide per H2, footer excluded; got {headings}"
    deck = s.build_deck(md, "Agentforce for Healthcare", "Slide Summary", "summer-26", "2026-06-24", home="index.html")
    assert 'class="slide slide-cover"' in deck, "deck must have a cover slide"
    assert deck.count('class="slide ') >= 3, "cover + 2 content slides"
    assert "cdn.jsdelivr.net/npm/mermaid@11" in deck, "deck must embed the mermaid CDN"
    assert '<pre class="mermaid">graph TD; A-->B;' in deck, "mermaid fence kept verbatim in a slide"
    assert "<strong>bold</strong>" in deck, "inline rendering in slides"
    assert "1 / 3" in deck and "3 / 3" in deck, "slide numbering across cover + sections"
    assert "**Sources:**" not in deck, "footer/Sources block must NOT appear as a slide"
    assert "{{" not in deck, "no surviving tokens in the deck"
    # pending diagram token renders as a visible note, not a raw token
    deck2 = s.build_deck("## Mkt\n{{MARKETECTURE_DIAGRAM}}\n", "T", "L", "summer-26", "2026-06-24")
    assert "Diagram pending" in deck2 and "{{" not in deck2, "pending diagram token must render as a note"
@check("R-RENDER-SAFE-01: md_to_html renders diagram + pricing placeholders to visible pending markers (exit 0) and scan flags the rendered pricing marker; a genuine unknown token still exits 1")
def t_render_safe_e2e():
    import subprocess, sys, tempfile, os as _os
    shell = _os.path.join(SKILL, "templates/document-shell.html")
    script = _os.path.join(SKILL, "scripts/md_to_html.py")
    d = tempfile.mkdtemp()
    # (a) intentional placeholders render, exit 0
    md_ok = ("# T\n## Tier decision (diagram)\n{{TIER_DIAGRAM}}\n\n"
             "## SKU\n| SKU | Price | Discount |\n|--|--|--|\n| X | {{PRICE_PENDING}} | {{DISCOUNT_PENDING}} |\n")
    p_md = _os.path.join(d, "a.md"); p_out = _os.path.join(d, "a.html")
    open(p_md, "w").write(md_ok)
    r = subprocess.run([sys.executable, script, "--md", p_md, "--shell", shell, "--out", p_out,
                        "--title", "T", "--label", "L", "--release", "summer-26", "--date", "2026-06-23"],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"intentional placeholders must render (exit 0), got {r.returncode}: {r.stderr}"
    out = open(p_out).read()
    assert "Diagram pending" in out, "unfilled *_DIAGRAM slot must render a visible pending marker"
    assert "$xx (pending)" in out and "xx% (pending)" in out, "price/discount placeholders must render as pending markers"
    assert "{{" not in out, "no raw token may survive a render-safe pass"
    # (b) scan flags the rendered pricing marker as a pricing gap (rolls into #00 register)
    sc = _load_script("scripts/scan.py", "rs_scan_mod")
    labels = [g["item"].lower() for g in sc.scan(out)]
    assert any("pricing pending" in i for i in labels), "rendered pricing marker must be flagged as a pricing gap by scan"
    # (c) a genuine unknown token still hard-fails (exit 1)
    p_bad = _os.path.join(d, "b.md"); p_bout = _os.path.join(d, "b.html")
    open(p_bad, "w").write("# T\n{{BOGUS_UNKNOWN_TOKEN}}\n")
    rb = subprocess.run([sys.executable, script, "--md", p_bad, "--shell", shell, "--out", p_bout,
                         "--title", "T", "--label", "L", "--release", "r", "--date", "2026-06-23"],
                        capture_output=True, text=True)
    assert rb.returncode == 1, "a genuine unknown token must still hard-fail (exit 1)"

# ---- R-POSTER-02: render_poster fills every panel from its source artifact; missing source/section raises -
@check("R-POSTER-02: merged poster fills all 7 panels from #14+#11 sources, no unfilled token; missing source/section raises; metadata escaped")
def t_poster_render():
    p = _load_script("scripts/poster.py", "poster_mod")
    tmpl = read("templates/exec-infographic-poster.html")
    md14 = """# Product — Executive Overview

## Vision
The vision is to transform the industry.

## Value proposition
We deliver value through innovation.

## Key use cases
- Use case one

## Ideal partners
Regional system integrators in healthcare.

## Market opportunity (TAM)
$50B market growing at 15% CAGR.
"""
    md11 = """# Product — Solution Infographic

## The one-line story
Revolutionizing healthcare data access.

## The problem (why this matters)
Fragmented patient data creates inefficiencies.

## The solution (what we built on Salesforce)
A unified Health Cloud platform.

## Outcomes (the proof)
- 40% reduction in coordination time

## Market & who it's for
Providers and payers in North America.

## Built on Salesforce (the OEM/Embedded stack)
Health Cloud + Agentforce + Data 360.
"""
    sources = {"14-exec-infographic": md14, "11-solution-infographic": md11}
    meta = {"TITLE":"X","LABEL":"Executive & Solution Overview","RELEASE":"r","GENERATED_DATE":"d","HOME_HREF":"index.html"}
    out, unfilled = p.render_poster("14-exec-infographic", sources, tmpl, meta)
    assert unfilled == [], f"unfilled poster tokens: {unfilled}"
    assert "{{" not in out, "no raw token may survive a complete poster fill"
    for tok in p.PANELS_FOR("14-exec-infographic"):
        assert "{{"+tok+"}}" not in out, f"{tok} not filled"
    # SOURCES_FOR reports both source artifacts
    assert p.SOURCES_FOR("14-exec-infographic") == {"14-exec-infographic", "11-solution-infographic"}, \
        "merged poster must declare both sources"
    # a missing section in a source raises (contract guard)
    broken = {**sources, "11-solution-infographic": md11.replace("## Outcomes (the proof)", "## Outcomesss")}
    try:
        p.render_poster("14-exec-infographic", broken, tmpl, meta)
        assert False, "missing mapped section must raise"
    except ValueError:
        pass
    # a missing SOURCE entirely raises
    try:
        p.render_poster("14-exec-infographic", {"14-exec-infographic": md14}, tmpl, meta)
        assert False, "missing source artifact must raise"
    except ValueError:
        pass
    # metadata HTML-escaped (matches md_to_html / canvas)
    out_esc, _ = p.render_poster("14-exec-infographic", sources, tmpl, {**meta, "TITLE": "Acme <Health> & Co"})
    assert "Acme &lt;Health&gt; &amp; Co" in out_esc, "metadata TITLE must be HTML-escaped"
    assert "Acme <Health>" not in out_esc, "raw HTML-special TITLE must not reach the markup"

_POSTER_FILES = {
    "14-exec-infographic": "templates/exec-infographic-poster.html",
}

@check("R-POSTER-01: the one merged poster template exists w/ UPPER_SNAKE tokens; the #11 poster is gone")
def t_poster_templates():
    for slug, path in _POSTER_FILES.items():
        assert exists(path), f"missing poster template: {path}"
        for tok in re.findall(r"\{\{([^{}]*)\}\}", read(path)):
            assert re.fullmatch(r"[A-Z0-9_]+", tok), f"{path}: malformed token {{{{{tok}}}}}"
    # consolidation guard: the #11 poster template must NOT exist (no stale duplicate)
    assert not exists("templates/solution-infographic-poster.html"), \
        "solution-infographic-poster.html must be removed (posters consolidated into the merged exec poster)"

@check("R-POSTER-03: merged poster PANEL_ slots exactly match SECTION_MAP; #11 has no poster map entry")
def t_poster_map_parity():
    p = _load_script("scripts/poster.py", "poster_parity_mod")
    for slug, path in _POSTER_FILES.items():
        body = read(path)
        slots = {t for t in re.findall(r"\{\{([A-Z0-9_]+)\}\}", body) if t.startswith("PANEL_")}
        mapped = p.PANELS_FOR(slug)
        assert slots == mapped, f"{slug}: poster PANEL_ slots {slots} != SECTION_MAP panels {mapped}"
    # consolidation guard: #11 must not carry a poster map entry
    assert "11-solution-infographic" not in p.SECTION_MAP, \
        "11-solution-infographic must have no SECTION_MAP entry (poster consolidated)"

# ---- R-RICH-01: rich-view registry maps #11 and #12 to their own templates + section maps ----
@check("R-RICH-01: RICH_VIEWS registers #11 and #12 with a template path and a PANEL→(source,H2) map matching each template's slots; #14 poster still registered")
def t_rich_view_registry():
    p = _load_script("scripts/poster.py", "rich_reg_mod")
    assert hasattr(p, "RICH_VIEWS"), "poster.py must expose RICH_VIEWS"
    for slug in ("11-solution-infographic", "12-marketecture"):
        assert slug in p.RICH_VIEWS, f"{slug} must be a rich view"
        entry = p.RICH_VIEWS[slug]
        assert exists(entry["template"]), f"{slug} rich template missing: {entry['template']}"
        # PANEL_ slots in the template must equal the map's keys
        body = read(entry["template"])
        slots = {t for t in re.findall(r"\{\{([A-Z0-9_]+)\}\}", body) if t.startswith("PANEL_")}
        assert slots == set(entry["map"].keys()), f"{slug}: template slots {slots} != map {set(entry['map'].keys())}"
    # #14 still projects (either via RICH_VIEWS or the retained SECTION_MAP)
    assert p.PANELS_FOR("14-exec-infographic"), "#14 merged poster must still project"

# ---- R-RICH-02: rich templates are light-scheme, carry metadata tokens + the shared table style ----
@check("R-RICH-02: #11/#12 rich templates use the SLDS light scheme (no dark body bg), carry all metadata tokens, and render cleanly from fixture sources")
def t_rich_render():
    p = _load_script("scripts/poster.py", "rich_render_mod")
    # fixture sources: reuse the effort's real markdown headings so the section map resolves
    md11 = ("# X — Solution Infographic\n> banner\n\n"
            "## The one-line story\nstory\n\n"
            "## The problem (why this matters)\nproblem body\n\n"
            "## The solution (what we built on Salesforce)\nsolution body\n\n"
            "## Outcomes (the proof)\noutcome body\n\n"
            "## Market & who it's for\nmarket body\n\n"
            "## Built on Salesforce (the OEM/Embedded stack)\nbuilt body\n\n"
            "---\n**Sources:** x\n**Confidence:** 0.6 — ok\n")
    tmpl = read(p.RICH_VIEWS["11-solution-infographic"]["template"])
    meta = {"TITLE":"X","LABEL":"Solution Infographic","RELEASE":"summer-26","GENERATED_DATE":"2026-07-01","HOME_HREF":"index.html"}
    out, unfilled = p.render_view("11-solution-infographic", {"11-solution-infographic": md11}, tmpl, meta)
    assert unfilled == [], f"unfilled tokens in #11 rich render: {unfilled}"
    assert "{{" not in out, "no raw token may survive the #11 rich render"
    assert "problem body" in out and "solution body" in out and "built body" in out, "panels not projected"
    # light scheme: body background must be light (not the #0f1117 dark ground)
    assert "#0f1117" not in out, "#11 must use the light scheme (no dark ground background)"
    assert "Salesforce Sans" in out, "#11 must carry the Salesforce Sans font stack"

    # #12 marketecture rich render
    md12 = ("# X — Solution Marketecture\n> banner\n\n"
            "## The architecture story (top to bottom)\nstory body\n\n"
            "## Partner solution layer (what the ISV builds & sells)\npartner body\n\n"
            "## Agent & experience layer (Agentforce, portals, channels)\nagent body\n\n"
            "## Platform layer (the parent SKU + Salesforce clouds)\nplatform body\n\n"
            "## Data & integration layer (Data 360, MuleSoft, Zero-Copy, source systems)\ndata body\n\n"
            "## Trust & compliance (Einstein Trust Layer, data protection, regulatory posture)\ntrust body\n\n"
            "---\n**Sources:** x\n**Confidence:** 0.6 — ok\n")
    tmpl12 = read(p.RICH_VIEWS["12-marketecture"]["template"])
    out12, unf12 = p.render_view("12-marketecture", {"12-marketecture": md12}, tmpl12, meta)
    assert unf12 == [], f"unfilled tokens in #12 rich render: {unf12}"
    assert "{{" not in out12, "no raw token may survive the #12 rich render"
    assert "partner body" in out12 and "trust body" in out12, "#12 layers not projected"
    assert "#0f1117" not in out12, "#12 must use the light scheme"
    assert "Salesforce Sans" in out12, "#12 must carry the Salesforce Sans font stack"

# ---- R-MD2H-03: a pipe in prose renders (is not silently dropped) ------
@check("R-MD2H-03: md_to_html renders a non-table paragraph line containing a pipe instead of dropping it")
def t_md_to_html_pipe_prose():
    m = _load_script("scripts/md_to_html.py", "md2h_pipe_mod")
    out = m.md_to_html("Choose OEM | VAR | ISVforce depending on the motion.\n")
    assert "ISVforce" in out and "OEM" in out, "pipe-bearing prose line must not be dropped"
    assert "<p>" in out, "pipe-bearing prose must render as a paragraph"
    # a real GFM table still renders as a table (regression guard the fix didn't break tables)
    tbl = m.md_to_html("| A | B |\n|---|---|\n| 1 | 2 |\n")
    assert "<table>" in tbl and "<td>1</td>" in tbl, "a real GFM table must still render as a table"

# ---- R-MD2H-05: links are clickable; external open in a new tab, internal stay same-tab ----
@check("R-MD2H-05: bare URLs autolink; external links (md + bare) get target=_blank rel=noopener; internal relative links stay same-tab; no double-wrap")
def t_md_to_html_links():
    m = _load_script("scripts/md_to_html.py", "md2h_links_mod")
    # bare URL -> clickable anchor, external -> new tab
    bare = m.md_to_html("See https://help.salesforce.com/s/articleView?id=sf.x.htm&type=5 for details.\n")
    assert '<a href="https://help.salesforce.com/s/articleView?id=sf.x.htm&amp;type=5"' in bare, "bare URL must become an anchor (href escaped)"
    assert 'target="_blank" rel="noopener noreferrer"' in bare, "external bare URL must open in a new tab"
    assert "for details." in bare, "trailing prose after a bare URL must survive"
    # trailing sentence punctuation not swallowed into the href
    dot = m.md_to_html("Docs at https://developer.salesforce.com/docs.\n")
    assert 'href="https://developer.salesforce.com/docs"' in dot, "trailing period must not be part of the URL"
    # markdown external link -> new tab
    mdext = m.md_to_html("[Guide](https://help.salesforce.com/x)\n")
    assert '<a href="https://help.salesforce.com/x" target="_blank" rel="noopener noreferrer">Guide</a>' in mdext, "md external link must open in a new tab"
    # internal relative link -> same tab (no target=_blank)
    intl = m.md_to_html("[Home](index.html)\n")
    assert '<a href="index.html">Home</a>' in intl, "internal relative link must stay same-tab"
    assert "index.html\" target" not in intl, "internal link must NOT get target=_blank"
    # no double-wrap: a markdown link whose URL is also a bare-URL pattern stays a single anchor
    once = m.md_to_html("[x](https://a.com/b)\n")
    assert once.count("<a ") == 1, "a markdown link must not be re-wrapped by the bare-URL pass"

# ---- R-MD2H-04: HTML comments (the VOICE marker) are stripped, not rendered as visible text --
@check("R-MD2H-04: md_to_html + slide_deck strip HTML comments (the VOICE authoring marker) instead of escaping them into visible body text")
def t_html_comment_stripped():
    m = _load_script("scripts/md_to_html.py", "md2h_cmt_mod")
    sd = _load_script("scripts/slide_deck.py", "slide_cmt_mod")
    sample = ("<!-- VOICE: narrative — first-person exec/architect McKinsey register; see refs/voice-and-style.md -->\n"
              "# Title\n\n## A Section\nReal body content.\n")
    h = m.md_to_html(sample)
    assert "VOICE:" not in h, "md_to_html must strip the VOICE comment, not render it"
    assert "&lt;!--" not in h and "<!--" not in h, "md_to_html must not emit the HTML comment (escaped or raw)"
    assert "Real body content" in h, "real content must still render"
    # every shipped template carries the VOICE marker on line 1 -> confirm it never survives a render
    for f in os.listdir(os.path.join(SKILL, "templates")):
        if f.endswith(".md"):
            assert "VOICE:" not in m.md_to_html(read(f"templates/{f}")), f"VOICE leaked from templates/{f}"
    # slide deck path strips it too (cover + section slides, no leaked comment)
    deck = sd.build_deck(sample, "T", "L", "summer-26", "2026-06-24")
    assert "VOICE:" not in deck and "&lt;!--" not in deck, "slide_deck must strip the VOICE comment"

# ---- R-DOC-01: hardcoded artifact-count / check-count claims match reality --
# This is the systemic guard for the "registry grew but prose still says N" drift class:
# the rest of the suite is registry-derived (it stays green while docs hardcode a stale count),
# so this check greps the human-facing docs for count claims and pins them to the real sizes.
@check("R-DOC-01: hardcoded 'N artifacts/deliverables' and 'N checks' claims in SKILL.md/refs/README match the real registry + suite size")
def t_doc_count_drift():
    n_art = len(ARTIFACT_REGISTRY)
    n_chk = len(RESULTS)  # at run time RESULTS already includes every @check, this one included
    docs = ["SKILL.md", "README.md", "refs/artifact-templates.md", "refs/voice-and-style.md",
            "refs/quality-loops.md", "refs/render-and-canvas.md", "refs/intake-source-map.md"]
    # Only match FAMILY-SIZE claims ("the 13 artifacts", "all 13 deliverables") -- not ranges/rates
    # like "3-4 artifacts per subagent". A claim qualifies when an article/the/all precedes the number
    # and no hyphen-range immediately precedes it.
    art_claim = re.compile(r"(?:\b(?:the|all)\s+)(\d{1,3})\s+(?:artifact|deliverable)s?\b", re.I)
    chk_claim = re.compile(r"\b(\d{1,3})\s+checks?\b", re.I)
    bad = []
    for d in docs:
        if not exists(d):
            continue
        body = read(d)
        for m in art_claim.finditer(body):
            if int(m.group(1)) != n_art:
                bad.append(f"{d}: '{m.group(0)}' but ARTIFACT_REGISTRY has {n_art}")
        for m in chk_claim.finditer(body):
            if int(m.group(1)) != n_chk:
                bad.append(f"{d}: '{m.group(0)}' but the suite has {n_chk} checks")
    assert not bad, "stale count claim(s) — registry/suite grew but a doc hardcodes the old number:\n  " + "\n  ".join(bad)

# ---- runner -------------------------------------------------------------
def main():
    failed = 0
    for name, fn in RESULTS:
        try:
            fn(); print(f"PASS  {name}")
        except AssertionError as e:
            failed += 1; print(f"FAIL  {name}\n      {e}")
    print(f"\n{len(RESULTS)-failed}/{len(RESULTS)} checks passed")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
