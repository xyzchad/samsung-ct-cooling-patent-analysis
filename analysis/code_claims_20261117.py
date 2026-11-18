"""Analyst coding of independent claim 1, not an automated legal-scope opinion.
Every code is linked to the cached claim and its original patent URL.
"""
import csv,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]; OUT=BASE/'outputs/team2_20261117'
# A: designed distribution/circulation architecture (not merely a port)
# B: explicit automatic state/flow/pressure control
# C: distinct heat-rejection exchanger/condenser/liquid-cooled heat sink
# D: connector mechanism, slide/hinge/service access, not merely a rack/drawer name
# E: expressly named facility coolant interface (not any external coolant source)
CODING=[
('US7318322B2','Hitachi → Maxell','10000','병렬 서버 냉각 루프','여러 서버를 병렬로 잇고 중간 냉각유닛에서 열을 외기로 방출.','parallel circulation path','설계 유량·서버별 분배 검토'),
('US6973801B1','IBM → Lenovo','10101','시설–시스템–서브시스템 열교환','시설 냉각수와 시스템 냉각수, 서브시스템 냉각수를 열교환기로 분리.','facility coolant; first/second heat exchanger; three loops','시설수와 IT측 유체 분리·열교환 인터페이스'),
('US7757506B2','IBM','11100','고장 시 냉각 우선순위 제어','MCU 고장 시 공기측 열교환기 유량을 차단하고 전자장치 액냉을 유지.','controller; isolation valve; failure; liquid-to-liquid heat exchanger','고장 시나리오와 잔여 냉각능력 검증'),
('US8583290B2','IBM','11000','수요 연동 유량·압력 제어','서버 냉각수요에 따라 유량을 조절하고 펌프 속도로 공급압력 유지.','flow controller; pressure controllers; pump speed','부하 대응·펌프 소비전력 비교'),
('US7639499B1','IBM','10010','정비 가능한 매니폴드','랙–섀시 매니폴드 연결을 유지하면서 하위 매니폴드를 슬라이드해 부품 접근.','rack/chassis manifolds; slideable; access','배관 연결과 정비 동선을 함께 설계'),
('US10225958B1','Baidu','10000','펌프 내장 매니폴드','공급·회수 매니폴드 안에 펌프를 내장하고 주배관과 하위 루프 연결.','embedded supply pump; embedded return pump; sub-loop','집중형/분산형 펌프 배치 비교'),
('US10701838B1','Amazon','10010','서버 삽입 시 자동 유체 연결','서버를 랙에 삽입할 때 공급·회수 매니폴드와 커넥터가 결합.','delivery/return manifold; self-installing connector','누수·교체시간·커넥터 호환성'),
('US11019752B2','Baidu','10000','냉각판–채널 일체형 구조','테이퍼 공급 매니폴드, 분배 채널, 복수 냉각판을 한 재료로 일체화.','tapered manifold; distribution channels; single piece','접속 수 감소와 제작·정비의 상충관계'),
('US10548240B1','Google','10000','발열 차이에 따른 수동 유로 분배','열이 적은 장치 앞 유량 일부를 유로 전환부로 발열이 큰 장치 쪽에 보냄.','flow diverter; first/second heat output','수동 유로 설계와 센서 기반 제어를 구분'),
('US11129292B1','Baidu','00010','밸브 게이트형 유체 커넥터','수·암 인터페이스와 탄성부재가 연결된 유체 게이트, 분배 포트의 결합.','male/female interface; fluid gates; elastic members','인터페이스 상세 설계 검토 대상'),
('US7905106B2','LiquidCool Solutions','10010','침지 부품에 국부 유동 유도','침지 서버 케이스 안 매니폴드·튜브·플리넘으로 특정 발열부품에 유동 집중.','manifold; tube; plenum; sealed electrical connector','탱크 전체 유량과 국부 냉각 성능을 구분'),
('US8351206B2','IBM','10101','시설수 연결 수직 응축기','침지 서브시스템의 증기를 수직 응축기에서 응축하고 저장조·펌프로 공급.','facility coolant supply/return; vapor-condensing unit; pump','2상 계통의 응축·보충·압력 관리'),
('US8184436B2','IBM → Lenovo','10101','시설수 연계 응축·과냉 루프','증기 응축기와 저장조 과냉 열교환기에 시설 냉각수를 직렬 공급.','chilled facility coolant; sub-cooling heat exchanger; pump','시설수 온도와 2상 루프 설계 연계'),
('US9049800B2','Dell','00000','침지 서버 서랍의 형상','서버 배치 방향과 크기에 대응하는 불투수 서랍 및 하부 냉각액 공간.','impervious enclosure; depth/width/height; liquid volume','청구항 1은 형상 중심; HDD 액면 위 배치는 이 항의 필수요건 아님'),
('US9622379B1','IBM','00110','정비 가능한 힌지 방열판','침지 부품 위 액냉 방열판을 회전시켜 운전 위치와 정비 위치 전환.','hinged liquid-cooled heat sink; service position','정비 접근성·작업시간 검토'),
('US10939581B1','Quanta','00010','슬라이드 탱크의 하중 지지','슬라이드 레일과 바닥 바퀴 지지구조로 운전 중 액침 탱크를 인출.','extendable slide rails; wheel assemblies; operational tank','유체 포함 하중·인출 공간·정비 동선'),
('US10925188B1','Microsoft','00100','서버 내부 응축·회수','침지 서버 내부 응축 코일에서 증기를 액체로 되돌려 부품 쪽으로 회수.','condenser assembly; condenser coil; vapor gap','2상 액침 모듈의 열방출 구조'),
('US11006547B2','Baidu','10100','구획별 하부 공급·상부 회수','높은 분리벽과 주변 회수조로 인접 구획 간 혼합·역류를 제한.','separator walls; bottom supply; top exit; reservoir; heat exchanger','삼성물산 유로 특허와 같은 과제, 구체적 구성은 다름'),
('US11076508B2','Baidu','10110','개방 정비 중 2상 냉각 유지','분리형 뚜껑, 상부 응축기, 저장조로 뚜껑 개방 중에도 IT 운전 유지.','removable lid; condenser; reservoir; continues while open','냉각 성능뿐 아니라 정비 중 연속운전 검증'),
('US11665863B2','Dell (담보권 표기 주의)','10100','침지 모듈–트레이 간 열교환','모듈 내 침지액 순환과 열판·패드, 트레이 측 별도 유체 순환을 결합.','thermal plate/pad; immersion fluid; additional fluid','모듈 경계의 열저항·누수·교체성 검토')]

