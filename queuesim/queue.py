from typing import Tuple, List
from rand.linearcongruent import RandomGenerator
from scheduler import Scheduler, Event, EventType
from tabulate import tabulate
from pydantic import validate_call

class Queue:
    """
    Queue class represents a simulation of a queueing system with a specified capacity, number of servers, 
    arrival and departure intervals, and an initial event.
    """
    @validate_call
    def __init__(self, capacity: int, servers: int, arrival_interval: Tuple[float, float], departure_interval: Tuple[float, float], first_event: Event):
        """
        Initializes a Queue object with the specified parameters.
        Args:
            capacity (int): The maximum number of items the queue can hold. Must be a positive integer.
            servers (int): The number of servers available to process items in the queue. Must be a positive integer.
            arrival_interval (Tuple[float, float]): A tuple representing the minimum and maximum time between arrivals.
                Must contain exactly two floats in increasing order.
            departure_interval (Tuple[float, float]): A tuple representing the minimum and maximum time for departures.
                Must contain exactly two floats in increasing order.
            first_event (Event): The first event to be scheduled in the queue. Must be an arrival event.
        Raises:
            ValueError: If any of the arguments have invalid values (e.g., non-positive integers, invalid intervals).
        """
        if capacity <= 0:                                  raise ValueError("capacity must be positive")
        if servers <= 0:                                   raise ValueError("servers must be positive")
        if len(arrival_interval) != 2:                     raise ValueError("arrival_interval must have 2 elements")
        if len(departure_interval) != 2:                   raise ValueError("departure_interval must have 2 elements")
        if arrival_interval[0] >= arrival_interval[1]:     raise ValueError("arrival_interval must be in increasing order")
        if departure_interval[0] >= departure_interval[1]: raise ValueError("departure_interval must be in increasing order")
        if first_event.type != EventType.ARRIVAL:          raise ValueError("first_event must be an arrival event")
        
        self.CAPACITY:           int             = capacity
        self.SERVERS:            int             = servers
        self.MIN_ARRIVAL_TIME:   float           = arrival_interval[0]
        self.MAX_ARRIVAL_TIME:   float           = arrival_interval[1]
        self.MIN_DEPARTURE_TIME: float           = departure_interval[0]
        self.MAX_DEPARTURE_TIME: float           = departure_interval[1]
        self.global_time:        float           = 0.0
        self.queue_occupied:     int             = 0
        self.queue_states:       List[float]     = [0.0] * (capacity + 1)
        self.losses:             int             = 0
        self.used_randoms:       int             = 0
        self.rnd:                RandomGenerator = RandomGenerator()
        self.scheduler:          Scheduler       = Scheduler()
        self.scheduler.schedule(first_event)
    
    @validate_call
    def handle_arrival(self, event: Event):
        """
        Handles the arrival of an event in the queue simulation.
        Args:
            event (Event): The event object representing an arrival. Must have an EventType of ARRIVAL.
        Raises:
            ValueError: If the provided event is not of type ARRIVAL.
        """
        if event.type != EventType.ARRIVAL: raise ValueError("event must be an arrival event")
        
        self.queue_states[self.queue_occupied] += event.time - self.global_time
        self.global_time = event.time

        if self.queue_occupied < self.CAPACITY:
            self.queue_occupied += 1
            if self.queue_occupied <= self.SERVERS:
                departure_time: float = self.global_time + self.rnd.next_in_range(self.MIN_DEPARTURE_TIME, self.MAX_DEPARTURE_TIME)
                departure: Event = Event(departure_time, EventType.DEPARTURE)
                self.scheduler.schedule(departure)
                self.used_randoms += 1
        else:
            self.losses += 1
        
        next_arrival_time: float = self.global_time + self.rnd.next_in_range(self.MIN_ARRIVAL_TIME, self.MAX_ARRIVAL_TIME)
        next_arrival: Event = Event(next_arrival_time, EventType.ARRIVAL)
        self.scheduler.schedule(next_arrival)
        self.used_randoms += 1
    
    @validate_call
    def handle_departure(self, event: Event):
        """
        Handles a departure event in the queue simulation.
        Args:
            event (Event): The departure event to be handled. Must have an EventType of DEPARTURE.
        Raises:
            ValueError: If the provided event is not of type EventType.DEPARTURE.
        """
        if event.type != EventType.DEPARTURE: raise ValueError("event must be a departure event")

        self.queue_states[self.queue_occupied] += event.time - self.global_time
        self.global_time = event.time

        self.queue_occupied -= 1

        if self.queue_occupied >= self.SERVERS:
            next_up_departure_time: float = self.global_time + self.rnd.next_in_range(self.MIN_DEPARTURE_TIME, self.MAX_DEPARTURE_TIME)
            next_up_departure: Event = Event(next_up_departure_time, EventType.DEPARTURE)
            self.scheduler.schedule(next_up_departure)
            self.used_randoms += 1
    
    @validate_call
    def simulate(self, n_randoms: int):
        """
        Simulates the queue system by processing events until the specified number 
        of random events have been used or there are no more events to process.
        Args:
            n_randoms (int): The number of random events to process.
        """
        if n_randoms <= 0: raise ValueError("n_randoms must be positive")

        while self.used_randoms < n_randoms:
            current_event = self.scheduler.get_next()
            if current_event == None:
                print("Out of events!")
                break

            if current_event.type == EventType.ARRIVAL:
                self.handle_arrival(current_event)
            else:
                self.handle_departure(current_event)
    
    def __repr__(self) -> str:
        headers = ["Queue Length", "Total Time", "Probability"]
        data = []
        for i in range(len(self.queue_states)):
            state = f"{i}"
            time  = f"{self.queue_states[i]:.2f}"
            prob  = f"{(self.queue_states[i] / self.global_time)*100:.2f}%"
            data.append([state, time, prob])

        results = "\n========================= QUEUE SIMULATION RESULTS =========================\n"
        results += f"\n{tabulate(data, headers=headers, tablefmt='pretty')}\n\n"
        results += f"TOTAL SIMULATION TIME: {self.global_time:.2f}\n"
        results += f"TOTAL LOSSES: {self.losses}\n"
        results += "\n===========================================================================\n"

        return results
