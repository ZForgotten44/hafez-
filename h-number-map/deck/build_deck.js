const pptxgen = require('pptxgenjs');
const { applyTheme } = require('/root/.claude/skills/synced/cd4fa728-fc4c-4fd2-8ea8-1ef32822210d_caf5ed74-d9a0-43bd-a8ab-614d666e6bad/pptx/scripts/apply_theme.js');
const IMG = __dirname + '/img/';
const THEME = { name: 'Cedar Grove Atlas', headFontFace: 'Cambria', bodyFontFace: 'Calibri',
  colors: { dk1: '1A2130', lt1: 'FFFFFF', dk2: '0C2340', lt2: 'F2F4F7', accent1: '0C2340', accent2: 'B8892F', accent3: '2F6B46', accent4: 'C9892F', accent5: '566274', accent6: '8FA3B8', hlink: '3A5578', folHlink: '566274' } };
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'Cedar Grove H-Number Atlas: progress update';
const NAVY = '0C2340', GOLD = 'B8892F', GREEN = '2F6B46', AMBER = 'B87A1F', SLATE = '566274', LIGHT = 'F2F4F7', INK = '1A2130', RULE = 'DDE3EA';
pres.defineSlideMaster({ title: 'TITLE', background: { color: NAVY } });
pres.defineSlideMaster({ title: 'CONTENT', background: { color: 'FFFFFF' }, slideNumber: { x: 12.2, y: 7.05, w: 0.6, h: 0.3, fontSize: 10, color: SLATE, fontFace: 'Calibri', align: 'right' } });

const title = (s, t) => s.addText(t, { x: 0.6, y: 0.35, w: 12.1, h: 0.8, fontSize: 30, bold: true, color: NAVY, fontFace: 'Cambria', valign: 'middle', margin: 0, isTextBox: true, objectName: 'Title' });
const txt = (s, t, o) => s.addText(t, Object.assign({ fontFace: 'Calibri', fontSize: 14, color: INK, margin: 0, valign: 'top', isTextBox: true }, o));
const chip = (s, text, x, y, w, fill) => s.addText(text, { x, y, w, h: 0.32, fontSize: 12, bold: true, color: 'FFFFFF', fill: { color: fill }, align: 'center', valign: 'middle', fontFace: 'Calibri', margin: 0, isTextBox: true, objectName: 'Status ' + text });
const badge = (s, n, x, y) => s.addText(String(n), { x: x - 0.17, y: y - 0.17, w: 0.34, h: 0.34, shape: pres.shapes.OVAL, fill: { color: GOLD }, line: { color: 'FFFFFF', width: 1.5 }, color: 'FFFFFF', bold: true, fontSize: 13, align: 'center', valign: 'middle', margin: 0, fontFace: 'Calibri', objectName: 'Callout ' + n });
const legend = (s, items, x, y, w, pitch) => items.forEach((it, i) => { const yy = y + i * (pitch || 0.52);
  s.addText(String(it[0]), { x, y: yy + 0.07, w: 0.32, h: 0.32, shape: pres.shapes.OVAL, fill: { color: GOLD }, color: 'FFFFFF', bold: true, fontSize: 12, align: 'center', valign: 'middle', margin: 0, fontFace: 'Calibri' });
  txt(s, it[1], { x: x + 0.45, y: yy, w: w - 0.45, h: (pitch || 0.52) - 0.02, valign: 'middle' }); });
const shot = (s, file, x, y, w, h, name, alt) => s.addImage({ path: IMG + file, x, y, w, h, altText: alt || name, objectName: name, shadow: { type: 'outer', color: '000000', opacity: 0.18, blur: 8, offset: 2, angle: 90 } });
const dims = (file) => { const sz = require('child_process').execSync(`python3 -c "from PIL import Image;i=Image.open('${IMG}${file}');print(i.size[0],i.size[1])"`).toString().trim().split(' ').map(Number); return sz; };
const hAt = (file, w) => { const d = dims(file); return w * d[1] / d[0]; };

