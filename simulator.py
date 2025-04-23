from queuesim import Queue, Connection, EXTERIOR
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
    "queues": [
        {
            "servers": 2,
            "capacity": 3,
            "min_arrival_time": 1.0,
            "max_arrival_time": 2.0,
            "min_departure_time": 3.0,
            "max_departure_time": 4.0
        },
        {
            "servers": 1,
            "capacity": 5,
            "min_departure_time": 2.0,
            "max_departure_time": 3.0
        },
    ],
    "network": [
        {
            "source": 0,
            "target": 1,
            "probability": 0.6
        }
    ],
    "max_randoms": 100_000,
    "init_arrival_time": 2.0
}
DEFAULT_CONFIGS_FILENAME: str = "configs.yaml"

queues: List[Queue] = []

rnd          = RandomGenerator()
sched        = Scheduler()
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
    global queues, sched, global_time

    if not os.path.exists(configs_filename):
        logging.error(f"File {configs_filename} not found.")
        return

    with open(configs_filename, "r") as f:
        configs = yaml.safe_load(f)
    
    logging.debug(f"Loaded configs:\n{json.dumps(configs, indent=4)}")

    queues_configs = configs.get("queues", [])
    for qc in queues_configs:
        queues.append(Queue(
            capacity=qc.get("capacity", 5),
            servers=qc.get("servers", 2),
            arrival_interval=(
                qc.get("min_arrival_time", 0.0),
                qc.get("max_arrival_time", 0.0)
            ),
            departure_interval=(
                qc.get("min_departure_time", 0.0),
                qc.get("max_departure_time", 0.0)
            )
        ))

    networks_configs = configs.get("network", [])
    for nc in networks_configs:
        source = nc.get("source", EXTERIOR)
        target = nc.get("target", EXTERIOR)
        probab = nc.get("probability", 0.25)
        queues[source].add_connection(Connection(
            target_id=target,
            probability=probab
        ))

    max_randoms = configs.get("max_randoms", 100_000)
    init_arrival_time = configs.get("init_arrival_time", 0.0)

    sched.schedule(Event(
        time=init_arrival_time,
        source=EXTERIOR,
        target=0,
        type=EventType.ARRIVAL
    ))
    while rnd.get_count() < max_randoms:
        current_event = sched.get_next()
        if current_event is None:
            logging.warning("Out of events! Finishing simulation...")
            break
        match current_event.type:
            case EventType.ARRIVAL:   arrival(current_event)
            case EventType.PASSAGE:   passage(current_event)
            case EventType.DEPARTURE: departure(current_event)
    
    print("\n======================== SIMULATION RESULTS ========================\n")
    print(f"TOTAL SIMULATION TIME: {global_time:.2f}\n")
    for q in queues:
        q.print(global_time)

@validate_call
def accumulate_time(event: Event):
    """
    Updates the global simulation time, as well as the queue states for all queues.
    Args:
        event (Event): The event object to accumulate time for.
    """
    global queues, global_time
    for q in queues:
        q.queue_states[q.queue_occupied] += event.time - global_time
    global_time = event.time

@validate_call
def get_target(conns: List[Connection]) -> int:
    """
    Tells the ID of the next queue to which the client will be routed, based on the provided connections.
    Args:
        conns (List[Connection]): The list of connections to choose from.
    Returns:
        int: The ID of the chosen target queue.
    """
    global rnd
    rand = rnd.next_normalized()
    for c in conns:
        if rand < c.probability:
            return c.target_id
    return EXTERIOR

