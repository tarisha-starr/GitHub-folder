"""Build the exact text to publish, in one place, for every push script.

All five zapier_push_* scripts POST to the same Catch Hook (they all read
ZAPIER_WEBHOOK_URL), so a single Zap receives image posts, testimonials,
book posts, infographics and journal prompts. That means the Zap's text
mapping has to work for all five, which is why this lives in one module
rather than being reimplemented per script.

Map `post_text` in Zapier and nothing else. If the Zap assembles the body
itself from hook + caption + hashtags, two things go wrong:

  - the hook prints in the body as well as on the card image
  - each content type needs its own branch, and they drift

The hook is deliberately never included. It's rendered onto the card by
render_post_cards.py.
"""

from __future__ import annotations


def build_post_text(
    caption: str = "",
    question: str = "",
    hashtags: list[str] | str | None = None,
) -> str:
    """Caption, then question, then hashtags, separated by blank lines.

    Skips anything empty, and skips the question when the caption already
    ends with it, which happens when a content type reuses one field for
    both (the infographic payload does exactly that).
    """
    parts: list[str] = []

    caption = (caption or "").strip()
    if caption:
        parts.append(caption)

    question = (question or "").strip()
    if question and question.lower() not in caption.lower():
        parts.append(question)

    if hashtags:
        tags = hashtags if isinstance(hashtags, str) else " ".join(hashtags)
        tags = tags.strip()
        # Testimonial captions already append their own hashtags.
        if tags and tags.lower() not in caption.lower():
            parts.append(tags)

    return "\n\n".join(parts)
