"""V2 그림. 실행: python src/v2/figs_v2.py  (analyze_v2.py, claims_v2.py 다음)
출력: deliverables/v2/figures/*.png, editable/*.svg. 스타일은 V1 그림(src/final/render_figures.py)과 같다.
05·06은 미국 검색 데이터와 무관해서 V1 그림을 그대로 쓴다.
"""
import json, os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/mpl')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from matplotlib import font_manager as fm
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[2]; R = ROOT/'data/v2/results'
FIG = ROOT/'deliverables/v2/figures'; (FIG/'editable').mkdir(parents=True, exist_ok=True)
for f in fm.findSystemFonts():
    if 'NotoSansCJK' in f: fm.fontManager.addfont(f)
mac = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
fam = 'Noto Sans CJK KR'
if Path(mac).exists(): fm.fontManager.addfont(mac); fam = fm.FontProperties(fname=mac).get_name()
plt.rcParams.update({'font.family': fam, 'font.size': 16, 'axes.unicode_minus': False, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.labelcolor': '#24344a', 'text.color': '#172c48', 'axes.edgecolor': '#b4bfcc', 'xtick.color': '#405269',
                     'ytick.color': '#405269', 'svg.fonttype': 'none'})
BLUE = '#355cbb'; TEAL = '#13857c'; LBLUE = '#c7d4ee'; LTEAL = '#bfe3de'; GRAY = '#e7ebf1'; INK2 = '#59677a'
A = json.loads((R/'analysis_v2.json').read_text(encoding='utf-8'))
checks = []
INPLACE = {'01_출원추이', '01b_출원추이_최근10년', '02_출원인_HHI', '03_CPC_기능변화', '07_S커브_참조분석', 'A1_S커브_검증', '08_최근3년_주도기업', '09_최근3년_기술비중', '10_핵심경쟁자_특허현황', 'C1_V1_V2_비교', '04_청구항_기능비교', 'A2_청구항_20건_행렬'}
def setup(title, sub=None):
    f = plt.figure(figsize=(16, 9), facecolor='white')
    f.text(.055, .93, title, fontsize=29, fontweight='bold', va='top')
    if sub: f.text(.055, .855, sub, fontsize=16, color=INK2, va='top')
    return f
def save(f, name, source):
    f.text(.055, .045, source, fontsize=11.5, color=INK2, va='bottom', linespacing=1.5)
    f.canvas.draw(); rd = f.canvas.get_renderer(); out = []
    for o in f.findobj(matplotlib.text.Text):
        if not o.get_visible() or not o.get_text(): continue
        bb = o.get_window_extent(rd)
        if bb.width and (bb.x0 < -1 or bb.x1 > f.bbox.width+1 or bb.y0 < -1 or bb.y1 > f.bbox.height+1): out.append(o.get_text())
    if out: raise RuntimeError(f'{name}: outside canvas {out}')
    f.savefig(FIG/f'{name}.png', dpi=160, facecolor='white'); f.savefig(FIG/'editable'/f'{name}.svg', facecolor='white')
    if name in INPLACE:  # V2 검토 브랜치: 팀원1 그림과 V2 핵심 20건 그림(04·A2)은 deliverables/figures에도 덮어쓴다
        f.savefig(ROOT/'deliverables/figures'/f'{name}.png', dpi=160, facecolor='white'); f.savefig(ROOT/'deliverables/figures/editable'/f'{name}.svg', facecolor='white')
    checks.append(name); plt.close(f)
def style(ax): ax.set_axisbelow(True); ax.grid(axis='y', color='#e6eaf0', lw=.8)
M = lambda v, t: A[f'{v}_{t}']['metrics']
SRC = ('출처: Lens.org 미국 특허, Filed 2000–2024, simple family, 연도=최우선일. V2 = 키워드 검색식 A·B(2026.11.09) + 데이터센터 액체냉각 CPC 검색(2026.11.20) 합집합.\n'
       f"V2 DLC {M('V2','DLC')['total']:,}·액침 {M('V2','액침')['total']}개 패밀리(중복 {A['overlap']['V2']}). CPC로만 들어온 특허는 제목·초록 규칙으로 판정, 표본 정확도 DLC 85%·액침 100%.")
