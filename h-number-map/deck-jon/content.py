import sys, importlib.util, subprocess, os, collections
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
def _load(src, name):
    spec = importlib.util.spec_from_loader(name, loader=None); m = importlib.util.module_from_spec(spec); exec(compile(src, name, 'exec'), m.__dict__); return m
D_REV = _load(subprocess.check_output(['git', '-C', REPO, 'show', 'd990927:s4/s4decoder1.py']).decode(), 'rev')
D_NOW = _load(open(os.path.join(REPO, 's4', 's4decoder1.py')).read(), 'now')
D_WD = _load(open(os.path.join(REPO, 's4', 's4decoder1.py')).read().replace("M_EASTTIP_STATUS = 'active'", "M_EASTTIP_STATUS = 'withdrawn'"), 'wd')
D_V1 = _load(open(os.path.join(REPO, 's4', 's4decoder_v1.py')).read(), 'v1')
def H(d, s, l):
    r = d.h_lot(s, l); return r[1] if r and r[0] else '—'
def hn(d, s, l):
    r = d.h_lot(s, l); return r[0] if r and r[0] else None
NEED, DONE, RES = 'Needs a decision', 'Already corrected · needs confirmation', 'Resolved'
S = []   # slides
def add(**k): S.append(k)
M_ROUTE = ['55', '56', '57', '61', '62', '63', '58', '59', '60', '66', '67', '68', '69', '64', '65']
# ---------------------------------------------------------------- numbering decisions
add(id='Q1', cat='N', status=NEED, title='What happened to Section M lots 11, 12 and 16?', img='Q1',
    obs='Old Section M sheet: 11 and 12 form the column east of 14 and 15 (11 above 12); 16 stands directly below 15. 2022 drawing: no lot outlines at 1, 2 or 3; a Saint Joseph hexagon (4) stands where 11 and 12 were, and the parking features (5) lie just south-east. The burial workbook has no lot 11, 12 or 16.',
    key='Red 1-3 = M 11, 12, 16 (solid where drawn on the old sheet, dashed = approximate position copied from the old sheet). Purple 4-5 = features that exist only in 2022. Green A, B = M 14, M 15 (same lots on both maps).',
    q='For each lot: is it still recognized here, was it renumbered or relocated, or was it withdrawn?',
    ans=['M 11:  ☐ still recognized   ☐ renumbered to ______   ☐ withdrawn', 'M 12:  ☐ still recognized   ☐ renumbered to ______   ☐ withdrawn', 'M 16:  ☐ still recognized   ☐ renumbered to ______   ☐ withdrawn'],
    chg='H-numbers and downstream numbering. Kept: M 11/12/16 = H002601, H002602, H002605 (as now). Withdrawn: those three numbers disappear, every later M lot moves up 1-3 places and K, J, I, L 69-107 move up 3 (table). Proposed numbers only; nothing has been changed yet.',
    table=dict(head=['Lot', 'H now (kept)', 'H if withdrawn (proposed)', 'Lot', 'H now (kept)', 'H if withdrawn (proposed)'],
        rows=[[l, H(D_NOW, 'M', l), H(D_WD, 'M', l), l2, H(D_NOW, s2, l2), H(D_WD, s2, l2)] for (l, (s2, l2)) in zip(['M 11', 'M 12', 'M 14', 'M 15', 'M 16'], [('M', '18'), ('M', '279'), ('K', '1'), ('L', '69'), ('M', '14')])] if False else
        [['M 11', H(D_NOW, 'M', '11'), '— (withdrawn)', 'M 18', H(D_NOW, 'M', '18'), H(D_WD, 'M', '18')], ['M 12', H(D_NOW, 'M', '12'), '— (withdrawn)', 'M 279 (last M)', H(D_NOW, 'M', '279'), H(D_WD, 'M', '279')],
         ['M 14', H(D_NOW, 'M', '14'), H(D_WD, 'M', '14'), 'K 1', H(D_NOW, 'K', '1'), H(D_WD, 'K', '1')], ['M 15', H(D_NOW, 'M', '15'), H(D_WD, 'M', '15'), 'L 69', H(D_NOW, 'L', '69'), H(D_WD, 'L', '69')], ['M 16', H(D_NOW, 'M', '16'), '— (withdrawn)', '', '', '']]))