// 1 ------------------------------------------------------------------ cover
{ const s = pres.addSlide({ masterName: 'TITLE' });
  s.addText('Cedar Grove\nH-Number Atlas', { x: 0.7, y: 1.9, w: 6.2, h: 1.7, fontSize: 44, bold: true, color: 'FFFFFF', fontFace: 'Cambria', valign: 'top', margin: 0, isTextBox: true });
  s.addText('Map cleanup, H-number placement, and remaining records work', { x: 0.7, y: 3.75, w: 5.6, h: 1.0, fontSize: 20, color: 'CADCFC', fontFace: 'Calibri', valign: 'top', margin: 0, isTextBox: true });
  s.addText('Mahmoud Hafez  |  October 12, 2026', { x: 0.7, y: 6.4, w: 5.8, h: 0.4, fontSize: 14, color: 'CADCFC', fontFace: 'Calibri', margin: 0, isTextBox: true });
  s.addImage({ path: IMG + 'dense_new.png', x: 7.15, y: 1.75, w: 5.5, h: 5.5 * 640 / 1000, altText: 'Current map: H-numbers inside lot outlines', objectName: 'Cover screenshot' });
  s.addText('Current map: H-numbers inside their lot outlines', { x: 7.15, y: 5.4, w: 5.5, h: 0.3, fontSize: 12, color: 'CADCFC', fontFace: 'Calibri', margin: 0, isTextBox: true });
  s.addNotes('A progress snapshot as of October 12, 2026. It covers what changed in the map, how the numbers are produced, what the evidence supports, and what I need from cemetery staff.'); }

// 2 ------------------------------------------------------------------ overview
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'Annotations removed; roads and lot outlines kept');
  const W = 6.0, H = 6.0 * 630 / 1200, Y = 1.75, XL = 0.6, XR = 6.73, k = W / 1200;
  chip(s, 'BEFORE: previous site', XL, 1.35, 2.3, SLATE); chip(s, 'NOW: rebuilt map', XR, 1.35, 2.0, NAVY);
  txt(s, 'Same map bounds in both screenshots', { x: 9.0, y: 1.35, w: 3.7, h: 0.32, fontSize: 12, color: SLATE, align: 'right', valign: 'middle' });
  shot(s, 'overview_old.png', XL, Y, W, H, 'Before overview', 'Previous site, whole cemetery'); shot(s, 'overview_new.png', XR, Y, W, H, 'Now overview', 'Rebuilt map, whole cemetery');
  badge(s, 1, XL + 510 * k, Y + 220 * k); badge(s, 2, XL + 75 * k, Y + 160 * k); badge(s, 3, XR + 760 * k, Y + 400 * k);
  legend(s, [[1, 'Dark "SECTION" title blocks sat over the lots.'], [2, 'Legend and descriptive notes were part of the picture.']], 0.6, 5.1, 6.0);
  legend(s, [[3, 'Original roads and lot outlines retained, with stronger lines.']], 6.73, 5.1, 6.0);
  txt(s, 'The first version drew new numbers over the old labels. In the rebuilt map the old text is never drawn. The original annotations can be switched on from Layers.', { x: 6.73, y: 5.7, w: 6.0, h: 0.9, fontSize: 14, color: SLATE });
  s.addNotes('Both views cover the same bounds. The earlier overall map had section titles, a legend and descriptive notes baked in. They are text objects in the source drawing, so the rebuilt map does not draw them. I left roads, lot outlines and building footprints in. All 11,890 lot-outline segments of the source are in the base layer; I removed only the legend frame and its rule. Original text can be switched on from Layers.'); }

// 3 ------------------------------------------------------------------ dense
function closeup(t, oldF, newF, oldB, newB, leg1, leg2, note, caption, W, legY, pitch) {
  const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, t);
  const H = W * 640 / 1000, Y = 1.75, XL = 0.6, XR = 6.73, k = W / 1000;
  chip(s, 'BEFORE', XL, 1.35, 1.3, SLATE); chip(s, 'NOW', XR, 1.35, 1.0, NAVY);
  txt(s, caption, { x: 2.1, y: 1.35, w: 4.4, h: 0.32, fontSize: 12, color: SLATE, valign: 'middle' });
  shot(s, oldF, XL, Y, W, H, 'Before close-up', 'Previous site, close-up'); shot(s, newF, XR, Y, W, H, 'Now close-up', 'Rebuilt map, same lots and zoom');
  oldB.forEach(b => badge(s, b[0], XL + b[1] * k, Y + b[2] * k)); newB.forEach(b => badge(s, b[0], XR + b[1] * k, Y + b[2] * k));
  legend(s, leg1, 0.6, legY, 6.0, pitch); legend(s, leg2, 6.73, legY, 6.0, pitch); s.addNotes(note); return s; }