NAME = {'HEBEI QINHUAI DATA CO LTD': 'Hebei Qinhuai Data', 'SUZHOU METABRAIN INTELLIGENT TECHNOLOGY CO LTD': 'Suzhou Metabrain', 'FOXCONN (HON HAI)': 'Foxconn',
        'INTEL CORP': 'Intel', 'FUJITSU LTD': 'Fujitsu', 'WIWYNN CORP': 'Wiwynn', 'EXASCALER INC': 'ExaScaler', 'AMULAIRE THERMAL TECH INC': 'Amulaire',
        'INVENTEC': 'Inventec', 'DELL': 'Dell', 'MICROSOFT': 'Microsoft', 'BAIDU': 'Baidu', 'QUANTA': 'Quanta', 'NVIDIA': 'NVIDIA', 'HPE': 'HPE', 'OVH': 'OVH',
        'IBM': 'IBM', 'GOOGLE': 'Google'}
nm = lambda a: NAME.get(a, a.title()[:24])

# 01 출원추이 2000–2024
f = setup('미국 특허 출원 활동: 두 기술 모두 증가', 'V2 데이터(키워드 + CPC). 점선은 V1(키워드만) · 회색 구간은 공개 지연으로 덜 잡히는 해')
ax = f.add_axes([.09, .29, .55, .48]); style(ax)
for t, col in [('DLC', BLUE), ('액침', TEAL)]:
    for v, ls, lw, a in [('V2', '-', 2.6, 1), ('V1', '--', 1.6, .55)]:
        yr = M(v, t)['annual']; ax.plot([int(y) for y in yr], list(yr.values()), ls=ls, lw=lw, color=col, alpha=a, marker='o' if v == 'V2' else None, ms=4,
                                        label=f"{t} {'V2' if v == 'V2' else 'V1'}")
ax.axvspan(2022.5, 2024.5, color=GRAY, alpha=.6, zorder=0); ax.set_xlim(2000, 2024.5); ax.set_ylim(bottom=0)
ax.set_xticks([2000, 2005, 2010, 2015, 2020, 2024]); ax.set_xlabel('최우선연도'); ax.set_ylabel('패밀리 수'); ax.legend(frameon=False, loc='upper left', fontsize=13, ncol=2)
for i, (t, col) in enumerate([('DLC', BLUE), ('액침', TEAL)]):
    m = M('V2', t); m1 = M('V1', t); y = .72-i*.24
    f.text(.70, y, t, color=col, fontsize=21, fontweight='bold')
    f.text(.70, y-.065, f"{m['p2013_17']} → {m['p2018_22']}건", fontsize=28, fontweight='bold')
    f.text(.70, y-.115, f"5년 합계 +{m['growth_pct']:.0f}%  (V1 +{m1['growth_pct']:.0f}%)", fontsize=16)
f.text(.70, .22, '2013–17 → 2018–22\n같은 길이의 기간 비교', fontsize=15, color=INK2)
f.text(.09, .13, '특허활동 증가를 확인한 것이며, 수요 성장률이나 기술 성숙도를 직접 뜻하지 않는다.', fontsize=18)
save(f, '01_출원추이', SRC)

# 01b 최근 10년
f = setup('최근 10년(2015–2024) 미국 출원 추이', '연도별 패밀리 수 · 회색 구간은 공개 지연으로 덜 잡히는 해')
ax = f.add_axes([.08, .2, .62, .58]); style(ax); yrs = list(range(2015, 2025))
for t, col in [('DLC', BLUE), ('액침', TEAL)]:
    v = [M('V2', t)['annual'][str(y)] for y in yrs]
    ax.plot(yrs, v, marker='o', ms=8, lw=2.5, color=col, label=t); ax.text(2024.25, v[-1], t, color=col, fontsize=17, fontweight='bold', va='center')
ax.axvspan(2022.5, 2024.6, color=GRAY, alpha=.7, zorder=0); ax.set_xlim(2014.6, 2024.9); ax.set_ylim(bottom=0); ax.set_xticks(yrs)
ax.set_ylabel('패밀리 수'); ax.legend(frameon=False, loc='upper left')
for i, (t, col) in enumerate([('DLC', BLUE), ('액침', TEAL)]):
    r3 = A[f'V2_{t}']['recent3']; y = .74-i*.25
    f.text(.76, y, t, color=col, fontsize=21, fontweight='bold'); f.text(.76, y-.065, f"10년 {M('V2', t)['recent10']:,}개", fontsize=28, fontweight='bold')
    f.text(.76, y-.115, f"2015–21 {r3['n0']} · 2022–24 {r3['n3']}", fontsize=16, color=INK2)
