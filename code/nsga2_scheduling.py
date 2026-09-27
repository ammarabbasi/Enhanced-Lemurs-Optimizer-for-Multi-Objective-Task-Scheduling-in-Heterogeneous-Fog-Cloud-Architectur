# -*- coding: utf-8 -*-
"""
NSGA-II baseline (Deb et al., 2002) for the three objectives (T_max, Energy, Cost), all minimised.
Integer encoding, binary tournament on (rank, crowding), uniform crossover (pc = 0.9),
per-gene reset mutation (pm = 1/N). Population 20; generations are run until the evaluation
budget of the other metaheuristics is reached (20 + 49 x 20 = 1000 evaluations).
A single schedule is selected from the final non-dominated front with the same weighted-sum
fitness used for all other algorithms (common decision-making rule).
"""
import numpy as np


def nondominated_sort(F):
    n = len(F)
    dom = (F[:, None, :] <= F[None, :, :]).all(-1) & (F[:, None, :] < F[None, :, :]).any(-1)
    n_dom = dom.sum(0).astype(float)
    fronts, rank = [], np.full(n, -1)
    cur = np.where(n_dom == 0)[0]; r = 0
    while len(cur):
        rank[cur] = r; fronts.append(cur)
        n_dom = n_dom - dom[cur].sum(0); n_dom[rank >= 0] = np.inf
        cur = np.where(n_dom == 0)[0]; r += 1
    return fronts, rank


def crowding(F):
    n, m = F.shape
    if n <= 2:
        return np.full(n, np.inf)
    d = np.zeros(n)
    for k in range(m):
        o = np.argsort(F[:, k]); span = (F[o[-1], k] - F[o[0], k]) or 1.0
        d[o[0]] = d[o[-1]] = np.inf
        d[o[1:-1]] += (F[o[2:], k] - F[o[:-2], k]) / span
    return d


def nsga2_scheduling(ev, dim, n_nodes, rng, npop=20, pc=0.9):
    def objs(x):
        M, E, C, Fit = ev.full(list(x)); ev.n += 1
        return (M, E, C), Fit
    X = rng.integers(0, n_nodes, size=(npop, dim))
    res = [objs(x) for x in X]; F = np.array([r[0] for r in res])
    pm = 1.0 / dim
    while ev.left >= npop:
        fronts, rank = nondominated_sort(F)
        cd = np.zeros(npop)
        for fr in fronts:
            cd[fr] = crowding(F[fr])
        kids = []
        for _ in range(npop):
            def tour():
                i, j = rng.integers(0, npop, 2)
                if rank[i] != rank[j]:
                    return X[i] if rank[i] < rank[j] else X[j]
                return X[i] if cd[i] >= cd[j] else X[j]
            p1, p2 = tour(), tour()
            c = np.where(rng.random(dim) < 0.5, p1, p2) if rng.random() < pc else p1.copy()
            mut = rng.random(dim) < pm; c[mut] = rng.integers(0, n_nodes, mut.sum())
            kids.append(c)
        KX = np.array(kids); KF = np.array([objs(x)[0] for x in KX])
        UX, UF = np.vstack([X, KX]), np.vstack([F, KF])
        fronts, _ = nondominated_sort(UF); keep = []
        for fr in fronts:
            if len(keep) + len(fr) <= npop:
                keep.extend(fr)
            else:
                c2 = crowding(UF[fr]); keep.extend(fr[np.argsort(-c2)[:npop - len(keep)]]); break
        X, F = UX[keep], UF[keep]
    fronts, _ = nondominated_sort(F)
    PX, PF = X[fronts[0]], F[fronts[0]]
    fits = [ev.full(list(x))[3] for x in PX]
    b = int(np.argmax(fits))
    return list(PX[b]), fits[b], PF
