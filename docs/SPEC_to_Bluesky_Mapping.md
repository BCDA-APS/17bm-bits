# SPEC to Bluesky Name Mapping

This is the authoritative reference mapping all SPEC motor mnemonics and detector names to their Bluesky device names and EPICS PV identifiers.

**Generated from:**
- SPEC beamline configuration
- Bluesky instrument device definitions

## Understanding the Three Names

Every hardware component in 17BM has three identifiers. Understanding them helps with debugging and troubleshooting:

### Name Layer 1: SPEC Mnemonic

**What it is:** The short name used in SPEC macros and at the SPEC command prompt.

**Example:** `samx`, `i0`, `s1_vgap`

**Purpose:** Human convenience. SPEC mnemonics are brief, memorable abbreviations chosen by beamline scientists.

**Where you see it:** SPEC macro code, SPEC console commands, printed output from SPEC.

### Name Layer 2: EPICS PV (Process Variable)

**What it is:** The raw identifier in the EPICS control system. The base address of the hardware on the network.

**Example:** `17bm:m10`, `17bm:scaler1.S3`, `17bmSoft:tc1:5A:setPoint`

**Purpose:** Direct hardware access. Used by all control software, including low-level IOC code and medm screens.

**Where you see it:** EPICS medm screens, IOC output, raw network diagnostics, error messages about missing PVs.

**Syntax:** `<IOC_name>:<device_name>:<field_name>`

### Name Layer 3: Bluesky Dotted Name

**What it is:** The Python object path to access the device in Bluesky/IPython.

**Example:** `sam.x`, `scaler1.channels.chan03.s`, `slit1.vgap`

**Purpose:** Python/Bluesky integration. How you reference hardware in custom plans and at the IPython prompt.

**Where you see it:** Your Python code, Bluesky plans, IPython commands, error messages about missing attributes.

**Syntax:** `<device>.<component>.<subcomponent>` (dot-separated path)

### Concrete Example: Same Physical Detector, Different Names

The ion chamber signal:

| Layer | Name | Context |
|-------|------|---------|
| SPEC mnemonic | `i0` | Type at SPEC prompt: `ct 1` counts both i0 and other signals |
| EPICS PV | `17bm:scaler1.S3` | Use in medm screen or `caget 17bm:scaler1.S3` |
| Bluesky path | `scaler1.channels.chan03.s` | In IPython: `val = scaler1.channels.chan03.s.get()` |
| Bluesky shortcut | `i0` | `i0.get()`

All refer to **exactly the same physical detector** (the ion chamber). They're just different ways to address it from different layers of the control system.

## Motor Mapping

All motors in the instrument, organized by stage group.

### Sample Positioning Stage

| SPEC mne | Bluesky (dotted) | EPICS PV | Motor ID | Purpose |
|----------|------------------|----------|----------|---------|
| samx | sam.x | 17bm:m10 | m10 | Sample X translation |
| samy | sam.y | 17bm:m11 | m11 | Sample Y translation |
| samr | sam.r | 17bm:m12 | m12 | Sample rotation (φ) |

### Monochromator Stage

| SPEC mne | Bluesky (dotted) | EPICS PV | Motor ID | Purpose |
|----------|------------------|----------|----------|---------|
| nmtheta | nm.theta | 17bm:m44 | m44 | Crystal Bragg angle |
| nmtwist | nm.twist | 17bm:m45 | m45 | Crystal twist |
| nmchi | nm.chi | 17bm:m46 | m46 | Crystal χ angle |
| nmpitch | nm.pitch | 17bm:m47 | m47 | Crystal pitch |
| nmbend | nm.bend | 17bm:m48 | m48 | Crystal bender |

### Beam Stop Stage

| SPEC mne | Bluesky (dotted) | EPICS PV | Motor ID | Purpose |
|----------|------------------|----------|----------|---------|
| bsx | bs.x | 17bm:m22 | m22 | Beam stop X |
| bsy | bs.y | 17bm:m21 | m21 | Beam stop Y |
| bsz | bs.z | 17bm:m24 | m24 | Beam stop Z |

### Area Detector Stage

| SPEC mne | Bluesky (dotted) | EPICS PV | Motor ID | Purpose |
|----------|------------------|----------|----------|---------|
| detx | det.x | 17bm:m23 | m23 | Detector X |
| dety | det.y | 17bm:m6 | m6 | Detector Y |
| detz | det.z | 17bm:m33 | m33 | Detector distance (Z) |

