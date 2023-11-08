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
from pm4py.algo.evaluation.generalization.variants import token_based as generalization_token_based
from pm4py.algo.evaluation.precision.variants import etconformance_token as precision_token_based
from pm4py.algo.evaluation.replay_fitness.variants import token_replay as fitness_token_based
from pm4py.algo.evaluation.simplicity.variants import arc_degree as simplicity_arc_degree
from pm4py.objects import log as log_lib
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.util import constants
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    PARAM_FITNESS_WEIGHT = 'fitness_weight'
    PARAM_PRECISION_WEIGHT = 'precision_weight'
    PARAM_SIMPLICITY_WEIGHT = 'simplicity_weight'
    PARAM_GENERALIZATION_WEIGHT = 'generalization_weight'


def apply(log: Union[EventLog, pd.DataFrame], net: PetriNet, initial_marking: Marking, final_marking: Marking, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, float]:
    """
    Calculates all metrics based on token-based replay and returns a unified dictionary

    Parameters
    -----------
    log
        Log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters

    Returns
    -----------
    dictionary
        Dictionary containing fitness, precision, generalization and simplicity; along with the average weight of
        these metrics
    """
    if parameters is None:
        parameters = {}
    log = log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, log_lib.util.xes.DEFAULT_NAME_KEY)
    fitness_weight = exec_utils.get_param_value(Parameters.PARAM_FITNESS_WEIGHT, parameters, 0.25)
    precision_weight = exec_utils.get_param_value(Parameters.PARAM_PRECISION_WEIGHT, parameters, 0.25)
    simplicity_weight = exec_utils.get_param_value(Parameters.PARAM_SIMPLICITY_WEIGHT, parameters, 0.25)
    generalization_weight = exec_utils.get_param_value(Parameters.PARAM_GENERALIZATION_WEIGHT, parameters, 0.25)

    sum_of_weights = (fitness_weight + precision_weight + simplicity_weight + generalization_weight)
    fitness_weight = fitness_weight / sum_of_weights
    precision_weight = precision_weight / sum_of_weights
    simplicity_weight = simplicity_weight / sum_of_weights
    generalization_weight = generalization_weight / sum_of_weights

    parameters_tr = {token_replay.Parameters.ACTIVITY_KEY: activity_key}

    aligned_traces = token_replay.apply(log, net, initial_marking, final_marking, parameters=parameters_tr)

    parameters = {
        token_replay.Parameters.ACTIVITY_KEY: activity_key
    }

    fitness = fitness_token_based.evaluate(aligned_traces)
    precision = precision_token_based.apply(log, net, initial_marking, final_marking, parameters=parameters)
    generalization = generalization_token_based.get_generalization(net, aligned_traces)
    simplicity = simplicity_arc_degree.apply(net)

    metrics_average_weight = fitness_weight * fitness["log_fitness"] + precision_weight * precision \
                             + generalization_weight * generalization + simplicity_weight * simplicity

    fscore = 0.0
    if (fitness['log_fitness'] + precision) > 0:
        fscore = (2*fitness['log_fitness']*precision)/(fitness['log_fitness']+precision)
    dictionary = {
        "fitness": fitness,
        "precision": precision,
        "generalization": generalization,
        "simplicity": simplicity,
        "metricsAverageWeight": metrics_average_weight,
        "fscore": fscore
    }

    return dictionary

