from queuesim import Queue
from scheduler import Event, EventType
import argparse
import yaml

DEFAULT_CONFIGS = {
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
DEFAULT_CONFIGS_FILENAME = "configs.yaml"


def default_configs():
    with open(DEFAULT_CONFIGS_FILENAME, "w") as f:
        yaml.dump(DEFAULT_CONFIGS, f)
    print("Default configurations saved to configs.yaml")

def simulation(configs_filename: str):
    with open(configs_filename, "r") as f:
        configs = yaml.safe_load(f)
    q = Queue(
        configs["queue"]["capacity"],
        configs["queue"]["servers"],
        (configs["queue"]["min_arrival_time"], configs["queue"]["max_arrival_time"]),
        (configs["queue"]["min_departure_time"], configs["queue"]["max_departure_time"]),
        Event(configs["scheduler"]["initial_arrival"]["time"], EventType.ARRIVAL)
    )
    q.simulate(configs["scheduler"]["max_randoms"])
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