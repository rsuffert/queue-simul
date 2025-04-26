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
- Under the `queues` section, if `min_arrival_time` and `max_arrival_time` (arrival interval to the queue) are omitted, then it is assumed that the queue doesn't receive any new clients from the exterior of the system. It can still receive clients forwarded from other queues, though.
- Under the `network` section, if a queue has outgoing connections with probabilities that add up to less than **1.0**, the remaining probability is treated as the chance of a client **leaving the system** directly from that queue. Similarly, if a **queue has no outgoing connections defined**, it is assumed that clients **will leave the system with 100% probability** upon reaching that queue.

## Example of Execution

The following instructions showcase how to use the simulator.


```bash
python3 simulator.py -g
```

- Generates a default configuration file named `configs.yaml`. If the file already exists, it will be preserved, the command will be ignored, and a notification will be displayed in the terminal.

```bash
python3 simulator.py -c configs.yaml 
```

- Runs the simulator using the specified configuration file (`configs.yaml` in this case). After execution, a detailed simulation report is printed to the terminal. 
- The output includes in the following order:
    - Total simulation time
    - Configuration of each queue in Kendall Notation
    - Arrival and departure times
    - A summary table of queue lengths, time spent at each length, and the corresponding probabilities
    - Number of losses per queue

```bash
python3 simulator.py -c configs.yaml -v
```

- Executes the simulator in verbose, displaying the parsed configuration from the file. This is especially useful for debugging or verifying.

