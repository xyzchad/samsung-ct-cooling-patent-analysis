"""Static, reproducible PNG/SVG figures for the final presentation handoff."""
from pathlib import Path
import os,json
from paths import ROOT as BASE, RESULTS, FIGURES, VALIDATION
os.environ.setdefault('MPLCONFIGDIR',str(BASE/'.plotcache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
OUT=RESULTS; FIG=FIGURES;FIG.mkdir(exist_ok=True)
font='/System/Library/Fonts/AppleSDGothicNeo.ttc'
if Path(font).exists(): fm.fontManager.addfont(font); family=fm.FontProperties(fname=font).get_name()
else: family='DejaVu Sans'
plt.rcParams.update({'font.family':family,'font.size':16,'axes.unicode_minus':False,
 'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#24344a','text.color':'#172c48',
 'axes.edgecolor':'#b4bfcc','xtick.color':'#405269','ytick.color':'#405269','svg.fonttype':'none'})
D=json.loads((OUT/'analysis.json').read_text()); C=json.loads((OUT/'claims_analysis.json').read_text())
BLUE='#355cbb'; TEAL='#13857c'; LIGHT='#c7d4ee';GRAY='#e7ebf1'; checks=[]
def setup(title):
 f=plt.figure(figsize=(16,9),facecolor='white')
 f.text(.055,.93,title,fontsize=29,fontweight='bold',va='top')
 return f
def save(f,name,source):
 f.text(.055,.045,source,fontsize=11.5,color='#59677a',va='bottom',linespacing=1.5)
 f.canvas.draw(); renderer=f.canvas.get_renderer();outside=[]
 for obj in f.findobj(matplotlib.text.Text):
  if not obj.get_visible() or not obj.get_text(): continue
  bb=obj.get_window_extent(renderer)
  if bb.width and (bb.x0< -1 or bb.x1>f.bbox.width+1 or bb.y0< -1 or bb.y1>f.bbox.height+1): outside.append(obj.get_text())
 if outside: raise RuntimeError(f'{name}: outside canvas {outside}')
 f.savefig(FIG/f'{name}.png',dpi=160,facecolor='white')
 f.savefig(FIG/'editable'/f'{name}.svg',facecolor='white')
 svg=FIG/'editable'/f'{name}.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
 checks.append({'figure':name,'width':2560,'height':1440,'outside_canvas':outside});plt.close(f)
def style(ax):
 ax.set_axisbelow(True);ax.grid(axis='y',color='#e6eaf0',lw=.8)
def table(f,cols,rows,widths,fontsize=18):
 ax=f.add_axes([.055,.19,.89,.63]);ax.axis('off')
 tbl=ax.table(cellText=rows,colLabels=cols,colWidths=widths,cellLoc='left',colLoc='left',bbox=[0,0,1,1])
 tbl.auto_set_font_size(False);tbl.set_fontsize(fontsize)
 for (r,c),cell in tbl.get_celld().items():
  cell.set_edgecolor('#d5dde7');cell.set_linewidth(.7);cell.PAD=.04
  cell.get_text().set_linespacing(1.45)
  if r==0: cell.set_facecolor('#edf2fb');cell.set_text_props(weight='bold',color='#214a8d')
 return tbl

f=setup('미국 특허 출원 활동: 두 검색군 모두 증가')
ax=f.add_axes([.09,.25,.55,.54]);style(ax)
for t,col,label in [('DLC',BLUE,'DLC 검색군'),('Immersion',TEAL,'액침 검색군')]:
 m=D['metrics'][t]['reviewed']; arr=m['annual']
 ax.plot([r['year'] for r in arr],[r['families'] for r in arr],marker='o',ms=4,lw=2.5,color=col,label=label)
ax.set_xlim(2000,2024.5);ax.set_ylim(bottom=0);ax.set_xticks([2000,2005,2010,2015,2020,2024])
ax.set_xlabel('최우선연도');ax.set_ylabel('패밀리 수');ax.legend(frameon=False,loc='upper left',fontsize=15)
ax.axvspan(2022.5,2024.5,color=GRAY,alpha=.6,zorder=0)
for i,(t,col,lab) in enumerate([('DLC',BLUE,'DLC'),('Immersion',TEAL,'액침')]):
 m=D['metrics'][t]['reviewed']; y=.72-i*.23
 f.text(.70,y,lab,color=col,fontsize=21,fontweight='bold')
 f.text(.70,y-.065,f"{m['period1']} → {m['period2']}건",fontsize=28,fontweight='bold')
 f.text(.70,y-.115,f"5년 합계 +{m['growth_pct']:.0f}%",fontsize=17)
f.text(.70,.24,'2013–17 → 2018–22\n같은 길이의 기간 비교',fontsize=15,color='#59677a')
f.text(.09,.14,'특허활동 증가를 확인한 것이며, 수요 성장률이나 기술 성숙도를 직접 뜻하지 않는다.',fontsize=18)
save(f,'01_출원추이','출처: Lens, 미국 Filed 2000–2024 / 검색 2026.11.09, 재검토 11.17. DLC 447·액침 163 패밀리(중복 21).\n회색: 최근연도 해석 주의. 최우선일 집계이므로 미국 출원연도와 다를 수 있음. 검색·분류 누락 가능.')

f=setup('출원인 분포는 분산되어 있으나, 권리 장벽은 별도 검토')
for i,(t,col,lab) in enumerate([('DLC',BLUE,'DLC'),('Immersion',TEAL,'액침')]):
 ax=f.add_axes([.22+i*.47,.28,.25,.49]);m=D['metrics'][t]['reviewed'];rr=m['top_applicants'][:6]
 names=[r['name'].replace('HEBEI QINHUAI DATA','Hebei Qinhuai').replace('HON HAI PRECISION INDUSTRY','Foxconn')[:23] for r in rr]
 vals=[r['share']*100 for r in rr];ax.barh(range(len(rr)),vals,color=col,height=.62)
 ax.set_yticks(range(len(rr)),names,fontsize=13);ax.invert_yaxis();ax.set_xlim(0,25);ax.set_xlabel('출원인–패밀리 쌍 비중 (%)',fontsize=14)
 for j,r in enumerate(rr):ax.text(vals[j]+.45,j,f"{vals[j]:.1f}% · {r['count']}건",va='center',fontsize=12)
 ax.set_title(f"{lab}  HHI {m['hhi_full']:.3f}  |  CR4 {m['cr4']:.1%}",fontsize=20,pad=27,fontweight='bold')
f.text(.08,.15,'특허 수의 분산 ≠ 자유실시 가능. 적은 수의 핵심 청구항도 특정 설계를 제약할 수 있다.',fontsize=18)
save(f,'02_출원인_HHI','출처: Lens 재검토 표본, 최우선 2015–2024 / DLC 352·액침 140 패밀리. 완전계수 분모: 364·149 출원인–패밀리 쌍.\nHHI = Σ비중². 매출 시장집중도가 아님. 분할계수 HHI 0.073·0.063; 공동출원·정규화 기준은 계산 CSV에 수록.')

f=setup('유체 순환·연결 부속을 다루는 특허 비중이 증가')
groups=['유체 순환·연결 부속','열·유량 제어']
for i,(t,lab) in enumerate([('DLC','DLC'),('Immersion','액침')]):
 ax=f.add_axes([.10+i*.46,.30,.36,.47]);style(ax)
 for j,(period,col,off) in enumerate([('2015–2019',LIGHT,-.18),('2020–2024',BLUE,.18)]):
  rr=[next(r for r in D['cpc'] if r['technology']==t and r['period']==period and r['group']==g) for g in groups]
  v=[r['share']*100 for r in rr];ax.bar(np.arange(2)+off,v,width=.32,color=col,label=period)
  for k,r in enumerate(rr):ax.text(k+off,v[k]+1.5,f"{v[k]:.1f}%\n({r['count']}/{r['denominator']})",ha='center',fontsize=13)
 ax.set_xticks([0,1],['유체 순환·연결','열·유량 제어'],fontsize=15);ax.set_ylim(0,90);ax.set_ylabel('분류 포함 패밀리 (%)')
 ax.set_title(lab,fontsize=22,fontweight='bold',pad=15);ax.legend(frameon=False,loc='upper left',fontsize=13)
f.text(.08,.17,'동일 기능의 비중 변화를 비교한다. 각 분류는 중복될 수 있으며 합계가 100%인 구성표가 아니다.',fontsize=17)
save(f,'03_CPC_기능변화','출처: Lens + CPC 공식 분류표(2026.08). H05K7/20281을 배관이 아닌 유량 제어로 수정; 2상 유체 부속도 포함.\n순환: H05K7/20272·7/20327, F04·F16L. 제어: 7/20281·7/20381·7/207·7/20836, G06F1/206, G05B·G05D.')

f=setup('핵심특허는 유로·열교환·정비의 구체적 구성을 다룬다')
ax=f.add_axes([.19,.26,.69,.55]);features=C['features'];y=np.arange(len(features))
for t,offset,col,lab in [('DLC',-.18,BLUE,'DLC 10건'),('Immersion',.18,TEAL,'액침 10건')]:
 vals=[C['counts'][t][g] for g in features];ax.barh(y+offset,vals,.32,color=col,label=lab)
 for i,v in enumerate(vals):ax.text(v+.1,i+offset,str(v),va='center',fontsize=16)
ax.set_yticks(y,features);ax.invert_yaxis();ax.set_xlim(0,10.5);ax.set_xticks(range(0,11,2));ax.set_xlabel('독립항 1에서 해당 구성이 확인된 특허 수');ax.legend(frameon=False,loc='lower right')
f.text(.08,.14,'시설 냉각수를 명시한 3건 모두 기존 건물·공조 CPC 판정은 N → CPC만으로 연계를 배제할 수 없다.',fontsize=17)
save(f,'04_청구항_기능비교','출처: 팀원1의 연도층별 피인용 선정 20건 + 미국 등록공보 독립항 1, 확인 2026.11.17. 기능 중복 코딩.\n목적표본의 구성 비교이며 전 산업 비중이 아님. 0은 이 항에서 미확인이라는 뜻; 특허 전체의 기능 부재를 뜻하지 않음.')

f=setup('삼성물산의 확인된 기반: 액침 유로 설계와 운전 제어')
table(f,['설계 과제','삼성물산·데이터빈','비교할 미국 사례 / 의미'],[
 ['유로 분배','10-2552810 · 등록\n거리에 따라 공급홀 직경 조절','Baidu · US11006547B2\n구획 하부 공급·상부 회수로 혼합 제한'],
 ['운전 제어','10-2815358 · 등록\n상태·온도에 따른 펌프 속도 제어','IBM · US8583290B2\n냉각수요·공급압력에 따른 펌프 제어'],
 ['시설 인터페이스','공동특허 2건만으로\n건물 전체 제어 성능은 미입증','US6973801B1 등 3건에 시설수 명시\n열교환·수질·압력 경계까지 비교'],
 ['해외 출원','US20250089206A1 · 공개출원\n10-2552810과 우선권 연결','미국 등록특허로 표시하지 않음\n국가별 청구문언을 구분']],[.19,.36,.45],18)
save(f,'05_자사기술_비교','출처: KIPRIS 기존 국내 검증 기록 + KR/US 청구항 원문, 확인 2026.11.17. 번호·항별 요약은 US_claim1_review_20.csv 참조.\n같은 설계 과제를 비교한 것이며 동일 권리범위·성능 우위를 주장하지 않음. 미국 공개출원은 국내 등록과 중복 발명 집계하지 않음.')

f=setup('공동개발과 조달을 비교하고, 통합설계 역량을 축적')
table(f,['대안','현재 근거','결과팀이 평가할 조건'],[
 ['액침 공동개발\n+ 시설 통합','데이터빈 공동등록 2건\n삼성물산 공식 개발 협력 설명','개선기술 귀속·설계변경 권한\n부하 변화·누수·정비 실증 / 개발비'],
 ['DLC·액침 조달\n+ 통합 서비스','기술군별 다양한 출원인·설계\n삼성물산–GRC 사업협약','서버 호환성·납기·가격·유지보수\n제어 인터페이스·운전 데이터 접근'],
 ['독자 장비개발\n또는 지분투자','현재 특허만으로\n필요성·수익성 확정 불가','협력·구매보다 추가로 얻는 통제권\n개발·투자비와 공급 의존도 비교']],[.24,.34,.42],18)
save(f,'06_기술확보_결과팀인계','근거: KIPRIS 공동등록 / 삼성물산 Newsroom 2025.09.11 / GRC 공식 사업협약 2025.06.03. 표는 분석에 따른 비교 대안.\nGRC 투자 주체인 삼성벤처투자와 삼성물산을 구별. 특허 수로 AHP 점수·최종 순위를 대신하지 않음.')

S=json.loads((OUT/'scurve_fits.json').read_text())
f=setup('Logistic·Gompertz S커브 적합')
f.text(.94,.925,'참고용',ha='right',fontsize=19,color='#59677a')
for i,(tech,label) in enumerate([('DLC','DLC'),('Immersion','액침')]):
 ax=f.add_axes([.10+i*.46,.28,.35,.49]);style(ax);v=S['technologies'][tech]
 ax.scatter([r['year'] for r in v['observed']],[r['cumulative'] for r in v['observed']],s=27,color='#24344a',label='관측 누적',zorder=4)
 for name,col in [('Logistic',BLUE),('Gompertz',TEAL)]:
  m=v['models'][name];p=m['parameters'];x=np.linspace(2000,2025,250);t=x-2000
  y=p[0]/(1+np.exp(-p[1]*(t-p[2]))) if name=='Logistic' else p[0]*np.exp(-p[1]*np.exp(-p[2]*t))
  mask=x<=2021;ax.plot(x[mask],y[mask],color=col,lw=2.5,label=f"{name} (R²={m['r2']:.3f})")
  ax.plot(x[~mask],y[~mask],color=col,lw=2,ls='--')
 ax.axvline(2021,color='#9aa6b5',lw=1);ax.set_xlim(2000,2025);ax.set_ylim(0,v['observed_2021']*1.85)
 ax.set_xticks([2000,2005,2010,2015,2021,2025]);ax.set_xlabel('최우선연도');ax.set_ylabel('현재 등록 패밀리의 누적 수')
 ax.set_title(label,fontsize=23,fontweight='bold',pad=16);ax.legend(frameon=False,loc='upper left',fontsize=12)
f.text(.09,.15,'실선: 2000–2021 적합  ·  점선: 모형 외삽 예시  ·  단계 판정·전략 점수에는 미반영',fontsize=18)
save(f,'07_S커브_참조분석','출처: 팀원1 원래 등록 표본(DLC 354·액침 157), 최우선 2000–2021 적합. 기존 R²·누적 수와 재현 일치.\n포화수준 미식별·종료연도 민감성으로 참고용만 사용. 점선은 수요 전망이 아니며 이후 관측치와 비교한 예측 결과도 아님.')

f=setup('S커브 검증: 높은 적합도만으로 성장단계를 확정할 수 없다')
for i,(t,lab) in enumerate([('DLC','DLC'),('Immersion','액침')]):
 ax=f.add_axes([.10+i*.46,.28,.35,.49]);style(ax)
 rr=[r for r in D['scurve_holdout'] if r['technology']==t and r['year']==2021]
 vals=[rr[0]['observed'],rr[0]['predicted'],rr[1]['predicted']]
 ax.bar(['관측 누적','Logistic','Gompertz'],vals,color=[BLUE,LIGHT,TEAL],width=.6)
 for j,v in enumerate(vals):ax.text(j,v+max(vals)*.035,f'{v:g}',ha='center',fontsize=19)
 ax.set_ylim(0,max(vals)*1.28);ax.set_ylabel('현재 등록 패밀리의 우선연도별 누적');ax.set_title(lab,fontsize=23,pad=16,fontweight='bold')
 f.text(.10+i*.46,.19,f"2021년 과소예측: {abs(rr[1]['error']):.0%}–{abs(rr[0]['error']):.0%}",fontsize=20)
save(f,'A1_S커브_검증','출처: 팀원1 기존 S커브 계산표. 2000–2018 적합 → 2021 검증 / 원래 등록 표본(DLC 354·액침 157), 재적합 아님.\n포화수준 미식별·종료연도 민감성·등록 선택편향 존재. 출원 증가와 제품 보급/성숙 단계는 구별.')

# Full claim-level matrix for appendix and inspection.
f=setup('미국 핵심특허 20건: 독립항 1 기능 체크표')
ax=f.add_axes([.30,.15,.63,.66]);mat=np.array([[r[k] for k in features] for r in C['rows']])
from matplotlib.colors import ListedColormap
ax.imshow(mat,cmap=ListedColormap(['#f0f3f7',BLUE]),vmin=0,vmax=1,aspect='auto')
ax.set_xticks(range(5),['유로·순환','자동 제어','열교환·응축','연결·정비','시설수 명시'],fontsize=14)
ax.xaxis.tick_top();ax.set_yticks(range(20),[r['patent'] for r in C['rows']],fontsize=12)
ax.set_xticks(np.arange(-.5,5,1),minor=True);ax.set_yticks(np.arange(-.5,20,1),minor=True);ax.grid(which='minor',color='white',linewidth=2);ax.tick_params(which='minor',bottom=False,left=False)
ax.axhline(9.5,color='#172c48',lw=2)
f.text(.065,.66,'DLC\n10건',fontsize=22,color=BLUE);f.text(.065,.33,'액침\n10건',fontsize=22,color=TEAL)
save(f,'A2_청구항_20건_행렬','출처: 미국 등록공보, 독립항 1. 파랑 = 명시적 구성 확인 / 옅은색 = 이 항에서 미확인. 확인 2026.11.17.\n행별 요약·코딩 근거·원문 링크: US_claim1_review_20.csv. 기능 부재나 자유실시 여부를 판단하는 표가 아님.')
(VALIDATION/'figure_render.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
print(json.dumps(checks,ensure_ascii=False))