f.text(.76, .2, f"두 기술 중복 포함\n합집합 10년 {M('V2', '합집합')['recent10']:,}개", fontsize=15, color=INK2)
save(f, '01b_출원추이_최근10년', SRC)

# 02 출원인·HHI
f = setup('출원인 분포는 분산되어 있으나, 권리 장벽은 별도 검토')
for i, (t, col) in enumerate([('DLC', BLUE), ('액침', TEAL)]):
    m = M('V2', t); ax = f.add_axes([.22+i*.47, .25, .25, .52]); rr = m['top10'][:6]
    vals = [100*s for _, _, s in rr]; ax.barh(range(6), vals, color=col, height=.62)
    ax.set_yticks(range(6), [nm(a) for a, _, _ in rr], fontsize=13); ax.invert_yaxis(); ax.set_xlim(0, 15); ax.set_xlabel('출원인–패밀리 쌍 비중 (%)', fontsize=14)
    for j, (a, n, s) in enumerate(rr): ax.text(vals[j]+.3, j, f"{vals[j]:.1f}% · {n}건", va='center', fontsize=12)
    ax.set_title(f"{t}  HHI {m['hhi_full']:.3f}  |  CR4 {m['cr4']:.1%}", fontsize=20, pad=27, fontweight='bold')
f.text(.08, .15, f"V1(키워드만) HHI는 DLC {M('V1','DLC')['hhi_full']:.3f}·액침 {M('V1','액침')['hhi_full']:.3f}. 범위를 넓히면 더 분산된다. 특허 수의 분산 ≠ 자유실시 가능.", fontsize=17)
save(f, '02_출원인_HHI', f"출처: V2 데이터, 최우선 2015–2024 / DLC {M('V2','DLC')['recent10']:,}·액침 {M('V2','액침')['recent10']} 패밀리. 완전계수 분모: {M('V2','DLC')['pair_den']:,}·{M('V2','액침')['pair_den']} 출원인–패밀리 쌍.\n"
     f"HHI = Σ비중². 매출 시장집중도가 아님. 분할계수 HHI {M('V2','DLC')['hhi_frac']:.3f}·{M('V2','액침')['hhi_frac']:.3f}. 같은 회사의 다른 표기는 합쳐 셈(src/v2/analyze_v2.py ALIAS).")

# 03 CPC 기능 변화 (5년 비교)
f = setup('미국 특허의 기능별 CPC 비중 변화', '2015–2019 대비 2020–2024 · 한 특허에 여러 기능군이 붙을 수 있어 합계는 100%가 아님')
for i, (t, col, lc) in enumerate([('DLC', BLUE, LBLUE), ('액침', TEAL, LTEAL)]):
    rows = pd.DataFrame(A[f'V2_{t}']['cpc']); ax = f.add_axes([.09+i*.46, .27, .37, .48]); style(ax)
    for k, g in enumerate(['유체 순환·연결 부속', '열·유량 제어']):
        for per, off, c in [('2015–2019', -.18, lc), ('2020–2024', .18, col)]:
            r = rows[(rows.group == g) & (rows.period == per)].iloc[0]
            ax.bar(k+off, r['share'], width=.34, color=c, label=per if k == 0 else None)
            ax.text(k+off, r['share']+1.5, f"{r['share']:.1f}%\n({r['count']}/{r['den']})", ha='center', fontsize=12.5)
    ax.set_xticks([0, 1], ['유체 순환·연결', '열·유량 제어'], fontsize=15); ax.set_ylim(0, 92); ax.set_ylabel('분류 포함 패밀리 (%)')
    ax.set_title(t, fontsize=22, fontweight='bold', pad=15); ax.legend(frameon=False, loc='upper left', fontsize=13)
