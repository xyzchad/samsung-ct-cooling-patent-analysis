"""V2 데이터 구성: 기존 키워드 검색(A·B) 판정 결과 + CPC 검색(V2-CPC)에서 새로 들어온 패밀리.
실행: python src/v2/build_v2.py   (저장소 루트에서)
입력
  data/processed/us_reviewed/us_{dlc,imm}_reviewed.csv   기존 판정 패밀리 (V1 그대로 유지)
  data/processed/us_baseline/us_{dlc,imm}_granted.csv    기존 등록특허
  data/raw/lens_us/us_{dlc,imm}_all.csv                   기존 원자료 (기존 제외 패밀리 대조용)
  data/raw/lens_us/v2/v2_fam_*.csv, v2_grant_*.csv        V2-CPC 검색 (2026-11-20)
출력 (data/v2/processed/)
  cpc_only_screening.csv   CPC로만 들어온 패밀리의 판정·기술 태그
  us_dlc_v2.csv, us_imm_v2.csv              V2 패밀리 (기술별, 둘 다 해당하면 양쪽에 포함)
  us_dlc_v2_granted.csv, us_imm_v2_granted.csv  V2 등록특허 (문서 단위, S커브·핵심특허용)
판정 원칙
  - 키워드 검색 결과는 V1 판정을 그대로 쓴다(V1과 비교 가능하게).
  - CPC로만 들어온 패밀리는 제목·초록 규칙으로 판정한다. 관련 기준은 V1과 같다:
    데이터센터·서버의 열을 액체로 제거하는 장치·방법·시스템, 전용 냉각액(소재) 포함.
    차량·전력기기·항공 등 비IT 용도, 공랭만 다루는 특허는 비대상.
    일반 PC 수냉, 룸 단위 공조, 시설 칠러만 다루는 특허는 경계로 두고 본 집계에서 뺀다.
  - 기술 태그는 V1 검색식 논리를 따른다. 액침 표현이 있으면 액침, DLC 핵심 표현도 있고 제목에
    immersion이 없으면 둘 다, 액침 표현이 없으면 DLC.
"""
import re, glob
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT/'data/raw/lens_us'; OUT = ROOT/'data/v2/processed'; OUT.mkdir(parents=True, exist_ok=True)
_ns = {}; exec(open(ROOT/'src/us_baseline/clean.py', encoding='utf-8').read().split('def members')[0].replace('os.chdir(Path(__file__).resolve().parent)', ''), _ns)
norm_list = _ns['norm_list']  # V1과 같은 출원인 정규화

def mem(r):
    s = set(x.strip() for x in str(r['Simple Family Members']).split(';;') if x.strip() and str(r['Simple Family Members']) != 'nan')
    return s | {r['Lens ID']}

# ---- 기존 판정
rev = {t: pd.read_csv(ROOT/f'data/processed/us_reviewed/us_{t}_reviewed.csv') for t in ['dlc', 'imm']}
gr1 = {t: pd.read_csv(ROOT/f'data/processed/us_baseline/us_{t}_granted.csv') for t in ['dlc', 'imm']}
rawv1 = pd.concat([pd.read_csv(RAW/f'us_{t}_all.csv') for t in ['dlc', 'imm']])
v1ids = set().union(*[mem(r) for _, r in rawv1.iterrows()])   # 기존 검색에 걸렸던 모든 패밀리(제외분 포함)

# ---- V2-CPC 패밀리
fam = pd.concat([pd.read_csv(f).assign(src_file=Path(f).name) for f in sorted(glob.glob(str(RAW/'v2/v2_fam_*.csv*')))], ignore_index=True)
n_raw = len(fam)
# 날짜 구간 경계에서 같은 패밀리가 두 파일에 들어갈 수 있으므로 패밀리 구성원으로 중복 제거
seen, keep = set(), []
for i, r in fam.iterrows():
    m = mem(r)
    keep.append(not (m & seen)); seen |= m
fam = fam[keep].copy()
n_dedup = len(fam)
fam['in_v1'] = fam.apply(lambda r: bool(mem(r) & v1ids), axis=1)
fam = fam[fam['Document Type'] != 'Design Right']
new = fam[~fam.in_v1].copy()
new['Earliest Priority Date'] = new['Earliest Priority Date'].fillna(new['Application Date'])  # 우선권 정보가 없는 1건은 출원일로 대체

