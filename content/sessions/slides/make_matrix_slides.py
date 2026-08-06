#!/usr/bin/env python3
"""Standalone 2-slide deck: the Transformation Matrix 'invisible -> present' pair.
Reuses the brand style from make_decks.py."""
import make_decks as m

deck = m.new_deck()

m.add_slide(deck, "gold", "I see myself. I am present.",
            eyebrow="The shift  ·  presencing",
            body="I stop waiting to be seen. I turn toward myself, and I make myself visible. It is my destiny to be visible.")

m.add_slide(deck, "navy", "I take my place",
            eyebrow="The power statement",
            body="I see myself. I am present to my own feelings, needs and desires. It is my destiny to be visible, and I take my rightful place.")

deck.save("content/sessions/slides/Matrix-Slides-Invisible-to-Present.pptx")
print("saved Matrix-Slides-Invisible-to-Present.pptx", len(deck.slides._sldIdLst), "slides")