closeup('Confirmed H-numbers now fit inside their lot outlines', 'dense_old.png', 'dense_new.png', [[1, 310, 140], [2, 368, 330]], [[3, 575, 340], [4, 342, 215]],
  [[1, 'Old numbers still showed beneath the new ones.'], [2, 'Heavy outlines pushed numbers against the lot ends.']],
  [[3, 'One H-number per confirmed lot, inside its outline.'], [4, 'Legacy labels are not drawn in the rebuilt layer.']],
  'Same lots at the same zoom in both versions (around H001900 to H002270). In the first version the old labels were drawn as tiny shapes that could not be removed from the PDF, so I drew the new numbers on top of them. The rebuilt layer takes numbers from the source drawing as text and never draws the old ones. Lots I could not confirm (218 visible, 3 too small for a number) are handled on the next slides.',
  'Same lots, same zoom', 6.0, 5.85, 0.52);
closeup('Labels follow the lot orientation, even on curves', 'curved_old.png', 'curved_new.png', [[1, 630, 200], [2, 205, 235], [3, 98, 150]], [[4, 500, 150], [5, 180, 305]],
  [[1, 'A "SECTION" block sits over lots 2894 to 2909.'], [2, 'Numbers cross lot edges.'], [3, 'Black smudges mark erased old labels.']],
  [[4, 'Each number turns with its lot and stays inside it.'], [5, 'Narrow lots get smaller numbers: zoom in on screen. PDF detail pages print the smallest at 7.4 pt.']],
  'Same lots at the same zoom (the curved rows west of the main grid, H002891 to H003082). The new placement measures each number and fits it inside the outline with a margin. On the PDF detail pages the smallest number is 7.4 pt and 20 lots print under 8 pt; none are under 7 pt. Three lots (E 195A, E 195B, H 21) are too small for any legible number and are listed instead. An automatic check found no number touching a lot line in the tested renders, which shows readability, not that every number belongs to the right physical lot.',
  'Same lots, same zoom', 5.7, 5.5, 0.5);

