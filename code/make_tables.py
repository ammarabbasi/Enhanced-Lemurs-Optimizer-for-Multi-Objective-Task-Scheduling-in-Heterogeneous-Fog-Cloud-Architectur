"""LaTeX tables (mean ± std over 30 paired runs) for the R2 manuscript."""
import pandas as pd
d = pd.read_csv("results/runs.csv")
A = ["ELO", "LO", "GA", "P2C", "SA", "Random"]; S = [100, 200, 300, 400]
spec = {"makespan": ("makespan_ms", "{:,.0f}", min), "energy": ("energy_J", "{:,.0f}", min),
        "cost": ("cost", "{:.1f}", min), "fitness": ("fitness", "{:.4f}", max)}
out = {}
for key, (col, fmt, best) in spec.items():
    g = d.groupby(["algorithm", "N"])[col].agg(["mean", "std"])
    bests = {N: best(g.loc[(a, N), "mean"] for a in A) for N in S}
    lines = []
    for a in A:
        cells = []
        for N in S:
            m, s = g.loc[(a, N)]
            txt = f"{fmt.format(m)} $\\pm$ {fmt.format(s)}".replace(",", "{,}")
            cells.append(f"\\textbf{{{txt}}}" if m == bests[N] else txt)
        lines.append(f"{a} & " + " & ".join(cells) + r" \\")
    out[key] = "\n".join(lines)
for k, v in out.items():
    open(f"results/table_{k}.tex", "w").write(v)
print(out["fitness"])
