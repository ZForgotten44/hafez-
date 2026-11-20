"""Regenerate every H-Tables/*.csv (and the four copies at the repo root) from the production decoder, keeping each file's existing column layout."""
import csv, glob, os, re, sys
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')); sys.path.insert(0, os.path.join(REPO, 's4'))
import s4decoder1 as D
def run():
    n = 0
    for p in sorted(glob.glob(os.path.join(REPO, 'H-Tables', '*.csv')) + glob.glob(os.path.join(REPO, 'cedar_grove_section_*_h_table.csv'))):
        sec = re.search(r'section_([A-M])_', p).group(1); head = next(csv.reader(open(p)))
        rows = D.full_table(sec)
        with open(p, 'w', newline='') as f:
            w = csv.writer(f); w.writerow(head)
            for r in rows: w.writerow([r.get(c, '') for c in head])
        n += len(rows); print(os.path.basename(p), len(rows))
    return n
if __name__ == '__main__': run()
