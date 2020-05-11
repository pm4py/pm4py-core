from enum import Enum
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY, PARAMETER_CONSTANT_TIMESTAMP_KEY


class Parameters(Enum):
    FORMAT = "format"
    DEBUG = "debug"
    RANKDIR = "set_rankdir"
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    AGGREGATION_MEASURE = "aggregationMeasure"

