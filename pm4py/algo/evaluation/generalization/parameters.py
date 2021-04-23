from enum import Enum
from pm4py.util import constants

import warnings

warnings.warn("pm4py.algo.evaluation.generalization.parameters is deprecated. Please use the variant-specific parameters.")


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