add(id='Q2', cat='N', status=DONE, title='Do M 56, 57, 62, 63, 68 and 69 continue the columns above them?', img='Q2',
    obs='2022 drawing: a second row of six lots sits under the columns 52-55, 58-61 and 64-67 (solid red). Old sheet: the same ground is blank apart from empty boxes that look like an older parking layout (dashed red = where the six would stand).',
    key='Red 1-6 = M 56, 57, 62, 63, 68, 69 (solid: drawn in 2022; dashed: approximate position on the old sheet). Green A, B, C = M 55, 61, 67, the bottom lot of each column on both maps.',
    q='Do 56 and 57 continue the column of 52-55 (likewise 62/63 under 58-61, 68/69 under 64-67), and were these six added after the old sheet?',
    ans=['☐ yes, columns run as drawn in 2022', '☐ no, the columns really run: ____________________', 'Added after old sheet?  ☐ yes   ☐ no   ☐ unknown'],
    chg='H-numbers within M only. The six are already numbered on the proposed route below. A "no" re-orders those 15 numbers inside M and nothing outside M moves.',
    table=dict(head=['Route step'] + ['M ' + l for l in M_ROUTE], rows=[['H now'] + [H(D_NOW, 'M', l)[1:] for l in M_ROUTE]]), tsmall=True)
add(id='Q3', cat='N', status=NEED, title='Are B 390A, 390B and 390C active lots, and where do they stand?', img='Q3',
    obs='Old sheet: three lots are stacked north of lot 390 (390A lowest, 390C highest). 2022 drawing: blank ground at that spot, next to the cottage polygon. Both maps draw 389A/389B and 388A/388B columns beside it.',
    key='Red 1-3 = B 390A, 390B, 390C (solid: drawn on the old sheet; dashed on 2022 = approximate position from the old map). Green A, B, C = B 390, 391, 389 (same lots on both maps).',
    q='Are 390A, 390B and 390C active lots at these places, withdrawn, or moved?',
    ans=['390A  ☐ active here  ☐ withdrawn  ☐ moved to ______', '390B  ☐ active here  ☐ withdrawn  ☐ moved to ______', '390C  ☐ active here  ☐ withdrawn  ☐ moved to ______'],
    chg='Map artwork and the lots\' status. The table already holds a number for each; withdrawing one leaves its number unused with no shift (no downstream change). Moving one changes only where its number is drawn.',
    table=dict(head=['B 391', 'B 390H', 'B 390', 'B 390A', 'B 390B', 'B 390C', 'B 389'], rows=[[H(D_NOW, 'B', l) for l in ('391', '390H', '390', '390A', '390B', '390C', '389')]]))
add(id='Q4a', cat='N', status=NEED, title='Were B 289 and 290 withdrawn, relocated, or are they still recognized?', img='Q4a',
    obs='Neither map draws a lot where 289 and 290 would continue the 281-288 column: the chapel entrance circle (3) stands there on both. The column resumes at 291. The numbering table has a free number for each (H000628, H000629) between 291 and 288.',
    key='Red 1-2 = where 289 and 290 would stand if the column continued; dashed on both maps because neither draws them. Purple 3 = chapel entrance circle, 4 = chapel. Green A, B = B 288, 291.',
    q='Were B 289 and 290 withdrawn, relocated, or are they still recognized at this place?',
    ans=['289  ☐ withdrawn  ☐ relocated to ______  ☐ recognized here', '290  ☐ withdrawn  ☐ relocated to ______  ☐ recognized here'],
    chg='Only whether H000629 and H000628 stay assigned. No lot after them moves either way. If relocated, the artwork moves; if withdrawn the two numbers stay unused (proposed).',
    table=dict(head=['B 291', 'B 290', 'B 289', 'B 288'], rows=[[H(D_NOW, 'B', l) for l in ('291', '290', '289', '288')]]))
