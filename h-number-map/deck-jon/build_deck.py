import json, os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image
import content as C
HERE = C.HERE; A = os.path.join(HERE, 'assets'); META = json.load(open(os.path.join(A, 'meta.json')))
FONT = 'Arial'
INK, GREY, RED, AMB, GRN, NAVY = RGBColor(0x20, 0x20, 0x20), RGBColor(0x55, 0x55, 0x55), RGBColor(0xB3, 0x26, 0x1E), RGBColor(0x9A, 0x5B, 0x00), RGBColor(0x2E, 0x7D, 0x32), RGBColor(0x1F, 0x3A, 0x5F)
STCOL = {C.NEED: RED, C.DONE: AMB, C.RES: GRN}
PAGE_SEC = {1: 'Section A', 2: 'Section B', 3: 'Section C', 4: 'Section D', 5: 'Section E & H', 6: 'Section F & G', 7: 'Section I & J & K', 8: 'Section L', 9: 'Section M', 11: 'Overall Map'}
prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5); BL = prs.slide_layouts[6]
def tb(sl, x, y, w, h, text='', size=11, bold=False, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, fill=None):
    s = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = s.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05); tf.margin_top = tf.margin_bottom = Inches(0.02)
    if fill is not None: s.fill.solid(); s.fill.fore_color.rgb = fill
    lines = text if isinstance(text, list) else [text]
    for i, t in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align
        runs = t if isinstance(t, list) else [(t, bold, color)]
        for r in runs:
            rr = p.add_run(); rr.text = r[0]; rr.font.size = Pt(size); rr.font.bold = r[1]; rr.font.name = FONT; rr.font.color.rgb = r[2]
    return s
def table(sl, x, y, w, rows, head, size=10.5, colw=None, rh=0.27, headfill=NAVY):
    n = len(rows) + 1; m = len(head)
    gs = sl.shapes.add_table(n, m, Inches(x), Inches(y), Inches(w), Inches(rh * n)); t = gs.table
    tblPr = gs._element.graphic.graphicData.tbl.tblPr; tblPr.set('bandRow', '0'); tblPr.set('firstRow', '0')
    if colw:
        tot = sum(colw)
        for i, c in enumerate(colw): t.columns[i].width = Inches(w * c / tot)
    for r in range(n):
        t.rows[r].height = Inches(rh)
        for c in range(m):
            cell = t.cell(r, c); cell.margin_left = cell.margin_right = Inches(0.05); cell.margin_top = cell.margin_bottom = Inches(0.02); cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            txt = head[c] if r == 0 else rows[r - 1][c]; cell.text = ''
            p = cell.text_frame.paragraphs[0]; run = p.add_run(); run.text = str(txt); run.font.size = Pt(size); run.font.name = FONT
            if r == 0: run.font.bold = True; run.font.color.rgb = RGBColor(255, 255, 255); cell.fill.solid(); cell.fill.fore_color.rgb = headfill
            else: run.font.color.rgb = INK; cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(0xF4, 0xF4, 0xF4) if r % 2 else RGBColor(255, 255, 255)
    return gs
def pic(sl, path, x, y, w, h):
    im = Image.open(path); r = min(w / im.width, h / im.height); pw, ph = im.width * r, im.height * r
    sl.shapes.add_picture(path, Inches(x + (w - pw) / 2), Inches(y), Inches(pw), Inches(ph)); return ph
def header(sl, title, status=None, qid=None):
    tb(sl, 0.4, 0.18, 10.3, 0.75, [[((qid + '  ') if qid else '', True, NAVY), (title, True, INK)]], size=22, anchor=MSO_ANCHOR.MIDDLE)
    if status: tb(sl, 10.75, 0.3, 2.2, 0.55, status, size=11, bold=True, color=RGBColor(255, 255, 255), align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, fill=STCOL[status])
def src_old(q, key):
    if key == 'Q7': return 'OLD · Cemetery Map – All Sections on Individual Pages (PDF), page 11, "Overall Map" sheet; crop with the MAINTENANCE BUILDING and RESTROOM labels and leaders (not registered to the 2022 drawing, so scale differs).'
    m = META[key]
    return 'OLD section map · Cemetery Map – All Sections on Individual Pages (PDF), page %d, %s sheet · drawing-unit box x %d-%d, y %d-%d' % (m['page'], PAGE_SEC[m['page']], m['box'][0], m['box'][2], m['box'][1], m['box'][3])
