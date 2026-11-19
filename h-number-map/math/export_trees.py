"""Write the reconciled tree inventory h-number-map/trees.json from three/data3d.json (made by build_3d_data.py, which is deterministic:
fixed RNG seed, building list independent of the numbering).  One object per tree with a stable id (T001 ...), in file order.
The maps read trees.json, not data3d.json, so a rebuild of the 3D data cannot change the inventory silently."""
import json, os
here = os.path.dirname(os.path.abspath(__file__))
def run():
    d = json.load(open(os.path.join(here, 'three', 'data3d.json'))); wf = d.get('woods_from', len(d['trees']))
    out = [dict(id='T%03d' % (i + 1), x=t[0], y=t[1], radius=t[2], kind='evergreen' if t[3] else 'leafy', origin='detected' if i < wf else 'woods fill') for i, t in enumerate(d['trees'])]
    json.dump(out, open(os.path.join(here, '..', 'trees.json'), 'w'), indent=1)
    print('trees.json', len(out), 'trees:', sum(o['origin'] == 'detected' for o in out), 'detected,', sum(o['origin'] != 'detected' for o in out), 'woods fill')
if __name__ == '__main__': run()
