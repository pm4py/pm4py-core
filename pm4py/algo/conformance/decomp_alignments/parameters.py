from enum import Enum
from pm4py.util import constants

class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    BEST_WORST_COST = 'best_worst_cost'
    PARAM_TRACE_COST_FUNCTION = 'trace_cost_function'
    ICACHE = "icache"
    MCACHE = "mcache"
    PARAM_THRESHOLD_BORDER_AGREEMENT = "thresh_border_agreement"
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
