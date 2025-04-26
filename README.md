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
python3 simulator.py --configs-path configs.yaml 
```

- Runs the simulator using the specified configuration file (`configs.yaml` in this case). After execution, a detailed simulation report is printed to the terminal. 
- The output includes in the following order:
    - Total simulation time
    - Configuration of each queue in Kendall Notation
    - Arrival and departure times
    - A summary table of queue lengths, time spent at each length, and the corresponding probabilities
    - Number of losses per queue
    - Total losses from the simulator

Example output:

```
======================== SIMULATION RESULTS ========================

TOTAL SIMULATION TIME: 37736.31

------------------ QUEUE 0 ------------------
Configuration: G/G/2/5
Arrivals:   [  1.50,   2.00]
Departures: [  2.00,   5.00]
+--------------+------------+-------------+
| Queue Length | Total Time | Probability |
+--------------+------------+-------------+
|      0       |    2.00    |    0.01%    |
|      1       |  1059.86   |    2.81%    |
|      2       |  7919.33   |   20.99%    |
|      3       |  14128.11  |   37.44%    |
|      4       |  11622.47  |   30.80%    |
|      5       |  3004.53   |    7.96%    |
+--------------+------------+-------------+
TOTAL LOSSES: 299

------------------ QUEUE 1 ------------------
Configuration: G/G/1/3
Departures: [  3.50,   5.00]
+--------------+------------+-------------+
| Queue Length | Total Time | Probability |
+--------------+------------+-------------+
|      0       |  1931.20   |    5.12%    |
|      1       |  7798.94   |   20.67%    |
|      2       |  16948.40  |   44.91%    |
|      3       |  11057.76  |   29.30%    |
+--------------+------------+-------------+
TOTAL LOSSES: 2120

------------------ QUEUE 2 ------------------
Configuration: G/G/1/2
Departures: [  2.00,   4.00]
+--------------+------------+-------------+
| Queue Length | Total Time | Probability |
+--------------+------------+-------------+
|      0       |  9015.55   |   23.89%    |
|      1       |  18985.75  |   50.31%    |
|      2       |  9735.00   |   25.80%    |
+--------------+------------+-------------+
TOTAL LOSSES: 1964
```


```bash
python3 simulator.py --configs-path configs.yaml -v
```

- Executes the simulator in verbose, displaying the parsed configuration from the file. This is especially useful for debugging or verifying.


Example of a configuration file being displayed:

```
{
    "init_arrival_time": 2.0,
    "max_randoms": 100000,
    "network": [
        {
            "probability": 0.5,
            "source": 0,
            "target": 1
        },
        {
            "probability": 0.3,
            "source": 0,
            "target": 2
        },
        {
            "probability": 0.6,
            "source": 1,
            "target": 2
        }
    ],
    "queues": [
        {
            "capacity": 5,
            "max_arrival_time": 2.0,
            "max_departure_time": 5.0,
            "min_arrival_time": 1.5,
            "min_departure_time": 2.0,
            "servers": 2
        },
        {
            "capacity": 3,
            "max_departure_time": 5.0,
            "min_departure_time": 3.5,
            "servers": 1,
            "min_arrival_time": 0.0,
            "max_arrival_time": 0.0
        },
        {
            "capacity": 2,
            "max_departure_time": 4.0,
            "min_departure_time": 2.0,
            "servers": 1,
            "min_arrival_time": 0.0,
            "max_arrival_time": 0.0
        }
    ]
}
```