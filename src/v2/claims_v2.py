"""V2 핵심특허 20건의 독립항 1 기능 코딩. 코딩 기준은 V1(src/final/review_claims.py)과 같다.
A 유로·분배·순환 구조(단순 포트 아님) / B 유량·압력·온도 자동 제어 / C 별도 열교환기·응축기·액냉 방열판
D 연결·슬라이드·힌지·정비 기구 / E 시설 냉각수 명시
V1과 겹치는 6건은 V1 코딩을 그대로 쓴다. 새 14건은 2026-11-20 Google Patents 원문 청구항 1을 읽고 코딩했다.
0은 그 항에 표시되지 않았다는 뜻이며, 특허 전체의 기능 부재나 권리범위 판단이 아니다.
실행: python src/v2/claims_v2.py
"""
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; R = ROOT/'data/v2/results'
G = 'https://patents.google.com/patent/{}/en#claims'
C = [  # 특허, 기술, 층, 권리자(원→현), 코드ABCDE, 주제, 청구항1 요약, 출처
 ('US7012807B2', 'DLC', '2000–2016', 'IBM → Lenovo', '10110', '도킹 시 냉각판 접촉 연결', '서랍 안 액냉 루프의 냉각판과 랙 쪽 루프의 냉각판이 서랍을 밀어 넣으면 스프링으로 맞붙는다.', 'new'),
 ('US6807056B2', 'DLC', '2000–2016', 'Hitachi', '10100', '장치 루프–랙 루프 2단 열전달', '장치마다 수열부·펌프·열교환기 루프가 있고, 랙 루프의 수열부가 장치 수열부와 맞닿아 열을 받는다.', 'new'),
 ('US7318322B2', 'DLC', '2000–2016', 'Hitachi → Maxell', '10000', '병렬 서버 냉각 루프', '여러 서버를 병렬로 잇고 중간 냉각유닛에서 열을 외기로 방출.', 'V1'),
 ('US9273906B2', 'DLC', '2000–2016', 'IBM', '11100', '현장 교체형 모듈 펌프 유닛', '병렬로 연결된 교체형 펌프 유닛 안에 저장조·펌프·필터 회수 라인을 두고, 수위 센서로 펌프를 자동 조절한다.', 'new'),
 ('US7106590B2', 'DLC', '2000–2016', 'IBM', '11101', '랙별 냉각수 조절 유닛과 시설수 밸브 제어', '랙마다 냉각수 조절 유닛을 두고, 제어 밸브로 시설 냉각수 유량을 조절해 시스템 냉각수 온도를 따로 맞춘다.', 'new'),
 ('US10225958B1', 'DLC', '2017–2024', 'Baidu', '10000', '펌프 내장 매니폴드', '공급·회수 매니폴드 안에 펌프를 내장하고 주배관과 하위 루프 연결.', 'V1'),
 ('US11553627B1', 'DLC', '2017–2024', 'Amazon', '00010', '누수 감지 시 섀시 자동 배출', '누수 센서가 감지하면 잠금이 풀리고 섀시가 밀려 나오면서 냉각수 커넥터가 분리된다.', 'new'),
 ('US11751359B2', 'DLC', '2017–2024', 'NVIDIA', '10010', '이동식 유량 제어기와 매니폴드 결합', '냉각 매니폴드 안 유량 제어기가 움직여 서버 트레이와 결합하고, 짝 제어기는 랙 매니폴드와 결합한다.', 'new'),
 ('US11395443B2', 'DLC', '2017–2024', 'CoolIT (현 Ecolab)', '00010', '블라인드 결합 펌프 트레이', '펌프 입출구에 블라인드 결합 커플러를 고정하고, 정렬 부재로 트레이를 펌프 유닛에 끼운다.', 'new'),
 ('US10561040B1', 'DLC', '2017–2024', 'HPE', '00000', '가스켓으로 맞춘 냉각판 유로', '유연 가스켓과 보강판으로 두 판 사이 유로를 만들어, 높이가 다른 여러 부품을 냉각판 하나로 식힌다.', 'new'),
 ('US8014150B2', 'Immersion', '2000–2016', 'IBM', '00000', '침지 펌프 분사와 증기 분리 배플', '밀폐 구획 안 침지 펌프가 하부 냉각액을 부품에 분사하고, 배플이 증기를 위로 보내 흡입액과 섞이지 않게 한다.', 'new'),
 ('US7905106B2', 'Immersion', '2000–2016', 'LiquidCool Solutions', '10010', '침지 부품에 국부 유동 유도', '침지 서버 케이스 안 매니폴드·튜브·플리넘으로 특정 발열부품에 유동 집중.', 'V1'),
 ('US10512192B2', 'Immersion', '2000–2016', 'Mark Miyoshi (TMGcore 계열)', '00100', '응축실 분리로 작동유체 손실 저감', '2상 액침 냉각조에 응축실과 주 응축기, 분리된 보조실, 증기 유도 구조를 둔다.', 'new'),
 ('US8351206B2', 'Immersion', '2000–2016', 'IBM', '10101', '시설수 연결 수직 응축기', '침지 서브시스템의 증기를 수직 응축기에서 응축하고 저장조·펌프로 공급.', 'V1'),
 ('US8184436B2', 'Immersion', '2000–2016', 'IBM → Lenovo', '10101', '시설수 연계 응축·과냉 루프', '증기 응축기와 저장조 과냉 열교환기에 시설 냉각수를 직렬 공급.', 'V1'),
 ('US10966349B1', 'Immersion', '2017–2024', 'Bitfury', '00100', '보조 응축기를 둔 증기 관리 계통', '액침조 증기를 밸브가 달린 통로로 보조 응축실에 보내 응축하고, 액체를 다시 조로 돌려보낸다.', 'new'),
 ('US10939581B1', 'Immersion', '2017–2024', 'Quanta', '00010', '슬라이드 탱크의 하중 지지', '슬라이드 레일과 바닥 바퀴 지지구조로 운전 중 액침 탱크를 인출.', 'V1'),
 ('US10609839B1', 'Immersion', '2017–2024', 'LiquidCool Solutions', '10100', '매니폴드·튜브로 부품별 국부 유동', '펌프·열교환기를 거친 냉각액을 내부 매니폴드와 튜브로 발열부품 위 트레이에 보내고 위어로 넘겨 돌린다.', 'new'),
 ('US10750637B1', 'Immersion', '2017–2024', 'Microsoft', '00000', '서버 슬롯형 펌프·필터 모듈', '액침 랙의 서버 슬롯과 같은 크기 슬롯에 펌프·필터 모듈을 넣어 서버처럼 설치한다.', 'new'),
 ('US11096313B2', 'Immersion', '2017–2024', 'Iceotope', '00100', '칩 위 냉각액 저류형 방열판', '부품 위 방열판의 벽 안에 냉각액을 더 높은 수위로 담아, 넘치는 냉각액이 주변 냉각액과 합쳐지게 한다.', 'new'),
]
F = ['유로·분배·순환', '자동 제어', '열교환·응축', '연결·정비 기구', '시설 냉각수 명시']
rows = [dict(technology=t, stratum=s, patent=p, owner=o, topic=tp, claim1_summary_ko=sm, coded_from=src,
             **dict(zip(F, map(int, b))), source_url=G.format(p), checked='2026-11-20' if src == 'new' else '2026-11-17(V1)')
        for p, t, s, o, b, tp, sm, src in C]
