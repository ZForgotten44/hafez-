"""Step 11: plain CSV lists that go with the map (same registry the site and PDFs use)."""
import csv, json, os
from common import *
def run():
    R = json.load(open(f'{DATA}/registry.json')); L = json.load(open(f'{DATA}/lots_fit.json')); out = os.path.join(REPO, 'h-number-map')
    with open(f'{out}/lots_with_h_numbers.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['h_number', 'section', 'lot', 'map_x', 'map_y', 'outline', 'section_evidence'])
        for o in sorted(L, key=lambda o: (o['hn'], o['h'])):
            w.writerow([o['h'], o['s'], o['l'], o['cx'], o['cy'], 'drawn' if o['poly'] else 'label only', 'two independent readings' if 'old_ocr_agrees' in o['ev'] else 'inferred from surrounding lots'])
    with open(f'{out}/unresolved_locations.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['kind', 'reason', 'h_number_candidate', 'section', 'lot', 'label_on_drawing', 'map_x', 'map_y', 'outline'])
        for r in R['review']:
            w.writerow(['visible lot, identity unresolved', ' | '.join(r.get('reasons', [])), r.get('htext', ''), r.get('section', ''), r.get('legacy', ''), ''.join(r['tokens']), r['pt'][0], r['pt'][1], r['geom']])
        for u in R['known_unplaced']:
            w.writerow(['known H-number, map position unresolved', u['note'] or 'No label on the drawing resolves to this decoder lot', u['htext'], u['section'], u['legacy'], '', '', '', ''])
    # Excel workbook (same registry), shipped next to the PDFs so the site can offer it
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    wb = Workbook(); ws = wb.active; ws.title = 'Read me'
    n_ok = sum(1 for o in L if 'old_ocr_agrees' in o['ev']); n_inf = len(L) - n_ok
    rows = [['Cedar Grove Cemetery - H-map lot lists'], [''], ['Lots with H-numbers', len(L), 'Outline (or label position) and a decoded H-number. Section corroborated by two independent readings (%d) or inferred from surrounding lots (%d).' % (n_ok, n_inf)],
            ['Lots to review', len(R['review']), 'Visible on the drawing; identity could not be tied to one H-number. Not drawn as H-numbers.'],
            ['No map position', len(R['known_unplaced']), 'Known to the decoder; no label on the drawing resolves to them. Some match a drawn lot in the review list.'],
            [''], ['Section and lot are the cemetery section letters and lot labels. Burial records are not part of this workbook.']]
    for r in rows: ws.append(r)
    ws['A1'].font = Font(bold=True, size=14); ws.column_dimensions['A'].width = 18; ws.column_dimensions['C'].width = 110
    def sheet(name, head, data):
        s = wb.create_sheet(name); s.append(head)
        for c in s[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='0C2340'); c.alignment = Alignment(vertical='center')
        for d in data: s.append(d)
        for i in range(1, len(head) + 1): s.column_dimensions[get_column_letter(i)].width = max(14, min(60, max(len(str(c.value or '')) for c in s[get_column_letter(i)]) + 2))
        s.freeze_panes = 'A2'; s.auto_filter.ref = s.dimensions
    sheet('Lots with H-numbers', ['H-number', 'Section', 'Lot', 'Section evidence', 'Outline'], [[o['h'], o['s'], o['l'], 'two independent readings' if 'old_ocr_agrees' in o['ev'] else 'inferred from surrounding lots', 'drawn' if o['poly'] else 'label only'] for o in sorted(L, key=lambda o: (o['hn'], o['h']))])
    sheet('Lots to review', ['Reason', 'H-number candidate', 'Section', 'Lot', 'Label on drawing', 'Map x', 'Map y', 'Outline'], [[' | '.join(r.get('reasons', [])), r.get('htext', ''), r.get('section', ''), r.get('legacy', ''), ''.join(r['tokens']), r['pt'][0], r['pt'][1], r['geom']] for r in R['review']])
    sheet('No map position', ['H-number', 'Section', 'Lot', 'Note'], [[u['htext'], u['section'], u['legacy'], u['note'] or 'No label on the drawing resolves to this decoder lot'] for u in R['known_unplaced']])
    os.makedirs(f'{out}/site/pdf', exist_ok=True); wb.save(f'{out}/site/pdf/Cedar_Grove_H-Map_lots.xlsx')
    print('wrote lots_with_h_numbers.csv (%d) and unresolved_locations.csv (%d)' % (len(L), len(R['review']) + len(R['known_unplaced'])))
if __name__ == '__main__': run()
