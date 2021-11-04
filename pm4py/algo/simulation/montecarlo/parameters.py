'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from enum import Enum
from pm4py.util import constants


import warnings

warnings.warn("pm4py.algo.simulation.montecarlo.parameters is deprecated. Please use the variant-specific parameters.")


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
