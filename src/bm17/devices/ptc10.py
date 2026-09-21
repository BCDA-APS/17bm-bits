"""
PTC10 Programmable Temperature Controller for 17BM beamline.

Omnibus device controlling three independent heaters:

1. **Flowcell heater** (5A: AIO/PID channel with setpoint control)
   - Temperature readback: 2A (Thermocouple)
   - PID control: 5A (inputchoice selects which TC to read)
   - Usage: yield from bps.mv(ptc10.temperature.setpoint, temp_C)

2. **Hot air blower** (3A: RTD channel, voltage monitored)
   - RTD temperature input
   - Ramp rate: 3A:rampRate
   - Setpoint: 3A:setPoint
   - Input selection (thermocouple or RTD): via 5A:pid:input

3. **Block furnace** (5B: AIO/PID channel, independent)
   - Max temperature: 600°C (hard-fail enforced)
   - PID parameters: tunable via 5B:pid:P/I/D

Channel assignments:
- 2A: Thermocouple (flowcell temperature readback)
- 3A: RTD channel (hot air blower)
- 5A: AIO/PID (flowcell control — readback via 2A)
- 5B: AIO/PID (block furnace control — independent RTD input)
- 5C: AIO voltage output (hot air blower voltage monitoring)

EPICS IOC note: 17bmSoft IOC uses "output_RBV" instead of apstools
default "voltage_RBV" for AIO channel outputs.

Usage examples::

    # Flowcell heater (readback from 2A, control via 5A)
    yield from bps.mv(ptc10.temperature.setpoint, 75)  # °C
    yield from bps.mv(ptc10.pid_5a.ramprate, 0.5)      # °C/s
    ptc10.temperature.position                           # current temp

    # Block furnace (independent control via 5B)
    yield from bps.mv(ptc10.pid_5b.setpoint, 100)      # °C
    yield from bps.mv(ptc10.pid_5b.ramprate, 0.3)      # °C/s

    # Hot air blower (control via 3A RTD)
    yield from bps.mv(ptc10.rtd_3a.setpoint, 50)       # °C
    yield from bps.mv(ptc10.rtd_3a.ramprate, 0.2)      # °C/s

    # Access voltage readbacks
    ptc10.pid_5a.voltage.get()  # flowcell AIO output
    ptc10.pid_5b.voltage.get()  # furnace AIO output
    ptc10.pid_5c.voltage.get()  # hot air blower AIO output

    # PID tuning (read from IOC, modify as needed)
    ptc10.pid_5a.P.get()        # flowcell P parameter
    yield from bps.mv(ptc10.pid_5a.P, 0.035)  # set new P

Temperature tolerance (done checking)::

    ptc10.tolerance.put(0.5)  # ±0.5°C for "at temperature"
    ptc10.inposition          # boolean: True when within tolerance
"""

from apstools.devices import (
    PTC10AioChannel,
    PTC10PositionerMixin,
    PTC10RtdChannel,
)
from ophyd import Component, EpicsSignalRO, EpicsSignalWithRBV, PVPositioner


class BM17_PTC10AioChannelFixed(PTC10AioChannel):
    """PTC10AioChannel with 17bmSoft IOC voltage-readback convention.

    Override the voltage component PV suffix:
    - apstools default: "voltage_RBV"
    - 17bmSoft convention: "output_RBV"
    """

    voltage = Component(EpicsSignalRO, "output_RBV", kind="config")


class BM17_PTC10(PTC10PositionerMixin, PVPositioner):
    """Omnibus PTC10 temperature controller for 17BM beamline.

    Attributes:
        temperature: PVPositioner interface (readback 2A, setpoint 5A)
        pid_5a: Flowcell heater AIO/PID channel (with voltage_RBV override)
        pid_5b: Block furnace heater AIO/PID channel (with voltage_RBV override)
        pid_5c: Hot air blower voltage monitoring channel (with voltage_RBV override)
        rtd_3a: Hot air blower RTD input channel

    Notes:
        - 2A thermocouple used only for flowcell readback (no contention)
        - 3A RTD independent from 5A AIO (no contention)
        - 5A and 5B are independent AIO channels (no contention)
        - P, I, D parameters accessed via ptc10.pid_5a.P / .I / .D etc.
          (these are EpicsSignalWithRBV, sourced from EPICS IOC)
        - RTD thermocouple input selection: settable via pid_5a.inputchoice
        - Block furnace maximum: 600°C (enforced at plan level)
    """

    # PVPositioner interface
    # readback from 2A (thermocouple), setpoint to 5A (AIO)
    readback = Component(EpicsSignalRO, "2A:temperature", kind="hinted")
    setpoint = Component(
        EpicsSignalWithRBV,
        "5A:setPoint",
        kind="hinted",
        doc="Flowcell setpoint temperature (°C)",
    )

    # PTC10 base control
    enable = Component(
        EpicsSignalWithRBV,
        "outputEnable",
        kind="config",
        string=True,
        doc="Enable/disable PTC10 output",
    )

    # AIO channels (with fixed voltage readback for 17bmSoft convention)
    pid_5a = Component(
        BM17_PTC10AioChannelFixed,
        "5A:",
        doc="Flowcell heater (AIO/PID channel 5A)",
    )
    pid_5b = Component(
        BM17_PTC10AioChannelFixed,
        "5B:",
        doc="Block furnace heater (AIO/PID channel 5B)",
    )
    pid_5c = Component(
        BM17_PTC10AioChannelFixed,
        "5C:",
        doc="Hot air blower voltage monitor (AIO channel 5C)",
    )

    # RTD channel
    rtd_3a = Component(
        PTC10RtdChannel, "3A:", doc="Hot air blower RTD input (RTD channel 3A)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Positioner tuning
        self.report_dmov_changes.put(True)  # Log done/moving transitions
        self.tolerance.put(1.0)  # Done when |readback-setpoint| <= 1°C