// 5 ------------------------------------------------------------------ progress
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'Where the lots stand: placed, unresolved, or unplaced');
  const H = (t) => ({ text: t, options: { bold: true, color: 'FFFFFF', fill: { color: NAVY }, fontSize: 13, fontFace: 'Calibri', valign: 'middle' } });
  const c = (t, col, b, al) => ({ text: t, options: { color: col || INK, bold: !!b, fontSize: 13, fontFace: 'Calibri', valign: 'middle', align: al || 'left' } });
  const rows = [[H('Status'), H('Lots'), H('What it means')],
    [c('Placed, section corroborated', GREEN, true), c('2,709', GREEN, true, 'right'), c('A second, earlier reading of the drawing puts the label in the same legacy section.')],
    [c('Placed, section inferred', SLATE, true), c('394', SLATE, true, 'right'), c('Section inferred from neighbouring lots. Not yet reviewed one by one.')],
    [c('Visible lot, number unresolved', AMBER, true), c('218', AMBER, true, 'right'), c('An outline is on the drawing; the evidence does not support one H-number. Shaded, never numbered.')],
    [c('Decoder lot, no map position', AMBER, true), c('68', AMBER, true, 'right'), c('Known to the decoder; no label resolves to it. 34 of these match a drawn lot counted in the 218.')]];
  s.addTable(rows, { x: 0.6, y: 1.3, w: 12.1, colW: [3.5, 0.9, 7.7], border: { type: 'solid', color: RULE, pt: 0.75 }, fill: { color: 'FFFFFF' }, margin: [0.05, 0.1, 0.05, 0.1], rowH: [0.38, 0.5, 0.5, 0.5, 0.5], objectName: 'Status table' });
  const ch = (labels, values, colors, x, ttl, max) => s.addChart(pres.charts.BAR, [{ name: ttl, labels, values }], { x, y: 3.85, w: 5.95, h: 2.65, barDir: 'bar', chartColors: colors, showTitle: true, title: ttl, titleFontSize: 14, titleColor: INK, titleFontFace: '+mn-lt',
    showValue: true, dataLabelColor: INK, dataLabelFontSize: 12, dataLabelFontFace: '+mn-lt', dataLabelFormatCode: '#,##0', dataLabelPosition: 'outEnd', showLegend: false, catAxisLabelColor: INK, catAxisLabelFontSize: 12, catAxisLabelFontFace: '+mn-lt',
    valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, catAxisOrientation: 'maxMin', valAxisMaxVal: max });
  ch(['Corroborated by two readings', 'Inferred, 90-100% neighbours agree', 'Inferred, 60-89% agree', 'Inferred, label in one section only'], [2709, 327, 46, 21], [GREEN, SLATE, SLATE, SLATE], 0.55, 'The 3,103 placed lots, by evidence', 3600);
  ch(['Label not in this area\'s section', 'No area evidence (crypt rows)', 'Same label twice in a section', 'Number far from neighbours', 'Label unknown to decoder', 'Outline with no label'], [77, 72, 28, 20, 12, 9], [AMBER], 6.75, 'Why the 218 visible lots are unresolved', 100);
  txt(s, 'The 218 and 68 overlap, so they should not be added together. No burial records and no verified grave counts are in the shared database yet.', { x: 0.6, y: 6.55, w: 11.4, h: 0.45, fontSize: 12, color: SLATE, valign: 'middle' });
  s.addNotes('I left the 218 visible lots unresolved because the evidence did not support a single reliable assignment. They carry no number on the map; a decoder candidate, where one exists, appears only in the lot panel. The 394 inferred-section lots are drawn with their H-number but I have not reviewed them individually: 327 have 90 to 100 percent agreement among nearby lots, 46 have 60 to 89 percent, and 21 have labels that exist in only one legacy section. The earlier build reported 3,063 placed, 136 unplaced and 49 unmatched labels; the categories differ, so I did not turn them into a percentage. The shared database was checked on October 12, 2026: no grave records (one leftover test note on H000001).'); }

