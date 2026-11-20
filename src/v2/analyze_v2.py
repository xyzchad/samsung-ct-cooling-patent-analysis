"""V2 분석: V1과 같은 지표를 V2 데이터로 다시 계산하고 V1과 나란히 저장한다.
실행: python src/v2/analyze_v2.py  (build_v2.py 다음)
출력: data/v2/results/*.csv, analysis_v2.json
지표 정의는 V1(src/final/analyze_patents.py, recent3.py, fit_scurves.py, src/us_baseline/build_core_list.py)과 같다.
출원인 이름은 V1 정규화(clean.py) 뒤에 같은 회사의 다른 표기를 ALIAS로 합친다(V1에도 같은 ALIAS를 적용해 비교).
"""
import json, re
from collections import Counter
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parents[2]
P = ROOT/'data/v2/processed'; R = ROOT/'data/v2/results'; R.mkdir(parents=True, exist_ok=True)

ALIAS = {
 'NAUTILUS TRUE LLC': 'NAUTILUS DATA TECH INC', 'VETTE TECHNOLOGY LLC': 'VETTE CORP', 'RITTAL GMBH & CO. KG': 'RITTAL GMBH & CO KG',
 'SUZHOU METABRAIN INTELLIGENT TECH CO LTD': 'SUZHOU METABRAIN INTELLIGENT TECHNOLOGY CO LTD',
 'HANGZHOU DARE ROUHAN TECHNOLOGY CO., LTD.': 'HANGZHOU DARE ROUHAN TECH CO LTD',
 'ZT GROUP INT’L INC DBA ZT SYSTEMS': 'ZT GROUP INTL INC', 'ZT GROUP INTL INC DBA ZT SYSTEMS': 'ZT GROUP INTL INC',
 'LENOVO ENTPR SOLUTIONS SINGAPORE PTE LTD': 'LENOVO', 'LENOVO BEIJING CO LTD': 'LENOVO', 'LENOVO GLOBAL TECH UNITED STATES INC': 'LENOVO',
 'BEIJING LENOVO SOFTWARE LTD': 'LENOVO', 'LENOVO GLOBAL TECHNOLOGY UNITED STATES INC': 'LENOVO',
 'INTEL CORPORATION': 'INTEL CORP', 'NEC PLATFORMS LTD': 'NEC CORP', 'NEC CORPORATION': 'NEC CORP',
 'HUAWEI DIGITAL POWER TECH CO LTD': 'HUAWEI', 'HEWLETT-PACKARD COMPANY': 'HP', 'HEWLETT PACKARD CO': 'HP',
 'INVENTEC CORPORATION': 'INVENTEC', 'INVENTEC TECH CORPORATION': 'INVENTEC',
 'BEIJING BAIDU NETCOM SCI & TECH CO LTD': 'BAIDU', 'BAIDUCOM TIMES TECH (BEIJING) CO LTD': 'BAIDU',
 'ASETEK DANMARK A/S': 'ASETEK', 'VERTIV CORPORATION': 'VERTIV (구 LIEBERT)', 'VERTIV CORP': 'VERTIV (구 LIEBERT)', 'LIEBERT CORP': 'VERTIV (구 LIEBERT)',
 'AMERICAN POWER CONV CORP': 'SCHNEIDER ELECTRIC (구 APC)', 'SCHNEIDER ELECTRIC IT CORP': 'SCHNEIDER ELECTRIC (구 APC)',
 'ICEOTOPE LTD': 'ICEOTOPE GROUP LTD', 'HONGFUJIN PREC IND SHENZHEN': 'FOXCONN (HON HAI)',
 'SHENZHEN FULIAN FUGUI PREC INDUSTRY CO LTD': 'FOXCONN (HON HAI)', 'NANNING FULIAN FUGUI PREC INDUSTRIAL CO LTD': 'FOXCONN (HON HAI)',
 '3M INNOVATIVE PROPERTIES COMPANY': '3M INNOVATIVE PROPERTIES CO', 'ASIA VITAL COMPONENTS CHINA CO LTD': 'ASIA VITAL COMPONENTS CO LTD',
 'EBULLIENT INC': 'EBULLIENT LLC', 'HITACHI PLANT TECHNOLOGIES LTD': 'HITACHI LTD', 'FACEBOOK INC': 'META PLATFORMS INC',
}
def apps(s):
    return sorted(set(ALIAS.get(a.strip(), a.strip()) for a in str(s).replace(';;', ';').split(';') if a.strip() and str(s) != 'nan'))
