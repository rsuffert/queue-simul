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
queue_occupied: int       = 0
queue_states: List[float] = [0.0] * (QUEUE_CAPACITY + 1)
global_time: float        = 0.0
n_losses: int             = 0
remaining_randoms: int    = MAX_RANDOMS
rnd                       = RandomGenerator()
scheduler                 = Scheduler()

def main():
    global scheduler, INITIAL_EVENT, queue_states, remaining_randoms

    scheduler.schedule(INITIAL_EVENT)
    while remaining_randoms > 0:
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
    for i in range(len(queue_states)):
        state = f"{i}"
        time  = f"{queue_states[i]:.2f}"
        prob  = f"{(queue_states[i] / global_time)*100:.2f}%"
        data.append([state, time, prob])
    print(tabulate(data, headers=headers, tablefmt="pretty"))
    print()
    print(f"TOTAL SIMULATION TIME: {global_time:.2f}")
    print(f"TOTAL LOSSES: {n_losses}")
    print("\n=======================================================================")

def handle_arrival(event: Event):
    global queue_states, queue_occupied, global_time, QUEUE_CAPACITY, N_SERVERS, n_losses
    global MIN_DEPARTURE_TIME, MAX_DEPARTURE_TIME, MIN_ARRIVAL_TIME, MAX_ARRIVAL_TIME
    global scheduler, rnd, remaining_randoms

    queue_states[queue_occupied] += event.time - global_time
    global_time = event.time

    if queue_occupied < QUEUE_CAPACITY:
        queue_occupied += 1
        if queue_occupied <= N_SERVERS:
            departure_time: float = global_time + rnd.next_in_range(MIN_DEPARTURE_TIME, MAX_DEPARTURE_TIME)
            departure: Event = Event(departure_time, EventType.DEPARTURE)
            scheduler.schedule(departure)
            remaining_randoms -= 1
    else:
        n_losses += 1
    
    next_arrival_time: float = global_time + rnd.next_in_range(MIN_ARRIVAL_TIME, MAX_ARRIVAL_TIME)
    next_arrival: Event = Event(next_arrival_time, EventType.ARRIVAL)
    scheduler.schedule(next_arrival)
    remaining_randoms -= 1

def handle_departure(event: Event):
    global queue_states, queue_occupied, global_time, N_SERVERS
    global MIN_DEPARTURE_TIME, MAX_DEPARTURE_TIME
    global scheduler, rnd, remaining_randoms

    queue_states[queue_occupied] += event.time - global_time
    global_time = event.time

    queue_occupied -= 1

    if queue_occupied >= N_SERVERS:
        next_up_departure_time: float = global_time + rnd.next_in_range(MIN_DEPARTURE_TIME, MAX_DEPARTURE_TIME)
        next_up_departure: Event = Event(next_up_departure_time, EventType.DEPARTURE)
        scheduler.schedule(next_up_departure)
        remaining_randoms -= 1

if __name__ == "__main__":
    main()