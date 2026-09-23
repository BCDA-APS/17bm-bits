# SPEC to Bluesky: Command Reference

If you know SPEC, you already understand 80% of Bluesky. The core concepts are the same—move motors, count detectors, control instruments. The main differences are syntax and the execution model.

## Key Differences

**SPEC:** Commands execute immediately; you wait for the beep.

**Bluesky:** Commands are wrapped in a "plan" (a Python generator) that the RunEngine executes. You must wrap commands in `RE(...)` to run them.

## Command Translation

### Motor Movement

```
SPEC: umv samx 10
      Move sample X to absolute position 10 mm

Bluesky: RE(bps.mv(sam.x, 10))
         Same thing, wrapped in RunEngine
```

```
SPEC: umvr samx 1
      Move sample X relative, +1 mm from current position

Bluesky: RE(bps.mvr(sam.x, 1))
         Same relative move syntax
```

```
SPEC: wa
      Show positions of all motors

Bluesky: %wa
         IPython magic command - same concept, same name
```

```
SPEC: wm samx
      Show position of one motor

Bluesky: sam.x.position
         Access the position attribute directly
```

### Multi-Motor Moves

```
SPEC: umv samx 10 samy 5
      Move two motors simultaneously

Bluesky: RE(bps.mv(sam.x, 10, sam.y, 5))
         Same, with explicit motor names
```

### Counting / Data Acquisition

```
SPEC: ct 1
      Count scaler for 1 second (count time is the argument)

Bluesky: RE(bp.count([scaler1]))
         Explicit list of detectors to read
         `preset_time` must be set first.
```

```
SPEC: tcount 5
      Count for 5 seconds

Bluesky: RE(bps.mv(scaler1.preset_time, 5))
         RE(bp.count([scaler1]))
         Set time explicitly, then count
```

### Scans

```
SPEC: dscan det scaler1 samx 0 10 5
      Motor scan: move samx from 0 to 10 (relative), 5 points, count at each

Bluesky: RE(bp.rel_scan([scaler1], sam.x, 0, 10, 5))
         Same concept, explicit device list
```

```
SPEC: a2scan motor1 1 10 motor2 2 20 5
      Two-motor scan (motors are stepped together)

Bluesky: RE(bp.scan([scaler1], sam.x, 1, 10, sam.y, 2, 20, 5))
         Two-motor scan (motors are stepped together)
```

### Waiting / Timing

```
SPEC: sleep 5
      Wait 5 seconds

Bluesky: RE(bps.sleep(5))
         Same concept
```

### Device Status

```
SPEC: show_counters
      List all configured counters/detectors

Bluesky: scaler1.select_channels()
         scaler1.read()
         Read configured scaler channels
```

```
SPEC: epics_get("PV_NAME")
      Read a raw EPICS PV

Bluesky: from ophyd import EpicsSignalRO
         sig = EpicsSignalRO("PV_NAME:rbv", name="mysignal")
         sig.wait_for_connection()  # to be safe
         sig.get()
```

## Concepts

### RunEngine (RE)

The RunEngine is Bluesky's control loop. Every command must be passed to it:

```python
# At prompt, you must wrap commands in RE()
RE(bps.mv(sam.x, 10))

# Inside a custom plan, you yield messages (no RE() wrapper)
def my_plan():
    yield from bps.mv(sam.x, 10)
    yield from bp.count([scaler1])
```

Why? Because the RunEngine:
- Coordinates device motion and data acquisition
- Records metadata (timestamps, hardware state)
- Handles errors gracefully
- Streams data to the data acquisition system

### Plan Stubs (bps)

Simple building blocks: `bps.mv()`, `bps.mvr()`, `bps.sleep()`, etc. They move one thing or do one simple action.

### Plans (bp)

Higher-level workflows: `bp.count()`, `bp.rel_scan()`, `bp.abs_scan()`, `bp.grid_scan()`, etc. They combine multiple stubs into coherent experiments.

### Devices (ophyd)

Hardware objects in Python. Each motor, scaler, detector is an ophyd Device:

```python
sam.x           # Sample X motor (EpicsMotor)
sam.x.position  # Current position
scaler1         # Scaler detector (ScalerCH)
scaler1.channels.chan01.s  # Timer channel
```

## Debugging & Common Errors

### `ConnectionError: "PV <name> not found"`

**Cause:** EPICS IOC is not running, or PV name is wrong.

**Fix:**
1. Check that the IOC is running: `ssh ioc-host` and check the process
2. Verify the PV name with `caget` from command line
3. Check `devices.yml` for correct PV prefix

### `TimeoutError: Motor did not move`

**Cause:** Motor is disabled, at limit, or communication is stuck.

**Fix:**
1. Check motor enable status: `device.report()` shows all details
2. Check limits: `motor.low_limit.get()`, `motor.high_limit.get()`
3. Try a small move first: `RE(bps.mvr(device, 0.01))`
4. Check EPICS medm screens for hardware status

### `AttributeError: 'device' has no attribute 'x'`

**Cause:** Device name is wrong or doesn't have that sub-device.

**Fix:**
1. List all devices: `listobjects()`
2. List components of a device: `motor_stage.component_names`
3. Check device spelling and capitalization

### Data looks wrong

**Cause:** Scaler channels not configured correctly.

**Fix:**
```python
scaler1.select_channels()  # Configure which channels to read
RE(bp.count([scaler1]))    # Count again
```

## Getting Help

### In-Session Help

```python
bps.mv?               # Quick help (IPython magic, no SPEC equivalent)
bps.mv??              # Full source code (equivalent to SPEC's prdef)
help(bps.mv)          # Show documentation for bps.mv
help(bp.rel_scan)     # Show documentation for bp.rel_scan
listplans()           # List all plans in global namespace
listplans(bp)         # List all standard Bluesky plans (similar to SPEC's lsdef)
listplans(bps)        # List all Bluesky plan stubs
listobjects()         # List all available devices
device.report()       # Show detailed status of a device
%wa                   # Show positions of all motors
```

### Online Resources

- Bluesky documentation: https://blueskyproject.io/
- Ophyd documentation: https://blueskyproject.io/ophyd/
- This repo's documentation: See [devices.md](./devices.md), [getting-started-custom-plans.md](./getting-started-custom-plans.md)

## Next Steps

1. Try the commands in the "Command Translation" section at the IPython prompt
2. Refer to [devices.md](./devices.md) for the complete list of available motors and detectors
3. See [getting-started-custom-plans.md](./getting-started-custom-plans.md) to learn how to write your own experiment workflows
