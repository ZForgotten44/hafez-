"""Print the explainer to a paper PDF (letter, light theme, static) with page numbers."""
import sys, os
from playwright.sync_api import sync_playwright
here = os.path.dirname(os.path.abspath(__file__))
src = 'file://' + os.path.join(here, 'Cedar_Grove_Numbering_Explained.html')
out = os.path.join(here, 'Cedar_Grove_Numbering_Explained.pdf')
FOOT = '<div style="width:100%;font:8px Helvetica,Arial,sans-serif;color:#444;display:flex;justify-content:space-between;padding:0 13mm"><span>Cedar Grove Numbering, Explained</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    ctx = b.new_context(viewport={'width': 1100, 'height': 1400}, color_scheme='light')
    pg = ctx.new_page(); pg.goto(src); pg.wait_for_timeout(1500)
    pg.emulate_media(media='print', color_scheme='light')
    pg.evaluate("document.documentElement.setAttribute('data-theme','light');window.dispatchEvent(new Event('beforeprint'))")
    pg.wait_for_timeout(800)
    pg.pdf(path=out, prefer_css_page_size=True, print_background=True, display_header_footer=True, header_template='<span></span>', footer_template=FOOT)
    b.close()
print(out, os.path.getsize(out) // 1024, 'KB')
