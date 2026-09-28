#!/usr/bin/env python3
"""Fig 3: baseline comparison timeline for VP-2 resonance report."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data") + os.sep
FIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures") + os.sep
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'axes.grid': True, 'grid.alpha': .25, 'grid.linestyle': ':',
                     'axes.spines.top': False, 'axes.spines.right': False})

labels = ['pre-rebuild\nbaseline\n(Claude, ~Aug)', 'after toolhead\nrebuild\n(Claude)', '2026-09-25\n(this sweep)\nmzv fit']
xv = [28.8, 60.8, 69.8]
yv = [39.0, 31.2, 37.4]

fig, ax = plt.subplots(figsize=(8.5, 4.4))
ax.axhspan(55, 85, color='#8ec9f5', alpha=.35, label='healthy X band (300-350mm CoreXY)')
ax.axhspan(25, 45, color='#c8e6c9', alpha=.35, label='Y band (any CoreXY; mass-limited)')
xi = np.arange(3)
b1 = ax.bar(xi - .18, xv, .34, color='#e5533c', alpha=.9, label='X dominant (Hz)')
b2 = ax.bar(xi + .18, yv, .34, color='#3b7dd8', alpha=.9, label='Y dominant (Hz)')
for r, v in zip(b1, xv):
    ax.text(r.get_x() + r.get_width()/2, v + 1.2, f'{v:g}', ha='center', fontsize=8.5, color='#e5533c', fontweight='bold')
for r, v in zip(b2, yv):
    ax.text(r.get_x() + r.get_width()/2, v + 1.2, f'{v:g}', ha='center', fontsize=8.5, color='#3b7dd8', fontweight='bold')
ax.set_xticks(xi); ax.set_xticklabels(labels, fontsize=8)
ax.set_ylabel('dominant resonance (Hz)')
ax.set_ylim(0, 95)
ax.set_title('VanderPrint-2 resonance baseline — X gained 2.4x stiffness, Y plateaued', fontsize=10)
ax.legend(fontsize=7.5, loc='upper left', ncol=2)
fig.tight_layout()
fig.savefig(FIGS + 'fig3-baseline.png', dpi=150, bbox_inches='tight')
print('ok')