// 6 ------------------------------------------------------------------ pipeline
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'Numbers stored as text changed the method');
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.3, w: 12.1, h: 0.95, fill: { color: LIGHT }, line: { color: RULE, width: 0.75 }, objectName: 'Key change' });
  txt(s, [{ text: 'The key finding: ', options: { bold: true, color: NAVY } }, { text: 'the source drawing (an Illustrator .ai vector file) stores lot numbers as live text and lot outlines as separate lines. I rebuilt the pipeline around that, so numbers are read instead of recognized and nothing has to be covered up.', options: { color: INK } }], { x: 0.8, y: 1.38, w: 11.7, h: 0.8, fontSize: 15, valign: 'middle' });
  const box = (x, y, w, h, t, fill, col) => s.addText(t, { x, y, w, h, fontSize: 14, color: col, fill: { color: fill }, line: { color: fill === 'FFFFFF' ? RULE : fill, width: 0.75 }, align: 'center', valign: 'middle', fontFace: 'Calibri', margin: 0.08, objectName: 'Step: ' + t });
  const arrow = (x, y) => s.addShape(pres.shapes.RIGHT_ARROW, { x, y, w: 0.34, h: 0.28, fill: { color: GOLD }, line: { color: GOLD, width: 0.5 } });
  txt(s, 'Earlier build: the drawing held numbers as strokes', { x: 0.6, y: 2.45, w: 8, h: 0.32, fontSize: 14, bold: true, color: SLATE });
  const A = ['Overall map and nine section pages (PDF)', 'Recognize each drawn character', 'Align the pages to the overall map', 'Decode to H-number'];
  A.forEach((t, i) => { const x = 0.6 + i * 3.17; box(x, 2.85, 2.6, 0.95, t, 'FFFFFF', INK); if (i < 3) arrow(x + 2.63, 3.18); });
  txt(s, 'Current build: the drawing holds numbers as text', { x: 0.6, y: 4.2, w: 8, h: 0.32, fontSize: 14, bold: true, color: NAVY });
  const B = ['Read text and lines from the .ai file', 'Trace each lot outline', 'Match labels to lots; decode H-number', 'Check neighbours, duplicates, collisions', 'Render map, PDFs and site'];
  B.forEach((t, i) => { const x = 0.6 + i * 2.525; box(x, 4.6, 2.0, 0.95, t, NAVY, 'FFFFFF'); if (i < 4) arrow(x + 2.03, 4.93); });
  // cross-check connector: earlier recognition -> current check
  const xa = 0.6 + 3.17 + 1.3, xb = 0.6 + 3 * 2.525 + 1.0;
  s.addShape(pres.shapes.LINE, { x: xa, y: 3.8, w: 0, h: 0.28, line: { color: GOLD, width: 1.5, dashType: 'dash' } });
  s.addShape(pres.shapes.LINE, { x: xa, y: 4.08, w: xb - xa, h: 0, line: { color: GOLD, width: 1.5, dashType: 'dash' } });
  s.addShape(pres.shapes.LINE, { x: xb, y: 4.08, w: 0, h: 0.5, line: { color: GOLD, width: 1.5, dashType: 'dash', endArrowType: 'triangle' } });
  txt(s, 'earlier readings kept as an independent cross-check of each label\'s legacy section', { x: xa + 0.15, y: 3.8, w: 5.5, h: 0.26, fontSize: 12, italic: true, color: SLATE, valign: 'middle' });
  txt(s, 'Alignment: earlier pages were aligned to the overall map within 0.05 map units, and the earlier readings to the source drawing within about 0.1 (roughly 2% of a lot width). This transfers labels between drawings; it is not survey accuracy.', { x: 0.6, y: 5.85, w: 12.1, h: 0.7, fontSize: 12, color: SLATE });
  s.addNotes('Steps in the earlier build existed because the original PDF stores numbers as vector strokes, so they had to be recognized and the pages aligned. While rebuilding I found that the Illustrator file in the Ground Maps folder keeps numbers as live text and lot outlines as separate lines. That removed the need to recognize or cover anything. The earlier recognition results are still useful: they independently say which legacy section a label belongs to, and I use that as a cross-check. The 0.05 and 0.1 figures are map units on the drawing, not physical measurements.'); }

// 7 ------------------------------------------------------------------ tools
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'Tools, grouped by the job they did');
  const jobs = [
    ['Read the source drawings', 'Python 3, PyMuPDF', 'Pull every line and every text label out of the .ai file, and write the PDFs.'],
    ['Find and fit the lot shapes', 'OpenCV, NumPy, SciPy, Shapely', 'Trace each lot outline, match numbers to the right lot, and keep each number inside it.'],
    ['Decode H-numbers', 'Project decoder (s4decoder1.py)', 'Turns "Section F, lot 34" into H001914. It is the only source of H-numbers.'],
    ['Build the map and site', 'SVG, plain JavaScript, shared database', 'A sharp, zoomable map with lot panels. Records are stored so that only people with edit access can change them.'],
    ['Check the result', 'Playwright, Chromium', 'Take the screenshots and run the automatic placement checks in a real browser.'] ];
  const y0 = 1.35, rh = 0.84;
  txt(s, 'Job', { x: 0.7, y: y0, w: 3.2, h: 0.3, fontSize: 12, bold: true, color: SLATE, valign: 'middle' }); txt(s, 'Tools', { x: 4.1, y: y0, w: 3.4, h: 0.3, fontSize: 12, bold: true, color: SLATE, valign: 'middle' }); txt(s, 'Why it mattered', { x: 7.7, y: y0, w: 5, h: 0.3, fontSize: 12, bold: true, color: SLATE, valign: 'middle' });
  jobs.forEach((j, i) => { const y = y0 + 0.35 + i * rh;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 12.1, h: rh - 0.08, fill: { color: i % 2 ? 'FFFFFF' : LIGHT }, line: { color: RULE, width: 0.5 }, objectName: 'Row ' + (i + 1) });
    txt(s, j[0], { x: 0.7, y, w: 3.3, h: rh - 0.08, fontSize: 16, bold: true, color: NAVY, fontFace: 'Cambria', valign: 'middle' });
    txt(s, j[1], { x: 4.1, y, w: 3.4, h: rh - 0.08, fontSize: 14, valign: 'middle' });
    txt(s, j[2], { x: 7.7, y, w: 4.9, h: rh - 0.08, fontSize: 14, valign: 'middle' }); });
  txt(s, [{ text: 'Checks: ', options: { bold: true, color: NAVY } }, { text: 'no label-to-line collisions were detected in the tested screen and PDF renders. That supports readability; it does not prove a number belongs to the right physical lot.', options: { color: INK } }], { x: 0.6, y: 6.0, w: 12.1, h: 0.5, fontSize: 14 });
  txt(s, [{ text: 'Formats: ', options: { bold: true, color: NAVY } }, { text: '.ai (source) > JSON (working data) > SVG (map), PDF, CSV and Excel (.xlsx) (outputs).', options: { color: INK } }], { x: 0.6, y: 6.55, w: 12.1, h: 0.35, fontSize: 14 });
  s.addNotes('Everything is under h-number-map/pipeline2 in the repository, and run_all.py rebuilds the map, PDFs and lists from the source drawing in about six minutes. Automatic checks: all 3,103 numbers lie inside their lot with clearance, and in the browser and PDF pixel tests no number pixel touches a lot line. The first version also used template matching for digit recognition; that code is kept in h-number-map/pipeline.'); }

