# Enhanced Lemurs Optimizer (ELO) for Multi-Objective Task Scheduling in Heterogeneous Fog‚ÄìCloud Architectures

Source code, random seeds, and per-run results for the paper:

> N. Ababneh, A. K. Abasi, Y. Hamid, and A. Koci, "Enhanced Lemurs Optimizer for Multi-Objective Task Scheduling in Heterogeneous Fog‚ÄìCloud Architectures," *Journal of Cloud Computing* (under review).

The repository contains everything needed to reproduce all tables, figures, and statistical tests of the paper.

---

## Overview

ELO schedules *N* independent tasks on a heterogeneous set of fog nodes and one cloud server. It jointly minimizes three objectives through a weighted-sum fitness (Eq. 16 of the paper):

- **Makespan** `T_max` (ms)
- **Energy consumption** (J)
- **Processing cost** (monetary units)

ELO has two phases:

1. **Heuristic initialization** (Eqs. 20‚Äì23). Tasks are assigned one by one to the node with the best combination of completion time, power efficiency, and cost efficiency, which produces a schedule `X0`.
2. **LO refinement** (Algorithm 2). The Lemurs Optimizer refines a population seeded with `X0`, using a linearly decaying jump rate, greedy selection, and elitism.

The algorithm is compared with the original **LO**, **GA**, **SA**, **P2C** (Power of Two Choices), **Random**, and the Pareto-based **NSGA-II**.

---

## Repository structure

```
.
‚îú‚îÄ‚îÄ code/
‚îÇ   ‚îú‚îÄ‚îÄ tasks.py                          # seeded task generator (ranges of Table 3)
‚îÇ   ‚îú‚îÄ‚îÄ nodes.py                          # seeded fog/cloud node generator; pe/ce efficiency coefficients
‚îÇ   ‚îú‚îÄ‚îÄ calculate_min_values.py           # normalization baselines M_min, E_min, C_min (Eqs. 13‚Äì15)
‚îÇ   ‚îú‚îÄ‚îÄ evaluate_solution.py              # makespan, energy, cost, fitness (Eqs. 5‚Äì11, 16); evaluation counter
‚îÇ   ‚îú‚îÄ‚îÄ proposed_scheduling.py            # ELO heuristic initialization (Eqs. 20‚Äì23)
‚îÇ   ‚îú‚îÄ‚îÄ hybird_lo_scheduling.py           # ELO = heuristic initialization + LO refinement (Algorithm 2)
‚îÇ   ‚îú‚îÄ‚îÄ lo_scheduling.py                  # original LO (Algorithm 1); shared refinement engine
‚îÇ   ‚îú‚îÄ‚îÄ ga_scheduling.py                  # GA baseline
‚îÇ   ‚îú‚îÄ‚îÄ simulated_annealing_scheduling.py # SA baseline
‚îÇ   ‚îú‚îÄ‚îÄ p2c_scheduling.py                 # P2C baseline
‚îÇ   ‚îú‚îÄ‚îÄ random_scheduling.py              # Random baseline
‚îÇ   ‚îú‚îÄ‚îÄ nsga2_scheduling.py               # NSGA-II baseline
‚îÇ   ‚îú‚îÄ‚îÄ run_experiments.py                # main experiments (100‚Äì1000 tasks)
‚îÇ   ‚îú‚îÄ‚îÄ run_r25.py                        # ablation study and ELO vs. NSGA-II comparison
‚îÇ   ‚îú‚îÄ‚îÄ make_tables.py                    # result tables (mean ¬± std)
‚îÇ   ‚îú‚îÄ‚îÄ statistics.py                     # Wilcoxon (exact, Holm), Friedman/Nemenyi tests
‚îÇ   ‚îú‚îÄ‚îÄ sensitivity.py                    # weight sensitivity analysis
‚îÇ   ‚îú‚îÄ‚îÄ make_figures.py                   # convergence curves and boxplots
‚îÇ   ‚îî‚îÄ‚îÄ make_pareto_figure.py             # ELO vs. NSGA-II non-dominated solutions
‚îî‚îÄ‚îÄ results/
    ‚îú‚îÄ‚îÄ runs_100-400.csv                  # main experiments, 100‚Äì400 tasks
    ‚îú‚îÄ‚îÄ runs_500-1000.csv                 # scalability experiments, 500 and 1000 tasks
    ‚îú‚îÄ‚îÄ ablation.csv                      # ELO ablation variants
    ‚îú‚îÄ‚îÄ nsga2.csv                         # ELO vs. NSGA-II (fitness, hypervolume, front size, runtime)
    ‚îú‚îÄ‚îÄ wilcoxon.csv                      # paired Wilcoxon tests
    ‚îú‚îÄ‚îÄ friedman_ranks.csv                # Friedman mean ranks (120 matched instances)
    ‚îî‚îÄ‚îÄ random_assignment.csv             # share of tasks per node for the Random scheduler
```

---

## Requirements

- Python ‚â• 3.10 (the reported experiments used Python 3.11)
- NumPy, SciPy, pandas, matplotlib

```bash
pip install numpy scipy pandas matplotlib
```

No external fog‚Äìcloud simulator is required.

---

## Reproducing the results

All commands are run from the `code/` directory.

