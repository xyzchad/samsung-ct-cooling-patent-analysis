import json,sys,os,csv
os.environ['MPLCONFIGDIR']='/tmp/mpl'
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
# 사용법: python figs.py <저장소 루트> <recent3.json> <그림 폴더>
base=sys.argv[1]; R=json.load(open(sys.argv[2],encoding='utf-8'))
FIG=sys.argv[3]; os.makedirs(FIG+'/editable',exist_ok=True)
fam=[f for f in fm.findSystemFonts() if 'NotoSansCJK-Regular' in f or 'NotoSansCJKkr-Regular' in f]
for f in fm.findSystemFonts():
    if 'NotoSansCJK' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family':'Noto Sans CJK KR','font.size':16,'axes.unicode_minus':False,
 'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#24344a','text.color':'#172c48',
 'axes.edgecolor':'#b4bfcc','xtick.color':'#405269','ytick.color':'#405269','svg.fonttype':'none'})
BLUE='#355cbb'; TEAL='#008a7c'; LBLUE='#c7d4ee'; LTEAL='#bfe3de'; GRAY='#e7ebf1'; INK2='#59677a'
def setup(title,sub=None):
    f=plt.figure(figsize=(16,9),facecolor='white')
    f.text(.055,.93,title,fontsize=29,fontweight='bold',va='top')
    if sub: f.text(.055,.855,sub,fontsize=16,color=INK2,va='top')
    return f
def save(f,name,source):
    f.text(.055,.045,source,fontsize=11.5,color=INK2,va='bottom',linespacing=1.5)
    f.savefig(f'{FIG}/{name}.png',dpi=160,facecolor='white'); f.savefig(f'{FIG}/editable/{name}.svg',facecolor='white'); plt.close(f)
SRC='출처: Lens.org 미국 특허(Filed 2000–2024, 검색 2026.11.09), simple family, 연도=최우선일. 저장소 data/processed/us_reviewed (DLC 447·액침 163, 합집합 589).'

# --- 01b 10-year trend
f=setup('최근 10년(2015–2024) 미국 출원 추이','연도별 패밀리 수 · 회색 구간은 공개 지연으로 덜 잡히는 해')
ax=f.add_axes([.08,.2,.62,.58]); ax.set_axisbelow(True); ax.grid(axis='y',color='#e6eaf0',lw=.8)
yrs=list(range(2015,2025))
for t,col,lab in [('DLC',BLUE,'DLC'),('액침',TEAL,'액침')]:
    v=[R[t]['by_year'][str(y)] for y in yrs]
    ax.plot(yrs,v,marker='o',ms=8,lw=2.5,color=col,label=lab)
    ax.text(2024.25,v[-1],lab,color=col,fontsize=17,fontweight='bold',va='center')
ax.axvspan(2022.5,2024.6,color=GRAY,alpha=.7,zorder=0)
ax.set_xlim(2014.6,2024.9); ax.set_ylim(0,80); ax.set_xticks(yrs); ax.set_ylabel('패밀리 수'); ax.legend(frameon=False,loc='upper left')
for i,t in enumerate(['DLC','액침']):
    d=R[t]; y=.74-i*.25; col=[BLUE,TEAL][i]
    f.text(.76,y,t,color=col,fontsize=21,fontweight='bold')
    f.text(.76,y-.065,f"10년 {d['n10']}개",fontsize=28,fontweight='bold')
    f.text(.76,y-.115,f"2015–21 {d['n0']} · 2022–24 {d['n3']}",fontsize=16,color=INK2)
f.text(.76,.2,'두 검색군 중복 포함\n합집합 10년 474개',fontsize=15,color=INK2)
save(f,'01b_출원추이_최근10년',SRC)

