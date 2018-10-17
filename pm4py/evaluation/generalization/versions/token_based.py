from collections import Counter
from math import sqrt

from pm4py import util as pmutil
from pm4py.algo.conformance.tokenreplay import factory as token_replay
from pm4py.objects import log as log_lib

PARAM_ACTIVITY_KEY = pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY

PARAMETERS = [PARAM_ACTIVITY_KEY]


def get_generalization(petri_net, aligned_traces):
    """
    Gets the generalization from the Petri net and the list of activated transitions
    during the replay

    The approach has been suggested by the paper
    Buijs, Joos CAM, Boudewijn F. van Dongen, and Wil MP van der Aalst. "Quality dimensions in process discovery:
    The importance of fitness, precision, generalization and simplicity."
    International Journal of Cooperative Information Systems 23.01 (2014): 1440001.

    A token replay is applied and, for each transition, we can measure the number of occurrences
    in the replay. The following formula is applied for generalization

           \sum_{t \in transitions} (math.sqrt(1.0/(n_occ_replay(t)))
    1 -    ----------------------------------------------------------
                             # transitions

    Parameters
    -----------
    petri_net
        Petri net
    aligned_traces
        Result of the token-replay

    Returns
    -----------
    generalization
        Generalization measure
    """

    trans_occ_map = Counter()
    for trace in aligned_traces:
        for trans in trace["activated_transitions"]:
            trans_occ_map[trans] += 1
    inv_sq_occ_sum = 0.0
    for trans in trans_occ_map:
        this_term = 1.0 / sqrt(trans_occ_map[trans])
        inv_sq_occ_sum = inv_sq_occ_sum + this_term
    for trans in petri_net.transitions:
        if trans not in trans_occ_map:
            inv_sq_occ_sum = inv_sq_occ_sum + 1
    generalization = 1.0
    if len(petri_net.transitions) > 0:
        generalization = 1.0 - inv_sq_occ_sum / float(len(petri_net.transitions))
    return generalization


def apply(log, petri_net, initial_marking, final_marking, parameters=None):
    """
    Calculates generalization on the provided log and Petri net.

    The approach has been suggested by the paper
    Buijs, Joos CAM, Boudewijn F. van Dongen, and Wil MP van der Aalst. "Quality dimensions in process discovery:
    The importance of fitness, precision, generalization and simplicity."
    International Journal of Cooperative Information Systems 23.01 (2014): 1440001.

    A token replay is applied and, for each transition, we can measure the number of occurrences
    in the replay. The following formula is applied for generalization

           \sum_{t \in transitions} (math.sqrt(1.0/(n_occ_replay(t)))
    1 -    ----------------------------------------------------------
                             # transitions

    Parameters
    -----------
    log
        Trace log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Algorithm parameters

    Returns
    -----------
    generalization
        Generalization measure
    """
    if parameters is None:
        parameters = {}
    activity_key = parameters[
        PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY

    parameters_tr = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}

    aligned_traces = token_replay.apply(log, petri_net, initial_marking, final_marking, parameters=parameters_tr)

    return get_generalization(petri_net, aligned_traces)