core=list(csv.DictReader((BASE/'outputs/team1_20261109/handoff/US_핵심특허_팀원2반환.csv').open(encoding='utf-8-sig')))
source={re.sub(r'\W','',r['grant_number']):r for r in core}
features=['유로·분배·순환','자동 제어','열교환·응축','연결·정비 기구','시설 냉각수 명시']
rows=[]
for pid,owner,bits,topic,summary,evidence,implication in CODING:
    r=source[pid]; d=json.loads((OUT/'evidence'/f'{pid}.json').read_text())
    first=next(c for c in d['claims'] if re.match(r'^1\.',c['text']))
    rows.append({'technology':r['technology'],'patent':pid,'original_applicant':r['applicant_normalized'],
      'ownership_note':owner,'claim_read':'1','topic':topic,'claim1_summary_ko':summary,'evidence_terms':evidence,
      **dict(zip(features,map(int,bits))), 'building_CPC_in_teammate_table':r['building_link'],
      'status_google_assumption_20261117':d['status_google_assumption'],
      'strategy_implication':implication,'source_url':d['source_url']+'#claims','evidence_file':f'evidence/{pid}.json',
      'limitation':'독립항 1만 기능 코딩. 0은 해당 항에서 미표시이며 특허 전체의 기능 부재·권리 비침해를 뜻하지 않음.'})