### Photodiode Stage

| SPEC mne | Bluesky (dotted) | EPICS PV | Motor ID | Purpose |
|----------|------------------|----------|----------|---------|
| pinx | pin.x | 17bm:m17 | m17 | Photodiode X |
| piny | pin.y | 17bm:m18 | m18 | Photodiode Y |

### Red Sample Stage

| SPEC mne | Bluesky (dotted) | EPICS PV | Motor ID | Purpose |
|----------|------------------|----------|----------|---------|
| redx | red.x | 17bm:m20 | m20 | Reference sample X |
| redy | red.y | 17bm:m16 | m16 | Reference sample Y |

### Monochromator Table

| SPEC mne | Bluesky (dotted) | EPICS PV | Motor ID | Purpose |
|----------|------------------|----------|----------|---------|
| utabv | monotab.utabv | 17bm:m41 | m41 | Upper table vertical |
| drtabv | monotab.drtabv | 17bm:m42 | m42 | Down-right table vertical |
| dltabv | monotab.dltabv | 17bm:m43 | m43 | Down-left table vertical |
| utabh | monotab.utabh | 17bm:m49 | m49 | Upper table horizontal |
| dtabh | monotab.dtabh | 17bm:m50 | m50 | Down table horizontal |

### Slit 1 Blades

| SPEC mne | Bluesky (dotted) | EPICS PV | Motor ID | Purpose |
|----------|------------------|----------|----------|---------|
| s1_top | slit1.top | 17bm:m27 | m27 | Top blade |
| s1_bot | slit1.bottom | 17bm:m28 | m28 | Bottom blade |
| s1_in | slit1.inboard | 17bm:m25 | m25 | Inboard blade |
| s1_out | slit1.outboard | 17bm:m26 | m26 | Outboard blade |

### Slit 1 Macro Motors

In SPEC, these motors are calculated in macros.  In Bluesky, these motors are calculated in EPICS, in the IOC.

| SPEC mne | Bluesky (dotted) | Formula | Purpose |
|----------|------------------|---------|---------|
| s1_vgap | slit1.vgap | (top + bottom) / 2 | Vertical opening |
| s1_voff | slit1.voff | (top - bottom) / 2 | Vertical center |
| s1_hgap | slit1.hgap | (inboard + outboard) / 2 | Horizontal opening |
| s1_hoff | slit1.hoff | (inboard - outboard) / 2 | Horizontal center |

### Slit 2 Blades

| SPEC mne | Bluesky (dotted) | EPICS PV | Motor ID | Purpose |
|----------|------------------|----------|----------|---------|
| s2_top | slit2.top | 17bm:m31 | m31 | Top blade |
| s2_bot | slit2.bottom | 17bm:m32 | m32 | Bottom blade |
| s2_in | slit2.inboard | 17bm:m29 | m29 | Inboard blade |
| s2_out | slit2.outboard | 17bm:m30 | m30 | Outboard blade |

### Slit 2 Macro Motors

| SPEC mne | Bluesky (dotted) | Formula | Purpose |
|----------|------------------|---------|---------|
| s2_vgap | slit2.vgap | (top + bottom) / 2 | Vertical opening |
| s2_voff | slit2.voff | (top - bottom) / 2 | Vertical center |
| s2_hgap | slit2.hgap | (inboard + outboard) / 2 | Horizontal opening |
| s2_hoff | slit2.hoff | (inboard - outboard) / 2 | Horizontal center |

### White Beam Slits

| SPEC mne | Bluesky (dotted) | EPICS PV | Motor ID | Purpose |
|----------|------------------|----------|----------|---------|
| wb_top | slitWB.top | 17bm:m1 | m1 | Top blade |
| wb_bot | slitWB.bottom | 17bm:m2 | m2 | Bottom blade |
| wb_in | slitWB.inboard | 17bm:m3 | m3 | Inboard blade |
| wb_out | slitWB.outboard | 17bm:m4 | m4 | Outboard blade |

## Detector / Scaler Mapping

### Scaler 1 Channels

