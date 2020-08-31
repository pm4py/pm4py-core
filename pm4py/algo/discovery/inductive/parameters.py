from pm4py.util import constants
from enum import Enum


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    NOISE_THRESHOLD = "noiseThreshold"
    EMPTY_TRACE_KEY = "empty_trace"
    ONCE_PER_TRACE_KEY = "once_per_trace"
    CONCURRENT_KEY = "concurrent"
    STRICT_TAU_LOOP_KEY = "strict_tau_loop"
    TAU_LOOP_KEY = "tau_loop"