T = lambda r: (str(r['Title']) + ' . ' + str(r['Abstract'])).lower()
EXCL = (r'vehicle|automotive|\bcar\b|battery|batteries|laser|medical|inverter|transformer|power magnetic|lithograph|aircraft|spacecraft|'
        r'avionic|aerospace|missile|radar|military|naval|\bship\b|subsea|underwater|superconduct|charging station|charger|electric motor|'
        r'motor drive|power conver|power electronic|power module|power semiconductor|power circuit|photovoltaic|led lamp|projector|'
        r'wafer|semiconductor manufactur|test(?:ing)? (?:apparatus|equipment|socket)|x-ray|mri\b|welding|fuel cell|nuclear|food|beverage|motor controller|junction box|leadframe|thermal regulation')
PC = r'personal computer|desktop|gaming|notebook|laptop|graphics card|video card|computer case|computer host|\bpc\b|all-in-one|cpu cooler|liquid cooler'
IMM = r'immers|submerg|submers|dielectric (?:liquid|fluid|coolant)|two-phase (?:cooling )?tank'
DLCKW = (r'cold plate|cold-plate|coldplate|cooling plate|direct liquid cooling|direct-to-chip|coolant distribution unit|liquid cooling|'
         r'liquid cooled|liquid-cooled|water[- ]cool|water block|cold block')
LIQ = (DLCKW + r'|coolant|liquid|cooling fluid|working fluid|refrigerant|spray|\bcdu\b|chilled water|heat transfer fluid|pump|'
       r'(?<!air )(?<!gas )\bfluid|cooling loop|thermosiphon|thermosyphon|evaporator|condenser|manifold|inlet pipe|outlet pipe|flow inlet|flow outlet|flow channel|flow path')
# 히트파이프·베이퍼챔버만 있는 특허는 액체 순환 냉각이 아니므로 LIQ에서 뺐다(표본 점검 1차 결과).
COMP = (r'comput|processor|\bcpu|\bgpu|chip|electronic|information handling|\bihs\b|\bit (?:equipment|component|device)|blade|'
        r'motherboard|circuit board|mining|data processing|memory|dimm|accelerator|heat[- ]generating|asic|cold plate|server|rack|data cent')
AIRC = (r'air[- ]condition|air handl|\bcrac\b|computer room air|fan wall|air wall|evaporative|room air|cooling air|airflow|air flow|air[- ]cool')
STRONG = r'cold plate|cold-plate|liquid[- ]cool|coolant|water[- ]cool|water block|cooling plate|cooling liquid|immers|submerg|dielectric'
COMPONENT = r'heating element|heat[- ]generating|processor|\bchip|\bcpu|\bgpu'  # 부품에 직접 붙는 냉각이면 룸 공조가 아님
FAC = r'chiller|cooling tower|dry cooler|waste heat|heat recovery|boiler'
PCHEAD = r'water[- ]cooling head|water[- ]cooled head|cooling head|radiator'
IDC = r'server|rack|data cent|cabinet|blade|information handling'
POWER = r'busbar|bus bar|power delivery|power distribution|wire harness'
DCCPC = {'H05K7/20763', 'H05K7/20772', 'H05K7/20781', 'H05K7/2079', 'H05K7/20809', 'H05K7/20818', 'H05K7/20827'}
cp = lambda s: set(x.strip() for x in str(s).split(';;'))

def judge(r):
    s = T(r); title = str(r['Title']).lower(); dc = bool(cp(r['CPC Classifications']) & DCCPC)
    if re.search(EXCL, s): return '비대상', '차량·전력기기·항공·장비 등 비IT 용도', ''
    if not dc and not re.search(COMP, s) and not (re.search(IMM, title) or (re.search(IMM, s) and re.search(r'tank|bath|server|rack|data|comput|electronic (?:device|equipment)', s))):
        return '비대상', '일반 액침 분류(H05K7/20236)만 있고 IT 용도 표현 없음', ''
    if re.search(PC, s) or (re.search(PCHEAD, title) and not re.search(IDC, s)): return '경계', '일반 PC 수냉', ''
    if re.search(POWER, title) and not re.search(STRONG, s): return '비대상', '전력 공급·배선 중심', ''
    imm = bool(re.search(IMM, s)); dk = bool(re.search(DLCKW, s)) and 'immers' not in title
    if not imm and not re.search(LIQ, s): return '비대상', '액체 냉각 표현 없음(공랭 등)', ''
    if not imm and re.search(r'air[- ]cooled', s) and not re.search(STRONG, s): return '경계', '룸 단위 공조(공랭·냉매), 칩·서버 직접 액체냉각 아님', ''
    if not imm and re.search(AIRC, s) and not re.search(STRONG + '|' + COMPONENT, s): return '경계', '룸 단위 공조(공랭·냉매), 칩·서버 직접 액체냉각 아님', ''
    if not imm and re.search(FAC, s) and not re.search(STRONG, s): return '경계', '시설 칠러·냉각탑 중심', ''
    tech = '둘 다' if (imm and dk) else ('액침' if imm else 'DLC')
    return '관련', '', tech

