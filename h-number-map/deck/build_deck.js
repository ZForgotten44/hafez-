const pptxgen = require('pptxgenjs');
const { applyTheme } = require('/root/.claude/skills/synced/cd4fa728-fc4c-4fd2-8ea8-1ef32822210d_caf5ed74-d9a0-43bd-a8ab-614d666e6bad/pptx/scripts/apply_theme.js');
const IMG = __dirname + '/img/';
const THEME = { name: 'Cedar Grove Atlas', headFontFace: 'Cambria', bodyFontFace: 'Calibri',
  colors: { dk1: '1A2130', lt1: 'FFFFFF', dk2: '0C2340', lt2: 'F2F4F7', accent1: '0C2340', accent2: 'B8892F', accent3: '2F6B46', accent4: 'C9892F', accent5: '566274', accent6: '8FA3B8', hlink: '3A5578', folHlink: '566274' } };
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';            // 13.33 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'Cedar Grove H-Number Atlas: progress report';
const C = pres.SchemeColor;
const NAVY = '0C2340', GOLD = 'B8892F', GREEN = '2F6B46', AMBER = 'C9892F', SLATE = '566274', LIGHT = 'F2F4F7', INK = '1A2130';

pres.defineSlideMaster({ title: 'TITLE', background: { color: NAVY }, objects: [], slideNumber: undefined });
pres.defineSlideMaster({ title: 'CONTENT', background: { color: 'FFFFFF' },
  objects: [
    { text: { text: 'Cedar Grove Cemetery  |  H-Number Atlas progress report', options: { x: 0.6, y: 7.05, w: 7, h: 0.3, fontSize: 10, color: SLATE, fontFace: 'Calibri', margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.05, w: 0.6, h: 0.3, fontSize: 10, color: SLATE, fontFace: 'Calibri', align: 'right' },
  placeholders: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.35, w: 12.1, h: 0.8, fontSize: 32, bold: true, color: NAVY, fontFace: 'Cambria', valign: 'middle', margin: 0 }, text: '' } }] });

function title(s, t) { s.addText(t, { x: 0.6, y: 0.35, w: 12.1, h: 0.8, fontSize: 30, bold: true, color: NAVY, fontFace: 'Cambria', valign: 'middle', margin: 0, isTextBox: true, objectName: 'Title' }); }
function chip(s, text, x, y, w, fill, color) { s.addText(text, { x, y, w, h: 0.32, fontSize: 12, bold: true, color: color || 'FFFFFF', fill: { color: fill }, align: 'center', valign: 'middle', fontFace: 'Calibri', margin: 0, isTextBox: true, objectName: 'Chip ' + text }); }
function badge(s, n, x, y) { s.addText(String(n), { x: x - 0.17, y: y - 0.17, w: 0.34, h: 0.34, shape: pres.shapes.OVAL, fill: { color: GOLD }, line: { color: 'FFFFFF', width: 1.5 }, color: 'FFFFFF', bold: true, fontSize: 13, align: 'center', valign: 'middle', margin: 0, fontFace: 'Calibri', objectName: 'Callout ' + n }); }
function legend(s, items, x, y, w) { // items: [n, text]
  items.forEach((it, i) => { const yy = y + i * 0.58;
    s.addText(String(it[0]), { x, y: yy + 0.04, w: 0.32, h: 0.32, shape: pres.shapes.OVAL, fill: { color: GOLD }, color: 'FFFFFF', bold: true, fontSize: 12, align: 'center', valign: 'middle', margin: 0, fontFace: 'Calibri' });
    s.addText(it[1], { x: x + 0.45, y: yy, w: w - 0.45, h: 0.5, fontSize: 14, color: INK, fontFace: 'Calibri', valign: 'middle', margin: 0, isTextBox: true }); }); }
function shot(s, file, x, y, w, h, name, alt) { s.addImage({ path: IMG + file, x, y, w, h, altText: alt || name, objectName: name, shadow: { type: 'outer', color: '000000', opacity: 0.18, blur: 8, offset: 2, angle: 90 } }); }

