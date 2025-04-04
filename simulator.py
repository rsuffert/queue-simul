from queuesim import Queue
from scheduler import Scheduler, Event, EventType
from rand.linearcongruent import RandomGenerator
import argparse
import yaml
import os
from pydantic import validate_call
import logging
import json
from typing import List

DEFAULT_CONFIGS: dict = {
    "queue0": {
        "servers": 2,
        "capacity": 3,
        "min_arrival_time": 1.0,
        "max_arrival_time": 4.0,
        "min_departure_time": 3.0,
        "max_departure_time": 4.0
    },
    "queue1": {
        "servers": 1,
        "capacity": 5,
        "min_departure_time": 2.0,
        "max_departure_time": 3.0
    },
    "scheduler": {
        "init_arrival_time": 2.0,
    },
    "max_randoms": 100_000,
}
DEFAULT_CONFIGS_FILENAME: str = "configs.yaml"

queues: List[Queue] = []

rnd          = RandomGenerator()
sched        = Scheduler()
used_randoms = 0
global_time  = 0.0

def default_configs():
    """
    Creates a default configuration file if it does not already exist.
    """
    if os.path.exists(DEFAULT_CONFIGS_FILENAME):
        logging.error(f"File {DEFAULT_CONFIGS_FILENAME} already exists. Not overwriting.")
        return

    with open(DEFAULT_CONFIGS_FILENAME, "w") as f:
        yaml.dump(DEFAULT_CONFIGS, f)

    logging.info(f"Default configurations written to the {DEFAULT_CONFIGS_FILENAME} file.")

@validate_call
def simulation(configs_filename: str):
    """
    Simulates a queueing system based on the provided configuration file.
    It processes events until the maximum number of random events is reached or
    no more events are available.
    Args:
        configs_filename (str): The path to the YAML configuration file.
    """
    global queues, sched, used_randoms, global_time

    if not os.path.exists(configs_filename):
        logging.error(f"File {configs_filename} not found.")
        return

    with open(configs_filename, "r") as f:
        configs = yaml.safe_load(f)
    
    logging.debug(f"Loaded configs:\n{json.dumps(configs, indent=4)}")

    queue0_configs    = configs.get("queue0", {})
    queue1_configs    = configs.get("queue1", {})
    sched_configs     = configs.get("scheduler", {})
    max_randoms       = configs.get("max_randoms", DEFAULT_CONFIGS["max_randoms"])
    init_arrival_time = sched_configs.get("initial_arrival_time", DEFAULT_CONFIGS["scheduler"]["init_arrival_time"])

    sched.schedule(Event(init_arrival_time, EventType.ARRIVAL))

    q0 = Queue(
        id=0,
        capacity=queue0_configs.get("capacity", DEFAULT_CONFIGS["queue0"]["capacity"]),
        servers=queue0_configs.get("servers", DEFAULT_CONFIGS["queue0"]["servers"]),
        arrival_interval=(queue0_configs.get("min_arrival_time", DEFAULT_CONFIGS["queue0"]["min_arrival_time"]),
                          queue0_configs.get("max_arrival_time", DEFAULT_CONFIGS["queue0"]["max_arrival_time"])),
        departure_interval=(queue0_configs.get("min_departure_time", DEFAULT_CONFIGS["queue0"]["min_departure_time"]),
                            queue0_configs.get("max_departure_time", DEFAULT_CONFIGS["queue0"]["max_departure_time"])),
    )
    q1 = Queue(
        id=1,
        capacity=queue1_configs.get("capacity", DEFAULT_CONFIGS["queue1"]["capacity"]),
        servers=queue1_configs.get("servers", DEFAULT_CONFIGS["queue1"]["servers"]),
        arrival_interval=(0.0, 0.0), # No external arrivals in queue2
        departure_interval=(queue1_configs.get("min_departure_time", DEFAULT_CONFIGS["queue1"]["min_departure_time"]),
                            queue1_configs.get("max_departure_time", DEFAULT_CONFIGS["queue1"]["max_departure_time"])),
    )
    queues.append(q0)
    queues.append(q1)

    while used_randoms < max_randoms:
        current_event = sched.get_next()
        if current_event == None:
            logging.warning("Out of events! Finishing simulation...")
            break
        match current_event.type:
            case EventType.ARRIVAL:   arrival(current_event)
            case EventType.PASSAGE:   passage(current_event)
            case EventType.DEPARTURE: departure(current_event)
    
    q0.print(global_time)
    q1.print(global_time)
    print(f"TOTAL SIMULATION TIME: {global_time:.2f}")

