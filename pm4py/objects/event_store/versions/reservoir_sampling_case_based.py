import random
import sys
import math

from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.objects.event_store.utils.event_store import EventStore
from pm4py.util import constants

N = "N"
k = "k"

DEFAULT_N = sys.maxsize
DEFAULT_K = DEFAULT_N / 50


class ReservoirSamplingTraceBasedStore(EventStore):
    def __init__(self, parameters):
        """
        Create a reservoir sampling event based event store with the specified N and k
        (if not specified, then the maximum integer size and /10 will be used)

        Parameters
        -------------
        parameters
            Parameters of the algorithm, including: N, k
        """
        EventStore.__init__(self)
        self.internal_case_count = 1
        if parameters is None:
            parameters = {}
        self.N = parameters[N] if N in parameters else DEFAULT_N
        self.k = parameters[k] if k in parameters else DEFAULT_K
        self.max_case_length = math.floor(self.N / self.k)
        self.case_events = {}
        self.case_glue = parameters[
            constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
        self.internal_count = 0

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
        case = event[self.case_glue]
        if case in self.case_events or len(self.case_events) < self.k:
            return True
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
        """case = event[self.case_glue]
        if case in self.case_events:
            if len(self.case_events[case]) > self.max_case_length:
                self.case_events[case].append
            self.case_events[case].append(event)"""
        pass

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