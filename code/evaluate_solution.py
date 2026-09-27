# -*- coding: utf-8 -*-
"""
Evaluation function (R2 revision).
Change vs. original: the makespan M is determined over ALL nodes first, and only then is the
energy of each node computed with the final M (Eqs. 8-9). In the original code the energy of each
node was computed inside the same loop that was still updating M.
Units: makespan in ms, energy in J, cost in monetary units.
"""


def evaluate_solution(tasks, fog, cloud, solution, min_M, min_engCons, min_procCost, nfog, ncloud, return_all=False):
    for node in fog + cloud:
        node.a = 0.0
        node.procCost = 0.0
        node.eng = 0.0

    for task_idx, node_idx in enumerate(solution):
        node = fog[node_idx] if node_idx < nfog else cloud[node_idx - nfog]
        etime = (float(tasks[task_idx].s) / node.c) * 1000          # ms
        node.a += etime
        tasks[task_idx].resp = node.a + node.d
        node.procCost += (float(tasks[task_idx].s) / node.c * node.pc)

    M = max(node.a for node in fog + cloud)                         # final makespan (ms)
    engCons = 0.0
    procCost = 0.0
    for node in fog + cloud:
        node.eng = (node.a / 1000.0) * node.pmax + ((M - node.a) / 1000.0) * node.pmin   # J
        engCons += node.eng
        procCost += node.procCost

    M = max(M, 1e-6); engCons = max(engCons, 1e-6); procCost = max(procCost, 1e-6)
    # min_M is in seconds (lower bound); x1000 converts it to ms, the unit of M.
    fitValue = 0.34 * min_engCons / engCons + 0.33 * min_procCost / procCost + 0.33 * min_M / M * 1000

    if return_all:
        return M, engCons, procCost, fitValue
    return fitValue


class Evaluator:
    """Wraps evaluate_solution and counts evaluations so that all algorithms get the same budget."""
    def __init__(self, tasks, fog, cloud, mins, nfog, ncloud, budget):
        self.args = (tasks, fog, cloud)
        self.mins = mins
        self.nfog, self.ncloud = nfog, ncloud
        self.budget = budget
        self.n = 0

    def __call__(self, sol):
        self.n += 1
        return evaluate_solution(*self.args, sol, *self.mins, self.nfog, self.ncloud)

    def full(self, sol):
        return evaluate_solution(*self.args, sol, *self.mins, self.nfog, self.ncloud, return_all=True)

    @property
    def left(self):
        return self.budget - self.n
