from enum import Enum
from pm4py.algo.conformance.tokenreplay import algorithm
from pm4py.util import constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    TOKEN_REPLAY_VARIANT = "token_replay_variant"
    PARAM_NUM_SIMULATIONS = "num_simulations"
    PARAM_FORCE_DISTRIBUTION = "force_distribution"
    PARAM_ENABLE_DIAGNOSTICS = "enable_diagnostics"
    PARAM_DIAGN_INTERVAL = "diagn_interval"
    PARAM_CASE_ARRIVAL_RATIO = "case_arrival_ratio"
    PARAM_PROVIDED_SMAP = "provided_stochastic_map"
    PARAM_MAP_RESOURCES_PER_PLACE = "map_resources_per_place"
    PARAM_DEFAULT_NUM_RESOURCES_PER_PLACE = "default_num_resources_per_place"
    PARAM_SMALL_SCALE_FACTOR = "small_scale_factor"
    PARAM_MAX_THREAD_EXECUTION_TIME = "max_thread_exec_time"
