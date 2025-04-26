from typing import Tuple, List, Dict
from scheduler import Event, EventType
from tabulate import tabulate
from pydantic import validate_call
from dataclasses import dataclass, field
import heapq
import copy
from rand.linearcongruent import RandomGenerator
from collections import defaultdict
from constants import EXTERIOR, INFINITY

@dataclass(order=True)
class Connection:
    """
    Represents a connection to a queue to which clients can be forwarded.

    Attributes:
        target_id (int): The ID of the queue to which clients are forwarded.
        probability (float): Probability of forwarding clients to this queue.
    """
    target_id: int = field(compare=False)
    probability: float

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
                Must contain exactly two floats in non-decreasing order.
            departure_interval (Tuple[float, float]): A tuple representing the minimum and maximum time for departures.
                Must contain exactly two floats in non-decreasing order.
        Raises:
            ValueError: If any of the arguments have invalid values (e.g., non-positive integers, invalid intervals).
        """
        if capacity <= 0:                                          raise ValueError("capacity must be positive")
        if servers <= 0:                                           raise ValueError("servers must be positive")
        if len(arrival_interval) != 2:                             raise ValueError("arrival_interval must have 2 elements")
        if len(departure_interval) != 2:                           raise ValueError("departure_interval must have 2 elements")
        if arrival_interval[0] > arrival_interval[1]:              raise ValueError("arrival_interval must be in non-decreasing order")
        if departure_interval[0] > departure_interval[1]:          raise ValueError("departure_interval must be in non-decreasing order")
        if arrival_interval[0] < 0 or arrival_interval[1] < 0:     raise ValueError("arrival_interval boundaries must be non-negative")
        if departure_interval[0] < 0 or departure_interval[1] < 0: raise ValueError("departure_interval boundaries must be non-negative")
        
        self.ID: int = Queue._instances_counter
        Queue._instances_counter += 1

        self.CAPACITY:           int               = capacity
        self.SERVERS:            int               = servers
        self.MIN_ARRIVAL_TIME:   float             = arrival_interval[0]
        self.MAX_ARRIVAL_TIME:   float             = arrival_interval[1]
        self.MIN_DEPARTURE_TIME: float             = departure_interval[0]
        self.MAX_DEPARTURE_TIME: float             = departure_interval[1]
        self.current_clients:    int               = 0
        self.states:             Dict[int, float]  = defaultdict(float)
        self.losses:             int               = 0
        self.connections:        List[Connection]  = []
        self.rnd:                RandomGenerator   = RandomGenerator()

    def get_next_target(self) -> int:
        """
        Returns the ID of the next target queue based on the connection probabilities.
        Returns:
            int: The ID of the next target queue, or the EXTERIOR.
        """
        r = self.rnd.next_normalized()
        prob_acc = 0.0
        for c in self.connections:
            prob_acc += c.probability
            if r < prob_acc:
                return c.target_id
        return EXTERIOR

    @validate_call
    def print(self, global_time: float):
        headers = ["Queue Length", "Total Time", "Probability"]
        data = []
        for i in range(len(self.states)):
            state = f"{i}"
            time  = f"{self.states[i]:.2f}"
            prob  = f"{(self.states[i] / global_time)*100:.2f}%"
            data.append([state, time, prob])
        results  = f"------------------ QUEUE {self.ID} ------------------\n"
        capacity = f"/{self.CAPACITY}" if self.CAPACITY != INFINITY else ""
        results += f"Configuration: G/G/{self.SERVERS}{capacity}\n"
        if self.MIN_ARRIVAL_TIME != 0 or self.MAX_ARRIVAL_TIME != 0:
            results += f"Arrivals:   [{self.MIN_ARRIVAL_TIME:6.2f}, {self.MAX_ARRIVAL_TIME:6.2f}]\n"
        results += f"Departures: [{self.MIN_DEPARTURE_TIME:6.2f}, {self.MAX_DEPARTURE_TIME:6.2f}]\n"
        results += f"{tabulate(data, headers=headers, tablefmt='pretty')}\n"
        results += f"TOTAL LOSSES: {self.losses}\n"
        print(results)
