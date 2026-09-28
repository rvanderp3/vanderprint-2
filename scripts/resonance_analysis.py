#!/usr/bin/env python3
"""VanderPrint-2 resonance analysis, Sept 25 2026 sweeps.
Peak finding, Q estimation, background/coupling analysis.
"""
import numpy as np, json, sys

import os
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data") + os.sep
FIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures") + os.sep

def load(name):
    d = np.genfromtxt(DATA + name, delimiter=',', names=True)
    return d['freq'], d['psd_x'], d['psd_y'], d['psd_z'], d['psd_xyz']

def robust_baseline(f, p):
    """rolling 5th percentile over 30Hz windows = incoherent background"""
    base = np.zeros_like(p)
    for i in range(len(f)):
        lo = np.searchsorted(f, f[i]-15); hi = np.searchsorted(f, f[i]+15)
        base[i] = np.percentile(p[lo:hi], 10)
    return np.maximum(base, 1.0)

def find_peaks(f, p, prominence_ratio=0.05):
    """local maxima on log psd above background, prominence vs global max."""
    b = robust_baseline(f, p)
    lp = np.log10(p + 1.0)
    lb = np.log10(b + 1.0)
    peaks = []
    for i in range(2, len(f)-2):
        if lp[i] > lp[i-1] and lp[i] >= lp[i+1] and (p[i] > prominence_ratio*p.max()):
            # above baseline by > 3dB
            if lp[i] - lb[i] > 0.5:
                if not peaks or f[i] - peaks[-1][0] > 4.0:
                    peaks.append((f[i], p[i]))
                elif p[i] > peaks[-1][1]:
                    peaks[-1] = (f[i], p[i])
    return peaks, b

def peak_q(f, p, fpk, base):
    """Q = f / (-6dB bandwidth of resonance above local background)."""
    b = np.interp(f, f, base)
    above = p - b
    if above.max() <= 0: return None, None
    half = above.max() / 2.0
    i = np.argmin(np.abs(f - fpk))
    # find crossings left/right of peak
    left = right = None
    for j in range(i, 0, -1):
        if above[j] < half:
            # linear interp
            t = (half - above[j]) / (above[j+1] - above[j] + 1e-12)
            left = f[j] + t*(f[j+1]-f[j]); break
    for j in range(i, len(f)):
        if above[j] < half:
            t = (half - above[j]) / (above[j-1] - above[j] + 1e-12)
            right = f[j] - t*(f[j]-f[j-1]); break
    if left is None or right is None: return None, None
    bw = right - left
    return (fpk/bw if bw > 0 else None), (left, right)

report = {}
for axis, fname in [('X', 'x-resonance-sept25.csv'), ('Y', 'y-resonance-sept25.csv')]:
    f, px, py, pz, pxyz = load(fname)
    # excited axis signal: for X sweep it's psd_x, for Y sweep psd_y
    sig = px if axis == 'X' else py
    cross = py if axis == 'X' else px
    peaks, base = find_peaks(f, pxyz)
    out = {'file': fname, 'peaks': [], 'noise_floor_hz_range': [float(f.min()), float(f.max())]}
    for fpk, amp in peaks:
        q, bw = peak_q(f, pxyz, fpk, base)
        # amplitude ratio vs base at peak
        b = np.interp(fpk, f, base)
        snr_db = 10*np.log10(amp/b) if b > 0 else None
        # cross-axis coupling at this freq
        ci = np.argmin(np.abs(f - fpk))
        out['peaks'].append({'freq_hz': float(fpk), 'psd': float(amp),
                             'q': float(q) if q else None,
                             'snr_db': float(snr_db) if snr_db else None,
                             'cross_axis_psd': float(cross[ci])})
    # global stats
    out['max_psd'] = float(pxyz.max())
    out['max_freq'] = float(f[np.argmax(pxyz)])
    out['median_psd'] = float(np.median(pxyz))
    out['z_peak_hz'] = float(f[np.argmax(pz)]); out['z_peak_psd'] = float(pz.max())
    report[axis] = out

print(json.dumps(report, indent=1))