add(id='Q5b', cat='N', status=DONE, title='Do the plain lots 20, 40, 60 … 300 need H-numbers?', img='Q5b',
    obs='Both drawings show a plain lot (2, 4) directly under each H lot (1, 3) with the same number: 40H over 40, 20H over 20. The review version of the table had no entry for these plain lots.',
    key='Red 1-4 = 40H, 40, 20H and 20 (solid on both maps). Plain 20 and 40 have been drawn since the first sheet.',
    q='Are the plain lots 20, 40, 60 … 300 real lots (each beside its H lot) that carry their own H-numbers?',
    ans=['☐ yes, they are lots and take H-numbers', '☐ no, they are not separate lots: ______________________'],
    chg='Already corrected: 40 … 360 added in v2, 20 added now. A "no" removes the numbers of these plain lots and moves later B lots back (the shift table lists every lot). Corrected numbers are in the table below.',
    table=dict(head=['B 40H', 'B 40', 'B 20H', 'B 20', 'B 19A'], rows=[['review ' + H(D_REV, 'B', '40H'), 'review ' + H(D_REV, 'B', '40'), 'review ' + H(D_REV, 'B', '20H'), 'review —', 'review ' + H(D_REV, 'B', '19A')], ['now ' + H(D_NOW, 'B', '40H'), 'now ' + H(D_NOW, 'B', '40'), 'now ' + H(D_NOW, 'B', '20H'), 'now ' + H(D_NOW, 'B', '20'), 'now ' + H(D_NOW, 'B', '19A')]]))
add(id='Q6', cat='N', status=NEED, title='Do the 18 row-start H lots in Section A exist, and where?', img='Q6',
    obs='Section A has 1H (4) drawn beside lot 1 and small H lots inside rows. Neither map draws a row-start H lot at the top of the columns for 20H, 39H, 58H … 343H; the numbering table has 18 route numbers for them.',
    key='Red 4 = 1H, drawn on both maps. Red dashed 1-3 = where 20H, 39H, 58H would stand if each column started like 1H (neither map draws them). Green A, B, C = A 20, 39, 58.',
    q='Do these 18 lots exist? What does the H mean in the ledger, and where are they?',
    ans=['☐ they exist at ______________________', '☐ never laid out', 'H means: ______________________'],
    chg='18 route numbers (H000087 … H000835). "Never laid out" leaves 18 unused numbers; no shift. If they exist the map gets 18 new outlines at the places Jon gives.',
    table=dict(head=['A 1H (drawn)', 'A 20H', 'A 39H', 'A 58H', 'A 77H', 'A 96H', 'A 115H', 'A 343H'], rows=[[H(D_NOW, 'A', l) for l in ('1H', '20H', '39H', '58H', '77H', '96H', '115H', '343H')]]))
add(id='Q8', cat='N', status=NEED, title='Where do the lots of the strip north of the oval belong in the numbering?', img='Q8',
    obs='On the old L sheet lots 1-13 stand inside the SECTION L boundary (1). Lots 14-19 are drawn in 2022 but blank on the old sheet (2, 3: first and last). Lot 21 is a hatched box in its own dash-dot rectangle (4). Section L has only 69-107 in the table.',
    key='Red 1 = lots 1-13 (drawn on both). Red dashed 2, 3 = lots 14 and 19 (blank on the old sheet: approximate position from 2022). Red 4 = lot 21. Green A = K 13. Each image is cut in two: top = west half, bottom = east half (cut at drawing x 737).',
    q='Are the strip lots 1-19 and 21 Section L lots, which are active, and do they number before L 69, after L 107 or outside the H-numbering?',
    ans=['1-13:  ☐ L lots, between M and K (as now)  ☐ other: ______', '14-19:  ☐ L lots, active  ☐ not lots  ☐ ______', '21:  ☐ L lot  ☐ not a lot  ☐ ______'],
    chg='H-numbers. L 1-13 now hold H002856-H002868 (inserted between M and K, moving K, J, I, L 69-107 by 13). If 14-19 and 21 are lots, seven more numbers are inserted after L 13 and K … L 107 move 7 further (proposed).',
    table=dict(head=['M 279', 'L 1', 'L 13', 'K 1', 'L 69 (review → now)'], rows=[[H(D_NOW, 'M', '279'), H(D_NOW, 'L', '1'), H(D_NOW, 'L', '13'), H(D_NOW, 'K', '1') + ' (review ' + H(D_REV, 'K', '1') + ')', H(D_NOW, 'L', '69') + ' (review ' + H(D_REV, 'L', '69') + ')']]))
