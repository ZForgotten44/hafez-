# H-map build

`python3 run_all.py` (add `--no-qa` to skip the checks). Needs `pymupdf numpy scipy shapely opencv-python-headless pillow playwright`
(+ a Chromium for the QA step). Paths are relative to the repo; nothing is machine-specific.

| step | file | what it does |
|---|---|---|
| 1 | `extract_ai.py` | reads every drawing and text object of the vector drawing (.ai) into `data/ai_raw.json` |
| 2 | `lots.py` | rasterises the lot-colour lines (8 px/unit), every enclosed white area is a lot cell, traced back to vector outlines |
| 3 | `identify.py` | groups text pieces per cell (`335` + `H`), finds the legacy section (region from an independent earlier reading), decodes with `s4decoder1.h_lot` |
| 4 | `classify.py` | verified / review / known-but-unplaced; flags duplicates and numbers far from their neighbours |
| 5 | `fit.py` | places each number: centre, orientation (horizontal preferred), largest font whose measured box fits inside the inset outline |
| 6 | `basemap.py` | clean base: every drawing except text and the legend frame; text goes to the optional annotations layer |
| 7 | `svgmap.py` | SVG fragments shared by the site and the QA renders |
| 8 | `qa.py` | model, outline, browser-pixel and PDF-pixel checks (`out/qa_report.json`) |
| 9 | `build_pdf.py` | overview sheet, overlapping detail pages, per-area PDFs, appendix |
| 10 | `build_site.py` + `site/template.html` | the single-file site (the template is kept here, so the site can always be rebuilt) |
| 11 | `export_lists.py` | `lots_with_h_numbers.csv`, `unresolved_locations.csv` |

Numbers use a monospace face (advance 0.60 em, ink height <= 0.77 em, measured in Chromium); on the site every label carries `textLength`,
so its width is fixed even if the viewer substitutes another monospace font.
