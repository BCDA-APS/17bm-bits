# 17BM Bluesky Architecture

This document explains the overall architecture of the 17BM Bluesky instrument—what the pieces are, how they fit together, and why they're organized this way.

## Context: From SPEC to Bluesky

### SPEC Era (Legacy)

For many years, 17BM was controlled by **SPEC**, a command-line control system designed for diffraction (and other) instruments. SPEC's model:

- **Interactive console** - Type commands, they execute immediately
- **Macros** - Scripts stored in text files, define multi-step procedures
- **Device mnemonics** - Short names for hardware (samx, s1_vgap, i0)
- **Direct motor control** - `umv motor position` moves immediately
- **Simple detectors** - Counters (SPEC calls them "counters"), collect counts

SPEC works well for straightforward control, but has limitations:
- Difficulty with complex conditional logic
- Difficulty with devices that acquire multi-dimensional data
- Hard to parallelize operations
- Metadata management is manual (printf logging)
- Limited data analysis integration
- Macro language is custom

### Bluesky Era (Current)

**Bluesky** is a modern control framework from Brookhaven National Lab, designed for synchrotron automation:

- **Plan-based** - Describe experiments as reusable plans written in Python, then run them
- **Metadata-aware** - Automatically captures hardware state, timestamps
- **Data integration** - Seamless connection to data storage and analysis
- **Composable** - Build complex workflows from simple building blocks
- **Reproducible** - Plans can be saved, shared, analyzed

The trade-off: slightly more setup and learning curve, but much more powerful.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  User Interface Layer                                           │
│  IPython + Jupyter Notebooks                                    │
│  (Type commands, write custom plans)                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ RE(plan)
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  Bluesky RunEngine Layer                                         │
│  - Interprets plans (generators)                                │
│  - Coordinates hardware execution                               │
│  - Records metadata (timestamps, UIDs, hardware state)          │
│  - Publishes events to subscribers                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
         ┌─────────┐  ┌─────────┐  ┌──────────┐
         │ Ophyd   │  │ Data    │  │ Metadata │
         │ Devices │  │ Broker  │  │ Store    │
         └────┬────┘  └────┬────┘  └──────────┘
              │             │
              │ read/write  │ store/retrieve
              ↓             ↓
         ┌─────────────────────────────────────┐
         │  Hardware Control Layer             │
         │  EPICS IOC (Experimental Physics    │
         │  and Industrial Control System)     │
         └────────────────────────────────────┘
              ↓
         Real Hardware (motors, detectors, slits)
```

## Layer 1: User Interface (Bluesky)

Users interact with Bluesky through:

1. **IPython console** - Interactive commands
   ```python
   RE(bps.mv(sam.x, 10))
   ```

2. **Custom plan files** - Saved Python scripts
   ```python
   # In the plans directory: my_experiment.py
   def my_scan(...):
       yield from ...
   ```

3. **Jupyter notebooks** - Interactive analysis and control

4. **QueueServer** (optional) - Queue-based experiment submission

**Philosophy:** Plans are first-class objects. Everything is reproducible and versionable.

## Layer 2: RunEngine (Bluesky Core)

The **RunEngine** is Bluesky's control loop. It:

1. **Interprets plans** - Converts generator functions into hardware commands
2. **Orchestrates execution** - Moves motors, triggers detectors, waits for responses
3. **Records metadata** - Timestamps every action, hardware state snapshots
4. **Publishes events** - Notifies subscribers (data aggregators, live plots, analysis)

**Key concept:** Plans are generators (lazy evaluation). They don't execute until passed to RE():

```python
my_plan()          # Creates generator, nothing happens
RE(my_plan())      # RunEngine executes it, hardware moves
```

Why generators? They allow:
- Pausing/resuming experiments
- Conditional logic (check result, then decide next step)
- Integration with analysis (feedback loops)

## Layer 3: Ophyd Devices

**Ophyd** ("Oph-yid") is the hardware abstraction layer. It maps Python objects to EPICS PVs.

### Device Hierarchy

Each device is a tree of components:

```python
sam                   # SampleStage device
  ├── x              # EpicsMotor (17bm:m10)
  ├── y              # EpicsMotor (17bm:m11)
  └── r              # EpicsMotor (17bm:m12)

