from enum import Enum
from pm4py.util import constants


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    SINGLE = "single"
    BINARIZE = "binarize"
    POSITIVE = "positive"
    LOWER_PERCENT = "lower_percent"

