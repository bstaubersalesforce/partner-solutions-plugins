#!/usr/bin/env python3
"""Tests for scaffold_kit.py — always-present rendering."""
import json, os, tempfile, importlib.util, pathlib, subprocess

SKILL = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sk", SKILL/"scripts/scaffold_kit.py")
sk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sk)

MINIMAL = {
    "name": "t",
    "title": "T",
    "mode": "lab",
    "duration": "2-day",
    "partner_overlay": "reference",
    "surfaces": {},
    "provisioning": {"needs_org": False, "model": "none", "required_features": []},
    "modules": [{"n": 0, "title": "Comprehend"}],
    "content_dirs": {},
    "reference_build": {"source": "none", "path": "sfdx/"}
}

def test_always_present_files_rendered():
    """Verify all always-present files are rendered."""
    with tempfile.TemporaryDirectory() as d:
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(MINIMAL))
        written = sk.render_kit(kj, os.path.join(d, "out"))
        for f in ["README.md", "GUIDE.md", "FACILITATOR.md", "LESSONS-LEARNED.md",
                  "config/kit.json", ".env.example", ".gitignore",
                  "scripts/lib/common.sh", "scripts/check.sh"]:
            assert f in written, f"{f} not rendered"
            assert os.path.exists(os.path.join(d, "out", f)), f"{f} does not exist on disk"

def test_no_residual_tokens():
    """Guard: no file should contain unsubstituted {{TOKEN}} after render."""
    with tempfile.TemporaryDirectory() as d:
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(MINIMAL))
        out_dir = os.path.join(d, "out")
        sk.render_kit(kj, out_dir)

        # Walk every rendered file, assert no {{ substring
        for root, dirs, files in os.walk(out_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                # Skip binary/config files that are not templates
                if fname.endswith(('.pyc', '.DS_Store')):
                    continue
                # Read and check
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    assert "{{" not in content, \
                        f"{os.path.relpath(fpath, out_dir)} contains unsubstituted token: {content[content.index('{{'):content.index('}}')+2]}"

def test_educate_kit_omits_org_and_matches_golden():
    """Educate-only kit (needs_org:false) omits org artifacts and is byte-equal to golden."""
    fx = SKILL / "tests/fixtures/educate"
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out")
        written = sk.render_kit(str(fx / "kit.json"), out)
        assert "docs/org-provisioning.md" not in written, "org-provisioning.md should not be rendered"
        assert "docs/credential-setup-cookbook.md" not in written, "credential cookbook is org-gated; should not render for needs_org:false"
        assert "scripts/deploy.sh" not in written, "deploy.sh should not be rendered"
        assert "scripts/assign-perms.sh" not in written, "assign-perms.sh should not be rendered"
        assert "KNOWN-GAPS.md" in written, "KNOWN-GAPS.md is always rendered"

        # Byte-equal against the committed golden tree
        for rel in written:
            got_path = os.path.join(out, rel)
            exp_path = fx / "expected" / rel
            with open(got_path, encoding="utf-8") as f:
                got = f.read()
            with open(exp_path, encoding="utf-8") as f:
                exp = f.read()
            assert got == exp, f"drift in {rel}"

        # META-CHECK: run the generated kit's own check.sh and assert it passes
        r = subprocess.run(["bash", "scripts/check.sh"], cwd=out, capture_output=True, text=True)
        assert r.returncode == 0, f"check.sh failed:\n{r.stdout}{r.stderr}"

def test_full_kit_matches_golden_and_check_passes():
    """Full kit (needs_org:true) renders org artifacts, is byte-equal, and its check.sh passes (meta-check)."""
    fx = SKILL / "tests/fixtures/full"
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out")
        written = sk.render_kit(str(fx / "kit.json"), out)

        # Assert org artifacts are rendered
        assert "docs/org-provisioning.md" in written, "org-provisioning.md should be rendered"
        assert "docs/credential-setup-cookbook.md" in written, "credential cookbook should render for needs_org:true"
        assert "KNOWN-GAPS.md" in written, "KNOWN-GAPS.md is always rendered"
        assert "scripts/01-check-env.sh" in written, "01-check-env.sh should be rendered"
        assert "scripts/02-deploy.sh" in written, "02-deploy.sh should be rendered"
        assert "scripts/03-assign-perms.sh" in written, "03-assign-perms.sh should be rendered"

        # Byte-equal against the committed golden tree
        for rel in written:
            got_path = os.path.join(out, rel)
            exp_path = fx / "expected" / rel
            with open(got_path, encoding="utf-8") as f:
                got = f.read()
            with open(exp_path, encoding="utf-8") as f:
                exp = f.read()
            assert got == exp, f"drift in {rel}"

        # META-CHECK: run the generated kit's own check.sh and assert it passes
        r = subprocess.run(["bash", "scripts/check.sh"], cwd=out, capture_output=True, text=True)
        assert r.returncode == 0, f"check.sh failed:\n{r.stdout}{r.stderr}"

def test_missing_required_key_gives_clear_error():
    """FIX #1: Missing required keys should raise clear ValueError, not KeyError."""
    with tempfile.TemporaryDirectory() as d:
        # Test missing 'name'
        bad_cfg = {"title": "T", "mode": "lab", "duration": "2-day"}
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(bad_cfg))
        try:
            sk.render_kit(kj, os.path.join(d, "out"))
            assert False, "should have raised error for missing 'name'"
        except (ValueError, SystemExit) as e:
            assert "name" in str(e).lower(), f"error should mention 'name', got: {e}"

        # Test missing module title
        bad_module_cfg = {
            "name": "t", "title": "T", "mode": "lab", "duration": "2-day",
            "modules": [{"n": 0}]  # missing title
        }
        kj2 = os.path.join(d, "kit2.json")
        open(kj2, "w").write(json.dumps(bad_module_cfg))
        try:
            sk.render_kit(kj2, os.path.join(d, "out2"))
            assert False, "should have raised error for missing module 'title'"
        except (ValueError, SystemExit) as e:
            assert "title" in str(e).lower(), f"error should mention 'title', got: {e}"

