# VP-2 Toolhead Vibration Triage Plan — 2026-09-26

**Symptom:** Audible vibration from the toolhead when running at 250 mm/s. Phone tuner reads ~200 Hz (±, coarse estimate). Mostly X, has also appeared on Y.

**Constraints:** Printer is running a job now. No printer interrogation until owner says clear.

## Governing physics

A **steady tone during constant-velocity cruise** cannot come from the input shaper or motion-profile excitation (Klipper commands near-zero force modulation while cruising). It must be periodic in distance or time: tooth engagement, rotating parts, fans, driver chopping, melt flow.

Vibration that **starts/stops with accel events and decays** is a different family: structural resonance ringing (shaper/mount/belt modes).

So the first branch to resolve is: **tonal-while-cruising vs bursty-at-corners**, and whether the pitch **tracks speed**.

## Machine facts already in hand (Sept 26)

- Active `[input_shaper]`: X mzv@71.2, Y ei@46.2 — **BUT** the `#*# SAVE_CONFIG` block at the bottom of printer.cfg still carries `shaper_freq_x = 28.8`, `shaper_type_y = 2hump_ei @ 39.0`. In Klipper the `#*#` block merges last and **wins**, so the *effective* shapers may still be the stale pre-rebuild ones → 66.8/73.1 Hz X doublet completely un-nulled. Verify before anything else when clear:
  `curl -s localhost:7050/printer/objects/query?input_shaper`
- `[printer]`: max_velocity 250 (at the ceiling — no headroom), SCV raised to **8** (doubles corner impulse vs SCV 4 — 250 mm/s corners inject big broadband energy), accel 3900, minimum_cruise_ratio 0.25.
- Known X modes: doublet 67.1/73.1, **new motor-mount peak 104.4 Hz Q 5.8**, belt-path bump 132.8 Hz (moved up after retension).
- Known Y modes: dominant 43.3 (tilt-coupled), remnant 37.3, belt bump 129.8.
- Sweeps top out at 201.4 Hz — **~200 Hz is the very edge of the measured band; we're partially blind there.**
- StealthChop is forced on **all** steppers (`stealthchop_threshold: 999999` on X, Y, Zs, extruder).
- At 250 mm/s on 2 mm GT2: belt tooth-pass = **125 Hz** (harmonics 250, 375). Full-step rate 1562 Hz, microstep rate 25 kHz (ultrasonic). A tuner app reports one dominant pitch of a complex tone — "200" could be tooth-pass + harmonics confused, a subharmonic/beat, or genuinely ~200.

## Phase 0 — observation only, while the job runs (answers from the room)

1. Is it a **steady tone during long straight cruises**, or **bursts on corners/accels** that decay?
2. Is it audible on **pure travel moves** (no extrusion) at the same speed, or only while extruding?
3. When it runs slower sections (100–150 mm/s walls, first layer) — is the pitch lower, absent, or the same?
4. Does changing `SPEED_FACTOR` (Mainsail slider) shift the pitch **proportionally**?
5. Is the volume position-dependent (louder at one end of the gantry)? → harness/wire routing.
6. Swap the phone tool: a tuner gives one number. **Spectroid** (free, live spectrogram) shows the true frequency and any harmonic comb — do this from the couch, zero printer interaction.

## Decision tree from Phase 0

| Observation | Mechanism family | Next step |
|---|---|---|
| Pitch ∝ speed, ~125 Hz at 250 (comb at 125/250/375) | **Belt/pulley tooth-pass** — engagement defect, worn belt section, pulley wobble, low tension | Phase 2 slope test + belt hardware inspection |
| Pitch ∝ speed but ≠ tooth-pass slope (other periodicity: harness slap, idler bearing ball-figures) | Rotating/passing component | Phase 2 + manual spin check of idlers/pulleys |
| Pitch **constant** regardless of speed, present at standstill when motors held | **StealthChop whine / driver current-waveform** | Phase 3 driver toggle test |
| Only during extrusion moves, ∝ feed rate | **Melt-flow buzz / nozzle chatter** (0.6 mm @ 250 = high flow) | Phase 3 travel-vs-extrude test |
| Bursts on corners, decaying chirp at ~67/73 or ~104 | **Resonance ringing** — stale-shaper bug and/or SCV 8 | Phase 1 shaper fix + sweep |
| Constant drone independent of motion | Fan blade-pass (heat-break controller_fan, part-fan, chassis fan) | Phase 3 fan isolation |