add(id='Q10', cat='N', status=DONE, title='B 20 is a separate lot between 20H and 19A: confirm its place in the route', img='Q10',
    obs='Both drawings show four separate outlines in the top row of Section B: 20H (1), 20 (2), 19A (3) and 19. The review decoder gave 20H and 19A route places 1 and 2 and no place to 20, which has an outline of its own. Row 1 now runs 20H, 20, 19A, 19 … 1 by position on the drawing.',
    key='Red 1-3 = B 20H, B 20, B 19A (solid, drawn on both maps). Green A, B, C = B 19, 18 and 40, the neighbours to match.',
    q='Are 20H, 20 and 19A three separate lots, what is 19A, and does the route read 20H → 20 → 19A → 19?',
    ans=['☐ yes, three lots, route as shown', '☐ no, they are: ____________________', '19A is: ____________________'],
    chg='H-numbers. B 20 takes H000002 and the 20 lots 19A … 1 each move one place later (H000003-H000022). The last place of that row was unused, so nothing after it moves. Route order is established by the drawings only.',
    table=dict(head=['', 'B 20H', 'B 20', 'B 19A', 'B 19', 'B 18'], rows=[['review commit', H(D_REV, 'B', '20H'), '— (no number)', H(D_REV, 'B', '19A'), H(D_REV, 'B', '19'), H(D_REV, 'B', '18')], ['now', H(D_NOW, 'B', '20H'), H(D_NOW, 'B', '20'), H(D_NOW, 'B', '19A'), H(D_NOW, 'B', '19'), H(D_NOW, 'B', '18')]]))
add(id='Q13a', cat='N', status=DONE, title='Do plain lots 311, 322 and 333 exist in Section D?', img='Q13a',
    obs='Both drawings show a plain lot directly below each of the H lots 311H, 322H and 333H (1, 2, 3). The review table had keys for the H lots only.',
    key='Red 1-3 = plain D 311, 322, 333 (solid on both maps). Green A = D 311H, B = D 310.',
    q='Do plain 311, 322 and 333 exist as lots in Section D?',
    ans=['☐ yes, all three', '☐ no: ______________________'],
    chg='H-numbers in D, C and everything after. Each plain lot now takes the place after its H lot (H001521, H001564, H001607); all later route numbers moved up one at each.',
    table=dict(head=['D 311H', 'D 311', 'D 310', 'D 322', 'D 333'], rows=[['review ' + H(D_REV, 'D', '311H'), 'review —', 'review ' + H(D_REV, 'D', '310'), 'review —', 'review —'], ['now ' + H(D_NOW, 'D', '311H'), 'now ' + H(D_NOW, 'D', '311'), 'now ' + H(D_NOW, 'D', '310'), 'now ' + H(D_NOW, 'D', '322'), 'now ' + H(D_NOW, 'D', '333')]]))
