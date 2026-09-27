# -*- coding: utf-8 -*-
"""
Normalisation baselines (unchanged from the original code; documented for R2).
All three are analytical lower bounds (utopia values) that no feasible schedule can beat:
  min_M       = sum(s_i) / sum(c_j)                 [s]  perfectly balanced, divisible load
  min_engCons = sum(s_i) * min_j (pmax_j / c_j)     [J]  all work on the most energy-efficient node, no idle energy
  min_procCost= sum(s_i) * min_j (pc_j / c_j)             all work on the most cost-efficient node
"""


def calculate_min_values(tasks, fog, cloud):
    total_task_size = sum(task.s for task in tasks)
    all_nodes = fog + cloud
    min_M = total_task_size / sum(node.c for node in all_nodes)
    min_engCons = min(total_task_size / n.c * n.pmax for n in all_nodes)
    min_procCost = min(total_task_size / n.c * n.pc for n in all_nodes)
    return min_M, min_engCons, min_procCost
