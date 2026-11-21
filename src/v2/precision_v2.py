"""V2 정확도 표본 확대 (2026-11-21).
기존 표본(precision_sample_v2.csv, 76건)에 같은 층 구조로 94건을 더 뽑아 제목·초록을 읽고 판정했다.
판정 기준은 기존 표본과 같다. 관련 = 데이터센터·서버·전자장비의 열을 액체로 제거하는 장치·방법·시스템.
X 사유: 액체 냉각·냉각 대상 불명확, 히트파이프 중심, 시설 단위(해수·지하·폐열), 전력·배선 중심, 비IT 가능성.
기술 태그 검증: 관련 판정 건에서 액침 구조(탱크·욕조·유전체 침지)인데 DLC로, 또는 그 반대로 태그된 경우를 센다.
실행: python src/v2/precision_v2.py
"""
import glob
from math import sqrt
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; P = ROOT/'data/v2/processed'; R = ROOT/'data/v2/results'
SEED = 20261121

s = pd.read_csv(P/'cpc_only_screening.csv.xz')
old = pd.read_csv(P/'precision_sample_v2.csv')
s = s[~s['Display Key'].isin(set(old['대표문헌']))].copy()
s['era'] = s['최우선연도'].apply(lambda y: '2000-14' if y <= 2014 else '2015-24')
parts = []
for tech, n in [('DLC', 20), ('액침', 17)]:
    for era in ['2000-14', '2015-24']:
        x = s[(s['판정'] == '관련') & (s['기술'] == tech) & (s.era == era)].sample(n, random_state=SEED)
        x['층'] = f'{tech}_{era}'; parts.append(x)
x = s[s['판정'].isin(['비대상', '경계'])].sample(20, random_state=SEED); x['층'] = '제외'; parts.append(x)
add = pd.concat(parts).reset_index(drop=True)

# 수작업 판정: 번호 → (관련 O/X, 비고, 기술태그 판정). 기술태그: 'ok' / 'error' / 'probable' / 'unclear'
J = {
 2: ('X', '유체·냉각 대상 불명확(회로기판 덮개 공동)'), 5: ('X', '화학 흡열 용기, 액체냉각 계통 아님'),
 9: ('X', '해상 데이터센터 해수 냉각(시설)'), 10: ('X', '지하 매설 용기 냉각(시설)'), 16: ('X', '히트파이프 중심'),
 0: ('O', '랙 냉각 루프+팬(공기-액체 열교환)'), 12: ('O', '루프 열사이펀(2상 루프)'), 15: ('O', '루프 열사이펀(2상 루프)'),
 32: ('X', '냉각 대상 불명확(환경 제어 냉·온수조)'),
 45: ('X', '냉각 대상 불명확(IT 용도 표현 없음)'), 63: ('X', '냉각 대상 불명확(IT 용도 표현 없음)'),
 66: ('X', 'IT 용도 불명확(전기·전자 부품 일반, 차량 가능성)'), 67: ('X', '전력 분배 중심(기존 비대상 규칙과 같음)'),
 82: ('O', '서버를 넣은 함체+작동유체+응축 모듈 = 2상 액침. 놓친 관련 특허'),
 74: ('X', '랙형 온도제어 모듈, 대상 불명확(제외 유지)'), 80: ('X', '초록상 액체 냉각 불명확(제외 유지)'),
}
TAG = {38: ('error', '냉각조에 냉각액을 채운 액침 구조인데 DLC 태그'), 29: ('probable', '데이터룸 액냉 함체(뚜껑 힌지) = 액침 함체로 보임, DLC 태그'),
       21: ('unclear', '용기로 감싼 부품에 열교환 유체 순환, 액침 여부 불명확')}
rows = []
for i, r in add.iterrows():
    excl = r['층'] == '제외'
    rel, note = J.get(i, ('X' if excl else 'O', ''))
    tag, tnote = TAG.get(i, ('ok', '')) if rel == 'O' and not excl else ('', '')
    rows.append({'번호': 77 + i, '층': r['층'], '대표문헌': r['Display Key'], '최우선연도': r['최우선연도'], '제목': r['Title'],
                 '규칙판정_최종': r['판정'], '규칙_기술태그': r['기술'], '수작업_관련': rel, '비고': note,
                 '기술태그_검증': tag, '기술태그_비고': tnote})
add = pd.DataFrame(rows)
add.to_csv(P/'precision_sample_v2_add.csv', index=False, encoding='utf-8-sig')

# 기존 + 추가 합산
old['기술태그_검증'] = old['비고'].fillna('').map(lambda t: 'error' if '기술 태그는 DLC' in t else '')
old.loc[(old['층'] != '제외') & (old['수작업_관련'] == 'O') & (old['기술태그_검증'] == ''), '기술태그_검증'] = 'ok'
allx = pd.concat([old.assign(표본='기존'), add.assign(표본='추가')], ignore_index=True)
def wilson(k, n, z=1.96):
    p = k/n; d = 1 + z*z/n; c = (p + z*z/(2*n))/d; h = z*sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return round(100*(c-h)), round(100*(c+h))
out = []
for name, mask, want in [('DLC 2000–14', allx['층'] == 'DLC_2000-14', 'O'), ('DLC 2015–24', allx['층'] == 'DLC_2015-24', 'O'),
                         ('DLC 전체', allx['층'].str.startswith('DLC'), 'O'), ('액침 2000–14', allx['층'] == '액침_2000-14', 'O'),
                         ('액침 2015–24', allx['층'] == '액침_2015-24', 'O'), ('액침 전체', allx['층'].str.startswith('액침'), 'O'),
                         ('제외 판정 중 실제 관련(놓침)', allx['층'] == '제외', 'O')]:
    y = allx[mask]; k = int((y['수작업_관련'] == want).sum()); n = len(y); lo, hi = wilson(k, n)
    out.append(dict(구분=name, 표본=n, 해당=k, 비율=round(100*k/n, 1), CI95_하한=lo, CI95_상한=hi,
                    기존표본=f"{int((y[y.표본=='기존']['수작업_관련']==want).sum())}/{int((y.표본=='기존').sum())}"))
rel = allx[(allx['층'] != '제외') & (allx['수작업_관련'] == 'O')]
for lab, cond in [('기술태그 오류(확실)', rel['기술태그_검증'] == 'error'), ('기술태그 오류(확실+가능성)', rel['기술태그_검증'].isin(['error', 'probable']))]:
    k = int(cond.sum()); n = len(rel); lo, hi = wilson(k, n)
    out.append(dict(구분=lab, 표본=n, 해당=k, 비율=round(100*k/n, 1), CI95_하한=lo, CI95_상한=hi, 기존표본=''))
out = pd.DataFrame(out); out.to_csv(R/'precision_summary_v2.csv', index=False, encoding='utf-8-sig')
print(out.to_string())