def fam(s, lid):
    return tuple(sorted(set(str(s).split(';;')))) if str(s) != 'nan' else (lid,)
def rd(path):
    # 새로 만든 CSV가 없으면 저장소의 압축본(.csv.xz)을 읽는다
    path = Path(path)
    return pd.read_csv(path if path.exists() else path.with_suffix(path.suffix + '.xz'))
def load(path):
    d = rd(path)
    d['year'] = pd.to_datetime(d['Earliest Priority Date']).dt.year
    d['apps'] = d['applicant_normalized'].apply(apps)
    d['fam'] = [fam(s, l) for s, l in zip(d['Simple Family Members'], d['Lens ID'])]
    d['cpcs'] = d['CPC Classifications'].apply(lambda s: set(x.strip() for x in str(s).split(';;') if x.strip()))
    return d
V = {}
for t in ['dlc', 'imm']:
    v2 = load(P/f'us_{t}_v2.csv')
    V[('V1', t)] = v2[v2.source == '키워드(V1)'].copy()
    V[('V2', t)] = v2
def union(ver):
    u = pd.concat([V[(ver, 'dlc')], V[(ver, 'imm')]]); return u.drop_duplicates('fam')
for ver in ['V1', 'V2']: V[(ver, 'union')] = union(ver)
TECHS = [('dlc', 'DLC'), ('imm', '액침'), ('union', '합집합')]

GROUPS = {'유체 순환·연결 부속': (['H05K7/20272', 'H05K7/20327'], ['F04', 'F16L']),
          '열·유량 제어': (['H05K7/20281', 'H05K7/20381', 'H05K7/207', 'H05K7/20836', 'G06F1/206'], ['G05B', 'G05D']),
          '건물·공조 분류': ([], ['E04B', 'E04F', 'E04H', 'F24F'])}
def has(cs, g): ex, pre = GROUPS[g]; return bool(cs & set(ex)) or any(c.startswith(tuple(pre)) for c in cs)
FACT = r'refrigerat|air[- ]condition|computer room|data room|machine room|container|modular data|chiller|cooling tower|edge data center|heat recovery|building'

def metrics(d):
    rec = d[d.year.between(2015, 2024)]
    full, frac, first = Counter(), Counter(), {}
    for _, r in d.iterrows():
        for a in r.apps: first[a] = min(r.year, first.get(a, 9999))
    for aa in rec.apps:
        for a in aa: full[a] += 1; frac[a] += 1/len(aa)
    n1 = int(d.year.between(2013, 2017).sum()); n2 = int(d.year.between(2018, 2022).sum())
    s5a = int(d.year.between(2015, 2019).sum()); s5b = int(d.year.between(2020, 2024).sum())
    F, Fr = sum(full.values()), sum(frac.values())
    return dict(total=len(d), recent10=len(rec), p2013_17=n1, p2018_22=n2, growth_pct=round(100*(n2/n1-1), 1),
                p2015_19=s5a, p2020_24=s5b, ratio_20_24_vs_15_19=round(s5b/s5a, 2),
                hhi_full=round(sum((v/F)**2 for v in full.values()), 5), hhi_frac=round(sum((v/Fr)**2 for v in frac.values()), 5),
                cr4=round(sum(v for _, v in full.most_common(4))/F, 3), pair_den=F,
                new_app_15_19=sum(2015 <= v <= 2019 for v in first.values())/5, new_app_20_24=sum(2020 <= v <= 2024 for v in first.values())/5,
                top10=[(a, v, round(v/F, 3)) for a, v in full.most_common(10)],
                annual={int(y): int((d.year == y).sum()) for y in range(2000, 2025)})