// 8 ------------------------------------------------------------------ workflow
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'One task from start to finish: find lot F 34 and open it');
  const WL = 5.5, WR = 5.6, XL = 0.6, XR = 7.1, Y = 1.85;
  chip(s, '1  Type a legacy label or H-number', XL, 1.4, 3.6, NAVY); chip(s, '2  Select it: the lot is zoomed, highlighted, described', XR, 1.4, 4.9, NAVY);
  shot(s, 'flow1_full.png', XL, Y, WL, hAt('flow1_full.png', WL), 'Search step', 'Typing F 34 lists lot H001914'); shot(s, 'flow2_full.png', XR, Y, WR, hAt('flow2_full.png', WR), 'Select step', 'Lot H001914 highlighted with its details panel');
  s.addShape(pres.shapes.RIGHT_ARROW, { x: 6.2, y: 3.0, w: 0.75, h: 0.5, fill: { color: GOLD }, line: { color: GOLD, width: 0.5 }, objectName: 'Workflow arrow' });
  chip(s, 'Working: tested in a browser', XL, 4.55, 2.9, GREEN);
  txt(s, 'Search takes an H-number, a legacy lot, or a recorded name. Name search is implemented but cannot be shown until burial records exist.', { x: XL, y: 4.95, w: 5.5, h: 0.9, fontSize: 14 });
  txt(s, [{ text: 'Open decision: ', options: { bold: true, color: NAVY } }, { text: 'the sidebar still groups lots by legacy section letter, labelled as cross-reference. I kept it because no approved area grouping exists yet.', options: { color: INK } }], { x: XL, y: 5.9, w: 5.5, h: 0.95, fontSize: 14 });
  txt(s, 'The panel stays beside the lot, so the selected lot is never covered. Back and Fit map return to earlier views.', { x: XR, y: 5.6, w: 5.6, h: 0.7, fontSize: 14 });
  s.addNotes('One lot is followed throughout: legacy label F 34 is H001914. The sidebar groups lots by legacy section letter with H-number ranges and is labelled as cross-reference; I did not invent a new numbered grouping.'); }

