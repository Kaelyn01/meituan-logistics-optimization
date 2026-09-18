# Meituan Multi-City Joint Inventory–Routing Optimization

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Tests](https://github.com/Kaelyn01/meituan-logistics-optimization/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-green)

## Abstract

This repository provides a **joint inventory–routing optimization framework** for a multi-city fresh-food logistics network. Given one central distribution center (CDC) and five satellite cities (25 retail stations in total), the model determines the optimal replenishment cycle $T^* \in \{1,\dots,7\}$ for each city and the corresponding vehicle routing plans. The objective is to minimize the sum of daily inventory holding and transportation costs. A complete enumeration of all $7^5 = 16{,}807$ global $T$-combinations guarantees system-wide optimality. The best policy achieves a total daily cost of **24,874 CNY**, outperforming uniform-$T$ baselines by up to **80.6%**.

## Problem Statement

A consumer-goods company replenishes 25 retail stations across five satellite cities from a single CDC. The task is to jointly optimize:

1. **Inventory** — the replenishment cycle $T \in \{1, 2, \dots, 7\}$ days of each city
2. **Routing** — the vehicle dispatch plan per city (station grouping + vehicle type + unloading sequence)

with the objective

```
Min Total Cost = Σ(daily transport cost + daily holding cost)
```

## Key Results

```
Global optimal solution:
   City A: T=1 day,  daily cost = 9,130 CNY
   City B: T=1 day,  daily cost = 6,215 CNY
   City C: T=2 days, daily cost = 4,915 CNY
   City D: T=3 days, daily cost = 2,928 CNY
   City E: T=6 days, daily cost = 1,686 CNY

Minimum system total daily cost: 24,874 CNY
   - Total holding cost:      13,409 CNY (53.9%)
   - Total transport cost:    11,465 CNY (46.1%)
```

The optimal differentiated policy undercuts the best uniform-$T$ baseline by up to **80.6%**.

**Utilization insight**: in City B, the station group `[B_4, B_5]` reaches only 42.5% utilization with a large vehicle, showing that distant, low-demand station pairs are prone to idle capacity — whereas City A's `[A_3, A_4, A_5]` achieves 95% utilization, confirming that dense high-demand clusters use capacity efficiently.

## Quick Start

### Installation

```bash
git clone https://github.com/Kaelyn01/meituan-logistics-optimization.git
cd meituan-logistics-optimization
pip install -r requirements.txt
```

### Run the optimization

```bash
python main.py
```

The pipeline executes:

1. Standalone per-city optimization
2. Global joint optimization (full enumeration of $7^5 = 16{,}807$ combinations)
3. Detailed reports written to `output/`

### Run the tests

```bash
python -m pytest tests/ -v
```

### Regenerate the figures

```bash
python scripts/fig1.py   # network topology + cost breakdown
python scripts/fig2.py   # T-sensitivity analysis
python scripts/fig3.py   # top-10 vs uniform-T baselines
```

Figures are written to `figures/`; the paper references them via `../figures/`.

## Repository Structure

```
meituan-logistics-optimization/
├── main.py                     # Entry point
├── config/                     # Configuration
│   └── parameters.py           # Fixed inputs (vehicles, distances, demands)
├── models/                     # Cost models
│   └── cost_models.py          # Holding + transportation cost functions
├── optimization/               # Optimization algorithms
│   ├── route_optimizer.py      # Station grouping + vehicle dispatch
│   ├── inventory_optimizer.py  # Per-city optimal cycle search
│   └── global_search.py        # Global enumeration (16,807 combinations)
├── tests/                      # Unit tests
│   ├── test_config.py
│   └── test_cost_models.py
├── scripts/                    # Figure generation scripts
│   ├── fig1.py                 # Topology + cost breakdown (combined)
│   ├── fig2.py                 # T-sensitivity (2x3 panels)
│   └── fig3.py                 # Top-10 vs uniform-T comparison
├── data/
│   └── results.json            # Optimal per-city results (figures + paper)
├── figures/                    # Generated figures (png / pdf)
├── report/                     # Academic paper
│   ├── main.tex                # LaTeX source
│   └── main.pdf                # Compiled PDF
└── output/                     # Runtime outputs (gitignored)
```

## Core Modules

### `route_optimizer.py` — Routing

- **Algorithm**: backtracking enumeration of all legal station partitions (≤3 stations per trip), retaining the minimum-cost plan
- **Features**: multi-vehicle dispatch (automatic splitting when station demand × T exceeds capacity) and per-vehicle load-rate evolution across stops (before/after unloading)

### `inventory_optimizer.py` — Inventory

- **Algorithm**: sweeps T = 1..7 and computes the total cost under each cycle
- **Output**: optimal T, cost breakdown, per-T comparison

### `global_search.py` — Global optimization

- **Algorithm**: complete enumeration of 16,807 T-combinations (5 cities × 7 cycles)
- **Output**: global optimum + top-10 alternatives

**Complexity**: station grouping scales with the Bell number $B_n$ (~203 partitions for 6 stations); the global search performs $O(7^5 \times 5 \times B_6) \approx 3.4$M evaluations and completes in seconds on commodity hardware.

## Problem Data

### City parameters

| City | CDC distance | Rent (CNY/m²/day) | Stations | Daily demand (pcs) | Profile |
| --- | --- | --- | --- | --- | --- |
| A | 40 km | 5.0 | 6 | 405,000 | Near suburb, expensive land |
| B | 70 km | 4.0 | 5 | 250,000 | Business district, high rent |
| C | 100 km | 3.0 | 5 | 200,000 | Standard region |
| D | 140 km | 2.0 | 5 | 125,000 | Outer suburb |
| E | 180 km | 1.5 | 4 | 57,000 | Remote, cheapest land |

### Vehicle parameters

| Vehicle | Capacity | Fixed cost | Variable cost |
| --- | --- | --- | --- |
| Small (Type-S) | 80,000 pcs | 300 CNY/trip | 4.0 CNY/km |
| Large (Type-L) | 200,000 pcs | 600 CNY/trip | 6.5 CNY/km |

### Constraints

- At most 3 stations per vehicle trip
- No cross-city routes
- Integer replenishment cycle T ∈ {1, …, 7} days
- All stations within a city share the same T
- Every vehicle returns to the CDC

## Figures

| Figure | Description | Script |
| --- | --- | --- |
| Fig 1 | Network topology with optimal configurations + daily cost breakdown | `scripts/fig1.py` |
| Fig 2 | T-sensitivity of daily cost for all five cities (2×3) | `scripts/fig2.py` |
| Fig 3 | Global top-10 solutions vs uniform-T baselines | `scripts/fig3.py` |

## Paper

| Version | File |
| --- | --- |
| English | [report/main.pdf](report/main.pdf) |

The paper derives the mathematical model, algorithm pseudocode, sensitivity analysis, and managerial implications. LaTeX source: `report/main.tex`.

## Output Files

Running `python main.py` writes to `output/`:

| File | Description |
| --- | --- |
| `optimal_solution_*.json` | Detailed optimal solution (JSON) |
| `top_solutions_*.json` | Top-10 solution list |
| `optimization_report_*.txt` | Text report with full vehicle dispatch plan |

## Dependencies

- Python 3.10+
- [requirements.txt](requirements.txt): numpy, matplotlib
- A LaTeX distribution (MacTeX / TeX Live), optional, only for recompiling the paper

## License

[MIT](LICENSE)
