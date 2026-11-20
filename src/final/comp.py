import csv,sys,re
from collections import Counter
# 사용법: python comp.py <저장소 루트>  (경쟁자별 건수를 화면에 출력)
base=sys.argv[1]
ALIAS={'NAUTILUS TRUE LLC':'NAUTILUS DATA TECH INC','VETTE TECHNOLOGY LLC':'VETTE CORP','RITTAL GMBH & CO. KG':'RITTAL GMBH & CO KG','SUZHOU METABRAIN INTELLIGENT TECH CO LTD':'SUZHOU METABRAIN INTELLIGENT TECHNOLOGY CO LTD','HANGZHOU DARE ROUHAN TECHNOLOGY CO., LTD.':'HANGZHOU DARE ROUHAN TECH CO LTD','ZT GROUP INT’L INC DBA ZT SYSTEMS':'ZT GROUP INTL INC'}
def read(p): return list(csv.DictReader(open(p,encoding='utf-8-sig')))
def year(r): return int(r['Earliest Priority Date'][:4])
def fam(r): return tuple(sorted(set(r['Simple Family Members'].split(';;'))))
u={}
tech={}
for t,k in [('DLC','dlc'),('액침','imm')]:
    for r in read(f'{base}/data/processed/us_reviewed/us_{k}_reviewed.csv'):
        u.setdefault(fam(r),r); tech.setdefault(fam(r),set()).add(t)
# also raw applicants & owners check
COMP={'Vertiv (CoolTera 포함)':r'VERTIV|COOLTERA','Schneider Electric (APC·Motivair 포함)':r'SCHNEIDER|AMERICAN POWER CONV|\bAPC\b|MOTIVAIR',
'Trane (LiquidStack 포함)':r'TRANE|LIQUIDSTACK','Ecolab (CoolIT 포함)':r'ECOLAB|COOLIT','LG전자':r'\bLG ELECTRONICS|LG ELECTRONICS',
'GRC':r'GREEN REVOLUTION|\bGRC\b','삼성물산':r'SAMSUNG C&T|SAMSUNG C & T','현대건설':r'HYUNDAI ENG|HYUNDAI E&C','GS건설':r'GS ENGINEERING|GS E&C',
'DL이앤씨':r'DL E&C|DAELIM','대우건설':r'DAEWOO E&C|DAEWOO ENG','SK에코플랜트':r'SK ECOPLANT|SK ECO PLANT','Nortek (공조)':r'NORTEK'}
allc=Counter()
for f,r in u.items():
    if 2015<=year(r)<=2024:
        for a in set(ALIAS.get(x.strip(),x.strip()) for x in r['applicant_normalized'].split(';') if x.strip()): allc[a]+=1
ranked=sorted(set(allc.values()),reverse=True)
def rank(n): return 1+sum(v>n for v in allc.values())
print('distinct applicants 10y',len(allc),' top10 cutoff',sorted(allc.values(),reverse=True)[9])
for name,pat in COMP.items():
    p=re.compile(pat,re.I)
    hits=[(f,r) for f,r in u.items() if p.search(r['Applicants']+' '+r['applicant_normalized']+' '+r['Owners'])]
    h10=[x for x in hits if 2015<=year(x[1])<=2024]; h3=[x for x in hits if 2022<=year(x[1])<=2024]
    dl=sum('DLC' in tech[f] for f,_ in h10); im=sum('액침' in tech[f] for f,_ in h10)
    via=[ (r['Display Key'],year(r),r['Applicants'][:40],r['Owners'][:60]) for f,r in hits]
    print(f'{name:38s} all{len(hits):3d} 10y{len(h10):3d} (DLC{dl} 액침{im}) 22-24:{len(h3)} rank~{rank(len(h10)) if h10 else "-"}')
    for v in via: print('     ',v)
