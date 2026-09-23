# Hardware Reference for 17BM

This document describes all the hardware devices available for bluesky control, organized by subsystem. Each device has a Bluesky name (how you access it in Python/IPython) and SPEC mnemonics (the names used in SPEC macros).

For a complete mapping of all motor names, see `SPEC_to_Bluesky_Mapping.md`.

## Motor Stages

The instrument has multiple independent motor stages for positioning samples, detectors, and optical components.

### Sample Positioning Stage (`sam`)

Controls the sample position (XY translation) and rotation (about vertical Z axis).

| SPEC mnemonic | Bluesky name | EPICS PV  | Range (typical) | Purpose |
|---------------|--------------|-----------|-----------------|---------|
| samx          | sam.x        | 17bm:m10  | ±40 mm          | Sample X translation |
| samy          | sam.y        | 17bm:m11  | ±40 mm          | Sample Y translation |
| samr          | sam.r        | 17bm:m12  | 0-360°          | Sample rotation (φ) |

**Example use:**
```python
RE(bps.mv(sam.x, 5.0))              # Move X to 5 mm
RE(bps.mvr(sam.y, 0.5))             # Move Y relative, +0.5 mm
RE(bp.rel_scan([scaler1], sam.r, 0, 180, 91))  # Rotate and collect data
```

### Monochromator Control Stage (`nm`)

Controls the Si(111) monochromator crystals. All five motors work together to tune photon energy while maintaining beam position and polarization. These are typically coordinated via energy-change procedures.

| SPEC mnemonic | Bluesky name | EPICS PV  | Purpose |
|---------------|--------------|-----------|---------|
| nmtheta       | nm.theta     | 17bm:m44  | Crystal Bragg angle |
| nmtwist       | nm.twist     | 17bm:m45  | Crystal twist (polarization) |
| nmchi         | nm.chi       | 17bm:m46  | Crystal χ angle |
| nmpitch       | nm.pitch     | 17bm:m47  | Crystal pitch |
| nmbend        | nm.bend      | 17bm:m48  | Crystal bender |

**Example use:**
```python
RE(bps.mv(nm.theta, 10.5))          # Move Bragg angle
# Note: Real energy changes are coordinated via planned composite plans
```

### Beam Stop / Fluorescence Detector Stage (`bs`)

Controls the beam stop and fluorescence detector positioning.

| SPEC mnemonic | Bluesky name | EPICS PV  | Range | Purpose |
|---------------|--------------|-----------|-------|---------|
| bsx           | bs.x         | 17bm:m22  | ±50 mm | Beam stop X |
| bsy           | bs.y         | 17bm:m21  | ±50 mm | Beam stop Y |
| bsz           | bs.z         | 17bm:m24  | ±50 mm | Beam stop Z (height) |

**Example use:**
```python
RE(bps.mv(bs.x, 0, bs.y, 0))       # Center beam stop on beam
```

### Area Detector Stage (`det`)

Controls the position of the area detector (moved for different scattering geometries).

| SPEC mnemonic | Bluesky name | EPICS PV  | Range | Purpose |
|---------------|--------------|-----------|-------|---------|
| detx          | det.x        | 17bm:m23  | ±100 mm | Detector X translation |
| dety          | det.y        | 17bm:m6   | ±100 mm | Detector Y translation |
| detz          | det.z        | 17bm:m33  | 0-1000 mm | Detector distance (Z) |

**Example use:**
```python
RE(bps.mv(det.z, 500))              # Move detector to 500 mm distance
# Note: Metadata records this distance with each scan
```

### Photodiode Stage (`pin`)

Controls position of the I₀ ionization chamber and reference photodiode.

| SPEC mnemonic | Bluesky name | EPICS PV  | Purpose |
|---------------|--------------|-----------|---------|
| pinx          | pin.x        | 17bm:m17  | Photodiode X |
| piny          | pin.y        | 17bm:m18  | Photodiode Y |

**Example use:**
```python
RE(bps.mv(pin.x, 0))                # Center photodiode on beam
```

### Reference Sample Stage (`red`)

Controls positioning of reference/calibration samples.

| SPEC mnemonic | Bluesky name | EPICS PV  | Purpose |
|---------------|--------------|-----------|---------|
| redx          | red.x        | 17bm:m20  | Reference sample X |
| redy          | red.y        | 17bm:m16  | Reference sample Y |

**Example use:**
```python
RE(bps.mv(red.x, 0, red.y, 0))     # Move reference sample into position
```

### Monochromator Table (`monotab`)

A Monochromator table with five independent motors.

| SPEC mnemonic | Bluesky name | EPICS PV  | Purpose |
|---------------|--------------|-----------|---------|
| utabv         | monotab.utabv | 17bm:m41  | Upper table vertical |
| drtabv        | monotab.drtabv | 17bm:m42 | Down-right table vertical |
| dltabv        | monotab.dltabv | 17bm:m43 | Down-left table vertical |
| utabh         | monotab.utabh | 17bm:m49  | Upper table horizontal |
| dtabh         | monotab.dtabh | 17bm:m50  | Down table horizontal |

**Example use:**
```python
RE(bps.mv(monotab.utabv, 10))       # Move upper table vertically
# Note: Often used as a group (3 vertical motors move together)
```

## Slit Systems

The instrument has three independent 2D slit systems, each controlled by four blade motors and four calculated macro motors (gap and offset).

### Slit 1 (`slit1`)

