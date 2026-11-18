"""Independent consistency checks for the deliverable; does not certify search recall."""
import csv,json,re,hashlib,struct
from pathlib import Path
from collections import Counter
BASE=Path(__file__).resolve().parents[1];OUT=BASE/'outputs/team2_20261117'
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
checks={}
def check(k,v):
 checks[k]=bool(v)
 if not v:raise AssertionError(k)
D=json.loads((OUT/'analysis.json').read_text()); C=json.loads((OUT/'claims_analysis.json').read_text())
for s in D['inputs']:
 p=BASE/s['file']; check('source_hash_'+p.stem,hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'])
for tech,t in [('DLC','dlc'),('Immersion','imm')]:
 rows=read(OUT/f'us_{t}_reviewed.csv');m=D['metrics'][tech]['reviewed']
 check(t+'_total',len(rows)==m['total'])
 check(t+'_annual_sum',sum(r['families'] for r in m['annual'])==len(rows))
 recent=[r for r in rows if '2015-01-01'<=r['Earliest Priority Date']<='2024-12-31']
 counter=Counter(a.strip() for r in recent for a in r['applicant_normalized'].split(';') if a.strip())
 den=sum(counter.values()); hhi=sum(v*v for v in counter.values())/(den*den)
 check(t+'_HHI_independent',abs(hhi-m['hhi_full'])<1e-12)
 check(t+'_pair_denominator',den==m['pair_denominator'])
 for rr in D['cpc']:
  if rr['technology']==tech: check(t+'_'+rr['group']+'_'+rr['period'],0<=rr['count']<=rr['denominator'] and abs(rr['count']/rr['denominator']-rr['share'])<1e-12)
core=read(BASE/'outputs/team1_20261109/handoff/US_핵심특허_팀원2반환.csv')
check('same_20_selected',set(re.sub(r'\W','',r['grant_number']) for r in core)=={r['patent'] for r in C['rows']})
for r in C['rows']:
 e=json.loads((OUT/r['evidence_file']).read_text())
 check(r['patent']+'_claim1',any(c['number']==1 and c['text'].startswith('1.') for c in e['claims']))
 check(r['patent']+'_source',r['source_url']==e['source_url']+'#claims')
 check(r['patent']+'_document_count',len(e['claims'])==int(re.search(r'Claims\s*\((\d+)\)',e['claims_full_text'])[1]))
for tech in ['DLC','Immersion']:
 rr=[r for r in C['rows'] if r['technology']==tech]
 check(tech+'_10',len(rr)==10)
 for f in C['features']:check(tech+'_feature_'+f,sum(r[f] for r in rr)==C['counts'][tech][f])
check('20_status_assumptions',Counter(r['status_google_assumption_20261117'] for r in C['rows'])==Counter({'Active':13,'Expired - Lifetime':2,'Expired - Fee Related':5}))
check('three_facility_CPC_counterexamples',sum(r['시설 냉각수 명시']==1 and r['building_CPC_in_teammate_table']=='N' for r in C['rows'])==3)
figs=list((OUT/'figures').glob('*.png'));check('eight_figures',len(figs)==8)
for p in figs:
 width,height=struct.unpack('>II',p.read_bytes()[16:24]);check(p.stem+'_size',(width,height)==(2560,1440));check(p.stem+'_SVG',p.with_suffix('.svg').exists())
check('no_figure_canvas_overflow',all(not r['outside_canvas'] for r in json.loads((OUT/'figures/render_checks.json').read_text())))
for name in ['결과팀_최종인계.md','발표대본.md','수정검증_기록.md','검색식_발표용.md','공유문서_반영안.md']:
 check('deliverable_'+name,(OUT/name).exists())
# Optional local attachment equality check; do not publish the user's absolute path.
attachment={'checked':False}
try:
 import openpyxl
 pp=list((Path.home()/'Downloads').glob('US_*2.xlsx'))
 if len(pp)==1:
  a=list(openpyxl.load_workbook(pp[0],read_only=True,data_only=True)['핵심특허'].values)
  b=list(openpyxl.load_workbook(BASE/'outputs/team1_20261109/handoff/US_핵심특허_팀원2반환.xlsx',read_only=True,data_only=True)['핵심특허'].values)
  check('attachment_core_A1_X21_equals_repo',a==b)
  attachment={'checked':True,'sheet':'핵심특허','range':'A1:X21','equal':a==b}
except ImportError:pass
result={'checked_at':'2026-11-18','passed':all(checks.values()),'checks':checks,'attachment':attachment,
 'visual_review':'8 PNGs inspected; no unreadable labels or clipping found.',
 'limits':['No full-cohort independent relevance re-screen or recall estimate.','Functional coding covers independent claim 1, not all claims.','Cost/performance/contract inputs remain for results-team evaluation.','Google Doc was not edited; prepared replacement text is supplied.']}
(OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'passed':result['passed'],'checks':len(checks),'attachment':attachment},ensure_ascii=False))
