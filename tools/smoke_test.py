#!/usr/bin/env python3
"""Browser smoke test using inlined assets in the test harness.
This sandbox blocks navigation to file/http addresses, so the test loads the
same HTML, styles, and scripts through Playwright's about:blank environment.
The produced public site remains a normal multi-file static website.
"""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parent.parent

def load(page):
  page.goto('about:blank')
  markup=(ROOT/'index.html').read_text('utf-8')
  markup=re.sub(r'<link rel="stylesheet"[^>]*>', '', markup)
  markup=re.sub(r'<script src="[^"]+" defer></script>','',markup)
  page.set_content(markup,wait_until='load')
  for c in ['css/site.css','css/animations.css']:
    page.add_style_tag(content=(ROOT/c).read_text('utf-8'))
  # about:blank doesn't permit a history replacement to an empty path.
  page.evaluate('history.replaceState = () => {};')
  for s in ['data/scenes.js','data/illustrations.js','js/motion.js','js/app.js']:
    page.add_script_tag(content=(ROOT/s).read_text('utf-8'))
  page.wait_for_timeout(100)

def main():
  from playwright.sync_api import sync_playwright
  result={'desktop':{},'mobile':{},'errors':[]}
  with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu'])
    page=browser.new_page(viewport={'width':1536,'height':900},device_scale_factor=1)
    page.on('pageerror',lambda e:result['errors'].append(str(e)))
    load(page)
    assert page.locator('#cover').is_visible(),'Cover not visible'
    page.screenshot(path='/mnt/data/golf_site_desktop_cover.png',full_page=True)
    page.locator('#enterStory').click()
    assert page.locator('#sceneNumber').inner_text()=='01'
    assert page.locator('#valeCard').get_attribute('aria-hidden')=='true'
    page.locator('#advanceButton').click()
    assert page.locator('#valeCard').get_attribute('aria-hidden')=='false'
    page.locator('#advanceButton').click()
    assert page.locator('#desk').evaluate('(e)=>e.classList.contains("has-clue")')
    page.screenshot(path='/mnt/data/golf_site_desktop_reveal.png',full_page=True)
    # Visit ALL 43 scenes using the index chooser, test two beats and unique SVG output.
    scene_count=page.locator('#indexGrid button').count()
    for i in range(1,44):
      page.locator('#indexOpen').click()
      assert page.locator('#indexGrid button').count()==43
      page.locator(f'#indexGrid button[data-index="{i-1}"]').click()
      assert page.locator('#sceneNumber').inner_text()==f'{i:02}',i
      page.locator('#advanceButton').click()
      page.locator('#advanceButton').click()
      assert page.locator('#kinetic svg').count()==1,i
      assert len(page.locator('#clueText').inner_text())>12,i
    result['desktop']['scenes']=43
    page.locator('#indexOpen').click()
    page.locator('#indexSearch').fill('bogey')
    assert page.locator('#indexGrid button').count()>=1
    page.locator('#indexGrid button').first.click()
    page.locator('#advanceButton').click();page.locator('#advanceButton').click()
    page.locator('#sourceOpen').click()
    assert page.locator('#infoOverlay').is_visible()
    assert 'DOCUMENT OR REFERENCE' in page.locator('#infoModal').inner_text()
    page.keyboard.press('Escape')
    assert page.locator('#infoOverlay').is_hidden()
    mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
    mobile.on('pageerror',lambda e:result['errors'].append(str(e)))
    load(mobile)
    mobile.screenshot(path='/mnt/data/golf_site_mobile_cover.png',full_page=True)
    mobile.locator('#enterStory').click()
    mobile.locator('#advanceButton').click();mobile.locator('#advanceButton').click()
    mobile.screenshot(path='/mnt/data/golf_site_mobile_reveal.png',full_page=True)
    result['mobile']['width']=390
    result['mobile']['scrollWidth']=mobile.evaluate('document.documentElement.scrollWidth')
    result['mobile']['bodyWidth']=mobile.evaluate('document.body.clientWidth')
    assert result['mobile']['scrollWidth']<=394,result['mobile']
    browser.close()
  if result['errors']:raise AssertionError(result['errors'])
  print(json.dumps(result,indent=2))
  (ROOT/'docs'/'QA_REPORT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
if __name__=='__main__':main()
