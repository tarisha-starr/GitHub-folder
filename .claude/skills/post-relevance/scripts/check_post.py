#!/usr/bin/env python3
"""Check a finished caption or set of pinned comments against the voice rules.

    python3 check_post.py draft.txt
    pbpaste | python3 check_post.py -

Takes plain text, not HTML, because this runs on the output of the relevance
workflow rather than on a built page. Use check_voice.py in the website-build
skill for pages.

Exits non-zero if anything fails, so it can gate a handoff. Failures are the
hard rules from content/style_guide.md plus the AI tells the workflow's
humanising pass is supposed to have removed. Flags are judgement calls that
Tarisha decides, so they never fail the run.
"""
import re
import sys

# Hard rules from the style guide. These are never acceptable in her copy.
BANNED = [
    (r"\bqueen energy\b", "coachy cliche"),
    (r"\bboss bab(?:e|es)\b", "coachy cliche"),
    (r"\bI see you\b", "performative empathy"),
    (r"\bI feel you,? (?:sister|sis)\b", "performative empathy"),
    (r"\bcome as you are\b", "banned phrase"),
    (r"\bresearch shows\b", "therapist-speak"),
    (r"\bstudies (?:show|suggest)\b", "therapist-speak"),
    (r"\bfurthermore\b", "stiff transition"),
    (r"\bmoreover\b", "stiff transition"),
    (r"^\s*However,", "stiff transition, start the sentence another way"),
]

# The tells from the humanising pass. If these survive, that pass did not run.
AI_TELLS = [
    (r"\bgame[- ]chang(?:er|ing)\b", "empty hype"),
    (r"\brevolutionary\b", "empty hype"),
    (r"\bdive into\b", "AI phrasing"),
    (r"\bdelve into\b", "AI phrasing"),
    (r"\bin today's fast[- ]paced world\b", "AI opener"),
    (r"\bunleash\b", "empty hype"),
    (r"\bsupercharge\b", "empty hype"),
    (r"\belevate your\b", "empty hype"),
    (r"\ba testament to\b", "AI phrasing"),
    (r"\bnavigat(?:e|ing) the (?:landscape|complexities|journey)\b", "AI phrasing"),
    (r"\bit'?s not (?:just )?\w+[\w\s]{0,20},? it'?s\b", "the it's-not-X-it's-Y pattern"),
]

# Generic engagement questions the save-and-share pass forbids.
GENERIC_QUESTIONS = [
    r"\bwhat do you think\?",
    r"\bdo you agree\?",
    r"\bwhich one is your favourite\?",
    r"\bwhich is your favourite\?",
    r"\bthoughts\?",
]

US_SPELLINGS = [
    "realize", "realized", "realizing", "realization", "color", "colors",
    "colored", "favorite", "favorites", "apologize", "behavior", "behaviors",
    "organize", "organized", "organizing", "recognize", "recognized",
    "prioritize", "prioritized", "humanized", "analyze", "analyzed",
    "center", "centers", "theater", "traveling", "canceled", "honor",
    "practicing", "fulfillment", "labeled", "marvelous",
]

# Contractions she always uses. Uncontracted forms read stiff in her voice.
UNCONTRACTED = [
    (r"\bcannot\b", "can't"),
    (r"\bdo not\b", "don't"),
    (r"\bdoes not\b", "doesn't"),
    (r"\bwill not\b", "won't"),
    (r"\bis not\b", "isn't"),
    (r"\bare not\b", "aren't"),
    (r"\bhas not\b", "hasn't"),
    (r"\bhave not\b", "haven't"),
    (r"\bit is\b", "it's"),
    (r"\bthat is\b", "that's"),
    (r"\byou are\b", "you're"),
]

# Her approved captions in the style guide run 25 to 35 words a paragraph, so
# anything past 45 has stopped sounding like her.
MAX_PARAGRAPH_WORDS = 45


def context(text, start, width=40):
    return text[max(0, start - width):start + width].strip().replace("\n", " ")


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: check_post.py <draft.txt|->")

    path = sys.argv[1]
    if path == "-":
        text = sys.stdin.read()
    else:
        text = open(path, encoding="utf-8").read()

    fails, flags = [], []

    for m in re.finditer(r"[—–]", text):
        fails.append("dash used as punctuation: ...%s..." % context(text, m.start()))

    for pattern, why in BANNED:
        for m in re.finditer(pattern, text, re.I | re.M):
            fails.append("%r (%s): ...%s..." % (m.group(0), why, context(text, m.start())))

    for pattern, why in AI_TELLS:
        for m in re.finditer(pattern, text, re.I):
            fails.append("%r (%s): ...%s..." % (m.group(0), why, context(text, m.start())))

    for pattern in GENERIC_QUESTIONS:
        for m in re.finditer(pattern, text, re.I):
            fails.append("generic engagement question %r, the save-and-share pass "
                         "forbids these" % m.group(0))

    for word in US_SPELLINGS:
        for m in re.finditer(r"\b%s\b" % word, text, re.I):
            fails.append("US spelling %r: ...%s..." % (m.group(0), context(text, m.start())))

    for pattern, better in UNCONTRACTED:
        for m in re.finditer(pattern, text, re.I):
            flags.append("%r reads stiff, prefer %r: ...%s..."
                         % (m.group(0), better, context(text, m.start())))

    # "unlock" is banned as a verb and kept as a product name, so it is a
    # judgement call rather than a failure.
    for m in re.finditer(r"\bunlock(?:s|ing|ed)?\b", text, re.I):
        after = text[m.end():m.end() + 24].lower()
        if "your desire" in after or "desire" in after:
            continue
        flags.append("%r, keep it only if it names an actual offer: ...%s..."
                     % (m.group(0), context(text, m.start())))

    for m in re.finditer(r"\breal\b", text, re.I):
        flags.append("'real' is discouraged as filler, keep it only if it carries "
                     "the sentence: ...%s..." % context(text, m.start()))

    for para in [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]:
        words = len(para.split())
        if words > MAX_PARAGRAPH_WORDS:
            flags.append("paragraph of %d words, she writes short ones: %s..."
                         % (words, para[:60].replace("\n", " ")))

    if not re.search(r"\?\s*$|comment\b|say with me|reach out|are you ready",
                     text.strip(), re.I | re.M):
        flags.append("no question or comment CTA found, the post needs somewhere "
                     "for the reader to go")

    for line in fails:
        print("FAIL  %s" % line)
    for line in flags:
        print("FLAG  %s" % line)

    print("\n%d failure%s, %d flag%s"
          % (len(fails), "" if len(fails) == 1 else "s",
             len(flags), "" if len(flags) == 1 else "s"))

    if fails:
        print("Fix the failures before publishing. Flags are yours to judge.")
        return 1
    print("Hard rules pass. Read the flags, then publish.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