// ---------------------------------------------------------------- 1 title
{ const s = pres.addSlide({ masterName: 'TITLE' });
  s.addText('Cedar Grove H-Number Atlas', { x: 0.7, y: 1.7, w: 6.4, h: 1.7, fontSize: 44, bold: true, color: 'FFFFFF', fontFace: 'Cambria', valign: 'top', margin: 0, isTextBox: true });
  s.addText('Progress report: the map, the numbers behind it, and what comes next', { x: 0.7, y: 3.55, w: 5.9, h: 1.2, fontSize: 20, color: 'CADCFC', fontFace: 'Calibri', valign: 'top', margin: 0, isTextBox: true });
  s.addText('University of Notre Dame, Cedar Grove Cemetery  |  October 2026', { x: 0.7, y: 6.5, w: 6.4, h: 0.4, fontSize: 14, color: 'CADCFC', fontFace: 'Calibri', margin: 0, isTextBox: true });
  s.addImage({ path: IMG + 'zoom_curved_new.png', x: 7.15, y: 1.3, w: 5.5, h: 3.52, altText: 'Current map: curved lots with centered H-numbers', objectName: 'Hero screenshot' });
  s.addText('Current map, curved lot rows (H002891 to H003082)', { x: 7.15, y: 4.9, w: 5.5, h: 0.3, fontSize: 11, color: 'CADCFC', fontFace: 'Calibri', margin: 0, isTextBox: true });
  s.addNotes('Purpose of this deck: show what changed in the H-number map, how it is built, what is verified, and what needs decisions or information from cemetery staff. All screenshots are taken from the previous and current versions of the site.'); }

// ---------------------------------------------------------------- 2 overview before / after
{ const s = pres.addSlide({ masterName: 'CONTENT' });
  title(s, 'The whole map is cleaner and easier to read');
  const W = 6.0, H = 6.0 * 860 / 1440, Y = 1.7, XL = 0.6, XR = 6.73;
  chip(s, 'BEFORE: previous site', XL, 1.3, 2.3, SLATE); chip(s, 'NOW: current site', XR, 1.3, 2.0, NAVY);
  shot(s, 'app_overview_old.png', XL, Y, W, H, 'Before overview', 'Previous site, full cemetery view');
  shot(s, 'app_overview_new.png', XR, Y, W, H, 'Now overview', 'Current site, full cemetery view');
  const k = W / 1440;
  badge(s, 1, XL + 750 * k, Y + 343 * k); badge(s, 2, XL + 420 * k, Y + 700 * k);
  badge(s, 3, XR + 1000 * k, Y + 350 * k); badge(s, 4, XR + 300 * k, Y + 262 * k);
  legend(s, [[1, 'Dark "SECTION" title blocks covered lots. They are gone.'], [2, 'Legend, parking and office notes are gone from the default map.']], 0.6, 5.35, 6.0);
  legend(s, [[3, 'Roads, buildings and every lot outline are kept, in lighter lines.'], [4, 'Search, areas with H-number ranges, and a list of lots to review.']], 6.73, 5.35, 6.0);
  s.addNotes('Same window size, full cemetery. The old overall map had section titles, the mausoleum legend and descriptive notes baked in. They are text in the CAD source, so the new map simply does not draw them. The original text can be switched on from Layers.'); }

// ---------------------------------------------------------------- 3 dense close-up
function closeup(title0, oldF, newF, oldB, newB, leg1, leg2, note, caption) {
  const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, title0);
  const W = 6.0, H = 6.0 * 640 / 1000, Y = 1.7, XL = 0.6, XR = 6.73, k = W / 1000;
  chip(s, 'BEFORE', XL, 1.3, 1.3, SLATE); chip(s, 'NOW', XR, 1.3, 1.0, NAVY);
  s.addText(caption, { x: 2.05, y: 1.3, w: 4.5, h: 0.32, fontSize: 12, color: SLATE, fontFace: 'Calibri', valign: 'middle', margin: 0, isTextBox: true });
  shot(s, oldF, XL, Y, W, H, 'Before close-up', 'Previous site, close-up'); shot(s, newF, XR, Y, W, H, 'Now close-up', 'Current site, same area and zoom');
  oldB.forEach(b => badge(s, b[0], XL + b[1] * k, Y + b[2] * k)); newB.forEach(b => badge(s, b[0], XR + b[1] * k, Y + b[2] * k));
  legend(s, leg1, 0.6, 5.65, 6.0); legend(s, leg2, 6.73, 5.65, 6.0); s.addNotes(note); return s; }