add(id='Q13b', cat='N', status=DONE, title='Does the H lot printed 300H head column 300 (not 280)?', img='Q13b',
    obs='Both drawings print 300H (1) above plain 300 and 280H (2) above plain 280. In rows 2-15 the H lot printed NH stands 8 units from the next route lot; the lot the review table keyed as 280H is 16-19 units away. The review table had no 300H.',
    key='Red 1-2 = the lots printed 300H and 280H (solid on both maps), above the plain lots 300 and 280.',
    q='Does the H lot printed NH head column N, so that each H number belongs to the lot printed with it?',
    ans=['☐ yes, as drawn', '☐ no, the H lot of column N is printed: ______'],
    chg='The H-number of each printed row-head lot: the lot printed 280H moved from H001465 to H001432, 300H gets H001476. Already corrected so labels follow the printed lots; the set of route numbers is unchanged. "No" moves each head label one column back.',
    table=dict(head=['Printed lot', 'Review table', 'Now'], rows=[['D 280H', H(D_REV, 'D', '280H') + ' (the route place of column 300)', H(D_NOW, 'D', '280H')], ['D 300H', 'no key', H(D_NOW, 'D', '300H')], ['D 300', H(D_REV, 'D', '300'), H(D_NOW, 'D', '300')]]))
add(id='Q14', cat='N', status=DONE, title='Are the nine C H-lots (237H, 218H … 13H) numbered lots?', img='Q14',
    obs='Both drawings show an H lot directly above each plain lot (237H over 237, 218H over 218, 161H over 161), like the numbered H lots beside them. The review table had no entry for these nine.',
    key='Red 1-3 = C 237H, 218H, 161H (solid on both maps). The other six (214H, 157H, 89H, 70H, 28H, 13H) look the same elsewhere in C.',
    q='Are these H lots numbered lots like the other C H lots?',
    ans=['☐ yes, numbered lots', '☐ no: ______________________'],
    chg='H-numbers in C and later: each of the nine takes the place before its plain lot (e.g. C 237H = H001421). "No" removes nine numbers and moves everything after them back (all of C, F, E, G, H, M, K, J, I, L).',
    table=dict(head=['C 237H', 'C 237', 'C 218H', 'C 161H', 'C 157H', 'C 89H', 'C 70H', 'C 28H', 'C 13H'], rows=[['review —', 'review ' + H(D_REV, 'C', '237'), '—', '—', '—', '—', '—', '—', '—'], ['now ' + H(D_NOW, 'C', '237H')[1:], 'now ' + H(D_NOW, 'C', '237')[1:]] + [H(D_NOW, 'C', l)[1:] for l in ('218H', '161H', '157H', '89H', '70H', '28H', '13H')]]), tsmall=True)
add(id='Q15', cat='N', status=NEED, title='Where do B 395-414 belong in the numbering?', img='Q15',
    obs='A column of 20 outlines labelled 395 (south) to 414 (north) runs along the west edge of Section B, inside the B boundary on the old sheet, beside 355-372. The table has no entries for them. The photo-strip shows the column in three slices (south end first).',
    key='Red 1 = lot 395, red 2 = lot 414. Green A, B = B 355 and B 372 beside the column. Both lots drawn on both maps; nothing here is dashed.',
    q='Are 395-414 Section B lots, and do they come (a) at the end of the B/A pass, just before D 1U, or (b) at the start of B, before 20H?',
    ans=['☐ (a) after the last B/A lot, before D 1U', '☐ (b) before B 20H', '☐ (c) other: ______________', 'Are all 20 lots active?  ☐ yes  ☐ no: ______'],
    chg='H-numbers for the whole cemetery. Proposed (a): 395-414 = H000837-H000856 and everything from D 1U on moves up 20. Proposed (b): 395-414 = H000001-H000020 and every lot moves up 20. (a) adds 13 map units to the route, (b) adds 275: the drawing favours (a). Nothing is applied yet.',
    table=dict(head=['', 'B 395', 'B 414', 'D 1U', 'Route length added'], rows=[['now', 'no number', 'no number', H(D_NOW, 'D', '1U'), '—'], ['(a) proposed', 'H000837', 'H000856', 'H000857', '+13 units'], ['(b) proposed', 'H000001', 'H000020', 'D 1U stays H000837; B 20H becomes H000021', '+275 units']], colw=[1.3, 1.3, 1.3, 4.2, 1.6]))
