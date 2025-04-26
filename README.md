# Queue Simulator

## Usage

Execute the `simulator.py` file. Run with the `--help` flag to see the available options for the simulation.

```bash
python simulator.py --help
```

Also, don't forget to install the dependencies before starting the simulation.

```bash
pip install -r requirements.txt
```

## Configuration file

When running with the `--help` flag, you'll see that the program also supports generating an initial YAML configuration file with default configs for you to get started. The YAML file is pretty self-explanatory, but a few points to note are:

- Under the `queues` section, if the `capacity` is omitted, then it will default to infinity.