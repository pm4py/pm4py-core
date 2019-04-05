import random
import sys

from pm4py.objects.event_store.utils.event_store import EventStore

N = "N"
DEFAULT_N = sys.maxsize


class ReservoirSamplingEventBasedStore(EventStore):
    def __init__(self, parameters=None):
        """
        Create a reservoir sampling event based event store with the specified N
        (if not specified, then the maximum integer size will be used)

        Parameters
        -------------
        parameters
            Parameters of the algorithm, including: N
        """
        EventStore.__init__(self)
        self.internal_count = 0
        if parameters is None:
            parameters = {}
        self.N = parameters[N] if N in parameters else DEFAULT_N

    def shall_be_added(self, event):
        """
        Decides if the event shall be added to the stream

        Parameters
        --------------
        event
            Event

        Returns
        --------------
        boolean
            Boolean value (True/False)
        """
        self.internal_count = self.internal_count + 1
        r = random.random()
        if r * self.internal_count <= self.N:
            return True
        return False

    def before_push(self, event):
        """
        Function that is executed after pushing the event
        in the event store

        Parameters
        -------------
        event
            Event
        """
        pass

    def do_push(self, event):
        """
        Version-specific function that is executed to push
        the event in the store

        Parameters
        -------------
        event
            Event
        """
        if len(self.event_stream) >= self.N:
            idx = random.randrange(0, len(self.event_stream))
            self.event_stream[idx] = event
        else:
            self.event_stream.append(event)

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