d = pd.DataFrame(rows); assert len(d) == 20 and d.patent.is_unique
# 프로젝트에 주는 질문: V1 공통 6건은 V1 표현 그대로, 새 14건은 같은 형식으로 작성
Q = {'US7012807B2': '서랍 도킹 시 냉각판 접촉 열저항과 정비 중 분리 방식', 'US6807056B2': '장치 루프와 랙 루프 사이 열전달 경계 설계',
     'US9273906B2': '펌프 이중화·운전 중 교체와 수위 기반 펌프 제어', 'US7106590B2': '시설 냉각수 유량으로 IT측 냉각수 온도를 맞추는 인터페이스',
     'US11553627B1': '누수 시 자동 격리와 서비스 영향 최소화', 'US11751359B2': '매니폴드–서버 결합 공차와 유량 제어기 위치',
     'US11395443B2': '펌프 유닛 교체시간과 블라인드 커넥터 호환성', 'US10561040B1': '높이가 다른 부품의 냉각판 접촉 압력 관리',
     'US8014150B2': '침지조 내부 유동과 증기 분리 설계', 'US10512192B2': '2상 액침의 작동유체 손실과 개방 정비 시 증기 관리',
     'US10966349B1': '2상 계통 응축 용량과 증기 배출 관리', 'US10609839B1': '탱크 전체 유량과 부품별 국부 냉각을 구분 (V1 US7905106B2와 같은 과제)',
     'US10750637B1': '펌프·필터를 서버처럼 교체하는 모듈화와 정비성', 'US11096313B2': '고발열 칩 국부 냉각과 침지 수위 관리'}
