import unittest
from scheduler import Event, EventType, Scheduler

class TestScheduler(unittest.TestCase):

    def setUp(self):
        """
        Set up a Scheduler instance for testing.
        """
        self.scheduler = Scheduler()

    def test_schedule_event(self):
        """
        Test scheduling an event.
        """
        event = Event(time=1.0, type=EventType.ARRIVAL)
        self.scheduler.schedule(event)
        self.assertEqual(len(self.scheduler.events), 1)
        self.assertEqual(self.scheduler.events[0], event)

    def test_schedule_invalid_event(self):
        """
        Test scheduling an invalid event raises a TypeError.
        """
        with self.assertRaises(TypeError):
            self.scheduler.schedule("not_an_event")

    def test_get_next_event(self):
        """
        Test retrieving the next event from the scheduler.
        """
        event1 = Event(time=1.0, type=EventType.ARRIVAL)
        event2 = Event(time=0.5, type=EventType.DEPARTURE)
        self.scheduler.schedule(event1)
        self.scheduler.schedule(event2)
        next_event = self.scheduler.get_next()
        self.assertEqual(next_event, event2)  # Event with the smallest time should be returned first
        self.assertEqual(len(self.scheduler.events), 1)

    def test_get_next_event_empty(self):
        """
        Test retrieving an event from an empty scheduler returns None.
        """
        self.assertIsNone(self.scheduler.get_next())

if __name__ == "__main__":
    unittest.main()