j = new.apply(judge, axis=1, result_type='expand'); new[['판정', '이유', '기술']] = j
new['최우선연도'] = pd.to_datetime(new['Earliest Priority Date']).dt.year
new['applicant_normalized'] = [';; '.join(norm_list(a, o)) for a, o in zip(new['Applicants'], new['Owners'])]
cols = ['Display Key', '최우선연도', 'Applicants', 'applicant_normalized', 'Title', '판정', '이유', '기술', 'Lens ID', 'src_file']
new[cols].to_csv(OUT/'cpc_only_screening.csv', index=False, encoding='utf-8-sig')

# ---- V2 패밀리 = 기존 판정 + CPC 신규 관련
add = new[new.판정 == '관련'].copy()
add['source'] = 'CPC'; add['both_tech'] = add.기술 == '둘 다'; add['boundary_tag'] = ''
out = {}
for t, lab in [('dlc', 'DLC'), ('imm', '액침')]:
    base = rev[t].copy(); base['source'] = '키워드(V1)'
    a = add[add.기술.isin([lab, '둘 다'])].drop(columns=['판정', '이유', '기술', '최우선연도', 'src_file', 'in_v1'])
    v2 = pd.concat([base, a], ignore_index=True)
    v2['technology'] = 'DLC' if t == 'dlc' else 'Immersion'
    v2.to_csv(OUT/f'us_{t}_v2.csv', index=False, encoding='utf-8-sig'); out[t] = v2

# ---- V2 등록특허 (문서 단위). V2 패밀리에 속하면 그 기술 태그를 따른다.
g2 = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(str(RAW/'v2/v2_grant_*.csv*')))], ignore_index=True).drop_duplicates('Lens ID')
g2 = g2[g2['Document Type'] == 'Granted Patent'].copy()
g2['Earliest Priority Date'] = g2['Earliest Priority Date'].fillna(g2['Application Date'])
fam_of = {}
for t in ['dlc', 'imm']:
    for _, r in out[t].iterrows():
        for m in mem(r): fam_of.setdefault(m, set()).add(t)
excluded_ids = set().union(*[mem(r) for _, r in new[new.판정 != '관련'].iterrows()]) | (v1ids - set(fam_of))
gstat = []
for t, lab in [('dlc', 'DLC'), ('imm', '액침')]:
    base = gr1[t].copy(); base['source'] = '키워드(V1)'
    have = set(base['Lens ID'])
    rows = []
    for _, r in g2.iterrows():
        if r['Lens ID'] in have: continue
        m = mem(r); tags = set().union(*[fam_of.get(x, set()) for x in m])
        if tags:
            if t in tags: rows.append(r)
        elif m & excluded_ids:
            continue
        else:  # 패밀리 대표가 기간 밖이라 패밀리 파일에 없던 문서: 같은 규칙으로 판정
            d, _, tech = judge(r)
            if d == '관련' and (lab == tech or tech == '둘 다'): rows.append(r)
    a = pd.DataFrame(rows)
    if len(a):
        a['source'] = 'CPC'; a['technology'] = 'DLC' if t == 'dlc' else 'Immersion'
        a['applicant_normalized'] = [';; '.join(norm_list(x, o)) for x, o in zip(a['Applicants'], a['Owners'])]
    v2g = pd.concat([base, a], ignore_index=True).drop_duplicates('Lens ID')
    v2g.to_csv(OUT/f'us_{t}_v2_granted.csv', index=False, encoding='utf-8-sig')
    gstat.append((t, len(base), len(v2g)))

print('V2-CPC 패밀리 원행', n_raw, '구간 중복 제거 후', n_dedup, '기존 검색과 겹침', int(fam.in_v1.sum()), '신규', len(new))
print(new.판정.value_counts().to_dict(), add.기술.value_counts().to_dict())
for t in ['dlc', 'imm']:
    print(t, 'V1', len(rev[t]), 'V2', len(out[t]))
print('granted', gstat)