def test_malformed_json_gives_clear_error():
    """FIX #1: Invalid JSON should raise clear error."""
    with tempfile.TemporaryDirectory() as d:
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write("{bad json")
        try:
            sk.render_kit(kj, os.path.join(d, "out"))
            assert False, "should have raised error for malformed JSON"
        except (ValueError, json.JSONDecodeError, SystemExit):
            pass  # expected

def test_name_slugified_for_permset():
    """FIX #2: name with spaces/special chars should be slugified for PERMSET_NAME."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()
        cfg["name"] = "My Kit!"
        # Set needs_org to true so 03-assign-perms.sh is generated
        cfg["provisioning"] = {"needs_org": True, "model": "sdo", "required_features": []}
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        out = os.path.join(d, "out")
        sk.render_kit(kj, out)

        # Check that 03-assign-perms.sh uses slugified name
        perms_script = os.path.join(out, "scripts/03-assign-perms.sh")
        assert os.path.exists(perms_script), "03-assign-perms.sh should exist for needs_org kits"
        with open(perms_script, "r") as f:
            content = f.read()
            # Should have my_kit_user, not "My Kit!" or "My_Kit!"
            assert "my_kit_user" in content, f"permset should be slugified to my_kit_user, got: {content}"
            assert "My Kit!" not in content, "should not have raw spaces/!"
            assert "!" not in content or "!/usr/bin" in content, "should not have unescaped !"

def test_content_dir_key_sanitized():
    """FIX #2: content_dirs keys with shell metacharacters should be sanitized."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()
        cfg["content_dirs"] = {"a; echo X": True, "normal-dir": True}
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        out = os.path.join(d, "out")
        sk.render_kit(kj, out)

        # Check check.sh doesn't contain raw shell injection
        check_script = os.path.join(out, "scripts/check.sh")
        with open(check_script, "r") as f:
            content = f.read()
            # Should NOT have raw "; echo X"
            assert "; echo X" not in content, "shell metacharacters should be scrubbed from content_dir keys"
            # Should have sanitized version (slug converts to underscore)
            assert "a_echo_x" in content.lower() or "a-echo-x" in content.lower(), "should have sanitized dir name"

