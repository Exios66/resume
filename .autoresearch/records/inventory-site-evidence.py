import json
from collections import Counter
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit,unquote
root=Path('docs'); base='https://exios66.github.io/resume/'
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=[];self.links=[];self.meta={};self.canonical=[];self.title='';self.in_title=False;self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a' and a.get('href'):self.links.append(a['href'])
  if tag=='meta':self.meta[a.get('name') or a.get('property')]=a.get('content','')
  if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
  if tag=='title':self.in_title=True
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
 def handle_data(self,data):
  if self.in_title:self.title+=data
pages={p.relative_to(root).as_posix():Page(p.read_text()) for p in root.rglob('*.html') if 'site_libs' not in p.parts}
missing=[];anchors=[]
for rel,page in pages.items():
 for href in page.links:
  url=urlsplit(urljoin(base+rel,href))
  if url.netloc!='exios66.github.io' or not url.path.startswith('/resume/'):continue
  target=unquote(url.path[len('/resume/'):])
  if not target or target.endswith('/'):target+='index.html'
  if not (root/target).exists():missing.append({'page':rel,'href':href})
  elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:anchors.append({'page':rel,'href':href})
titles=Counter(p.title for p in pages.values())
report={'pages':len(pages),'missingDescription':[r for r,p in pages.items() if not p.meta.get('description')], 'missingCanonical':[r for r,p in pages.items() if not p.canonical], 'missingOgImage':[r for r,p in pages.items() if not p.meta.get('og:image')], 'duplicateTitles':[t for t,n in titles.items() if n>1], 'missingLocalDestinations':missing,'missingAnchorTargets':anchors,'fontBytes':sum(p.stat().st_size for p in (root/'assets/fonts').glob('*.woff2')),'limits':'Static built-artifact inventory; excludes external destinations, runtime-inserted anchors, asset dimensions, metadata semantics, transfer/compression, CLS and browser paint timings.'}
Path('.hillclimb-evidence/site-coverage-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