closeup('Each lot shows one number, centered inside it', 'zoom_dense_old.png', 'zoom_dense_new.png',
  [[1, 310, 140], [2, 368, 330]], [[3, 575, 340], [4, 342, 215]],
  [[1, 'Old numbers still show underneath the new ones.'], [2, 'Heavy outlines crowd the numbers against the lot ends.']],
  [[3, 'One H-number per lot, centered, with clear space around it.'], [4, 'Thin outlines; no old numbers anywhere.']],
  'Same map area and zoom in both versions (about H001900 to H002270). In the previous version the old lot labels were drawn as tiny shapes and could not be removed from the PDF, so the new numbers were drawn on top of them. The new build never draws them.',
  'Same area and zoom, east side of the main grid');
closeup('Curved and angled lots keep their numbers inside', 'zoom_curved_old.png', 'zoom_curved_new.png',
  [[1, 630, 200], [2, 205, 235], [3, 98, 150]], [[4, 500, 150], [5, 180, 305]],
  [[1, 'A "SECTION" block sits over lots 2894 to 2909.'], [2, 'Numbers run across lot edges; black smudges are erased old labels.']],
  [[4, 'Each number turns with its lot and stays fully inside it.'], [5, 'Narrow lots get a smaller number, never a clipped one.']],
  'Same area and zoom (the curved rows west of the main grid, H002891 to H003082). The new placement measures each number and fits it inside the lot outline with a margin. It was checked automatically: none of 773,021 number pixels touch a lot line.',
  'Same area and zoom, curved rows');

