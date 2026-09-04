#!/usr/bin/env python3
"""Quiet Signal: five Meta ad cards, 1080x1350.

Rendered at 2x and downsampled with Lanczos so every hairline stays true.
"""
import os
from PIL import Image, ImageDraw, ImageFont

S = 2
W, H = 1080 * S, 1350 * S
MARGIN = 96 * S

FONTS = "./fonts"
OUT = "/home/user/GitHub-folder/images/ads"

PINE_DEEP = (31, 44, 31)
PINE_FOREST = (45, 62, 44)
MOSS = (93, 107, 63)
TERRACOTTA = (199, 93, 61)
ANTIQUE_GOLD = (184, 148, 90)
CAMEL = (201, 165, 121)
WARM_TAUPE = (168, 149, 128)
CREAM = (245, 239, 227)
WARM_CHARCOAL = (42, 37, 32)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def text_w(d, s, f, track=0):
    if not s:
        return 0
    w = sum(d.textlength(c, font=f) for c in s)
    return w + track * (len(s) - 1)


def draw_tracked(d, xy, s, f, fill, track=0, anchor="ls"):
    """Draw with per-character tracking. anchor: ls (left baseline) or ms."""
    x, y = xy
    if anchor == "ms":
        x -= text_w(d, s, f, track) / 2
    elif anchor == "rs":
        x -= text_w(d, s, f, track)
    for c in s:
        d.text((x, y), c, font=f, fill=fill, anchor="ls")
        x += d.textlength(c, font=f) + track


def fit_size(d, lines, fname, measure, hi, lo=40):
    """Largest size at which every line fits the measure."""
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        f = font(fname, mid)
        if max(d.textlength(l, font=f) for l in lines) <= measure:
            best, lo = mid, mid + 1
        else:
            hi = mid - 1
    return best


def corner_marks(d, colour):
    """Registration marks at the trim, clear of every text field."""
    a, ln = round(MARGIN * 0.56), 22 * S
    for cx, cy, dx, dy in (
        (a, a, 1, 1), (W - a, a, -1, 1),
        (a, H - a, 1, -1), (W - a, H - a, -1, -1),
    ):
        d.line([(cx, cy), (cx + dx * ln, cy)], fill=colour, width=S)
        d.line([(cx, cy), (cx, cy + dy * ln)], fill=colour, width=S)


# The finding: the same signal, sent and received. Hand-tuned, not random.
SENT_LEN = 15 * S
HEARD = [15, 15, 14, 15, 14, 15, 13, 13, 14, 12, 12, 11, None,
         10, 9, 10, 7, None, 6, 5, None, 4, 3, 2]
BREAK_AT = 12


SIG_H = 132 * S


def sig_top():
    """The diagram sits on a fixed baseline so the five plates align as a set."""
    return H - MARGIN - 42 * S - 100 * S - SIG_H


def signal(d, y, ink, faint, accent):
    """Two registers. The upper is what she said. The lower is what arrived."""
    y = y + 16 * S
    x0, x1 = MARGIN, W - MARGIN
    gap = 62 * S
    n = len(HEARD)
    step = (x1 - x0) / (n - 1)
    lab = font("Lora-Regular.ttf", 15 * S)

    draw_tracked(d, (x0, y - 16 * S), "SENT", lab, faint, track=4 * S)
    d.line([(x0, y), (x1, y)], fill=ink, width=S)
    for i in range(n):
        x = x0 + i * step
        d.line([(x, y), (x, y + SENT_LEN)], fill=ink, width=S)

    y2 = y + gap
    draw_tracked(d, (x0, y2 - 16 * S), "HEARD", lab, faint, track=4 * S)
    d.line([(x0, y2), (x1, y2)], fill=faint, width=S)
    for i, h in enumerate(HEARD):
        if h is None:
            continue
        x = x0 + i * step
        drift = round(i * 0.34) * S
        if i == BREAK_AT:
            continue
        d.line([(x, y2 + drift), (x, y2 + drift + h * S)], fill=ink, width=S)

    # The finding. The single place the accent is spent: one reading that
    # left the upper register and arrived nowhere near the lower one.
    x = x0 + BREAK_AT * step
    d.line([(x, y + 2 * S), (x, y2 + 34 * S)], fill=accent, width=2 * S)
    r = 4 * S
    d.ellipse([x - r, y2 + 34 * S, x + r, y2 + 34 * S + 2 * r], fill=accent)
    fig = font("Lora-Italic.ttf", 15 * S)
    d.text((x + 12 * S, y2 + 42 * S), "deviation", font=fig, fill=accent,
           anchor="ls")
    return y2 + 46 * S


def base(bg):
    img = Image.new("RGB", (W, H), bg)
    return img, ImageDraw.Draw(img)


