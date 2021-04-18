from pm4py.util import constants
from enum import Enum


import warnings

warnings.warn("pm4py.algo.discovery.heuristics.parameters is deprecated. Please use the variant-specific parameters instead.")


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    DEPENDENCY_THRESH = "dependency_thresh"
    AND_MEASURE_THRESH = "and_measure_thresh"
    MIN_ACT_COUNT = "min_act_count"
    MIN_DFG_OCCURRENCES = "min_dfg_occurrences"
    DFG_PRE_CLEANING_NOISE_THRESH = "dfg_pre_cleaning_noise_thresh"
    LOOP_LENGTH_TWO_THRESH = "loop_length_two_thresh"
    HEU_NET_DECORATION = "heu_net_decoration"
