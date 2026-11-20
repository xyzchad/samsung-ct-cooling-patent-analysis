"""CPC 교차검증: 데이터센터·서버 액체냉각 CPC가 있지만 server/data center/rack 단어가 없는 특허를 판정한다.
사용법: python cpc_check.py <repo root> <out csv> <csv1> [csv2 ...]
결과의 판정 열이 keyword_check_cpc.csv의 판정이다. 표본점검 열(무작위 55건 수작업 확인)은 그 뒤에 손으로 붙였다."""
import sys,re,pandas as pd
root,out,files=sys.argv[1],sys.argv[2],sys.argv[3:]
d=pd.concat([pd.read_csv(f) for f in files],ignore_index=True).drop_duplicates('Lens ID')
def fam(r): return set([r['Lens ID']]+[x.strip() for x in str(r['Simple Family Members']).split(';;') if x.strip() and x!='nan'])
base=set()
for f in ['us_dlc_all','us_imm_all']:
    b=pd.read_csv(f'{root}/data/raw/lens_us/{f}.csv')
    for _,r in b.iterrows(): base|=fam(r)
d['in_base']=d.apply(lambda r: bool(fam(r)&base),axis=1)
DCCPC=['H05K7/20763','H05K7/20772','H05K7/20781','H05K7/2079','H05K7/20809','H05K7/20818','H05K7/20827']
cp=lambda s:[x.strip() for x in str(s).split(';;')]
d['dc_cpc']=d['CPC Classifications'].apply(lambda s:any(c in cp(s) for c in DCCPC))
t=(d.Title.fillna('')+' . '+d.Abstract.fillna('')).str.lower()
EXCL=r'vehicle|automotive|\bcar\b|battery|batteries|laser|medical|inverter|transformer|power magnetic|lithograph|aircraft|spacecraft|charging station|charger|electric motor|power conver|photovoltaic|led lamp|projector|semiconductor (?:wafer|manufactur)|wafer|test(?:ing)? (?:apparatus|equipment|socket)'
IMM=r'immers|submerg|dielectric (?:liquid|fluid|coolant)|two-phase (?:cooling )?tank|immersion'
LIQ=r'cold plate|cold-plate|cooling plate|liquid[- ]cool|coolant|water[- ]cool|water block|liquid|cooling fluid|working fluid|refrigerant|spray|coolant distribution|\bcdu\b|chilled water|heat transfer fluid|pump|(?<!air )(?<!gas )\bfluid|cooling loop|cold plates'
COMP=r'comput|processor|\bcpu|\bgpu|chip|electronic|information handling|\bit (?:equipment|component|device)|blade|motherboard|circuit board|mining|data processing|memory|dimm|accelerator|heat[- ]generating|heat generating|asic|information handling|\bihs\b|cold plate'
AIRC=r'air[- ]condition|air handl|\bcrac\b|computer room air|fan wall|air wall|evaporative|room air|cooling air|airflow|air flow|air[- ]cool'
STRONG=r'cold plate|cold-plate|liquid[- ]cool|coolant|water[- ]cool|water block|cooling plate|cooling liquid|liquid cooling'
CHEM=r'^(?:[^.]*)(?:compound|composition|perfluor|fluorinated|hydrofluoro|ether|olefin)'
def judge(i):
    s=t[i]; title=str(d.Title.iloc[i]).lower()
    if re.search(EXCL,s): return '비대상','차량·전력기기·장비 등 비IT 용도'
    if re.search(CHEM,title): return '경계','냉매·유체 조성물(냉각 장치 아님)'
    imm=bool(re.search(IMM,s)); liq=bool(re.search(LIQ,s)); comp=bool(re.search(COMP,s))
    if not d.dc_cpc.iloc[i] and not comp: return '비대상','일반 액침(H05K7/20236만), IT 용도 표현 없음'
    if imm: return '관련(액침)',''
    if re.search(AIRC,s) and not re.search(STRONG,s): return '경계','룸 단위 공조(공랭·냉매), 칩·서버 직접 액체냉각 아님'
    if liq: return '관련(DLC)',''
    return '비대상','액체 냉각 표현 없음(공랭 등)'
r=[judge(i) for i in range(len(d))]
d['판정']=[x[0] for x in r]; d['이유']=[x[1] for x in r]
d.loc[d.in_base,'판정']='기존포함'; d.loc[d.in_base,'이유']='기존 검색 결과와 같은 패밀리'
d['최우선연도']=pd.to_datetime(d['Earliest Priority Date']).dt.year
o=d[['Display Key','최우선연도','Applicants','Title','dc_cpc','판정','이유','Lens ID','Simple Family Members','Abstract']].rename(columns={'Display Key':'대표문헌','Applicants':'출원인','Title':'제목','dc_cpc':'DC_CPC'})
o.to_csv(out,index=False,encoding='utf-8-sig')
print(o.판정.value_counts().to_dict())
print(o[o.최우선연도.between(2015,2024)].판정.value_counts().to_dict())
