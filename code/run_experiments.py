# -*- coding: utf-8 -*-
"""
R2 experiment driver.
 * For every task size and run r, ONE instance (tasks + nodes) is generated from seed 1000*N + r
   and shared by all algorithms (paired design).
 * Every stochastic algorithm gets its own seeded generator, derived from (seed, algorithm id).
 * Metaheuristics (ELO, LO, GA, SA) receive the same budget of P*(T+1) = 1010 fitness evaluations.
 * Output: results/runs.csv (one row per run and algorithm), results/convergence.npz,
   results/random_assignment.csv
"""
import csv, os, sys, time, random
import numpy as np
from tasks import tasks as gen_tasks
from nodes import nodes as gen_nodes, reset
from calculate_min_values import calculate_min_values
from evaluate_solution import Evaluator
from hybird_lo_scheduling import hybird_lo_scheduling
from lo_scheduling import lo_scheduling
from ga_scheduling import ga_scheduling
from simulated_annealing_scheduling import simulated_annealing_scheduling
from p2c_scheduling import p2c_scheduling
from random_scheduling import random_scheduling

P, T = 10, 100
BUDGET = P * (T + 1)
SIZES = [int(x) for x in os.environ.get("SIZES", "100,200,300,400").split(",")]
NRUN = int(os.environ.get("NRUN", 30))
OUT = os.environ.get("OUT", "results")
NCLOUD = 1
ALGS = ["ELO", "LO", "GA", "P2C", "SA", "Random"]


def nfog_for(n):
    return 3 if n <= 200 else 9        # Table 2


def run_one(alg, inst, rng):
    tasks, fog, cloud, nfog, ncloud, mins = inst
    dim, n_nodes = len(tasks), nfog + ncloud
    ev = Evaluator(tasks, fog, cloud, mins, nfog, ncloud, BUDGET)
    if alg == "ELO":
        sol, f, conv = hybird_lo_scheduling(ev, dim, n_nodes, rng, tasks, fog, cloud, nfog, ncloud, Nitr=T, npop=P)
    elif alg == "LO":
        sol, f, conv = lo_scheduling(ev, dim, n_nodes, rng, Nitr=T, npop=P)
    elif alg == "GA":
        sol, f, conv = ga_scheduling(ev, dim, n_nodes, rng, npop=P)
    elif alg == "SA":
        sol, f, conv = simulated_annealing_scheduling(ev, dim, n_nodes, rng)
    elif alg == "P2C":
        sol = p2c_scheduling(tasks, fog, cloud, nfog, ncloud, rng); conv = None
    elif alg == "Random":
        sol = random_scheduling(dim, n_nodes, rng); conv = None
    M, E, C, F = ev.full(list(sol))
    # secondary metric (not optimised): share of tasks whose response time a_j + d_j (ms),
    # accumulated in task order on the assigned node, does not exceed the task deadline
    dl = sum(1 for t in tasks if t.resp <= t.d) / len(tasks)
    return list(sol), M, E, C, F, conv, ev.n, dl


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, conv_store, rand_freq = [], {}, []
    for N in SIZES:
        nfog = nfog_for(N)
        for r in range(NRUN):
            seed = 1000 * N + r
            g = random.Random(seed)
            tasks = gen_tasks(N, g)
            fog, cloud = gen_nodes(nfog, NCLOUD, g)
            mins = calculate_min_values(tasks, fog, cloud)
            inst = (tasks, fog, cloud, nfog, NCLOUD, mins)
            for a_id, alg in enumerate(ALGS):
                rng = np.random.default_rng([seed, a_id])
                t0 = time.perf_counter()
                sol, M, E, C, F, conv, nev, dl = run_one(alg, inst, rng)
                dt = time.perf_counter() - t0
                rows.append([N, nfog, r, seed, alg, M, E, C, F, dt, nev, *mins, dl])
                if conv is not None:
                    conv_store.setdefault((N, alg), []).append(conv)
                if alg == "Random":
                    cnt = np.bincount(sol, minlength=nfog + NCLOUD) / N
                    rand_freq.append([N, r, *cnt.round(4)])
            print(f"N={N} run {r+1}/{NRUN} done", flush=True)
    with open(os.path.join(OUT, "runs.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["N", "nfog", "run", "seed", "algorithm", "makespan_ms", "energy_J", "cost", "fitness",
                    "runtime_s", "evaluations", "min_M_s", "min_E_J", "min_C", "deadline_rate"])
        w.writerows(rows)
    np.savez(os.path.join(OUT, "convergence.npz"),
             **{f"{N}_{a}": np.array([c[:min(map(len, v))] for c in v]) for (N, a), v in conv_store.items()})
    with open(os.path.join(OUT, "random_assignment.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["N", "run", "share_per_node(fog...,cloud)"]); w.writerows(rand_freq)


if __name__ == "__main__":
    main()
