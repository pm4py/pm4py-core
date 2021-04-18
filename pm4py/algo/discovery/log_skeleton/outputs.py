from enum import Enum

import warnings
warnings.warn("pm4py.algo.discovery.log_skeleton.outputs is deprecated.")


class Outputs(Enum):
    EQUIVALENCE = "equivalence"
    ALWAYS_AFTER = "always_after"
    ALWAYS_BEFORE = "always_before"
    NEVER_TOGETHER = "never_together"
    DIRECTLY_FOLLOWS = "directly_follows"
    ACTIV_FREQ = "activ_freq"
