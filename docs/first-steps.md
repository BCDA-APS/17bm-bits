# Your first session

Start a bluesky session for 17BM:

```bash
conda activate 17bm-bits
ipython -i -c "from bm17.startup import *"
```

This should start with no errors. Next, confirm you got the devices you expected:

```bash
listobjects()
```

You should see the motors, scaler, and slits configured in the device configuration file.

In addition to the simulation devices (`sim_motor` and `sim_det`), you can expect to see:
- **Motor stages:** `sam`, `nm`, `bs`, `det`, `pin`, `red`, `monotab`
- **Slits:** `slit1`, `slit2`, `slitWB`
- **Scaler:** `scaler1`

Assuming success, you can ask for the current values of all devices using `%wa` (Where All). For any motor or positioner, you can check the current position using its `.position` attribute, such as `sam.x.position`. For ophyd signals that are not positioners (like scaler channels), use the more generic `.get()` method, such as `scaler1.channels.chan01.s.get()`.

## Moving Motors

Moving a motor (or other ophyd movable) can be done with either the `bps.mv()` or `bps.mvr()` plan stubs and the `RE` (RunEngine). Here's a relative move example of 0.1 in the motor's engineering units:

```bash
RE(bps.mvr(sam.x, 0.1))
# ... shows progress bar until move completes
# Now, put it back
RE(bps.mvr(sam.x, -0.1))
```

You can move more than one thing at a time:

```bash
RE(bps.mvr(sam.x, 0.1, sam.y, 0.2))
```

To move to an absolute position:

```bash
RE(bps.mv(sam.x, 5.0))
```

## Using the Scaler

Exercise the scaler by first setting the count time (in seconds), then configuring it to read only the named EPICS channels, and finally counting once:

```bash
RE(bps.mv(scaler1.preset_time, 0.5))
scaler1.select_channels()
RE(bp.count([scaler1]))
```

The scaler has these channels (named in startup.py):
- `clock_pulses` - Integration timer (corresponds to SPEC `sec`)
- `i1` - Photodiode signal
- `i0` - Ion chamber (beam flux)
- `i2` - Beam stop diode (SPEC `bsd` becomes `i2` in Bluesky)

## Scanning

Try a relative scan: move the sample X motor from 0 to 10 mm in 5 steps, collecting scaler data at each point:

```bash
RE(bp.rel_scan([scaler1], sam.x, 0, 10, 5))
```

This should acquire 5 data points. For an absolute scan (moving to specific absolute positions):

```bash
RE(bp.abs_scan([scaler1], sam.x, 0, 10, 5))
```

For a scan at specific motor positions:

```bash
RE(bp.list_scan([scaler1], sam.x, [0, 2.5, 5.0, 7.5, 10.0]))
```

## Next Steps

Now that you're familiar with basic operations, check out:
- [`spec-to-bluesky.md`](./spec-to-bluesky.md) - Compare SPEC commands with Bluesky equivalents
- [`devices.md`](./devices.md) - Full reference of available hardware
- [`getting-started-custom-plans.md`](./getting-started-custom-plans.md) - How to write your own experiment workflows