slit1                # Optics2Slit2D_HV device
  ├── top            # EpicsMotor (blade)
  ├── bottom         # EpicsMotor (blade)
  ├── inboard        # EpicsMotor (blade)
  ├── outboard       # EpicsMotor (blade)
  ├── vgap           # Calculated (macro motor)
  ├── voff           # Calculated (macro motor)
  ├── hgap           # Calculated (macro motor)
  └── hoff           # Calculated (macro motor)

scaler1              # ScalerCH device
  └── channels
       ├── chan01    # Timer
       ├── chan02    # Photodiode (i1)
       ├── chan03    # Ion chamber (i0)
       └── chan04    # Beam stop (bsd)
```

### How Ophyd Works in Bluesky Plans

When you move a motor in a Bluesky plan:

```python
yield from bps.mv(sam.x, 10)
```

Ophyd:
1. Knows that `sam.x` is an `EpicsMotor` with EPICS PV `17bm:m10`
2. Connects to the IOC via network socket
3. Sends a setpoint command to the PV
4. Polls the motor's "done" status
5. Returns control when motion is complete

### Device Configuration

Devices are defined in the device configuration file:

```yaml
apstools.devices.motor_factory.mb_creator:
- name: sam
  class_name: SampleStage
  labels: ["baseline"]
  prefix: "17bm:"
  motors:
    x: m10
    y: m11
    r: m12
```

This YAML tells Bluesky:
- Create a device called `sam` (SampleStage class)
- It has motors x, y, r
- Each motor is at `17bm:m<N>`
- This device should be in the "baseline" stream (collected *before* the scan starts and also *after* the scan end)

## Layer 4: EPICS (Hardware Control)

**EPICS** is the real-time control system talking directly to hardware.

### IOC: The Gateway to Hardware

The **Input/Output Controller (IOC)** is a dedicated computer running EPICS software:

- Runs on a separate machine (typically `ioc-17bm`)
- Manages all hardware connections (RS-232, Ethernet, analog cards)
- Provides **PVs** (Process Variables) - network-addressable hardware channels
- Handles real-time constraints (motor ramping, synchronization)

### PVs: The Hardware Interface

Every controllable thing in 17BM is a PV:

```
17bm:m10        → Sample X motor position
17bm:m10.RBV    → Sample X readback
17bm:m10.VELO   → Sample X velocity
17bm:scaler1.S1 → Scaler timer
17bm:scaler1.S3 → Ion chamber counts
```

**Etymology:** "17bm:" is the IOC prefix, "m10" is the part that says motor 10. Together, they make the PV name: `17bm:m10`

EPICS handles the low-level communication:
- Converts network commands to hardware signals
- Polls hardware status
- Provides alarm handling
- Manages configuration

## Data Flow

### A Complete Measurement Cycle

```
User types: RE(bp.rel_scan([scaler1], sam.x, 0, 10, 5))
                ↓
RunEngine interprets the plan
                ↓
For each of 5 points:
  ├─ Move sam.x to position (0, 2.5, 5.0, 7.5, 10.0)
  │   └─ Ophyd sends EPICS command → IOC → Motor moves
  │       └─ Motor reaches position, Ophyd reads 17bm:m10.RBV
  │
  ├─ Count scaler1 (detector readout)
  │   └─ Ophyd triggers 17bm:scaler1.S1, S2, S3, S4
  │       └─ IOC accumulates counts, returns values
  │
  ├─ RunEngine collects data
  │   ├─ Motor position: sam.x = 2.5
  │   ├─ Detector counts: i0, i1, bsd
  │   └─ Metadata: timestamp, motor_id, detector_id
  │
  └─ Store in DataBroker
       └─ Creates HDF5 file with full experiment record
                ↓
