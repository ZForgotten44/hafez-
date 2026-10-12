from playwright.sync_api import sync_playwright
stub=open('/tmp/w/edit_test.py').read().split("stub='''")[1].split("'''")[0]
OUT='/home/user/hafez-/h-number-map/deck/img/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args=['--no-sandbox'])
    for name,edit in (('viewer',False),('editor',True)):
        pg=b.new_page(viewport={'width':1440,'height':860},device_scale_factor=2)
        pg.add_init_script(('window.__edit=%s;'%('true' if edit else 'false'))+stub)
        pg.goto('file:///home/user/hafez-/h-number-map/site/index.html');pg.wait_for_timeout(800)
        pg.fill('#q','H001914');pg.keyboard.press('Enter');pg.wait_for_timeout(1200)
        pg.locator('#panel').screenshot(path=OUT+'panel_%s.png'%name)
        if edit:
            pg.click('#r-edit');pg.click('#r-add');pg.wait_for_timeout(200)
            pg.locator('#panel').screenshot(path=OUT+'panel_editor_form.png')
        pg.close()
    pg=b.new_page(viewport={'width':1440,'height':860});pg.goto('file:///home/user/hafez-/h-number-map/site/index.html');pg.wait_for_timeout(800)
    pg.fill('#q','B 20H');pg.wait_for_timeout(400);pg.screenshot(path=OUT+'site_search.png')
    b.close()
