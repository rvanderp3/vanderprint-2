#!/usr/bin/env python3
"""Fig 2 (fixed): normalized curves vs CoreXY reference bands, labeled."""
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

def load(name):
    d = np.genfromtxt(DATA + name, delimiter=',', names=True)
    return d['freq'], d['psd_x'], d['psd_y'], d['psd_z'], d['psd_xyz']

fx, xpx, *_ = load('x-resonance-sept25.csv')
fy, _, ypy, *_ = load('y-resonance-sept25.csv')

fig, (a1, a2) = plt.subplots(2, 1, figsize=(10.5, 6.2), sharex=True)
# X panel
a1.axvspan(55, 85, color='#8ec9f5', alpha=.45)
a1.axvspan(45, 70, color='#c8e6c9', alpha=.55)
a1.text(70, 1.03, 'compact CoreXY (300–350 mm): X 55–85 Hz', fontsize=7.5, ha='center', color='#2a5580')
a1.text(57.5, 1.03, '', fontsize=7.5)
a1.text(37, .55, '600 mm-class:\nX 45–70 Hz', fontsize=7.5, ha='center', color='#2e6b34')
a1.plot(fx, xpx/xpx.max(), lw=1.8, color='#e5533c', label='VP-2 X sweep (X channel)')
a1.axvline(69.8, color='k', ls='--', lw=1)
a1.annotate('mzv fit 69.8 Hz', (69.8, .78), fontsize=8, ha='right')
a1.set_ylabel('normalized PSD'); a1.set_ylim(0, 1.15)
a1.set_title('X axis — VP-2 vs typical CoreXY ranges', fontsize=10, loc='left')
a1.legend(fontsize=8, loc='upper left')

# Y panel
a2.axvspan(40, 60, color='#8ec9f5', alpha=.45)
a2.axvspan(25, 45, color='#c8e6c9', alpha=.55)
a2.text(50, 1.03, 'compact CoreXY: Y 40–60 Hz', fontsize=7.5, ha='center', color='#2a5580')
a2.text(18, .5, '600 mm-class:\nY 25–45 Hz', fontsize=7.5, ha='center', color='#2e6b34')
a2.plot(fy, ypy/ypy.max(), lw=1.8, color='#3b7dd8', label='VP-2 Y sweep (Y channel)')
a2.axvline(37.4, color='k', ls='--', lw=1)
a2.annotate('mzv fit 37.4 Hz', (37.4, .75), fontsize=8, ha='right')
a2.axvline(45.2, color='k', ls=':', lw=1)
a2.annotate('ei fit 45.2 Hz', (45.2, .5), fontsize=8)
a2.set_xlabel('frequency (Hz)'); a2.set_ylabel('normalized PSD'); a2.set_ylim(0, 1.15)
a2.set_xlim(0, 140)
a2.set_title('Y axis — VP-2 vs typical CoreXY ranges', fontsize=10, loc='left')
a2.legend(fontsize=8, loc='upper right')
fig.tight_layout()
fig.savefig(FIGS + 'fig2-corexy-overlay.png', dpi=150, bbox_inches='tight')
print('ok')
