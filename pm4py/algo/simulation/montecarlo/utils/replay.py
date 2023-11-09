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
from pm4py.algo.conformance.tokenreplay.variants import token_replay
from pm4py.statistics.variants.log import get as variants_module
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.random_variables.random_variable import RandomVariable
from pm4py.objects.petri_net.utils import performance_map
from pm4py.util import exec_utils, xes_constants
from pm4py.algo.conformance.tokenreplay import algorithm as executor

from enum import Enum
from pm4py.util import constants
from copy import copy


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


def get_map_from_log_and_net(log, net, initial_marking, final_marking, force_distribution=None, parameters=None):
    """
    Get transition stochastic distribution map given the log and the Petri net

    Parameters
    -----------
    log
        Event log
    net
        Petri net
    initial_marking
        Initial marking of the Petri net
    final_marking
        Final marking of the Petri net
    force_distribution
        If provided, distribution to force usage (e.g. EXPONENTIAL)
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> activity name
            Parameters.TIMESTAMP_KEY -> timestamp key

    Returns
    -----------
    stochastic_map
        Map that to each transition associates a random variable
    """
    stochastic_map = {}

    if parameters is None:
        parameters = {}

    token_replay_variant = exec_utils.get_param_value(Parameters.TOKEN_REPLAY_VARIANT, parameters,
                                                      executor.Variants.TOKEN_REPLAY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)

    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}
    variants_idx = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters_variants)
    variants = variants_module.convert_variants_trace_idx_to_trace_obj(log, variants_idx)

    parameters_tr = copy(parameters)
    parameters_tr[token_replay.Parameters.ACTIVITY_KEY] = activity_key
    parameters_tr[token_replay.Parameters.VARIANTS] = variants

    parameters_ses = copy(parameters)

    # do the replay
    aligned_traces = executor.apply(log, net, initial_marking, final_marking, variant=token_replay_variant,
                                        parameters=parameters_tr)

    element_statistics = performance_map.single_element_statistics(log, net, initial_marking,
                                                                   aligned_traces, variants_idx,
                                                                   activity_key=activity_key,
                                                                   timestamp_key=timestamp_key,
                                                                   parameters=parameters_ses)

    for el in element_statistics:
        if type(el) is PetriNet.Transition and "performance" in element_statistics[el]:
            values = element_statistics[el]["performance"]

            rand = RandomVariable()
            rand.calculate_parameters(values, force_distribution=force_distribution)

            no_of_times_enabled = element_statistics[el]['no_of_times_enabled']
            no_of_times_activated = element_statistics[el]['no_of_times_activated']

            if no_of_times_enabled > 0:
                rand.set_weight(float(no_of_times_activated) / float(no_of_times_enabled))
            else:
                rand.set_weight(0.0)

            stochastic_map[el] = rand

    return stochastic_map