@validate_call
def departure(event: Event):
    """
    Handles a departure event in the queue simulation.
    Args:
        event (Event): The departure event to be handled. Must have an EventType of DEPARTURE.
    Raises:
        ValueError: If the provided event is not of type EventType.DEPARTURE.
    """
    global queues, sched, global_time
    if event.type != EventType.DEPARTURE: raise ValueError("event must be a departure event")

    accumulate_time(event)
    src = queues[event.source]
    src.queue_occupied -= 1

    if src.queue_occupied < src.SERVERS:
        return # no one is waiting to be served
    
    # someone was waiting to be served, so we schedule their next action
    tgt_id = get_target(src.get_connections())
    sched.schedule(Event(
        time=global_time + rnd.next_in_range(src.MIN_DEPARTURE_TIME, src.MAX_DEPARTURE_TIME),
        source=src.ID,
        target=tgt_id,
        type=EventType.DEPARTURE if tgt_id == EXTERIOR else EventType.PASSAGE
    ))

@validate_call
def arrival(event: Event):
    """
    Handles the arrival of an event in the queue simulation.
    Args:
        event (Event): The event object representing an arrival. Must have an EventType of ARRIVAL.
    Raises:
        ValueError: If the provided event is not of type ARRIVAL.
    """
    global queues, sched, rnd, global_time
    if event.type != EventType.ARRIVAL: raise ValueError("event must be an arrival event")
    
    accumulate_time(event)
    tgt = queues[event.target]

    # schedule the next arrival to the system (so the simulation can continue)
    sched.schedule(Event(
        time=global_time + rnd.next_in_range(tgt.MIN_ARRIVAL_TIME, tgt.MAX_ARRIVAL_TIME),
        source=EXTERIOR,
        target=tgt.ID,
        type=EventType.ARRIVAL
    ))

    # check if there is room for the new client of the current event in the target queue
    if tgt.queue_occupied >= tgt.CAPACITY:
        tgt.losses += 1
        return
    tgt.queue_occupied += 1

    if tgt.queue_occupied > tgt.SERVERS:
        return # client will need to wait for the next available server

    # client will be served immediately, so we schedule its next action
    next_tgt_id = get_target(tgt.get_connections())
    sched.schedule(Event(
        time=global_time + rnd.next_in_range(tgt.MIN_DEPARTURE_TIME, tgt.MAX_DEPARTURE_TIME),
        source=tgt.ID,
        target=next_tgt_id,
        type=EventType.DEPARTURE if next_tgt_id == EXTERIOR else EventType.PASSAGE
    ))

@validate_call
def passage(event: Event):
    """
    Handles a passage event in the queue simulation.
    Args:
        event (Event): The passage event to be handled. Must have an EventType of PASSAGE.
    Raises:
        ValueError: If the provided event is not of type EventType.PASSAGE.
    """
    global queues, sched, rnd, global_time
    if event.type != EventType.PASSAGE: raise ValueError("event must be a passage event")

    accumulate_time(event)

    # handle departure from source queue
    src = queues[event.source]
    src.queue_occupied -= 1
    if src.queue_occupied >= src.SERVERS:
        # someone is waiting to be served in src, so we schedule their next action
        next_tgt_id = get_target(src.get_connections())
        sched.schedule(Event(
            time=global_time + rnd.next_in_range(src.MIN_DEPARTURE_TIME, src.MAX_DEPARTURE_TIME),
            source=src.ID,
            target=next_tgt_id,
            type=EventType.DEPARTURE if next_tgt_id == EXTERIOR else EventType.PASSAGE
        ))
    
    # handle arrival to the target queue
    tgt = queues[event.target]
    if tgt.queue_occupied < tgt.CAPACITY:
        # the queue is not full, so we can add the client
        tgt.queue_occupied += 1
        if tgt.queue_occupied <= tgt.SERVERS:
            # client will be served immediately, so we schedule its next action
            next_tgt_id = get_target(tgt.get_connections())
            sched.schedule(Event(
                time=global_time + rnd.next_in_range(tgt.MIN_DEPARTURE_TIME, tgt.MAX_DEPARTURE_TIME),
                source=tgt.ID,
                target=next_tgt_id,
                type=EventType.DEPARTURE if next_tgt_id == EXTERIOR else EventType.PASSAGE
            ))
    else:
        tgt.losses += 1

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
        # TODO: validate the configs file
        simulation(args.configs_path)

if __name__ == "__main__":
    main()