def recent3(d):
    first = {}
    for _, r in d.iterrows():
        for a in r.apps: first[a] = min(r.year, first.get(a, 9999))
    P0 = d[d.year.between(2015, 2021)]; P3 = d[d.year.between(2022, 2024)]
    c0 = Counter(a for l in P0.apps for a in l); c3 = Counter(a for l in P3.apps for a in l); t3 = sum(c3.values())
    rank0 = {a: i+1 for i, (a, _) in enumerate(c0.most_common())}
    new = [a for a in c3 if first[a] >= 2022]
    out = dict(n0=len(P0), n3=len(P3), n_app3=len(c3), n_new=len(new), new_share=round(len(new)/len(c3), 3),
               hhi3=round(sum((v/t3)**2 for v in c3.values()), 4), cr4_3=round(sum(v for _, v in c3.most_common(4))/t3, 3),
               top=[(a, v, round(v/len(P3)*100, 1), rank0.get(a, '-'), c0.get(a, 0)) for a, v in c3.most_common(12)])
    out['grp'] = {g: (round(P0.cpcs.apply(lambda s: has(s, g)).mean()*100, 1), round(P3.cpcs.apply(lambda s: has(s, g)).mean()*100, 1)) for g in GROUPS}
    f0 = P0.Title.str.contains(FACT, case=False, regex=True); f3 = P3.Title.str.contains(FACT, case=False, regex=True)
    out['facility_title'] = dict(n0=int(f0.sum()), n3=int(f3.sum()), share0=round(f0.mean()*100, 1), share3=round(f3.mean()*100, 1),
                                 top3=Counter(a for l in P3[f3].apps for a in l).most_common(3))
    return out

def cpc5(d):
    rows = []
    for per, lo, hi in [('2015–2019', 2015, 2019), ('2020–2024', 2020, 2024), ('2015–2024', 2015, 2024)]:
        x = d[d.year.between(lo, hi)]
        for g in GROUPS:
            c = int(x.cpcs.apply(lambda s: has(s, g)).sum()); rows.append(dict(period=per, group=g, count=c, den=len(x), share=round(c/len(x)*100, 1)))
    return rows

res = {}
for ver in ['V1', 'V2']:
    for t, lab in TECHS:
        d = V[(ver, t)]
        res[f'{ver}_{lab}'] = dict(metrics=metrics(d), recent3=recent3(d), cpc=cpc5(d))
res['overlap'] = {ver: int(len(V[(ver, 'dlc')]) + len(V[(ver, 'imm')]) - len(V[(ver, 'union')])) for ver in ['V1', 'V2']}

# ---- S커브 (등록특허, 최우선연도 기준 누적, 적합 2000–2021). V1과 같은 모형·초깃값.
def logistic(t, L, k, t0): return L/(1+np.exp(-k*(t-t0)))
def gompertz(t, L, b, k): return L*np.exp(-b*np.exp(-k*t))
def fit(counts, end):
    years = np.arange(2000, end+1); tt = np.arange(len(years), dtype=float)
    yy = np.cumsum([counts.get(int(y), 0) for y in years]).astype(float); out = {'observed_end': int(yy[-1])}
    for name, f, p0, b in [('Logistic', logistic, [yy[-1]*2, .3, len(tt)], ([yy[-1], .01, 0], [yy[-1]*100, 3, 80])),
                           ('Gompertz', gompertz, [yy[-1]*2, 5, .1], ([yy[-1], .01, .001], [yy[-1]*100, 200, 3]))]:
        p, cov = curve_fit(f, tt, yy, p0=p0, bounds=b, maxfev=200000)
        r2 = 1-float(((yy-f(tt, *p))**2).sum()/((yy-yy.mean())**2).sum())
        out[name] = dict(L=float(p[0]), r2=round(r2, 4), L_rel_se=round(float(np.sqrt(cov[0, 0])/p[0]), 3), L_at_bound=bool(p[0] >= yy[-1]*99),
                         L_over_obs=round(float(p[0]/yy[-1]), 2), params=[float(x) for x in p], f=f)
    return out, years, yy
scurve, curves, holdout = {}, [], []
for ver in ['V1', 'V2']:
    for t, lab in [('dlc', 'DLC'), ('imm', 'Immersion')]:
        g = rd(P/f'us_{t}_v2_granted.csv')
        if ver == 'V1': g = g[g.source == '키워드(V1)']
        cnt = Counter(pd.to_datetime(g['Earliest Priority Date']).dt.year.astype(int))
        o, years, yy = fit(cnt, 2021)
        scurve[f'{ver}_{lab}'] = {'granted_docs': len(g), 'observed_2021': o['observed_end'],
                                  **{m: {k: v for k, v in o[m].items() if k != 'f'} for m in ['Logistic', 'Gompertz']}}
        for m in ['Logistic', 'Gompertz']:
            for y in range(2000, 2026):
                curves.append(dict(version=ver, technology=lab, model=m, year=y, cumulative_fit=float(o[m]['f'](y-2000, *o[m]['params'])),
                                   observed=int(np.cumsum([cnt.get(int(z), 0) for z in range(2000, y+1)])[-1]) if y <= 2024 else None,
                                   segment='fit' if y <= 2021 else 'illustrative_extrapolation'))
        for end in [2018, 2019, 2020]:   # 종료연도 검증: end까지 적합 → 2021 누적 예측 오차
            oe, _, _ = fit(cnt, end); obs21 = o['observed_end']
            for m in ['Logistic', 'Gompertz']:
                pred = float(oe[m]['f'](2021-2000, *oe[m]['params']))
                holdout.append(dict(version=ver, technology=lab, model=m, fit_end=end, pred_2021=round(pred, 1), obs_2021=obs21,
                                    error_pct=round(100*(pred-obs21)/obs21, 1), L=round(oe[m]['L'], 0)))
