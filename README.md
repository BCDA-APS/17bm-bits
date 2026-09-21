# BITS Starter

Bluesky BITS instrument for the 17-BM powder diffraction beamline.

## Session startup

You can start a bluesky session in any directory using IPython console
session or Jupyter notebook.  From IPython:

```bash
bash
conda activate 17bm-bits
ipython -i -c "from bm17.startup import *"
```

See below for other startups.

### IPython console Start

To start the bluesky instrument session in a ipython execute the next command in a terminal:

```bash
ipython
```

### Jupyter Notebook Start
Start JupyterLab, a Jupyter notebook server, or a notebook, VSCode.

### Starting the BITS Package

```py
from bm17.startup import *
```

## Run Sim Plan Demos

To run some simulated plans that ensure the installation worked as expected
please run the next commands inside an ipython session or a jupyter notebook
after starting the data acquisition:

### sim_print_plan() - demonstrates a simple plan stub (no data acquired)

```py
from bm17.plans.sim_plans import sim_print_plan
RE(sim_print_plan())
```

### sim_count_plan() - demonstrates data acquisition with a counter

```py
from bm17.plans.sim_plans import sim_count_plan
RE(sim_count_plan())
```

### sim_rel_scan_plan() - demonstrates data acquisition with a counter & motor

```py
from bm17.plans.sim_plans import sim_rel_scan_plan
RE(sim_rel_scan_plan())
```

## Configuration files

The files that can be configured to adhere to your preferences are:

- `configs/iconfig.yml` - configuration for data collection
- `configs/extra_logging.yml` - configuration for session logging to console and/or files
- `src/bm17/qserver/qs-config.yml`    - contains all configuration of the QS host process. See the [documentation](https://blueskyproject.io/bluesky-queueserver/manager_config.html) for more details of the configuration.

## queueserver

The queueserver has a host process that manages a RunEngine. Client sessions
will interact with that host process.

### Run a queueserver host process

Install screen

```bash
sudo apt install screen
```

Use the queueserver host management script to start the QS host process.  The
`restart` option stops the server (if it is running) and then starts it.  This is
the usual way to (re)start the QS host process. Using `restart`, the process
runs in the background.

```bash
./scripts/bm17_qs_host.sh restart
```

### Run a queueserver client GUI

To run the gui client for the queueserver you can use the next command inside the terminal:

```bash
queue-monitor &
```

### Shell script explained

A [shell script](https://github.com/BCDA-APS/BITS/blob/main/src/apsbits/demo_qserver/qs_host.sh) (`./scripts/bm17_qs_host.sh`) starts the QS host process. Below
are all the command options, and what they do.

```bash
(17bm-bits) $ ./scripts/bm17_qs_host.sh help
Usage: qs_host.sh {start|stop|restart|status|checkup|console|run} [NAME]

    COMMANDS
        console   attach to process console if process is running in screen
        checkup   check that process is running, restart if not
        restart   restart process
        run       run process in console (not screen)
        start     start process
        status    report if process is running
        stop      stop process

    OPTIONAL TERMS
        NAME      name of process (default: bluesky_queueserver-)
```

Alternatively, run the QS host's startup command directly within the `./src/bm17/qserver/`
subdirectory.

```bash
cd ./src/bm17/qserver
start-re-manager --config=./qs-config.yml
```

## (Re)Installation

These steps describe the installation procedure.

### Start a fresh BITS environment with Conda

```bash
export ENV_NAME=17bm-bits
conda create -y -n $ENV_NAME python=3.12
conda activate $ENV_NAME
pip install apsbits
```

### Start a fresh BITS environment with pixi

**Build the environment** (also installs apsbits and this package, editable):

```bash
pixi install
```

### Creating a New Instrument
```bash
bits-create bm17
pip install -e .
```
