"""Figure 1: A shifted slightly counter-clockwise, A/B labels raised."""

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
    """将 HEX 颜色加深。"""
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

with open('data/results.json', 'r') as f:
    data = json.load(f)

fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
ax.set_aspect('equal')

# CDC centered, label on left
cdc_x, cdc_y = 0, 0
ax.scatter(cdc_x, cdc_y, s=400, c='#2A2A2A', zorder=5, edgecolors='white', linewidths=2)
ax.annotate('CDC', (cdc_x, cdc_y), textcoords="offset points", xytext=(-14, 0),
            ha='right', va='center', fontsize=11, fontweight='bold')

cities = ['A', 'B', 'C', 'D', 'E']
display_distances = [50, 70, 90, 110, 120]
# Shift A slightly counter-clockwise (from 90 to 100) to widen A-B gap
angles_deg = [100, 30, -30, -90, -150]
scale = 0.035

for i, city in enumerate(cities):
    angle = np.radians(angles_deg[i])
    d = display_distances[i] * scale
    cx = cdc_x + d * np.cos(angle)
    cy = cdc_y + d * np.sin(angle)
    
    ax.plot([cdc_x, cx], [cdc_y, cy], 'k-', linewidth=1.0, alpha=0.25, zorder=1)
    star_color = darken_color(COLOR_CITIES[city], 0.65)
    ax.scatter(cx, cy, s=420, color=star_color, marker='*', zorder=4,
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
    
    # Raise A/B labels a bit higher than others
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
    
    ax.annotate(f'{city}  T*={data["cities"][city]["optimal_T"]}', 
                (ax_x, ax_y), textcoords="offset points",
                xytext=(tx, ty),
                ha='center', va='center', fontsize=9, fontweight='bold',
                color=text_color,
                bbox=dict(boxstyle='round,pad=0.22', facecolor='white', edgecolor='none', alpha=0.95))
    
    ax.annotate(veh_label, 
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
        ax.scatter(sx, sy, s=point_size, c=COLOR_CITIES[city], alpha=0.9, zorder=3,
                   edgecolors='white', linewidths=0.8)
        ax.plot([cx, sx], [cy, sy], '-', color=COLOR_CITIES[city], linewidth=0.9, alpha=0.6, zorder=2)

ax.set_xlim(-6.5, 6.5)
ax.set_ylim(-5.5, 5.5)
ax.axis('off')

ax.set_title('(a) Logistics Network Topology and Optimal Configurations',
             fontsize=10, fontweight='bold', pad=15, y=1.02)

legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#2A2A2A', markersize=10, label='CDC'),
    Line2D([0], [0], marker='*', color='w', markerfacecolor='dimgray', markersize=12, label='City (optimal T*)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=5, label='Retail Station (size ∝ inventory)'),
]
ax.legend(handles=legend_elements, loc='upper right', frameon=False, fontsize=9,
          bbox_to_anchor=(1.0, 1.0))

plt.tight_layout()
plt.savefig('figures/fig1.pdf', bbox_inches='tight', pad_inches=0.05)
plt.savefig('figures/fig1.png', dpi=300, bbox_inches='tight', pad_inches=0.05)
plt.close()
print('Fig 1 fixed and saved.')
