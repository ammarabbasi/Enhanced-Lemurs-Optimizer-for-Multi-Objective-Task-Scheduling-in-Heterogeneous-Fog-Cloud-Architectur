import pandas as pd, numpy as np
from scipy.stats import wilcoxon, friedmanchisquare
d=pd.read_csv('results/runs.csv'); A=["ELO","LO","GA","P2C","SA","Random"]
for met,fmt in [('makespan_ms','{:,.0f}'),('energy_J','{:,.0f}'),('cost','{:.2f}'),('fitness','{:.4f}')]:
    print('==',met)
    for a in A:
        s=''
        for N in [100,200,300,400]:
            v=d[(d.N==N)&(d.algorithm==a)][met]; s+=f"  {fmt.format(v.mean())} ± {fmt.format(v.std())}".ljust(26)
        print(f"{a:7s}"+s)
print('== Wilcoxon signed-rank, paired, exact, one-sided (ELO > X), n=30; wins/30')
piv={N:d[d.N==N].pivot(index='run',columns='algorithm',values='fitness') for N in [100,200,300,400]}
for a in A[1:]:
    s=''
    for N in piv:
        x=piv[N]['ELO']-piv[N][a]; w=wilcoxon(piv[N]['ELO'],piv[N][a],alternative='greater')
        s+=f"  p={w.pvalue:.2g} ({(x>0).sum()}/30)".ljust(22)
    print(f"{a:7s}"+s)
# Friedman on 120 matched instances (blocks)
allp=pd.concat(piv.values()); st=friedmanchisquare(*[allp[a] for a in A])
ranks=allp[A].rank(axis=1).mean(); print('Friedman over 120 instances chi2=%.1f p=%.2g'%(st.statistic,st.pvalue)); print(ranks.sort_values(ascending=False).round(2).to_dict())
print('runtime s:',d.groupby(['algorithm','N']).runtime_s.mean().unstack().round(3).to_dict('index'))