@validate_call
def accumulate_time(event: Event):
    """
    Updates the global simulation time, as well as the queue states for all queues.
    Args:
        event (Event): The event object to accumulate time for.
    """
    global queues, global_time
    
    queues[0].queue_states[queues[0].queue_occupied] += event.time - global_time
    queues[1].queue_states[queues[1].queue_occupied] += event.time - global_time
    global_time = event.time

@validate_call
def departure(event: Event):
    """
    Handles a departure event in the queue simulation.
    Args:
        event (Event): The departure event to be handled. Must have an EventType of DEPARTURE.
    Raises:
        ValueError: If the provided event is not of type EventType.DEPARTURE.
    """
    global queues, sched, rnd, used_randoms, global_time
    if event.type != EventType.DEPARTURE: raise ValueError("event must be a departure event")

    accumulate_time(event)
    queues[1].queue_occupied -= 1

    if queues[1].queue_occupied >= queues[1].SERVERS:
        sched.schedule(Event(
            global_time + rnd.next_in_range(queues[1].MIN_DEPARTURE_TIME, queues[1].MAX_DEPARTURE_TIME),
            EventType.DEPARTURE
        ))
        used_randoms += 1

@validate_call
def arrival(event: Event):
    """
    Handles the arrival of an event in the queue simulation.
    Args:
        event (Event): The event object representing an arrival. Must have an EventType of ARRIVAL.
    Raises:
        ValueError: If the provided event is not of type ARRIVAL.
    """
    global queues, sched, rnd, used_randoms, global_time
    if event.type != EventType.ARRIVAL: raise ValueError("event must be an arrival event")
    
    accumulate_time(event)

    if queues[0].queue_occupied < queues[0].CAPACITY:
        queues[0].queue_occupied += 1
        if queues[0].queue_occupied <= queues[0].SERVERS:
            sched.schedule(Event(
                global_time + rnd.next_in_range(queues[0].MIN_DEPARTURE_TIME, queues[0].MAX_DEPARTURE_TIME),
                EventType.PASSAGE
            ))
            used_randoms += 1
    else:
        queues[0].losses += 1
    
    sched.schedule(Event(
        global_time + rnd.next_in_range(queues[0].MIN_ARRIVAL_TIME, queues[0].MAX_ARRIVAL_TIME),
        EventType.ARRIVAL
    ))
    used_randoms += 1

@validate_call
def passage(event: Event):
    """
    Handles a passage event in the queue simulation.
    Args:
        event (Event): The passage event to be handled. Must have an EventType of PASSAGE.
    Raises:
        ValueError: If the provided event is not of type EventType.PASSAGE.
    """
    global queues, sched, rnd, used_randoms, global_time
    if event.type != EventType.PASSAGE: raise ValueError("event must be a passage event")

    accumulate_time(event)
    queues[0].queue_occupied -= 1

    if queues[0].queue_occupied >= queues[0].SERVERS:
        sched.schedule(Event(
            global_time + rnd.next_in_range(queues[0].MIN_DEPARTURE_TIME, queues[0].MAX_DEPARTURE_TIME),
            EventType.PASSAGE
        ))
        used_randoms += 1
    
    if queues[1].queue_occupied < queues[1].CAPACITY:
        queues[1].queue_occupied += 1
        if queues[1].queue_occupied <= queues[1].SERVERS:
            sched.schedule(Event(
                global_time + rnd.next_in_range(queues[1].MIN_DEPARTURE_TIME, queues[1].MAX_DEPARTURE_TIME),
                EventType.DEPARTURE
            ))
            used_randoms += 1
    else:
        queues[1].losses += 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-configs", "-g", action="store_true", help="Generate default configurations in the configs.yaml file")
    parser.add_argument("--configs-path", "-c", type=str, help="Path to the configurations file to be used for the simulation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s"
    )

    if args.generate_configs:
        default_configs()
    
    if args.configs_path:
        simulation(args.configs_path)

if __name__ == "__main__":
    main()