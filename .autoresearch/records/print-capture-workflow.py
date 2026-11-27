import sys,json
from pathlib import Path
from playwright.sync_api import sync_playwright
phase=sys.argv[1]
out=Path('.hillclimb-shots');out.mkdir(exist_ok=True)
rows=[]
with sync_playwright() as p:
 browser=p.chromium.launch()
 for width in (375,1280):
  for theme in ('light','dark'):
   for label,route in [('project','projects/mailroom-ml.html'),('search','search.html?q=calibration')]:
    page=browser.new_page(viewport={'width':width,'height':900},color_scheme=theme,reduced_motion='reduce')
    page.goto('http://127.0.0.1:8769/'+route,wait_until='networkidle')
    page.emulate_media(media='print')
    page.evaluate('document.fonts.ready')
    if label=='project':page.evaluate('window.scrollTo(0,document.body.scrollHeight)')
    visible=page.locator('.project-pager' if label=='project' else '.search-suggest').is_visible()
    assert visible==(phase=='before'),(label,width,theme,visible)
    assert page.get_by_role('heading',level=1).is_visible()
    name=f'segment-12-before-{label}-{width}-{theme}' if phase=='before' else f'run-62-print-{label}-{width}-{theme}'
    page.screenshot(path=str(out/(name+'.png')))
    rows.append({'page':route,'width':width,'theme':theme,'screenNavigationVisible':visible,'primaryTitleVisible':True,'screenshot':name+'.png'})
    page.close()
 browser.close()
Path('/tmp/print-'+phase+'-observations.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
