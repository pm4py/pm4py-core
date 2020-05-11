from enum import Enum


class Outputs(Enum):
    EQUIVALENCE = "equivalence"
    ALWAYS_AFTER = "always_after"
    ALWAYS_BEFORE = "always_before"
    NEVER_TOGETHER = "never_together"
    DIRECTLY_FOLLOWS = "directly_follows"
    ACTIV_FREQ = "activ_freq"
