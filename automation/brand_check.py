"""Deterministic brand-voice linter for outgoing copy.

Catches the mechanical rules from content/style_guide.md — the ones that
don't need judgement and shouldn't need a human. Em-dashes, curly quotes,
American spellings, banned phrases.

The judgement calls (voice, therapist-speak, coaching cliches) belong to
the /brand-check skill, which reads the same style guide. This script is
the half that can run in CI.

Deliberately NOT checked: content/testimonials.json. Those are real women's
own words. Contracting "you are" or removing a dash from a quote would be
falsifying it. Testimonials get copied exactly as given, always.

Usage:
    python brand_check.py                    # check all default content files
    python brand_check.py path/to/file.json  # check specific files
    python brand_check.py --text "some copy" # check a string

Exit code 1 if any violation is found, so it can gate a workflow.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Files whose copy goes out in Tarisha's voice. Keys are the JSON fields
# that contain prose; everything else in the file is ignored.
DEFAULT_TARGETS = {
    "content/posts.json": ["hook", "caption", "question"],
    "content/journal_prompts.json": ["prompt", "caption"],
    "content/infographics.json": ["title", "caption"],
    "content/practices.json": ["title", "caption"],
    "content/reels.json": ["hook", "caption"],
    "content/drafts/image_post_drafts.json": ["hook", "caption", "question"],
    "content/drafts/journal_prompt_drafts.json": ["prompt", "caption"],
    "content/drafts/infographic_drafts.json": ["title", "caption"],
}

# American → British/NZ. Word-boundary matched, case-insensitive.
US_TO_NZ = {
    "realize": "realise",
    "realized": "realised",
    "realizing": "realising",
    "color": "colour",
    "colors": "colours",
    "favorite": "favourite",
    "apologize": "apologise",
    "apologized": "apologised",
    "honor": "honour",
    "honored": "honoured",
    "recognize": "recognise",
    "recognized": "recognised",
    "organize": "organise",
    "organized": "organised",
    "prioritize": "prioritise",
    "prioritized": "prioritised",
    "behavior": "behaviour",
    "neighbor": "neighbour",
    "center": "centre",
    "centered": "centred",
    "labeled": "labelled",
    "traveled": "travelled",
    "fulfill": "fulfil",
    "defense": "defence",
}

# Phrases the style guide explicitly rules out.
BANNED_PHRASES = [
    "darling",  # use "beautiful" instead — hard rule
    "gently",   # softening adverbs weaken the line, cut them
    "quietly",
    "queen energy",
    "boss babe",
    "self-care",
    "i see you",
    "i feel you, sister",
    "research shows",
    "studies suggest",
    "studies show",
    "furthermore",
    "moreover",
    "however,",
    "in conclusion",
    "it is important to note",
]

# Uncontracted forms the guide says to always contract.
UNCONTRACTED = {
    "cannot": "can't",
    "do not": "don't",
    "does not": "doesn't",
    "did not": "didn't",
    "will not": "won't",
    "is not": "isn't",
    "are not": "aren't",
    "was not": "wasn't",
    "has not": "hasn't",
    "have not": "haven't",
    "would not": "wouldn't",
    "should not": "shouldn't",
    "could not": "couldn't",
    "it is ": "it's ",
    "you are ": "you're ",
    "they are ": "they're ",
}

CURLY = {
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
}


class Violation:
    def __init__(self, source: str, field: str, rule: str, found: str, fix: str):
        self.source = source
        self.field = field
        self.rule = rule
        self.found = found
        self.fix = fix

    def __str__(self) -> str:
        where = f"{self.source}" + (f" [{self.field}]" if self.field else "")
        return f"  {where}\n    {self.rule}: {self.found!r} → {self.fix!r}"


def check_text(text: str, source: str = "", field: str = "") -> list[Violation]:
    """Run every mechanical rule over one string."""
    out: list[Violation] = []
    if not isinstance(text, str) or not text.strip():
        return out

    lowered = text.lower()

    for dash in ("—", "–"):
        if dash in text:
            idx = text.index(dash)
            snippet = text[max(0, idx - 30): idx + 30]
            out.append(Violation(
                source, field, "em/en-dash banned",
                snippet.strip(), "use a comma, full stop or ellipsis",
            ))

    for curly, straight in CURLY.items():
        if curly in text:
            out.append(Violation(
                source, field, "curly quote", curly, straight,
            ))

    for us, nz in US_TO_NZ.items():
        if re.search(rf"\b{us}\b", lowered):
            out.append(Violation(source, field, "US spelling", us, nz))

    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            out.append(Violation(
                source, field, "banned phrase", phrase, "cut it or rewrite",
            ))

    for long_form, short in UNCONTRACTED.items():
        if re.search(rf"\b{re.escape(long_form.strip())}\b", lowered):
            out.append(Violation(
                source, field, "not contracted", long_form.strip(), short.strip(),
            ))

    return out


def walk_json(obj, fields: list[str], source: str, path: str = "") -> list[Violation]:
    """Recursively pull the prose fields out of a JSON structure."""
    out: list[Violation] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            here = f"{path}.{key}" if path else key
            if key in fields and isinstance(value, str):
                out.extend(check_text(value, source, here))
            else:
                out.extend(walk_json(value, fields, source, here))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            out.extend(walk_json(item, fields, source, f"{path}[{i}]"))
    return out


def check_file(rel_path: str, fields: list[str]) -> list[Violation]:
    full = os.path.join(REPO_ROOT, rel_path)
    if not os.path.exists(full):
        return []
    with open(full, encoding="utf-8") as fh:
        if rel_path.endswith(".json"):
            try:
                data = json.load(fh)
            except json.JSONDecodeError as exc:
                return [Violation(rel_path, "", "invalid JSON", str(exc), "fix the syntax")]
            return walk_json(data, fields, rel_path)
        return check_text(fh.read(), rel_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Brand voice linter")
    parser.add_argument("files", nargs="*", help="specific files to check")
    parser.add_argument("--text", help="check a raw string instead of files")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="report violations but always exit 0 (for CI while the existing backlog is cleared)",
    )
    args = parser.parse_args()

    violations: list[Violation] = []

    if args.text:
        violations = check_text(args.text, "--text")
    elif args.files:
        for path in args.files:
            rel = os.path.relpath(os.path.abspath(path), REPO_ROOT)
            fields = DEFAULT_TARGETS.get(rel, ["hook", "caption", "question", "prompt", "text", "title"])
            violations.extend(check_file(rel, fields))
    else:
        for rel, fields in DEFAULT_TARGETS.items():
            violations.extend(check_file(rel, fields))

    if not violations:
        print("Brand check passed. Nothing to fix.")
        return 0

    print(f"Brand check found {len(violations)} violation(s):\n")
    for v in violations:
        print(v)
    print("\nRules live in content/style_guide.md")

    if args.warn_only:
        print("(--warn-only: not failing the build)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
