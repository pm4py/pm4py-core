import warnings
from enum import Enum

from pm4py.util import constants

warnings.warn(
    "pm4py.algo.clustering.trace_attribute_driven.parameters is deprecated. please use the variant-specific parameters")


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    SINGLE = "single"
    BINARIZE = "binarize"
    POSITIVE = "positive"
    LOWER_PERCENT = "lower_percent"
