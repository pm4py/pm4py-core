from enum import Enum
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY


class Parameters(Enum):
    # parameter for the noise threshold
    NOISE_THRESHOLD = "noise_threshold"
    # considered constraints in conformance checking among: equivalence, always_after, always_before, never_together, directly_follows, activ_freq
    CONSIDERED_CONSTRAINTS = "considered_constraints"
    # default choice for conformance checking
    DEFAULT_CONSIDERED_CONSTRAINTS = ["equivalence", "always_after", "always_before", "never_together",
                                      "directly_follows", "activ_freq"]
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"


NOISE_THRESHOLD = Parameters.NOISE_THRESHOLD
CONSIDERED_CONSTRAINTS = Parameters.CONSIDERED_CONSTRAINTS
DEFAULT_CONSIDERED_CONSTRAINTS = Parameters.DEFAULT_CONSIDERED_CONSTRAINTS
ACTIVITY_KEY = Parameters.ACTIVITY_KEY
PARAMETER_VARIANT_DELIMITER = Parameters.PARAMETER_VARIANT_DELIMITER