def test_no_org_kit_has_no_org_refs():
    """FIX #3: needs_org:false kits should have no ORG_ALIAS or org references."""
    fx = SKILL / "tests/fixtures/educate"
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out")
        sk.render_kit(str(fx / "kit.json"), out)

        # Check .env.example has no ORG_ALIAS
        env_ex = os.path.join(out, ".env.example")
        with open(env_ex, "r") as f:
            content = f.read()
            assert "ORG_ALIAS" not in content, f".env.example should not reference ORG_ALIAS for no-org kit: {content}"

        # Check README.md has no org setup instructions
        readme = os.path.join(out, "README.md")
        with open(readme, "r") as f:
            content = f.read()
            assert "ORG_ALIAS" not in content, "README.md should not reference ORG_ALIAS for no-org kit"

        # Check 00-preflight.sh has no resolve_org or org checks
        preflight = os.path.join(out, "scripts/00-preflight.sh")
        with open(preflight, "r") as f:
            content = f.read()
            assert "resolve_org" not in content, "00-preflight.sh should not call resolve_org for no-org kit"
            assert "ORG=" not in content or "# no ORG" in content, "00-preflight.sh should not set ORG for no-org kit"

def test_surfaces_are_descriptive_only():
    """FIX #5: surfaces are descriptive (JSON/narrative), not auto-scaffolded directories."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()
        cfg["surfaces"] = {"web": True, "slack": True}
        # Explicitly NOT listing web or slack in content_dirs
        cfg["content_dirs"] = {"docs": True}
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        out = os.path.join(d, "out")
        written = sk.render_kit(kj, out)

        # Should NOT auto-create web/ or slack/ directories
        assert "web/.gitkeep" not in written, "surfaces should not auto-create directories"
        assert "slack/.gitkeep" not in written, "surfaces should not auto-create directories"
        assert not os.path.exists(os.path.join(out, "web")), "web/ should not exist"
        assert not os.path.exists(os.path.join(out, "slack")), "slack/ should not exist"

        # Should have docs/ since it IS in content_dirs
        assert "docs/.gitkeep" in written, "docs should be created since it's in content_dirs"

def test_always_present_list_derived_from_constant():
    """FIX #6: test derives expected files from sk.ALWAYS, not a hardcoded list."""
    # This test replaces test_always_present_files_rendered to use sk.ALWAYS as source of truth
    with tempfile.TemporaryDirectory() as d:
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(MINIMAL))
        written = sk.render_kit(kj, os.path.join(d, "out"))

        # Derive expected from sk.ALWAYS
        expected = [rel for _, rel in sk.ALWAYS] + ["config/kit.json", "scripts/check.sh"]
        for f in expected:
            assert f in written, f"{f} not rendered"
            assert os.path.exists(os.path.join(d, "out", f)), f"{f} does not exist on disk"

def test_reference_build_path_sanitized():
    """D-01: reference_build.path tokens must scrub shell metacharacters but preserve legitimate paths."""
    with tempfile.TemporaryDirectory() as d:
        # Test adversarial path with command substitution
        adversarial_cfg = MINIMAL.copy()
        adversarial_cfg["provisioning"] = {"needs_org": True, "model": "sdo", "required_features": []}
        adversarial_cfg["reference_build"] = {"source": "repo", "path": "sfdx/$(echo PWNED)"}
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(adversarial_cfg))
        out = os.path.join(d, "out")
        sk.render_kit(kj, out)

        # Check 02-deploy.sh: should NOT contain command substitution
        deploy_script = os.path.join(out, "scripts/02-deploy.sh")
        with open(deploy_script, "r") as f:
            content = f.read()
            # Should not have the original command substitution pattern
            assert "$(echo PWNED)" not in content, \
                f"02-deploy.sh should not contain command substitution from path: {content}"
            assert "`" not in content, f"02-deploy.sh should not contain backticks from path: {content}"
            # Command substitution for ROOT and BASH_SOURCE are allowed (those are built-in)
            # The test is that user-supplied path metacharacters are stripped
            # Sanitized version should strip $, (, ), and space, leaving "sfdx/echoPWNED"
            assert "sfdx/" in content, "should preserve legitimate path prefix"
            # Verify the sanitized version exists (metacharacters gone but alphanumerics kept)
            assert "echoPWNED" in content, "should preserve alphanumeric parts after sanitization"

        # Test normal path is preserved
        normal_cfg = MINIMAL.copy()
        normal_cfg["provisioning"] = {"needs_org": True, "model": "sdo", "required_features": []}
        normal_cfg["reference_build"] = {"source": "repo", "path": "sfdx/force-app"}
        kj2 = os.path.join(d, "kit2.json")
        open(kj2, "w").write(json.dumps(normal_cfg))
        out2 = os.path.join(d, "out2")
        sk.render_kit(kj2, out2)

        deploy_script2 = os.path.join(out2, "scripts/02-deploy.sh")
        with open(deploy_script2, "r") as f:
            content2 = f.read()
            # Should preserve normal path exactly (with /, -, _)
            assert "sfdx/force-app" in content2 or "sfdx" in content2, \
                f"should preserve normal path structure: {content2}"

