# -*- coding: utf-8 -*-
"""
Original Lemurs Optimizer (Algorithm 1) — R2 revision.
Changes vs. original: paper parameters (P=10, T=100, jr 0.70 -> 0.05); searches with the same
fitness/baselines used for reporting; elitist reinsertion (Algorithm 1, line "Insert X_best");
optional init_sol (used by ELO in hybird_lo_scheduling.py).
"""
import numpy as np


def lo_engine(ev, dim, n_nodes, rng, Nitr=100, npop=10, jr_max=0.70, jr_min=0.05,
              init_sol=None, elitism=True, adaptive_jr=True, return_population=False):
    population = rng.integers(0, n_nodes, size=(npop, dim))
    if init_sol is not None:
        population[0] = np.array(init_sol)
    fitness = np.array([ev(sol) for sol in population], dtype=float)
    b = int(np.argmax(fitness)); best_fit = fitness[b]; best_sol = population[b].copy()
    convergence = [best_fit]
    for itr in range(1, Nitr + 1):
        jr = jr_max - itr * (jr_max - jr_min) / Nitr if adaptive_jr else 0.5 * (jr_max + jr_min)
        sorted_idx = np.argsort(-fitness)
        rank = np.empty(npop, int); rank[sorted_idx] = np.arange(npop)
        for k in range(npop):
            r = rank[k]
            near = sorted_idx[r - 1] if r > 0 else sorted_idx[1]      # nearest-ranked (better) neighbour
            x = population[k]
            r_u = rng.random(dim); eps = rng.random(dim)
            guide = np.where(r_u < jr, population[near], best_sol)     # Eq. 23
            new = x + np.abs(x - guide) * (2 * eps - 1)               # Eq. 24
            new = np.clip(np.rint(new), 0, n_nodes - 1).astype(int)   # Eq. 25
            f = ev(new)
            if f > fitness[k]:                                        # greedy selection
                population[k] = new; fitness[k] = f
                if f > best_fit:
                    best_fit = f; best_sol = new.copy()
        if elitism:                                                   # Eq. 26
            population[0] = best_sol.copy(); fitness[0] = best_fit
        convergence.append(best_fit)
    if return_population:
        return best_sol, best_fit, convergence, population
    return best_sol, best_fit, convergence


def lo_scheduling(ev, dim, n_nodes, rng, **kw):
    return lo_engine(ev, dim, n_nodes, rng, init_sol=None, **kw)
