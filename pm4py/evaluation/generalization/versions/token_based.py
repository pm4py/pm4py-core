from pm4py.algo.tokenreplay import factory as token_replay
from pm4py import log as log_lib
from collections import Counter
from math import sqrt

PARAM_ACTIVITY_KEY = 'activity_key'

PARAMETERS = [PARAM_ACTIVITY_KEY]

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
        Generalization measured
    """
    if parameters is None:
        parameters = {}
    activity_key = parameters[PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY
    [traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] =\
        token_replay.apply(log, petri_net, initial_marking, final_marking, activity_key=activity_key)
    transOccMap = Counter()
    for trace in activatedTransitions:
        for trans in trace:
            transOccMap[trans] += 1
    inv_sq_occ_sum = 0.0
    for trans in transOccMap:
        this_term = 1.0 / sqrt(transOccMap[trans])
        inv_sq_occ_sum = inv_sq_occ_sum + this_term
    for trans in petri_net.transitions:
        if not trans in transOccMap:
            inv_sq_occ_sum = inv_sq_occ_sum + 1
    generalization = 1.0
    if len(petri_net.transitions) > 0:
        generalization = 1.0 - inv_sq_occ_sum / float(len(petri_net.transitions))
    return generalization