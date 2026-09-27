# -*- coding: utf-8 -*-
"""
Heuristic initialization of ELO (Eqs. 17-20), taken from the original proposed_scheduling.py.
R2 changes: operates on a given (shared) instance; pe/ce are now set (see nodes.py).
Score: fit_ij = 0.25*pe_j + 0.25*ce_j + 0.5 * ET_i^min / ET_ij, with ET_ij = a_j + s_i/c_j*1000.
"""
from nodes import reset


def heuristic_schedule(tasks, fog, cloud, nfog, ncloud):
    reset(fog, cloud)
    all_nodes = fog + cloud
    solution = []
    for task in tasks:
        ET = [node.a + (task.s / node.c) * 1000 for node in all_nodes]     # Eq. 17
        ET_min = min(ET)                                                  # Eq. 18
        best_fit, best_j = -float('inf'), None
        for j, node in enumerate(all_nodes):
            fit = 0.25 * node.pe + 0.25 * node.ce + 0.5 * ET_min / ET[j]  # Eq. 19
            if fit > best_fit:
                best_fit, best_j = fit, j
        all_nodes[best_j].a += (task.s / all_nodes[best_j].c) * 1000      # Eq. 20, update load
        solution.append(best_j)
    reset(fog, cloud)
    return solution
