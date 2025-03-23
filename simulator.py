from queuesim import Queue
from scheduler import Event, EventType

MAX_RANDOMS: int          = 100_000
INITIAL_EVENT: Event      = Event(2.0, EventType.ARRIVAL)

N_SERVERS: int            = 1
QUEUE_CAPACITY: int       = 5
MIN_ARRIVAL_TIME: float   = 2.0
MAX_ARRIVAL_TIME: float   = 5.0
MIN_DEPARTURE_TIME: float = 3.0
MAX_DEPARTURE_TIME: float = 5.0


def main():
    q = Queue(
        QUEUE_CAPACITY,
        N_SERVERS,
        (MIN_ARRIVAL_TIME, MAX_ARRIVAL_TIME),
        (MIN_DEPARTURE_TIME, MAX_DEPARTURE_TIME),
        INITIAL_EVENT
    )
    q.simulate(MAX_RANDOMS)
    print(q)


if __name__ == "__main__":
    main()