# -*- coding: utf-8 -*-
"""
SA baseline — R2 revision.
Changes vs. original: makespan reported in ms like all other algorithms (the original divided the
average by 1000); same evaluation budget as ELO (the cooling factor is set so that the temperature
schedule spans the budget); the temperature range 0.05 -> 1e-4 is scaled to the fitness range [0,1] (the original
T = 1000 -> 1 accepted every move, i.e. SA degenerated into a random walk); operates on the shared instance.
"""
import math
import numpy as np


def simulated_annealing_scheduling(ev, dim, n_nodes, rng, T0=0.05, Tf=1e-4, iters_per_temp=10):
    curr = list(rng.integers(0, n_nodes, dim)); curr_fit = ev(curr)
    best, best_fit = list(curr), curr_fit
    n_levels = max(1, (ev.left) // iters_per_temp)
    alpha = (Tf / T0) ** (1.0 / n_levels)
    T = T0
    convergence = [best_fit]
    while ev.left > 0:
        for _ in range(min(iters_per_temp, ev.left)):
            neigh = list(curr); neigh[int(rng.integers(dim))] = int(rng.integers(n_nodes))
            nf = ev(neigh)
            delta = nf - curr_fit
            if delta > 0 or rng.random() < math.exp(delta / T):
                curr, curr_fit = neigh, nf
            if curr_fit > best_fit:
                best, best_fit = list(curr), curr_fit
        convergence.append(best_fit)
        T *= alpha
    return best, best_fit, convergence
