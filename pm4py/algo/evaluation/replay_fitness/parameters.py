from enum import Enum
from pm4py.util import constants

import warnings

warnings.warn("pm4py.algo.evaluation.replay_fitness.parameters is deprecated. Please use the variant-specific parameters.")


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    TOKEN_REPLAY_VARIANT = "token_replay_variant"
    CLEANING_TOKEN_FLOOD = "cleaning_token_flood"
    MULTIPROCESSING = "multiprocessing"
