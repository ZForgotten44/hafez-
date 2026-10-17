"""Assemble the standalone 3D page: fonts, lot data and the warped aerial are inlined; three.js loads from jsDelivr."""
import json, base64, os
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
FONTS = '@font-face{font-family:"Space Grotesk";font-style:normal;font-weight:300 700;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2")}' % b64('fonts/SpaceGrotesk-400.woff2')
for w in (400, 500, 600):
    FONTS += '@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:%d;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2")}' % (w, b64('fonts/IBMPlexMono-%d.woff2' % w))
html = open('cemetery3d_template.html').read().replace('/*__FONTS__*/', FONTS).replace('/*__DATA__*/null', open('three/data3d.json').read().replace('</', '<\\/'))
open('Cedar_Grove_3D.html', 'w').write(html)
print(len(html) // 1024, 'KB')
