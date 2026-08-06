#!/usr/bin/env python3
"""Master Your Emotions - two Zoom decks (Session 1 Safety & Self-Compassion,
Session 2 Riding the Waves & Tapping). Self-contained. SEFW palette only,
Marcellus + Lora, upright text, one line or a few bullets per slide."""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
import os

# ---- SEFW brand palette (exact hexes) ----
NAVY =RGBColor(0x1D,0x28,0x3C); PLUM =RGBColor(0x74,0x23,0x4F)
BLUSH=RGBColor(0xE4,0xBB,0xC2); PINK =RGBColor(0xFC,0xE8,0xEA)
SAGE =RGBColor(0x7C,0xA1,0xA5); TEAL =RGBColor(0x22,0x46,0x52)
GOLD =RGBColor(0xC9,0xA8,0x6D)

HEAD_FONT="Marcellus"; BODY_FONT="Lora"

# key -> (bg, text, accent); every colour from the SEFW palette
SCHEME={
    "pink":  (PINK, NAVY, PLUM),
    "blush": (BLUSH,NAVY, PLUM),
    "plum":  (PLUM, PINK, GOLD),
    "navy":  (NAVY, PINK, GOLD),
    "teal":  (TEAL, PINK, GOLD),
    "sage":  (SAGE, NAVY, PLUM),
    "gold":  (GOLD, NAVY, PLUM),
}


def new_deck():
    prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
    return prs


def add(prs,bg,title,body=None,eyebrow=None,big=False,footer=True):
    bg_col,txt_col,accent=SCHEME[bg]
    s=prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb=bg_col
    left=Inches(0.9); width=Inches(11.5); top=Inches(1.1)
    if eyebrow:
        eb=s.shapes.add_textbox(left,Inches(0.6),width,Inches(0.5))
        r=eb.text_frame.paragraphs[0].add_run(); r.text=eyebrow.upper()
        r.font.name=BODY_FONT; r.font.size=Pt(15); r.font.bold=True; r.font.color.rgb=accent
    tb=s.shapes.add_textbox(left,top,width,Inches(3.2))
    tf=tb.text_frame; tf.word_wrap=True; tf.vertical_anchor=MSO_ANCHOR.TOP
    r=tf.paragraphs[0].add_run(); r.text=title
    r.font.name=HEAD_FONT; r.font.size=Pt(54 if big else 40); r.font.color.rgb=txt_col
    ln=s.shapes.add_shape(1,left,top+Inches(3.25 if big else 2.0),Inches(1.6),Pt(3))
    ln.fill.solid(); ln.fill.fore_color.rgb=accent; ln.line.fill.background(); ln.shadow.inherit=False
    if body:
        by=s.shapes.add_textbox(left,top+Inches(3.6 if big else 2.35),width,Inches(3.2))
        bf=by.text_frame; bf.word_wrap=True
        items=body if isinstance(body,list) else [body]
        for i,item in enumerate(items):
            para=bf.paragraphs[0] if i==0 else bf.add_paragraph()
            bullet=isinstance(body,list) and len(body)>1
            run=para.add_run(); run.text=("•  "+item) if bullet else item
            run.font.name=BODY_FONT; run.font.size=Pt(23 if bullet else 27)
            run.font.italic=False; run.font.color.rgb=txt_col
            para.space_after=Pt(12)
    if footer:
        ft=s.shapes.add_textbox(left,Inches(6.85),width,Inches(0.4))
        fr=ft.text_frame.paragraphs[0].add_run(); fr.text="SEXUALEMPOWERMENTFORWOMEN.COM"
        fr.font.name=BODY_FONT; fr.font.size=Pt(11); fr.font.color.rgb=accent
    return s


# ============ SESSION 1 - Safety & Self-Compassion ============
s1=new_deck()
add(s1,"navy","Master Your Emotions",eyebrow="Radiant Women's Circle  ·  Session 1",
    body="Safety and self-compassion.",big=True)
add(s1,"pink","Lack of safety is the problem.",
    body="Not the emotions. Emotions aren't dangerous. Being flooded is.",big=True)
add(s1,"plum","Start with safety.",
    body="We only expand, feel more, open more, when we're not overwhelmed and not sliding into our old patterns.")
add(s1,"navy","What safety is",
    body=["I'm connected to myself.","I feel what's good for me.","I test it out.",
          "I read how the other responds.","Then I step forward, or step away."])
add(s1,"gold","Then, no overwhelm.",
    body="Because I never abandon myself to cope. I stay with me the whole way.")
add(s1,"blush","Reflect",eyebrow="Before the breakout",
    body=["When do I feel safe? When do I not?","Where do I abandon myself to keep the peace?",
          "What does it feel like in my body when I leave myself?"])