v1 = {t: pd.DataFrame(A[f'V1_{t}']['cpc']) for t in ['DLC', '액침']}
g = lambda d, gg, p: d[(d.group == gg) & (d.period == p)].share.iloc[0]
f.text(.08, .16, f"V1 유체 순환·연결: DLC {g(v1['DLC'],'유체 순환·연결 부속','2015–2019')}→{g(v1['DLC'],'유체 순환·연결 부속','2020–2024')}%, 액침 {g(v1['액침'],'유체 순환·연결 부속','2015–2019')}→{g(v1['액침'],'유체 순환·연결 부속','2020–2024')}%. 증가 방향은 같다.", fontsize=17)
save(f, '03_CPC_기능변화', '출처: V2 데이터 + CPC 공식 분류표. 순환: H05K7/20272·7/20327, F04·F16L. 제어: H05K7/20281·7/20381·7/207·7/20836, G06F1/206, G05B·G05D.\n분류 포함 비중이며 기술 비중을 그대로 뜻하지 않음.')

# 04 청구항 기능 비교
cf = pd.read_csv(R/'claim1_feature_counts_v1_v2.csv'); FE = ['유로·분배·순환', '자동 제어', '열교환·응축', '연결·정비 기구', '시설 냉각수 명시']
f = setup('핵심특허 20건 독립항 1: 유로·열교환·연결이 반복된다', 'V2 핵심특허(연도층별 연평균 피인용 상위) · 막대 = 기능을 명시한 특허 수 (기술별 10건 중)')
ax = f.add_axes([.25, .26, .5, .53]); y = np.arange(5)
for t, col, off in [('DLC', BLUE, -.18), ('Immersion', TEAL, .18)]:
    vals = cf[(cf.version == 'V2') & (cf.technology == t)][FE].iloc[0].tolist()
    ax.barh(y+off, vals, height=.34, color=col, label='DLC' if t == 'DLC' else '액침')
    for i, v in enumerate(vals): ax.text(v+.1, i+off, str(v), va='center', fontsize=16)
ax.set_yticks(y, FE, fontsize=16); ax.invert_yaxis(); ax.set_xlim(0, 10.5); ax.set_xlabel('특허 수'); ax.legend(frameon=False, loc='lower right')
v1c = cf[cf.version == 'V1'][FE].sum(); v2c = cf[cf.version == 'V2'][FE].sum()
f.text(.78, .62, '20건 합계\nV2 vs V1', fontsize=16, color=INK2)
for i, k in enumerate(FE): f.text(.78, .55-i*.055, f"{k.split('·')[0]}  {v2c[k]} vs {v1c[k]}", fontsize=15)
f.text(.08, .125, '20건 중 V1과 같은 특허는 6건. 구성이 바뀌어도 유로·열교환·연결 기구가 상위 3개인 점은 같다.', fontsize=17)
save(f, '04_청구항_기능비교', '출처: 미국 등록공보 독립항 1(새 14건 Google Patents 확인 2026.11.20, V1 6건은 11.17 코딩 유지). 기능 중복 코딩.\n목적표본의 구성 비교이며 전 산업 비중이 아님. 0은 이 항에서 미확인이라는 뜻. 행별 근거: data/v2/results/US_claim1_review_v2.csv')

# 07 S커브
cv = pd.read_csv(R/'scurve_curves_v2.csv'); S = A['scurve']
f = setup('Logistic·Gompertz S커브 적합'); f.text(.94, .925, '참고용', ha='right', fontsize=19, color=INK2)
for i, (t, lab) in enumerate([('DLC', 'DLC'), ('Immersion', '액침')]):
    ax = f.add_axes([.10+i*.46, .28, .35, .49]); style(ax); x = cv[(cv.version == 'V2') & (cv.technology == t)]
    obs = x[(x.model == 'Logistic') & (x.year <= 2021)]; ax.scatter(obs.year, obs.observed, s=27, color='#24344a', label='관측 누적', zorder=4)
    for mname, col in [('Logistic', BLUE), ('Gompertz', TEAL)]:
        y = x[x.model == mname]; fit = y[y.year <= 2021]; ext = y[y.year >= 2021]
        ax.plot(fit.year, fit.cumulative_fit, color=col, lw=2.5, label=f"{mname} (R²={S[f'V2_{t}'][mname]['r2']:.3f})")
        ax.plot(ext.year, ext.cumulative_fit, color=col, lw=2, ls='--')
    o21 = S[f'V2_{t}']['observed_2021']; ax.axvline(2021, color='#9aa6b5', lw=1); ax.set_xlim(2000, 2025); ax.set_ylim(0, o21*1.85)
    ax.set_xticks([2000, 2005, 2010, 2015, 2021, 2025]); ax.set_xlabel('최우선연도'); ax.set_ylabel('등록특허 누적 수')
    ax.set_title(lab, fontsize=23, fontweight='bold', pad=16); ax.legend(frameon=False, loc='upper left', fontsize=12)
