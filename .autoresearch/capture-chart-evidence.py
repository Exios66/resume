"""Capture selected source-row states against the locally rendered candidate."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('.hillclimb-shots');out.mkdir(exist_ok=True)
cases=[('bars','projects/natd.html',3),('dumbbell','projects/mailroom-ml/report.html',2),('step','projects/mailroom-corpus-eda/report.html',3),('strip','projects/langtons-ant.html',2)]
observations=[]
with sync_playwright() as p:
 browser=p.chromium.launch()
 for width in (375,1280):
  for theme in ('light','dark'):
   for kind,route,index in cases:
    page=browser.new_page(viewport={'width':width,'height':1100},color_scheme=theme,reduced_motion='reduce')
    page.goto('http://127.0.0.1:8769/'+route,wait_until='networkidle')
    figure=page.locator('figure.chart').first
    mark=figure.locator(f'.mark[data-source-row="{index}"]').first
    mark.evaluate('el => el.focus({preventScroll:true})')
    page.keyboard.press('Escape')
    figure.evaluate("el => el.scrollIntoView({block:'start'})")
    page.evaluate('window.scrollBy(0,-90)')
    assert page.locator('table.chart-source tr.is-linked').count()==1
    assert figure.locator('.chart-readout').is_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    name=f'run-65-{kind}-{width}-{theme}.png'
    page.screenshot(path=str(out/name))
    observations.append({'route':route,'width':width,'theme':theme,'sourceRow':index,'readout':figure.locator('.chart-readout').inner_text(),'screenshot':name})
    if kind=='bars' and width==1280 and theme=='dark':
     page.emulate_media(forced_colors='active')
     assert page.locator('table.chart-source tr.is-linked').evaluate('el => getComputedStyle(el).outlineWidth')=='2px'
     page.screenshot(path=str(out/'run-65-bars-forced-colors.png'))
     page.emulate_media(forced_colors='none')
    if kind in ('bars','strip') and width==1280 and theme=='light':
     page.emulate_media(media='print')
     assert not figure.locator('.chart-readout').is_visible()
     assert not figure.locator('.chart-tools').is_visible()
     assert not page.locator('.chart-return').is_visible()
     assert page.locator('table.chart-source').is_visible()
     figure.evaluate("el => el.scrollIntoView({block:'start'})")
     page.screenshot(path=str(out/f'run-65-{kind}-print.png'))
    page.close()
 browser.close()
Path('.hillclimb-evidence/run-65-observations.json').write_text(json.dumps(observations,indent=2)+'\n')
print('Captured 16 focus states, one forced-colors state and two print states.')
