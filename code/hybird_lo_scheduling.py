# -*- coding: utf-8 -*-
"""
ELO = heuristic initialization (proposed_scheduling.heuristic_schedule, Eqs. 17-20)
      + LO refinement with adaptive jump rate and elitism (Eqs. 21-27, Algorithm 2).
R2 changes: the heuristic schedule is now actually passed as init_sol (the original driver called
this function without it); paper parameters; same fitness during search and reporting.
The local_search() helper of the original file is not part of ELO and is not used.
"""
from lo_scheduling import lo_engine
from proposed_scheduling import heuristic_schedule


def hybird_lo_scheduling(ev, dim, n_nodes, rng, tasks, fog, cloud, nfog, ncloud, **kw):
    x0 = heuristic_schedule(tasks, fog, cloud, nfog, ncloud)
    return lo_engine(ev, dim, n_nodes, rng, init_sol=x0, **kw)
