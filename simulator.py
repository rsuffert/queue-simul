from queue import Queue, Connection
from constants import EXTERIOR
from scheduler import Scheduler, Event, EventType
from rand.linearcongruent import RandomGenerator
import argparse
import yaml
import os
from pydantic import validate_call
import logging
import json
from typing import List, Dict
from configs import load_and_validate_configs, DEFAULT_CONFIGS, DEFAULT_CONFIGS_FILENAME

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
def simulation(configs: dict):
    """
    Simulates a queueing system based on the provided configuration file.
    It processes events until the maximum number of random events is reached or
    no more events are available.
    Args:
        configs (dict): The configuration dictionary containing queue and network settings.
    """
    global queues, sched, global_time
    
    logging.debug(f"Simulating with configs:\n{json.dumps(configs, indent=4)}")

    for qc in configs["queues"]:
        queues.append(Queue(
            capacity=qc["capacity"],
            servers=qc["servers"],
            arrival_interval=(qc["min_arrival_time"], qc["max_arrival_time"]),
            departure_interval=(qc["min_departure_time"], qc["max_departure_time"])
        ))

    for nc in configs["network"]:
        source = nc["source"]
        target = nc["target"]
        probab = nc["probability"]
        queues[source].connections.append(Connection(
            target_id=target,
            probability=probab
        ))

    sched.schedule(Event(
        time=configs["init_arrival_time"],
        source=EXTERIOR,
        target=0,
        type=EventType.ARRIVAL
    ))
    while RandomGenerator.count < configs["max_randoms"]:
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
        q.states[q.current_clients] += event.time - global_time
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
    global queues, rnd, sched, global_time
    if event.type != EventType.DEPARTURE: raise ValueError("event must be a departure event")

    accumulate_time(event)
    src = queues[event.source]
    src.current_clients -= 1

    if src.current_clients < src.SERVERS:
        return # no one is waiting to be served
    
    # someone was waiting to be served, so we schedule their next action
    tgt_id = src.get_next_target()
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
    if tgt.current_clients >= tgt.CAPACITY:
        tgt.losses += 1
        return
    tgt.current_clients += 1

    if tgt.current_clients > tgt.SERVERS:
        return # client will need to wait for the next available server

    # client will be served immediately, so we schedule its next action
    next_tgt_id = tgt.get_next_target()
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
    src.current_clients -= 1
    if src.current_clients >= src.SERVERS:
        # someone is waiting to be served in src, so we schedule their next action
        next_tgt_id = src.get_next_target()
        sched.schedule(Event(
            time=global_time + rnd.next_in_range(src.MIN_DEPARTURE_TIME, src.MAX_DEPARTURE_TIME),
            source=src.ID,
            target=next_tgt_id,
            type=EventType.DEPARTURE if next_tgt_id == EXTERIOR else EventType.PASSAGE
        ))
    
    # handle arrival to the target queue
    tgt = queues[event.target]
    if tgt.current_clients < tgt.CAPACITY:
        # the queue is not full, so we can add the client
        tgt.current_clients += 1
        if tgt.current_clients <= tgt.SERVERS:
            # client will be served immediately, so we schedule its next action
            next_tgt_id = tgt.get_next_target()
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
        configs = load_and_validate_configs(args.configs_path)
        simulation(configs)

if __name__ == "__main__":
    main()