f.text(.09, .15, '실선: 2000–2021 적합  ·  점선: 모형 외삽 예시  ·  단계 판정·전략 점수에는 미반영', fontsize=18)
lg = S['V2_DLC']['Logistic']; li = S['V2_Immersion']['Logistic']
save(f, '07_S커브_참조분석', f"출처: V2 등록특허(DLC {S['V2_DLC']['granted_docs']:,}·액침 {S['V2_Immersion']['granted_docs']}건, 문서 단위), 최우선 2000–2021 누적 적합. V1과 같은 모형·초깃값.\n"
     f"DLC Logistic 포화수준 L={lg['L']:,.0f}(관측의 {lg['L_over_obs']}배), 액침은 상한에 걸려 포화수준 미식별. 최근연도 등록 지연으로 참고용만 사용.")

# A1 S커브 검증
ho = pd.read_csv(R/'scurve_holdout_v2.csv')
f = setup('S커브 검증: 적합 종료연도를 바꾸면 예측이 달라진다', '2018·2019·2020년까지 적합한 뒤 2021년 누적을 예측한 오차 (V2 등록특허)')
for i, (t, lab) in enumerate([('DLC', 'DLC'), ('Immersion', '액침')]):
    ax = f.add_axes([.10+i*.46, .28, .35, .47]); style(ax); x = ho[(ho.version == 'V2') & (ho.technology == t)]
    for k, (mname, col) in enumerate([('Logistic', BLUE), ('Gompertz', TEAL)]):
        y = x[x.model == mname]; ax.bar(np.arange(3)+(k-.5)*.36, y.error_pct, width=.34, color=col, label=mname)
        for j, v in enumerate(y.error_pct): ax.text(j+(k-.5)*.36, v+(1 if v >= 0 else -3.5), f'{v:+.0f}%', ha='center', fontsize=13)
    ax.axhline(0, color='#9aa6b5', lw=1); ax.set_xticks(range(3), ['~2018', '~2019', '~2020']); ax.set_ylabel('2021 누적 예측 오차 (%)')
    ax.set_title(lab, fontsize=23, fontweight='bold', pad=16); ax.legend(frameon=False, loc='lower right', fontsize=12); ax.set_ylim(min(-20, x.error_pct.min()-8), max(10, x.error_pct.max()+8))
save(f, 'A1_S커브_검증', '출처: data/v2/results/scurve_holdout_v2.csv. 적합 구간만 바꿔 같은 모형을 다시 적합.\n포화수준 미식별·종료연도 민감성·등록 지연이 있어 성숙단계 판정 근거로 쓰지 않음.')

# 08 최근 3년 주도 기업
U = A['V2_합집합']['recent3']; top = U['top'][:10]
TYPE = {'DELL': '서버 제조', 'HEBEI QINHUAI DATA CO LTD': '데이터센터 운영', 'INVENTEC': '서버 제조', 'NVIDIA': '칩·서버', 'INTEL CORP': '칩', 'MICROSOFT': '데이터센터 운영',
        'FOXCONN (HON HAI)': '서버 제조', 'QUANTA': '서버 제조', 'WIWYNN CORP': '서버 제조', 'BAIDU': '데이터센터 운영', 'OVH': '데이터센터 운영', 'HPE': '서버 제조',
        'SUZHOU METABRAIN INTELLIGENT TECHNOLOGY CO LTD': '서버 제조', 'LENOVO': '서버 제조', 'GOOGLE': '데이터센터 운영', 'AMAZON TECH INC': '데이터센터 운영'}
