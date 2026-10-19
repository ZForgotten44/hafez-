"""Shared paths for the H-map build.  Everything is relative to the repo, so the
pipeline runs the same on any machine:  python3 run_all.py"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
AI_SRC = os.path.join(REPO, 'Ground Maps', 'Cedar Grove 2022 with CR.ai')
DECODER = os.path.join(REPO, 's4', 's4decoder1.py')
OLD_PLACED = os.path.join(REPO, 'h-number-map', 'placed_lots.csv')   # old OCR result, used only as a cross-check
DATA = os.path.join(HERE, 'data')
OUT = os.path.join(HERE, 'out')
os.makedirs(DATA, exist_ok=True); os.makedirs(OUT, exist_ok=True)
LOT_COLOR = (0.3, 0.52, 0.6)          # stroke colour of every lot outline in the CAD export