add(id='Q16', cat='N', status=DONE, title='Were the lots 12, 31, 50 … ever recorded under the version 1 H-numbers?', img='Q16',
    obs='On both drawings B 12 stands between 13 and 11 in its level, not at the far end. Version 1 gave B 12 the number of the end of the level (H000022); the place between 13 and 11 had no label. Version 2 put B 12 between its neighbours and the same applies to the 19 lots 12, 31, 50 … 354.',
    key='Red 1 = B 12 (solid, drawn on both maps). Green A, B = B 13 and B 11 on both maps.',
    q='Were lots 12, 31, 50 … recorded anywhere under their version 1 H-IDs (H000022 for B 12, H000066 for B 31 …)? Which records?',
    ans=['☐ no record used the v1 H-IDs', '☐ yes, records: ______________________'],
    chg='Records only. If any burial or ownership record used v1 H-IDs, the crosswalk (crosswalk_v1_to_v2.csv) re-keys them. Maps and decoder are not affected by the answer.',
    table=dict(head=['', 'B 13', 'B 12', 'B 11'], rows=[['version 1', H(D_V1, 'B', '13'), H(D_V1, 'B', '12'), H(D_V1, 'B', '11')], ['review commit', H(D_REV, 'B', '13'), H(D_REV, 'B', '12'), H(D_REV, 'B', '11')], ['now (after B 20)', H(D_NOW, 'B', '13'), H(D_NOW, 'B', '12'), H(D_NOW, 'B', '11')]]))
add(id='Q17', cat='N', status=DONE, title='Is lot 293 in Section D, between 294 and 292?', img='Q17',
    obs='Both drawings print 293 between 294 and 292 in the same column. The review decoder listed 274 at this place (a typing slip: 274 is a lot elsewhere in D) and so gave the place to no printed label.',
    key='Red 1 = D 293 (solid on both maps). Green A, B = D 294 and D 292.',
    q='Is lot 293 in Section D, the one between 294 and 292 in this column?',
    ans=['☐ yes', '☐ no: ______________________'],
    chg='One lot\'s label (H-number unchanged by this answer). "Yes" keeps D 293 where it is; "no" frees the place.',
    table=dict(head=['', 'D 294', 'D 293', 'D 292'], rows=[['review commit', H(D_REV, 'D', '294'), H(D_REV, 'D', '293') + ' (read as 293 in v2)', H(D_REV, 'D', '292')], ['now', H(D_NOW, 'D', '294'), H(D_NOW, 'D', '293'), H(D_NOW, 'D', '292')]]))
# ---------------------------------------------------------------- label / location decisions
add(id='Q4b', cat='L', status=NEED, title='Which label is right for the four lots north of the chapel?', img='Q4b',
    obs='The old sheet prints B362, C344, C326 and B308 on these four outlines; the 2022 drawing prints 362H, 344H, 326H and 308H. Directly north of each stand 363, 345, 327 and 309. The numbering table has no key for any of the eight labels.',
    key='Red 1-4 = the four lots, west to east, same outlines on both maps (solid). Neighbours: directly north of 1-4 stand B 363, 345, 327, 309.',
    q='Which label is the ledger name of each lot (old sheet or 2022), and which section is it in?',
    ans=['1  ☐ B362  ☐ 362H  ☐ other ______', '2  ☐ C344  ☐ 344H  ☐ other ______', '3  ☐ C326  ☐ 326H  ☐ other ______', '4  ☐ B308  ☐ 308H  ☐ other ______'],
    chg='Official labels, and then H-numbers: the four lots have no number now. If they are lots, four numbers are inserted in route order (proposed, not assigned). Only the label changes on the map if they are already numbered.',
    table=dict(head=['Lot', 'old sheet label', '2022 label', 'decoder key', 'H now'], rows=[['1', 'B362', '362H', 'B 362H / C 362H', '—'], ['2', 'C344', '344H', 'B 344H / C 344', '— (C 344 is another lot: ' + H(D_NOW, 'C', '344') + ')'], ['3', 'C326', '326H', 'B 326H / C 326', '— (C 326 is another lot: ' + H(D_NOW, 'C', '326') + ')'], ['4', 'B308', '308H', 'B 308H', '—']]))