f = setup('최근 3년(2022–2024) 기술개발 주도 기업', f"DLC·액침 합집합 {U['n3']}개 패밀리 기준 상위 출원인 · 공동출원은 각 출원인에 1건씩")
ax = f.add_axes([.25, .19, .40, .6]); vals = [v for _, v, _, _, _ in top][::-1]
ax.barh(range(len(vals)), vals, color=BLUE, height=.62)
for i, (a, v, p, r0, c0) in enumerate(top[::-1]):
    ax.text(v+.8, i, f"{v}건 ({p:.0f}%)", va='center', fontsize=15)
    ax.text(max(vals)*1.32, i, f"{TYPE.get(a, '')}  ·  {'2015–21 '+str(r0)+'위' if r0 != '-' else '2015–21 출원 없음'}", va='center', fontsize=13.5, color=INK2)
ax.set_yticks(range(len(vals))); ax.set_yticklabels([nm(a) for a, *_ in top][::-1], fontsize=15); ax.set_xlim(0, max(vals)*1.28); ax.set_xticks([]); ax.spines['bottom'].set_visible(False)
b0 = A['V2_합집합']['recent3']; bc0 = [x for x in pd.read_csv(R/'recent3_applicants_v2.csv').query("version=='V2' and technology=='합집합'").itertuples()]
f.text(.055, .13, f"최근 3년 출원인 중 {100*U['new_share']:.0f}%가 이 기간에 처음 등장  ·  HHI {U['hhi3']:.3f}, CR4 {100*U['cr4_3']:.0f}%  ·  V1(키워드만) 1위는 Hebei Qinhuai Data였다", fontsize=15)
save(f, '08_최근3년_주도기업', SRC+' 2023–24는 공개 지연으로 과소 관찰.')

# 09 최근 3년 기술 비중
f = setup('최근 3년 기술개발 초점: 유체 순환·연결 부속', '기능군별 패밀리 비중, 2015–21 대비 2022–24 · 한 특허에 여러 기능군이 붙을 수 있어 합계는 100%가 아님')
groups = ['유체 순환·연결 부속', '열·유량 제어', '건물·공조 분류']
for j, (t, col, lc) in enumerate([('DLC', BLUE, LBLUE), ('액침', TEAL, LTEAL)]):
    ax = f.add_axes([.12+j*.45, .22, .36, .53]); d = A[f'V2_{t}']['recent3']
    for i, gname in enumerate(groups):
        a, b = d['grp'][gname]; y = len(groups)-1-i
        ax.barh(y+.18, a, height=.32, color=lc); ax.barh(y-.18, b, height=.32, color=col)
        ax.text(a+1, y+.18, f"{a:.1f}%", va='center', fontsize=13.5, color=INK2); ax.text(b+1, y-.18, f"{b:.1f}%", va='center', fontsize=14.5, fontweight='bold')
    ax.set_yticks(range(3)); ax.set_yticklabels(groups[::-1] if j == 0 else ['']*3, fontsize=15); ax.set_xlim(0, 90); ax.set_xticks([]); ax.spines['bottom'].set_visible(False)
    ax.set_title(f"{t}  (n={d['n0']} → {d['n3']})", fontsize=19, color=col, fontweight='bold', loc='left')
    ft = d['facility_title']; ax.text(0, -.9, f"옅은 막대 2015–21 · 진한 막대 2022–24  ·  시설 단 냉각(제목) {ft['share0']}% → {ft['share3']}%", fontsize=12.5, color=INK2)
save(f, '09_최근3년_기술비중', SRC.split('\n')[0]+'\n기능군 CPC: 순환·연결 H05K7/20272·20327, F04, F16L / 제어 H05K7/20281·20381·207·20836, G06F1/206, G05B·G05D / 건물·공조 E04B·E04F·E04H, F24F.')

# 10 경쟁자 표
cp = pd.read_csv(R/'competitors_v2.csv').query("version=='V2'").set_index('competitor')
def grade(n): return '상' if n >= 12 else '중' if n >= 5 else '하' if n >= 1 else '검색 범위 내 0건'
D = {'삼성물산': 2, 'Trane (LiquidStack 포함)': 9, 'Vertiv (Liebert·CoolTera 포함)': 5, 'Ecolab (CoolIT 포함)': 4, 'Schneider (APC·Motivair 포함)': 3, 'LG전자': 0, 'GRC': 7}
def row(grp, k, label=None, kip='미검색', extra=''):
    r = cp.loc[k]; n = int(r.n10)
    return [grp, label or k, f"{n} ({int(r.dlc)} / {int(r.imm)})", str(int(r.n3)), str(D.get(k, '-')), kip, grade(n)+extra]
