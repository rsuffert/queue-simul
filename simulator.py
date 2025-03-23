from queuesim import Queue
from scheduler import Event, EventType
import argparse
import yaml
import os
from pydantic import validate_call

DEFAULT_CONFIGS: dict = {
    "queue": {
        "servers": 2,
        "capacity": 5,
        "min_arrival_time": 2.0,
        "max_arrival_time": 5.0,
        "min_departure_time": 3.0,
        "max_departure_time": 5.0
    },
    "scheduler": {
        "max_randoms": 100_000,
        "initial_arrival": {
            "time": 2.0,
        }
    }
}
DEFAULT_CONFIGS_FILENAME: str = "configs.yaml"

def default_configs():
    with open(DEFAULT_CONFIGS_FILENAME, "w") as f:
        yaml.dump(DEFAULT_CONFIGS, f)
    print("Default configurations saved to configs.yaml")

@validate_call
def simulation(configs_filename: str):
    if not os.path.exists(configs_filename): raise FileNotFoundError(f"File {configs_filename} not found")

    with open(configs_filename, "r") as f:
        configs = yaml.safe_load(f)

    queue_configs = configs.get("queue", {})
    sched_configs = configs.get("scheduler", {})

    q = Queue(
        queue_configs.get("capacity", DEFAULT_CONFIGS["queue"]["capacity"]),
        queue_configs.get("servers", DEFAULT_CONFIGS["queue"]["servers"]),
        (
            queue_configs.get("min_arrival_time", DEFAULT_CONFIGS["queue"]["min_arrival_time"]),
            queue_configs.get("max_arrival_time", DEFAULT_CONFIGS["queue"]["max_arrival_time"])
        ),
        (
            queue_configs.get("min_departure_time", DEFAULT_CONFIGS["queue"]["min_departure_time"]),
            queue_configs.get("max_departure_time", DEFAULT_CONFIGS["queue"]["max_departure_time"])
        ),
        Event(
            sched_configs.get("initial_arrival", {}).get("time", DEFAULT_CONFIGS["scheduler"]["initial_arrival"]["time"]),
            EventType.ARRIVAL
        )
    )
    q.simulate(sched_configs.get("max_randoms", DEFAULT_CONFIGS["scheduler"]["max_randoms"]))

    print(q)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-configs", "-g", action="store_true", help="Generate default configurations in the configs.yaml file")
    parser.add_argument("--configs-path", "-c", type=str, help="Path to the configurations file to be used for the simulation")
    args = parser.parse_args()

    if args.generate_configs:
        default_configs()
    
    if args.configs_path:
        simulation(args.configs_path)

if __name__ == "__main__":
    main()