```bash
cd code

# 1. Main experiments: 100, 200, 300, 400 tasks, 30 runs, 6 algorithms  ->  results/runs.csv
python run_experiments.py

# 2. Scalability experiments: 500 and 1000 tasks  ->  results_large/runs.csv
SIZES=500,1000 OUT=results_large python run_experiments.py

# 3. Ablation study and NSGA-II comparison  ->  results/ablation.csv, results/nsga2.csv
python run_r25.py

# 4. Tables, statistical tests, sensitivity analysis, and figures
python make_tables.py
python statistics.py
python sensitivity.py
python make_figures.py          # writes PDFs to ../images/
python make_pareto_figure.py    # writes PDF to ../images/
```

Steps 1‚Äì3 regenerate `code/results/runs.csv`, `code/results_large/runs.csv`, `code/results/ablation.csv`, and `code/results/nsga2.csv`. The copies in the top-level `results/` folder are the files used in the paper; they are renamed (`runs_100-400.csv`, `runs_500-1000.csv`) and identical to what the scripts produce. The figure scripts write to `../images/`, so create that folder first (`mkdir ../images`).

On Windows, set the environment variables for step 2 separately:
`set SIZES=500,1000` and `set OUT=results_large` (cmd), or `$env:SIZES="500,1000"; $env:OUT="results_large"` (PowerShell).

On a single core, step 1 takes about 1 minute, step 2 about 3 minutes, and step 3 about 2 minutes.

### Mapping to the paper

| Paper item | Script | Output |
|---|---|---|
| Table 2 (normalization baselines) | `run_experiments.py` | columns `min_M_s`, `min_E_J`, `min_C` |
| Tables 4‚Äì7 (makespan, energy, cost, fitness) | `make_tables.py` | `results/table_*.tex` |
| Table 8 (ablation) | `run_r25.py` | `results/ablation.csv` |
| Table 9, Fig. 4 (NSGA-II) | `run_r25.py`, `make_pareto_figure.py` | `results/nsga2.csv` |
| Table 10 (Wilcoxon) | `statistics.py` | `results/wilcoxon.csv` |
| Table 11 (Friedman / Nemenyi) | `statistics.py` | `results/friedman_ranks.csv` |
| Table 12 (weight sensitivity) | `sensitivity.py` | `results/table_sensitivity.tex` |
| Table 13 (runtime) | `run_experiments.py`, `run_r25.py` | column `runtime_s` |
| Table 14 (scalability) | `run_experiments.py` (step 2) | `results_large/runs.csv` |
| Fig. 3 (convergence), Fig. 5 (boxplots) | `make_figures.py` | `../images/*.pdf` |

---

## Experimental protocol

- **Paired design.** For task size *N* and run *r* (r = 0, ‚Ä¶, 29), one problem instance (tasks and nodes) is generated from the seed `1000¬∑N + r` and shared by all algorithms.
- **Seeds.** Algorithm *a* uses the NumPy generator `default_rng([1000¬∑N + r, a])`, with a = 0 ELO, 1 LO, 2 GA, 3 P2C, 4 SA, 5 Random, and 6 NSGA-II. The ablation variants use a = 100 + variant index. Results are therefore fully reproducible.
- **Evaluation budget.** ELO, LO, GA, and SA use 1010 fitness evaluations (P = 10, T = 100); NSGA-II uses 1000 (population 20, 49 generations).
- **Parameters.** jr_max = 0.70, jr_min = 0.05. GA uses roulette selection, one-point crossover, mutation 0.05, and 2 elites. SA uses a temperature schedule of 0.05 ‚Üí 1e-4. Parameter ranges follow Table 3 of the paper.
- **Fog/cloud configuration.** 3 fog nodes for 100‚Äì200 tasks, 9 fog nodes for 300‚Äì1000 tasks, and 1 cloud server.
- **Units.** Makespan in ms, energy in J, cost in monetary units.

---

## Result files

`runs_*.csv` contains one row per (task size, run, algorithm):

| Column | Description |
|---|---|
| `N`, `nfog`, `run`, `seed` | task size, number of fog nodes, run index, instance seed |
| `algorithm` | ELO, LO, GA, P2C, SA, Random |
| `makespan_ms` | makespan T_max (ms) |
| `energy_J` | total energy consumption (J) |
| `cost` | total processing cost |
| `fitness` | weighted-sum fitness (Eq. 16), in (0, 1] |
| `runtime_s` | wall-clock time of the run (s) |
| `evaluations` | number of fitness evaluations used |
| `min_M_s`, `min_E_J`, `min_C` | normalization baselines of the instance |
| `deadline_rate` | share of tasks that meet their deadline (secondary metric, not optimized) |

---

## Citation

If you use this code, please cite the paper (the full reference will be added upon publication):

```bibtex
@article{ababneh2026elo,
  title   = {Enhanced Lemurs Optimizer for Multi-Objective Task Scheduling in Heterogeneous Fog--Cloud Architectures},
  author  = {Ababneh, Nedal and Abasi, Ammar Kamal and Hamid, Yasir and Koci, Artur},
  journal = {Journal of Cloud Computing},
  year    = {2026},
  note    = {Under review}
}
```

---

## License

This code is released under the MIT License (see `LICENSE`).

## Contact

Nedal Ababneh ‚Äî Nedal.Ababneh@ukf.ac.ae
Ammar Kamal Abasi ‚Äî ammar.abasi@actvet.gov.ae