add(s1,"teal","Breakout · My safety",eyebrow="In pairs",
    body=["One place I feel safe is... one place I don't is...","One way I abandon myself is...",
          "Partner: just witness. Then swap."])
add(s1,"plum","The loop",
    body="Stress makes emotions. Emotions make stress. So we reach for something to fill the hole.")
add(s1,"pink","The hole can't be filled from outside",
    body="There's no signal that says your emotional need is met. The fix backfires, and the feeling still waits to be heard.")
add(s1,"navy","Emotions are the messengers.",
    body="Ignore them and they don't go away. They get louder. They start screaming until we listen.",big=True)
add(s1,"sage","Reflection",eyebrow="One minute",
    body="What do you reach for when a feeling gets too big?")
add(s1,"gold","The reframe",eyebrow="Dr Linda Bacon",
    body="If you numb, you don't have a problem with food or wine or your phone. You have a problem with taking care of yourself.")
add(s1,"blush","Self-compassion",eyebrow="Hands on heart",
    body=["How do you feel? What's going on for you?","I hear you feel...","I see this is difficult. I am here."])
add(s1,"teal","Breakout · Self-compassion",eyebrow="In pairs",
    body=["Hands on heart. Say it out loud to your partner.","Partner reflects: I hear you feel...",
          "No advice. Then swap."])
add(s1,"navy","This week",eyebrow="Take home",
    body=["Am I safe? Am I connected to myself?","Hands on heart: how do you feel?","Listen. That's the practice."])

# ============ SESSION 2 - Riding the Waves & Tapping ============
s2=new_deck()
add(s2,"navy","Master Your Emotions",eyebrow="Radiant Women's Circle  ·  Session 2",
    body="Riding the waves, and tapping.",big=True)
add(s2,"plum","Anchor safety first.",
    body="Feet on the floor. Hand on your heart. Right now, in this moment, I am here, and I am safe.")
add(s2,"pink","Reflect",eyebrow="Before we begin",
    body=["What feeling, if I let it, feels too big?","Where do I feel it in my body? Where am I braced?",
          "What brings me back to safety?"])
add(s2,"navy","Riding the wave",
    body="Not shutting it out. Not drowning in it. Feeling into it without being taken over.",big=True)
add(s2,"gold","Grief comes in waves",
    body="You don't feel all of it at once. It rises, it crests, it passes, for now. Then it comes again. That's grief, not you failing.")
add(s2,"blush","Feel a little, then come back",
    body=["Go into the feeling for a breath.","Come back to safety: feet, breath, hand on heart.",
          "A little in, a little out."])
add(s2,"sage","Keep one foot in the present",
    body="Name five things you see. Right now, I am here, and I am safe. That's how you feel it without disappearing into it.")
add(s2,"teal","Breakout · Feel a little, come back",eyebrow="In pairs · pick a 3 or 4, not a 9",
    body=["A feels it for a breath, names where it is.","B guides A back to safety.",
          "A little in, a little out, three times. Swap."])
add(s2,"plum","The body still braces",
    body="You can make peace in your head, and your body can still be holding it. It lets go through breath, tears, moving, being held.")
add(s2,"navy","EFT · tapping",
    body="An easy, direct way to settle a big feeling and come back to safety in your body.")
add(s2,"gold","Why it works",
    body="Tapping calms the amygdala's alarm, so you shift into your logical brain and choose your response.")
add(s2,"pink","Wash the laundry",
    body="We don't hide the feeling in the wardrobe. We take it out, wash it, and clear it. Then reframes come naturally.")
add(s2,"navy","How to tap",
    body=["Name it, be specific. Rate it 1 to 10.","Setup: even though I feel this, I love and accept myself.",
          "Tap the points, say it out loud.","Breathe, re-rate, repeat until it drops."])
add(s2,"sage","The points",
    body=["Top of head · eyebrow · side of eye · under eye","Under nose · chin · collarbone",
          "Under arm · wrist","Sip water as you go."])
add(s2,"teal","Breakout · Tap together",eyebrow="In pairs",
    body=["Each pick an issue, rate it 1 to 10.","Tap through the points, say your phrase out loud.",
          "Breathe, re-rate. Swap who leads."])
add(s2,"plum","This week",eyebrow="Take home",
    body=["Safety first: am I connected to myself?","Hands on heart: how do you feel?",
          "Tap when it's big. Feel a little, come back."])
add(s2,"gold","You don't control your emotions.",
    body="You master them by feeling safe enough to finally listen.",big=True)

os.makedirs("content/sessions/slides",exist_ok=True)
p1="content/sessions/slides/Master-Your-Emotions-Session-1.pptx"
p2="content/sessions/slides/Master-Your-Emotions-Session-2.pptx"
s1.save(p1); s2.save(p2)
print("saved",p1,len(s1.slides._sldIdLst),"slides")
print("saved",p2,len(s2.slides._sldIdLst),"slides")
