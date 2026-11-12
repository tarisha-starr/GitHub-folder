#!/usr/bin/env python3
"""The Art of Polarity & Attraction - one combined deck, two Zoom sessions.
SEFW palette, Belleza headings + Lora body, upright text, NO presenter notes."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
import os

NAVY =RGBColor(0x1D,0x28,0x3C); PLUM =RGBColor(0x74,0x23,0x4F)
BLUSH=RGBColor(0xE4,0xBB,0xC2); PINK =RGBColor(0xFC,0xE8,0xEA)
SAGE =RGBColor(0x7C,0xA1,0xA5); TEAL =RGBColor(0x22,0x46,0x52)
GOLD =RGBColor(0xC9,0xA8,0x6D)
HEAD_FONT="Belleza"; BODY_FONT="Lora"
SCHEME={"pink":(PINK,NAVY,PLUM),"blush":(BLUSH,NAVY,PLUM),"plum":(PLUM,PINK,GOLD),
        "navy":(NAVY,PINK,GOLD),"teal":(TEAL,PINK,GOLD),"sage":(SAGE,NAVY,PLUM),
        "gold":(GOLD,NAVY,PLUM)}

def new_deck():
    p=Presentation(); p.slide_width=Inches(13.333); p.slide_height=Inches(7.5); return p

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
    r.font.name=HEAD_FONT; r.font.size=Pt(52 if big else 40); r.font.color.rgb=txt_col
    ln=s.shapes.add_shape(1,left,top+Inches(3.1 if big else 1.95),Inches(1.6),Pt(3))
    ln.fill.solid(); ln.fill.fore_color.rgb=accent; ln.line.fill.background(); ln.shadow.inherit=False
    if body:
        by=s.shapes.add_textbox(left,top+Inches(3.5 if big else 2.3),width,Inches(3.2))
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

d=new_deck()

# ===== SESSION 1 - The Open Heart =====
add(d,"navy","The Art of Polarity & Attraction",
    eyebrow="November Training  ·  Session 1",
    body="The Open Heart: staying with love.",big=True)
add(d,"pink","What is polarity?",
    body="Polarity is the attraction between love and presence, between the feminine and the masculine. The pull comes from their difference, and the greater the difference, the stronger the charge.")
add(d,"navy","Masculine energy",
    body="The masculine is presence: a steady, grounded, focused energy that holds and gives structure, the banks of the river. It lives in all of us, and here it is his gift.")
add(d,"blush","Feminine energy",
    body="The feminine is love in motion, radiant and flowing and alive with feeling. She is the river. This energy lives in all of us too, and here it is her gift.")
add(d,"plum","The three arts",eyebrow="Our map",
    body=["Stay with love, with an open heart.","Amplify your expression.","Amplify and express polarity."])
add(d,"blush","David Deida",eyebrow="Teachings we weave",
    body=["We weave my work with David Deida's teachings on polarity.",
          "Dear Lover, his guide for women.","The Way of the Superior Man, his book for men."])
add(d,"navy","Stay with love",eyebrow="Art one",
    body="With an open heart. Love is openness; fear is contraction. When you open, you magnetise. When you close, the charge dies.",big=True)
add(d,"gold","Vulnerable vs emotional",
    body=["Connected to your heart: vulnerable, and still loving, even in anger.",
          "Disconnected from your heart: emotional, and it lands as an attack.",
          "And he has every right to protect himself from an attack."])
add(d,"plum","Anger from the heart",
    body="You can feel anger and still stay connected. Same fire, open heart. That's vulnerability, not attack.")
add(d,"blush","Reflect",eyebrow="Before the breakout",
    body=["When does my anger come from love? When does it become an attack?",
          "What happens in my body when I close my heart?"])
add(d,"teal","Group demo · Anger from the heart",eyebrow="As a group",
    body=["A volunteer names something she's angry about.","She says it disconnected, then again, hand on heart.",
          "The group feels the difference: attack, versus anger that still loves.",
          "Then we all practise the connected version together."])
add(d,"pink","Open to love, in the whole body",
    body="Love isn't only in the heart. We can open the heart and the whole body, more and more. There's no limit to how much you can let in.")
add(d,"sage","Group practice · Open your heart & body",eyebrow="As a group",
    body="Together: hand on heart, hand on belly. Breathe. Feel love in your chest, let it spread through your whole body. Open a little more with each breath.")
add(d,"plum","Devotion",eyebrow="The heart of the practice",
    body="The feminine's deepest practice: opening your heart and offering your love, again and again, as a gift. Not love you earn or withhold. Love you give, to your partner, to life, to the divine.")
add(d,"blush","The practice of devotion",
    body=["Open your heart as an offering, every day.","Give your love freely, radiate it, don't ration it.",
          "Let your relationship be a doorway to something greater.","When you want to close, choose to open to love instead."])
add(d,"pink","Reflect",eyebrow="Devotion",
    body="When, and how, are you withholding your love?")
add(d,"navy","This week",eyebrow="Take home",
    body=["When anger rises, keep one hand on your heart.","Feel it, speak it, stay connected.",
          "Each day, open your whole body to love a little more."])

# ===== SESSION 2 - Amplifying Expression & Polarity =====
add(d,"navy","The Art of Polarity & Attraction",
    eyebrow="November Training  ·  Session 2",
    body="Amplifying expression and polarity.",big=True)
add(d,"plum","Amplify your expression",eyebrow="Art two",
    body="He can't feel what you only hint at. When you let your feeling move through your body, he finally gets you.",big=True)
add(d,"pink","Show, don't hint",
    body="Face, voice, movement, energy. Let him see and feel what you feel, so he can actually understand you.")
add(d,"gold","How to encourage her",eyebrow="The witness's role",
    body=["Encourage more, don't critique.","'Relax here a little more.'  'Give me more expression.'",
          "Affirm when it lands: 'Yes, I can really feel you.'","Draw her out, and celebrate her."])
add(d,"blush","Reflect",eyebrow="Before the breakout",
    body=["Where do I hold my expression in?","What does my body do when I let it show?"])
add(d,"teal","Breakout · Amplify your expression",eyebrow="In pairs · with feedback",
    body=["A expresses a feeling, fully, through face, voice and body.",
          "B encourages: 'relax here more,' 'give me more,' and affirms 'yes, I can really feel you.'",
          "Let A grow bigger with the encouragement. Swap."])
add(d,"navy","Amplify polarity",eyebrow="Art three",
    body="Not by becoming the strong one. By amplifying the feminine, more emotion, more expression, so he is drawn into his presence.",big=True)
add(d,"gold","Draw him into his presence",
    body=["Presence is his masculine gift, not yours to supply.",
          "When he drops, go further in, not away. If he's helpless, become even more helpless.",
          "Bring more emotion, more expression, through your body, from an open heart.",
          "Your amplified feminine calls him into his presence."])
add(d,"sage","Be the river",
    body=["A river needs banks. If you hold the banks, structured, controlled, strong, he has nothing to hold.",
          "Become the river: softer, more flowing, less structured.",
          "Then he has to become the banks, the structure and the presence for you."])
add(d,"pink","Reflect",eyebrow="Before the breakout",
    body=["How do I usually respond when he drops, shrink, fix, or go strong myself?",
          "What would it be like to amplify the feeling through my body instead?"])
add(d,"teal","Breakout · Amplifying polarity",eyebrow="In pairs",
    body=["One of you drops: sad, flat, giving up.",
          "The other: don't shrink, fix, or go strong. Amplify the SAME feeling, more emotion, more expression through your body.",
          "Feel how it calls the other into presence. Swap roles."])
add(d,"blush","The three arts, together",
    body=["Stay with love, with an open heart.","Amplify your expression, through the body.",
          "Amplify polarity: more feeling, more expression, so he rises into presence."])
add(d,"navy","This week",eyebrow="Take home",
    body=["Show one feeling fully through your body each day.","When he drops, don't shrink, amplify the feeling through your body.",
          "Keep your heart open, let yourself be seen, and let him rise to meet you."])
add(d,"plum","Love meeting presence",
    body="Polarity is the attraction between love and presence, the feminine and the masculine. Keep your heart open, let your love be seen, and he rises to meet you.",big=True)

os.makedirs("content/sessions/slides",exist_ok=True)
out="content/sessions/slides/Polarity-and-Attraction.pptx"
d.save(out)
print("saved",out,len(d.slides._sldIdLst),"slides")
