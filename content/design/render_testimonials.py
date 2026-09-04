#!/usr/bin/env python3
"""Quiet Signal, proof series: ten testimonial cards, 1080x1350.

Same plate system as the statement cards, with one inversion. On these the
lower register matches the upper: the signal arrived. The accent marks the
point of contact rather than the point of loss.
"""
import json
import os
import sys

sys.path.insert(
    0, ".")
from render_cards import (  # noqa: E402
    S, W, H, MARGIN, PINE_DEEP, PINE_FOREST, TERRACOTTA, CAMEL, CREAM,
    font, mix, text_w, draw_tracked, base, corner_marks, sig_top, SENT_LEN,
)
from PIL import Image  # noqa: E402

OUT = "/home/user/GitHub-folder/images/ads/testimonials"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def furniture(d, plate, fig, ink, faint):
    corner_marks(d, faint)
    n = font("Lora-Regular.ttf", 17 * S)
    y = MARGIN + 4 * S
    draw_tracked(d, (MARGIN, y), plate, n, faint, track=5 * S)
    draw_tracked(d, (W - MARGIN, y), fig, n, faint, track=5 * S, anchor="rs")

    left = "LEARN HOW TO TALK TO HIM SO HE CAN HEAR"
    right = "WED 9 SEPT  ·  6PM NZ  ·  $27"
    yb = H - MARGIN - 2 * S
    rs, tr = 18 * S, 6 * S
    while rs > 10 * S:
        r = font("Lora-Regular.ttf", rs)
        if (text_w(d, left, r, tr) + text_w(d, right, r, tr)
                + 60 * S) <= (W - 2 * MARGIN):
            break
        rs -= S
        tr = max(3 * S, tr - S // 2)
    r = font("Lora-Regular.ttf", rs)
    draw_tracked(d, (MARGIN, yb), left, r, ink, track=tr)
    draw_tracked(d, (W - MARGIN, yb), right, r, faint, track=tr, anchor="rs")
    d.line([(MARGIN, yb - 40 * S), (W - MARGIN, yb - 40 * S)],
           fill=faint, width=S)


def received(d, y, ink, faint, accent):
    """The inversion: what was sent is what arrived."""
    y += 16 * S
    x0, x1 = MARGIN, W - MARGIN
    gap = 62 * S
    n = 24
    step = (x1 - x0) / (n - 1)
    lab = font("Lora-Regular.ttf", 15 * S)

    draw_tracked(d, (x0, y - 16 * S), "SENT", lab, faint, track=4 * S)
    d.line([(x0, y), (x1, y)], fill=ink, width=S)
    for i in range(n):
        x = x0 + i * step
        d.line([(x, y), (x, y + SENT_LEN)], fill=ink, width=S)

    y2 = y + gap
    draw_tracked(d, (x0, y2 - 16 * S), "HEARD", lab, faint, track=4 * S)
    d.line([(x0, y2), (x1, y2)], fill=ink, width=S)
    for i in range(n):
        x = x0 + i * step
        d.line([(x, y2), (x, y2 + SENT_LEN)], fill=ink, width=S)

    # the accent is spent once, on contact rather than loss
    x = x0 + 12 * step
    d.line([(x, y + 2 * S), (x, y2 + SENT_LEN)], fill=accent, width=2 * S)
    r = 4 * S
    d.ellipse([x - r, y2 + SENT_LEN + 6 * S, x + r, y2 + SENT_LEN + 6 * S + 2 * r],
              fill=accent)
    fig = font("Lora-Italic.ttf", 15 * S)
    d.text((x + 12 * S, y2 + SENT_LEN + 14 * S), "received", font=fig,
           fill=accent, anchor="ls")


def wrap(d, words, f, measure):
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= measure or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(path, plate, quote, attrib, bg, ink, faint, accent):
    img, d = base(bg)
    furniture(d, plate, "FIG. 12  ·  RECEPTION", ink, faint)
    measure = W - 2 * MARGIN
    words = ('“' + quote + '”').split()

    top_b = MARGIN + 96 * S
    bot_b = sig_top() - 72 * S
    avail = bot_b - top_b - 46 * S  # room kept back for the attribution

    size = 40 * S
    lines = []
    for trial in range(88 * S, 30 * S, -2 * S):
        f = font("Marcellus-Regular.ttf", trial)
        ls = wrap(d, words, f, measure)
        if len(ls) * round(trial * 1.30) <= avail:
            size, lines = trial, ls
            break
    f = font("Marcellus-Regular.ttf", size)
    lead = round(size * 1.30)

    block = lead * len(lines)
    y = top_b + (avail - block) * 0.42 + size * 0.76
    for i, line in enumerate(lines):
        x = MARGIN
        if i == 0:
            x -= d.textlength('“', font=f) * 0.58
        d.text((x, y), line, font=f, fill=ink, anchor="ls")
        y += lead

    a = font("Lora-Regular.ttf", 16 * S)
    draw_tracked(d, (MARGIN, y + 20 * S), attrib, a, faint, track=5 * S)

    received(d, sig_top(), ink, faint, accent)
    img.resize((1080, 1350), Image.LANCZOS).save(path)
    print("wrote", os.path.basename(path), "| display", size // S, "px |",
          len(lines), "lines")


os.makedirs(OUT, exist_ok=True)
DARK = dict(bg=PINE_DEEP, ink=CREAM, faint=mix(PINE_DEEP, CAMEL, 0.52),
            accent=TERRACOTTA)
LIGHT = dict(bg=CREAM, ink=PINE_DEEP, faint=mix(CREAM, PINE_FOREST, 0.40),
             accent=TERRACOTTA)

src = {t["id"]: t["text"] for t in json.load(
    open("/home/user/GitHub-folder/content/testimonials.json"))}

# Chosen for the objection this workshop actually has to beat: will I feel
# exposed, and is three hours with strangers worth twenty-seven dollars.
PICKS = [6, 13, 16, 9, 15, 2, 19, 20, 21, 17]

for i, tid in enumerate(PICKS):
    theme = DARK if i % 2 == 0 else LIGHT
    card(f"{OUT}/proof-{i + 1:02d}.png", f"PLATE {ROMAN[i]}", src[tid],
         "WORKSHOP PARTICIPANT", **theme)
