from enum import Enum
from pm4py.util import constants

import warnings

warnings.warn("pm4py.algo.organizational_mining.sna.parameters is deprecated. please use the variant-specific"
              "parameters.")


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    METRIC_NORMALIZATION = "metric_normalization"