// ---------------------------------------------------------------- 5 progress
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'Where things stand: what is mapped, unmatched, and still missing');
  const cols = [{ x: 0.6, w: 3.7, head: 'On the map', color: GREEN }, { x: 4.55, w: 4.95, head: 'Unmatched', color: AMBER }, { x: 9.75, w: 2.98, head: 'Information still missing', color: SLATE }];
  cols.forEach(c => s.addText(c.head, { x: c.x, y: 1.3, w: c.w, h: 0.4, fontSize: 18, bold: true, color: c.color, fontFace: 'Cambria', margin: 0, isTextBox: true }));
  // column 1
  s.addText('3,103', { x: 0.6, y: 1.75, w: 3.7, h: 0.9, fontSize: 54, bold: true, color: GREEN, fontFace: 'Cambria', margin: 0, isTextBox: true });
  s.addText('lots verified: drawn outline, H-number and legacy label all agree', { x: 0.6, y: 2.65, w: 3.7, h: 0.7, fontSize: 14, color: INK, fontFace: 'Calibri', margin: 0, valign: 'top', isTextBox: true });
  s.addChart(pres.charts.BAR, [{ name: 'Verified lots', labels: ['Section confirmed by two readings', 'Section inferred from neighbours'], values: [2709, 394] }],
    { x: 0.5, y: 3.5, w: 3.9, h: 2.4, barDir: 'bar', chartColors: [GREEN], showTitle: true, title: 'How the 3,103 were confirmed', titleFontSize: 14, titleColor: INK, titleFontFace: '+mn-lt',
      showValue: true, dataLabelColor: INK, dataLabelFontSize: 12, dataLabelFontFace: '+mn-lt', dataLabelFormatCode: '#,##0', dataLabelPosition: 'outEnd', showLegend: false,
      catAxisLabelColor: INK, catAxisLabelFontSize: 11, catAxisLabelFontFace: '+mn-lt', valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, catAxisOrientation: 'maxMin', valAxisMaxVal: 3300 });
  // column 2
  s.addText('218', { x: 4.55, y: 1.75, w: 1.9, h: 0.9, fontSize: 54, bold: true, color: AMBER, fontFace: 'Cambria', margin: 0, isTextBox: true });
  s.addText('visible lots whose number is unresolved', { x: 4.55, y: 2.65, w: 2.3, h: 0.7, fontSize: 14, color: INK, fontFace: 'Calibri', margin: 0, valign: 'top', isTextBox: true });
  s.addText('68', { x: 7.2, y: 1.75, w: 1.5, h: 0.9, fontSize: 54, bold: true, color: AMBER, fontFace: 'Cambria', margin: 0, isTextBox: true });
  s.addText('decoder lots with no map position', { x: 7.2, y: 2.65, w: 2.3, h: 0.7, fontSize: 14, color: INK, fontFace: 'Calibri', margin: 0, valign: 'top', isTextBox: true });
  s.addChart(pres.charts.BAR, [{ name: 'Visible lots', labels: ['Label not in this area\'s section', 'No area evidence (crypt rows)', 'Same label twice in a section', 'Number far from neighbours', 'Label unknown to decoder', 'Outline with no label'], values: [77, 72, 28, 20, 12, 9] }],
    { x: 4.45, y: 3.5, w: 5.1, h: 2.9, barDir: 'bar', chartColors: [AMBER], showTitle: true, title: 'Why the 218 are unresolved', titleFontSize: 14, titleColor: INK, titleFontFace: '+mn-lt',
      showValue: true, dataLabelColor: INK, dataLabelFontSize: 12, dataLabelFontFace: '+mn-lt', dataLabelPosition: 'outEnd', showLegend: false,
      catAxisLabelColor: INK, catAxisLabelFontSize: 11, catAxisLabelFontFace: '+mn-lt', valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, catAxisOrientation: 'maxMin', valAxisMaxVal: 95 });
  // column 3
  s.addText([{ text: '0', options: { fontSize: 54, bold: true, color: SLATE, fontFace: 'Cambria', breakLine: true } }, { text: 'burial records entered so far', options: { fontSize: 14, color: INK, fontFace: 'Calibri' } }], { x: 9.75, y: 1.75, w: 2.98, h: 1.6, margin: 0, valign: 'top', isTextBox: true });
  s.addText([{ text: '0', options: { fontSize: 54, bold: true, color: SLATE, fontFace: 'Cambria', breakLine: true } }, { text: 'lots with a verified grave count', options: { fontSize: 14, color: INK, fontFace: 'Calibri' } }], { x: 9.75, y: 3.5, w: 2.98, h: 1.6, margin: 0, valign: 'top', isTextBox: true });
  s.addText('Unresolved lots are shaded, never numbered by guesswork. A candidate H-number appears only in the lot panel.', { x: 9.75, y: 5.2, w: 2.98, h: 1.2, fontSize: 12, color: SLATE, fontFace: 'Calibri', margin: 0, valign: 'top', isTextBox: true });
  s.addText('Previous build, for reference (project figures): 3,063 lots placed, 136 unplaced entries listed, 49 unmatched labels. The categories are not identical, so the counts are shown side by side, not as a percentage.', { x: 0.6, y: 6.5, w: 12.1, h: 0.45, fontSize: 12, color: SLATE, fontFace: 'Calibri', margin: 0, valign: 'middle', isTextBox: true });
  s.addNotes('All counts come from the current build (pipeline2/classify.py output). Verified means a drawn outline, a decoded H-number and a section confirmed either by an independent earlier reading (2,709) or by surrounding lots (394). The 218 unresolved visible lots and the 68 decoder lots with no position are listed in unresolved_locations.csv. No grave counts or burial records have been entered yet.'); }

