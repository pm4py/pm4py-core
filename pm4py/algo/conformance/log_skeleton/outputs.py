from enum import Enum


class Outputs(Enum):
    DEVIATIONS = "deviations"
    NO_DEV_TOTAL = "no_dev_total"
    NO_CONSTR_TOTAL = "no_constr_total"
    DEV_FITNESS = "dev_fitness"
    IS_FIT = "is_fit"
