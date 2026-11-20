import csv,sys,json
from collections import Counter,defaultdict
# 사용법: python recent3.py <저장소 루트> <출력 json>
base=sys.argv[1]; out=sys.argv[2]
def read(p): return list(csv.DictReader(open(p,encoding='utf-8-sig')))
def apps(r): return sorted(set(x.strip() for x in r['applicant_normalized'].split(';') if x.strip()))
def year(r): return int(r['Earliest Priority Date'][:4])
def cpcs(r): return set(x.strip() for x in r['CPC Classifications'].split(';;') if x.strip())
def fam(r): return tuple(sorted(set(r['Simple Family Members'].split(';;'))))
GROUPS={
 '유체 순환·연결 부속':{'exact':['H05K7/20272','H05K7/20327'],'prefix':['F04','F16L']},
 '열·유량 제어':{'exact':['H05K7/20281','H05K7/20381','H05K7/207','H05K7/20836','G06F1/206'],'prefix':['G05B','G05D']},
 '건물·공조 분류':{'exact':[],'prefix':['E04B','E04F','E04H','F24F']}}
def has(r,g):
    cs=cpcs(r); return bool(cs & set(g['exact'])) or any(c.startswith(tuple(g['prefix'])) for c in cs)
# alias merge for names split in normalization
ALIAS={'NAUTILUS TRUE LLC':'NAUTILUS DATA TECH INC','VETTE TECHNOLOGY LLC':'VETTE CORP','RITTAL GMBH & CO. KG':'RITTAL GMBH & CO KG','SUZHOU METABRAIN INTELLIGENT TECH CO LTD':'SUZHOU METABRAIN INTELLIGENT TECHNOLOGY CO LTD','HANGZHOU DARE ROUHAN TECHNOLOGY CO., LTD.':'HANGZHOU DARE ROUHAN TECH CO LTD','ZT GROUP INT’L INC DBA ZT SYSTEMS':'ZT GROUP INTL INC'}
def A(r): return sorted(set(ALIAS.get(a,a) for a in apps(r)))
res={}
data={t:read(f'{base}/data/processed/us_reviewed/us_{k}_reviewed.csv') for t,k in [('DLC','dlc'),('액침','imm')]}
# union
u={}
for t,rows in data.items():
    for r in rows: u.setdefault(fam(r),r)
data['합집합']=list(u.values())
lines=[]
for t,rows in data.items():
    P0=[r for r in rows if 2015<=year(r)<=2021]; P3=[r for r in rows if 2022<=year(r)<=2024]; P10=[r for r in rows if 2015<=year(r)<=2024]
    first={}
    for r in rows:
        for a in A(r): first[a]=min(year(r),first.get(a,9999))
    def top(rs,n=10):
        c=Counter(a for r in rs for a in A(r)); tot=len(rs)
        return [(a,v,v/tot) for a,v in c.most_common(n)],c
    t3,c3=top(P3,12); t10,c10=top(P10,12); _,c0=top(P0,9999)
    # rank in 2015-21
    rank0={a:i+1 for i,(a,v) in enumerate(sorted(c0.items(),key=lambda x:-x[1]))}
    new3=sorted([a for a,y in first.items() if y>=2022])
    grp={g:(sum(has(r,G) for r in P0)/len(P0), sum(has(r,G) for r in P3)/len(P3)) for g,G in GROUPS.items()}
    # subgroup lift: CPC H05K7/2xxxx & others at main-group/subgroup level, families share
    def sh(rs):
        c=Counter(cc for r in rs for cc in cpcs(r)); return {k:v/len(rs) for k,v in c.items()},c
    s0,_=sh(P0); s3,cnt3=sh(P3)
    lift=sorted([(k,cnt3[k],s3[k],s0.get(k,0)) for k in s3 if cnt3[k]>=max(5,0.08*len(P3))],key=lambda x:-(x[2]-x[3]))
    res[t]=dict(n10=len(P10),n0=len(P0),n3=len(P3),by_year={y:sum(year(r)==y for r in rows) for y in range(2015,2025)},
        top3=t3,top10=t10,rank0=rank0,c0=dict(c0),new3_count=len(new3),
        new3_share_of_applicants=len(new3)/len(c3),
        fams_with_new=sum(any(first[a]>=2022 for a in A(r)) for r in P3)/len(P3),
        hhi3=sum((v/sum(c3.values()))**2 for v in c3.values()), cr4_3=sum(v for _,v in c3.most_common(4))/sum(c3.values()),
        grp=grp,lift=lift[:8],lift_down=sorted([(k,cnt3.get(k,0),s3.get(k,0),s0[k]) for k in s0 if s0[k]>=0.15],key=lambda x:(x[2]-x[3]))[:4])
# 제목 기준 시설 단 냉각 특허(CPC 대리지표 보완): 냉동·공조 시스템, 컨테이너·모듈러 데이터센터, 전산실 냉각 등
FAC=r'refrigerat|air[- ]condition|computer room|data room|machine room|container|modular data|chiller|cooling tower|edge data center|heat recovery|building'
import re as _re
for t,rows in data.items():
    P0=[r for r in rows if 2015<=year(r)<=2021]; P3=[r for r in rows if 2022<=year(r)<=2024]
    f0=[r for r in P0 if _re.search(FAC,r['Title'],_re.I)]; f3=[r for r in P3 if _re.search(FAC,r['Title'],_re.I)]
    res[t]['facility_title']={'n0':len(f0),'n3':len(f3),'share0':len(f0)/len(P0),'share3':len(f3)/len(P3),
        'top3':Counter(a for r in f3 for a in A(r)).most_common(3)}
json.dump(res,open(out,'w',encoding='utf-8'),ensure_ascii=False,indent=1,default=str)
for t,d in res.items():
    print('=====',t,'10y',d['n10'],'15-21',d['n0'],'22-24',d['n3'],d['by_year'])
    print('HHI3 %.3f CR4_3 %.1f%% new-applicant share %.0f%% fams w/ new %.0f%%'%(d['hhi3'],100*d['cr4_3'],100*d['new3_share_of_applicants'],100*d['fams_with_new']))
    print('top 22-24:'); [print('  %-45s %3d %5.1f%%  rank15-21:%s (%s)'%(a,v,100*s,d['rank0'].get(a,'-'),d['c0'].get(a,0))) for a,v,s in d['top3']]
    print('top 15-24:'); [print('  %-45s %3d %5.1f%%'%(a,v,100*s)) for a,v,s in d['top10']]
    print('groups:',{g:('%.1f→%.1f'%(100*a,100*b)) for g,(a,b) in d['grp'].items()})
    print('lift up:',[(k,c,'%.0f%%'%(100*s),'%.0f%%'%(100*s0)) for k,c,s,s0 in d['lift']])
    print('lift down:',[(k,c,'%.0f%%'%(100*s),'%.0f%%'%(100*s0)) for k,c,s,s0 in d['lift_down']])
