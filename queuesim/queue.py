from typing import Tuple, List
from scheduler import Event, EventType
from tabulate import tabulate
from pydantic import validate_call

class Queue:
    """
    Queue class represents a simulation of a queueing system with a specified capacity, number of servers, 
    arrival and departure intervals, and an initial event.
    """
    
    _instances_counter: int = 0
    
    @validate_call
    def __init__(self, capacity: int, servers: int, arrival_interval: Tuple[float, float], departure_interval: Tuple[float, float]):
        """
        Initializes a Queue object with the specified parameters.
        Args:
            capacity (int): The maximum number of items the queue can hold. Must be a positive integer.
            servers (int): The number of servers available to process items in the queue. Must be a positive integer.
            arrival_interval (Tuple[float, float]): A tuple representing the minimum and maximum time between arrivals.
                Must contain exactly two floats in increasing order.
            departure_interval (Tuple[float, float]): A tuple representing the minimum and maximum time for departures.
                Must contain exactly two floats in increasing order.
        Raises:
            ValueError: If any of the arguments have invalid values (e.g., non-positive integers, invalid intervals).
        """
        if capacity <= 0:                                  raise ValueError("capacity must be positive")
        if servers <= 0:                                   raise ValueError("servers must be positive")
        if len(arrival_interval) != 2:                     raise ValueError("arrival_interval must have 2 elements")
        if len(departure_interval) != 2:                   raise ValueError("departure_interval must have 2 elements")
        if arrival_interval[0] > arrival_interval[1]:      raise ValueError("arrival_interval must be in non-decreasing order")
        if departure_interval[0] > departure_interval[1]:  raise ValueError("departure_interval must be in non-decreasing order")
        
        self.ID:                 int             = Queue._instances_counter
        Queue._instances_counter += 1
        self.CAPACITY:           int             = capacity
        self.SERVERS:            int             = servers
        self.MIN_ARRIVAL_TIME:   float           = arrival_interval[0]
        self.MAX_ARRIVAL_TIME:   float           = arrival_interval[1]
        self.MIN_DEPARTURE_TIME: float           = departure_interval[0]
        self.MAX_DEPARTURE_TIME: float           = departure_interval[1]
        self.queue_occupied:     int             = 0
        self.queue_states:       List[float]     = [0.0] * (capacity + 1)
        self.losses:             int             = 0
        self.used_randoms:       int             = 0
    
    @validate_call
    def print(self, global_time: float):
        headers = ["Queue Length", "Total Time", "Probability"]
        data = []
        for i in range(len(self.queue_states)):
            state = f"{i}"
            time  = f"{self.queue_states[i]:.2f}"
            prob  = f"{(self.queue_states[i] / global_time)*100:.2f}%"
            data.append([state, time, prob])
        results  = f"------------------ QUEUE {self.ID} ------------------"
        results += f"\n{tabulate(data, headers=headers, tablefmt='pretty')}\n"
        results += f"TOTAL LOSSES: {self.losses}\n"
        print(results)
