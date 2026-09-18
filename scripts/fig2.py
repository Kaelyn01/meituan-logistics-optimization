"""Fix Figure 2: title/legend aligned with Fig 1 style, axis hierarchy clarified."""

import json
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 9

COLOR_STORAGE = '#E07A5F'
COLOR_TRANSPORT = '#3D405B'

with open('data/results.json', 'r') as f:
    data = json.load(f)

fig, ax = plt.subplots(figsize=(7, 5), dpi=300)

cities = ['A', 'B', 'C', 'D', 'E']
storage = [data['cities'][c]['storage_cost'] for c in cities]
transport = [data['cities'][c]['transport_cost'] for c in cities]
optimal_T = [data['cities'][c]['optimal_T'] for c in cities]

x = np.arange(len(cities))
width = 0.6

bars1 = ax.bar(x, storage, width, label='Storage Cost', color=COLOR_STORAGE, edgecolor='white', linewidth=0.5)
bars2 = ax.bar(x, transport, width, bottom=storage, label='Transport Cost', color=COLOR_TRANSPORT, edgecolor='white', linewidth=0.5)

# Annotate optimal T on top
for i, (s, t, T) in enumerate(zip(storage, transport, optimal_T)):
    ax.annotate(f'T*={T}', (x[i], s + t), textcoords="offset points",
                xytext=(0, 6), ha='center', va='bottom', fontsize=10, fontweight='bold')

# Axis labels (slightly larger/bolder than ticks)
ax.set_ylabel('Daily Cost (CNY)', fontsize=10)
ax.set_xlabel('City', fontsize=10, labelpad=8)
ax.set_xticks(x)
ax.set_xticklabels(cities, fontsize=9)

# Distinguish tick labels from axis labels: make ticks gray and smaller
ax.tick_params(axis='y', labelsize=8, colors='dimgray')
ax.tick_params(axis='x', labelsize=9, colors='black')

# Format y-axis with thousand separators
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

# Clean spines (academic style)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(0.8)
ax.spines['left'].set_bounds(0, 10000)
ax.spines['bottom'].set_linewidth(0.8)

# Title at top-left like Fig 1
ax.text(0.02, 0.98, '(b) Optimal Daily Cost Breakdown by City',
        transform=ax.transAxes, fontsize=10, fontweight='bold',
        va='top', ha='left')

# Legend at top-right like Fig 1
ax.legend(loc='upper right', frameon=False, fontsize=9,
          bbox_to_anchor=(1.0, 1.0))

ax.set_ylim(0, 11000)

plt.tight_layout()
plt.savefig('figures/fig2.pdf', bbox_inches='tight', pad_inches=0.05)
plt.savefig('figures/fig2.png', dpi=300, bbox_inches='tight', pad_inches=0.05)
plt.close()
print('Fig 2 fixed and saved.')
