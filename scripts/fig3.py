"""Figure 3: global top-10 solutions versus uniform-T baselines."""

import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

import matplotlib.pyplot as plt
import numpy as np

from optimization.inventory_optimizer import calculate_city_total_cost

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 9

COLOR_OPTIMAL = '#81B29A'
COLOR_BASELINE = '#D3D3D3'

# Load top 10 solutions and optimal cost from central data
with open('data/results.json', 'r') as f:
    data = json.load(f)

top_solutions = data['top_solutions']
top_costs = [sol['total_cost'] for sol in top_solutions[:10]]
optimal_cost = data['global_optimal']['total_cost']

# Compute uniform-T baselines
uniform_costs = {}
for T in [1, 3, 7]:
    uniform_costs[T] = sum(calculate_city_total_cost(c, T)['total_cost'] for c in ['A', 'B', 'C', 'D', 'E'])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 5), dpi=300)
plt.subplots_adjust(wspace=0.35)

# --- Left: Top 10 solutions ---
y_pos = np.arange(10, 0, -1)
colors = [COLOR_OPTIMAL] + [COLOR_BASELINE] * 9
bars1 = ax1.barh(y_pos, top_costs, color=colors, edgecolor='white', height=0.6)

# Annotations: cost difference
for i, (cost, y) in enumerate(zip(top_costs, y_pos)):
    diff = cost - optimal_cost
    if i == 0:
        ax1.text(cost + 8, y, f'{cost:.0f}', va='center', ha='left', fontsize=9, fontweight='bold', color='darkgreen')
    else:
        ax1.text(cost + 8, y, f'+{diff:.0f}', va='center', ha='left', fontsize=9, color='gray')

ax1.set_yticks(y_pos)
ax1.set_yticklabels([f'#{i}' for i in range(1, 11)], fontsize=9)
ax1.set_xlabel('Total Daily Cost (CNY)', fontsize=10)
ax1.set_xlim(24850, 25040)
ax1.tick_params(axis='x', labelsize=8, colors='dimgray')
ax1.tick_params(axis='y', labelsize=9, colors='black')
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_linewidth(0.8)
ax1.spines['bottom'].set_linewidth(0.8)

# Title top-left for left subplot
ax1.text(0.02, 1.02, '(d) Top 10 Joint Optimization Solutions',
         transform=ax1.transAxes, fontsize=10, fontweight='bold', va='top', ha='left')

# --- Right: Uniform-T baseline comparison ---
labels = ['Global\nOptimal', 'All T=1', 'All T=3', 'All T=7']
values = [optimal_cost, uniform_costs[1], uniform_costs[3], uniform_costs[7]]
colors2 = [COLOR_OPTIMAL, COLOR_BASELINE, COLOR_BASELINE, COLOR_BASELINE]

bars2 = ax2.bar(labels, values, color=colors2, edgecolor='white', width=0.6)

for i, (label, val) in enumerate(zip(labels, values)):
    diff = val - optimal_cost
    if i == 0:
        ax2.text(i, val - 1200, f'{val:.0f}', ha='center', va='top', fontsize=11, fontweight='bold', color='white')
    else:
        ax2.text(i, val - 1500, f'+{diff:.0f}', ha='center', va='top', fontsize=10, fontweight='bold', color='white')

ax2.set_ylabel('Total Daily Cost (CNY)', fontsize=10)
ax2.tick_params(axis='y', labelsize=8, colors='dimgray')
ax2.tick_params(axis='x', labelsize=9, colors='black')
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_linewidth(0.8)
ax2.spines['left'].set_bounds(0, 45000)
ax2.spines['bottom'].set_linewidth(0.8)

# Title top-left for right subplot
ax2.text(0.02, 1.02, '(e) Comparison with Uniform-T Strategies',
         transform=ax2.transAxes, fontsize=10, fontweight='bold', va='top', ha='left')

ax2.set_ylim(0, 46000)

plt.tight_layout()
plt.savefig('figures/fig3.pdf', bbox_inches='tight', pad_inches=0.05)
plt.savefig('figures/fig3.png', dpi=300, bbox_inches='tight', pad_inches=0.05)
plt.close()
print('Figure 3 saved.')
