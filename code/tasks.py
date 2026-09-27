# -*- coding: utf-8 -*-
"""Task model (R2 revision): ranges follow Table 2; seeded generator for shared instances."""
import random


class Task:
    def __init__(self, id, s=0, m=0, d=0, p=0.0, q=0.0, in_size=0, out_size=0, resp=0):
        self.id = id
        self.s = s
        self.m = m
        self.d = d
        self.p = p
        self.q = q
        self.in_size = in_size
        self.out_size = out_size
        self.resp = resp


def tasks(ntask, rng=random):
    task_list = []
    for i in range(ntask):
        task = Task(i)
        task.s = rng.randint(100, 10000)          # MI           (Table 2)
        task.d = rng.randint(100, 10000)          # deadline     (Table 2)
        task.p = rng.randint(1, 10)               # priority     (Table 2)
        task.q = rng.uniform(0.1, 1.0)            # QoS factor   (Table 2)
        task.m = rng.randint(50, 200)
        task.in_size = rng.randint(100, 10000)
        task.out_size = rng.randint(1, 1000)
        task_list.append(task)
    return task_list