**Slope arithmetic for the speed sweep:** f = v / d where d is the spatial period. GT2 tooth-pass → d = 2 mm → 62.5 Hz per 100 mm/s. Measure f at 100/150/200/250, fit a line, invert the slope to read d directly. That single number names the mechanism.

## When the printer is clear

### Phase 1 — remove the confounds (5 min)
1. `QUERY` effective shapers via Moonraker. If stale (28.8 / 2hump_ei@39): `SET_INPUT_SHAPER SHAPER_TYPE_X=mzv SHAPER_FREQ_X=71.2 SHAPER_TYPE_Y=ei SHAPER_FREQ_Y=46.2`, re-verify, then `SAVE_CONFIG` once to purge the stale `#*#` block. Note: this may change the sound by itself.
2. `MEASURE_AXES_NOISE` (fans off, then on) — contamination baseline.

### Phase 2 — characterize the tone (the tight feedback loop)
Macro `TONE_TEST` (below): straight X cruises at a set speed, optional matched extrusion, so Klipper runs the *real* current/shaper path — better than `FORCE_MOVE`.
- Speed ladder: **80, 120, 160, 200, 250 mm/s** (each ×3 passes), record Spectroid screenshots.
- Repeat the winning speed on Y.
- Log to a table: speed vs measured Hz → compute period d = v/f.
- Compare against 2 mm (tooth-pass) vs ~1.25 mm vs non-integer (bearing defect).

### Phase 3 — falsify hypotheses one variable at a time (one per run!)
1. **Driver whine:** `SET_TMC_FIELD STEPPER=stepper_x FIELD=stealthchop_threshold VALUE=0` (forces spreadCycle) — rerun worst-case speed. Tone gone → chopper; tune chop settings / hysteresis, or keep spreadCycle above a sane threshold.
2. **Extrusion:** TONE_TEST with and without `EXTRUDE=1` at same speed → separates melt-flow buzz.
3. **Fans:** `SET_FAN_SPEED FAN=heat_break_fan SPEED=0` (briefly, watch temps) and part-fan off → blade-pass check.
4. **Shaper sensitivity:** `SET_INPUT_SHAPER SHAPER_TYPE_X=none` vs `mzv@71.2` at 250 — if the sound is shaper-sensitive it was ringing, not tonal.
5. **SCV:** `SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=4` — if corner bursts drop, the SCV 8 impulse was the driver.

### Phase 4 — hands-on inspection (power off, belt family)
- Pluck both A/B belts: expect ~47 Hz, matched within ±3 Hz (low/unequal tension → tooth-pass tone).
- Grab each pulley + both idler bearings: zero radial wobble, no notchy feel. Loose eccentric pulley is the classic speed-tracking buzz.
- Motor mount bolts (the 104.4 Hz peak is already whispering about this), motor heatsinks, wire loom clearance across full X travel.
- Belt tooth wear/glossy patches over full travel span; clean both sides.
- Extruder grip: idler bearing, tension screw (a chattering gear can sound ~200 Hz).

### Phase 5 — extended measurement (ADXL blind-spot fix)
Sweeps stop at ~201 Hz. Re-run `TEST_RESONANCES AXIS=X INPUT_SHAPER=none FREQ_RANGE=120-200` with finer `SMOOTHING=0.05` to resolve the top band; a real ~200 Hz structural mode would show there and re-rank everything. (`output=excel` if you want the raw table beside the CSVs.)

## Macro (add to Klipper config when clear — I'll apply it via the tool then)

