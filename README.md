# vanderprint-2

Documentation and calibration data for **VP-2**, a 600×600 mm fixed-top CoreXY 3D printer (BTT Octopus, Klipper, Hermit Crab V2 CAN toolhead).

## Reports

- **[Resonance report — Sept 25, 2026](reports/resonance-report-sept25.md)** — ADXL345 X/Y resonance sweeps, input-shaper fits (Klipper `calibrate_shaper.py` + independent peak/Q analysis), baseline history, CoreXY class comparison, recommended motion settings. Includes a Sept 26 addendum after an X/Y motor upgrade + belt retension, and a travel-speed stall discovery (24 V NEMA 17 torque cliff at 500 mm/s).
- **[Vibration triage plan — Sept 26, 2026](reports/vibration-triage-plan-sept26.md)** — systematic triage of a ~200 Hz toolhead buzz at 250 mm/s travel. Root cause confirmed: StealthChop current-control instability at high sustained step rate; fixed via `stealthchop_threshold`.

## Repository layout

| Path | Contents |
|---|---|
| `reports/` | Markdown reports (linked figures use relative paths) |
| `figures/` | Analysis figures and Klipper shaper-fit charts |
| `data/` | PSD resonance sweep CSVs (0–202 Hz, ~1.5 Hz bins) |
| `scripts/` | Analysis/figure scripts (run against `data/` and write to `figures/`) |

## Data files

| File | Description |
|---|---|
| `x-resonance-sept25.csv`, `y-resonance-sept25.csv` | Sept 25 sweeps (pre motor upgrade) |
| `x-resonance-sept25-evening.csv`, `y-resonance-sept25-evening.csv` | Duplicate Sept 25 evening runs |
| `x-resonance-sept26.csv`, `y-resonance-sept26.csv` | Sept 26 sweeps (post motor upgrade, belts at 47 Hz pluck) |

Columns: `freq, psd_x, psd_y, psd_z, psd_xyz` (power spectral density from Klipper `TEST_RESONANCES`).

## Current shaper config

```ini
[input_shaper]
shaper_type_x: mzv
shaper_freq_x: 71.2
shaper_type_y: ei
shaper_freq_y: 46.2
```

## Reproducing the analysis

```bash
pip install numpy matplotlib
python scripts/resonance_analysis.py   # peak/Q JSON
python scripts/fig1b.py                # spectra figure
python scripts/fig2b.py                # CoreXY class overlay
python scripts/fig3.py                 # baseline timeline
```

License: Apache-2.0.
