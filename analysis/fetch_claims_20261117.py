"""Cache public patent claim text; no teammate source files are modified."""
import csv, json, re, hashlib
from datetime import date
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen, Request
from lxml import html

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'outputs/team2_20261117/evidence'
OUT.mkdir(parents=True, exist_ok=True)
rows = list(csv.DictReader((BASE/'outputs/team1_20261109/handoff/US_핵심특허_팀원2반환.csv').open(encoding='utf-8-sig')))
ids = [re.sub(r'\W', '', r['grant_number']) for r in rows]
ids += ['US9992914B2', 'US20250089206A1', 'KR102552810B1', 'KR102815358B1']

def normalize(obj):
    unique={}
    for c in obj['claims']:
        m=re.match(r'^(\d+)\.',c['text'])
        n=c.get('number') or (int(m.group(1)) if m else None)
        if n is not None:
            c['number']=int(n)
            unique[int(n)]=c
    obj['claims']=[unique[n] for n in sorted(unique)]
    if 'priority_date' in obj:
        obj['document_dates_metadata']=obj.pop('priority_date')
    return obj

def fetch(pid):
    dest = OUT / (pid+'.json')
    if dest.exists():
        obj=normalize(json.loads(dest.read_text()))
        dest.write_text(json.dumps(obj,ensure_ascii=False,indent=2))
        return obj
    url = f'https://patents.google.com/patent/{pid}/en'
    with urlopen(Request(url, headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as response:
        content=response.read()
    soup=html.fromstring(content)
    sections=soup.xpath('//section[@itemprop="claims"]')
    if not sections:
        raise ValueError(f'No claims section: {pid}')
    section=sections[0]
    norm=lambda el: re.sub(r'\s+', ' ', el.text_content()).strip()
    claims = []
    elements=section.xpath('.//claim') or section.xpath('.//div[@class="claim"]')
    for el in elements:
        txt=norm(el)
        mt=re.match(r'^(\d+)\.',txt)
        number=el.get('num') or (mt.group(1) if mt else None)
        if number is None: continue
        korean=el.xpath('.//span[@class="google-src-text"]')
        claims.append({'number':int(number), 'text':txt, 'korean_original': ' '.join(norm(x) for x in korean)})
    def meta(name):
        return soup.xpath(f'//meta[@name="{name}"]/@content')
    status=soup.xpath('//*[@itemprop="status"]')
    abstract=soup.xpath('//*[@itemprop="abstract"]')
    obj={'patent':pid, 'source_url':url, 'retrieved':date.today().isoformat(),
         'html_sha256':hashlib.sha256(content).hexdigest(),
         'title':meta('DC.title'), 'document_dates_metadata':meta('DC.date'),
         'status_google_assumption': norm(status[0]) if status else None,
         'original_assignee': [norm(x) for x in soup.xpath('//*[@itemprop="assigneeOriginal"]')],
         'current_assignee_display': [norm(x) for x in soup.xpath('//*[@itemprop="assigneeCurrent"]')],
         'abstract':norm(abstract[0]) if abstract else '',
         'claims':claims,
         'claims_full_text': norm(section)}
    if not claims: raise ValueError(f'No parsed claims: {pid}')
    obj=normalize(obj)
    dest.write_text(json.dumps(obj, ensure_ascii=False, indent=2))
    return obj

with ThreadPoolExecutor(max_workers=4) as pool:
    for o in pool.map(fetch, ids):
        print(o['patent'],len(o['claims']),o['status_google_assumption'])