// ---------------------------------------------------------------- 6 pipeline
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'How the map is built, and why each step exists');
  const steps = [
    ['1', 'Original drawings', 'Two PDFs: an overall map and nine section pages. Lot numbers are drawn as tiny shapes, not text.', 'Now: the CAD file holds real text, so numbers are read directly.'],
    ['2', 'Glyph recognition', 'Software matched each drawn digit against templates for 0 to 9, A, B and H.', 'Now: kept only as an independent cross-check.'],
    ['3', 'Coordinate registration', 'Section pages were lined up on the overall map (error under 0.05 map units).', 'Now: old readings are aligned to the CAD file (0.1 unit).'],
    ['4', 'H-number decoding', 'The Python decoder turns "Section B, lot 20H" into H000001. It is the only source of H-numbers.', 'Now: unchanged.'],
    ['5', 'SVG rendering', 'The map is drawn as scalable shapes, so it stays sharp at any zoom and prints cleanly.', 'Now: each number is measured and fitted inside its lot.'],
    ['6', 'Site and PDFs', 'The interactive site and the printable PDFs are generated from the same data.', 'Now: rebuilt, with lot panels and review states.'] ];
  const cw = 3.75, ch = 2.45, gx = 0.425, gy = 0.3, x0 = 0.6, y0 = 1.45;
  steps.forEach((st, i) => { const col = i % 3, row = Math.floor(i / 3), x = x0 + col * (cw + gx), y = y0 + row * (ch + gy);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: cw, h: ch, fill: { color: LIGHT }, line: { color: 'DDE3EA', width: 0.75 }, objectName: 'Step card ' + st[0] });
    s.addText(st[0], { x: x + 0.2, y: y + 0.2, w: 0.42, h: 0.42, shape: pres.shapes.OVAL, fill: { color: NAVY }, color: 'FFFFFF', bold: true, fontSize: 14, align: 'center', valign: 'middle', margin: 0, fontFace: 'Calibri' });
    s.addText(st[1], { x: x + 0.75, y: y + 0.2, w: cw - 0.95, h: 0.42, fontSize: 17, bold: true, color: NAVY, fontFace: 'Cambria', valign: 'middle', margin: 0, isTextBox: true });
    s.addText(st[2], { x: x + 0.2, y: y + 0.75, w: cw - 0.4, h: 0.95, fontSize: 14, color: INK, fontFace: 'Calibri', valign: 'top', margin: 0, isTextBox: true });
    s.addText(st[3], { x: x + 0.2, y: y + 1.72, w: cw - 0.4, h: 0.6, fontSize: 13, italic: true, color: SLATE, fontFace: 'Calibri', valign: 'top', margin: 0, isTextBox: true });
    if (col < 2) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + cw + 0.04, y: y + ch / 2 - 0.15, w: 0.35, h: 0.3, fill: { color: GOLD }, line: { color: GOLD, width: 0.5 } }); });
  s.addNotes('Steps 1 to 3 existed because the original PDF stores numbers as vector strokes. That is why the first version needed shape recognition and page alignment, and why its numbers could not be separated from the old labels. While rebuilding, the CAD file in the Ground Maps folder turned out to keep numbers as text and lot outlines as lines. That removed the need for recognition and covering-up. The older recognition results are still used as an independent check of which legacy section a label belongs to.'); }

// ---------------------------------------------------------------- 7 tools
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'Tools and technical work, in plain terms');
  const tools = [
    ['Python 3', 'Runs the whole build, from the drawing to the finished site, with one command.'],
    ['PyMuPDF', 'Reads the lines and text out of the drawing, and writes the PDFs.'],
    ['OpenCV, NumPy, SciPy', 'Find each lot\'s outline and match positions between the two drawings.'],
    ['Shapely', 'Geometry maths that keeps every number inside its own lot.'],
    ['s4decoder1.py', 'The decoder: legacy lot label in, H-number out.'],
    ['SVG and plain JavaScript', 'The interactive map. Stays sharp when zoomed and needs no add-ons.'],
    ['Playwright and Chromium', 'Take the screenshots and run the automatic checks in a real browser.'],
    ['Shared database (Artifact)', 'Stores grave records. Only people with edit access can write.'] ];
  const cw = 2.85, ch = 1.95, gx = 0.233, gy = 0.25, x0 = 0.6, y0 = 1.45;
  tools.forEach((t, i) => { const col = i % 4, row = Math.floor(i / 4), x = x0 + col * (cw + gx), y = y0 + row * (ch + gy);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: cw, h: ch, fill: { color: LIGHT }, line: { color: 'DDE3EA', width: 0.75 }, objectName: 'Tool card ' + (i + 1) });
    s.addText(t[0], { x: x + 0.2, y: y + 0.15, w: cw - 0.4, h: 0.5, fontSize: 16, bold: true, color: NAVY, fontFace: 'Cambria', valign: 'middle', margin: 0, isTextBox: true });
    s.addText(t[1], { x: x + 0.2, y: y + 0.7, w: cw - 0.4, h: 1.15, fontSize: 14, color: INK, fontFace: 'Calibri', valign: 'top', margin: 0, isTextBox: true }); });
  s.addText([{ text: 'Data formats: ', options: { bold: true, color: NAVY } }, { text: '.ai / PDF (source drawing)  >  JSON (working data)  >  SVG (map), PDF (print), CSV (lists and imports). Excel (.xlsx) import is built but not yet tested.', options: { color: INK } }],
    { x: 0.6, y: 5.85, w: 12.1, h: 0.45, fontSize: 14, fontFace: 'Calibri', margin: 0, valign: 'middle', isTextBox: true });
  s.addText([{ text: 'Automatic checks: ', options: { bold: true, color: NAVY } }, { text: 'every number lies inside its lot (3,103 of 3,103); 0 of 773,021 number pixels touch a lot line on screen, and 0 of 1.74 million in the PDF.', options: { color: INK } }],
    { x: 0.6, y: 6.35, w: 12.1, h: 0.5, fontSize: 14, fontFace: 'Calibri', margin: 0, valign: 'middle', isTextBox: true });
  s.addNotes('Everything is in the repository under h-number-map/pipeline2. Running run_all.py rebuilds the map, PDFs and lists from the source drawing in about six minutes. The first version also used template matching for digit recognition (glyphs.py, recog.py); that code is kept in h-number-map/pipeline for reference.'); }

