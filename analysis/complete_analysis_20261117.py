"""Reproduce the Nov17 handoff without overwriting Team1's original work.
Python standard library; pandas/openpyxl needed only to read existing S-curve output.
"""
import csv, json, re, hashlib
from pathlib import Path
from collections import Counter, defaultdict

BASE=Path(__file__).resolve().parents[1]
T1=BASE/'outputs/team1_20261109'
OUT=BASE/'outputs/team2_20261117'
OUT.mkdir(parents=True,exist_ok=True)
def read(p):
    return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def family(r):
    return tuple(sorted(set(r['Simple Family Members'].split(';;'))))
def apps(r):
    return sorted(set(x.strip() for x in r['applicant_normalized'].split(';') if x.strip()))
def year(r): return int(r['Earliest Priority Date'][:4])
def cpcs(r): return set(x.strip() for x in r['CPC Classifications'].split(';;') if x.strip())

# Four unambiguous mismatches in the teammate's already-selected screening sample.
# Ambiguous hybrid/thermal-integration records remain tagged and enter sensitivity tests.
EXCLUDE={
 'US 10470342 B2':'수상 데이터센터의 외부 취수·시설 냉각. 칩/서버 직접액체냉각 근거가 초록에 없어 DLC 주표본 제외, 시설 인접기술로 보존.',
 'US 2015/0319889 A1':'전자장비 액침용 냉각 매체. DLC 대신 액침 분야에 해당.',
 'US 2025/0008703 A1':'서버가 냉각액에 잠기는 캐비닛. DLC 대신 액침 분야에 해당.',
 'US 2023/0057545 A1':'액냉 랙의 전력분배 부품 분리 설계가 중심. DLC 냉각 구성 자체 분석에서는 제외.'}
BOUNDARY={
 'US 2016/0286695 A1':'3D IC 구조와 액체냉각을 함께 다룸. 액체냉각은 명시되어 있어 유지.',
 'US 7626820 B1':'히트파이프와 외부 냉각액 공급 냉각판을 함께 사용. 하이브리드 경계로 유지.',
 'US 9543787 B2':'엑서지 회수·다중유체 열 버스와 액체냉각의 통합. 열관리 경계로 유지.'}
sample=read(T1/'clean/precision_sample_dlc.csv')
for i in [23,49]:
    BOUNDARY[sample[i-1]['Display Key']]='팀원1이 관련으로 포함한 전력/냉각 또는 시설측 통합 경계 사례.'
imm_sample=read(T1/'clean/precision_sample_imm.csv')
rechecks=[{'technology':'DLC','document':k,'decision':'제외','reason':v} for k,v in EXCLUDE.items()]
rechecks += [{'technology':'DLC','document':k,'decision':'경계 유지·민감도 제외','reason':v} for k,v in BOUNDARY.items()]
for i in [30,33]:
    r=imm_sample[i-1]
    rechecks.append({'technology':'Immersion','document':r['Display Key'],'decision':'유지(기존 비관련 판정 수정)',
        'reason':'초록에 전자 발열부품의 침지 또는 immersive pods/immersion tanks가 명시됨. 공기/컨테이너 냉각만 다룬다는 기존 설명을 수정.'})
write('screening_rechecks.csv',rechecks)

# Exact subgroup codes + explicit prefix groups. H05K7/20281 belongs to control.
GROUPS={
 '유체 순환·연결 부속':{'exact':['H05K7/20272','H05K7/20327'],'prefix':['F04','F16L']},
 '열·유량 제어':{'exact':['H05K7/20281','H05K7/20381','H05K7/207','H05K7/20836','G06F1/206'],'prefix':['G05B','G05D']},
 '건물·공조 분류':{'exact':[],'prefix':['E04B','E04F','E04H','F24F']}}
def has_group(r,g):
    cs=cpcs(r); return bool(cs.intersection(g['exact'])) or any(c.startswith(tuple(g['prefix'])) for c in cs)
def metrics(rows):
    recent=[r for r in rows if 2015<=year(r)<=2024]
    full=Counter();frac=Counter(); first={}
    for r in rows:
        for a in apps(r): first[a]=min(year(r),first.get(a,9999))
    for r in recent:
        aa=apps(r)
        for a in aa: full[a]+=1;frac[a]+=1/len(aa)
    n1=sum(2013<=year(r)<=2017 for r in rows);n2=sum(2018<=year(r)<=2022 for r in rows)
    return {'total':len(rows),'recent':len(recent),'period1':n1,'period2':n2,'growth_pct':100*(n2/n1-1),
      'pair_denominator':sum(full.values()),'fractional_denominator':sum(frac.values()),
      'hhi_full':sum((v/sum(full.values()))**2 for v in full.values()),
      'hhi_fractional':sum((v/sum(frac.values()))**2 for v in frac.values()),
      'cr4':sum(v for k,v in full.most_common(4))/sum(full.values()),
      'top_applicants':[{'name':k,'count':v,'share':v/sum(full.values()),'fractional_count':frac[k]} for k,v in full.most_common()],
      'new_applicants_2015_19':sum(2015<=v<=2019 for v in first.values())/5,
      'new_applicants_2020_24':sum(2020<=v<=2024 for v in first.values())/5,
      'annual':[{'year':y,'families':sum(year(r)==y for r in rows)} for y in range(2000,2025)]}

