# Getting Started with Custom Plans

This guide teaches you how to write your own experiment workflows in Bluesky. You'll learn by doing, starting simple and building toward the kinds of complex multi-step procedures you're familiar with from SPEC macros.

## What is a Plan?

In Bluesky, a **plan** is a Python function that describes an experiment. Instead of executing immediately, plans generate a sequence of "messages" that the RunEngine interprets and executes.

**SPEC way:**
```spec
def my_macro() {
    umv samx 10
    ct 1
    umv samx 20
    ct 1
}
```

**Bluesky way:**
```python
def my_plan():
    yield from bps.mv(sam.x, 10)
    yield from bps.mv(scaler1.preset_time, 1)
    yield from bp.count([scaler1])
    yield from bps.mv(sam.x, 20)
    yield from bp.count([scaler1])
```

The `yield from` syntax tells Python: "execute this plan step and wait for it to finish."

## Plan Stubs: The Building Blocks

**Plan stubs** (`bps.*`) can be simple, single-action building blocks or higher-level composites built from smaller blocks. (Plans collect data, plan *stubs* do not.)  Here are the most common ones:

### Hardware Control

```python
from bluesky import plan_stubs as bps

# Move a motor to absolute position
yield from bps.mv(sam.x, 10)

# Move a motor relative to current position
yield from bps.mvr(sam.x, 1)

# Move multiple motors simultaneously
yield from bps.mv(sam.x, 10, sam.y, 5)

# Set a PV (like preset_time on scaler)
yield from bps.mv(scaler1.preset_time, 0.5)

# Wait (no action, just delay)
yield from bps.sleep(5)  # Wait 5 seconds
```

### Data Acquisition

```python
# Trigger a detector (take one reading)
yield from bps.trigger(scaler1)

# Read a device (get its current value)
yield from bps.read(sam.x)

# Read multiple devices
yield from bps.read(sam.x, sam.y, scaler1)
```

## Pre-Built Plans: Higher Level Workflows

**Plans** (`bp.*`) are higher-level, pre-built workflows that combine stubs into common patterns:

```python
from bluesky import plans as bp

# Count scaler once
yield from bp.count([scaler1])

# Count N times
yield from bp.count([scaler1], num=5)

# Relative scan: move motor, count at each point
yield from bp.rel_scan([scaler1], sam.x, 0, 10, 5)
# Moves sam.x from 0 to 10 mm (relative), 5 points

# Absolute scan
yield from bp.abs_scan([scaler1], sam.x, 0, 10, 5)

# List scan: count at specific motor positions
yield from bp.list_scan([scaler1], sam.x, [0, 2.5, 5.0, 7.5, 10.0])

# Grid scan: 2D Cartesian scan
yield from bp.grid_scan(
    [scaler1],
    sam.x, 0, 10, 5,  # 5 points in X
    sam.y, 0, 20, 3   # 3 points in Y
)
```

## Running a Plan

Once you've written a plan, execute it with the RunEngine:

```python
# At IPython prompt
RE(my_plan())

# With arguments
RE(my_plan(start_pos=5, end_pos=15, num_points=10))
```

## Example 1: Simple Position Scan

**Goal:** Move sample X to three positions and count at each.

```python
def position_scan():
    """Count scaler at three sample X positions."""
    positions = [0, 5, 10]
    for pos in positions:
        yield from bps.mv(sam.x, pos)
        yield from bp.count([scaler1])
```

**Run it:**
```python
RE(position_scan())
```

**Equivalent SPEC macro:**
```spec
def position_scan '{
    umv samx 0
    ct 1
    umv samx 5
    ct 1
    umv samx 10
    ct 1
}
```

## Example 2: Parameterized Scan

**Goal:** Make the positions and count time configurable.

```python
def position_scan_param(positions, count_time):
    """Count scaler at specified positions with given preset time.
    
    Parameters
    ----------
    positions : list
        Motor positions (mm)
    count_time : float
        Scaler preset time (seconds)
    """
    yield from bps.mv(scaler1.preset_time, count_time)
    
    for pos in positions:
        yield from bps.mv(sam.x, pos)
        yield from bp.count([scaler1])
```

**Run it:**
```python
RE(position_scan_param([0, 5, 10], count_time=0.5))
```

## Example 3: Multi-Motor Scan with Condition Check

**Goal:** Scan sample X, but skip any points where the photodiode signal is too low.

```python
def guarded_scan(start, stop, num_points, min_signal=100):
    """Scan with signal threshold check at each point.
    
    Parameters
    ----------
    start, stop : float
        Motor range (mm)
    num_points : int
        Number of points
    min_signal : float
        Minimum acceptable photodiode signal (counts)
    """
    yield from bps.mv(scaler1.preset_time, 1.0)
    
    positions = np.linspace(start, stop, num_points)
    
    for pos in positions:
        yield from bps.mv(sam.x, pos)
        yield from bp.count([scaler1])
        
        # Check the signal (i1 is photodiode)
        data = db[-1]  # Last scan result
        i1_value = data.table()['scaler1_channels_chan02_s'].iloc[-1]
        
        if i1_value < min_signal:
            print(f"Warning: Signal too low ({i1_value}) at position {pos}")
```

**Run it:**
```python
RE(guarded_scan(0, 10, 5, min_signal=200))
```

## Example 4: Nested Loops (2D Scan)

**Goal:** Scan two motors in a grid pattern.

**Option A: Using pre-built grid_scan (recommended)**
```python
def my_2d_scan():
    """Use pre-built grid scan."""
    yield from bp.grid_scan(
        [scaler1],
        sam.x, 0, 10, 5,    # 5 points X
        sam.y, 0, 20, 3     # 3 points Y
    )

RE(my_2d_scan())
```

