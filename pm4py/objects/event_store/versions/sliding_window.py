import sys

from pm4py.objects.event_store.utils.event_store import EventStore

N = "N"
DEFAULT_N = sys.maxsize


class SlidingWindowEventStore(EventStore):
    def __init__(self, parameters=None):
        """
        Create a sliding window event store with the specified N
        (if not specified, then the maximum integer size will be used)

        Parameters
        -------------
        parameters
            Parameters of the algorithm, including: N
        """
        EventStore.__init__(self)
        if parameters is None:
            parameters = {}
        self.N = parameters[N] if N in parameters else DEFAULT_N

    def before_push(self, event):
        """
        Function that is executed before pushing the event
        in the event store

        Parameters
        --------------
        event
            Event
        """
        if len(self.event_stream) == self.N:
            del self.event_stream[0]

    def after_push(self, event):
        """
        Function that is executed after pushing the event
        in the event store

        Parameters
        -------------
        event
            Event
        """
        pass
