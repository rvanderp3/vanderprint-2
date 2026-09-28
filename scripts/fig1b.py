#!/usr/bin/env python3
"""Fig 1 (fixed): resonance spectra with clean annotation placement."""
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

fx, xpx, xpy, xpz, xxyz = load('x-resonance-sept25.csv')
fy, ypx, ypy, ypz, yxyz = load('y-resonance-sept25.csv')
cols = dict(x='#e5533c', y='#3b7dd8', z='#7a7a7a')

fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), sharey=True)
for ax, (f, px, py, pz, ttl, ta) in [
    (axes[0], (fx, xpx, xpy, xpz, 'X sweep (AXIS=X excitation)', 'x')),
    (axes[1], (fy, ypx, ypy, ypz, 'Y sweep (AXIS=Y excitation)', 'y'))]:
    sig = px if ta == 'x' else py
    ax.plot(f, px, lw=.7, color=cols['x'], alpha=.45, label='psd_x')
    ax.plot(f, py, lw=.7, color=cols['y'], alpha=.45, label='psd_y')
    ax.plot(f, pz, lw=.7, color=cols['z'], alpha=.45, label='psd_z')
    ax.plot(f, sig, lw=2.0, color=cols[ta])
    ax.set_yscale('log'); ax.set_title(ttl, fontsize=10); ax.set_xlabel('frequency (Hz)')
axes[0].set_ylabel('power spectral density')

# X annotations — staggered, arrow-led, no collisions
ann_x = [
    (66.8, xxyz[np.argmin(abs(fx-66.8))], '66.8 Hz  Q≈4.8', (0, 34), 'center'),
    (72.8, xxyz[np.argmin(abs(fx-72.8))], '72.8 Hz  Q≈5.2  (dominant)', (-66, 26), 'center'),
    (98.0, xxyz[np.argmin(abs(fx-98.0))], '98 Hz  2nd hump', (0, 26), 'center'),
    (124.8, xxyz[np.argmin(abs(fx-124.8))], '117–131 Hz bump', (18, 30), 'center'),
]
for f0, y0, txt, off, ha in ann_x:
    i = np.argmin(np.abs(fx - f0))
    axes[0].annotate(txt, (fx[i], xxyz[i]), xytext=off, textcoords='offset points',
                     fontsize=7.5, ha=ha, color='#222',
                     arrowprops=dict(arrowstyle='->', lw=.7, color='#555'))
axes[0].annotate('Z channel tracks X response,\npeaks 96.5 Hz (−9.7 dB)', xy=(96.5, xpz[np.argmin(abs(fx-96.5))]),
                 xytext=(118, 6e5), fontsize=7.5, color='#555',
                 arrowprops=dict(arrowstyle='->', lw=.7, color='#888'))
# Y annotations
for f0, txt, off in [(35.7, '35.7 Hz  Q≈3.1  (dominant)', (-46, 22)),
                     (43.1, '43.1 Hz  shoulder\n(+Z tilt)', (26, -6))]:
    i = np.argmin(np.abs(fy - f0))
    axes[1].annotate(txt, (fy[i], yxyz[i]), xytext=off, textcoords='offset points',
                     fontsize=7.5, ha='center', color='#222',
                     arrowprops=dict(arrowstyle='->', lw=.7, color='#555'))
axes[1].annotate('127.8 Hz bump', xy=(127.8, yxyz[np.argmin(abs(fy-127.8))]),
                 xytext=(152, 2.5e5), fontsize=7.5, color='#222',
                 arrowprops=dict(arrowstyle='->', lw=.7, color='#555'))
axes[0].legend(loc='lower right', fontsize=7, framealpha=.9)
axes[0].set_ylim(30, 1.2e7)
fig.suptitle('VanderPrint-2 — resonance sweeps, 2026-09-25 (ADXL345, log PSD)', fontsize=11)
fig.tight_layout(rect=[0, 0, 1, .96])
fig.savefig(FIGS + 'fig1-spectra.png', dpi=150, bbox_inches='tight')
print('ok')
