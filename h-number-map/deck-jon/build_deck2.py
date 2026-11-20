import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, 'assets2')
INK, GREY, NAVY = RGBColor(0x1A, 0x1A, 0x1A), RGBColor(0x55, 0x55, 0x55), RGBColor(0x1F, 0x3A, 0x5F)
T = [  # (id, question, old sheet, tool)
 ('Q1', 'What happened to Section M lots 11, 12 and 16: are they still recognized, renumbered, or withdrawn?', 'Section M sheet'),
 ('Q2', 'Do Section M lots 56 and 57 continue the column of 52–55 (likewise 62/63 under 58–61 and 68/69 under 64–67)?', 'Section M sheet'),
 ('Q3', 'Are Section B lots 390A, 390B and 390C active lots, and where do they stand?', 'Section B sheet'),
 ('Q4', 'Were Section B lots 289 and 290 withdrawn, relocated, or are they still recognized at the chapel entrance circle?', 'Section B sheet'),
 ('Q5', 'Which are the real names of the last four Section B H lots: 318H, 336H, 354H, 372H (as drawn) or 320H, 340H, 360H, 380H (as in the table)?', 'Section B sheet'),
 ('Q6', 'Do the Section A row-start H lots (20H, 39H, 58H …) exist, and where do they stand?', 'Section A sheet'),
 ('Q7', 'What is the hatched building beside the accessible parking space: maintenance building, restroom, or something else?', 'Overall Map sheet'),
 ('Q8', 'Are the strip lots 1–19 and 21 north of the oval Section L lots, and where do they belong in the numbering?', 'Section L sheet'),
 ('Q9', 'Which cell beside Section B lots 361–362 is A361, which is A362, and what is the unlabelled cell?', 'Section B sheet'),
 ('Q10', 'Are Section B lots 20H, 20 and 19A three separate lots, and what is 19A?', 'Section B sheet'),
 ('Q11', 'Do the strip lots 312A, 293A and 291A exist in Section A, and is the unlabelled strip 292A?', 'Section A sheet'),
 ('Q12', 'What is the narrow unlabelled lot between Section G 58 and Section F 210, and is it a grave lot?', 'Section F & G sheet'),
 ('Q13', 'Do plain lots 311, 322 and 333 exist in Section D below the H lots 311H, 322H and 333H?', 'Section D sheet'),
 ('Q14', 'Are the Section C H lots 237H, 218H and 161H (and six more like them) numbered lots?', 'Section C sheet'),
 ('Q15', 'Are the 20 lots 395–414 along the west edge of Section B Section B lots, and where do they belong in the numbering?', 'Section B sheet'),
 ('Q16', 'Were Section B lots 12, 31, 50 … ever recorded under their old H-numbers (B 12 = H000022)?', 'Section B sheet'),
 ('Q17', 'Is lot 293 in Section D, the lot between 294 and 292?', 'Section D sheet')]
prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5); BL = prs.slide_layouts[6]
def tb(sl, x, y, w, h, text, size, bold=False, color=INK, anchor=MSO_ANCHOR.TOP, align=PP_ALIGN.LEFT):
    s = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = s.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.03); tf.margin_top = tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]; p.alignment = align; r = p.add_run(); r.text = text; r.font.size = Pt(size); r.font.bold = bold; r.font.name = 'Arial'; r.font.color.rgb = color
for qid, q, sheet in T:
    sl = prs.slides.add_slide(BL)
    tb(sl, 0.35, 0.15, 12.65, 1.05, '%s  %s' % (qid, q), 24, True, anchor=MSO_ANCHOR.MIDDLE)
    for side, x, head in (('old', 0.35, 'Old section map · ' + sheet), ('new', 6.78, '2022 ground map')):
        tb(sl, x, 1.25, 6.2, 0.3, head, 12, True, NAVY)
        im = Image.open(os.path.join(A, '%s_%s.png' % (qid, side))); w = 6.2; h = min(5.55, im.height * w / im.width); w = im.width * h / im.height
        sl.shapes.add_picture(os.path.join(A, '%s_%s.png' % (qid, side)), Inches(x + (6.2 - w) / 2 if w < 6.2 else x), Inches(1.6), Inches(w), Inches(h))
prs.save(os.path.join(HERE, 'Cedar_Grove_Questions_for_Jon.pptx')); print(len(prs.slides))
