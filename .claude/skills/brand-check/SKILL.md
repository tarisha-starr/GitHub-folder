---
name: brand-check
description: Check draft copy against Tarisha's approved voice, terminology and claims before it goes out. Use whenever a caption, hook, email, sales page, newsletter or post is about to be published, or when the user says "check this", "does this sound like me", "brand check", "is this on voice", or pastes draft copy for review. Also use before any bulk content generation is committed.
---

# Brand Consistency Checker

Automation #20. Catches voice drift before customers see it, instead of
after, which is what's been happening manually.

## Two layers, run both

### Layer 1: the mechanical rules (deterministic)

Run the linter first. It's faster and never wrong about these:

```bash
python3 automation/brand_check.py                     # all content files
python3 automation/brand_check.py --text "the copy"   # a single string
python3 automation/brand_check.py content/posts.json  # one file
```

It catches em-dashes, curly quotes, American spellings, uncontracted forms
and banned phrases. Exit code 1 means violations exist.

Don't re-check these by eye. If the linter passed, they're clean.

### Layer 2: the judgement rules (your job)

Read `content/style_guide.md` in full, then assess the draft on things a
regex can't see:

**Voice tests, in priority order:**

1. **Does it sound spoken?** Her voice is spoken word, not written prose.
   Run-ons, fragments and trailing thoughts are correct. Polished,
   balanced, essay-like sentences are wrong.
2. **Is there a first-person anchor?** "I see this every day in my work,"
   "I had a client say..." Copy that floats free of her actual practice
   reads generic.
3. **Is the body personified as "she"?** Not required everywhere, but it's
   a signature move and its absence across a whole batch is a flag.
4. **Is it therapist-speak?** "Research shows", "studies suggest",
   clinical distance. Cut it.
5. **Is it coaching cliche?** "Queen energy", "boss babe", "step into your
   power", "self-care". Instant fail.
6. **Is it performative empathy?** "I see you", "I feel you, sister".
   Instant fail.
7. **Are paragraphs short?** Long blocks are wrong for her.

**Structure check.** Captions should follow:

```
[I-statement opening from her work]
[Reframe / emotional truth, 1-3 short sentences]
[Optional: another short paragraph or rhetorical question]

[Direct question or CTA]
```

**Claims check.** She works with women's sexuality, intimacy and midlife
bodies. Flag anything that:
- promises a specific outcome ("this will fix your marriage")
- makes a medical or clinical claim
- implies therapy or diagnosis rather than coaching
- guarantees results from a program

This matters more than voice. Voice is a brand problem; a false claim is
a real one.

## What NOT to check

**Never apply voice rules to testimonials.** `content/testimonials.json`
holds real women's own words. If a testimonial says "you are worthy" with
an em-dash, it stays exactly as she wrote it. Contracting or restyling a
customer quote is falsifying it. The linter deliberately skips that file.
Do the same.

Same goes for anything quoted from a podcast guest, a client email or a
review.

## Output

Report only what's actually wrong. For each issue:

```
[rule broken] — [the exact text] → [the fix in her voice]
```

Then give the corrected draft in full so it can be pasted straight back.

If it passes both layers, say so in one line. Don't invent problems to
look thorough, and don't soften a real claims issue to be agreeable.