rows = [row('국내 건설사', '삼성물산', '삼성물산 (자사)', '액침 2 + 인접 1', ' · 국내 건설사 중 유일'),
        ['', '현대건설·GS건설·DL이앤씨\n대우건설·SK에코플랜트', '0', '0', '-', '0\n(후보 36건 모두 비대상)', '검색 범위 내 0건'],
        row('장비·시설\n통합 공급자', 'Trane (LiquidStack 포함)'), row('', 'Vertiv (Liebert·CoolTera 포함)'), row('', 'Ecolab (CoolIT 포함)'),
        row('', 'Schneider (APC·Motivair 포함)'), row('', 'LG전자', 'LG전자 (GRC·SK엔무브 MOU)'), row('냉각 전문\n(협력·잠재 경쟁)', 'GRC'),
        ['참고: 기술 주도\n(고객·수요자)', 'Baidu · NVIDIA', f"{int(cp.loc['Baidu'].n10)} · {int(cp.loc['NVIDIA'].n10)}", f"{int(cp.loc['Baidu'].n3)} · {int(cp.loc['NVIDIA'].n3)}", '-', '미검색', '상 (1위·3위권)']]
f = setup('핵심 경쟁자별 특허 출원 현황과 기술력 수준', '경쟁자 = 삼성물산과 같은 데이터센터 고객에게 냉각 인프라를 설계·시공·공급하는 기업 · 미국은 V2 검색 기준')
cols = ['구분', '경쟁자', 'V2 미국 10년\n(DLC / 액침)', '최근 3년\n(2022–24)', '회사 이름\n검색(D)', '국내 KIPRIS\n(2000–24)', '특허 기준\n기술력']
ax = f.add_axes([.055, .225, .89, .575]); ax.axis('off')
tbl = ax.table(cellText=rows, colLabels=cols, colWidths=[.12, .22, .12, .09, .10, .16, .19], cellLoc='left', colLoc='left', bbox=[0, 0, 1, 1])
tbl.auto_set_font_size(False); tbl.set_fontsize(13)
for (r, c), cell in tbl.get_celld().items():
    cell.set_edgecolor('#d5dde7'); cell.set_linewidth(.7); cell.PAD = .03; cell.get_text().set_linespacing(1.35)
    if r == 0: cell.set_facecolor('#edf2fb'); cell.set_text_props(weight='bold', color='#214a8d')
    elif r == 1: cell.set_facecolor('#f4f7fc')
    elif r == 9: cell.get_text().set_color(INK2)
f.text(.055, .135, '기술력 기준(공지: 특허를 많이 보유할수록 기술력 우수) — 상: 12건 이상  중: 5–11건  하: 1–4건 (미국 10년, 최우선일 2015–2024)\n회사 이름 검색(D)은 V1 때 따로 센 값. V2 수치가 D와 비슷하거나 많아, V2가 냉각 전문회사 특허도 대부분 잡는다.', fontsize=13.5, color='#24344a', linespacing=1.5)
save(f, '10_핵심경쟁자_특허현황', '출처: Lens.org 미국 특허 V2 데이터(data/v2/results/competitors_v2.csv), 회사 이름 검색 2026.11.20. 국내: KIPRIS 2026.11.08. 인수 기업은 인수 대상 출원분까지 합산.\n특허 수는 개발 활동 지표이며 시장점유율·제품 성능이 아님. 국내 건설사 5곳은 회사 이름 검색을 하지 않았음.')