High-resolution slit system at entrance of beamline.

**Blade motors:**
| SPEC mnemonic | Bluesky name | EPICS PV  | Purpose |
|---------------|--------------|-----------|---------|
| s1_top        | slit1.top    | 17bm:m27  | Top blade |
| s1_bot        | slit1.bottom | 17bm:m28  | Bottom blade |
| s1_in         | slit1.inboard | 17bm:m25 | Inboard blade (left) |
| s1_out        | slit1.outboard | 17bm:m26 | Outboard blade (right) |

**Macro motors (calculated):**
| SPEC mnemonic | Bluesky name | Formula | Purpose |
|---------------|--------------|---------|---------|
| s1_vgap       | slit1.vgap   | (top + bottom) / 2 | Vertical opening |
| s1_voff       | slit1.voff   | (top - bottom) / 2 | Vertical center offset |
| s1_hgap       | slit1.hgap   | (inboard + outboard) / 2 | Horizontal opening |
| s1_hoff       | slit1.hoff   | (inboard - outboard) / 2 | Horizontal center offset |

**Example use:**
```python
RE(bps.mv(slit1.vgap, 0.2))         # Set vertical opening to 0.2 mm
RE(bps.mv(slit1.hgap, 0.3))         # Set horizontal opening to 0.3 mm
# The underlying blade motors move automatically
```

### Slit 2 (`slit2`)

Secondary slit system in experimental hutch.

**Motors:** Same structure as `slit1` (top, bottom, inboard, outboard, vgap, voff, hgap, hoff)

| SPEC mnemonic prefix | Bluesky path | EPICS PV prefix |
|----------------------|--------------|-----------------|
| s2_*                 | slit2.*      | 17bm:m{29-32,37-40} |

### White Beam Slits (`slitWB`)

Full-aperture white beam slit system.

**Motors:** Same structure as `slit1` (top, bottom, inboard, outboard, vgap, voff, hgap, hoff)

| SPEC mnemonic prefix | Bluesky path | EPICS PV prefix |
|----------------------|--------------|-----------------|
| wb_*                 | slitWB.*     | 17bm:m{1-4,29-32} |

## Scaler / Detector

### Scaler 1 (`scaler1`)

Multi-channel scaler for counting detector signals. Provides synchronized counting of multiple signals.

**Channels:**

| SPEC mne | EPICS PV | Bluesky variable | Ophyd path | Physical detector |
|----------|----------|------------------|------------|-------------------|
| sec      | 17bm:scaler1.S1 | clock_pulses | scaler1.channels.chan01.s | Integration timer |
| i1       | 17bm:scaler1.S2 | i1 | scaler1.channels.chan02.s | Photodiode (PIN) |
| i0       | 17bm:scaler1.S3 | i0 | scaler1.channels.chan03.s | Ion chamber (incident flux) |
| bsd      | 17bm:scaler1.S4 | i2 | scaler1.channels.chan04.s | Beam stop diode |

**Four name representations explained:**

- **SPEC mnemonic** (e.g., `i0`): Short name used in SPEC macros. Established by beamline conventions.
- **EPICS PV** (e.g., `17bm:scaler1.S3`): Raw Process Variable in the IOC. Used for direct hardware access and debugging via medm screens.
- **Bluesky variable** (e.g., `i0`): Python name defined in startup.py for convenient access at the IPython prompt.
- **Ophyd path** (e.g., `scaler1.channels.chan03.s`): Device component path in the Python object hierarchy. Used in custom plans and advanced scripts.

All three names refer to the same physical detector channel (ion chamber in this example).

**Example use:**
```python
# Configure scaler to read only named channels
scaler1.select_channels()

# Count once with 0.5 second preset time
RE(bps.mv(scaler1.preset_time, 0.5))
RE(bp.count([scaler1]))

# Scan with scaler
RE(bp.rel_scan([scaler1], sam.x, 0, 10, 5))

# Access individual channel values (convenience names from startup.py)
i0_value = i0.get()              # Ion chamber
i1_value = i1.get()              # Photodiode
i2_value = i2.get()              # Beam stop
timer_value = clock_pulses.get() # Timer

# Or via low-level ophyd path
i0_value = scaler1.channels.chan03.s.get()
```

## [TODO] Temperature Control (PTC10)

**Status:** Awaiting PTC10 activation.

When integrated, this will provide:
- **Flowcell heater** - controlled via AIO channel 5A
- **Block furnace** - controlled via AIO channel 5B
- **Hot air blower** - controlled via RTD channel 3A
- **Temperature readback** - from thermocouple 2A

The device will be accessible as `ptc10` with sub-components:
- `ptc10.temperature.setpoint` - Set target temperature
- `ptc10.pid_5a.ramprate` - Set ramp rate
- `ptc10.inposition` - Check if at temperature
- `ptc10.tolerance` - Temperature tolerance for "at position" check

## [TODO] Cryostream

**Status:** Not yet integrated into Bluesky.

SPEC controls cryostream via `17bmCryo:BM:*` PVs. Future integration will expose:
- Temperature control
- Cooling rate
- Status monitoring

## Summary

For a complete authoritative mapping of all motors and their SPEC↔Bluesky names, see [SPEC_to_Bluesky_Mapping.md](./SPEC_to_Bluesky_Mapping.md).

For examples of how to use these devices in custom plans, see [getting-started-custom-plans.md](./getting-started-custom-plans.md).
