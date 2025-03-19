from enum import Enum
from dataclasses import dataclass
from typing import List
import heapq

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
    type: EventType

class Scheduler:
    """
    A class to manage and schedule events in a priority queue.
    Attributes:
        events (list): A list that holds the scheduled events in a priority queue.
    """
    def __init__(self):
        """
        Initializes the Scheduler instance.

        This constructor initializes an empty list to store events that will be
        managed by the scheduler.
        """
        self.events = []
    
    def schedule(self, event):
        """
        Schedules a new event by adding it to the priority queue.

        Args:
            event (Event): The event to be scheduled. Must be an instance of the Event class.

        Raises:
            TypeError: If the provided event is not an instance of the Event class.
        """
        if not isinstance(event, Event): raise TypeError("event must be an instance of Event.")
        heapq.heappush(self.events, event)
    
    def get_next(self) -> Event:
        """
        Retrieve and remove the next scheduled event from the priority queue.

        Returns:
            Event: The next event in the priority queue based on its priority.
                   Returns None if the queue is empty.
        """
        if len(self.events) == 0: return None
        return heapq.heappop(self.events)