#!/usr/bin/env python3
"""Validation suite for partner-blocker-forge — generated via skill-forge. Stdlib only."""
import os, re, sys, importlib.util
sys.dont_write_bytecode = True  # don't cache scripts/ loads (mutation tests must see live source)

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load(rel):
    """Load a script from scripts/ as a module (behavioral-test helper, R-TEST-04)."""
    p = os.path.join(SKILL, rel)
    spec = importlib.util.spec_from_file_location(os.path.basename(rel)[:-3], p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod
RESULTS = []
def check(name):
    def deco(fn): RESULTS.append((name, fn)); return fn
    return deco
def read(rel):
    with open(os.path.join(SKILL, rel), encoding="utf-8") as f: return f.read()
def exists(rel):
    return os.path.exists(os.path.join(SKILL, rel))

# ---- injected check-library snippets (verbatim) ----

def chk_frontmatter():
    head = read("SKILL.md")[:600]
    assert head.startswith("---"), "no YAML frontmatter block"
    assert re.search(r"^name:\s*\S", head, re.M), "missing name:"
    assert re.search(r"^description:\s*\S", head, re.M), "missing description:"

def chk_refusal_present():
    txt = read("SKILL.md")
    low = txt.lower()
    assert any(k in low for k in ("refus", "do not", "don't", "stop and", "when not")), \
        "SKILL.md states no refusal/scope conditions"
    lines = txt.splitlines()
    cue = next((i for i, l in enumerate(lines)
                if any(k in l.lower() for k in ("refus", "stop and", "when not", "do not", "don't"))), None)
    body = []
    if cue is not None:
        for l in lines[cue + 1:]:
            if l.lstrip().startswith("#"): break
            if l.strip(): body.append(l.strip())
    cue_is_heading = cue is not None and lines[cue].lstrip().startswith("#")
    assert body or (cue is not None and not cue_is_heading), \
        "refusal section has a heading/cue but no stated conditions beneath it"

def chk_refs_dir():
    assert os.path.isdir(os.path.join(SKILL, "refs")), "no refs/ directory"

def chk_refs_exist():
    parts = [read("SKILL.md")]
    for dp, _, files in os.walk(os.path.join(SKILL, "refs")):
        parts += [read(os.path.relpath(os.path.join(dp, f), SKILL)) for f in files if f.endswith(".md")]
    corpus = "\n".join(parts)
    paths = set(re.findall(r"(?:templates|refs|validation|scripts)/[A-Za-z0-9._*/-]+", corpus))
    def concrete(p):
        return "*" not in p and "NN" not in p and "{" not in p and "<" not in p
    missing = [p.rstrip(".") for p in paths if concrete(p) and not exists(p.rstrip("."))]
    assert not missing, f"referenced but missing: {sorted(missing)}"

def chk_no_orphans():
    parts = [read("SKILL.md")]
    for dp, _, files in os.walk(os.path.join(SKILL, "refs")):
        parts += [read(os.path.relpath(os.path.join(dp, f), SKILL)) for f in files if f.endswith(".md")]
    corpus = "\n".join(parts)
    refs = re.findall(r"(?:refs|templates|validation|scripts)/[A-Za-z0-9._*/<>{}-]+", corpus)
    patterns = []
    for r in refs:
        if not any(tok in r for tok in ("*", "<", "{", "NN")): continue
        rx = re.sub(r"<[^>]*>|\{[^}]*\}|NN|\*", "\x00", r)
        patterns.append(re.compile(re.escape(rx).replace("\x00", "[^/]*") + r"$"))
    orphans = []
    for d in ("refs", "templates", "validation"):
        dpath = os.path.join(SKILL, d)
        if not os.path.isdir(dpath): continue
        for root, _, files in os.walk(dpath):
            for f in files:
                if f.startswith(".") or not os.path.isfile(os.path.join(root, f)): continue
                rel = os.path.relpath(os.path.join(root, f), SKILL)
                if rel in corpus: continue
                if any(p.search(rel) for p in patterns): continue
                orphans.append(rel)
    assert not orphans, f"present but never referenced: {sorted(orphans)}"

def chk_test_suite_exists():
    assert exists("tests/validate_skill.py"), "no tests/validate_skill.py"

def chk_token_hygiene():
    bad = {}
    tdir = os.path.join(SKILL, "templates")
    if not os.path.isdir(tdir): return
    for f in os.listdir(tdir):
        if not f.endswith((".html", ".tmpl")): continue
        s = read(f"templates/{f}")
        if s.count("{{") != s.count("}}"):
            bad[f] = "unbalanced braces"; continue
        off = [t for t in re.findall(r"\{\{([^{}]*)\}\}", s) if not re.fullmatch(r"[A-Z0-9_]+", t)]
        if off: bad[f] = off
    assert not bad, f"token defects: {bad}"

def chk_router_parity():
    sdir = os.path.join(SKILL, "refs/stages")
    if not os.path.isdir(sdir): return
    skill = read("SKILL.md")
    on_disk = {f"refs/stages/{f}" for f in os.listdir(sdir) if f.endswith(".md")}
    referenced = set(re.findall(r"refs/stages/[A-Za-z0-9._-]+\.md", skill))
    not_routed = sorted(on_disk - referenced)
    dangling = sorted(referenced - on_disk)
    assert not not_routed, f"stage files not referenced by SKILL.md: {not_routed}"
    assert not dangling, f"SKILL.md references missing stage files: {dangling}"

def chk_behavioral_tests():
    sdir = os.path.join(SKILL, "scripts")
    scripts = []
    if os.path.isdir(sdir):
        scripts = [f for f in os.listdir(sdir) if f.endswith(".py") and not f.startswith("__")]
    if not scripts:
        return  # n-a — no deterministic code to exercise
    assert exists("tests/validate_skill.py"), \
        "ships scripts/ but has no tests/validate_skill.py to exercise them"
    suite = read("tests/validate_skill.py")
    loads_script = ("spec_from_file_location" in suite
                    or re.search(r"exec\(\s*[^)]*read\([^)]*scripts/", suite, re.S))
    assert loads_script, "suite references no behavioral exercise of scripts/ (R-TEST-04)"
    fxdir = os.path.join(SKILL, "tests/fixtures")
    has_fixture = os.path.isdir(fxdir) and any(
        os.path.isfile(os.path.join(r, f))
        for r, _, fs in os.walk(fxdir) for f in fs)
    assert has_fixture, "behavioral tests need golden fixtures under tests/fixtures/ (none found)"

def chk_precommit_hook():
    assert exists(".githooks/pre-commit"), "no tracked .githooks/pre-commit"
    assert "validate_skill.py" in read(".githooks/pre-commit"), "hook does not run the suite"

def chk_ci_workflow():
    wdir = os.path.join(SKILL, ".github/workflows")
    assert os.path.isdir(wdir), "no .github/workflows/"
    ymls = [f for f in os.listdir(wdir) if f.endswith((".yml", ".yaml"))]
    assert ymls, "no CI workflow file"
    assert any("validate_skill.py" in read(f".github/workflows/{f}") for f in ymls), \
        "no workflow runs validate_skill.py"

def chk_spec_plan_archive():
    for d in ("docs/superpowers/specs", "docs/superpowers/plans"):
        p = os.path.join(SKILL, d)
        assert os.path.isdir(p) and any(f.endswith(".md") for f in os.listdir(p)), \
            f"no archived docs under {d}/"

def chk_readme():
    assert exists("README.md"), "no README.md"
    assert len(read("README.md").split()) >= 30, "README.md too thin to document the skill"

def chk_behavioral_scrub():
    # R-TEST-04 behavioral: load scripts/scrub_check.py and exercise its detector against
    # golden fixtures — dirty must flag leaks, clean must pass. Not a presence check.
    assert exists("scripts/scrub_check.py"), "no scripts/scrub_check.py to exercise"
    mod = _load("scripts/scrub_check.py")
    dirty = mod.scan_text(read("tests/fixtures/dirty-draft.md"))
    clean = mod.scan_text(read("tests/fixtures/clean-draft.md"))
    labels = {lbl for _, lbl, _ in dirty}
    for expected in ("sfid-org", "sfid-case", "internal-gus", "phone"):
        assert expected in labels, f"scrub_check missed '{expected}' in dirty fixture (got {sorted(labels)})"
    assert clean == [], f"scrub_check false-positived on clean fixture: {clean}"

# ---- registry ----
check("R-FM-01: frontmatter")(lambda: chk_frontmatter())
check("R-REF-01: refusal conditions present")(lambda: chk_refusal_present())
check("R-ARCH-01: refs/ dir")(lambda: chk_refs_dir())
check("R-ARCH-02: referenced paths exist")(lambda: chk_refs_exist())
check("R-ARCH-03: no orphan files")(lambda: chk_no_orphans())
check("R-TEST-01: test suite exists")(lambda: chk_test_suite_exists())
check("R-TEST-02: template token hygiene")(lambda: chk_token_hygiene())
check("R-TEST-03: router parity")(lambda: chk_router_parity())
check("R-TEST-04: behavioral tests apparatus")(lambda: chk_behavioral_tests())
check("R-TEST-04b: scrub_check behavioral (golden fixtures)")(lambda: chk_behavioral_scrub())
check("R-CI-01: pre-commit hook")(lambda: chk_precommit_hook())
check("R-CI-02: CI workflow")(lambda: chk_ci_workflow())
check("R-DOC-01: README")(lambda: chk_readme())
check("R-PROC-01: spec+plan archive")(lambda: chk_spec_plan_archive())

def main():
    width = max(len(n) for n, _ in RESULTS)
    passed = 0
    print(f"\npartner-blocker-forge validation — {len(RESULTS)} checks\n" + "=" * (width + 12))
    for name, fn in RESULTS:
        try:
            fn(); print(f"PASS  {name.ljust(width)}"); passed += 1
        except AssertionError as e:
            print(f"FAIL  {name.ljust(width)}  → {e}")
        except Exception as e:
            print(f"ERROR {name.ljust(width)}  → {type(e).__name__}: {e}")
    print("=" * (width + 12)); print(f"{passed}/{len(RESULTS)} passed\n")
    sys.exit(0 if passed == len(RESULTS) else 1)

if __name__ == "__main__":
    main()
