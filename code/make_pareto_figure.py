"""Pareto-front figure (makespan vs. processing cost projection) (ELO vs NSGA-II) for one representative instance at 100 and 400 tasks.
Representative run = the run whose HV difference (ELO - NSGA-II) is closest to the median of the 30 runs.
Uses the same seeds as run_r25.py, so fronts are identical to those behind Table 9."""
import random, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tasks import tasks as gen_tasks
from nodes import nodes as gen_nodes
from calculate_min_values import calculate_min_values
from evaluate_solution import Evaluator
from lo_scheduling import lo_engine
from proposed_scheduling import heuristic_schedule
from nsga2_scheduling import nsga2_scheduling, nondominated_sort

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#8a8a85", "xtick.color": "#55554f", "ytick.color": "#55554f"})
BLUE, ORANGE = "#2a78d6", "#eb6834"
n = pd.read_csv("results/nsga2.csv"); n["dhv"] = n.elo_hv - n.nsga2_hv
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), dpi=150)
for ax, N in zip(axes, [100, 400]):
    s = n[n.N == N]; r = int(s.iloc[(s.dhv - s.dhv.median()).abs().argsort().iloc[0]].run)
    nfog = 3 if N <= 200 else 9; seed = 1000 * N + r; g = random.Random(seed)
    tasks = gen_tasks(N, g); fog, cloud = gen_nodes(nfog, 1, g); mins = calculate_min_values(tasks, fog, cloud)
    ev = Evaluator(tasks, fog, cloud, mins, nfog, 1, 1010)
    x0 = heuristic_schedule(tasks, fog, cloud, nfog, 1)
    best, bf, _, pop = lo_engine(ev, N, nfog + 1, np.random.default_rng([seed, 0]), Nitr=100, npop=10, init_sol=x0, return_population=True)
    EF = np.array([ev.full(list(x))[:3] for x in pop]); EF = EF[nondominated_sort(EF)[0][0]]
    eb = ev.full(list(best))
    ev2 = Evaluator(tasks, fog, cloud, mins, nfog, 1, 1010)
    nsol, nfit, NF = nsga2_scheduling(ev2, N, nfog + 1, np.random.default_rng([seed, 6])); nb = ev2.full(nsol)
    o = np.argsort(NF[:, 0])
    ax.plot(NF[o, 0] / 1000, NF[o, 2], color=ORANGE, lw=1, alpha=0.5, zorder=1)
    ax.scatter(NF[:, 0] / 1000, NF[:, 2], s=22, color=ORANGE, edgecolor="white", lw=0.6, label="NSGA-II front", zorder=2)
    ax.scatter(EF[:, 0] / 1000, EF[:, 2], s=34, marker="s", color=BLUE, edgecolor="white", lw=0.6, label="ELO non-dominated", zorder=3)
    ax.scatter([nb[0] / 1000], [nb[2]], s=110, marker="*", facecolor="none", edgecolor=ORANGE, lw=1.4, label="NSGA-II selected", zorder=4)
    ax.scatter([eb[0] / 1000], [eb[2]], s=110, marker="*", color=BLUE, edgecolor="#1d1d1b", lw=0.6, label="ELO selected", zorder=5)
    ax.scatter([mins[0]], [mins[2]], s=40, marker="x", color="#55554f", label="Utopia point", zorder=5)
    ax.set_title(f"({'a' if N == 100 else 'b'}) {N} tasks (run {r + 1})", fontsize=9)
    ax.set_xlabel("Makespan (s)"); ax.set_ylabel("Processing cost"); ax.grid(color="#e4e4df", lw=0.6)
    print(N, "run", r, "ELO HV", round(float(s[s.run == r].elo_hv.iloc[0]), 3), "NSGA HV", round(float(s[s.run == r].nsga2_hv.iloc[0]), 3),
          "median dHV", round(s.dhv.median(), 3), "ELO fit", round(eb[3], 4), "NSGA fit", round(nb[3], 4), "sizes", len(EF), len(NF))
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=5, frameon=False, fontsize=7.5)
fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig("../images/pareto_elo_nsga2_r2.pdf")
print("saved")
