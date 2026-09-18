"""Figure 2: T-sensitivity of daily cost for all five cities (2x3 layout)."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

import matplotlib.pyplot as plt
import numpy as np

from optimization.inventory_optimizer import calculate_city_total_cost

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 9

COLOR_STORAGE = '#E07A5F'
COLOR_TRANSPORT = '#3D405B'
COLOR_TOTAL = '#81B29A'

cities = ['A', 'B', 'C', 'D', 'E']

import json
with open('data/results.json', 'r') as f:
    _data = json.load(f)
_optimal_T_map = {c: _data['cities'][c]['optimal_T'] for c in cities}
T_range = np.arange(1, 8)

fig, axes = plt.subplots(2, 3, figsize=(12, 8), dpi=300)
axes = axes.flatten()

for idx, city in enumerate(cities):
    ax = axes[idx]
    storage = []
    transport = []
    total = []
    for T in T_range:
        res = calculate_city_total_cost(city, T)
        storage.append(res['storage_cost'])
        transport.append(res['transport_cost'])
        total.append(res['total_cost'])

    ax.plot(T_range, storage, 'o-', color=COLOR_STORAGE, label='Storage Cost', linewidth=2, markersize=6)
    ax.plot(T_range, transport, 's-', color=COLOR_TRANSPORT, label='Transport Cost', linewidth=2, markersize=6)
    ax.plot(T_range, total, '^--', color=COLOR_TOTAL, label='Total Cost', linewidth=2.5, markersize=8)

    # Optimal marker
    optimal_T = _optimal_T_map[city]
    opt_total = total[optimal_T - 1]
    ax.axvline(x=optimal_T, color='gray', linestyle='--', alpha=0.6, linewidth=1)
    ax.plot(optimal_T, opt_total, '*', color='green', markersize=14, zorder=5)

    # Compute text position: place it near the top of the subplot in an empty corner
    y_top = max(total) * 1.05
    if idx == 0:  # City A: monotone ascending, text far upper-right
        tx = 5.5
    elif idx == 1:  # City B: monotone ascending, text far upper-right
        tx = 5.5
    elif idx == 2:  # City C: weak U, text upper-left
        tx = 1.3
    elif idx == 3:  # City D: U-shape, text upper-right
        tx = 5.8
    else:  # City E: U-shape, optimal at T=6 (right side), text upper-left
        tx = 1.5

    ax.annotate(f'Optimal\nT*={optimal_T}', xy=(optimal_T, opt_total),
                xytext=(tx, y_top),
                fontsize=9, color='green', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='green', lw=1,
                                connectionstyle='arc3,rad=0.15'))

    # Per-subplot title
    pad = 15 if city in ['D', 'E'] else 8
    ax.set_title(f'City {city}', fontsize=10, fontweight='bold', pad=pad)
    ax.set_xlabel('Replenishment Cycle T (days)', fontsize=9)
    ax.set_ylabel('Daily Cost (CNY)', fontsize=9)
    ax.set_xticks(T_range)

    # Tick hierarchy
    ax.tick_params(axis='y', labelsize=7, colors='dimgray')
    ax.tick_params(axis='x', labelsize=8, colors='black')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)

    # Y-limit with some padding
    ax.set_ylim(0, max(total) * 1.25)

# Remove the unused 6th subplot to make room for a bottom legend
fig.delaxes(axes[-1])

# Overall title at top-left of the figure
fig.text(0.02, 0.98, '(c) Cost Sensitivity to Replenishment Cycle by City',
         fontsize=11, fontweight='bold', va='top', ha='left')

# Shared legend at bottom center, horizontal layout
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', ncol=3, frameon=False,
           fontsize=11, bbox_to_anchor=(0.5, 0.02), columnspacing=2.5,
           handletextpad=1.0)

plt.tight_layout(rect=[0, 0.06, 1, 0.97])
plt.savefig('figures/fig2.pdf', bbox_inches='tight', pad_inches=0.05)
plt.savefig('figures/fig2.png', dpi=300, bbox_inches='tight', pad_inches=0.05)
plt.close()
print('Figure 2 saved.')