# --- 08 recent-3y leaders (union)
U=R['합집합']; top=U['top3'][:10]
TYPE={'HEBEI QINHUAI DATA CO LTD':'데이터센터 운영','NVIDIA':'칩·서버','OVH':'데이터센터 운영','INVENTEC':'서버 제조','DELL':'서버 제조',
'SUZHOU METABRAIN INTELLIGENT TECHNOLOGY CO LTD':'서버 제조','MICROSOFT':'데이터센터 운영','BAIDU':'데이터센터 운영','SQ TECH SHANGHAI CORPORATION':'서버·냉각 부품',
'ZT GROUP INTL INC':'서버 제조','SHENZHEN ENVICOOL TECH CO LTD':'냉각 장비','FOXCONN (HON HAI)':'서버 제조'}
NAME={'HEBEI QINHUAI DATA CO LTD':'Hebei Qinhuai Data','SUZHOU METABRAIN INTELLIGENT TECHNOLOGY CO LTD':'Suzhou Metabrain','SQ TECH SHANGHAI CORPORATION':'SQ Tech Shanghai',
'ZT GROUP INTL INC':'ZT Group','SHENZHEN ENVICOOL TECH CO LTD':'Shenzhen Envicool','FOXCONN (HON HAI)':'Foxconn','INVENTEC':'Inventec','DELL':'Dell','MICROSOFT':'Microsoft','BAIDU':'Baidu'}
f=setup('최근 3년(2022–2024) 기술개발 주도 기업','DLC·액침 합집합 219개 패밀리 기준 상위 출원인 · 공동출원은 각 출원인에 1건씩')
ax=f.add_axes([.27,.19,.43,.6])
names=[NAME.get(a,a) for a,_,_ in top][::-1]; vals=[v for _,v,_ in top][::-1]
ax.barh(range(len(vals)),vals,color=BLUE,height=.62)
for i,(a,v,s) in enumerate(top[::-1]):
    r0=U['rank0'].get(a); prev=f"2015–21 {r0}위" if r0 else '2015–21 출원 없음'
    ax.text(v+.4,i,f"{v}건 ({100*s:.0f}%)",va='center',fontsize=15)
    ax.text(29.5,i,f"{TYPE.get(a,'')}  ·  {prev}",va='center',fontsize=13.5,color=INK2)
ax.set_yticks(range(len(vals))); ax.set_yticklabels(names,fontsize=15); ax.set_xlim(0,28); ax.set_xticks([])
ax.spines['bottom'].set_visible(False)
f.text(.055,.13,f"Baidu: 2015–21 {U['c0']['BAIDU']}건(1위) → 2022–24 8건  ·  최근 3년 출원인 중 {100*U['new3_share_of_applicants']:.0f}%가 이 기간에 처음 등장  ·  HHI {U['hhi3']:.3f}, CR4 {100*U['cr4_3']:.0f}%",fontsize=15)
save(f,'08_최근3년_주도기업',SRC+' 2023–24는 공개 지연으로 과소 관찰.')

# --- 09 recent-3y CPC function share
f=setup('최근 3년 기술개발 초점: 유체 순환·연결 부속','기능군별 패밀리 비중, 2015–21 대비 2022–24 · 한 특허에 여러 기능군이 붙을 수 있어 합계는 100%가 아님')
groups=['유체 순환·연결 부속','열·유량 제어','건물·공조 분류']
for j,(t,col,lc) in enumerate([('DLC',BLUE,LBLUE),('액침',TEAL,LTEAL)]):
    ax=f.add_axes([.12+j*.45,.2,.36,.55]); d=R[t]['grp']
    for i,g in enumerate(groups):
        a,b=d[g]; y=len(groups)-1-i
        ax.barh(y+.18,100*a,height=.32,color=lc); ax.barh(y-.18,100*b,height=.32,color=col)
        ax.text(100*a+1,y+.18,f"{100*a:.1f}%",va='center',fontsize=13.5,color=INK2)
        ax.text(100*b+1,y-.18,f"{100*b:.1f}%",va='center',fontsize=14.5,fontweight='bold')
    ax.set_yticks(range(len(groups))); ax.set_yticklabels(groups[::-1] if j==0 else ['']*3,fontsize=15)
    ax.set_xlim(0,90); ax.set_xticks([]); ax.spines['bottom'].set_visible(False)
    ax.set_title(f"{t}  (n={R[t]['n0']} → {R[t]['n3']})",fontsize=19,color=col,fontweight='bold',loc='left')
    ax.text(0,-.85,'옅은 막대 2015–21 · 진한 막대 2022–24',fontsize=12.5,color=INK2)