assert len(rows)==20 and len({r['patent'] for r in rows})==20
assert {r['patent'] for r in rows}==set(source)
with (OUT/'US_claim1_review_20.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
summary={t:{k:sum(r[k] for r in rows if r['technology']==t) for k in features} for t in ['DLC','Immersion']}
(OUT/'claims_analysis.json').write_text(json.dumps({'basis':'20 purposively selected patents; independent claim 1 only','features':features,'rows':rows,'counts':summary},ensure_ascii=False,indent=2))
md=['# 미국 핵심특허 20건: 독립항 1 검토\n',
'팀원1 선정 표본을 변경하지 않았다. 기술별 10건은 전 산업 Top 10이 아니라 연도별 두 층에서 연간 피인용을 기준으로 뽑은 목적표본이다. 아래 요약은 각 **등록본 독립항 1**의 필수 구성 조합을 읽은 결과다. 종속항·다른 독립항을 포함한 전 청구범위/침해 분석은 아니다. 확인일 2026-11-17.\n',
'| 기술 | 등록번호 | 독립항 1의 구성 | 프로젝트에 주는 질문 |', '|---|---|---|---|']
for r in rows:
 md.append(f"| {r['technology']} | [{r['patent']}]({r['source_url']}) | {r['claim1_summary_ko']} | {r['strategy_implication']} |")
md += ['\n## 코딩 기준\n',
'유로·분배·순환은 구체적 분배/순환 구조, 자동 제어는 명시적 제어기·상태 반응, 열교환·응축은 별도 열방출 구성, 연결·정비는 커넥터·슬라이드·힌지·운전 중 개방 기구를 뜻한다. 시설 냉각수 명시는 `facility coolant`의 직접 기재만 센다. 단순한 외부 유체 공급은 포함하지 않았다. 기능은 중복 코딩하므로 합계가 10을 넘을 수 있다.\n',
'시설 냉각수가 명시된 것은 **US6973801B1, US8351206B2, US8184436B2**의 3건이다. 세 건 모두 팀원1의 E04B/F/H·F24F 기준에는 N이었다. 이는 건물·공조 CPC가 없더라도 시설 인터페이스를 다룰 수 있다는 직접 반례다. 시설수 연결과 건물 전체의 통합 제어도 다른 수준이다.\n',
'Google Patents의 상태 표시는 자동 추정이다. 선택 20건에서 Active 13건, 만료/수수료 소멸 표기 7건을 확인했다. 이 수치로 실효 권리·라이선스 필요 여부를 확정하지 않는다. US11665863B2의 Credit Suisse 표기는 담보권 관련 기록이므로 기술을 인수한 경쟁기업으로 집계하지 않는다.\n',
'## 삼성물산과의 연결\n',
'국내 10-2552810 청구항 1은 공급·배출 유로 및 배출홀과의 거리에 비례해 커지는 공급홀 직경을 포함한다. 10-2815358 청구항 1은 온도변화 정상 여부 판단과 두 온도값에 기반한 펌프 제어를 포함한다. 둘은 각각 **유로 분배**와 **운전 제어**의 자사 개발 참여 근거다. Baidu의 구획별 유로(US11006547B2), IBM의 수요·압력 제어(US8583290B2)와 해결 과제를 비교할 수 있으나 구성이나 권리범위가 같다는 뜻은 아니다.\n',
'US20250089206A1은 10-2552810과 같은 최초 한국 출원을 우선권으로 하는 미국 **공개출원**이다. 미국 공개 청구항 1은 챔버·랙 슬롯·공급부·이격된 배출부를 기재하며, 한국 등록 청구항 1의 홀 직경 조건까지 담은 동일 문언이 아니다. 국내 등록이 미국 등록을 뜻하지 않고, 두 문헌을 별개 발명 2건으로 중복 계산하지 않는다.\n',
'GRC US9992914B2는 추가 참고 사례다. 청구항 1에 탱크 내 유속 증강, 부분 재순환, 외부 열교환기, 온도 제어, 개별 서버 인출 조건이 함께 있다. 선정 20건과 분리하여 공동개발·조달 시 검토할 구체적 인터페이스 사례로만 사용한다.\n']
(OUT/'미국_청구항_검토20건.md').write_text('\n'.join(md))
print(json.dumps(summary,ensure_ascii=False,indent=2))
