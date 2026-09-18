"""Figure 1: logistics network topology with optimal configurations (a) and per-city optimal daily cost breakdown (b)."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
import numpy as np
from config.parameters import get_daily_demand, LEAD_TIME, STORAGE_CONVERSION

def darken_color(hex_color: str, factor: float = 0.65):
    """Darken a HEX color by the given factor."""
    rgb = mcolors.to_rgb(hex_color)
    return tuple(c * factor for c in rgb)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 9

COLOR_CITIES = {
    'A': '#E07A5F',
    'B': '#3D405B',
    'C': '#81B29A',
    'D': '#F2CC8F',
    'E': '#A8DADC'
}
DARK_TEXT_CITIES = {'D', 'E'}
COLOR_STORAGE = '#E07A5F'
COLOR_TRANSPORT = '#3D405B'

with open('data/results.json', 'r') as f:
    data = json.load(f)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2), dpi=300)
plt.subplots_adjust(wspace=0.28)

# =================== LEFT panel: network topology ===================
ax1.set_aspect('equal')

cdc_x, cdc_y = 0, 0
ax1.scatter(cdc_x, cdc_y, s=400, c='#2A2A2A', zorder=5, edgecolors='white', linewidths=2)
ax1.annotate('CDC', (cdc_x, cdc_y), textcoords="offset points", xytext=(-14, 0),
            ha='right', va='center', fontsize=11, fontweight='bold')

cities = ['A', 'B', 'C', 'D', 'E']
display_distances = [50, 70, 90, 110, 120]
angles_deg = [100, 30, -30, -90, -150]
scale = 0.035

for i, city in enumerate(cities):
    angle = np.radians(angles_deg[i])
    d = display_distances[i] * scale
    cx = cdc_x + d * np.cos(angle)
    cy = cdc_y + d * np.sin(angle)

    ax1.plot([cdc_x, cx], [cdc_y, cy], 'k-', linewidth=1.0, alpha=0.25, zorder=1)
    star_color = darken_color(COLOR_CITIES[city], 0.65)
    ax1.scatter(cx, cy, s=420, color=star_color, marker='*', zorder=4,
               edgecolors='white', linewidths=1.2)

    text_color = '#2A2A2A' if city in DARK_TEXT_CITIES else 'black'
    n_small = data['cities'][city]['n_small']
    n_large = data['cities'][city]['n_large']
    parts = []
    if n_small > 0:
        parts.append(f"{n_small}Type-S")
    if n_large > 0:
        parts.append(f"{n_large}Type-L")
    veh_label = "+".join(parts)
    anchor_radius = 1.8 if city in ('A', 'B') else 1.4
    ax_x = cx + anchor_radius * np.cos(angle)
    ax_y = cy + anchor_radius * np.sin(angle)

    text_offsets = {
        'A': (-56, -10),
        'B': (18, 0),
        'C': (23, 0),
        'D': (-8, 0),
        'E': (0, 0),
    }
    tx, ty = text_offsets[city]

    ax1.annotate(f'{city}  T*={data["cities"][city]["optimal_T"]}',
                (ax_x, ax_y), textcoords="offset points",
                xytext=(tx, ty),
                ha='center', va='center', fontsize=9, fontweight='bold',
                color=text_color,
                bbox=dict(boxstyle='round,pad=0.22', facecolor='white', edgecolor='none', alpha=0.95))

    ax1.annotate(veh_label,
                (ax_x, ax_y), textcoords="offset points",
                xytext=(tx, ty - 13),
                ha='center', va='top', fontsize=7, color='dimgray', style='italic')

    n_stations = data['cities'][city]['station_count']
    station_radius = 0.9
    station_angles = np.linspace(0, 2*np.pi, n_stations, endpoint=False)

    optimal_T = data['cities'][city]['optimal_T']
    for j, sa in enumerate(station_angles):
        sx = cx + station_radius * np.cos(sa)
        sy = cy + station_radius * np.sin(sa)
        daily = get_daily_demand(city, j)
        peak_inventory = daily * (optimal_T + LEAD_TIME)
        area = peak_inventory / STORAGE_CONVERSION
        point_size = area * 0.7 + 5
        ax1.scatter(sx, sy, s=point_size, c=COLOR_CITIES[city], alpha=0.9, zorder=3,
                   edgecolors='white', linewidths=0.8)
        ax1.plot([cx, sx], [cy, sy], '-', color=COLOR_CITIES[city], linewidth=0.9, alpha=0.6, zorder=2)

ax1.set_xlim(-6.5, 6.5)
ax1.set_ylim(-5.5, 5.5)
ax1.axis('off')
ax1.text(0.02, 1.02, '(a) Logistics Network Topology and Optimal Configurations',
         transform=ax1.transAxes, fontsize=10, fontweight='bold', va='top', ha='left')

legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#2A2A2A', markersize=10, label='CDC'),
    Line2D([0], [0], marker='*', color='w', markerfacecolor='dimgray', markersize=12, label='City (optimal T*)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=5, label='Retail Station (size ∝ inventory)'),
]
ax1.legend(handles=legend_elements, loc='upper right', frameon=False, fontsize=9,
          bbox_to_anchor=(1.0, 1.0))

# =================== RIGHT panel: cost breakdown ===================
storage = [data['cities'][c]['storage_cost'] for c in cities]
transport = [data['cities'][c]['transport_cost'] for c in cities]
optimal_T = [data['cities'][c]['optimal_T'] for c in cities]

x = np.arange(len(cities))
width = 0.6

bars1 = ax2.bar(x, storage, width, label='Storage Cost', color=COLOR_STORAGE, edgecolor='white', linewidth=0.5)
bars2 = ax2.bar(x, transport, width, bottom=storage, label='Transport Cost', color=COLOR_TRANSPORT, edgecolor='white', linewidth=0.5)

for i, (s, t, T) in enumerate(zip(storage, transport, optimal_T)):
    ax2.annotate(f'T*={T}', (x[i], s + t), textcoords="offset points",
                xytext=(0, 6), ha='center', va='bottom', fontsize=10, fontweight='bold')

ax2.set_ylabel('Daily Cost (CNY)', fontsize=10)
ax2.set_xlabel('City', fontsize=10, labelpad=8)
ax2.set_xticks(x)
ax2.set_xticklabels(cities, fontsize=9)
ax2.tick_params(axis='y', labelsize=8, colors='dimgray')
ax2.tick_params(axis='x', labelsize=9, colors='black')
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_linewidth(0.8)
ax2.spines['left'].set_bounds(0, 10000)
ax2.spines['bottom'].set_linewidth(0.8)

ax2.text(0.02, 1.02, '(b) Optimal Daily Cost Breakdown by City',
         transform=ax2.transAxes, fontsize=10, fontweight='bold', va='top', ha='left')
ax2.legend(loc='upper right', frameon=False, fontsize=9,
          bbox_to_anchor=(1.0, 1.0))
ax2.set_ylim(0, 11000)

plt.tight_layout()
plt.savefig('figures/fig1.pdf', bbox_inches='tight', pad_inches=0.05)
plt.savefig('figures/fig1.png', dpi=300, bbox_inches='tight', pad_inches=0.05)
plt.close()
print('Figure 1 saved.')
