from enum import Enum
from dataclasses import dataclass, field
from typing import List, Union
import heapq
from pydantic import validate_call

class EventType(Enum):
    """
    EventType is an enumeration that represents the types of events that can occur
    in a queue simulation.
    """
    ARRIVAL = 1
    DEPARTURE = 2

@dataclass(order=True)
class Event:
    """
    Represents an event in the simulation with a specific time and type.

    Attributes:
        time (float): The time at which the event occurs.
        type (EventType): The type of the event, represented as an instance of the EventType enumeration.
    """
    time: float
    type: EventType = field(compare=False)

class Scheduler:
    """
    A class to manage and schedule events in a priority queue.
    """
    def __init__(self):
        """
        Constructor of the class.
        """
        self.events = []
    
    @validate_call
    def schedule(self, event: Event):
        """
        Schedules a new event by adding it to the priority queue.
        Args:
            event (Event): The event to be scheduled.
        """
        heapq.heappush(self.events, event)
    
    def get_next(self) -> Union[Event, None]:
        """
        Retrieve and remove the next scheduled event from the priority queue.
        Returns:
            Union[Event, None]: The next event in the priority queue based on its priority, or None if the queue is empty.
        """
        if len(self.events) == 0: return None
        return heapq.heappop(self.events)