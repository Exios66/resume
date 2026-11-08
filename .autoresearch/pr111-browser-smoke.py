import json,re,sys
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
base=sys.argv[1] if len(sys.argv)>1 else 'https://exios66.github.io/resume/'
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch()
 for width in (375,1280):
  for theme in ('light','dark'):
   for js in (True,False):
    context=browser.new_context(viewport={'width':width,'height':1100},color_scheme=theme,java_script_enabled=js,reduced_motion='reduce')
    page=context.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    response=page.goto(base+'projects/mapreduce-reloaded.html?verify=pr111-final',wait_until='networkidle');assert response.status==200
    expect(page.locator('figure.chart')).to_have_count(3)
    for selector in ('#mr-backup-duration','#mr-backup-uncertainty'):
     panel=page.locator(selector)
     assert panel.locator('.chart-body').evaluate('el=>el.scrollWidth<=el.clientWidth+1')
    duration=page.locator('#mr-backup-duration')
    assert [m.get_attribute('data-tip-value') for m in duration.locator('.mark').all()]==['17.58 s','11.24 s']
    expect(duration).to_contain_text('0.2 CPU')
    expect(duration).to_contain_text('not drift-controlled')
    interval=page.locator('#mr-backup-uncertainty')
    expect(interval).to_contain_text('does not prove zero cost')
    assert interval.locator('.mark').get_attribute('data-tip-value')=='−0.11 s; −0.38 s to +0.16 s'
    geometry=interval.evaluate("el=>[Number(el.querySelector('.interval-range').getAttribute('x1')),Number(el.querySelector('.dot').getAttribute('cx')),Number(el.querySelector('line.ref').getAttribute('x1')),Number(el.querySelector('.interval-range').getAttribute('x2'))]")
    assert geometry==sorted(geometry)
    for figure in page.locator('figure.chart').all():
     forward=figure.locator('.chart-tools a');table=page.locator(forward.get_attribute('href'))
     forward.focus();page.keyboard.press('Enter');expect(table).to_be_focused()
     back=table.locator('xpath=following-sibling::p[1]').locator('a');caption=page.locator(back.get_attribute('href'))
     back.focus();page.keyboard.press('Enter');expect(caption).to_be_focused()
     if js:
      row=table.locator('tbody tr').last;row.focus()
      expect(figure.locator('.mark.is-linked')).not_to_have_count(0)
      for cell in row.locator('td').all_text_contents():expect(figure.locator('.chart-readout')).to_contain_text(' '.join(cell.split()))
    for index in (1,2):
     page.locator(f'#fnref{index}').click();expect(page).to_have_url(re.compile(f'#fn{index}$'))
     note=page.locator(f'#fn{index}');expect(note).to_contain_text('4dd1ca4')
     note.locator('a[role="doc-backlink"]').click();expect(page).to_have_url(re.compile(f'#fnref{index}$'))
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.emulate_media(media='print')
    for figure in page.locator('figure.chart').all():
     expect(figure.locator('svg')).to_be_visible()
     expect(page.locator(figure.locator('.chart-tools a').get_attribute('href'))).to_be_visible()
     if js:expect(figure.locator('.chart-readout')).to_be_hidden()
    assert not errors,errors
    results.append({'width':width,'theme':theme,'javascript':js,'status':'passed','charts':3,'native_source_roundtrips':3,'citation_roundtrips':2,'console_errors':errors})
    context.close()
 browser.close()
out=Path('.hillclimb-evidence/pr111-live-smoke.json');out.write_text(json.dumps({'base':base,'cases':results},indent=2)+'\n')
print(f'{len(results)} MapReduce smoke cases passed; evidence: {out}')
