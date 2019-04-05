import sys

from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.objects.event_store.utils.event_store import EventStore
from pm4py.util import constants

N = "N"
k = "k"

DEFAULT_N = sys.maxsize
DEFAULT_K = DEFAULT_N / 50


class ReservoirSamplingTraceBasedStore(EventStore):
    def __init__(self, parameters):
        EventStore.__init__(self)
        self.internal_case_count = 1
        if parameters is None:
            parameters = {}
        self.N = parameters[N] if N in parameters else DEFAULT_N
        self.k = parameters[k] if k in parameters else DEFAULT_K
        self.case_events = {}
        self.case_glue = parameters[
            constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
        self.internal_count = 0

    def shall_be_added(self, event):
        case = event[self.case_glue]
        if case in self.case_events or len(self.case_events) < self.k:
            return True