data={}; audit=[]; cpcrows=[]; yearly=[]; concentration=[]; inputs=[]
for tech,t in [('DLC','dlc'),('Immersion','imm')]:
    p=T1/f'clean/us_{t}_families.csv';old=read(p)
    inputs.append({'file':str(p.relative_to(BASE)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':len(old)})
    assert len({family(r) for r in old})==len(old)
    reviewed=[r for r in old if tech!='DLC' or r['Display Key'] not in EXCLUDE]
    strict=[r for r in reviewed if tech!='DLC' or r['Display Key'] not in BOUNDARY]
    assert all(r['Jurisdiction']=='US' and '2000-01-01'<=r['Application Date']<='2024-12-31' for r in old)
    write(f'us_{t}_reviewed.csv',reviewed)
    data[tech]={'original':metrics(old),'reviewed':metrics(reviewed),'strict_boundary_excluded':metrics(strict)}
    for version,rr in [('original',old),('reviewed',reviewed),('strict_boundary_excluded',strict)]:
        mm=metrics(rr)
        audit.append({'technology':tech,'version':version,**{k:v for k,v in mm.items() if k not in ['top_applicants','annual']}})
    for period,lo,hi in [('2015–2019',2015,2019),('2020–2024',2020,2024),('2015–2024',2015,2024)]:
        rr=[r for r in reviewed if lo<=year(r)<=hi]
        for name,g in GROUPS.items():
            count=sum(has_group(r,g) for r in rr)
            cpcrows.append({'technology':tech,'group':name,'period':period,'count':count,'denominator':len(rr),'share':count/len(rr)})
    yearly += [{'technology':tech,**r} for r in data[tech]['reviewed']['annual']]
    concentration += [{'technology':tech,**r} for r in data[tech]['reviewed']['top_applicants']]
    assert abs(data[tech]['reviewed']['fractional_denominator']-data[tech]['reviewed']['recent'])<1e-8

a=read(OUT/'us_dlc_reviewed.csv');b=read(OUT/'us_imm_reviewed.csv')
overlap=len({family(r) for r in a}&{family(r) for r in b})
write('metrics_comparison.csv',audit);write('annual_families.csv',yearly);write('applicant_concentration.csv',concentration);write('cpc_corrected.csv',cpcrows)
write('cpc_definitions.csv',[{'group':k,'exact_codes':';'.join(v['exact']),'prefix_codes':';'.join(v['prefix']),
 'source':'https://www.cooperativepatentclassification.org/cpc/scheme/H/scheme-H05K.pdf; https://www.cooperativepatentclassification.org/cpc/scheme/G/scheme-G06F.pdf',
 'note':'최소한의 기능별 비교용 분류. 전체 기술체계의 완전한 분할이 아님; 중복 가능.'} for k,v in GROUPS.items()])
out={'as_of':'2026-11-17','source_search_date':'2026-11-09','inputs':inputs,'metrics':data,'cpc':cpcrows,
 'overlap_reviewed_families':overlap,'unique_union':len(a)+len(b)-overlap,
 'precision_note':'팀원1의 무작위 표본 중 논쟁 사례만 재검토했다. 독립 재표본검사가 아니므로 새 precision 추정치로 발표하지 않는다.',
 'checks':{'family_unique':True,'US_and_filed_filter':True,'fractional_count_sums':True,
 'original_DLC_451':len(read(T1/'clean/us_dlc_families.csv'))==451,'original_Immersion_163':len(b)==163,
 'four_DLC_removed':len(a)==447,'core_20_unchanged':len(read(T1/'handoff/US_핵심특허_팀원2반환.csv'))==20}}
# Existing fit output remains an original-cohort diagnostic, not a fit on our revised cohort.
try:
 import pandas as pd
 fits=[]
 for tech in ['DLC','Immersion']:
  df=pd.read_excel(T1/'analysis/특허분석_결과.xlsx',sheet_name=f'{tech}_S커브',header=None)
  for _,r in df.iterrows():
   if r.iloc[0] in ['Logistic','Gompertz'] and r.iloc[1] in [2019,2020,2021]:
    fits.append({'technology':tech,'model':r.iloc[0],'year':int(r.iloc[1]),'observed':float(r.iloc[2]),'predicted':float(r.iloc[3]),'error':float(r.iloc[4])})
 assert len(fits)==12
 write('scurve_existing_holdout.csv',fits);out['scurve_holdout']=fits
except ImportError:
 pass
(OUT/'analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({'metrics':audit,'overlap':overlap,'cpc':cpcrows},ensure_ascii=False,indent=2))