**Option B: Custom nested loops (if you need fine control)**
```python
def custom_2d_scan(x_range, y_range, x_points, y_points):
    """Custom 2D scan with explicit loop structure.
    
    Like SPEC a2scan but with explicit control.
    """
    x_positions = np.linspace(x_range[0], x_range[1], x_points)
    y_positions = np.linspace(y_range[0], y_range[1], y_points)
    
    yield from bps.mv(scaler1.preset_time, 0.5)
    
    for x in x_positions:
        for y in y_positions:
            yield from bps.mv(sam.x, x, sam.y, y)
            yield from bp.count([scaler1])

RE(custom_2d_scan((0, 10), (0, 20), 5, 3))
```

## Common Patterns

### Pattern: Waiting for a Condition

```python
def wait_for_condition_example():
    """Wait until a motor reaches position (alternative to relying on done signal)."""
    yield from bps.mv(sam.x, 10)
    
    # Wait for position to settle
    timeout = 10  # seconds
    start_time = time.time()
    while True:
        current_pos = sam.x.position
        if abs(current_pos - 10) < 0.01:  # Within 0.01 mm
            break
        if time.time() - start_time > timeout:
            raise TimeoutError("Motor did not reach position in time")
        yield from bps.sleep(0.1)
```

### Pattern: Conditional Branching

```python
def conditional_scan(temperature_setpoint):
    """Branch based on a condition."""
    yield from bps.mv(scaler1.preset_time, 1.0)
    
    # Read current ion chamber signal
    yield from bps.read(scaler1)
    
    if scaler1.channels.chan03.s.get() > 500:
        # Good signal: do detailed scan
        yield from bp.rel_scan([scaler1], sam.x, 0, 10, 21)
    else:
        # Poor signal: skip
        print("Signal too low, skipping scan")
```

### Pattern: Early Exit from Loop

```python
def scan_until_signal_drops():
    """Scan and stop when signal drops below threshold."""
    yield from bps.mv(scaler1.preset_time, 0.5)
    
    threshold = 200
    positions = np.linspace(0, 50, 100)
    
    for pos in positions:
        yield from bps.mv(sam.x, pos)
        yield from bp.count([scaler1])
        
        # Check ion chamber
        signal = scaler1.channels.chan03.s.get()
        
        if signal < threshold:
            print(f"Signal dropped at position {pos}, stopping scan")
            break
```

## Accessing Data Within a Plan

After a count or scan, you can access the collected data:

```python
def scan_with_inline_analysis():
    """Access data immediately after collection."""
    yield from bp.rel_scan([scaler1], sam.x, 0, 10, 5)
    
    # Get the last completed scan
    scan_uid = RE.run_engine.run_engine.run_start['uid']
    data = db[scan_uid]  # Load from DataBroker
    
    # Extract values
    table = data.table()
    x_values = table['sam_x']
    i0_values = table['scaler1_channels_chan03_s']
    
    # Compute something
    transmission = i0_values.max() / i0_values.min()
    print(f"Transmission ratio: {transmission}")
```

## Putting Your Plan in a File

For reusable plans, save them in the plans directory:

```bash
# Create a file in the plans directory: my_custom_plans.py
cat > my_custom_plans.py << 'EOF'
"""Custom experiment plans for 17BM."""

from bluesky import plan_stubs as bps
from bluesky import plans as bp
import numpy as np

def my_position_scan(positions, count_time=1.0):
    """Scan to specified positions."""
    yield from bps.mv(scaler1.preset_time, count_time)
    for pos in positions:
        yield from bps.mv(sam.x, pos)
        yield from bp.count([scaler1])

def my_2d_scan(x_range, y_range, x_points, y_points):
    """2D grid scan."""
    yield from bp.grid_scan(
        [scaler1],
        sam.x, x_range[0], x_range[1], x_points,
        sam.y, y_range[0], y_range[1], y_points
    )
EOF
```

Then import in IPython:

```python
from bm17.plans.my_custom_plans import my_position_scan, my_2d_scan

RE(my_position_scan([0, 5, 10]))
```

## Next Steps

1. **Try the examples** - Run each example at the IPython prompt
2. **Modify them** - Change parameters, add motors, add conditions
3. **Read the reference** - See [spec-to-bluesky.md](./spec-to-bluesky.md) for more plan stubs and plans
4. **Reference the hardware** - Check [devices.md](./devices.md) for available motors and detectors
5. **Advanced tutorials** - Once comfortable, explore the Bluesky documentation: https://blueskyproject.io/

## Troubleshooting

### Plan doesn't run / syntax error

**Check:** Python syntax is correct. Plans are just Python functions.

```python
# Wrong: forgetting yield from
def bad_plan():
    bps.mv(sam.x, 10)  # Missing 'yield from'

# Right: use yield from for all plan stubs/plans
def good_plan():
    yield from bps.mv(sam.x, 10)
```

### Motor doesn't move / no error

**Check:** You wrapped the plan in RE()?

```python
# Wrong: just calling the plan function
my_plan()  # Creates generator, doesn't execute

# Right: pass to RunEngine
RE(my_plan())
```

### Data not showing up

**Check:** Did you yield from `bp.count()` or similar data collection?

```python
# Wrong: no data collected
def bad_plan():
    yield from bps.mv(sam.x, 10)
    # Missing count or scan!

# Right: collect data
def good_plan():
    yield from bps.mv(sam.x, 10)
    yield from bp.count([scaler1])
```

## See Also

- [spec-to-bluesky.md](./spec-to-bluesky.md) - Command mapping reference
- [devices.md](./devices.md) - Available hardware (motors, detectors)
- Bluesky docs: https://blueskyproject.io/
