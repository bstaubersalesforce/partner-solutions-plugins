#!/usr/bin/env python3
"""
Validation suite ("test class") for the tech-strat-pov-forge skill.

Asserts the structural invariants of the skill — the contracts that must hold
for the skill to run correctly. It does NOT judge LLM output quality (that is
not unit-testable); it validates files, references, tokens, and naming so a
careless edit can't silently break the skill.

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

# SKILL.md (core flow) + every per-stage file under refs/stages/ form one
# instruction corpus; reference/stage checks must span all of them.
def _instruction_files():
    # Assumes only per-stage definition files live in refs/stages/ (guarded by t_stage_router_parity).
    files = ["SKILL.md"]
    stages_dir = os.path.join(SKILL, "refs/stages")
    if os.path.isdir(stages_dir):
        files += sorted(f"refs/stages/{f}" for f in os.listdir(stages_dir) if f.endswith(".md"))
    return files
INSTRUCTION_FILES = _instruction_files()
def instructions():
    return "\n".join(read(f) for f in INSTRUCTION_FILES if exists(f))

TEMPLATE_HTML = [
    "templates/mvp-build-plan.html", "templates/investor-presentation.html",
    "templates/solution-infographic.html", "templates/partner-readiness-scorecard.html",
    "templates/document-shell.html", "templates/output-index.html",
    "templates/marketecture.html",
    "templates/discovery-document.html",
    "templates/technical-architecture-assessment.html",
    "templates/consumption-opportunities.html",
    "templates/competitive-assessment.html",
]
TOKEN_RE = re.compile(r"\{\{([^{}]*)\}\}")

# ---- 1. cross-reference integrity --------------------------------------
@check("Every file path referenced in the instructions exists")
def t_refs_exist():
    skill = instructions()
    paths = set(re.findall(r"(?:templates|refs|validation|scripts)/[A-Za-z0-9._/-]+", skill))
    missing = []
    for p in paths:
        p = p.rstrip(".")                 # strip trailing sentence punctuation
        if p == "refs/verticals":         # directory reference
            if not os.path.isdir(os.path.join(SKILL, p)): missing.append(p)
        elif not exists(p):
            missing.append(p)
    assert not missing, f"referenced but missing: {sorted(missing)}"

@check("Every template/validation/script/ref file is referenced by the instructions (no orphans)")
def t_no_orphans():
    skill = instructions()
    orphans = []
    # Flat dirs: every file must be named somewhere in the instruction corpus.
    for d in ("templates", "validation", "scripts"):
        for f in os.listdir(os.path.join(SKILL, d)):
            if f.startswith(".") or f == "__pycache__": continue  # caches aren't artifacts
            if not os.path.isfile(os.path.join(SKILL, d, f)): continue  # skip sub-dirs
            if f"{d}/{f}" not in skill: orphans.append(f"{d}/{f}")
    # Top-level refs/ files (verticals/ handled by the router-parity check, and
    # the instruction files themselves are not required to self-reference).
    for f in os.listdir(os.path.join(SKILL, "refs")):
        if f.startswith(".") or f"refs/{f}" in INSTRUCTION_FILES: continue
        if not os.path.isfile(os.path.join(SKILL, "refs", f)): continue  # skip verticals/ dir
        if f"refs/{f}" not in skill: orphans.append(f"refs/{f}")
    assert not orphans, f"present but never referenced: {sorted(orphans)}"

# ---- 1b. vertical router integrity --------------------------------------
# The router (refs/industry-alignment.md) is the only thing that points to the
# per-vertical files; INSTRUCTION_FILES does not, so these checks guard the
# router↔verticals contract that t_refs_exist / t_no_orphans cannot see.
VERTICAL_HEADINGS = [
    "**Salesforce Industry Cloud:**", "**Market snapshot:**",
    "**Key focus areas:**", "**Top aligned use cases:**",
    "**Regulatory drivers:**", "**Suggested KPIs", "**MVP alignment signal:**",
]

# ---- 1c. discovery framework integrity ----------------------------------
# The discovery framework, its output template, and its checklist must list
# the same 10 dimensions; t_discovery_dimension_parity (below) guards that.
DISCOVERY_DIMENSIONS = [
    "Users, Personas & Journeys",
    "Operational Process Flows",
    "Pain & Friction Points",
    "Success Metrics & Desired Outcomes",
    "Technical Architecture & Readiness",
    "Salesforce Ecosystem Footprint",
    "Data Landscape & Sources",
    "Business Alignment",
    "Decision-Making & Stakeholders",
    "Competitive Landscape & Alternatives",
]
DISCOVERY_FILES = [
    "refs/discovery-framework.md",
    "templates/discovery-document.md",
    "validation/discovery-checklist.md",
]

# ---- 1d. architecture assessment integrity ------------------------------
# The architecture-assessment ref, its template, and its checklist must all
# carry the Well-Architected pillars/qualities; t_well_architected_parity guards it.
WA_PILLARS = ["Trusted", "Easy", "Adaptable"]
WA_QUALITIES = ["Secure", "Compliant", "Reliable", "Intentional",
                "Automated", "Engaging", "Resilient", "Composable"]
ARCH_FILES = [
    "refs/architecture-assessment.md",
    "templates/technical-architecture-assessment.md",
    "validation/architecture-checklist.md",
]

# ---- 1e. stage-file architecture integrity ------------------------------
# The downstream optional stages (8-18) each live in their own file under
# refs/stages/; SKILL.md's router must point to each, bidirectionally.
DOWNSTREAM_STAGES = {
    8:  "refs/stages/stage-08-mvp-build-plan.md",
    9:  "refs/stages/stage-09-red-team.md",
    10: "refs/stages/stage-10-investor-presentation.md",
    11: "refs/stages/stage-11-solution-infographic.md",
    12: "refs/stages/stage-12-partner-readiness-scorecard.md",
    13: "refs/stages/stage-13-output-home-page.md",
    14: "refs/stages/stage-14-marketecture.md",
    15: "refs/stages/stage-15-discovery-framework.md",
    16: "refs/stages/stage-16-architecture-assessment.md",
    17: "refs/stages/stage-17-pov-presentation.md",
    18: "refs/stages/stage-18-consumption-opportunities.md",
    19: "refs/stages/stage-19-competitive-assessment.md",
}

@check("Router and refs/verticals/ are in bidirectional sync (no missing/orphan verticals)")
def t_router_vertical_parity():
    router = read("refs/industry-alignment.md")
    on_disk = {f"refs/verticals/{f}" for f in os.listdir(os.path.join(SKILL, "refs/verticals"))
               if f.endswith(".md")}
    in_router = set(re.findall(r"refs/verticals/[a-z0-9-]+\.md", router))
    missing = sorted(in_router - on_disk)   # router names a file that doesn't exist
    orphan  = sorted(on_disk - in_router)   # vertical file the router never lists
    assert not missing, f"router points to missing vertical files: {missing}"
    assert not orphan, f"vertical files absent from router lookup: {orphan}"

@check("Every refs/verticals/ file carries the full vertical schema")
def t_vertical_schema():
    bad = {}
    for f in sorted(os.listdir(os.path.join(SKILL, "refs/verticals"))):
        if not f.endswith(".md"): continue
        s = read(f"refs/verticals/{f}")
        gaps = [h.rstrip(":*") for h in VERTICAL_HEADINGS if h not in s]
        if gaps: bad[f] = gaps
    assert not bad, f"vertical files missing required sections: {bad}"

@check("No vertical leads its Industry Cloud line with a 'no SKU' disclaimer (uniform schema)")
def t_vertical_cloud_line_uniform():
    # The Industry Cloud line must open by naming the cloud(s) Salesforce uses for
    # the vertical — not with a "No standalone/dedicated X Cloud" disclaimer. Verticals
    # with no purpose-built SKU still lead with the clouds they DO use; the no-SKU note
    # is demoted to a trailing clause. Keeps the line scannable and uniform across files.
    disclaimer = re.compile(r"^(no\b|n/a|none\b)", re.I)
    bad = {}
    for f in sorted(os.listdir(os.path.join(SKILL, "refs/verticals"))):
        if not f.endswith(".md"): continue
        for line in read(f"refs/verticals/{f}").splitlines():
            if line.startswith("**Salesforce Industry Cloud:**"):
                rest = line.split("**Salesforce Industry Cloud:**", 1)[1].lstrip().lstrip("*").lstrip()
                if disclaimer.match(rest):
                    bad[f] = rest[:60]
                break
    assert not bad, f"Industry Cloud line leads with a disclaimer (lead with the clouds instead): {bad}"

@check("Discovery framework, template, and checklist list the same 10 dimensions")
def t_discovery_dimension_parity():
    bad = {}
    for rel in DISCOVERY_FILES:
        s = read(rel)
        missing = [d for d in DISCOVERY_DIMENSIONS if d not in s]
        if missing:
            bad[rel] = missing
    assert not bad, f"files missing discovery dimensions: {bad}"

@check("Red team lenses, template, and checklist list the same 6 frameworks")
def t_red_team_frameworks():
    lenses = read("refs/red-team-lenses.md")
    template = read("templates/red-team-assessment.md")
    checklist = read("validation/red-team-checklist.md")
    for name in ("Salesforce Investment Teardown", "Commercial Model Pressure Test"):
        assert name in lenses, f"red-team-lenses.md missing framework '{name}'"
        assert name in template, f"red-team-assessment.md missing framework '{name}'"
        assert name in checklist, f"red-team-checklist.md missing framework '{name}'"
    assert "## Framework 5:" in template, "template missing '## Framework 5:' heading"
    assert "## Framework 6:" in template, "template missing '## Framework 6:' heading"
    assert "Biggest Blind Spot" in template, "template Synthesis missing 'Biggest Blind Spot'"
    assert "6 frameworks" in checklist, "checklist does not say '6 frameworks'"
    assert "4 frameworks" not in checklist, "checklist still says '4 frameworks'"

@check("Discovery template (md+html) carries the capture slot + mode/status header")
def t_discovery_capture_slot():
    md = read("templates/discovery-document.md")
    html = read("templates/discovery-document.html")
    assert "Discussion capture: [pending]" in md, "md template missing capture sentinel"
    assert re.search(r"Mode:.*(Auto-capture|Workshop)", md), "md template missing mode/status header"
    assert "{{MODE_STATUS}}" in html, "html template missing {{MODE_STATUS}} token"
    assert "discussion-capture" in html, "html template missing discussion-capture slot styling/markup"

@check("Discovery reference defines auto-capture mode + capture-readback")
def t_discovery_two_mode():
    ref = read("refs/discovery-framework.md")
    low = ref.lower()
    assert "auto-capture" in low, "discovery-framework.md missing auto-capture mode"
    assert "workshop" in low, "discovery-framework.md missing workshop mode"
    assert "readback" in low and "source of truth" in low, \
        "discovery-framework.md missing capture-readback procedure"

@check("Architecture ref, template, and checklist carry the Well-Architected pillars + 8 qualities")
def t_well_architected_parity():
    bad = {}
    for rel in ARCH_FILES:
        s = read(rel)
        missing = [w for w in WA_PILLARS + WA_QUALITIES if w not in s]
        if missing:
            bad[rel] = missing
    assert not bad, f"files missing Well-Architected terms: {bad}"

@check("SKILL.md router and refs/stages/ are in bidirectional sync (stages 8-18)")
def t_stage_router_parity():
    skill = read("SKILL.md")
    on_disk = {f"refs/stages/{f}" for f in os.listdir(os.path.join(SKILL, "refs/stages"))
               if f.endswith(".md")}
    expected = set(DOWNSTREAM_STAGES.values())
    missing_files = sorted(expected - on_disk)          # router maps a stage to a missing file
    orphan_files  = sorted(on_disk - expected)          # stage file not in the canonical map
    assert not missing_files, f"router stages with no file on disk: {missing_files}"
    assert not orphan_files, f"refs/stages files absent from the stage map: {orphan_files}"
    not_routed = sorted(p for p in expected if p not in skill)  # file exists but SKILL.md never links it
    assert not not_routed, f"stage files not referenced by the SKILL.md router: {not_routed}"

@check("Consumption stage 18 files exist and are wired")
def t_consumption_stage_files():
    assert exists("refs/stages/stage-18-consumption-opportunities.md"), "stage-18 file missing"
    assert exists("templates/consumption-opportunities.md"), "consumption md template missing"
    assert exists("templates/consumption-opportunities.html"), "consumption html template missing"
    assert exists("validation/consumption-checklist.md"), "consumption checklist missing"
    skill = read("SKILL.md")
    assert "refs/stages/stage-18-consumption-opportunities.md" in skill, "SKILL.md router missing stage 18"
    stage = read("refs/stages/stage-18-consumption-opportunities.md")
    assert re.search(r"^\*\*Stage 18 —", stage, re.M), "stage-18 missing '**Stage 18 —' heading"

@check("Consumption estimation rate-card ref exists, is wired, and carries the model")
def t_consumption_estimation_ref():
    assert exists("refs/consumption-estimation.md"), "refs/consumption-estimation.md missing"
    ref = read("refs/consumption-estimation.md")
    # core credit rules (from the Agentforce Credit Estimator + Questionnaire)
    assert "20" in ref and re.search(r"action", ref, re.I), "ref missing 20-credit action rule"
    assert re.search(r"\b2\b.*basic|basic.*\b2\b", ref, re.I), "ref missing basic-prompt (2) rule"
    assert re.search(r"\b4\b.*standard|standard.*\b4\b", ref, re.I), "ref missing standard-prompt (4) rule"
    # Data 360 model + a known meter
    assert re.search(r"run frequency", ref, re.I), "ref missing Data 360 run-frequency lever"
    assert "100,000" in ref or "100000" in ref, "ref missing Profile Unification meter"
    # abstract bands (no reference ranges) + sync note
    assert re.search(r"\bS/M/L/XL\b|abstract", ref, re.I), "ref missing abstract band model"
    assert re.search(r"sf-flex-estimator", ref), "ref missing authoritative-owner sync note"
    # stage 18 must load it
    assert "refs/consumption-estimation.md" in read("refs/stages/stage-18-consumption-opportunities.md"), \
        "stage-18 does not load the rate-card ref"

@check("Stage 18 instructs the directional estimate (anchored band, credits, no $)")
def t_stage18_directional_instructions():
    s = read("refs/stages/stage-18-consumption-opportunities.md")
    assert re.search(r"directional", s, re.I), "stage-18 missing directional-estimate instruction"
    assert re.search(r"sizing-band anchor|anchored band|anchor.*band", s, re.I), \
        "stage-18 missing the Sizing-Band Anchor instruction"
    assert re.search(r"U\s*[×x]\s*F\s*[×x]\s*A", s), "stage-18 missing the U×F×A volume formula"
    assert re.search(r"credits?, not (a )?dollar|no dollar|not produce.*dollar", s, re.I), \
        "stage-18 must keep the credits-only (no dollar) boundary"

@check("Consumption MD template carries the anchor note + per-opportunity estimate fields")
def t_consumption_md_estimate_fields():
    md = read("templates/consumption-opportunities.md")
    assert "Sizing-Band Anchor" in md, "md template missing Sizing-Band Anchor note"
    assert re.search(r"Directional [Ee]stimate", md), "md template missing per-opportunity Directional Estimate block"
    assert re.search(r"U\s*[×x]\s*F\s*[×x]\s*A", md), "md template missing U×F×A assumptions line"
    assert re.search(r"credit", md, re.I), "md template missing credit-band field"
    assert re.search(r"Est\. credits|Directional credits", md), "md map table missing directional-credits column"

@check("Consumption HTML carries the sizing-band note token + directional-credits column")
def t_consumption_html_estimate():
    html = read("templates/consumption-opportunities.html")
    assert "{{SIZING_BAND_NOTE}}" in html, "html missing {{SIZING_BAND_NOTE}} token"
    assert html.count("{{SIZING_BAND_NOTE}}") == 1, "{{SIZING_BAND_NOTE}} must appear exactly once"
    assert re.search(r"Est\. credits|Directional credits", html), "html map table missing directional-credits header"

@check("Consumption checklist guards the directional estimate (present, credits-only)")
def t_consumption_checklist_estimate_guards():
    cl = read("validation/consumption-checklist.md")
    assert re.search(r"Sizing-Band Anchor", cl), "checklist missing anchor-note check"
    assert re.search(r"directional", cl, re.I), "checklist missing directional-estimate check"
    assert re.search(r"assumption", cl, re.I), "checklist missing assumptions-shown check"
    assert re.search(r"no dollar|NO dollar|never.*dollar|credits?-only", cl, re.I), \
        "checklist lost the no-dollar guard"

@check("SKILL.md Stage 7 menu mentions the directional consumption pre-estimate")
def t_skill_menu_directional():
    s = read("SKILL.md")
    m = re.search(r"Consumption Opportunities.*?\n.*?directional", s, re.S | re.I)
    assert m, "SKILL.md Consumption Opportunities menu option does not mention the directional pre-estimate"

@check("Competitive Assessment stage 19 files exist and are wired")
def t_competitive_stage_files():
    assert exists("refs/stages/stage-19-competitive-assessment.md"), "stage-19 file missing"
    assert exists("templates/competitive-assessment.md"), "competitive md template missing"
    assert exists("templates/competitive-assessment.html"), "competitive html template missing"
    assert exists("validation/competitive-checklist.md"), "competitive checklist missing"
    assert exists("refs/competitive-landscape.md"), "competitive-landscape ref missing"
    skill = read("SKILL.md")
    assert "refs/stages/stage-19-competitive-assessment.md" in skill, "SKILL.md router missing stage 19"
    stage = read("refs/stages/stage-19-competitive-assessment.md")
    assert re.search(r"^\*\*Stage 19 —", stage, re.M), "stage-19 missing '**Stage 19 —' heading"

@check("Every refs/stages/ file carries its '**Stage N —' heading")
def t_stage_file_schema():
    bad = {}
    for n, rel in DOWNSTREAM_STAGES.items():
        if not exists(rel):
            bad[rel] = "missing file"; continue
        if not re.search(rf"^\*\*Stage {n} ", read(rel), re.M):
            bad[rel] = f"no '**Stage {n} ' heading"
    assert not bad, f"stage files failing schema: {bad}"

# Stages that fill an HTML template — they must point to the shared method ref,
# not SKILL.md, so a fanned-out subagent (which lacks SKILL.md) can load it.
HTML_STAGE_FILES = [
    "refs/stages/stage-08-mvp-build-plan.md",
    "refs/stages/stage-10-investor-presentation.md",
    "refs/stages/stage-11-solution-infographic.md",
    "refs/stages/stage-12-partner-readiness-scorecard.md",
    "refs/stages/stage-13-output-home-page.md",
    "refs/stages/stage-14-marketecture.md",
    "refs/stages/stage-17-pov-presentation.md",
    "refs/stages/stage-19-competitive-assessment.md",
]

# Every HTML artifact carries a home-page back-link via the {{HOME_HREF}} token,
# and that token must appear exactly once per template (a second occurrence — e.g.
# inside a comment — would double-inject under plain string-replace).
HOME_LINK_TEMPLATES = [
    "templates/investor-presentation.html",
    "templates/solution-infographic.html",
    "templates/marketecture.html",
    "templates/mvp-build-plan.html",
    "templates/partner-readiness-scorecard.html",
    "templates/technical-architecture-assessment.html",
    "templates/pov-presentation.html",
    "templates/document-shell.html",
    "templates/discovery-document.html",
    "templates/consumption-opportunities.html",
    "templates/competitive-assessment.html",
]

@check("HTML Output Method lives in its own ref and every HTML stage points to it")
def t_html_output_method_ref():
    assert exists("refs/html-output-method.md"), "refs/html-output-method.md is missing"
    method = read("refs/html-output-method.md").lower()
    for marker in ("placeholder", "regex", "token"):   # core of the method
        assert marker in method, f"html-output-method.md missing '{marker}'"
    missing = [f for f in HTML_STAGE_FILES if "refs/html-output-method.md" not in read(f)]
    assert not missing, f"HTML stage files not pointing to the method ref: {missing}"

@check("Every HTML artifact template carries exactly one {{HOME_HREF}} back-link token")
def t_home_link_token_once():
    bad = {}
    for rel in HOME_LINK_TEMPLATES:
        if not exists(rel):
            bad[rel] = "missing file"; continue
        n = read(rel).count("{{HOME_HREF}}")
        if n != 1:
            bad[rel] = f"{n} HOME_HREF tokens (want exactly 1)"
    assert not bad, f"home-link token defects: {bad}"

# The {{HOME_HREF}} token must live inside the "All artifacts" pill anchor — not
# loose in the markup. This guards the template side; scripts/ensure-home-link.py
# guards the runtime output side (it detects the pill by this same anchor shape).
HOME_LINK_ANCHOR_RE = re.compile(
    r'<a\s+[^>]*href="\{\{HOME_HREF\}\}"[^>]*>\s*(?:&#8592;|&larr;|←)?\s*All artifacts\s*</a>',
    re.IGNORECASE,
)

@check("Every HTML artifact template wraps {{HOME_HREF}} in an 'All artifacts' pill anchor")
def t_home_link_anchor_shape():
    bad = {}
    for rel in HOME_LINK_TEMPLATES:
        if not exists(rel):
            bad[rel] = "missing file"; continue
        if not HOME_LINK_ANCHOR_RE.search(read(rel)):
            bad[rel] = "no <a href=\"{{HOME_HREF}}\">… All artifacts</a> pill"
    assert not bad, f"home-link pill defects: {bad}"

@check("The Markdown->HTML converter script exists and Stage 13 invokes it")
def t_md_to_html_script():
    assert exists("scripts/md-to-html.py"), "scripts/md-to-html.py is missing"
    stage13 = read("refs/stages/stage-13-output-home-page.md")
    assert "scripts/md-to-html.py" in stage13, "Stage 13 does not invoke scripts/md-to-html.py"

@check("Stage 13 references the discovery-document filename")
def t_stage13_discovery_filename():
    s = read("refs/stages/stage-13-output-home-page.md")
    assert "discovery-document" in s, "Stage 13 does not reference {SLUG}-discovery-document"

@check("Stage 13 references the consumption-opportunities filename")
def t_stage13_consumption_filename():
    s = read("refs/stages/stage-13-output-home-page.md")
    assert "consumption-opportunities" in s, "Stage 13 does not reference {SLUG}-consumption-opportunities"

@check("Stage 13 references the competitive-assessment filename")
def t_stage13_competitive_filename():
    s = read("refs/stages/stage-13-output-home-page.md")
    assert "competitive-assessment" in s, "Stage 13 does not reference {SLUG}-competitive-assessment"

@check("refs/parallel-dispatch.md defines the dispatch protocol elements")
def t_dispatch_protocol_tokens():
    if not exists("refs/parallel-dispatch.md"):
        raise AssertionError("refs/parallel-dispatch.md is missing")
    s = read("refs/parallel-dispatch.md").lower()
    required = {
        "threshold (>=3)":   "3 or more",
        "compact payload":   "compact payload",
        "wave order 16->8":  "wave 0",
        "home page last":    "stage 13",
        "graceful fallback": "fall back",
        "pov persisted":     "persist the approved pov",
        "package date":      "package_date",      # one date fixed by orchestrator, passed to every subagent
        "confidence anchor": "anchor to the pov",  # analytical artifacts anchor confidence to the POV
        "fill-script sweep": "_fill",             # orchestrator sweeps stray fill scripts before the home page
        "per-artifact critic": "per-artifact critic",     # Feature 1 — heavy-artifact generate→critic→repair loop
        "package critic":      "completeness-critic",     # Feature 2 — Wave-2 cross-artifact critic
    }
    missing = sorted(label for label, needle in required.items() if needle not in s)
    assert not missing, f"parallel-dispatch.md missing protocol elements: {missing}"

@check("Parallel dispatch includes Stage 15 auto-capture in Wave 1 + capture-preservation check")
def t_dispatch_discovery():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "stage 15" in low, "parallel-dispatch.md does not mention Stage 15"
    assert "auto-capture" in low, "parallel-dispatch.md missing auto-capture directive for discovery"
    assert "capture-preservation" in low or "archive" in low, \
        "parallel-dispatch.md missing the capture-preservation/archive check"

@check("Parallel dispatch includes Stage 18 (Consumption) in Wave 1")
def t_dispatch_consumption():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "stage 18" in low or "consumption" in low, "parallel-dispatch.md missing Stage 18 / consumption"

@check("Parallel dispatch includes Stage 19 (Competitive Assessment) in Wave 1")
def t_dispatch_competitive():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "stage 19" in low or "competitive assessment" in low, \
        "parallel-dispatch.md missing Stage 19 / competitive assessment"

@check("Per-artifact critic pipeline (Stages 8/9/16) is defined with a 1-round cap")
def t_per_artifact_critic():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "per-artifact critic" in low, "missing the 'per-artifact critic' section"
    # the generate → critic → repair pipeline, named
    assert "generate" in low and "critic" in low and "repair" in low, \
        "per-artifact pipeline must name generate / critic / repair"
    assert "generate → critic → repair" in low or "generate, critic, repair" in low, \
        "per-artifact section must name the 'generate → critic → repair' pipeline explicitly"
    # scoped to the three heavy artifacts
    for s in ("stage 8", "stage 9", "stage 16"):
        assert s in low, f"per-artifact critic must name {s} as in scope"
    # one-round cap
    assert "one round" in low or "1 round" in low or "one-round" in low, \
        "per-artifact critic must state the one-round repair cap"

@check("Package completeness-critic (Wave 2) defines its 4 defect classes and ordering")
def t_package_critic():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "completeness-critic" in low, "missing the 'completeness-critic' (Wave 2) section"
    assert "wave 2" in low, "package critic must be labelled Wave 2"
    # four defect classes
    classes = {
        "contradiction with the pov": "contradiction with the pov",
        "contradiction between artifacts": "contradiction between artifacts",
        "confidence drift": "confidence drift",
        "anti-overlap": "anti-overlap",
    }
    missing = sorted(label for label, needle in classes.items() if needle not in low)
    assert not missing, f"package critic missing defect classes: {missing}"
    # ordering: after the mechanical cleanups, before Stage 13
    assert "after the mechanical cleanup" in low, \
        "package critic must state it runs AFTER the mechanical cleanups"
    assert "before stage 13" in low, "package critic must state it runs BEFORE Stage 13"
    # detect → auto-repair, one round
    assert "auto-repair" in low, "package critic must state detect → auto-repair"
    assert "one round" in low or "1 round" in low or "one-round" in low, \
        "package critic must state the one-round cap"

@check("Both critics are independent subagents; repair is a fresh subagent")
def t_critic_independence():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "independent" in low or "separate subagent" in low, \
        "protocol must state the critic is independent of the generator"
    assert "fresh repair subagent" in low or "fresh subagent" in low, \
        "protocol must state repair runs on a fresh subagent"
    # the principle: do not let the author grade its own work
    assert "grade" in low or "grading" in low or "attacks the artifact" in low, \
        "protocol must state the don't-grade-your-own-work rationale"

@check("Repair safety: scoped-edit constraint + post-repair re-validation gate")
def t_repair_safety():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    # scoped-edit constraint
    assert "edit" in low and "in place" in low, "repair must state 'edit in place'"
    assert "do not regenerate" in low, \
        "repair must forbid regeneration ('do not regenerate')"
    # post-repair re-validation gate — anchor to the affirmative gate terms, not a bare
    # "re-run" (which also appears in the negative "does not re-run the checklist" sentence)
    assert "post-repair" in low or "re-validation" in low, \
        "protocol must state a post-repair re-validation step"
    assert "previously-passing" in low or "previously passing" in low, \
        "re-validation gate must discard a repair that regresses a previously-passing check"
    assert "discard the repair" in low, \
        "re-validation gate must say discard the repair and keep the pre-repair version"

@check("Per-artifact critic payload is widened (stage file + framework + vertical + discovery) with the build-detail exclusion")
def t_critic_payload():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    # the four context inputs beyond artifact + POV
    assert "stage instruction file" in low or "its stage file" in low or "stage-nn" in low, \
        "critic payload must include the artifact's own stage instruction file"
    assert "og-tech-strategy-framework.md" in low, "critic payload must include the framework spine"
    assert "vertical file" in low or "refs/verticals/" in low, \
        "critic payload must include the matched vertical file"
    # anchor to the new payload prose ('Discovery Theme' rationale), not the pre-existing
    # capture-preservation mention of 'discovery-document' elsewhere in the file
    assert "discovery theme" in low and ("discovery-document" in low or "discovery document" in low), \
        "critic payload must include the package discovery document (with the Discovery-Theme rationale)"
    # the mandated-build-detail exclusion
    assert "by mandate" in low or "mandated" in low, \
        "critic lens must carry the mandated-build-detail exclusion"
    assert "do not flag" in low, \
        "exclusion must instruct the critic NOT to flag mandated build detail as ungrounded"

@check("Critics carry the disclosed-gap exclusion (never fabricate to close a known TBD)")
def t_disclosed_gap_exclusion():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "disclosed gap" in low or "disclosed-gap" in low, \
        "critics must define a disclosed-gap exclusion"
    # the rule: a gap the POV/artifact already discloses (TBD / not-yet-committed) is not a defect
    assert "already discloses" in low or "honestly-disclosed" in low or "honestly disclosed" in low, \
        "disclosed-gap exclusion must key off a gap the POV/artifact already discloses"
    # the anti-fabrication imperative on repair
    assert "never fabricate" in low or "do not fabricate" in low or "never invent" in low, \
        "disclosed-gap exclusion must forbid fabricating a value to close a disclosed gap"

@check("Anti-overlap (class 4) is advisory — reported, not auto-repaired")
def t_class4_advisory():
    ref = read("refs/parallel-dispatch.md")
    low = ref.lower()
    assert "advisory" in low, "class-4 anti-overlap findings must be marked advisory"
    # classes 1-3 auto-repair; class 4 is reported, not repaired
    assert "not auto-repaired" in low or "reported, not" in low or "not repaired" in low, \
        "anti-overlap (class 4) must be reported, not auto-repaired"

@check("SKILL.md Stage 7 points to the dispatch protocol with the >=3 threshold")
def t_dispatch_pointer():
    skill = read("SKILL.md")
    assert "refs/parallel-dispatch.md" in skill, "SKILL.md never references refs/parallel-dispatch.md"
    assert "3 or more" in skill, "SKILL.md does not state the '3 or more' dispatch threshold"

# ---- 2. token hygiene ---------------------------------------------------
@check("HTML templates have balanced {{ }} braces")
def t_braces_balanced():
    bad = []
    for t in TEMPLATE_HTML:
        s = read(t)
        if s.count("{{") != s.count("}}"):
            bad.append(f"{t} (open={s.count('{{')} close={s.count('}}')})")
    assert not bad, f"unbalanced: {bad}"

@check("Every {{TOKEN}} is UPPER_SNAKE_CASE")
def t_token_convention():
    bad = {}
    for t in TEMPLATE_HTML:
        offenders = [tok for tok in TOKEN_RE.findall(read(t)) if not re.fullmatch(r"[A-Z0-9_]+", tok)]
        if offenders: bad[t] = offenders
    assert not bad, f"malformed tokens: {bad}"

@check("Variable-length block tokens appear at most once per template (no glossary double-fill)")
def t_no_block_token_doubling():
    # Tokens filled by injecting a variable-length HTML block (rows/blocks/sections)
    # must occur exactly once. A second occurrence — typically a {{TOKEN}} copy inside
    # a TOKEN-REFERENCE comment — double-injects the whole block under string-replace
    # (the document-shell {{CONTENT}} bug class). Scalar header tokens (PARTNER_NAME in
    # <title> + <h1>) may legitimately repeat, so only block-family suffixes are checked.
    block_suffixes = ("_HTML", "_ROWS", "_BLOCKS")
    bad = {}
    for t in TEMPLATE_HTML:
        s = read(t)
        for tok in set(TOKEN_RE.findall(s)):
            if tok.endswith(block_suffixes):
                n = s.count("{{" + tok + "}}")
                if n > 1:
                    bad.setdefault(t, []).append(f"{tok}×{n}")
    assert not bad, f"block tokens duplicated (will double-inject): {bad}"

@check("Discovery HTML carries the VPC and BMC canvas token families")
def t_discovery_canvas_tokens():
    s = read("templates/discovery-document.html")
    vpc = [f"VPC_{x}" for x in ("JOBS","PAINS","GAINS","PRODUCTS","RELIEVERS","CREATORS")]
    bmc = [f"BMC_{x}" for x in ("PARTNERSHIPS","ACTIVITIES","VALUE_PROPS","RELATIONSHIPS",
                                "SEGMENTS","RESOURCES","CHANNELS","COSTS","REVENUE")]
    missing = [t for t in vpc + bmc if f"{{{{{t}}}}}" not in s]
    assert not missing, f"discovery HTML missing canvas tokens: {missing}"

@check("Architecture HTML carries the Well-Architected RAG token families")
def t_architecture_rag_tokens():
    s = read("templates/technical-architecture-assessment.html")
    keys = ["SECURE","COMPLIANT","RELIABLE","INTENTIONAL","AUTOMATED","ENGAGING","RESILIENT","COMPOSABLE"]
    missing = []
    for k in keys:
        for suffix in ("RAG", "NOTE"):
            if f"{{{{WA_{k}_{suffix}}}}}" not in s:
                missing.append(f"WA_{k}_{suffix}")
    assert not missing, f"architecture HTML missing RAG tokens: {missing}"

# ---- 2b. vertical-neutrality of HTML templates --------------------------
# The HTML templates are vertical-agnostic shells; any industry-specific name
# (a cloud SKU, a standard, a regulation) must be a {{TOKEN}} filled at runtime,
# never baked-in literal text. Hardcoded literals leak one partner's vertical
# (usually the build that seeded the template) into every other partner's output.
# Program-universal strings (AppExchange, "Built on Salesforce") are allowed.
VERTICAL_LITERALS = [
    "HIPAA", "FHIR", "Epic", "Cerner", "HL7", "HEDIS", "ICD-10",
    "Health Cloud", "FSC", "FedRAMP", "Basel", "FINRA",
]
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)

@check("HTML templates carry no hardcoded vertical-specific literals (must be tokens)")
def t_html_vertical_neutral():
    bad = {}
    for t in TEMPLATE_HTML:
        body = _HTML_COMMENT_RE.sub("", read(t))   # ignore comments/fill-guides
        hits = sorted({lit for lit in VERTICAL_LITERALS
                       if re.search(rf"(?<![A-Za-z]){re.escape(lit)}(?![A-Za-z])", body)})
        if hits:
            bad[t] = hits
    assert not bad, f"hardcoded vertical literals (tokenize these): {bad}"

# ---- 3. scorecard structural completeness -------------------------------
@check("Scorecard HTML has complete A1..A18 token families")
def t_scorecard_tokens():
    s = read("templates/partner-readiness-scorecard.html")
    missing = []
    for i in range(1, 19):
        for suffix in ("STATUS_CLASS", "STATUS", "OWNER", "NOTES"):
            if f"{{{{A{i}_{suffix}}}}}" not in s:
                missing.append(f"A{i}_{suffix}")
    assert not missing, f"missing row tokens: {missing}"

@check("Scorecard Markdown has exactly 18 attribute rows")
def t_scorecard_md_rows():
    rows = [l for l in read("templates/partner-readiness-scorecard.md").splitlines()
            if l.startswith("| **")]
    assert len(rows) == 18, f"expected 18 attribute rows, found {len(rows)}"

@check("Scorecard attribute names match the framework reference (same 18, same order)")
def t_attribute_parity():
    md = [m.group(1).strip() for m in
          (re.match(r"\|\s*\*\*(.+?)\*\*\s*\|", l) for l in read("templates/partner-readiness-scorecard.md").splitlines())
          if m]
    # framework ref table under the "Readiness Scorecard Attributes" heading
    ref_section = read("refs/og-tech-strategy-framework.md").split("## Readiness Scorecard Attributes", 1)[1]
    ref = []
    for l in ref_section.splitlines():
        if not l.strip().startswith("|"): continue
        first = l.split("|")[1].strip()
        if first in ("Attribute", "") or set(first) <= set("-: "): continue
        ref.append(first)
    assert len(md) == 18, f"scorecard md has {len(md)} names"
    assert len(ref) == 18, f"framework ref has {len(ref)} names"
    diff = [f"{i+1}: md='{a}' ref='{b}'" for i,(a,b) in enumerate(zip(md, ref)) if a != b]
    assert not diff, f"name mismatches: {diff}"

@check("Scorecard HTML row names match the Markdown (same 18, same order)")
def t_scorecard_html_names():
    md = [m.group(1).strip() for m in
          (re.match(r"\|\s*\*\*(.+?)\*\*\s*\|", l) for l in read("templates/partner-readiness-scorecard.md").splitlines())
          if m]
    html = [h.replace("&amp;", "&").strip() for h in
            re.findall(r'<td class="attr-name">(.*?)</td>', read("templates/partner-readiness-scorecard.html"))]
    assert len(html) == 18, f"scorecard html has {len(html)} attr-name cells"
    diff = [f"{i+1}: html='{a}' md='{b}'" for i,(a,b) in enumerate(zip(html, md)) if a != b]
    assert not diff, f"name mismatches: {diff}"

# ---- 4. rename invariant (OG Tech Strategy, no 'inspire') ----------------
@check("No 'inspire' references anywhere except LICENSE")
def t_no_inspire():
    hits = []
    for root, _, files in os.walk(SKILL):
        if "/.git" in root or os.sep + "tests" in root: continue  # tests/ names the term on purpose
        for f in files:
            if f == "LICENSE" or f.startswith("."): continue
            p = os.path.join(root, f)
            try: txt = open(p, encoding="utf-8", errors="ignore").read()
            except Exception: continue
            if "inspire" in txt.lower():
                hits.append(os.path.relpath(p, SKILL))
    assert not hits, f"'inspire' found in: {sorted(hits)}"

# ---- 5. opportunity-stage vocabulary ------------------------------------
CANON_STAGES = ["00-Prospect","01-Qualify","02-Assess","03-Contract",
                "04-Build","05-In Market","06-First Report","08-Dead"]

@check("Framework reference defines all canonical Org62 Opportunity stages")
def t_canonical_stages():
    ref = read("refs/og-tech-strategy-framework.md")
    missing = [s for s in CANON_STAGES if s not in ref]
    assert not missing, f"missing stage labels: {missing}"

@check("No legacy numeric stage pickers or retired tokens remain")
def t_no_legacy_stage_tokens():
    bad = []
    for t in ("templates/pov-output.md", "templates/mvp-build-plan.md"):
        if "[1 / 2 / 3" in read(t): bad.append(f"{t}: legacy '[1 / 2 / 3]' picker")
    for t in TEMPLATE_HTML:
        s = read(t)
        for tok in ("FRAMEWORK_STAGE", "STAGE_3_TARGET"):
            if tok in s: bad.append(f"{t}: retired token {tok}")
    assert not bad, f"{bad}"

@check("POV template + presentation carry the Product Strategy section/slides")
def t_pov_product_strategy():
    pov = read("templates/pov-output.md")
    deck = read("templates/pov-presentation.html")
    assert "## Product Strategy" in pov, "pov-output.md missing ## Product Strategy section"
    assert "Strategic Thesis" in pov, "pov-output.md missing Strategic Thesis"
    assert "{{STRATEGIC_THESIS}}" in deck, "pov-presentation.html missing {{STRATEGIC_THESIS}} slide token"
    assert "{{PILLAR_1_NAME}}" in deck, "pov-presentation.html missing pillar slide token"

# ---- 6. stage numbering + menu consistency ------------------------------
@check("Stages are contiguous 1..19 across the instructions (no gaps or duplicates)")
def t_stage_contiguous():
    nums = sorted(int(n) for n in re.findall(r"^\*\*Stage (\d+) —", instructions(), re.M))
    assert nums == list(range(1, 20)), f"stage sequence is {nums}"

@check("Every '(Stage N)' cited in the output menu maps to a real stage")
def t_menu_stage_refs():
    corpus = instructions()
    stages = set(int(n) for n in re.findall(r"^\*\*Stage (\d+)", corpus, re.M))
    cited = set(int(n) for n in re.findall(r"\(Stage (\d+)\)", corpus))
    missing = sorted(cited - stages)
    assert not missing, f"menu cites non-existent stages: {missing}"

@check("SKILL.md states the Stage 14 gate (Architecture Summary must be populated)")
def t_stage14_gate_in_skill():
    # parallel-dispatch.md defers to SKILL.md as the canonical source of this gate
    # ("same gate SKILL.md applies"); the sequential path reads only SKILL.md, so
    # the gate must live here too or an empty Marketecture can be generated.
    skill = read("SKILL.md")
    assert re.search(r"Stage 14[^\n]*Architecture Summary", skill) or \
           re.search(r"Architecture Summary[^\n]*Stage 14", skill), \
        "SKILL.md does not state the Stage 14 gate tying Marketecture to a populated Architecture Summary"

@check("Output menu includes the 'All outputs + home page' option")
def t_menu_all_option():
    assert "All outputs + home page" in read("SKILL.md")

@check("Output menu offers the Discovery Framework and cites Stage 15")
def t_menu_discovery_option():
    skill = read("SKILL.md")
    assert "Discovery Framework" in skill, "menu missing 'Discovery Framework' option"
    assert "(Stage 15)" in skill, "menu does not cite (Stage 15)"

@check("Output menu offers the Technical & Architectural Assessment and cites Stage 16")
def t_menu_architecture_option():
    skill = read("SKILL.md")
    assert "Technical & Architectural Assessment" in skill, "menu missing the Assessment option"
    assert "(Stage 16)" in skill, "menu does not cite (Stage 16)"

@check("The 'Optional outputs' section header range matches the downstream stage map (8..max)")
def t_optional_outputs_header_range():
    # The '**Stages N–M — Optional outputs' header introduces the router table; its
    # range must span the optional downstream stages. A new optional stage (17, 18, …)
    # that lands without bumping M leaves a stale header the other checks can't see.
    skill = read("SKILL.md")
    m = re.search(r"\*\*Stages\s+(\d+)\s*[–-]\s*(\d+)\s*—\s*Optional outputs", skill)
    assert m, "SKILL.md missing the '**Stages N–M — Optional outputs' section header"
    lo, hi = int(m.group(1)), int(m.group(2))
    want_lo, want_hi = min(DOWNSTREAM_STAGES), max(DOWNSTREAM_STAGES)
    assert (lo, hi) == (want_lo, want_hi), \
        f"Optional-outputs header says Stages {lo}–{hi}, but the stage map spans {want_lo}–{want_hi}"

@check("Each output-menu question text agrees with its header chip (no stale wording)")
def t_menu_question_header_agreement():
    # The user sees both the question text and the header chip; if a menu is renamed
    # (e.g. 'Architecture & Build' → 'Architecture & Growth') and only one is updated,
    # they disagree. Assert every substantive word in a header appears in its question.
    skill = read("SKILL.md")
    pairs = re.findall(r'^\s*question:\s*"([^"]+)",\s*\n\s*header:\s*"([^"]+)"', skill, re.M)
    assert pairs, "no question/header pairs found in the output menu"
    bad = {}
    for q, h in pairs:
        ql = q.lower()
        missing = [w for w in re.findall(r"[A-Za-z]{4,}", h) if w.lower() not in ql]
        if missing:
            bad[h] = missing
    assert not bad, f"menu header words absent from their question text (stale wording): {bad}"

# ---- 7. home page + document shell required tokens ----------------------
@check("document-shell.html and output-index.html carry their required tokens")
def t_package_tokens():
    shell = read("templates/document-shell.html")
    for tok in ("{{CONTENT}}", "{{DOC_LABEL}}", "{{PARTNER_NAME}}", "{{HOME_HREF}}"):
        assert tok in shell, f"document-shell missing {tok}"
    idx = read("templates/output-index.html")
    for tok in ("{{ARTIFACT_CARDS}}", "{{ARTIFACT_COUNT}}", "{{PARTNER_NAME}}"):
        assert tok in idx, f"output-index missing {tok}"

# ---- 8. SKILL.md frontmatter --------------------------------------------
@check("SKILL.md has name + description frontmatter")
def t_frontmatter():
    head = read("SKILL.md")[:600]
    assert head.startswith("---"), "no YAML frontmatter block"
    assert re.search(r"^name:\s*\S", head, re.M), "missing name:"
    assert re.search(r"^description:\s*\S", head, re.M), "missing description:"

# ---- 9. Slack insights -------------------------------------------------
SLACK_REF = "refs/slack-insights.md"

@check("Slack insights ref file exists")
def t_slack_ref_exists():
    assert exists(SLACK_REF), f"{SLACK_REF} is missing"

@check("Slack ref defines the seven extraction buckets")
def t_slack_buckets():
    txt = read(SLACK_REF).lower()
    buckets = ["exec sponsor", "pilot", "commercial model",
               "stakeholder needs", "blocker", "proof point", "timeline"]
    missing = [b for b in buckets if b not in txt]
    assert not missing, f"buckets missing from slack ref: {missing}"

@check("Slack ref defines the Slack-specific confidence + sentiment labels")
def t_slack_labels():
    txt = read(SLACK_REF)
    assert "[from internal Slack — confirm]" in txt, "missing fact confidence tier label"
    assert "[internal Slack sentiment — not partner-confirmed]" in txt, "missing sentiment label"

@check("Slack ref defines capability check, fallback, and MCP-only discovery")
def t_slack_capability():
    txt = read(SLACK_REF).lower()
    assert "capability check" in txt, "missing capability check"
    assert "fallback" in txt, "missing fallback path"
    assert "via **export**" in read(SLACK_REF) or "via export" in txt, "missing paste/export fallback"
    assert "mcp-only" in txt or "mcp only" in txt, "discovery must be flagged MCP-only"

@check("Slack ref defines the confirm-before-read gate and 3-6 Medium+High shortlist")
def t_slack_gate():
    txt = read(SLACK_REF).lower()
    assert "confirm-before-read" in txt or "confirm before read" in txt, "missing consent gate"
    raw = read(SLACK_REF)
    assert "**High** —" in raw and "**Medium** —" in raw, "missing High/Medium tier definitions"
    assert "top 6" in txt or "3-6" in txt or "3–6" in txt, "missing 3-6 shortlist cap"

@check("Slack ref reads config from the dedicated config file with a 90-day default window")
def t_slack_config():
    txt = read(SLACK_REF)
    assert "tech-strat-pov-forge-slack.json" in txt, "must read config from ~/.claude/tech-strat-pov-forge-slack.json"
    assert "read_window_days" in txt, "missing read_window_days key"
    assert "Default 90" in txt or "default **90**" in txt or "= 90" in txt, "missing 90-day default wording"

@check("SKILL.md carries the three thin Slack hooks and references the ref")
def t_slack_hooks_in_skill():
    skill = read("SKILL.md")
    assert "refs/slack-insights.md" in skill, "SKILL.md must reference the Slack ref"
    assert "[from internal Slack — confirm]" in skill, "Stage 2 hook label missing"
    low = skill.lower()
    assert "slack" in low and "reconcile" in low, "Stage 3 reconciliation hook missing"
    assert "5–8" in skill or "5-8" in skill or "~5" in skill, "relaxed 5-8 question target missing"

@check("Scorecard carries the Slack fast-follow note (documentation only)")
def t_slack_scorecard_note():
    txt = read("refs/stages/stage-12-partner-readiness-scorecard.md").lower()
    assert "slack" in txt and "fast-follow" in txt, "missing Slack fast-follow note"
    assert "not wired in v1" in txt or "not v1" in txt, "fast-follow must state it is not v1"

@check("README documents the Slack capability, config file, and the consent gate")
def t_slack_readme():
    txt = read("README.md")
    low = txt.lower()
    assert "slack" in low, "README missing Slack section"
    assert "tech-strat-pov-forge-slack.json" in txt, "README must document the dedicated config file"
    assert "read_window_days" in txt, "README must show the slack config schema"
    assert "confirm" in low and "read" in low, "README must state the confirm-before-read gate"
    assert "export" in low, "README must document the paste/export fallback"

@check("Org62 pre-fill module exists, is referenced, and is read-only")
def t_org62_prefill():
    path = "refs/org62-prefill.md"
    assert exists(path), f"missing {path}"
    body = read(path)
    forbidden = ["sf project deploy", "sf data create", "sf data update",
                 "sf data delete", "sf data upsert", "DELETE FROM", "UPDATE "]
    hits = [tok for tok in forbidden if tok in body]
    assert not hits, f"module must be read-only, found: {hits}"
    assert "Optionality contract" in body, "module missing Optionality contract section"
    assert path in read("SKILL.md"), f"{path} not referenced by SKILL.md"

@check("Org62 module copy in pie-poc-forge is in sync (skipped if sibling absent)")
def t_org62_module_parity():
    sibling = os.path.join(SKILL, "..", "pie-poc-forge", "refs", "org62-prefill.md")
    if not os.path.exists(sibling):
        return  # sibling skill not installed here — nothing to compare (n-a)
    here = open(os.path.join(SKILL, "refs/org62-prefill.md"), encoding="utf-8").read()
    there = open(sibling, encoding="utf-8").read()
    assert here == there, "refs/org62-prefill.md differs between tech-strat-pov-forge and pie-poc-forge — re-sync the copies"

# ---- 10. script behavior (deterministic converters) --------------------
# The two scripts in scripts/ are pure, deterministic code with defined behavior.
# Earlier checks only assert they EXIST and are REFERENCED; these run them.
def _load_script(rel, name):
    import importlib.util
    sys.dont_write_bytecode = True   # don't litter scripts/__pycache__ during tests
    spec = importlib.util.spec_from_file_location(name, os.path.join(SKILL, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

@check("md-to-html renders the golden fixture exactly (behavioral)")
def t_md_to_html_golden():
    m = _load_script("scripts/md-to-html.py", "md_to_html_mod")
    md = read("tests/fixtures/md-to-html/sample.md")
    md = re.sub(r'^#\s+.*\n', '', md, count=1)          # the leading-H1 drop main() does
    got = m.md_to_html(md)
    want = read("tests/fixtures/md-to-html/expected-body.html").rstrip("\n")
    assert got == want, ("md_to_html output drifted from golden fixture.\n"
                         "Regenerate intentionally if the change is correct.\n"
                         f"--- got ---\n{got}\n--- want ---\n{want}")

@check("md-to-html escapes HTML and drops the leading H1 (behavioral)")
def t_md_to_html_escaping():
    m = _load_script("scripts/md-to-html.py", "md_to_html_mod2")
    body = m.md_to_html(re.sub(r'^#\s+.*\n', '', "# Drop Me\n\nText with <b> & risk.\n", count=1))
    assert "Drop Me" not in body, "leading H1 should be dropped before md_to_html"
    assert "&lt;b&gt;" in body and "&amp;" in body, "raw HTML must be escaped"
    assert "<b>" not in body, "unescaped tag leaked into output"

@check("ensure-home-link injects, repairs, and is idempotent (behavioral)")
def t_ensure_home_link_behavior():
    import tempfile, shutil
    e = _load_script("scripts/ensure-home-link.py", "ensure_home_mod")
    d = tempfile.mkdtemp()
    try:
        from pathlib import Path
        home = "acme-index.html"
        # 1) artifact WITHOUT a pill → inject after <body>
        p1 = Path(d, "acme-pov.html"); p1.write_text("<html><body>\n<h1>x</h1></body></html>")
        assert e.process(p1, home) == "injected", "should inject a missing pill"
        assert e.MARKER in p1.read_text(), "pill marker absent after inject"
        # 2) running again → idempotent ('ok', no change)
        before = p1.read_text()
        assert e.process(p1, home) == "ok", "second run should be a no-op"
        assert p1.read_text() == before, "idempotent run changed the file"
        # 3) artifact with a WRONG href → repaired to the index
        p2 = Path(d, "acme-red-team.html")
        p2.write_text('<html><body>\n<a href="{{HOME_HREF}}" >&#8592; All artifacts</a></body></html>')
        assert e.process(p2, home) == "repaired", "should repair a wrong/leftover href"
        assert f'href="{home}"' in p2.read_text(), "href not repaired to the index"
        # 4) no <body> → reported error, not a crash
        p3 = Path(d, "acme-broken.html"); p3.write_text("<html>no body here</html>")
        assert e.process(p3, home).startswith("error:"), "missing <body> should report an error"
    finally:
        shutil.rmtree(d, ignore_errors=True)

# ---- runner -------------------------------------------------------------
def main():
    width = max(len(n) for n, _ in RESULTS)
    passed = 0
    print(f"\ntech-strat-pov-forge skill validation — {len(RESULTS)} checks\n" + "=" * (width + 12))
    for name, fn in RESULTS:
        try:
            fn(); print(f"PASS  {name.ljust(width)}"); passed += 1
        except AssertionError as e:
            print(f"FAIL  {name.ljust(width)}  → {e}")
        except Exception as e:
            print(f"ERROR {name.ljust(width)}  → {type(e).__name__}: {e}")
    print("=" * (width + 12))
    print(f"{passed}/{len(RESULTS)} passed\n")
    sys.exit(0 if passed == len(RESULTS) else 1)

if __name__ == "__main__":
    main()