// ---------------------------------------------------------------- 8 site: find and select
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'Website: find a lot and open it');
  const XL = 0.6, XR = 6.73, W = 6.0;
  chip(s, 'Working: tested in a browser', XL, 1.3, 2.9, GREEN); chip(s, 'Working: tested in a browser', XR, 1.3, 2.9, GREEN);
  shot(s, 'crop_search.png', XL, 1.75, W, W * 400 / 830, 'Search screenshot', 'Search box with the matching lot listed');
  shot(s, 'crop_selected.png', XR, 1.75, W, W * 540 / 880, 'Selected lot screenshot', 'A selected lot, highlighted, with its details panel');
  s.addText([{ text: 'Search ', options: { bold: true, color: NAVY } }, { text: 'by H-number, by legacy lot such as "B 20H", or by recorded name (names appear once records exist). Close matches are suggested while typing.', options: { color: INK } }], { x: XL, y: 5.2, w: W, h: 1.2, fontSize: 14, fontFace: 'Calibri', margin: 0, valign: 'top', isTextBox: true });
  s.addText([{ text: 'Click any lot ', options: { bold: true, color: NAVY } }, { text: 'and the map zooms to it, highlights it and opens its panel beside the map, so the lot stays visible. Back and Fit map return to earlier views.', options: { color: INK } }], { x: XR, y: 5.55, w: W, h: 1.2, fontSize: 14, fontFace: 'Calibri', margin: 0, valign: 'top', isTextBox: true });
  s.addNotes('Both screenshots are cropped from the current site opened in a browser. The panel shows the H-number, the legacy reference, how the match was confirmed, and grave fields that are honestly empty. Shared records show as unavailable in these screenshots because they were taken outside the hosted page.'); }

// ---------------------------------------------------------------- 9 site: records, editing, exports
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'Website: records, editing and exports');
  const Y = 1.7, H = 4.0, wv = H * 744 / 930, wf = H * 744 / 1000, we = H * 520 / 516;
  const xv = 0.6, xf = xv + wv + 0.4, xe = xf + wf + 0.4;
  shot(s, 'crop_viewer.png', xv, Y, wv, H, 'Panel for viewers', 'Lot panel as a viewer sees it: empty record fields, no Edit button');
  shot(s, 'crop_form.png', xf, Y, wf, H, 'Edit form', 'Edit form for people with edit access');
  shot(s, 'crop_export.png', xe, Y, we, H, 'Export dialog', 'Export dialog listing PDFs and CSV lists');
  chip(s, 'Viewers', xv, 1.3, 1.2, SLATE); chip(s, 'Editors', xf, 1.3, 1.2, SLATE); chip(s, 'Exports', xe, 1.3, 1.2, SLATE);
  const yv = Y + H + 0.15, tx = (x, w, t) => s.addText(t, { x, y: yv + 0.4, w, h: 0.85, fontSize: 12, color: INK, fontFace: 'Calibri', margin: 0, valign: 'top', isTextBox: true });
  chip(s, 'Working', xv, yv, 1.1, GREEN); tx(xv, wv, 'Fields start empty and say so. No guessed graves. No Edit button.');
  chip(s, 'Not yet tested live', xf, yv, 1.9, AMBER); tx(xf, wf + 0.3, 'Edit button and form only for people with edit access. Tried with a simulated sign-in. Import is built, untested.');
  chip(s, 'PDFs, CSV built', xe, yv, 1.5, GREEN); chip(s, 'Download untested', xe + 1.6, yv, 1.6, AMBER); chip(s, 'Excel: planned', xe + 3.3, yv, 1.1, SLATE);
  tx(xe, we, 'Full map and each area as PDF, plus CSV lists. Excel (.xlsx) export is planned; CSV opens in Excel.');
  s.addNotes('Be clear about status. The panel screenshots come from a browser test with a stand-in sign-in and an empty database, so they show real screens but not a live editor session. Permission is enforced by the shared database rule (anyone who can open the page reads; only people with edit access write); a normal-user write was refused when checked. No burial data has been entered. Excel export existed in the previous site and has not been rebuilt; CSV replaces it for now.'); }