v1q = pd.read_csv(ROOT/'data/results/final/US_claim1_review_20.csv').set_index('patent')['strategy_implication'].to_dict()
d['project_question'] = [Q.get(p, v1q.get(p, '')) for p in d.patent]
gr = pd.concat([pd.read_csv(ROOT/f'data/v2/processed/us_{t}_v2_granted.csv.xz') for t in ['dlc', 'imm']]).drop_duplicates('Lens ID')
gr['pid'] = gr['Display Key'].str.replace(r'\W', '', regex=True)
bc = {r.pid: any(c.strip().startswith(('E04B', 'E04F', 'E04H', 'F24F')) for c in str(cc).split(';;')) for r, cc in zip(gr.itertuples(), gr['CPC Classifications'])}
d['building_CPC'] = d.patent.map(lambda p: 'Y' if bc.get(p) else 'N')
d['evidence_note'] = ['V1 청구항 원문 캐시(data/raw/patent_claims) 기준' if s == 'V1' else 'Google Patents 청구항 1을 웹 도구로 읽어 구성요소별로 정리(원문 캐시 없음)' for s in d.coded_from]
d.to_csv(R/'US_claim1_review_v2.csv', index=False, encoding='utf-8-sig')
v1 = pd.read_csv(ROOT/'data/results/final/US_claim1_review_20.csv')
summ = []
for ver, x in [('V1', v1), ('V2', d)]:
    for tech in ['DLC', 'Immersion']:
        y = x[x.technology == tech]
        summ.append(dict(version=ver, technology=tech, n=len(y), **{f: int(y[f].sum()) for f in F}))
pd.DataFrame(summ).to_csv(R/'claim1_feature_counts_v1_v2.csv', index=False, encoding='utf-8-sig')
print(pd.DataFrame(summ).to_string())
# 상세표 (V1 미국특허_20건_청구항분석.md와 같은 형식)
L = ['# 미국 핵심특허 20건 (V2): 독립항 1 검토', '',
     '[행별 기능 코딩 CSV](../../data/v2/results/US_claim1_review_v2.csv) · [V2 인계서](결과팀_인계_v2.md) · [V1 상세표](../미국특허_20건_청구항분석.md)', '',
     'V2 데이터(키워드 + CPC)에서 V1과 같은 규칙으로 다시 뽑은 20건이다. 등록특허, 같은 패밀리 1건, 연평균 피인용 순, 출원연도 2000–2016 / 2017–2024 층에서 기술별 5건씩. 전 산업 Top 10이 아니라 목적표본이다.',
     '아래 요약은 각 **등록본 독립항 1**의 필수 구성 조합을 읽은 결과다. 종속항·다른 독립항을 포함한 전 청구범위/침해 분석은 아니다.',
     'V1과 같은 6건은 V1 코딩(2026-11-17, 원문 캐시)을 그대로 썼다. 새 14건은 2026-11-20 Google Patents의 청구항 1을 읽고 코딩했다. 새 14건은 원문을 저장소에 캐시하지 않았으므로, 인용이 필요하면 링크의 원문을 확인한다.', '',
     '| 기술 | 등록번호 | 독립항 1의 구성 | 프로젝트에 주는 질문 | V1 공통 |', '|---|---|---|---|---|']