add(id='Q5a', cat='L', status=NEED, title='Which labels are the real names of the last four H lots in B: 318H … 372H or 320H … 380H?', img='Q5a',
    obs='Both drawings label the last four H lots of the north-edge row 318H, 336H, 354H and 372H. The numbering table expects 320H, 340H, 360H and 380H. Both maps show 19 H lots in the row and the table has 19, so no lot is missing: by position 318H = 320H, 336H = 340H, 354H = 360H, 372H = 380H.',
    key='Red 1-4 = 372H, 354H, 336H, 318H (solid on both maps). Green A = 300H, where the labels still agree with the table.',
    q='Which labels are the real lot names in the ledger: the map labels or the table labels?',
    ans=['☐ map labels (318H, 336H, 354H, 372H)', '☐ table labels (320H, 340H, 360H, 380H)', '☐ other: ______________________'],
    chg='Official labels only. H-numbers do not change; the decoder accepts both labels now (label_aliases.csv).',
    table=dict(head=['Printed (both maps)', '318H', '336H', '354H', '372H'], rows=[['Table key', '320H', '340H', '360H', '380H'], ['H-number', H(D_NOW, 'B', '318H'), H(D_NOW, 'B', '336H'), H(D_NOW, 'B', '354H'), H(D_NOW, 'B', '372H')]]))
add(id='Q9a', cat='L', status=NEED, title='Which of the three cells beside lots 403-361 is A361, and which is A362?', img='Q9',
    obs='Three outlines stand beside lots 403-361 at the chapel edge: one without a label (1), one labelled A362 (2) and one labelled A361 (3). The old sheet prints A362 inside the unlabelled outline of the 2022 drawing.',
    key='Red 1-3 = the three outlines, north to south (solid on both maps). Green A, B = B 362 and B 361.',
    q='Which cell is A361, which is A362, and what is the third cell?',
    ans=['1 is: ____________  2 is: ____________  3 is: ____________', '☐ A361 and A362 are lots  ☐ not lots: ____________'],
    chg='Labels and then possibly three H-numbers (none assigned today). Proposed numbers only after Jon names the lots and their section.',
    table=dict(head=['Outline', 'label on 2022', 'label on old sheet', 'decoder key', 'H now'], rows=[['1', '(none)', 'A362', '—', '—'], ['2', 'A362', '—', '—', '—'], ['3', 'A361', '—', '—', '—']]))
add(id='Q9b', cat='L', status=NEED, title='Ledger name and section of the four south-end lots 344H, 326H, 308H, 362H', img='Q4b',
    obs='The same four outlines as Q4b: old sheet C344, C326, B308, B362; 2022 344H, 326H, 308H, 362H. This slide asks only for the ledger entries (section and name); Q4b asks which printed label is right.',
    key='Red 1-4 = 362H, 344H, 326H, 308H on the 2022 drawing (B362, C344, C326, B308 on the old sheet).',
    q='What are the ledger names and sections of these four lots (B/C ledger entries for 361, 362, 308, 326, 344)?',
    ans=['1: section ____ name ____', '2: section ____ name ____', '3: section ____ name ____', '4: section ____ name ____'],
    chg='Section assignment, label and H-numbers: a lot in Section C would be numbered in the C pass, a lot in B in the B/A pass (every later number moves by one for each inserted lot).',
    table=dict(head=['Lot', 'old sheet', '2022', 'H now'], rows=[['1', 'B362', '362H', '—'], ['2', 'C344', '344H', '—'], ['3', 'C326', '326H', '—'], ['4', 'B308', '308H', '—']]))