def src_new(q, key):
    if key == 'Q7': return '2022 ground map · Cedar Grove 2022 with CR.ai (page 1) · drawing-unit box x 1290-1375, y 318-372 (Section M parking corner).'
    m = META[key]; return '2022 ground map · Cedar Grove 2022 with CR.ai (page 1) · same drawing-unit box x %d-%d, y %d-%d (same area, scale and orientation as the left crop)' % (m['box'][0], m['box'][2], m['box'][1], m['box'][3])
ORDER = [s for cat in 'NLA' for s in sorted([x for x in C.S if x['cat'] == cat], key=lambda z: z['id'])]
# natural Q order within each group
def qn(i): 
    import re; m = re.match(r'Q(\d+)([ab]?)', i); return (int(m.group(1)), m.group(2))
ORDER = [s for cat in 'NLA' for s in sorted([x for x in C.S if x['cat'] == cat], key=lambda z: qn(z['id']))]
PAGES = {s['id']: i + 2 for i, s in enumerate(ORDER)}
GROUPS = {'N': 'NUMBERING DECISIONS (change or keep an H-number)', 'L': 'LABEL / LOCATION DECISIONS (what a lot is called or where it stands)', 'A': 'MAP ARTWORK ONLY'}
# ---------- index
sl = prs.slides.add_slide(BL); header(sl, 'Cedar Grove map questions for Jon', None)
tb(sl, 0.4, 0.88, 12.5, 0.5, 'Each slide: old section map (left) and 2022 ground map (right) at the same scale, one question, space for the answer. Numbering decisions come first. Status of every item below: none has been answered yet.', size=11, color=GREY)
rows = []; fills = []
for cat in 'NLA':
    rows.append([GROUPS[cat], '', '', '']); fills.append(cat)
    for s in [x for x in ORDER if x['cat'] == cat]: rows.append([s['id'], s['title'], s['status'], str(PAGES[s['id']])]); fills.append(None)
half = (len(rows) + 1) // 2
def idx_table(x, part):
    gs = table(sl, x, 1.45, 6.15, part, ['Q', 'Decision', 'Status', 'Slide'], size=9, colw=[0.6, 4.4, 1.7, 0.5], rh=0.215)
    t = gs.table
    for r, row in enumerate(part, start=1):
        if row[1] == '':
            t.cell(r, 0).merge(t.cell(r, 3))
            for p in t.cell(r, 0).text_frame.paragraphs:
                for rn in p.runs: rn.font.bold = True; rn.font.color.rgb = NAVY; rn.font.size = Pt(9)
        else:
            for rn in t.cell(r, 2).text_frame.paragraphs[0].runs: rn.font.bold = True; rn.font.color.rgb = STCOL[row[2]]
