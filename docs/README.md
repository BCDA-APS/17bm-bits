# 17BM Bluesky Documentation

Welcome! This documentation is organized following the [Diataxis framework](https://diataxis.fr/) — four modes of documentation that serve different needs.

## Getting Started

**New to Bluesky?** Start here:

1. **[Your first session](first-steps.md)** (Tutorial)
   - Basic commands and device operations
   - How to move motors, count detectors, run scans
   - Verify your setup is working

2. **[SPEC to Bluesky reference](spec-to-bluesky.md)** (How-To Guide)
   - Side-by-side comparison of SPEC and Bluesky commands
   - For users migrating from SPEC
   - Quick lookup of syntax equivalents

## Learning the System

**Want to understand the bigger picture?**

3. **[System architecture](architecture.md)** (Explanation)
   - Why Bluesky is organized this way
   - How data flows from user commands to hardware
   - Concepts: RunEngine, Ophyd devices, EPICS IOC
   - Suitable for understanding design decisions

## Reference Documentation

**Looking for specific information?**

4. **[Hardware devices](devices.md)** (Reference)
   - Complete catalog of available motors, slits, detectors
   - Motor ranges, EPICS PVs, usage examples
   - Organized by subsystem (sample stage, monochromator, slits, etc.)

5. **[Name mapping reference](SPEC_to_Bluesky_Mapping.md)** (Reference)
   - Authoritative mapping of all device names
   - Three representations: SPEC mnemonic → EPICS PV → Bluesky path
   - Use this when debugging or converting SPEC macros

## Writing Custom Experiments

**Ready to write your own plans?**

6. **[Getting started with custom plans](getting-started-custom-plans.md)** (Tutorial)
   - Learn plan writing by example
   - Plan stubs (basic building blocks)
   - Pre-built plans (ready-to-use workflows)
   - Six complete code examples from simple to advanced

## Documentation Organization

### By Purpose (Diataxis)

| Mode | Purpose | Documents |
|------|---------|-----------|
| **Tutorials** | Hands-on learning, step-by-step | first-steps.md, getting-started-custom-plans.md |
| **How-To Guides** | Goal-oriented, "how do I do X?" | spec-to-bluesky.md |
| **Reference** | Lookup, technical specs | devices.md, SPEC_to_Bluesky_Mapping.md |
| **Explanation** | Conceptual understanding, "why?" | architecture.md |

### By Audience

| You are... | Start here |
|-----------|-----------|
| New to Bluesky | [first-steps.md](first-steps.md) |
| Coming from SPEC | [spec-to-bluesky.md](spec-to-bluesky.md) |
| Want to write custom plans | [getting-started-custom-plans.md](getting-started-custom-plans.md) |
| Need hardware details | [devices.md](devices.md) |
| Looking up a device name | [SPEC_to_Bluesky_Mapping.md](SPEC_to_Bluesky_Mapping.md) |
| Understanding system design | [architecture.md](architecture.md) |

## Common Tasks

### Start a Bluesky session

See: [first-steps.md](first-steps.md#your-first-session)

```bash
conda activate 17bm-bits
ipython -i -c "from bm17.startup import *"
```

### Move a motor

See: [spec-to-bluesky.md](spec-to-bluesky.md#motor-movement)

```python
RE(bps.mv(sam.x, 10))              # Absolute move
RE(bps.mvr(sam.x, 1))              # Relative move
```

### Run a scan

See: [first-steps.md](first-steps.md#scanning)

```python
RE(bp.rel_scan([scaler1], sam.x, 0, 10, 5))    # 5 points, 0-10 mm
```

### Find a device name

See: [SPEC_to_Bluesky_Mapping.md](SPEC_to_Bluesky_Mapping.md#how-to-use-this-reference)

Example: SPEC mnemonic `samx` → Bluesky name `sam.x` → EPICS PV `17bm:m10`

### Write a custom plan

See: [getting-started-custom-plans.md](getting-started-custom-plans.md)

```python
def my_scan(positions):
    yield from bps.mv(scaler1.preset_time, 0.5)
    for pos in positions:
        yield from bps.mv(sam.x, pos)
        yield from bp.count([scaler1])

RE(my_scan([0, 5, 10]))
```

### Understand device architecture

See: [architecture.md](architecture.md)

Topics: RunEngine, Ophyd devices, EPICS, data flow, configuration

## Device Status

### Available Devices

✅ **Fully available:**
- Sample stage (sam): X, Y, rotation
- Detector stage (det): X, Y, distance
- Monochromator (nm): theta, twist, chi, pitch, bend
- Monochromator table (monotab): 5 motors
- Beam stop (bs): X, Y, Z
- Slits: slit1, slit2, slitWB (with gap/offset)
- Photodiode (pin): X, Y
- Reference sample (red): X, Y
- Scaler (scaler1): 4 channels (timer, i1, i0, bsd)

🔄 **Planned / In Development:**
- Temperature control (ptc10): Awaiting activation
- Cryostream: Not yet integrated
- PE15HE remote detector: Not yet integrated
- Raman camera: Not yet integrated

See: [devices.md](devices.md) for details

## Tips

### Getting Help In-Session

```python
bps.mv?                   # Quick help on a function
bps.mv??                  # Full help with source code
help(bps.mv)              # Documentation for a plan stub
help(bp.rel_scan)         # Documentation for a plan
listobjects()             # List all available devices
listdevice(sam)           # List all parts of the `sam` device
listplans()               # List all plans in global namespace (somewhat similar to SPEC's `lsdef`)
listplans(bp)             # List all available plans in `bp` (bluesky.plans, bluesky standard plans)
listplans(bps)            # List all available plans in `bps` (bluesky.plan_stubs)
sam.summary()             # Detailed status of the `sam` device
%wa                       # Show all motor positions
```

The `?` and `??` magic commands are quick ways to get help:
- `?` shows the docstring and call signature (IPython-specific, no direct SPEC equivalent)
- `??` shows the docstring and source code (equivalent to SPEC's `prdef`)

### Debugging

If you see an error about a missing PV:

1. Check device spelling: `listobjects()` shows all available devices
2. Verify device configuration: See [devices.md](devices.md)
3. Check name mapping: See [SPEC_to_Bluesky_Mapping.md](SPEC_to_Bluesky_Mapping.md)
4. Test the EPICS PV directly: `caget 17bm:m10` from a terminal
5. Check if `sam` device is connected with EPICS: `sam.connected`
6. If not connected, repeat step 5 with each of its components.  A list of component names: `sam.component_names`

### When Things Don't Work

See [spec-to-bluesky.md — Debugging & Common Errors](spec-to-bluesky.md#debugging--common-errors)

## External Resources

- **Bluesky project:** https://blueskyproject.io/
- **Ophyd (device layer):** https://blueskyproject.io/ophyd/
- **apstools (APS-specific devices and plans)**: https://bcda-aps.github.io/apstools/latest/
- **EPICS:** https://epics.anl.gov/

## Contributing to These Docs

Found an error? Want to improve the documentation?

- Report issues at: https://github.com/BCDA-APS/17bm-bits/issues
- Documentation follows [Diataxis framework](https://diataxis.fr/)
- Device names are the source of truth from `devices.yml`
- File system paths should NOT be in repository docs (use `.nogit_*` working files instead)
- See `.config/opencode/AGENTS.md` for detailed documentation guidance

## Summary

**Navigation Guide:**

- 📖 **Learning:** first-steps.md → architecture.md
- 🔄 **Converting from SPEC:** spec-to-bluesky.md → SPEC_to_Bluesky_Mapping.md
- 🛠️ **Building experiments:** getting-started-custom-plans.md
- 📚 **Looking things up:** devices.md, SPEC_to_Bluesky_Mapping.md
- 🤔 **Understanding design:** architecture.md

Choose your starting point above, or browse all documents in this directory.
