from threading import Semaphore
from pm4py.objects.log.log import Trace, Event


class ConcurrentTrace(object):
    def __init__(self):
        """
        Initialize concurrent trace object
        """
        self.visible_transitions = []
        self.semaphore = Semaphore(1)

    def add_visible_transition(self, transition):
        """
        Adds a visible transition to the concurrent trace

        Parameters
        -----------
        transition
            Visible transition to add to the concurrent trace object
        """
        self.semaphore.acquire()
        self.visible_transitions.append(transition)
        self.semaphore.release()

    def get_trace(self):
        """
        Returns a Trace object for a TraceLog given the transitions labels

        Returns
        -----------
        trace
            Trace of the trace log
        """
        trace = Trace()
        for trans in self.visible_transitions:
            event = Event()
            event["concept:name"] = trans.label
            trace.append(event)
        return trace
