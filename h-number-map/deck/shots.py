"""Screenshots for the progress deck: the previous site (git b3e9060) and the current site, same map area, same pixel size."""
import json, subprocess, sys
from playwright.sync_api import sync_playwright
REPO = '/home/user/hafez-'
OUT = REPO + '/h-number-map/deck/img/'
old = subprocess.check_output(['git', '-C', REPO, 'show', 'b3e9060:h-number-map/site/index.html']).decode()
open('/tmp/w/old.html', 'w').write(old)
reg = json.load(open(REPO + '/h-number-map/pipeline2/data/identified.json')); s, t = reg['scale'], reg['shift']
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
W, H = 1000, 640
AREAS = {'dense': (830, 380, 130), 'curved': (430, 440, 130), 'garden': (1330, 395, 130)}   # CAD x, y, width
def viewbox_new(a): x, y, w = a; return (x, y, w, w * H / W)
def viewbox_old(a): x, y, w = a; return (x * s + t[0], y * s + t[1], w * s, w * s * H / W)
FIX = '''(() => {var st=document.createElement('style');st.textContent=`__SEL__{position:fixed!important;left:0;top:0;width:1000px!important;height:640px!important;z-index:9999;flex:none!important}
.ctl,.map-float,#zoomhint,#legend{display:none!important}`;document.head.appendChild(st)})()'''
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
    # ---------- full-app screenshots (overview) ----------
    for name, url, sel in (('old', 'file:///tmp/w/old.html', None), ('new', 'file://' + REPO + '/h-number-map/site/index.html', None)):
        pg = b.new_page(viewport={'width': 1440, 'height': 860}); pg.goto(url); pg.wait_for_timeout(1800)
        if name == 'new': pg.click('#z-fit'); pg.wait_for_timeout(700)
        pg.screenshot(path=OUT + f'app_overview_{name}.png'); pg.close()
    # ---------- same-area close-ups ----------
    for key, a in AREAS.items():
        pg = b.new_page(viewport={'width': 1000, 'height': 640}); pg.goto('file:///tmp/w/old.html'); pg.wait_for_timeout(1500)
        pg.evaluate(FIX.replace('__SEL__', '#mapwrap'))
        vb = viewbox_old(a)
        pg.evaluate('''(vb)=>{var s=document.getElementById('atlas-svg');s.classList.remove('zoom-overview');s.setAttribute('viewBox',vb.join(' '));s.style.width='1000px';s.style.height='640px';document.querySelectorAll('.sechit').forEach(e=>e.remove())}''', list(vb))
        pg.wait_for_timeout(500); pg.screenshot(path=OUT + f'zoom_{key}_old.png'); pg.close()
        pg = b.new_page(viewport={'width': 1000, 'height': 640}); pg.goto('file://' + REPO + '/h-number-map/site/index.html'); pg.wait_for_timeout(1200)
        pg.evaluate(FIX.replace('__SEL__', '#mapwrap'))
        vb = viewbox_new(a)
        pg.evaluate('''(vb)=>{var s=document.getElementById('svg');s.setAttribute('viewBox',vb.join(' '));document.querySelectorAll('#labels g').forEach(g=>g.classList.add('show'))}''', list(vb))
        pg.wait_for_timeout(400); pg.screenshot(path=OUT + f'zoom_{key}_new.png'); pg.close()
    # ---------- current-site states ----------
    pg = b.new_page(viewport={'width': 1440, 'height': 860}); pg.goto('file://' + REPO + '/h-number-map/site/index.html'); pg.wait_for_timeout(1200)
    pg.fill('#q', 'F 3'); pg.wait_for_timeout(300); pg.screenshot(path=OUT + 'site_search.png')
    pg.fill('#q', 'H001914'); pg.keyboard.press('Enter'); pg.wait_for_timeout(1300); pg.screenshot(path=OUT + 'site_selected.png')
    pg.click('#t-review'); pg.wait_for_timeout(200); pg.click('[data-un="0"]'); pg.wait_for_timeout(1300); pg.screenshot(path=OUT + 'site_unplaced.png')
    pg.click('#b-export'); pg.wait_for_timeout(300); pg.screenshot(path=OUT + 'site_export.png')
    b.close()
print('ok')
