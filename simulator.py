from rand.linearcongruent import RandomGenerator
from scheduler import Scheduler, Event, EventType
from typing import List
from tabulate import tabulate

# Algorithm parameters (do not modify during run time!)
MAX_RANDOMS: int          = 100_000
INITIAL_EVENT: Event      = Event(2.0, EventType.ARRIVAL)

N_SERVERS: int            = 1
QUEUE_CAPACITY: int       = 5
MIN_ARRIVAL_TIME: float   = 2.0
MAX_ARRIVAL_TIME: float   = 5.0
MIN_DEPARTURE_TIME: float = 3.0
MAX_DEPARTURE_TIME: float = 5.0

# Algorithm state
QUEUE_OCCUPIED: int       = 0
QUEUE_STATES: List[float] = [0.0] * (QUEUE_CAPACITY + 1)
GLOBAL_TIME: float        = 0.0
N_LOSSES: int             = 0
rnd                       = RandomGenerator()
scheduler                 = Scheduler()

def main():
    global scheduler, INITIAL_EVENT, MAX_RANDOMS, QUEUE_STATES

    scheduler.schedule(INITIAL_EVENT)
    for _ in range(MAX_RANDOMS):
        current_event: Event = scheduler.get_next()
        if current_event == None:
            print("Out of events!")
            break

        if current_event.type == EventType.ARRIVAL:
            handle_arrival(current_event)
        else:
            handle_departure(current_event)

    print_results()

def print_results():
    print("========================= SIMULATION RESULTS =========================\n")
    headers = ["Queue Length", "Total Time", "Probability"]
    data = []
    for i in range(len(QUEUE_STATES)):
        state = f"{i}"
        time  = f"{QUEUE_STATES[i]:.2f}"
        prob  = f"{(QUEUE_STATES[i] / GLOBAL_TIME)*100:.2f}%"
        data.append([state, time, prob])
    print(tabulate(data, headers=headers, tablefmt="pretty"))
    print()
    print(f"TOTAL SIMULATION TIME: {GLOBAL_TIME:.2f}")
    print(f"TOTAL LOSSES: {N_LOSSES}")
    print("\n=======================================================================")

def handle_arrival(event: Event):
    global QUEUE_STATES, QUEUE_OCCUPIED, GLOBAL_TIME, QUEUE_CAPACITY, N_SERVERS, N_LOSSES
    global MIN_DEPARTURE_TIME, MAX_DEPARTURE_TIME, MIN_ARRIVAL_TIME, MAX_ARRIVAL_TIME
    global scheduler, rnd

    QUEUE_STATES[QUEUE_OCCUPIED] += event.time - GLOBAL_TIME
    GLOBAL_TIME = event.time

    if QUEUE_OCCUPIED < QUEUE_CAPACITY:
        QUEUE_OCCUPIED += 1
        if QUEUE_OCCUPIED <= N_SERVERS:
            departure_time: float = GLOBAL_TIME + rnd.next_in_range(MIN_DEPARTURE_TIME, MAX_DEPARTURE_TIME)
            departure: Event = Event(departure_time, EventType.DEPARTURE)
            scheduler.schedule(departure)
    else:
        N_LOSSES += 1
    
    next_arrival_time: float = GLOBAL_TIME + rnd.next_in_range(MIN_ARRIVAL_TIME, MAX_ARRIVAL_TIME)
    next_arrival: Event = Event(next_arrival_time, EventType.ARRIVAL)
    scheduler.schedule(next_arrival)

def handle_departure(event: Event):
    global QUEUE_STATES, QUEUE_OCCUPIED, GLOBAL_TIME, N_SERVERS
    global MIN_DEPARTURE_TIME, MAX_DEPARTURE_TIME
    global scheduler, rnd

    QUEUE_STATES[QUEUE_OCCUPIED] += event.time - GLOBAL_TIME
    GLOBAL_TIME = event.time

    QUEUE_OCCUPIED -= 1

    if QUEUE_OCCUPIED >= N_SERVERS:
        next_up_departure_time: float = GLOBAL_TIME + rnd.next_in_range(MIN_DEPARTURE_TIME, MAX_DEPARTURE_TIME)
        next_up_departure: Event = Event(next_up_departure_time, EventType.DEPARTURE)
        scheduler.schedule(next_up_departure)

if __name__ == "__main__":
    main()