save(f,'09_최근3년_기술비중',SRC+'\n기능군 CPC: 순환·연결 H05K7/20272·20327, F04, F16L / 제어 H05K7/20281·20381·207·20836, G06F1/206, G05B·G05D / 건물·공조 E04B·E04F·E04H, F24F.')
print('ok')

# --- 10 competitor table
f=setup('핵심 경쟁자별 특허 출원 현황과 기술력 수준','경쟁자 = 삼성물산과 같은 데이터센터 고객에게 냉각 인프라를 설계·시공·공급하는 기업 · 건수는 검색식 범위 내 하한값')
cols=['구분','경쟁자','미국 10년\n(2015–24)','최근 3년\n(2022–24)','국내 KIPRIS\n(2000–24)','특허 기준\n기술력(하한)']
rows=[
['국내 건설사','삼성물산 (자사)','1 (액침)','1','액침 2 + 인접 1','국내 건설사 중 우위\n글로벌 비교는 단정 안 함'],
['','현대건설·GS건설·DL이앤씨\n대우건설·SK에코플랜트','0','0','0\n(후보 36건 모두 비대상)','검색 범위 내 0건'],
['장비·시설\n통합 공급자','Vertiv (CoolTera 포함)','3 (DLC)','3','미검색','하 · 3건 모두 2023–24'],
['','Schneider (APC·Motivair 포함)','2 (DLC 2, 액침 1)*','1','미검색','하'],
['','Trane (LiquidStack 포함)','2 (액침)','2','미검색','하'],
['','Ecolab (CoolIT 포함)','0','0','미검색','검색 범위 내 0건'],
['','LG전자 (GRC·SK엔무브 MOU)','0','0','미검색','검색 범위 내 0건'],
['냉각 전문\n(협력·잠재 경쟁)','GRC','1 (액침)','0','미검색','하'],
['참고: 기술 주도\n(고객·수요자)','Baidu · NVIDIA','83 · 57','8 · 19','미검색','상 (1·2위)'],
]
ax=f.add_axes([.055,.235,.89,.585]);ax.axis('off')
tbl=ax.table(cellText=rows,colLabels=cols,colWidths=[.14,.25,.15,.1,.17,.19],cellLoc='left',colLoc='left',bbox=[0,0,1,1])
tbl.auto_set_font_size(False);tbl.set_fontsize(14.5)
for (r,c),cell in tbl.get_celld().items():
    cell.set_edgecolor('#d5dde7');cell.set_linewidth(.7);cell.PAD=.03;cell.get_text().set_linespacing(1.35)
    if r==0: cell.set_facecolor('#edf2fb');cell.set_text_props(weight='bold',color='#214a8d')
    elif r==1: cell.set_facecolor('#f4f7fc')
    elif r==9: cell.get_text().set_color(INK2)
f.text(.055,.145,'기술력 기준(공지: 특허를 많이 보유할수록 기술력 우수) — 미국 10년 합집합 474개 패밀리·출원인 112곳 중  상: 상위 10위권(12건 이상)  중: 5–11건  하: 1–4건  0건: 검색 범위 내 0건\n검색식이 서버·데이터센터 표현을 요구해 냉각 전문회사의 부품 특허는 덜 잡힌다(예: CoolIT은 2015년에 미국 특허 50건 보유). 장비사 건수는 실제보다 적을 수 있다.',fontsize=13,linespacing=1.5)
save(f,'10_핵심경쟁자_특허현황',SRC+'\n국내: KIPRIS 2026.11.08, 6개 건설사 후보 44건 판정(data/raw/kipris/records_builders.tsv).\n* 1건이 두 검색군에 중복. 인수 기업 특허는 인수 대상 회사 출원분까지 합산. 특허 수는 개발 활동 지표이며 시장점유율·제품 성능이 아님.')
print('ok10')