# A2 청구항 행렬
cl = pd.read_csv(R/'US_claim1_review_v2.csv')
f = setup('미국 핵심특허 20건(V2): 독립항 1 기능 체크표')
ax = f.add_axes([.30, .15, .63, .66]); mat = cl[FE].values
ax.imshow(mat, cmap=ListedColormap(['#f0f3f7', BLUE]), vmin=0, vmax=1, aspect='auto')
ax.set_xticks(range(5), ['유로·순환', '자동 제어', '열교환·응축', '연결·정비', '시설수 명시'], fontsize=14); ax.xaxis.tick_top()
ax.set_yticks(range(20), [p + ('  (V1 공통)' if s == 'V1' else '') for p, s in zip(cl.patent, cl.coded_from)], fontsize=11.5)
ax.set_xticks(np.arange(-.5, 5, 1), minor=True); ax.set_yticks(np.arange(-.5, 20, 1), minor=True); ax.grid(which='minor', color='white', linewidth=2)
ax.tick_params(which='minor', bottom=False, left=False); ax.axhline(9.5, color='#172c48', lw=2)
f.text(.045, .66, 'DLC\n10건', fontsize=22, color=BLUE); f.text(.045, .33, '액침\n10건', fontsize=22, color=TEAL)
save(f, 'A2_청구항_20건_행렬', '출처: 미국 등록공보, 독립항 1. 파랑 = 명시적 구성 확인 / 옅은색 = 이 항에서 미확인. 새 14건 확인 2026.11.20.\n행별 요약·코딩 근거·원문 링크: data/v2/results/US_claim1_review_v2.csv. 기능 부재나 자유실시 여부를 판단하는 표가 아님.')

# C1 V1 vs V2 비교
f = setup('V1(키워드) vs V2(키워드 + CPC): 결론은 같고 건수는 커졌다', '합집합 연도별 패밀리 수와 주요 지표 비교')
ax = f.add_axes([.07, .27, .42, .5]); style(ax); yrs = range(2000, 2025)
for v, col, lab in [('V2', BLUE, 'V2'), ('V1', '#9aa6b5', 'V1')]:
    yy = [M(v, '합집합')['annual'][str(y)] for y in yrs]; ax.plot(list(yrs), yy, color=col, lw=2.6, marker='o', ms=3.5, label=f"{lab} ({M(v,'합집합')['total']:,}개)")
ax.axvspan(2022.5, 2024.5, color=GRAY, alpha=.6, zorder=0); ax.set_xlim(2000, 2024.5); ax.set_ylim(bottom=0); ax.set_xlabel('최우선연도'); ax.set_ylabel('패밀리 수'); ax.legend(frameon=False, loc='upper left')
m1, m2 = M('V1', '합집합'), M('V2', '합집합'); r1, r2 = A['V1_합집합']['recent3'], A['V2_합집합']['recent3']
rows = [['10년 패밀리 (합집합)', f"{m1['recent10']}", f"{m2['recent10']:,}", '건수 커짐'],
        ['출원 증가 2020–24÷2015–19', f"{m1['ratio_20_24_vs_15_19']}배", f"{m2['ratio_20_24_vs_15_19']}배", '증가 유지'],
        ['10년 1위 출원인', 'Baidu', 'Baidu', '같음'],
        ['HHI (10년, DLC/액침)', f"{M('V1','DLC')['hhi_full']:.3f}/{M('V1','액침')['hhi_full']:.3f}", f"{M('V2','DLC')['hhi_full']:.3f}/{M('V2','액침')['hhi_full']:.3f}", '더 분산'],
        ['최근 3년 1위', 'Hebei Qinhuai', 'Dell', '바뀜'],
        ['최근 3년 신규 출원인', f"{100*r1['new_share']:.0f}%", f"{100*r2['new_share']:.0f}%", '과반 유지'],
        ['유체 순환·연결 (최근 3년)', f"{r1['grp']['유체 순환·연결 부속'][1]}%", f"{r2['grp']['유체 순환·연결 부속'][1]}%", '같음']]
ax2 = f.add_axes([.53, .27, .43, .5]); ax2.axis('off')
tb = ax2.table(cellText=rows, colLabels=['지표', 'V1', 'V2', '결론'], colWidths=[.42, .2, .2, .18], cellLoc='left', colLoc='left', bbox=[0, 0, 1, 1])
tb.auto_set_font_size(False); tb.set_fontsize(13.5)
for (r, c), cell in tb.get_celld().items():
    cell.set_edgecolor('#d5dde7'); cell.set_linewidth(.7); cell.PAD = .04
    if r == 0: cell.set_facecolor('#edf2fb'); cell.set_text_props(weight='bold', color='#214a8d')
    if c == 3 and r > 0 and cell.get_text().get_text() == '바뀜': cell.get_text().set_color('#b4462f')
f.text(.07, .135, 'V1은 제목·초록에 server·data center·rack 단어를 요구해, CPC로만 확인되는 특허를 놓쳤다. V2는 이를 보완했다.', fontsize=16)
save(f, 'C1_V1_V2_비교', SRC)
print(checks)
