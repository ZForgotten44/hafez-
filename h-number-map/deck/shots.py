"""Screenshots for the progress deck: previous site (git b3e9060) and current site; same map bounds and pixel size for each pair."""
import json, subprocess
from playwright.sync_api import sync_playwright
REPO = '/home/user/hafez-'; OUT = REPO + '/h-number-map/deck/img/'
open('/tmp/w/old.html', 'w').write(subprocess.check_output(['git', '-C', REPO, 'show', 'b3e9060:h-number-map/site/index.html']).decode())
reg = json.load(open(REPO + '/h-number-map/pipeline2/data/identified.json')); s, t = reg['scale'], reg['shift']
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
NEW = 'file://' + REPO + '/h-number-map/site/index.html'
STUB = open('/tmp/w/edit_test.py').read().split("stub='''")[1].split("'''")[0]
def hide(vw, vh): return '''(() => {var st=document.createElement('style');st.textContent=`#mapwrap{position:fixed!important;left:0;top:0;width:%dpx!important;height:%dpx!important;z-index:9999;flex:none!important}.ctl,.map-float,#zoomhint,#legend{display:none!important}`;document.head.appendChild(st)})()''' % (vw, vh)
def shot_pair(b, key, x, y, w, vw, vh, labels=True):
    h = w * vh / vw
    pg = b.new_page(viewport={'width': vw, 'height': vh}); pg.goto('file:///tmp/w/old.html'); pg.wait_for_timeout(1500); pg.evaluate(hide(vw, vh))
    pg.evaluate('''(a)=>{var sv=document.getElementById('atlas-svg');if(a.labels)sv.classList.remove('zoom-overview');sv.setAttribute('viewBox',a.vb.join(' '));sv.style.width=a.vw+'px';sv.style.height=a.vh+'px';if(a.labels)document.querySelectorAll('.sechit').forEach(e=>e.remove())}''',
                {'vb': [x * s + t[0], y * s + t[1], w * s, h * s], 'vw': vw, 'vh': vh, 'labels': labels})
    pg.wait_for_timeout(500); pg.screenshot(path=OUT + f'{key}_old.png'); pg.close()
    pg = b.new_page(viewport={'width': vw, 'height': vh}); pg.goto(NEW); pg.wait_for_timeout(1200); pg.evaluate(hide(vw, vh))
    pg.evaluate('''(a)=>{var sv=document.getElementById('svg');sv.setAttribute('viewBox',a.vb.join(' '));if(a.labels)document.querySelectorAll('#labels g').forEach(g=>g.classList.add('show'))}''', {'vb': [x, y, w, h], 'labels': labels})
    pg.wait_for_timeout(400); pg.screenshot(path=OUT + f'{key}_new.png'); pg.close()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
    shot_pair(b, 'overview', 359.86, 231.75, 1321.1, 1200, 630, labels=False)
    shot_pair(b, 'dense', 830, 380, 130, 1000, 640)
    shot_pair(b, 'curved', 430, 440, 130, 1000, 640)
    # search -> select -> details for ONE lot (legacy F 34 = H001914)
    pg = b.new_page(viewport={'width': 1440, 'height': 860}); pg.add_init_script('window.__edit=false;' + STUB); pg.goto(NEW); pg.wait_for_timeout(1000)
    pg.fill('#q', 'F 34'); pg.wait_for_timeout(400); pg.screenshot(path=OUT + 'flow1_full.png', clip={'x': 0, 'y': 0, 'width': 830, 'height': 330})
    pg.keyboard.press('Enter'); pg.wait_for_timeout(1400); pg.screenshot(path=OUT + 'flow2_full.png', clip={'x': 560, 'y': 60, 'width': 880, 'height': 560})
    pg.close()
    # record panels (tall viewport so nothing is clipped)
    for name, edit in (('viewer', False), ('editor', True)):
        pg = b.new_page(viewport={'width': 1440, 'height': 1500}, device_scale_factor=2); pg.add_init_script('window.__edit=%s;' % ('true' if edit else 'false') + STUB); pg.goto(NEW); pg.wait_for_timeout(900)
        pg.fill('#q', 'H001914'); pg.keyboard.press('Enter'); pg.wait_for_timeout(1300)
        if name == 'viewer':
            box = pg.locator('#rec-box').bounding_box(); pb = pg.locator('#panel').bounding_box()
            pg.screenshot(path=OUT + 'panel_viewer.png', clip={'x': pb['x'], 'y': pb['y'], 'width': pb['width'], 'height': box['y'] + box['height'] + 60 - pb['y']})
        else:
            pg.click('#r-edit'); pg.click('#r-add'); pg.wait_for_timeout(300)
            fb = pg.locator('#rec-box .form').bounding_box(); pb = pg.locator('#panel').bounding_box()
            pg.screenshot(path=OUT + 'panel_form.png', clip={'x': pb['x'], 'y': fb['y'] - 8, 'width': pb['width'], 'height': fb['height'] + 16})
        pg.close()
    pg = b.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=2); pg.goto(NEW); pg.wait_for_timeout(900); pg.click('#b-export'); pg.wait_for_timeout(300)
    mb = pg.locator('.modal').bounding_box(); mb['height'] = min(mb['height'], 412); pg.screenshot(path=OUT + 'export_dialog.png', clip=mb)
    b.close()
from PIL import Image
for n in ['flow1_full', 'flow2_full', 'panel_viewer', 'panel_form', 'export_dialog', 'overview_new', 'overview_old']:
    print(n, Image.open(OUT + n + '.png').size)