def furniture(d, plate, fig, ink, faint):
    corner_marks(d, faint)
    n = font("Lora-Regular.ttf", 17 * S)
    y = MARGIN + 4 * S
    draw_tracked(d, (MARGIN, y), plate, n, faint, track=5 * S)
    draw_tracked(d, (W - MARGIN, y), fig, n, faint, track=5 * S, anchor="rs")
    # bottom rail: one sentence, then when. Auto-fitted so it never crowds.
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


def wrap(d, text, f, measure):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= measure or not cur:
            cur = t
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def statement_card(path, plate, fig, lines, bg, ink, faint, accent,
                   quote_lead=None, hang=False, maxsize=118, tail=None,
                   cta=None, tail_strong=False):
    img, d = base(bg)
    furniture(d, plate, fig, ink, faint)
    measure = W - 2 * MARGIN
    disp = "Marcellus-Regular.ttf"
    size = fit_size(d, lines, disp, measure, maxsize * S)
    # Optically centre the whole group (statement + evidence) in the field
    # between the notation row and the bottom rail, biased a little high.
    tf = tl = None
    tail_h = 0
    if tail:
        tf = font("Lora-Regular.ttf", 30 * S)
        tl = [wrap(d, para, tf, W - 2 * MARGIN) for para in tail]
        tail_h = 44 * S + sum(len(b) * 44 * S + 20 * S for b in tl)
    if cta:
        tail_h += 116 * S

    top_b = MARGIN + 88 * S
    bot_b = sig_top() - 64 * S
    room = bot_b - top_b

    # Shrink the display until the whole group clears the diagram. A card
    # that overflows into the plate is worse than one set a size smaller.
    def measure(sz):
        ld = round(sz * 1.20)
        lq = (round(sz * 0.40 * 1.34) * len(quote_lead)
              + round(sz * 0.24)) if quote_lead else 0
        return lq + ld * len(lines) + tail_h, ld, lq

    block, lead, lq_h = measure(size)
    while block > room and size > 52 * S:
        size -= 2 * S
        block, lead, lq_h = measure(size)
    f = font(disp, size)
    lq_f = font("Lora-Italic.ttf", round(size * 0.40)) if quote_lead else None

    top = top_b + max(0, (room - block)) * 0.46
    y = top + size * 0.76

    if quote_lead:
        for ql in quote_lead:
            d.text((MARGIN, y - size * 0.30), ql, font=lq_f, fill=faint,
                   anchor="ls")
            y += round(size * 0.40 * 1.34)
        y += round(size * 0.24)

    for i, line in enumerate(lines):
        x = MARGIN
        if hang and i == 0 and line and line[0] in "“\"":
            # optical: hang the opening quote into the margin
            x -= d.textlength(line[0], font=f) * 0.62
        d.text((x, y), line, font=f, fill=ink, anchor="ls")
        y += lead

    if tail:
        y += 26 * S
        tc = mix(faint, ink, 0.42) if tail_strong else faint
        for blk in tl:
            for ln in blk:
                d.text((MARGIN, y), ln, font=tf, fill=tc, anchor="ls")
                y += 44 * S
            y += 20 * S

    if cta:
        y += 22 * S
        cf = font("Lora-SemiBold.ttf", 30 * S)
        d.text((MARGIN, y), cta, font=cf, fill=ink, anchor="ls")
        wc = d.textlength(cta, font=cf)
        d.line([(MARGIN, y + 15 * S), (MARGIN + wc, y + 15 * S)],
               fill=accent, width=2 * S)

    signal(d, sig_top(), ink, faint, accent)
    img.resize((1080, 1350), Image.LANCZOS).save(path)
    print("wrote", path, "| display", size // S, "px")


def list_card(path, plate, fig, header, items, bg, ink, faint, accent,
              tail=None, cta=None):
    img, d = base(bg)
    furniture(d, plate, fig, ink, faint)
    measure = W - 2 * MARGIN

    hf = font("Lora-Regular.ttf", 27 * S)
    hlead = round(27 * S * 1.5)
    size = fit_size(d, items, "Marcellus-Regular.ttf", measure - 54 * S, 76 * S)
    num = font("Lora-Regular.ttf", 15 * S)

    tf = font("Lora-Regular.ttf", 30 * S)
    tl = [wrap(d, para, tf, W - 2 * MARGIN) for para in (tail or [])]
    extra = (44 * S + sum(len(b) * 44 * S + 20 * S for b in tl)) if tail else 0
    if cta:
        extra += 116 * S

    top_b = MARGIN + 88 * S
    bot_b = sig_top() - 64 * S
    room = bot_b - top_b

    # Same rule as the statement cards: shrink rather than run into the plate.
    def blk(sz):
        st = round(sz * 1.72)
        return hlead * len(header) + 52 * S + st * len(items) + extra, st

    block, step = blk(size)
    while block > room and size > 40 * S:
        size -= 2 * S
        block, step = blk(size)
    f = font("Marcellus-Regular.ttf", size)

    y = top_b + max(0, (room - block)) * 0.46 + 27 * S

    for hl in header:
        d.text((MARGIN, y), hl, font=hf, fill=faint, anchor="ls")
        y += hlead
    y += 52 * S

    for i, it in enumerate(items):
        d.text((MARGIN + 54 * S, y), it, font=f, fill=ink, anchor="ls")
        draw_tracked(d, (MARGIN, y - size * 0.30), f"0{i + 1}", num, faint,
                     track=3 * S)
        # the strike: a hairline through the line, terracotta on the last
        wln = d.textlength(it, font=f)
        c = accent if i == len(items) - 1 else faint
        sy = y - size * 0.30
        d.line([(MARGIN + 54 * S, sy), (MARGIN + 54 * S + wln, sy)],
               fill=c, width=S)
        y += step

    if tail:
        y += 4 * S
        tc = mix(faint, ink, 0.42)
        for blk in tl:
            for ln in blk:
                d.text((MARGIN, y), ln, font=tf, fill=tc, anchor="ls")
                y += 44 * S
            y += 20 * S
    if cta:
        y += 22 * S
        cf = font("Lora-SemiBold.ttf", 30 * S)
        d.text((MARGIN, y), cta, font=cf, fill=ink, anchor="ls")
        wc = d.textlength(cta, font=cf)
        d.line([(MARGIN, y + 15 * S), (MARGIN + wc, y + 15 * S)],
               fill=accent, width=2 * S)

    signal(d, sig_top(), ink, faint, accent)
    img.resize((1080, 1350), Image.LANCZOS).save(path)
    print("wrote", path, "| display", size // S, "px")


os.makedirs(OUT, exist_ok=True)

DARK = dict(bg=PINE_DEEP, ink=CREAM, faint=mix(PINE_DEEP, CAMEL, 0.52),
            accent=TERRACOTTA)
LIGHT = dict(bg=CREAM, ink=PINE_DEEP, faint=mix(CREAM, PINE_FOREST, 0.40),
             accent=TERRACOTTA)

statement_card(
    f"{OUT}/ad-02-he-does-what.png", "PLATE I", "FIG. 12  ·  DEVIATION",
    ["I’m sorry,", "he does WHAT?!"], maxsize=104, tail_strong=True,
    tail=["He brings her flowers once a week.",
          "He takes the rubbish out. He does the dishes without being asked.",
          "Her friends have no idea how she did it.",
          "She didn’t nag him for twenty years. She learned how to talk to "
          "him so he could actually hear her."],
    cta="That’s what we’re doing on Wednesday. $27.", **DARK)

statement_card(
    f"{OUT}/ad-03-im-fine.png", "PLATE II", "FIG. 12  ·  DEVIATION",
    ["“I said", "I’m fine.”"], hang=True, maxsize=132, tail_strong=True,
    tail=["You weren’t fine. He knew you weren’t fine.",
          "And you both let it go, again, because the last four times it "
          "turned into a fight.",
          "Twenty years of that is how two people end up living like "
          "flatmates in a house they bought together."],
    cta="Wednesday we break it. $27.", **LIGHT)

statement_card(
    f"{OUT}/ad-04-what-he-hears.png", "PLATE III", "FIG. 12  ·  DEVIATION",
    ["It isn’t what you say.", "It’s what he hears."],
    maxsize=94,
    tail=["He hears that he’s failing you.",
          "You don’t even know that’s what he heard.",
          "And that’s what he defends himself against."],
    cta="Wednesday 9 September, 6pm NZ. $27.", **DARK)

statement_card(
    f"{OUT}/ad-05-costume.png", "PLATE IV", "FIG. 12  ·  DEVIATION",
    ["is not a feeling.", "That’s why he", "defends himself."], maxsize=104,
    quote_lead=["“I feel like you never listen”"], tail_strong=True,
    tail=["He hears blame. So he defends himself.",
          "And then you wonder why this keeps happening.",
          "There are three sentences that actually get through."],
    cta="Wednesday, 6pm NZ. $27.", **LIGHT)

list_card(
    f"{OUT}/ad-08-four-sentences.png", "PLATE V", "FIG. 12  ·  DEVIATION",
    ["Four sentences that guarantee", "he stops listening."],
    ["“You always...”", "“Why can’t you just...”",
     "“I shouldn’t have to ask.”",
     "“Never mind, forget it.”"],
    tail=["I’ve said all four of them. They’re what comes out when you’re "
          "tired of asking."],
    cta="Learn how to say it so he can give you what you want.", **DARK)

statement_card(
    f"{OUT}/ad-10-its-tomorrow.png", "PLATE VI", "FIG. 12  ·  DEVIATION",
    ["It’s tomorrow."], maxsize=124,
    tail=["Feel Wanted and Loved Again.",
          "Wednesday 9 September, 6 to 9pm NZ.",
          "Three hours, live on Zoom. $27."],
    cta="Join us.", **LIGHT)
