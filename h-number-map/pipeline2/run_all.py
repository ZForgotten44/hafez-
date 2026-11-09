"""Rebuild everything from the sources in the repo:  python3 run_all.py
Needs: pymupdf, numpy, scipy, shapely, opencv-python-headless, pillow, playwright (+ chromium) for the QA step."""
import sys, time
import extract_ai, lots, identify, classify, fit, resolve, finalize, basemap, build_site
steps = [('extract CAD drawing', extract_ai.run), ('trace lot outlines', lots.run), ('identify labels', identify.run), ('classify lots', classify.run),
         ('fit numbers to lots (classifier output)', lambda: fit.run('registry_raw.json', 'lots_fit_raw.json')), ('propose numbers for the open lots from the path', resolve.run),
         ('close every open case', finalize.run), ('fit numbers to all lots', fit.run), ('clean base layer', basemap.build)]
for name, fn in steps:
    t = time.time(); print('==', name); fn(); print('   %.1fs' % (time.time() - t))
if '--no-qa' not in sys.argv:
    import qa; print('== QA'); qa.run()
try:
    import build_pdf; print('== PDFs'); pdfs = build_pdf.run()
except ImportError:
    pdfs = {}
import export_lists; export_lists.run()
print('== site'); build_site.run(pdfs or None)
