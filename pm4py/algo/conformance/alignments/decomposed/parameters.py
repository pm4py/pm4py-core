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
warnings.warn("pm4py.algo.conformance.alignments.decomposed.parameters is deprecated. Please use the variant-specific"
              "parameters.")


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    BEST_WORST_COST = 'best_worst_cost'
    PARAM_TRACE_COST_FUNCTION = 'trace_cost_function'
    ICACHE = "icache"
    MCACHE = "mcache"
    PARAM_THRESHOLD_BORDER_AGREEMENT = "thresh_border_agreement"
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
    PARAM_MODEL_COST_FUNCTION = 'model_cost_function'
    PARAM_SYNC_COST_FUNCTION = 'sync_cost_function'
    PARAM_TRACE_NET_COSTS = "trace_net_costs"
    PARAM_MAX_ALIGN_TIME = "max_align_time"
    PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
    SHOW_PROGRESS_BAR = "show_progress_bar"