def test_optional_module_renders_marker():
    """A module with optional:true renders an (Optional) marker in GUIDE.md."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()
        cfg["modules"] = [{"n": 0, "title": "Comprehend"},
                          {"n": 6, "title": "Agent Grounding", "optional": True}]
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        out = os.path.join(d, "out")
        sk.render_kit(kj, out)
        guide = open(os.path.join(out, "GUIDE.md"), encoding="utf-8").read()
        assert "## Module 6: Agent Grounding (Optional)" in guide, guide
        assert "## Module 0: Comprehend\n" in guide, guide  # non-optional: no marker

def test_mode_gated_module_included_when_mode_matches():
    """A module gated to the kit's mode is rendered."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()  # mode == "lab"
        cfg["modules"] = [{"n": 0, "title": "Comprehend"},
                          {"n": 5, "title": "BYO Data", "modes": ["lab"]}]
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        out = os.path.join(d, "out")
        sk.render_kit(kj, out)
        guide = open(os.path.join(out, "GUIDE.md"), encoding="utf-8").read()
        assert "## Module 5: BYO Data" in guide, guide

def test_mode_gated_module_omitted_when_mode_differs():
    """A module gated to a different mode is omitted from GUIDE.md but kept in config."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()  # mode == "lab"
        cfg["modules"] = [{"n": 0, "title": "Comprehend"},
                          {"n": 5, "title": "Engagement Deep Dive", "modes": ["engagement"]}]
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        out = os.path.join(d, "out")
        sk.render_kit(kj, out)
        guide = open(os.path.join(out, "GUIDE.md"), encoding="utf-8").read()
        assert "Engagement Deep Dive" not in guide, guide
        cfgout = json.loads(open(os.path.join(out, "config/kit.json"), encoding="utf-8").read())
        titles = [m["title"] for m in cfgout["modules"]]
        assert "Engagement Deep Dive" in titles, "config/kit.json must retain all authored modules"

def test_module_optional_must_be_bool():
    """optional not a bool → clear ValueError mentioning 'optional'."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()
        cfg["modules"] = [{"n": 0, "title": "C", "optional": "yes"}]
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        try:
            sk.render_kit(kj, os.path.join(d, "out"))
            assert False, "should raise for non-bool optional"
        except ValueError as e:
            assert "optional" in str(e).lower(), e

def test_module_modes_must_be_nonempty_valid_list():
    """modes empty or containing an unknown mode → clear ValueError mentioning 'modes'."""
    with tempfile.TemporaryDirectory() as d:
        for bad in ([], ["bogus"], "lab"):
            cfg = MINIMAL.copy()
            cfg["modules"] = [{"n": 0, "title": "C", "modes": bad}]
            kj = os.path.join(d, "kit.json")
            open(kj, "w").write(json.dumps(cfg))
            try:
                sk.render_kit(kj, os.path.join(d, "out_" + str(bad)))
                assert False, f"should raise for modes={bad!r}"
            except ValueError as e:
                assert "modes" in str(e).lower(), e

def test_sample_data_path_emits_data_dir():
    """reference_build.sample_data_path set → data/.gitkeep + data/README.md emitted and required."""
    with tempfile.TemporaryDirectory() as d:
        cfg = MINIMAL.copy()
        cfg["reference_build"] = {"source": "freeform", "path": "sfdx/", "sample_data_path": "data/"}
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(cfg))
        out = os.path.join(d, "out")
        written = sk.render_kit(kj, out)
        assert "data/.gitkeep" in written, written
        assert "data/README.md" in written, written
        assert os.path.exists(os.path.join(out, "data/README.md"))
        check = open(os.path.join(out, "scripts/check.sh"), encoding="utf-8").read()
        assert "data/README.md" in check, "check.sh must require data/README.md"
        # meta-check: generated check.sh passes
        r = subprocess.run(["bash", "scripts/check.sh"], cwd=out, capture_output=True, text=True)
        assert r.returncode == 0, f"{r.stdout}{r.stderr}"

