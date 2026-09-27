# -*- coding: utf-8 -*-
"""Random baseline — each task to a uniformly random node. R2: makespan reported in ms (the original
divided the average by 1000); operates on the shared instance."""


def random_scheduling(ntask, n_nodes, rng):
    return [int(rng.integers(n_nodes)) for _ in range(ntask)]
