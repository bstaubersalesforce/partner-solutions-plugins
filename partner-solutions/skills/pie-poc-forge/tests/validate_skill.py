#!/usr/bin/env python3
"""
Validation suite for the pie-poc-forge skill. Stdlib-only.

Asserts the structural invariants that must hold for the skill to run correctly
and to satisfy the skill-forge Tier-3 rubric. It validates files, references,
tokens, and router parity — it does NOT judge LLM output quality.

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

# ---- canvas-artifact registry (single source of truth) ------------------
ALWAYS = ["01-execution-plan", "02-mvp-pov-opinion", "03-pre-instance-config",
          "04-package-analysis", "05-post-config-steps", "06-security-review",
          "07-gaps-document", "08-component-manifest", "10-dev-environment",
          "11-kickoff-deck", "12-engagement-review-deck"]
CONDITIONAL = ["09-agentscript", "13-finalize-report"]
ALL_ARTIFACTS = ALWAYS + CONDITIONAL

# SKILL.md is the only instruction file for this skill (no refs/stages router).
INSTRUCTION_FILES = ["SKILL.md"]
def instructions():
    return "\n".join(read(f) for f in INSTRUCTION_FILES if exists(f))

TOKEN_RE = re.compile(r"\{\{([^{}]*)\}\}")

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

# ---- R-ARCH-01: refs/ directory exists and holds the domain logic -------
EXPECTED_REFS = [
    "refs/requirements-schema.md", "refs/packaging-analysis.md",
    "refs/security-review.md", "refs/gaps-document.md",
    "refs/sfdx-scaffold.md", "refs/agentscript-handoff.md",
    "refs/mvp-opinion.md", "refs/workflow-dispatch.md",
    "refs/dev-environment.md", "refs/engagement-decks.md",
    "refs/mcp-integration.md", "refs/finalize.md",
]

@check("R-ARCH-01: refs/ exists and SKILL.md stays lean (domain logic externalized)")
def t_refs_dir():
    assert os.path.isdir(os.path.join(SKILL, "refs")), "refs/ directory missing"
    assert len(read("SKILL.md")) < 20000, \
        "SKILL.md too large — domain logic belongs in refs/"

# ---- R-ARCH-02: every referenced path exists ----------------------------
@check("R-ARCH-02: every file path referenced in the instructions exists")
def t_refs_exist():
    skill = instructions()
    paths = set(re.findall(r"(?:templates|refs|validation|scripts)/[A-Za-z0-9._/-]+", skill))
    missing = [p.rstrip(".") for p in paths if not exists(p.rstrip("."))]
    assert not missing, f"referenced but missing: {sorted(missing)}"

# ---- R-ARCH-03: no orphans under refs/ templates/ scripts/ --------------
@check("R-ARCH-03: every file under refs/ templates/ scripts/ is referenced (no orphans)")
def t_no_orphans():
    skill = instructions()
    # Canvas .md source templates are referenced collectively via the `templates/NN-*.md`
    # render glob and the `01 … 09` range shorthand in SKILL.md, not by 12 literal paths —
    # so the registry blesses them. (No .html stubs exist: rendering WRITES docs/NN-*.html
    # from the .md + document-shell.html — see refs/workflow-dispatch.md.)
    registry_slugs = {f"{a}.md" for a in ALL_ARTIFACTS}
    orphans = []
    for d in ("refs", "templates", "scripts"):
        dpath = os.path.join(SKILL, d)
        if not os.path.isdir(dpath): continue
        for f in os.listdir(dpath):
            if f.startswith(".") or f == "__pycache__": continue
            if not os.path.isfile(os.path.join(dpath, f)): continue
            rel = f"{d}/{f}"
            if rel in skill: continue
            if d == "templates" and f in registry_slugs: continue
            orphans.append(rel)
    assert not orphans, f"present but never referenced: {sorted(orphans)}"

@check("All expected refs/ files exist")
def t_expected_refs_exist():
    missing = [r for r in EXPECTED_REFS if not exists(r)]
    assert not missing, f"expected refs missing: {missing}"

# ---- R-TEST-02: token hygiene -------------------------------------------
@check("R-TEST-02: every {{TOKEN}} in templates is UPPER_SNAKE_CASE with balanced braces")
def t_token_hygiene():
    tdir = os.path.join(SKILL, "templates")
    if not os.path.isdir(tdir):
        raise AssertionError("templates/ directory missing")
    bad = []
    for f in os.listdir(tdir):
        if not (f.endswith(".html") or f.endswith(".md")): continue
        text = read(f"templates/{f}")
        for tok in TOKEN_RE.findall(text):
            if not re.fullmatch(r"[A-Z0-9_]+", tok):
                bad.append(f"templates/{f}: {{{{{tok}}}}}")
    assert not bad, f"malformed tokens: {bad}"

# ---- R-TEST-03: canvas router parity ------------------------------------
# Parity is between the artifact REGISTRY, the SOURCE templates, and the INDEX:
#   - every artifact has a `.md` source template (rendering reads NN-*.md +
#     document-shell.html and WRITES docs/NN-*.html — there is no per-artifact
#     .html template, by design);
#   - every ALWAYS artifact's rendered output slug (NN-*.html) is linked from the
#     index card grid, and the index links no slug outside the registry.
@check("R-TEST-03: artifact registry, .md source templates, and output-index are in bidirectional sync")
def t_router_parity():
    assert exists("templates/output-index.html"), "templates/output-index.html missing"
    index = read("templates/output-index.html")
    # 1) every artifact has a .md source template
    missing_md = [f"templates/{a}.md" for a in ALL_ARTIFACTS if not exists(f"templates/{a}.md")]
    assert not missing_md, f"artifact .md source templates missing: {missing_md}"
    # 2) every ALWAYS artifact's rendered slug is linked from the index
    not_in_index = [a for a in ALWAYS if f"{a}.html" not in index]
    assert not not_in_index, f"ALWAYS artifacts not linked from output-index.html: {not_in_index}"
    # 3) the index links no rendered slug that isn't a known artifact (no orphan cards)
    linked = set(re.findall(r'href="([0-9]{2}-[a-z-]+)\.html"', index))
    unknown = sorted(linked - set(ALL_ARTIFACTS))
    assert not unknown, f"output-index links unknown artifact slugs: {unknown}"

@check("Shared shell + index templates exist")
def t_shell_index_exist():
    for rel in ("templates/document-shell.html", "templates/output-index.html"):
        assert exists(rel), f"{rel} missing"

@check("Render scripts present")
def t_scripts_exist():
    for rel in ("scripts/md-to-html.py", "scripts/ensure-home-link.py"):
        assert exists(rel), f"{rel} missing"

# ---- R-CI-01 / R-CI-02 --------------------------------------------------
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

# ---- R-PROC-01 ----------------------------------------------------------
@check("R-PROC-01: spec->plan archive exists under docs/superpowers/")
def t_spec_plan_archive():
    specs = os.path.join(SKILL, "docs/superpowers/specs")
    plans = os.path.join(SKILL, "docs/superpowers/plans")
    assert os.path.isdir(specs) and any(f.endswith(".md") for f in os.listdir(specs)), \
        "no spec under docs/superpowers/specs/"
    assert os.path.isdir(plans) and any(f.endswith(".md") for f in os.listdir(plans)), \
        "no plan under docs/superpowers/plans/"

# ---- R-SCRIPT-01..03: deterministic-converter behavior ------------------
# scripts/md-to-html.py and scripts/ensure-home-link.py are pure, deterministic
# code with defined behavior. The checks above only assert they EXIST and are
# REFERENCED; these RUN them. Ported from pov-builder's shipped R1 (the scripts
# were copied from there without their tests — backlog B2).
def _load_script(rel, name):
    import importlib.util
    sys.dont_write_bytecode = True   # don't litter scripts/__pycache__ during tests
    spec = importlib.util.spec_from_file_location(name, os.path.join(SKILL, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

@check("R-SCRIPT-01: md-to-html renders the golden fixture exactly (behavioral)")
def t_md_to_html_golden():
    m = _load_script("scripts/md-to-html.py", "md_to_html_mod")
    md = read("tests/fixtures/md-to-html/sample.md")
    md = re.sub(r'^#\s+.*\n', '', md, count=1)          # the leading-H1 drop main() does
    got = m.md_to_html(md)
    want = read("tests/fixtures/md-to-html/expected-body.html").rstrip("\n")
    assert got == want, ("md_to_html output drifted from the golden fixture.\n"
                         "If the change is intentional, regenerate "
                         "tests/fixtures/md-to-html/expected-body.html.\n"
                         f"--- got ---\n{got}\n--- want ---\n{want}")

@check("R-SCRIPT-02: md-to-html escapes HTML and drops the leading H1 (behavioral)")
def t_md_to_html_escaping():
    m = _load_script("scripts/md-to-html.py", "md_to_html_mod2")
    body = m.md_to_html(re.sub(r'^#\s+.*\n', '', "# Drop Me\n\nText with <b> & risk.\n", count=1))
    assert "Drop Me" not in body, "leading H1 should be dropped before md_to_html"
    assert "&lt;b&gt;" in body and "&amp;" in body, "raw HTML must be escaped"
    assert "<b>" not in body, "unescaped tag leaked into output"

@check("R-SCRIPT-04: md-to-html renders fenced code blocks (mermaid verbatim, other langs escaped)")
def t_md_to_html_fenced_code():
    m = _load_script("scripts/md-to-html.py", "md_to_html_mod3")
    # a ```mermaid fence renders live: <pre class="mermaid"> with source kept verbatim
    mer = m.md_to_html("```mermaid\nflowchart TD\n  A --> B{X}\n```")
    assert '<pre class="mermaid">' in mer, "mermaid fence must render as <pre class=\"mermaid\">"
    assert "flowchart TD" in mer and "A --> B{X}" in mer, "mermaid source must be kept verbatim (not escaped/mangled)"
    assert "```" not in mer, "the fence backticks must be consumed, not leaked as literal text"
    assert "<br>" not in mer, "mermaid body must not be paragraph-wrapped with <br> (the old mangling bug)"
    # any other language is an escaped <pre><code> source block
    apex = m.md_to_html("```apex\npublic class Foo { // <b> & x }\n```")
    assert "<pre><code>" in apex, "non-mermaid fence must render as <pre><code>"
    assert "&lt;b&gt;" in apex and "&amp;" in apex, "non-mermaid code must be HTML-escaped"
    assert "```" not in apex, "fence backticks must be consumed"

@check("R-SCRIPT-03: ensure-home-link injects, repairs, is idempotent, and reports errors (behavioral)")
def t_ensure_home_link_behavior():
    import tempfile, shutil
    from pathlib import Path
    e = _load_script("scripts/ensure-home-link.py", "ensure_home_mod")
    d = tempfile.mkdtemp()
    try:
        home = "index.html"   # pie-poc-forge flat layout: single index.html, NN-*.html artifacts
        # 1) artifact WITHOUT a pill -> inject after <body>
        p1 = Path(d, "01-execution-plan.html"); p1.write_text("<html><body>\n<h1>x</h1></body></html>")
        assert e.process(p1, home) == "injected", "should inject a missing pill"
        assert e.MARKER in p1.read_text(), "pill marker absent after inject"
        assert f'href="{home}"' in p1.read_text(), "injected pill must point at the index"
        # 2) running again -> idempotent ('ok', no change)
        before = p1.read_text()
        assert e.process(p1, home) == "ok", "second run should be a no-op"
        assert p1.read_text() == before, "idempotent run changed the file"
        # 3) artifact with a leftover/wrong href -> repaired to the index
        p2 = Path(d, "06-security-review.html")
        p2.write_text('<html><body>\n<a href="{{HOME_HREF}}" >&#8592; All artifacts</a></body></html>')
        assert e.process(p2, home) == "repaired", "should repair a wrong/leftover href"
        assert f'href="{home}"' in p2.read_text(), "href not repaired to the index"
        # 4) no <body> -> reported error, not a crash
        p3 = Path(d, "07-gaps-document.html"); p3.write_text("<html>no body here</html>")
        assert e.process(p3, home).startswith("error:"), "missing <body> should report an error"
    finally:
        shutil.rmtree(d, ignore_errors=True)

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