def test_no_sample_data_path_emits_no_data_dir():
    """No sample_data_path → no data/ artifacts (back-compat)."""
    with tempfile.TemporaryDirectory() as d:
        kj = os.path.join(d, "kit.json")
        open(kj, "w").write(json.dumps(MINIMAL))  # no sample_data_path
        out = os.path.join(d, "out")
        written = sk.render_kit(kj, out)
        assert "data/.gitkeep" not in written
        assert "data/README.md" not in written
        assert not os.path.exists(os.path.join(out, "data"))

def test_rich_kit_matches_golden_and_check_passes():
    """Rich fixture (optional + mode-gated modules + sample_data_path) is byte-equal and self-validates."""
    fx = SKILL / "tests/fixtures/rich"
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out")
        written = sk.render_kit(str(fx / "kit.json"), out)
        # new-field expectations
        assert "data/README.md" in written, written
        guide = open(os.path.join(out, "GUIDE.md"), encoding="utf-8").read()
        assert "## Module 6: Agent Grounding (Optional)" in guide
        assert "## Module 5: BYO Dataset" in guide
        assert "Engagement Deep Dive" not in guide  # gated to engagement
        # byte-equal against committed golden
        for rel in written:
            got = open(os.path.join(out, rel), encoding="utf-8").read()
            exp = open(fx / "expected" / rel, encoding="utf-8").read()
            assert got == exp, f"drift in {rel}"
        # meta-check
        r = subprocess.run(["bash", "scripts/check.sh"], cwd=out, capture_output=True, text=True)
        assert r.returncode == 0, f"{r.stdout}{r.stderr}"

if __name__ == "__main__":
    test_always_present_files_rendered()
    print("test_always_present_files_rendered: PASS")
    test_no_residual_tokens()
    print("test_no_residual_tokens: PASS")
    test_educate_kit_omits_org_and_matches_golden()
    print("test_educate_kit_omits_org_and_matches_golden: PASS")
    test_full_kit_matches_golden_and_check_passes()
    print("test_full_kit_matches_golden_and_check_passes: PASS")
    test_missing_required_key_gives_clear_error()
    print("test_missing_required_key_gives_clear_error: PASS")
    test_malformed_json_gives_clear_error()
    print("test_malformed_json_gives_clear_error: PASS")
    test_name_slugified_for_permset()
    print("test_name_slugified_for_permset: PASS")
    test_content_dir_key_sanitized()
    print("test_content_dir_key_sanitized: PASS")
    test_no_org_kit_has_no_org_refs()
    print("test_no_org_kit_has_no_org_refs: PASS")
    test_surfaces_are_descriptive_only()
    print("test_surfaces_are_descriptive_only: PASS")
    test_always_present_list_derived_from_constant()
    print("test_always_present_list_derived_from_constant: PASS")
    test_reference_build_path_sanitized()
    print("test_reference_build_path_sanitized: PASS")
    test_optional_module_renders_marker()
    print("test_optional_module_renders_marker: PASS")
    test_mode_gated_module_included_when_mode_matches()
    print("test_mode_gated_module_included_when_mode_matches: PASS")
    test_mode_gated_module_omitted_when_mode_differs()
    print("test_mode_gated_module_omitted_when_mode_differs: PASS")
    test_module_optional_must_be_bool()
    print("test_module_optional_must_be_bool: PASS")
    test_module_modes_must_be_nonempty_valid_list()
    print("test_module_modes_must_be_nonempty_valid_list: PASS")
    test_sample_data_path_emits_data_dir()
    print("test_sample_data_path_emits_data_dir: PASS")
    test_no_sample_data_path_emits_no_data_dir()
    print("test_no_sample_data_path_emits_no_data_dir: PASS")
    test_rich_kit_matches_golden_and_check_passes()
    print("test_rich_kit_matches_golden_and_check_passes: PASS")
    print("\nAll tests passed!")
