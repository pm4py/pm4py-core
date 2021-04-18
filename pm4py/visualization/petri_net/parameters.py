import warnings
from enum import Enum

from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY, PARAMETER_CONSTANT_TIMESTAMP_KEY

warnings.warn(
    "pm4py.visualization.petri_net.parameters is deprecated. please use the parameters inside the visualization variant.")


class Parameters(Enum):
    FORMAT = "format"
    DEBUG = "debug"
    RANKDIR = "set_rankdir"
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    AGGREGATION_MEASURE = "aggregationMeasure"
    FONT_SIZE = "font_size"