res['scurve'] = scurve
pd.DataFrame(curves).to_csv(R/'scurve_curves_v2.csv', index=False, encoding='utf-8-sig')
pd.DataFrame(holdout).to_csv(R/'scurve_holdout_v2.csv', index=False, encoding='utf-8-sig')

# ---- 핵심특허 후보 (V1 규칙: 등록특허, 같은 패밀리 1건, 연평균 피인용, 출원연도 2000–2016 / 2017–2024 각 상위 5)
ASOF = pd.Timestamp('2026-11-20')
V1_EXCL = {'US 6775137 B2', 'US 11516943 B2', 'US 9101078 B2'}
core = []
for t, lab in [('dlc', 'DLC'), ('imm', 'Immersion')]:
    g = rd(P/f'us_{t}_v2_granted.csv')
    g['yrs'] = ((ASOF - pd.to_datetime(g['Publication Date'])).dt.days/365.25).clip(lower=1)
    g['annual_cit'] = g['Cited by Patent Count']/g['yrs']
    g['fam'] = [fam(s, l) for s, l in zip(g['Simple Family Members'], g['Lens ID'])]
    g['filing_year'] = pd.to_datetime(g['Application Date']).dt.year
    g = g[~g['Display Key'].isin(V1_EXCL)].sort_values('annual_cit', ascending=False).drop_duplicates('fam')
    for era, lo, hi in [('2000–2016', 2000, 2016), ('2017–2024', 2017, 2024)]:
        top = g[g.filing_year.between(lo, hi)].head(12)
        for i, (_, r) in enumerate(top.iterrows()):
            core.append(dict(technology=lab, stratum=era, rank=i+1, grant_number=r['Display Key'], title=r['Title'],
                             applicant=r['applicant_normalized'], filing_year=int(r.filing_year), cited=int(r['Cited by Patent Count']),
                             annual_citations=round(r.annual_cit, 2), source=r['source'], abstract=str(r['Abstract'])[:400]))
core = pd.DataFrame(core)
# 초록 확인으로 핵심특허에서 뺀 경계 사례 (V1 규칙: 칩·부품에 냉각액을 직접 보내지 않는 랙 측면·후면 공기-액체 열교환, 룸 공조, 시설 단위는 제외)
CORE_EXCL = {
 'US 6374627 B1': '액체 과급 공조기로 찬 공기를 공급하는 룸 공조. DLC 아님',
 'US 7738251 B2': '컨테이너형 모듈에 냉각유체를 공급하는 시설 단위 허브. 칩·부품 직접 냉각이 아님',
 'US 10408545 B2': '장비 배기열을 냉매로 흡수하는 랙 단위 열교환. 칩·부품 직접 냉각이 아님',
 'US 7385810 B2': '랙 후면 도어의 공기-액체 열교환기. V1 제외 기준과 같음',
 'US 7365973 B2': '랙형 냉각기와 유체 배관으로 공기를 식히는 방식. 칩·부품 직접 냉각이 아님',
 'US 6924981 B2': '랙 측면 공기-액체 열교환기와 공랭 결합. V1 제외 기준과 같음',
 'US 7403392 B2': '독립항이 개인용 컴퓨터(PC) 액침 구조. 데이터센터·서버 특허가 아님 (원문 청구항 확인 2026-11-20)',
}
core['core_excluded_reason'] = core.grant_number.map(CORE_EXCL).fillna('')
sel = core[core.core_excluded_reason == ''].groupby(['technology', 'stratum']).head(5).copy()
sel['core_rank'] = sel.groupby(['technology', 'stratum']).cumcount()+1
core['selected_core20'] = core.index.isin(sel.index)
assert len(sel) == 20
v1core = set(pd.read_csv(ROOT/'data/reference/us_core_patents.csv')['grant_number'])
core['in_v1_core20'] = core.grant_number.isin(v1core)
core.to_csv(R/'core_candidates_v2.csv', index=False, encoding='utf-8-sig')

