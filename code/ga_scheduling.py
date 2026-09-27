# -*- coding: utf-8 -*-
"""
GA baseline — R2 revision.
Changes vs. original: returns the best individual found over the run (the original indexed the
new offspring population with the previous generation's fitness); searches with the same 3-term
fitness used for reporting (the original used 0.67*makespan + 0.33*cost); population 10 and the
same evaluation budget as ELO. Operators unchanged: roulette selection, one-point crossover at N/2,
mutation rate 0.05 per individual, 2 elites.
"""
import numpy as np


def ga_scheduling(ev, dim, n_nodes, rng, npop=10, mrate=0.05, elitism_count=2):
    sol = [list(rng.integers(0, n_nodes, dim)) for _ in range(npop)]
    fit = [ev(s) for s in sol]
    b = int(np.argmax(fit)); best_sol, best_fit = list(sol[b]), fit[b]
    convergence = [best_fit]
    while ev.left >= npop - elitism_count:
        order = sorted(range(npop), key=lambda i: fit[i], reverse=True)
        new_sol = [list(sol[i]) for i in order[:elitism_count]]
        new_fit = [fit[i] for i in order[:elitism_count]]
        tot = sum(fit); cum = np.cumsum([f / tot for f in fit])
        children = []
        while len(new_sol) + len(children) < npop:
            x = int(np.searchsorted(cum, rng.random())); y = int(np.searchsorted(cum, rng.random()))
            x, y = min(x, npop - 1), min(y, npop - 1)
            cut = dim // 2
            children.append(sol[x][:cut] + sol[y][cut:])
            if len(new_sol) + len(children) < npop:
                children.append(sol[y][:cut] + sol[x][cut:])
        for c in children:
            if rng.random() < mrate:
                c[int(rng.integers(dim))] = int(rng.integers(n_nodes))
            new_sol.append(c); new_fit.append(ev(c))
        sol, fit = new_sol, new_fit
        b = int(np.argmax(fit))
        if fit[b] > best_fit:
            best_fit, best_sol = fit[b], list(sol[b])
        convergence.append(best_fit)
    return best_sol, best_fit, convergence