add(id='Q11a', cat='L', status=NEED, title='Do the narrow A-suffix strips 312A, 293A and 291A exist, and what is the unlabelled one?', img='Q11a',
    obs='Narrow strip lots 312A (1), 293A (2) and 291A (4) lie in the aisle columns of Section A, with an unlabelled strip (3) between 293A and 291A. The numbering table has no A-suffix keys in Section A.',
    key='Red 1-4 = 312A, 293A, the unlabelled strip, 291A (solid on both maps). Green A, B, C = A 312, 293, 291.',
    q='Do these strips exist as lots, is the unlabelled one 292A, and are they numbered?',
    ans=['312A  ☐ lot  ☐ not a lot', '293A  ☐ lot  ☐ not a lot', 'unlabelled  ☐ 292A  ☐ other ______  ☐ not a lot', '291A  ☐ lot  ☐ not a lot'],
    chg='H-numbers in A (and everything after): each strip that is a lot adds one number in the A pass; none is assigned today (proposed only after the answer).',
    table=dict(head=['Strip', 'decoder key', 'H now'], rows=[['312A', 'none', '—'], ['293A', 'none', '—'], ['unlabelled (292A?)', 'none', '—'], ['291A', 'none', '—']]))
add(id='Q11b', cat='L', status=NEED, title='Is 204A a lot, and is it numbered?', img='Q11b',
    obs='A narrow strip labelled 204A lies in an aisle column of Section A beside 204 and 203H on both maps. The table has no A-suffix key.',
    key='Red 1 = 204A (solid on both maps). Green A, B = A 204 and A 203H.',
    q='Does 204A exist as a lot, and is it numbered?',
    ans=['☐ lot, numbered', '☐ lot, not numbered', '☐ not a lot'],
    chg='One number in the A pass if it is a lot (later numbers move one place); none is assigned today.',
    table=dict(head=['Strip', 'decoder key', 'H now'], rows=[['204A', 'none', '—']]))
add(id='Q12', cat='L', status=NEED, title='What is the narrow unlabelled lot between G 58 and F 210?', img='Q12',
    obs='A narrow outline with no label stands between G 58 and the F margin lot 210. It is unlabelled on both the old sheet and the 2022 drawing.',
    key='Red 1 = the unlabelled lot (solid on both maps). Green A, B = G 58 and F 210.',
    q='What is this lot called (F margin 211, a G lot, something else), and is it a grave lot?',
    ans=['☐ F margin 211', '☐ a G lot: ______', '☐ other: ______', 'Grave lot?  ☐ yes  ☐ no'],
    chg='Label and, if it is a grave lot, one H-number inserted in route order (proposed, not assigned). Otherwise only the map artwork.',
    table=dict(head=['Neighbour', 'H now'], rows=[['G 58', H(D_NOW, 'G', '58')], ['F 210', H(D_NOW, 'F', '210')]]))
# ---------------------------------------------------------------- artwork only
add(id='Q7', cat='A', status=DONE, title='Is the hatched building the maintenance building, and is the small square the restroom?', img='Q7',
    obs='The old overall sheet has two leaders: MAINTENANCE BUILDING ends at the hatched box (1) and RESTROOM ends at a small square inside the oval (2). An earlier overview put "Restroom" on the hatched building; that label was removed. The 2022 drawing shows the hatched building (1), the accessible-parking symbol (3) and a small symbol (2) near the drive, and names only the maintenance building and the cottage.',
    key='Red 1 = hatched building, red 2 = the small square at the RESTROOM leader end (approximate match on 2022: the nearest small object), purple 3 = accessible-parking symbol (2022 only). The old overall sheet is a separate drawing, not registered to the 2022 map, so the scales differ.',
    q='Does the old sheet read correctly: hatched building = maintenance building, small square in the oval = restroom? What is object 2 on the ground?',
    ans=['1  ☐ maintenance building  ☐ other: ______', '2  ☐ restroom  ☐ storage  ☐ other: ______'],
    chg='Map artwork only. A "Restroom" label would go on object 2, not on the hatched building; the label is off the maps until Jon answers. No H-number depends on it.',
    table=None)
