"""Capture actual interval states on the local candidate; no external state changes."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('.hillclimb-shots');observations=[]
with sync_playwright() as p:
 browser=p.chromium.launch()
 for width in (375,768,1280):
  for theme in ('light','dark'):
   page=browser.new_page(viewport={'width':width,'height':1200},color_scheme=theme,reduced_motion='reduce')
   page.goto('http://127.0.0.1:8769/projects/mapreduce-reloaded.html',wait_until='networkidle')
   panel=page.locator('#mr-backup-uncertainty')
   mark=panel.locator('.mark')
   mark.evaluate('el=>el.focus({preventScroll:true})');page.keyboard.press('Escape')
   panel.evaluate("el=>el.scrollIntoView({block:'start'})");page.evaluate('window.scrollBy(0,-100)')
   assert panel.locator('.chart-body').evaluate('el=>el.scrollWidth<=el.clientWidth+1')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   screenshot=f'run-70-interval-{width}-{theme}.png';page.screenshot(path=str(out/screenshot))
   observations.append({'width':width,'theme':theme,'readout':panel.locator('.chart-readout').inner_text(),'horizontalScrollRequired':False,'screenshot':screenshot})
   if width==1280 and theme=='dark':
    page.emulate_media(forced_colors='active');page.screenshot(path=str(out/'run-70-interval-forced-colors.png'));page.emulate_media(forced_colors='none')
   if width==1280 and theme=='light':
    page.emulate_media(media='print')
    assert not panel.locator('.chart-readout').is_visible()
    assert panel.locator('svg').is_visible() and panel.locator('table').is_visible()
    panel.evaluate("el=>el.scrollIntoView({block:'start'})");page.screenshot(path=str(out/'run-70-interval-print.png'))
   page.close()
 browser.close()
Path('.hillclimb-evidence/run-70-observations.json').write_text(json.dumps(observations,indent=2)+'\n')
print('Captured six interval states, forced colors and print; all comparison marks fit without sideways scrolling.')
