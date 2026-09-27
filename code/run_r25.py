# -*- coding: utf-8 -*-
"""R2 Comment 5: ablation variants of ELO and NSGA-II comparison on the SAME seeded instances
as run_experiments.py (seed 1000*N + r). Output: results/ablation.csv, results/nsga2.csv"""
import csv, os, time, random
import numpy as np
from tasks import tasks as gen_tasks
from nodes import nodes as gen_nodes
from calculate_min_values import calculate_min_values
from evaluate_solution import Evaluator
from lo_scheduling import lo_engine
from proposed_scheduling import heuristic_schedule
from nsga2_scheduling import nsga2_scheduling, nondominated_sort

P, T, BUDGET, NRUN = 10, 100, 1010, 30
VARIANTS = {"ELO (full)": dict(init=True, adaptive_jr=True, elitism=True),
            "w/o heuristic init (= LO)": dict(init=False, adaptive_jr=True, elitism=True),
            "w/o adaptive jump rate": dict(init=True, adaptive_jr=False, elitism=True),
            "w/o elitism": dict(init=True, adaptive_jr=True, elitism=False),
            "heuristic only": None}


def hv3(points, ref):
    """exact hypervolume of a minimisation point set in 3-D (slicing on the 3rd objective)"""
    pts = np.array([p for p in points if (p < ref).all()])
    if len(pts) == 0:
        return 0.0
    pts = pts[np.argsort(pts[:, 2])]
    total = 0.0
    for k in range(len(pts)):
        z0 = pts[k, 2]; z1 = pts[k + 1, 2] if k + 1 < len(pts) else ref[2]
        if z1 <= z0:
            continue
        sl = pts[:k + 1, :2]; sl = sl[np.argsort(sl[:, 0])]
        area, best_y = 0.0, ref[1]
        for x, y in sl:
            if y < best_y:
                area += (ref[0] - x) * (best_y - y); best_y = y
        total += area * (z1 - z0)
    return total


def main():
    os.makedirs("results", exist_ok=True)
    ab, ns = [], []
    for N in [100, 200, 300, 400]:
        nfog = 3 if N <= 200 else 9
        for r in range(NRUN):
            seed = 1000 * N + r; g = random.Random(seed)
            tasks = gen_tasks(N, g); fog, cloud = gen_nodes(nfog, 1, g)
            mins = calculate_min_values(tasks, fog, cloud); n_nodes = nfog + 1
            for v_id, (name, cfg) in enumerate(VARIANTS.items()):
                ev = Evaluator(tasks, fog, cloud, mins, nfog, 1, BUDGET)
                rng = np.random.default_rng([seed, 100 + v_id]) if v_id else np.random.default_rng([seed, 0])
                if cfg is None:
                    sol = heuristic_schedule(tasks, fog, cloud, nfog, 1)
                else:
                    x0 = heuristic_schedule(tasks, fog, cloud, nfog, 1) if cfg["init"] else None
                    sol, _, _ = lo_engine(ev, N, n_nodes, rng, Nitr=T, npop=P, init_sol=x0,
                                          adaptive_jr=cfg["adaptive_jr"], elitism=cfg["elitism"])
                M, E, C, F = ev.full(list(sol))
                ab.append([N, r, name, M, E, C, F])
            # NSGA-II vs ELO (ELO rerun with its standard seed -> identical to the main experiment)
            ev = Evaluator(tasks, fog, cloud, mins, nfog, 1, BUDGET)
            x0 = heuristic_schedule(tasks, fog, cloud, nfog, 1)
            _, elo_f, _, pop = lo_engine(ev, N, n_nodes, np.random.default_rng([seed, 0]), Nitr=T, npop=P,
                                         init_sol=x0, return_population=True)
            EF = np.array([ev.full(list(x))[:3] for x in pop]); EF = EF[nondominated_sort(EF)[0][0]]
            ev2 = Evaluator(tasks, fog, cloud, mins, nfog, 1, BUDGET)
            t0 = time.perf_counter()
            nsol, nfit, NF = nsga2_scheduling(ev2, N, n_nodes, np.random.default_rng([seed, 6]))
            dt = time.perf_counter() - t0
            Mn, En, Cn, _ = ev2.full(nsol)
            utopia = np.array([mins[0] * 1000, mins[1], mins[2]])
            allp = np.vstack([EF, NF]); nadir = allp.max(0)
            scale = lambda X: (X - utopia) / (nadir - utopia)
            ref = np.full(3, 1.1)
            ns.append([N, r, elo_f, nfit, Mn, En, Cn, len(EF), len(NF), hv3(scale(EF), ref), hv3(scale(NF), ref), dt, ev2.n])
        print("N", N, "done", flush=True)
    with open("results/ablation.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["N", "run", "variant", "makespan_ms", "energy_J", "cost", "fitness"]); w.writerows(ab)
    with open("results/nsga2.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["N", "run", "elo_fitness", "nsga2_fitness", "nsga2_makespan_ms", "nsga2_energy_J",
                                       "nsga2_cost", "elo_front_size", "nsga2_front_size", "elo_hv", "nsga2_hv",
                                       "nsga2_runtime_s", "nsga2_evaluations"]); w.writerows(ns)


if __name__ == "__main__":
    main()
