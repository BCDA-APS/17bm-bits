# Your first session

NOTE: These instructions were adapted from a neighboring beamline.  Your motors, scaler, and other devices will be named differently.

```bash
conda activate 17bm-bits
ipython -i -c "from bm17.startup import *"
```

This should start with no errors.  Next, confirm you got the devices you expected:

```bash
listobjects()
```

In addition to sim_motor and sim_det, you should see any other devices you configured in `src/bm17/configs/device.yml`.

Assuming success, you can ask for the current values of them all using `wh()`.  If you just want to see the current position of any motor, you can use it's `.position` attribute, such as `sample.x.position`.  For ophyd signals that are not positioners (ophyd objects that do not have a `.position` property), then you can use the more generic `.get()` method, such as `thermocouple.get()`.

Moving a motor (or other ophyd movable), can be done with either the `bps.mv()` or `bps.mvr()` plan stubs and the `RE` (RunEngine).  Here, I show a relative move example of 0.1 in the motors engineering units:

```bash
RE(bps.mvr(sample.x, 0.1))
# ... for long moves, shows a progress bar until move completes
# Now, put it back
RE(bps.mvr(sample.x, -0.1))
```

You can move more than one thing at a time:

```bash
RE(bps.mvr(sample.x, 0.1, sample.y, 0.2))
```

Next, exercise the scaler.  First, set the count time, say 1/2 second, configure the scaler object for only the named EPICS channels,, then count once:

```bash
RE(bps.mv(scaler1.preset_time, 0.5))
scaler1.select_channels()
RE(bp.count([scaler1]))
```

Next, try a scaler v. motor (relative) scan.  For kicks, also report temperature at each point:

```bash
RE(bp.rel_scan([scaler1, thermocouple], sample.x, 0, 0.1, 5))
```

Should get 5 points.
