#!/usr/bin/env python3
"""
Template renderer for ps-npi-forge. Stdlib-only, side-effect-free.

Fills {{UPPER_SNAKE}} tokens in a Phase-3a artifact template from a `fills` dict and reports any
token left unfilled. This module is the authoritative fill-set for a template: the validation suite
asserts that a complete fill leaves no surviving {{TOKEN}}.
"""
import re
import os

TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

def render(template_text, fills):
    unfilled = []
    def repl(m):
        key = m.group(1)
        if key in fills:
            return str(fills[key])
        if key not in unfilled:
            unfilled.append(key)
        return m.group(0)  # leave the token literal so the gap is visible + scannable
    out = TOKEN_RE.sub(repl, template_text)
    return out, unfilled

def wants_html(artifact_md, template_md):
    """
    Returns True if the artifact should have an HTML view per the format rule:
    an artifact renders to HTML if and only if it is EITHER:
    - a narrative artifact (template VOICE comment contains "narrative"), OR
    - a reference artifact that carries a mermaid diagram (artifact markdown has a ```mermaid fence).

    Falls back to has-mermaid-only if the VOICE comment is absent.
    """
    # Detect "narrative" ONLY in the VOICE marker comment, not anywhere in the template body.
    # The VOICE marker is an HTML comment on line 1, e.g.:
    #   <!-- VOICE: narrative — first-person exec/architect ... -->
    #   <!-- VOICE: reference — factual/precise ... -->
    is_narrative = False
    if "VOICE:" in template_md:
        # Extract the first HTML comment that contains "VOICE:"
        voice_match = re.search(r"<!--(.*?)-->", template_md, re.DOTALL)
        if voice_match and "VOICE:" in voice_match.group(1):
            voice_comment = voice_match.group(1)
            is_narrative = "narrative" in voice_comment.lower()

    has_mermaid = "```mermaid" in artifact_md
    return is_narrative or has_mermaid

def orphan_html(canvas_dir, keep_slugs):
    """
    Pure inspection helper: returns a list of absolute paths of <slug>.html files in canvas_dir
    that are NOT in keep_slugs. These are orphans to remove.

    Considers only files matching the artifact-slug pattern NN-name.html (two digits, hyphen, name).
    Does NOT return the merged poster (14-exec-infographic-poster.html), index.html, or slide decks
    (*-slides.html) as orphans — those are legitimate non-<slug>.html outputs.

    This function does NOT delete anything; it returns the list for the caller to remove.
    """
    if not os.path.isdir(canvas_dir):
        return []

    orphans = []
    slug_pattern = re.compile(r"^\d{2}-[a-z0-9-]+\.html$")

    for f in os.listdir(canvas_dir):
        # Skip special files: index.html, poster suffix, and slides suffix.
        # LOAD-BEARING: the regex matches "14-exec-infographic-poster.html" and "02-slide-summary-slides.html"
        # since it only tests the NN-name.html pattern. These explicit exclusions prevent false-positives.
        if f == "index.html" or f.endswith("-poster.html") or f.endswith("-slides.html"):
            continue

        if not slug_pattern.match(f):
            # Not a plain artifact <slug>.html
            continue

        slug = f[:-5]  # strip .html
        if slug not in keep_slugs:
            orphans.append(os.path.join(canvas_dir, f))

    return orphans
