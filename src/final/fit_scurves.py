"""Reproduce the original baseline fits; exports are illustrative, not market forecasts."""
import csv,json
from collections import Counter
import numpy as np
from scipy.optimize import curve_fit
from paths import BASELINE,RESULTS

def logistic(t,L,k,t0): return L/(1+np.exp(-k*(t-t0)))
def gompertz(t,L,b,k): return L*np.exp(-b*np.exp(-k*t))

result={'fit_period':[2000,2021],'baseline':'original granted families, grouped by earliest priority year',
 'interpretation':'참고용 적합 곡선. 포화수준·성숙도·시장수요 예측에 사용하지 않음. 점선은 모형 외삽 예시.', 'technologies':{}}
curves=[]
for tech,slug in [('DLC','dlc'),('Immersion','imm')]:
 rows=list(csv.DictReader((BASELINE/f'us_{slug}_granted.csv').open(encoding='utf-8-sig')))
 count=Counter(int(r['Earliest Priority Date'][:4]) for r in rows)
 years=np.arange(2000,2022);tt=np.arange(len(years),dtype=float)
 yy=np.cumsum([count[int(y)] for y in years]).astype(float)
 out={'baseline_total':len(rows),'observed_2021':int(yy[-1]),'observed':[{'year':int(y),'cumulative':int(n)} for y,n in zip(years,yy)],'models':{}}
 for name,f,p0,bounds in [('Logistic',logistic,[yy[-1]*2,.3,len(tt)],([yy[-1],.01,0],[yy[-1]*100,3,80])),('Gompertz',gompertz,[yy[-1]*2,5,.1],([yy[-1],.01,.001],[yy[-1]*100,200,3]))]:
  p,cov=curve_fit(f,tt,yy,p0=p0,bounds=bounds,maxfev=100000)
  fit=f(tt,*p);r2=1-float(((yy-fit)**2).sum()/((yy-yy.mean())**2).sum())
  out['models'][name]={'parameters':[float(x) for x in p],'r2':r2,'L_relative_SE':float(np.sqrt(cov[0,0])/p[0]),'L_at_upper_bound':bool(p[0]>=yy[-1]*99)}
  for year in range(2000,2026):curves.append({'technology':tech,'model':name,'year':year,'cumulative_fit':float(f(year-2000,*p)),'segment':'fit' if year<=2021 else 'illustrative_extrapolation'})
 result['technologies'][tech]=out
assert result['technologies']['DLC']['observed_2021']==289
assert result['technologies']['Immersion']['observed_2021']==120
# Agreement with the teammate's saved workbook (R² rounded to three decimals).
expected={('DLC','Logistic'):.985,('DLC','Gompertz'):.986,('Immersion','Logistic'):.945,('Immersion','Gompertz'):.942}
for (t,m),v in expected.items():assert round(result['technologies'][t]['models'][m]['r2'],3)==v
(RESULTS/'scurve_fits.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
with (RESULTS/'scurve_curves.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(curves[0]),lineterminator='\n');w.writeheader();w.writerows(curves)
print('Original fits reproduced: R² and 2021 cumulative totals agree for both models and technologies.')