Data available for analysis, export, archival
```

## Device Organization in 17BM

### Motor Stages

Each stage is a group of motors working together:

- **Sample stage (`sam`)** - 3D positioning (X, Y, rotation)
- **Detector stage (`det`)** - 3D positioning (X, Y, distance)
- **Monochromator (`nm`)** - 5 coordinated motors for energy tuning
- **Monochromator table (`monotab`)** - Supports the Monochromator (5 motors)
- **Slits (`slit1`, `slit2`, `slitWB`)** - 4 blade motors + 4 calculated macro motors each
- **Beam stop (`bs`)** - Fluorescence detector positioning

Each stage is **independent** - you can move any stage without affecting others (except for coordinated operations like energy changes).

### Scalers and Detectors

- **scaler1** - Multi-channel counter (4 channels: timer, i1, i0, bsd)
- **PE15HE detector** (planned) - Remote control of photon emission detector
- **Raman camera** (planned) - Spectroscopy detector

### Temperature Control (Planned)

- **ptc10** - PTC10 programmable temperature controller
  - Flowcell heater (AIO channel 5A)
  - Block furnace (AIO channel 5B)
  - Hot air blower (RTD channel 3A)

## Why This Architecture?

### Separation of Concerns

- **User plans** (Python) - What to do
- **Bluesky** (RunEngine) - How to coordinate it
- **Ophyd** (devices) - How to talk to hardware
- **EPICS** (IOC) - How to control hardware

Each layer can be updated independently without affecting others.

### Reproducibility

- Plans are code, not menu clicks
- Plans can be version-controlled (git)
- Metadata is automatic (timestamps, UIDs, hardware state)
- Experiments are reproducible on other machines/times

### Flexibility

- Custom plans can use any combination of devices
- Conditional logic (check data, adjust next step)
- Integration with analysis (feedback loops)
- Easy to add new hardware (just configure ophyd device)

## Configuration Files

The 17BM instrument is configured by a few key files:

### Device Configuration File

Defines all hardware devices:
- Motors (stages, slits)
- Detectors (scaler)
- Signals (readbacks, setpoints)
- Labels (which devices are "baseline")

**Who edits this:** Beamline scientist, when adding/removing hardware.

### Startup Script

Initialization code:
- Imports devices from `devices.yml`
- Sets up metadata structure
- Configures data storage
- Loads standard plans

**Who edits this:** Developers, rarely needed.

### Custom Plan Files

Custom experiment plans:
- Multi-step procedures
- Energy scans
- Temperature studies
- Sample alignment routines

**Who edits this:** Beamline users, as they develop new experiments.

## Typical Workflow

```
1. User writes a custom plan:
   
   # In the plans directory: my_experiment.py
   def temperature_scan(start_temp, end_temp, num_points):
       yield from ... (plan code)
   
2. Load the plan in IPython:
   
   from bm17.plans.my_experiment import temperature_scan
   
3. Execute the plan:
   
   RE(temperature_scan(20, 100, 10))
   
4. Data is automatically stored with metadata
   
5. Analyze the data:
   
   data = db[-1]  # Last scan
   table = data.table()
   # ... analysis code ...
```

## Comparison with SPEC

| Aspect | SPEC | Bluesky |
|--------|------|---------|
| **Input** | Text commands / macros | Python functions (plans) |
| **Execution** | Immediate | Plan → RunEngine → hardware |
| **Metadata** | Manual (printf) | Automatic (UIDs, timestamps, state) |
| **Data storage** | Files, ASCII/CCD | HDF5, DataBroker (searchable) |
| **Analysis integration** | Post-hoc | Real-time callbacks possible |
| **Parallelism** | Limited | Better coordination |
| **Modularity** | Macro files | Importable Python modules |
| **Version control** | Manual | Git-friendly |

## Key Takeaways

1. **Bluesky plans are generators** - They don't execute until you pass them to RE()
2. **Ophyd abstracts EPICS** - You use Python objects, Ophyd handles PV communication
3. **Metadata is automatic** - Every experiment is timestamped, recorded, reproducible
4. **EPICS is the foundation** - The IOC controls all real hardware
5. **Configuration is declarative** - Edit devices.yml to add hardware, not code

## Next Steps

- **Device reference:** See [devices.md](./devices.md) to understand available hardware
- **Getting started:** See [first-steps.md](./first-steps.md) for your first commands
- **Command mapping:** See [spec-to-bluesky.md](./spec-to-bluesky.md) to compare SPEC ↔ Bluesky syntax
- **Custom plans:** See [getting-started-custom-plans.md](./getting-started-custom-plans.md) to write your own experiments
- **Name mapping:** See [SPEC_to_Bluesky_Mapping.md](./SPEC_to_Bluesky_Mapping.md) for the complete device reference
