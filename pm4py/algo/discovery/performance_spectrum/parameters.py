from enum import Enum
from pm4py.util import constants

import warnings

warnings.warn("pm4py.algo.discovery.performance_spectrum.parameters is deprecated. please use the variant-specific parameters")


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    PARAMETER_SAMPLE_SIZE = "sample_size"