```ini
[gcode_macro TONE_TEST]
gcode:
  {% set v = params.SPEED|default(250)|float %}
  {% set ax = params.AXIS|default('X') %}
  {% set ext = params.EXTRUDE|default(0)|int %}
  {% set f = (v * 60)|int %}
  SAVE_GCODE_STATE NAME=tone_test
  M83
  G90
  G1 Z20 F600
  {% if ax == 'X' %}
    G1 X50 Y275 F6000
    {% if ext %}
      ; line section 0.42w x 0.2h -> 0.084 mm^2 -> 10.44 mm filament per 300 mm, speed-independent
      G1 X350 Y275 E10.44 F{f}
      G1 X50  Y275 E10.44 F{f}
    {% else %}
      G1 X350 Y275 F{f}
      G1 X50  Y275 F{f}
    {% endif %}
  {% else %}
    G1 X275 Y50 F6000
    {% if ext %}
      G1 X275 Y350 E10.44 F{f}
      G1 X275 Y50  E10.44 F{f}
    {% else %}
      G1 X275 Y350 F{f}
      G1 X275 Y50  F{f}
    {% endif %}
  {% endif %}
  RESTORE_GCODE_STATE NAME=tone_test
```

Run as: `TONE_TEST SPEED=250 EXTRUDE=1`, `TONE_TEST SPEED=150`, `TONE_TEST AXIS=Y SPEED=250 EXTRUDE=1`.

## VERDICT (Sept 26, ~15:40) — ROOT CAUSE CONFIRMED: StealthChop at high sustained step rate

