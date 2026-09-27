# -*- coding: utf-8 -*-
"""
Node model (R2 revision).
Changes vs. original:
  * ranges follow Table 2 of the manuscript (cloud power 100-200 W);
  * a seeded random.Random instance is used so that every algorithm sees the same instance;
  * cloud node ids are offset by nfog so that ids are unique over fog+cloud;
  * power-efficiency (pe = c/pmax) and cost-efficiency (ce = c/pc) coefficients are set and
    normalised within each tier (they were never set in the original code, i.e. pe = ce = 0).
"""
import random


class Node:
    def __init__(self, id, c=0, m=0, b=0, a=0, d=0, pe=0.0, ce=0.0, pc=0.0, pmin=0.0, pmax=0.0):
        self.id = id
        self.c = c
        self.m = m
        self.b = b
        self.a = a
        self.d = d
        self.pe = pe
        self.ce = ce
        self.pc = pc
        self.pmin = pmin
        self.pmax = pmax
        self.eng = 0.0
        self.procCost = 0.0
        self.ms = 0.0
        self.fit = 0.0


def nodes(nfog, ncloud, rng=random):
    fog_nodes, cloud_nodes = [], []
    for i in range(nfog):
        node = Node(i)
        node.c = rng.randint(500, 1500)            # MIPS   (Table 2)
        node.m = rng.randint(150, 250)
        node.b = rng.randint(10, 1000)
        node.pc = rng.uniform(0.1, 0.4)            # cost rate (Table 2)
        node.d = rng.randint(1, 10)                # ms
        node.pmax = rng.uniform(40, 100)           # W      (Table 2)
        node.pmin = rng.uniform(0.6, 1.0) * node.pmax
        fog_nodes.append(node)
    for i in range(ncloud):
        node = Node(nfog + i)
        node.c = rng.randint(3000, 5000)           # MIPS   (Table 2)
        node.m = rng.randint(8192, 65536)
        node.b = rng.randint(100, 10000)
        node.pc = rng.uniform(0.7, 1.0)            # cost rate (Table 2)
        node.d = rng.randint(200, 500)             # ms
        node.pmax = rng.uniform(100, 200)          # W      (Table 2)
        node.pmin = rng.uniform(0.6, 1.0) * node.pmax
        cloud_nodes.append(node)
    # efficiency coefficients, normalised to (0, 1] within each tier
    for tier in (fog_nodes, cloud_nodes):
        if not tier:
            continue
        max_pe = max(n.c / n.pmax for n in tier)
        max_ce = max(n.c / n.pc for n in tier)
        for n in tier:
            n.pe = (n.c / n.pmax) / max_pe
            n.ce = (n.c / n.pc) / max_ce
    return fog_nodes, cloud_nodes


def reset(fog, cloud):
    for n in fog + cloud:
        n.a = 0.0
        n.procCost = 0.0
        n.eng = 0.0