idx_table(0.4, rows[:half]); idx_table(6.78, rows[half:])
tb(sl, 0.4, 6.95, 12.5, 0.4, 'Colour key: red = Needs a decision · amber = Already corrected · needs confirmation · green = Resolved (none yet). Proposed numbers are always marked "proposed"; nothing marked proposed has been applied.', size=9, color=GREY)
# ---------- question slides
for s in ORDER:
    sl = prs.slides.add_slide(BL); header(sl, s['title'], s['status'], s['id'])
    t = s['table']; th = 0.25 * (len(t['rows']) + 1) if t else 0; ih = max(2.3, min(3.5, 7.4 - 1.0 - 0.44 - 0.4 - 0.08 - th - (1.4 if t else 1.9)))
    phs = []
    for side, x in (('old', 0.4), ('new', 6.83)):
        key = s['img']; path = os.path.join(A, '%s_%s.png' % (key, side)); phs.append(pic(sl, path, x, 1.0, 6.1, ih))
    ph = max(phs)
    for side, x in (('old', 0.4), ('new', 6.83)):
        tb(sl, x, 1.0 + ph + 0.02, 6.1, 0.42, (src_old if side == 'old' else src_new)(s['id'], s['img']), size=8, color=GREY)
    y = 1.0 + ph + 0.46
    tb(sl, 0.4, y, 12.5, 0.36, [[('Key: ', True, RED), (s['key'], False, GREY)]], size=8.5); y += 0.4
    if t:
        rh = 0.25; colw = None
        table(sl, 0.4, y, 12.5, t['rows'], t['head'], size=9 if t.get('tsmall') else 10, rh=rh, colw=t.get('colw')); y += rh * (len(t['rows']) + 1) + 0.1 + (0.12 if t.get('colw') is None and any(len(str(c)) > 34 for r in t['rows'] for c in r) else 0)
    hh = 7.4 - y
    w1, w2, w3 = 4.1, 4.5, 3.7
    tb(sl, 0.4, y, w1, hh, [[('What both drawings show', True, NAVY)], s['obs']], size=10 if t else 10.5)
    ans = [[('Question for Jon', True, NAVY)], [(s['q'], True, INK)]] + [[(a, False, INK)] for a in s['ans']] + [[('Jon\'s notes: ______________________________', False, GREY)]]
    tb(sl, 0.4 + w1 + 0.1, y, w2, hh, ans, size=10 if t else 10.5)
    tb(sl, 0.4 + w1 + w2 + 0.2, y, w3, hh, [[('What the answer changes', True, NAVY)], s['chg']], size=10 if t else 10.5)
# ---------- decision sheets
UPD = {'Q1': 'M 11/12/16 kept → no change; withdrawn → remove H002601/02/05, shift later M by 1-3 and K…L by 3; renumbered → new labels',
 'Q2': 'Confirm M 56-69 route (15 numbers); a "no" reorders those numbers inside M only', 'Q3': 'Keep or withdraw H002378-80; relocate artwork if moved',
 'Q4a': 'Keep or withdraw H000628/629; no shift', 'Q5b': 'Keep plain-lot numbers (B 20-360) or remove them and shift later B lots', 'Q6': 'Draw 18 A row-start H lots or leave H000087…H000835 unused',
 'Q8': 'Keep L 1-13 as H002856-68; if 14-19/21 are lots insert 7 numbers and shift K…L 107 by 7', 'Q10': 'Confirm B 20 = H000002, 19A…1 = H000003-22; otherwise restore review rows',
 'Q13a': 'Confirm 311/322/333 inserted (H001521/64/607); else remove and shift D…L back 1 per lot', 'Q13b': 'Confirm printed-lot labels for D row heads (280H = H001432, 300H = H001476); else relabel',
 'Q14': 'Confirm nine C H lots numbered; "no" removes nine numbers and shifts C…L back', 'Q15': 'Apply (a) +20 from D 1U, or (b) +20 for every lot, or other; then regenerate all tables and maps',
 'Q16': 'Re-key any record that used v1 H-IDs through crosswalk_v1_to_v2.csv', 'Q17': 'Confirm D 293 = H001484; else free the place', 'Q4b': 'Set official labels for the four lots; then insert four numbers if they are lots (proposed)',
 'Q5a': 'Set official labels (map labels or table labels); aliases already accepted', 'Q9a': 'Name the three outlines (A361, A362, third); insert numbers if lots', 'Q9b': 'Record section and ledger names of the four lots; number them in their section\'s pass',
 'Q11a': 'Add A-pass numbers for each strip that is a lot; name the unlabelled one', 'Q11b': 'Add one A-pass number if 204A is a lot', 'Q12': 'Label the lot; add one number if a grave lot', 'Q7': 'Restore or keep removed the "Restroom" label; artwork only'}
rows = [[s['id'], s['title'], '', UPD[s['id']]] for s in ORDER]
for part, (lo, hi) in enumerate([(0, 11), (11, 22)]):
    sl = prs.slides.add_slide(BL); header(sl, 'Decision sheet (%d of 2)' % (part + 1), None)
    table(sl, 0.4, 1.0, 12.5, rows[lo:hi], ['Q', 'Decision', "Jon's answer", 'Update it triggers'], size=9, colw=[0.5, 3.9, 3.0, 5.1], rh=0.52)
prs.save(os.path.join(HERE, 'Cedar_Grove_Questions_for_Jon.pptx')); print('saved', len(prs.slides))
