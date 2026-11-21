"""CPC 교차검증 결과가 기존 결론(추이·주도기업·집중도)을 바꾸는지 본다.
사용법: python cpc_impact.py <repo root> <keyword_check_cpc.csv> <out json> data/raw/lens_us/us_cpc_check1.csv us_cpc_check2.csv us_cpc_check3.csv"""
import sys,json,re,importlib.util,pandas as pd
from collections import Counter
root,jc,out=sys.argv[1:4]
spec=importlib.util.spec_from_file_location('clean',f'{root}/src/us_baseline/clean.py')
src=open(f'{root}/src/us_baseline/clean.py',encoding='utf-8').read().split('def members')[0].replace('os.chdir(Path(__file__).resolve().parent)','')
ns={};exec(src,ns);norm=ns['norm_list']
ALIAS={'NAUTILUS TRUE LLC':'NAUTILUS DATA TECH INC','VETTE TECHNOLOGY LLC':'VETTE CORP','RITTAL GMBH & CO. KG':'RITTAL GMBH & CO KG','SUZHOU METABRAIN INTELLIGENT TECH CO LTD':'SUZHOU METABRAIN INTELLIGENT TECHNOLOGY CO LTD','HANGZHOU DARE ROUHAN TECHNOLOGY CO., LTD.':'HANGZHOU DARE ROUHAN TECH CO LTD','ZT GROUP INT’L INC DBA ZT SYSTEMS':'ZT GROUP INTL INC','LENOVO ENTPR SOLUTIONS SINGAPORE PTE LTD':'LENOVO','LENOVO GLOBAL TECHNOLOGY UNITED STATES INC':'LENOVO'}
A=lambda names:sorted(set(ALIAS.get(a.strip(),a.strip()) for a in names if a.strip()))
rows=[]
for t,k in [('DLC','dlc'),('액침','imm')]:
    b=pd.read_csv(f'{root}/data/processed/us_reviewed/us_{k}_reviewed.csv')
    for _,r in b.iterrows():
        rows.append(dict(src='기존',tech=t,year=int(str(r['Earliest Priority Date'])[:4]),apps=A(str(r.applicant_normalized).split(';')),fam=tuple(sorted(str(r['Simple Family Members']).split(';;')))))
c=pd.read_csv(jc)
for _,r in c[c.판정.str.startswith('관련')].iterrows():
    rows.append(dict(src='CPC추가',tech='액침' if '액침' in r.판정 else 'DLC',year=int(r.최우선연도),apps=A(norm(r.출원인)),fam=(r['Lens ID'],)))
d=pd.DataFrame(rows); d=d[d.year.between(2015,2024)]
res={}
def stats(x):
    yr={y:int((x.year==y).sum()) for y in range(2015,2025)}
    g=sum(yr[y] for y in range(2020,2025))/max(1,sum(yr[y] for y in range(2015,2020)))
    c10=Counter(a for l in x.apps for a in l); p3=x[x.year>=2022]; c3=Counter(a for l in p3.apps for a in l)
    tot3=sum(c3.values())
    return dict(n=len(x),by_year=yr,growth_20_24_vs_15_19=round(g,2),top10=c10.most_common(10),top5_recent3=c3.most_common(5),
                hhi3=round(sum((v/tot3)**2 for v in c3.values()),4),cr4_3=round(sum(v for _,v in c3.most_common(4))/tot3,3),n3=len(p3))
for t in ['DLC','액침']:
    x=d[d.tech==t]
    res[t]={'기존':stats(x[x.src=='기존']),'CPC추가만':stats(x[x.src=='CPC추가']),'합산':stats(x)}
json.dump(res,open(out,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
for t,v in res.items():
    print('=====',t)
    for k,s in v.items():
        print(k,'n',s['n'],'growth',s['growth_20_24_vs_15_19'],'hhi3',s['hhi3'],'cr4',s['cr4_3'])
        print('  year',list(s['by_year'].values()))
        print('  top10',[(a[:22],n) for a,n in s['top10']])
        print('  top5 recent3',[(a[:22],n) for a,n in s['top5_recent3']])

# ---- 합집합 기준 최근 3년 주도기업·집중도·CPC 기능군 (14.4절 비교용)
cp=lambda s:set(x.strip() for x in str(s).split(';;') if x.strip())
GROUPS={'유체 순환·연결 부속':(['H05K7/20272','H05K7/20327'],['F04','F16L']),'열·유량 제어':(['H05K7/20281','H05K7/20381','H05K7/207','H05K7/20836','G06F1/206'],['G05B','G05D'])}
def grp(cs,g): ex,pre=GROUPS[g]; return bool(cs&set(ex)) or any(c.startswith(tuple(pre)) for c in cs)
U={}
for k in ['dlc','imm']:
    b=pd.read_csv(f'{root}/data/processed/us_reviewed/us_{k}_reviewed.csv')
    for _,r in b.iterrows():
        f=tuple(sorted(str(r['Simple Family Members']).split(';;')))
        U.setdefault(f,dict(src='기존',year=int(str(r['Earliest Priority Date'])[:4]),apps=A(str(r.applicant_normalized).split(';')),cpc=cp(r['CPC Classifications'])))
for _,r in c[c.판정.str.startswith('관련')].iterrows():
    U[(r['Lens ID'],)]=dict(src='CPC추가',year=int(r.최우선연도),apps=A(norm(r.출원인)),cpc=None)
raw=pd.concat([pd.read_csv(f) for f in sys.argv[4:]]) if len(sys.argv)>4 else None
if raw is not None:
    m=dict(zip(raw['Lens ID'],raw['CPC Classifications']))
    for k,v in U.items():
        if v['cpc'] is None: v['cpc']=cp(m.get(k[0],''))
uu=pd.DataFrame(U.values())
out2={}
for lab,x in [('기존',uu[uu.src=='기존']),('합산',uu)]:
    first={}
    for _,r in x.iterrows():
        for a in r.apps: first[a]=min(r.year,first.get(a,9999))
    P0=x[x.year.between(2015,2021)];P3=x[x.year.between(2022,2024)]
    c3=Counter(a for l in P3.apps for a in l);c0=Counter(a for l in P0.apps for a in l);t3=sum(c3.values())
    rank0={a:i+1 for i,(a,_) in enumerate(c0.most_common())}
    new=[a for a in c3 if first[a]>=2022]
    o=dict(n3=len(P3),n0=len(P0),top8=[(a,v,round(v/len(P3)*100,1),rank0.get(a,'-'),c0.get(a,0)) for a,v in c3.most_common(8)],
           new_share=round(len(new)/len(c3),3),n_new=len(new),n_app=len(c3),hhi3=round(sum((v/t3)**2 for v in c3.values()),4),cr4=round(sum(v for _,v in c3.most_common(4))/t3,3))
    if raw is not None or lab=='기존':
        o['grp']={g:(round(P0.cpc.apply(lambda s:grp(s,g)).mean()*100,1),round(P3.cpc.apply(lambda s:grp(s,g)).mean()*100,1)) for g in GROUPS}
    out2[lab]=o
    print('====',lab,{k:v for k,v in o.items() if k!='top8'})
    for t in o['top8']: print('  ',t)
res['합집합_최근3년']=out2
json.dump(res,open(out,'w',encoding='utf-8'),ensure_ascii=False,indent=1,default=str)