**Decisive test result:** with `stealthchop_threshold: 0` (spreadCycle) on X/Y, the ~195 Hz travel buzz is **gone**. Printer idle, homing verified working (the earlier homing failure was the owner's test with `homing_speed: 20` — StallGuard needs sufficient velocity to register a stall; 20 mm/s was too slow to produce a stall signature, unrelated to the chopper change).

**Mechanism, for the record:** at 250 mm/s the X/Y motors step at ~25 kHz (rotation_distance 32 → 100 steps/mm × 250). StealthChop's amplitude-modulated current controller (pwm_freq ≈ 1 → ~1 kHz update) cannot regulate current pulse-by-pulse once the step rate approaches/passes its update rate; current error ripples → ~200 Hz torque buzz, harmonics (2×375, 3×540, 4×741 seen in the audio), slow swell as the cruise lengthens, drifting pitch — everything the spectrogram showed. SpreadCycle (fast decay chopper) tracks step rate directly and stays clean. Extrusion-matched print moves are damped by filament drag and rarely sustain max step rate long enough; travels do. The Sept-26 15:16 sweeps had already flagged the machine as acoustically healthy — the "200 Hz vibration" was never structural at all.

**Why sensorless homing still works** (Klipper tmc.py `handle_homing_move_begin`): on StallGuard4 drivers (2209) Klipper *forces StealthChop on during every homing move* (tpwmthrs=0, en_spreadcycle=0) and restores the configured mode afterward — regardless of the config threshold. So `stealthchop_threshold: 0` + `driver_SGTHRS` homing is a supported combination, not a coincidence.

**Refinement to consider:** threshold 0 = spreadCycle everywhere → audible "stepping growl" returns at low speeds (first layer, z_tilt probing). Hybrid option keeps both: `stealthchop_threshold: 80–120` (StealthChop below, spreadCycle above; buzz only lived above ~200). Validate with the same TONE_TEST travel.

**Final config state (current):** X/Y/extruder `stealthchop_threshold: 0`; Z steppers commented (→ default); shaper body mzv@71.2/ei@46.2 active. ⚠️ Still to do: verify the stale `#*#` SAVE_CONFIG shaper block (28.8/2hump_ei@39) was purged — effective shapers via Moonraker `/printer/objects/query?input_shaper` returned empty, worth re-checking after a SAVE_CONFIG.

**Lesson for next time:** tune-app "vibration frequency" + audio spectrum beats shaper assumptions; the buzz lived at 195 Hz *outside* every structural mode of the machine.



**Audio facts:** fundamental 188–201 Hz drifting ~10 Hz (rough buzz, not pure tone), harmonics 2×375.7, 3×~540–565, 4×~741–787; NO strong 125 Hz tooth-pass fundamental; onset is a ~0.45 s swell during cruise (too slow for resonance ringing ~0.1 s; melt-fill time fits exactly); sidebands ~6.6 Hz apart.

**Owner observation:** buzz only on TRAVEL at 250 mm/s, observed on both X and Y, does NOT correlate with extrusion.

**Config facts noticed:** `max_travel_velocity: 250` and `max_travel_accel: 2000` are COMMENTED OUT in [printer] — and Klipper core has no travel-specific caps anyway — so travels currently run at the full print envelope: 250 mm/s sustained cruise with 3900 mm/s² accel/decel + SCV 8 corners, no extrusion drag damping the system.

**Re-ranking:**
1. ~~Melt-flow buzz~~ — DEAD: no extrusion during travel.
2. **Driver/current instability at max sustained step rate** — X and Y both have `stealthchop_threshold: 999999` (forced quiet-mode at ALL speeds). Travels are the only moves that sustain the max step rate long enough for a steady tone. StealthChop current control degrades as step rate approaches the chopper domain; travels are also undamped (no filament drag). Explains: both axes (identical driver config), travel-only, swell onset, buzz-with-harmonics, drifting pitch, fixed ~195 Hz. **FALSIFIER: `SET_TMC_FIELD STEPPER=stepper_x FIELD=stealthchop_threshold VALUE=0` → rerun travel.** (Ties old #2, now #1.)
3. **Belt/idler common-mode mechanism** — CoreXY: *every* travel (X or Y) drives both belts, both motors, both idlers — so "both axes" is naturally explained by the shared belt path (not an axis-specific structural mode). Candidates: slack-side belt flutter/singing at 250 mm/s (600 mm spans), notchy idler bearing, eccentric-pulley slip. **FALSIFIER: speed ladder — tooth-pass/flutter pitch ∝ speed (would slide from ~195→~78 Hz across 80–250); StealthChop tone behavior differs.** Also hand-test: press slack belt span during a slow travel.
4. **Resonance family (stale #*# shapers + SCV 8)** — downgraded again: ringing decays after corners; this swells *during* cruise. But travels at 250/3900 do hammer the 67/73 doublet, and the stale SAVE_CONFIG block is a real bug regardless → still purge it first.
5. ~~Belt tooth-pass at 125 Hz~~ — missing 125 line in spectrum; keep only as a variant of #3.
6. ~~Fans~~ — fans run during printing too; travel-only kills this.

**Revised experiment order when clear (each step one variable):**
1. SET_INPUT_SHAPER correct values + SAVE_CONFIG (config hygiene; note any change in sound).
2. TONE_TEST SPEED=250 AXIS=X (travel, EXTRUDE=0) → reproduce. Confirm same for AXIS=Y.
3. **StealthChop toggle on X** → rerun travel. Gone = chopper; then either sane threshold (e.g. 0/3 → spreadCycle above idle) or retune chop settings. This is the cheapest decisive test — do it before anything physical.
4. If chopper test negative → **speed ladder** 250/200/160/120/80, note pitch slide vs fixed (distance-periodic vs time-periodic).
5. If pitch ∝ speed → belt path: pluck/inspect idlers, damp slack span during travel.
6. Extended sweep FREQ_RANGE=120-200 (INPUT_SHAPER=none) for the band-top blind spot; also compare travel at accel 3900 vs SET_VELOCITY_LIMIT MAX_ACCEL=2000 to quantify what the restored travel limits would buy.
7. Consider re-enabling a travel governor properly — Klipper has no max_travel_* keys; the proven approach is slicer-side travel speed (Orca → 200) or a SET_VELOCITY_LIMIT wrapper on travel macros.

## Original hypotheses (pre-observation, superseded — kept for history)


1. **Belt/pulley tooth-pass + harmonic**, riding on a marginal tension/pulley condition — f ∝ v, same family on both axes (matches "X mostly, Y sometimes", same belt physics). 125 Hz fundamental explains "200" as a misread complex tone.
2. **StealthChop whine** (threshold 999999 = always-quiet-mode on both steppers) — speed-correlated, axis-selective by how the frame radiates; trivially falsifiable in Phase 3.1.
3. **Resonance burst misheard as a tone** — stale `#*#` shapers (28.8/39!) un-notch X's 67–73 doublet and Y's 43.3 tilt mode while SCV 8 at 250 mm/s hammers corners. Even if it isn't the vibration, this bug deserves fixing anyway.
4. Motor-mount 104.4 Hz ringing (accel-coupled only; second harmonic 209 is suspiciously close to "200").
5. Melt-flow buzz at 0.6 mm/250 flow.
6. Fan blade-pass.

**Success criterion:** a table of speed vs frequency with a fitted spatial period d = v/f that either equals 2 mm (tooth-pass) or points at a specific named component, and a Phase-3 toggle that makes the tone disappear. Fix follows root cause, not before.