// 9 ------------------------------------------------------------------ records
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'Records, editing and exports: built, with live testing still to do');
  const Y = 1.8, xa = 0.6, wa = 2.55, xb = 3.5, wb = 3.3, xc = 7.15, wc = 4.6;
  chip(s, 'Editing: not tested live', xa, 1.4, 2.55, AMBER); chip(s, 'Viewing: working', xb, 1.4, 1.8, GREEN); chip(s, 'Files built; download untested', xc, 1.4, 2.8, AMBER);
  shot(s, 'panel_form.png', xa, Y, wa, hAt('panel_form.png', wa), 'Edit form', 'Edit form: grave count, one record, Save and Cancel');
  shot(s, 'panel_viewer.png', xb, Y, wb, hAt('panel_viewer.png', wb), 'Viewer panel', 'Lot panel as a viewer sees it');
  shot(s, 'export_dialog.png', xc, Y, wc, hAt('export_dialog.png', wc), 'Export dialog', 'Export dialog: PDF, Excel and CSV');
  txt(s, 'Each record is one burial in the lot. Grave position is optional text, marked verified or not. Fields start empty and say so.', { x: xb, y: 5.6, w: wb, h: 0.8, fontSize: 12 });
  txt(s, 'A standard viewer\'s write was refused in a service-level test. Editing is not yet tried with real editor accounts in the browser.', { x: xb, y: 6.3, w: wb, h: 0.65, fontSize: 12, color: SLATE });
  txt(s, 'PDF, CSV and Excel (.xlsx) files are generated. Downloading them from the hosted page, and the record import, still need testing.', { x: xc, y: 6.1, w: wc, h: 0.8, fontSize: 12 });
  s.addNotes('Status, plainly. The form and viewer screenshots come from a browser test with a stand-in sign-in and an empty database, so they show the real screens, not a live editor session. Separately, a write as a standard viewer was refused by the shared database rules. No burial data has been entered. PDF, CSV and Excel files are generated by the build; the Excel workbook was added this week. Downloading them from the hosted page and the CSV or Excel record import have not been tested with real accounts or data.'); }

// 10 ----------------------------------------------------------------- next
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'Next steps: who does what');
  const col = (x, head, items) => { s.addShape(pres.shapes.RECTANGLE, { x, y: 1.35, w: 3.9, h: 4.35, fill: { color: LIGHT }, line: { color: RULE, width: 0.5 }, objectName: head });
    txt(s, head, { x: x + 0.2, y: 1.5, w: 3.5, h: 0.4, fontSize: 17, bold: true, color: NAVY, fontFace: 'Cambria', valign: 'middle' });
    s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 8 } })), { x: x + 0.2, y: 2.05, w: 3.5, h: 3.6, fontSize: 16, color: INK, fontFace: 'Calibri', margin: 0, valign: 'top', isTextBox: true }); };
  col(0.6, 'My next development work', ['Spot-check the 394 inferred-section lots, weakest 46 first', 'Fix the exceptions I can: 9 unlabelled outlines, 3 lots too small for a number', 'Validate the record import and report matched and skipped rows', 'Test editing and downloads on the hosted page']);
  col(4.7, 'Needed from cemetery staff', ['A sample burial-record spreadsheet, even 20 rows', 'Any lot-capacity or grave-position records', 'Someone to rule on the numbering conflicts: B 373 to 380H, G lot 19, A 20H to 343H, B-side 395 to 414, crypt rows', 'A short session to test editing with real accounts']);
  col(8.8, 'To settle together', ['Area names to show instead of legacy section letters', 'Which resolved conflicts to accept', 'Logo and where the site is hosted']);
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 5.95, w: 12.1, h: 0.85, fill: { color: NAVY }, line: { color: NAVY, width: 0.5 }, objectName: 'Next milestone' });
  txt(s, [{ text: 'Next review: ', options: { bold: true, color: 'CADCFC' } }, { text: 'remaining map exceptions, a sample record import, and verified PDF and Excel downloads.', options: { color: 'FFFFFF' } }], { x: 0.85, y: 5.95, w: 11.6, h: 0.85, fontSize: 16, valign: 'middle' });
  s.addNotes('The numbering conflicts need someone who knows the original scheme, not more software. The map work, import validation and download testing can continue on my side in the meantime. The spreadsheet does not need to be complete for the first import test.'); }

(async () => { const f = __dirname + '/Cedar_Grove_H-Number_Atlas_Progress.pptx'; await pres.writeFile({ fileName: f }); await applyTheme(f, THEME); console.log('written'); })();
