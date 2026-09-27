"""Weight sensitivity: re-score every final schedule (runs.csv) under alternative weights,
using the same normalisation baselines (as described in the manuscript)."""
import pandas as pd
d = pd.read_csv("results/runs.csv")
W = {"W1": (0.34, 0.33, 0.33), "W2": (1/3, 1/3, 1/3), "W3": (0.50, 0.25, 0.25), "W4": (0.25, 0.50, 0.25), "W5": (0.25, 0.25, 0.50)}
A = ["ELO", "LO", "GA", "P2C", "SA", "Random"]
res = {}
for k, (wE, wC, wM) in W.items():
    f = wE * d.min_E_J / d.energy_J + wC * d.min_C / d.cost + wM * d.min_M_s * 1000 / d.makespan_ms
    res[k] = d.assign(f=f).groupby("algorithm").f.mean().reindex(A)
t = pd.DataFrame(res); print(t.round(4)); print({k: list(t[k].sort_values(ascending=False).index) for k in W})
lines = []
for a in A:
    cells = [(f"\\textbf{{{t.loc[a,k]:.4f}}}" if t.loc[a, k] == t[k].max() else f"{t.loc[a,k]:.4f}") for k in W]
    lines.append(f"{a:7s} & " + " & ".join(cells) + r" \\")
open("results/table_sensitivity.tex", "w").write("\n".join(lines))
