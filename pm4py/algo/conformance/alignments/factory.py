'''
This module contains the factory method

'''
from pm4py import util as pm4pyutil
from pm4py.algo.conformance.alignments import versions
from pm4py.entities.log.util import xes
from pm4py.entities.log import log as log_implementation
import pm4py
from pm4py.algo.conformance import alignments as ali
from copy import copy
from pm4py.algo.conformance.alignments import utils

VERSION_STATE_EQUATION_A_STAR = 'state_equation_a_star'
VERSIONS = {VERSION_STATE_EQUATION_A_STAR: versions.state_equation_a_star.apply}
VERSIONS_COST = {VERSION_STATE_EQUATION_A_STAR: versions.state_equation_a_star.get_best_worst_cost}


def apply(trace, petri_net, initial_marking, final_marking, parameters=None, variant=VERSION_STATE_EQUATION_A_STAR):
    """
    Apply alignments to a trace

    Parameters
    -----------
    trace
        Trace
    petri_net
        Petri net object
    initial_marking
        Initial marking of the Petri net
    final_marking
        Final marking of the Petri net
    parameters
        Parameters of the algorithm, including:
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Attribute in the log that contains the activity
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION ->
                                                    Attribute in the log that contains the cost function for model moves
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION ->
                                                    Attribute in the log that contains the cost function for sync moves
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_TRACE_COST_FUNCTION ->
                                                    Attribute in the log that contains the cost function for log moves
    variant
        Selected variant of the algorithm

    Returns
    -----------
    alignment
        Alignment for the given trace in the log
    """
    if parameters is None:
        parameters = {pm4pyutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: xes.DEFAULT_NAME_KEY}
    parameters2 = copy(parameters)
    if not pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_TRACE_COST_FUNCTION in parameters2:
        parameters2[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_TRACE_COST_FUNCTION] = list(map(lambda e: ali.utils.STD_MODEL_LOG_MOVE_COST, trace))
    return VERSIONS[variant](trace, petri_net, initial_marking, final_marking, parameters2)

def apply_log(log, petri_net, initial_marking, final_marking, parameters=None, variant=VERSION_STATE_EQUATION_A_STAR):
    """
    Apply alignments to a log

    Parameters
    -----------
    log
        Trace log object
    petri_net
        Petri net object
    initial_marking
        Initial marking of the Petri net
    final_marking
        Final marking of the Petri net
    parameters
        Parameters of the algorithm, including:
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Attribute in the log that contains the activity
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION ->
                                                        Attribute in the log that contains the cost function for model moves
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION ->
                                                        Attribute in the log that contains the cost function for sync moves
    variant
        Selected variant of the algorithm

    Returns
    -----------
    alignments
        Alignments for all the traces in the log
    """
    if parameters is None:
        parameters = {}
    activity_key = parameters[pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else pm4py.entities.log.util.xes.DEFAULT_NAME_KEY
    model_cost_function = parameters[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION] if pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION in parameters else None
    sync_cost_function = parameters[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION] if pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION in parameters else None
    if model_cost_function is None or sync_cost_function is None:
        # reset variables value
        model_cost_function = 0
        sync_cost_function = 0
        model_cost_function = dict()
        sync_cost_function = dict()
        for t in petri_net.transitions:
            if t.label is not None:
                model_cost_function[t] = ali.utils.STD_MODEL_LOG_MOVE_COST
                sync_cost_function[t] = 0
            else:
                model_cost_function[t] = 1

    best_worst_cost = VERSIONS_COST[variant](petri_net, initial_marking, final_marking)

    parameters[pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
    parameters[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION] = model_cost_function
    parameters[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION] = sync_cost_function
    alignments = list(map(lambda trace: apply(trace, petri_net, initial_marking, final_marking, parameters=parameters, variant=variant), log))

    # assign fitness to traces
    for index, align in enumerate(alignments):
        align_cost = align['cost']  // ali.utils.STD_MODEL_LOG_MOVE_COST

        #align['fitness'] = 1 - ((align['cost']  // ali.utils.STD_MODEL_LOG_MOVE_COST) / best_worst_cost)
        align['fitness'] = 1 - ((align['cost'] // ali.utils.STD_MODEL_LOG_MOVE_COST) / (len(log[index]) + best_worst_cost))

    return alignments