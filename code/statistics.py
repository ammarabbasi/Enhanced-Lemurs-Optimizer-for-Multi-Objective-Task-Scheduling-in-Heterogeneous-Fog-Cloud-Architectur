"""Paired statistical analysis for the R2 manuscript (results/runs.csv, results_large/runs.csv)."""
import numpy as np, pandas as pd
from scipy.stats import wilcoxon, friedmanchisquare, studentized_range
A = ["ELO", "LO", "GA", "P2C", "SA", "Random"]; B = A[1:]
d = pd.concat([pd.read_csv("results/runs.csv"), pd.read_csv("results_large/runs.csv")])
rows = []
for N in [100, 200, 300, 400, 500, 1000]:
    pv = d[d.N == N].pivot(index="run", columns="algorithm", values="fitness")
    for b in B:
        diff = pv.ELO - pv[b]
        w = wilcoxon(pv.ELO, pv[b], alternative="greater", method="exact", zero_method="wilcox")
        n = int((diff != 0).sum()); ranks = pd.Series(diff[diff != 0].abs()).rank()
        wplus = ranks[diff[diff != 0] > 0].sum(); wminus = ranks[diff[diff != 0] < 0].sum()
        rbc = (wplus - wminus) / (n * (n + 1) / 2)          # matched-pairs rank-biserial correlation
        rows.append(dict(N=N, baseline=b, n=n, zeros=int((diff == 0).sum()), Wplus=wplus, p=w.pvalue,
                         r=rbc, wins=int((diff > 0).sum())))
t = pd.DataFrame(rows)
# Holm correction within the main family (100-400: 20 tests) and within the large-scale family (10 tests)
for fam, mask in [("main", t.N <= 400), ("large", t.N > 400)]:
    sub = t[mask].sort_values("p"); m = len(sub); adj = []; run = 0
    for k, (i, r) in enumerate(sub.iterrows()):
        run = max(run, min(1, (m - k) * r.p)); adj.append((i, run))
    for i, v in adj: t.loc[i, "p_holm"] = v
t.to_csv("results/wilcoxon.csv", index=False)
print(t.round(6).to_string())
print("ties/zeros total:", t.zeros.sum(), "; exact method used; max ties in |diff|:",
      max(d[d.N == N].pivot(index="run", columns="algorithm", values="fitness").pipe(lambda pv: (pv.ELO - pv[b]).abs().duplicated().sum()) for N in [100,200,300,400,500,1000] for b in B))
# Friedman on the 120 matched instances (100-400) as blocks
main = d[d.N <= 400]
blk = main.pivot_table(index=["N", "run"], columns="algorithm", values="fitness")[A]
st = friedmanchisquare(*[blk[a] for a in A]); n, k = blk.shape
ranks = blk.rank(axis=1).mean()
W = st.statistic / (n * (k - 1))
q = studentized_range.ppf(0.95, k, np.inf) / np.sqrt(2); CD = q * np.sqrt(k * (k + 1) / (6 * n))
print(f"Friedman: n={n} k={k} chi2={st.statistic:.2f} p={st.pvalue:.3g} KendallW={W:.3f} CD={CD:.3f}")
print(ranks.sort_values(ascending=False).round(3).to_dict())
r = ranks.sort_values(ascending=False)
print("pairs NOT significantly different:", [(a, b) for i, a in enumerate(r.index) for b in r.index[i+1:] if abs(r[a]-r[b]) <= CD])
pd.DataFrame({"mean_rank": ranks}).to_csv("results/friedman_ranks.csv")