# ---- 경쟁자: V2 검색(합집합)에 걸린 10년·최근 3년 건수
COMP = {'삼성물산': r'SAMSUNG C&T', 'Trane (LiquidStack 포함)': r'TRANE|LIQUIDSTACK', 'Vertiv (Liebert·CoolTera 포함)': r'VERTIV|LIEBERT|COOLTERA',
        'Ecolab (CoolIT 포함)': r'ECOLAB|COOLIT', 'Schneider (APC·Motivair 포함)': r'SCHNEIDER|AMERICAN POWER|MOTIVAIR', 'LG전자': r'LG ELECTRONICS',
        'GRC': r'GREEN REVOLUTION|GRC', 'Baidu': r'BAIDU', 'NVIDIA': r'NVIDIA'}
comp = []
for ver in ['V1', 'V2']:
    u = V[(ver, 'union')]; u10 = u[u.year.between(2015, 2024)]
    for k, pat in COMP.items():
        m = u10.apps.apply(lambda l: any(re.search(pat, a) for a in l))
        comp.append(dict(version=ver, competitor=k, n10=int(m.sum()), n3=int((m & u10.year.between(2022, 2024)).sum()),
                         dlc=int(V[(ver, 'dlc')].pipe(lambda x: x[x.year.between(2015, 2024)]).apps.apply(lambda l: any(re.search(pat, a) for a in l)).sum()),
                         imm=int(V[(ver, 'imm')].pipe(lambda x: x[x.year.between(2015, 2024)]).apps.apply(lambda l: any(re.search(pat, a) for a in l)).sum())))
pd.DataFrame(comp).to_csv(R/'competitors_v2.csv', index=False, encoding='utf-8-sig')
res['competitors'] = comp

# ---- 저장
rows = []
for k in [f'{v}_{lab}' for v in ['V1', 'V2'] for _, lab in TECHS]:
    m = res[k]['metrics']; r3 = res[k]['recent3']
    rows.append(dict(key=k, **{x: m[x] for x in ['total', 'recent10', 'p2013_17', 'p2018_22', 'growth_pct', 'p2015_19', 'p2020_24', 'ratio_20_24_vs_15_19',
                                               'hhi_full', 'hhi_frac', 'cr4', 'pair_den', 'new_app_15_19', 'new_app_20_24']},
                     top1=m['top10'][0][0], n3=r3['n3'], new_share3=r3['new_share'], hhi3=r3['hhi3'], cr4_3=r3['cr4_3'], top1_recent3=r3['top'][0][0]))
pd.DataFrame(rows).to_csv(R/'metrics_v1_v2.csv', index=False, encoding='utf-8-sig')
pd.DataFrame([dict(version=v, technology=lab, year=y, families=n) for v in ['V1', 'V2'] for _, lab in TECHS
              for y, n in res[f'{v}_{lab}']['metrics']['annual'].items()]).to_csv(R/'annual_families_v2.csv', index=False, encoding='utf-8-sig')
pd.DataFrame([dict(version=v, technology=lab, rank=i+1, applicant=a, count=n, share=s) for v in ['V1', 'V2'] for _, lab in TECHS
              for i, (a, n, s) in enumerate(res[f'{v}_{lab}']['metrics']['top10'])]).to_csv(R/'applicants_top10_v2.csv', index=False, encoding='utf-8-sig')
pd.DataFrame([dict(version=v, technology=lab, rank=i+1, applicant=a, n_2022_24=n, pct=p, rank_2015_21=r0, n_2015_21=c0) for v in ['V1', 'V2'] for _, lab in TECHS
              for i, (a, n, p, r0, c0) in enumerate(res[f'{v}_{lab}']['recent3']['top'])]).to_csv(R/'recent3_applicants_v2.csv', index=False, encoding='utf-8-sig')
pd.DataFrame([dict(version=v, technology=lab, **row) for v in ['V1', 'V2'] for _, lab in TECHS for row in res[f'{v}_{lab}']['cpc']]).to_csv(R/'cpc_groups_v2.csv', index=False, encoding='utf-8-sig')
(R/'analysis_v2.json').write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
print(pd.DataFrame(rows).to_string())