for r in d.itertuples():
    L.append(f"| {r.technology} | [{r.patent}]({r.source_url}) | {r.claim1_summary_ko} | {r.project_question} | {'예' if r.coded_from == 'V1' else ''} |")
fac = d[d['시설 냉각수 명시'] == 1]
L += ['', '## 코딩 기준', '', 'V1과 같다. 유로·분배·순환은 구체적 분배/순환 구조, 자동 제어는 명시적 제어기·상태 반응, 열교환·응축은 별도 열방출 구성(액냉 방열판 포함), 연결·정비는 커넥터·슬라이드·힌지·운전 중 교체 기구를 뜻한다. 시설 냉각수 명시는 `facility coolant`의 직접 기재만 센다. 기능은 중복 코딩한다.', '',
      '| 기능 | DLC 10건 | 액침 10건 | 20건 합계 (V1) |', '|---|---:|---:|---:|']
for f_ in F:
    a = int(d[d.technology == 'DLC'][f_].sum()); b = int(d[d.technology == 'Immersion'][f_].sum()); c = int(v1[f_].sum())
    L.append(f'| {f_} | {a} | {b} | {a+b} ({c}) |')
L += ['', f"시설 냉각수가 명시된 것은 **{', '.join(fac.patent)}**의 {len(fac)}건이다. 건물·공조 CPC(E04B/F/H·F24F)는 {', '.join(fac.patent + ' ' + fac.building_CPC)}이다. V1처럼, 건물·공조 CPC가 없어도 시설 인터페이스를 다룰 수 있다는 반례다.", '',
      'Google Patents 상태 표시(자동 추정)는 Active 13건, 만료·수수료 소멸 7건이다. 실효 권리·라이선스 필요 여부를 확정하지 않는다.', '',
      '## V1과 달라진 점', '',
      '- V1 20건 중 14건이 빠졌다. 검색 범위가 넓어져 피인용이 더 많은 IBM·Hitachi(2000년대), Amazon·NVIDIA·CoolIT·HPE(최근) 특허가 들어왔다.',
      '- 초록·청구항 확인으로 7건을 핵심특허에서 뺐다. 랙 후면·측면 공기-액체 열교환(3), 룸 공조(1), 시설 단위 허브(1), 랙 단위 배기열 냉매 흡수(1), 개인용 PC 액침(1)이다(`data/v2/results/core_candidates_v2.csv`).',
      '- 해석은 같다. 유로·열교환·연결 기구가 반복되는 설계 과제이고, 시설 냉각수 명시 3건은 건물 CPC가 없다.', '',
      '## 삼성물산과의 연결', '',
      'V1 상세표의 내용과 같다. 10-2552810(유로 분배)과 10-2815358(펌프 제어)을 Baidu US11006547B2, IBM US8583290B2와 비교한다. 두 미국 특허는 V2 핵심 20건에는 없지만 V2 데이터에 있고, 비교 사례로 그대로 쓸 수 있다. V2 20건 중에서는 IBM US9273906B2(수위 기반 펌프 제어)와 US7106590B2(시설수 밸브 제어)가 펌프·운전 제어 비교에, LiquidCool US10609839B1(매니폴드·튜브 국부 유동)이 유로 분배 비교에 추가로 쓸 수 있는 사례다.']
(ROOT/'deliverables/v2/미국특허_20건_청구항분석_v2.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