// ---------------------------------------------------------------- 10 next steps
{ const s = pres.addSlide({ masterName: 'CONTENT' }); title(s, 'What happens next, in priority order');
  const hdr = (t) => ({ text: t, options: { bold: true, color: 'FFFFFF', fill: { color: NAVY }, fontSize: 14, fontFace: 'Calibri', valign: 'middle' } });
  const c1 = (n, h, d) => ({ text: [{ text: n + '. ' + h, options: { bold: true, color: NAVY, fontSize: 14, breakLine: true } }, { text: d, options: { color: INK, fontSize: 13 } }], options: { valign: 'top', fontFace: 'Calibri' } });
  const c2 = (t) => ({ text: t, options: { color: INK, fontSize: 13, valign: 'top', fontFace: 'Calibri' } });
  const rows = [
    [hdr('What needs to happen'), hdr('What we need from cemetery staff')],
    [c1(1, 'Settle the numbering conflicts', 'Section B 373 to 380H appear in two places. Section G has lot 19 twice. Section A lots 20H to 343H show as plain numbers on the map. Several B-side labels (395 to 414) are unknown to the decoder.'), c2('Someone who knows the original numbering to say which version is right for each conflict.')],
    [c1(2, 'Finish the map corrections', '72 crypt-row labels have no section. 9 outlined lots have no label. 3 lots are too small for a number (E 195A, E 195B, H 21).'), c2('Which numbering the crypt rows follow, and a site check of the 9 unlabelled lots.')],
    [c1(3, 'Verify grave counts per lot', 'Lots hold different numbers of graves, so the map shows "grave count not verified" until it is confirmed.'), c2('A per-lot capacity sheet: lot, number of graves, and how they are arranged.')],
    [c1(4, 'Provide the master record spreadsheet', 'One row per burial, matched to a lot by H-number or by section and lot. The import is ready.'), c2('Columns: H-number or section + lot, name, birth, death, grave position, source, notes.')],
    [c1(5, 'Test live and decide', 'Try editing, import and downloads with real accounts. Settle area names, logo and where the site is hosted.'), c2('Editor accounts for testing, and a decision on area names and hosting.')] ];
  s.addTable(rows, { x: 0.6, y: 1.35, w: 12.1, colW: [7.3, 4.8], border: { type: 'solid', color: 'DDE3EA', pt: 0.75 }, fill: { color: 'FFFFFF' }, margin: [0.07, 0.12, 0.07, 0.12], rowH: [0.4, 1.12, 0.9, 0.9, 0.9, 0.9], objectName: 'Next steps table' });
  s.addNotes('Items 1 and 2 address the 286 unresolved entries (218 visible lots and 68 decoder lots with no position). They need a person who knows the original numbering, not more software. Item 3 decides whether the site can ever show a grave count. Item 4 is independent of the map, so it can start whenever the spreadsheet exists.'); }

(async () => { await pres.writeFile({ fileName: __dirname + '/Cedar_Grove_H-Number_Atlas_Progress.pptx' }); await applyTheme(__dirname + '/Cedar_Grove_H-Number_Atlas_Progress.pptx', THEME); console.log('written'); })();
