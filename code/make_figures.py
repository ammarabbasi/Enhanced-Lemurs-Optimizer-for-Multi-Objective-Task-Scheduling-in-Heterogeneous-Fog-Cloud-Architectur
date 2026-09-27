"""Convergence and boxplot figures for the R2 manuscript (from results/)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": "#8a8a85",
                     "axes.labelcolor": "#2b2b28", "xtick.color": "#55554f", "ytick.color": "#55554f",
                     "axes.spines.top": False, "axes.spines.right": False})
COL = {"ELO": "#2a78d6", "LO": "#eb6834", "GA": "#1baf7a", "P2C": "#eda100", "SA": "#e87ba4", "Random": "#008300"}
LS = {"ELO": "-", "LO": "--", "GA": "-.", "SA": ":", "P2C": (0, (5, 2, 1, 2)), "Random": (0, (1, 1))}
ORDER = ["ELO", "LO", "GA", "P2C", "SA", "Random"]
d = pd.read_csv("results/runs.csv"); conv = np.load("results/convergence.npz")
OUT = "../images/"

for N in [100, 200, 300, 400]:
    nf = 3 if N <= 200 else 9
    fig, ax = plt.subplots(figsize=(4.6, 3.4), dpi=150)
    for a in ["ELO", "LO", "GA", "SA"]:
        c = conv[f"{N}_{a}"]
        # x axis in fitness evaluations: LO/ELO/GA record once per P=10 evaluations, SA once per 10 moves
        x = np.arange(c.shape[1]) * 10 + 10
        m, s = c.mean(0), c.std(0, ddof=1)
        ax.plot(x, m, color=COL[a], ls=LS[a], lw=2.2 if a == "ELO" else 1.6, label=a, zorder=3 if a == "ELO" else 2)
        ax.fill_between(x, m - s, m + s, color=COL[a], alpha=0.12, lw=0)
    for a in ["P2C", "Random"]:
        v = d[(d.N == N) & (d.algorithm == a)].fitness.mean()
        ax.axhline(v, color=COL[a], ls=LS[a], lw=1.6, label=f"{a} (single pass)")
    ax.set_xlabel("Fitness evaluations"); ax.set_ylabel("Best fitness (mean ± std, 30 runs)")
    ax.grid(axis="y", color="#e4e4df", lw=0.6); ax.set_xlim(0, 1010)
    ax.legend(fontsize=7, frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    fig.tight_layout(); fig.savefig(f"{OUT}convergence_{N}_{nf}_r2.pdf"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(4.6, 3.0), dpi=150)
    data = [d[(d.N == N) & (d.algorithm == a)].fitness.values for a in ORDER]
    bp = ax.boxplot(data, tick_labels=ORDER, patch_artist=True, widths=0.55,
                    medianprops=dict(color="#1d1d1b", lw=1.4), whiskerprops=dict(color="#6b6b66"),
                    capprops=dict(color="#6b6b66"), flierprops=dict(marker="o", ms=4, mfc="white", mec="#6b6b66"))
    for p, a in zip(bp["boxes"], ORDER):
        p.set_facecolor(COL[a]); p.set_alpha(0.75); p.set_edgecolor("#4a4a46")
    ax.set_ylabel("Fitness (30 runs)"); ax.grid(axis="y", color="#e4e4df", lw=0.6)
    fig.tight_layout(); fig.savefig(f"{OUT}boxplot_fitness_{N}_r2.pdf"); plt.close(fig)
print("figures written")