| SPEC mne | EPICS PV | Bluesky variable | Ophyd path | Physical detector |
|----------|----------|------------------|------------|-------------------|
| sec | 17bm:scaler1.S1 | clock_pulses | scaler1.channels.chan01.s | Integration timer |
| i1 | 17bm:scaler1.S2 | i1 | scaler1.channels.chan02.s | Photodiode (I₁) |
| i0 | 17bm:scaler1.S3 | i0 | scaler1.channels.chan03.s | Incident flux (I₀) |
| bsd | 17bm:scaler1.S4 | i2 | scaler1.channels.chan04.s | Transmitted flux (I₂) |

**Explanation of the four names:**
- **SPEC mnemonic** (sec, i1, i0, bsd): Short names used in SPEC macros. Human-readable, established by beamline conventions.
- **EPICS PV suffix** (.S1, .S2, .S3, .S4): Raw Process Variable identifiers. Used in IOC databases and medm screens for direct hardware access.
- **Bluesky variable** (clock_pulses, i1, i0, i2): Python names defined in startup.py for convenient IPython prompt access.
- **Ophyd path** (scaler1.channels.chan01.s, etc.): Device component path in the Python object hierarchy. Used in custom plans and advanced scripts.

## [TODO] Temperature Control (PTC10)

**Status:** Awaiting PTC10 activation into Bluesky.

When integrated, the mapping will be:

| SPEC control | EPICS PV prefix | Bluesky path | Device |
|--------------|-----------------|--------------|--------|
| `ptc10` commands | `17bmSoft:tc1:` | `ptc10.*` | PTC10 controller |
| `heater_1()` | `17bmSoft:tc1:5C:` | `ptc10.pid_5c.voltage` | Hot air blower voltage |
| `heater_2()` | `17bmSoft:tc1:2A:temperature` | `ptc10.readback` | Flowcell temperature |
| `flow_ramp()` | `17bmSoft:tc1:5A:` | `ptc10.pid_5a.*` | Flowcell AIO/PID |
| `bk_ramp()` | `17bmSoft:tc1:5B:` | `ptc10.pid_5b.*` | Block furnace AIO/PID |
| `hotair_ramp()` | `17bmSoft:tc1:3A:` | `ptc10.rtd_3a.*` | Hot air blower RTD |

## [TODO] Cryostream

**Status:** Not yet integrated into Bluesky.

## How to Use This Reference

### Finding a motor name

1. **You know the SPEC mnemonic** (e.g., `samx`):
   - Look in the tables above for that mnemonic
   - Find the **Bluesky (dotted)** column: `sam.x`
   - Use that name in your IPython commands

2. **You know the EPICS PV** (e.g., from a medm screen):
   - Look for that PV in the **EPICS PV** column
   - Find the **Bluesky (dotted)** column
   - Use that name in your Bluesky plans

3. **You know the Bluesky name** and need SPEC equivalent:
   - Look for the Bluesky path in the tables
   - Find the **SPEC mne** column
   - Use that name in SPEC macros (if running SPEC)

### Debugging with EPICS

If you see an error message about a PV:

```
ConnectionError: failed to connect to 17bm:m10
```

1. Look up `17bm:m10` in the tables → it's `sam.x`
2. Try moving it in Bluesky: `RE(bps.mv(sam.x, 5))`
3. Or test the PV directly: `caget 17bm:m10`

### Understanding a SPEC macro

If you see SPEC code like:

```spec
def my_macro '{
    umv samx 10
    umv slit1_vgap 0.2
    ct 1
}
```

Map to Bluesky:
- `samx` → `sam.x`
- `slit1_vgap` → `slit1.vgap`
- `ct 1` → `RE(bp.count([scaler1]))`

Becomes:
```python
def my_plan():
    yield from bps.mv(sam.x, 10)
    yield from bps.mv(slit1.vgap, 0.2)
    yield from bp.count([scaler1])
```

## Quick Reference: Most Common Motors

For quick reference, here are the most frequently used motors:

| What | SPEC | Bluesky |
|------|------|---------|
| Move sample X | `umv samx 10` | `RE(bps.mv(sam.x, 10))` |
| Rotate sample | `umv samr 45` | `RE(bps.mv(sam.r, 45))` |
| Open slit 1 | `umv s1_vgap 0.2` | `RE(bps.mv(slit1.vgap, 0.2))` |
| Move detector | `umv detz 500` | `RE(bps.mv(det.z, 500))` |
| Count | `ct 1` | `RE(bp.count([scaler1]))` |
| Scan | `rel_scan det scaler1 samx 0 10 5` | `RE(bp.rel_scan([scaler1], sam.x, 0, 10, 5))` |
