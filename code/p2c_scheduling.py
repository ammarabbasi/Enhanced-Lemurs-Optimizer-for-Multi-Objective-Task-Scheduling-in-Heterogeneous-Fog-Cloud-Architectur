# -*- coding: utf-8 -*-
"""P2C (Power of Two Choices) baseline — logic unchanged; operates on the shared instance."""
from nodes import reset


def p2c_scheduling(tasks, fog, cloud, nfog, ncloud, rng):
    reset(fog, cloud)
    n_nodes = nfog + ncloud
    all_nodes = fog + cloud
    sol = []
    for task in tasks:
        x, y = int(rng.integers(n_nodes)), int(rng.integers(n_nodes))
        fx, fy = all_nodes[x], all_nodes[y]
        j = x if fx.a + (task.s / fx.c) * 1000 < fy.a + (task.s / fy.c) * 1000 else y
        all_nodes[j].a += (task.s / all_nodes[j].c) * 1000
        sol.append(j)
    reset(fog, cloud)
    return sol
